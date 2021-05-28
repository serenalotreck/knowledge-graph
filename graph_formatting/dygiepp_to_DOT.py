"""
Formats the output of dygiepp into a DOT file, where triples take the form:

    A -> B [ label = "relation", weight=1 ];

Edge weights are incremented if the triple is already present in the graph, 
so an edge weight represents how many times the triple occurs in a dataset.

Keeps the same file name as the dygiepp input, changes the ext to .dot
"""
from os.path import abspath
import argparse 

import jsonlines


def get_loose_ents(preds):
    """
    Get all entities as a list from a set of dygiepp predictions.

    parameters:
        preds, list of dict: one dict per doc, minimally must contain the keys
            'sentences', 'predicted_ner_' and 'predicted_relations'

    returns: ents, list of str: entities 
    """

    ## TODO 
    # Clarify variable names 
    # Consider combining this and the triples function to reduce number of loops


    ents = []
    for doc in preds:
        # Get tokenized document
        for sentence in doc:
            for word in sentence:
                tokenized_doc.append(word)

        ent_list = []
        for sent_ent_list in doc['predicted_ner']:
            entities = []
            for ent_list in sent_ent_list:
                ent = " ".join(tokenized_doc[ent_list[0]:ent_list[1]+1])
                entities.append(ent)

            ent_list += entities

        ents += ent_list

    return ents


def get_triples(preds):
    """
    Takes a list of dygiepp predictions (list of json-like dict) and returns 
    a list of triples present in the list, with any duplicates that may exist.

    parameters:
        preds, list of dict: one dict per doc, minimally must contain the keys
            'sentences', 'predicted_ner_' and 'predicted_relations'
    
    returns:
        triples, list of 3-tuples: each entry is a triple of the form 
            (head, relation, tail), where all entries are strings
    """
    triples = []
    for doc in preds:
        # Get full tokenized doc 
        tokenized_doc = []
        for sentence in doc['sentences']:
            for word in sentence:
                tokenized_doc.append(word)
        # Get triples
        for sent_rel_list in doc['predicted_relations']:
            rels = []
            for rel_list in sent_rel_list:
                rel = (" ".join(tokenized_doc[rel_list[0]:rel_list[1]+1),
                        rel_list[4],
                        " ".join(tokenized_doc[rel_list[2]:rel_list[3]+1))
                rels.append(rel)
            triples += rels

    return triples


def main(dygiepp_preds, out_loc):

    # Read in the data 
    print('\nReading in the data...\n')
    total = 0
    failed = 0 
    preds = []
    with jsonlines.open(dygiepp_preds) as reader:
        for obj in reader:
            total += 1
            if "_FAILED_PREDICTION" in obj.keys():
                if obj["_FAILED_PREDICTION"]:
                    failed += 1
            else: preds.append(obj)

    print(f'\nTotal docs: {total}\nFailed predictions: {failed}\n'
            f'Docs to process: {len(preds)}')

    # Format the predictions as triples & loose entities 
    triples = get_triples(preds)
    loose_ents = get_loose_ents(preds)
    
    # Write to doc 

    ## Picup here on Tuesday



    
if __name __ == "__main__":

    parser = argparse.ArgumentParser(description='Put dygiepp output into DOT')

    parser.add_argument('-dygiepp_preds', type=str, 
            help='Path to file with dygiepp output')
    parser.add_argument('-out_loc', type=str,
            help='Path tp save the output')

    args = parser.parse_args()

    args.dygiepp_preds = abspath(args.dygiepp_preds)
    args.out_loc = abspath(args.out_loc)

    main(args.dygiepp_preds, args.out_loc)
