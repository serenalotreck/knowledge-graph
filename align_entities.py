"""
Creates a table comparing the entities extracted from scispaCy models with hand-
annotated entities in plant biology literature.

Hand-annotated entities should be in the first column of a csv.

Will compare the en_core_sci_md and all four NER models.

Author: Serena G. Lotreck
"""
import argparse
import os
import csv

import pandas as pd
import spacy
from spacy.matcher import Matcher
from functools import reduce


def add_annotation_iob(iob_table, annotation, doc_sci):
    """
    Adds annotation entities to iob table.

    Uses spaCy's Matcher to get all instances of annotated entities in the text,
    and adds the corresponding IOB type to the table. Uses the text from the
    sci model for matching.

    returns: completed iob table
    """
    # Find matches for annotated entities in doc
    nlp = spacy.load('en_core_sci_md')

    patterns = [[{'LOWER':token.text.lower()} for token in nlp(entity)] for entity in annotation]
    print(f'patterns = {patterns}')

    matcher = Matcher(nlp.vocab)
    for i, pattern in enumerate(patterns):
        matcher.add(f'entity{i}', None, pattern)

    matches = matcher(doc_sci)

    # Check to make sure all entities were found
    matches_check = [(doc_sci[match[1]:match[2]]).text.lower() for match in matches]
    print(f'matches_check: {matches_check}')
    print(f'annotation: {annotation}')
    for entity in annotation:
        if entity.lower() not in matches_check:
            raise Exception(f'Entity {entity} not found in matches!')

    # Initialize empty string column in table
    iob_table['annotation_iob'] = ""

    # Populate column with IOB
    for match in matches:
        start_id = match[1]
        end_id = match[2]

        # Give IOB to single-word entities
        if start_id+1 == end_id:
            iob_table.loc[start_id, 'annotation_iob'] = "B"
        # Give IOB to multi-word entities
        else:
            iob_table.loc[start_id, 'annotation_iob'] = "B"
            for ix in range(start_id+1, end_id, 1):
                iob_table.loc[ix, 'annotation_iob'] = "I"

    # Fill in remaining columns with O
    iob_table.loc[iob_table.annotation_iob == "", 'annotation_iob'] = "O"

    # Check that all rows have been filled
    empty_rows = iob_table[iob_table['annotation_iob'] == ''].index.tolist()
    if len(empty_rows) != 0:
        raise Exception(f'Row(s) {empty_rows} are missing IOB value!')

    print(f'\n\nSnapshot of completed IOB table:\n{iob_table.head()}')
    return iob_table


def main(text, annotation, save_path, save_name):
    """
    Compares entities from different models and hand annotation

    parameters:
        text, str: string of text on which to apply models
        annotation, list of str: entities from hand annotation
        save_path, str: path to save file
        save_name, str: root name for files. NO file extension
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
    doc_dict = {'sci':doc_sci, 'craft':doc_craft,
                'jnlpba':doc_jnlpba, 'bc5cdr':doc_bc5cdr,
                'bionlp':doc_bionlp}

    # Print numbers of entities
    print(f'\nNumber of entities identified:\nFull pipeline: {len(doc_sci.ents)} '
            f'\nCRAFT model: {len(doc_craft.ents)}'
            f'\nJNLPBA model: {len(doc_jnlpba.ents)}'
            f'\nBC5CDR model: {len(doc_bc5cdr.ents)}'
            f'\nBIONLP13CG model: {len(doc_bionlp.ents)}'
            f'\nHand annotation: {len(annotation)}')

    # Make comparison table
    print('\n\nMaking entity comparison table. This will use the spaCy IOB '
            'scheme: I = inside an entity span, O = not an entity, B = '
            'beginning of an entity span')

    iob_df_list = []
    for key, doc in doc_dict.items():
        iob = [(t.text, t.ent_iob_, t.ent_type_) for t in doc]
        cols = ['text', f'{key}_iob', f'{key}_type']
        df = pd.DataFrame(iob, columns=cols)
        iob_df_list.append(df)
    print(f'Dataframe shapes are {[df.shape for df in iob_df_list]}')
    # Merge is too memory intensive, so concatonate, assert that all text
    # columns are equal, and drop all but one
    iob_concat = reduce(lambda left, right: pd.concat([left, right], axis=1), iob_df_list)
    print(f'Snapshot of concatonated frames:\n{iob_concat.head()}')

    # Add hand annotation
    iob_complete = add_annotation_iob(iob_concat, annotation, doc_sci)

    # Save csv of table and table transpose
    print('Saving to csv...')
    iob_complete.to_csv(f'{save_path}/{save_name}.csv', index=False)
    print('Saving table transpose to csv...')
    iob_transpose = iob_complete.T
    iob_transpose.to_csv(f'{save_path}/{save_name}_transpose.csv', index=False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare entities between models')
    parser.add_argument('text', type=str, help='Text to apply model on (path)')
    parser.add_argument('annotation', type=str, help='Hand annotated entities (path)')
    parser.add_argument('save_path', type=str, help='Path to directory where '
                        'files will be saved')
    parser.add_argument('save_name', type=str, help='Root name for the table files '
                        'NO file extension')

    args = parser.parse_args()

    args.text = os.path.abspath(args.text)
    args.annotation = os.path.abspath(args.annotation)
    args.save_path = os.path.abspath(args.save_path)

    with open(args.text) as f:
        text = " ".join([x.strip() for x in f])
    with open(args.annotation) as f:
        annotation = [row[0] for row in csv.reader(f)]

    main(text, annotation, args.save_path, args.save_name)
