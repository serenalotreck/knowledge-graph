"""
Formats the output of dygiepp into a DOT file, where triples take the form:

    A -> B [ label = "relation", weight=1 ];

Edge weights are incremented if the triple is already present in the graph, 
so an edge weight represents how many times the triple occurs in a dataset.

Keeps the same file name as the dygiepp input, changes the ext to .dot
"""
from os.path import abspath
import argparse 
from collections import defaultdict
import jsonlines
import pygraphviz as pgv 


def write_dot_file(triples, loose_ents, graph_name, out_loc):
    """
    Takes triples and loose entities and uses the graphviz library
    to format them into a DOT file. 

    parameters:
        triples, list of 3-tuples: (head, relation, tail) triples
        loose_ents, list of str: loose entities 
        graph_name, str: filename for output file 
        out_loc, str: path to save file 
    """
    # Instatiate the graph 
    dot = pgv.AGraph(directed=True, name=graph_name)

    # Get triple weights
    triple_weights = defaultdict(int)
    
    for triple in triples:
        triple_weights[triple] += 1
    
    # Add triples 
    for triple, weight in triple_weights.items():

        dot.add_edge(triple[0], triple[2], label=triple[1], 
                weight=f'{weight}')

    # Add entities 
    for entity in loose_ents:
        dot.add_node(entity)

    # Save the file 
    dot.write(f'{out_loc}/{graph_name}.gv')


def get_tokenized_doc(doc):
    """
    Helper for get_loose_ents and get_triples. Takes a dygiepp-formatted
    doc and returns the text as a list of tokens. 

    parameters:
        doc, dict: dygiepp formatted doc 

    returns: tokenized_doc, list of str: tokens in the doc
    """
    tokenized_doc = []
    for sentence in doc['sentences']:
        for word in sentence:
            tokenized_doc.append(word)
    
    return tokenized_doc


def get_loose_ents(preds, triples):
    """
    Get all entities  that are not included in a relation as a list from a set 
    of dygiepp predictions. 

    parameters:
        preds, list of dict: one dict per doc, minimally must contain the keys
            'sentences', 'predicted_ner_' and 'predicted_relations'
        triples, list of 3-tuples: triples from the same set of preds

    returns: ents, list of str: entities 
    """
    # Get list of all entities already included in triples 
    previous_ents = set()
    for triple in triples:
        previous_ents.add(triple[0])
        previous_ents.add(triple[2])
    
    loose_ents = []
    for doc in preds:
        # Get tokenized document
        tokenized_doc = get_tokenized_doc(doc)

        for per_sentence_ent_list in doc['predicted_ner']:
            for ent_list in per_sentence_ent_list:
                ent = " ".join(tokenized_doc[ent_list[0]:ent_list[1]+1])
                if ent not in previous_ents:
                    loose_ents.append(ent)

    return loose_ents


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
        tokenized_doc = get_tokenized_doc(doc)
        
        # Get triples
        for per_sentence_rels_list in doc['predicted_relations']:
            for triple_list in per_sentence_rels_list:
                
                # Get the elements of the triple
                head = " ".join(tokenized_doc[triple_list[0]:triple_list[1]+1])
                rel = triple_list[4]
                tail =  " ".join(tokenized_doc[triple_list[2]:triple_list[3]+1])
                
                # Add to the list of triples 
                triple = (head, rel, tail)
                
                # Add the triple to the graph
                triples.append(triple)
    
    return triples


def main(dygiepp_preds, graph_name, out_loc):

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
    print('\nFormatting predictions into triples and entities...\n')
    triples = get_triples(preds)
    loose_ents = get_loose_ents(preds, triples)
    
    # Write to doc 
    print('\nWriting predictions to DOT file...\n')
    write_dot_file(triples, loose_ents, graph_name, out_loc)    
    print('\nDone!\n')

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Put dygiepp output into DOT')

    parser.add_argument('-dygiepp_preds', type=str, 
            help='Path to file with dygiepp output')
    parser.add_argument('-graph_name', type=str, 
            help='Filename for dot file')
    parser.add_argument('-out_loc', type=str,
            help='Path tp save the output')

    args = parser.parse_args()

    args.dygiepp_preds = abspath(args.dygiepp_preds)
    args.out_loc = abspath(args.out_loc)

    main(args.dygiepp_preds, args.graph_name, args.out_loc)
