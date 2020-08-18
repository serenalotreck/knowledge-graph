"""
Creates a table comparing the entities extracted from scispaCy models with hand-
annotated entities in plant biology literature.

Hand-annotated entities should be in the first column of a csv, and the second
column should contain their IOB. Entities must be spaCy-compatible tokens
(i.e. single words).

Will compare the en_core_sci_md and all four NER models.

Author: Serena G. Lotreck
"""
import argparse
import os

import pandas as pd
import spacy


def make_comparison_table(text, annotation):
    """
    Makes IOB table with extracted entities and annotation entities.
    """
    pass

def main(text, annotation):
    """
    Compares entities from different models and hand annotation

    parameters:
        text, str: string of text on which to apply models
        annotation, Series: entities from hand annotation
    """
    # Load the models
    nlp_sci = spacy.load("en_core_sci_md")
    nlp_craft = spacy.load("en_ner_craft_md")
    nlp_jnlpba = spacy.load("en_ner_jnlpba_md")
    nlp_bc5cdr = spacy.load("en_ner_bc5cdr_md")
    nlp_bionlp = spacy.load("en_ner_bionlp13cg_md")

    # Create doc objects
    doc_sci = nlp_sci(text)
    doc_craft = nlp_craft(text)
    doc_jnlpba = nlp_jnlpba(text)
    doc_bc5cdr = nlp_bc5cdr(text)
    doc_bionlp = nlp_bionlp(text)

    # Print numbers of entities
    print(f'Number of entities identified:\nFull pipeline: {len(doc_sci.ents)} '
            f'\nCRAFT model: {len(doc_craft.ents)}'
            f'\nJNLPBA model: {len(doc_jnlpba.ents)}'
            f'\nBC5CDR model: {len(doc_bc5cdr)}'
            f'\nBIONLP13CG model: {len(doc_bionlp)}'
            f'\n Hand annotation: {len(annotation)}')

    # Make comparison table
    print('\n\nMaking entity comparison table. This will use the spaCy IOB '
            'scheme: I = inside an entity span, O = not an entity, B = '
            'beginning of an entity span')
    make_comparison_table(text, annotation)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare entities between models')
    parser.add_argument('text', type=str, help='Text to apply model on (path)')
    parser.add_argument('annotation', type=str, help='Hand annotated entities (path)')

    args = parser.parse_args()

    args.text = os.path.abspath(args.text)
    args.annotation = os.path.abspath(args.annotation)

    with open(args.text) as f:
        text = " ".join([x.strip() for x in f])
    annotation = pd.read_csv(args.annotation)

    main(text, annotation)
