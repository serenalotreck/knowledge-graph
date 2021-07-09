"""
Get the percentage of overlap between the ner-extracted entities and those used 
in relations for a dygiepp output. 

Author: Serena G. Lotreck
"""
import os
import argparse
import jsonlines
import DocClass as dc
import statistics

def main(dygiepp_output):

    # Read in jsonl file 
    docs = []
    with jsonlines.open(dygiepp_output) as reader:
        for obj in reader:
            docs.append(obj)

    # Get percentages 
    percent_ents = []
    percent_rels = []
    for doc in docs:
        doc_obj = dc.Doc(doc, '')
        per_ent, per_rel = doc_obj.get_entity_overlap()
        if per_ent is not None:
            percent_ents.append(per_ent)
        if per_rel is not None:
            percent_rels.append(per_rel)

    # Calculate mean and median 
    percent_ent_mean = statistics.mean(percent_ents)
    percent_ent_med = statistics.median(percent_ents)
    percent_rels_mean = statistics.mean(percent_rels)
    percent_rels_med = statistics.median(percent_rels)

    # Print results 
    print(f'On average, {percent_ent_mean:.2f} % of ner-extracted entities were '
            f'involved in relations (median value: {percent_ent_med:.2f} %)')
    print(f'On average, {percent_rels_mean:.2f} % of entities involved in '
            f'relations were also extracted by ner (median value: {percent_rels_med:.2f} %)')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get entity overlap')

    parser.add_argument('dygiepp_output', type=str,
            help='Path to dygiepp output file')

    args = parser.parse_args()

    args.dygiepp_output = os.path.abspath(args.dygiepp_output)

    main(args.dygiepp_output)
