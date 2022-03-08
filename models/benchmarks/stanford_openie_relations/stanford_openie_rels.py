"""
Script to perform open relation extraction on text using Stanford OpenIE and
convert the output to the dygiepp format.

Author: Serena G. Lotreck
"""
import argparse
from os import listdir
from os.path import abspath, join, splitext, basename

import jsonlines
import stanza
stanza.install_corenlp()
from stanza.server import CoreNLPClient


def get_doc_rels(ann):
    """
    Get relation annotations from openie objects. Assigns the text extracted as
    the relation as the relation type in order to preserve that information.

    NOTE: Will have to account for having done this in the evaluation script,
    may decide to change it to just having a generic relation type.

    parameters:
        ann, output from OpenIE

    returns:
        rels, list of list of lists: one list per sentence, one list per
            relation annotation in sentence
    """
    rels = []
    for sent in ann["sentences"]:
        sent_rels = []
        triples = sent["openie"]
        for triple in triples:
            rel = [triple["subjectSpan"][0] - 1,
                   triple["subjectSpan"][1] - 1,
                   triple["objectSpan"][0] - 1,
                   triple["objectSpan"][1] - 1,
                   triple["relation"]]
            sent_rels.append(rel)
        rels.append(sent_rels)

    return rels


def get_doc_ents(ann):
    """
    Get entity annotations from ann openie objects.

    parameters:
        ann, output from OpenIE

    returns:
        ents, list of list of lists: one list per sentence, one list per
            entity annotation in sentence
    """
    ents = []
    for sent in ann["sentences"]:
        sent_ents = []
        triples = sent["openie"]
        for triple in triples:
            for part in ['subject', 'object']:
                ent = [triple[f"{part}Span"][0] - 1,
                       triple[f"{part}Span"][1] - 1,
                       'ENTITY']
                sent_ents.append(ent)
        ents.append(sent_ents)

    return ents


def get_doc_sents(ann):
    """
    Reconstruct sentences from the index object in the ann object.

    parameters:
        ann, output from OpenIE

    returns:
        sents, list of lists: one list per sentence containing tokens as
            elements
    """
    sents = []
    for sent in ann["sentences"]:
        sent = []
        for idx in sent["index"]:
            sent.append(idx["originalText"])
        sents.append(sent)

    return sents


def openie_to_dygiepp(ann, doc_key):
    """
    Convert the output of StanfordNLP OpenIE to dygiepp format. Subtracts 1
    from all token offsets to convert 1-indexted token offsets to 0-indexed
    token offsets.

    parameters:
        ann, output form stanza.server.CoreNLPClient annotate function:
            annotation to convert
        doc_key, str: string to identify the document

    returns:
        json, dict: dygiepp formatted json for the annotated file
    """
    # Get doc sentences
    sents = get_doc_sents(ann)

    # Get doc ents
    ents = get_doc_ents(ann)

    # Get doc rels
    rels = get_doc_rels(ann)

    # Make the json
    json = {}
    json["doc_key"] = doc_key
    json["dataset"] = 'scierc' # Doesn't matter what this is for eval
    json["sentences"] = sents
    json["predicted_ner"] = ents
    json["predicted_relations"] = rels

    return json


def main(data_dir, to_annotate, affinity_cap, output_name):

    properties = {'openie.affinity_probability_cap': affinity_cap}

    dygiepp_jsonl = []
    for doc in to_annotate:

        # Get the doc_key
        doc_key = splitext(basename(doc))[0]

        # Read in the text
        with open(doc) as f:
            text = " ".join(f.read().split('\n'))

        # Perform OpenIE
        with CoreNLPClient(annotators=["openie"], output_format="json") as client:
            ann = client.annotate(text)

        # Convert output to dygiepp format
        dygiepp_jsonl.append(openie_to_dygiepp(ann, doc_key))

    # Write out dygiepp-formatted output 
    with jsonlines.open(output_name, 'w') as writer:
        writer.write_all(dygiepp_jsonl)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Use Stanford OpenIE for '
            'relation extraction')

    parser.add_argument('data_dir', type=str, help='Path to directory with '
            'files to annotate.')
    parser.add_argument('output_name', type=str, help='Path, including name, '
            'to save the dygiepp-formatted OpenIE annotations.')
    parser.add_argument('-affinity_cap', type=float, help='"Hyperparameter '
            'denoting the min fraction ofd the time an edge should occur in a '
            'context in order to be considered unremoveable from the graph", '
            'in the original OpenIE experiments this is set to 1/3.',
            default=1/3)

    args = parser.parse_args()
    args.data_dir = abspath(args.data_dir)
    args.output_name = abspath(args.output_name)

    to_annotate = [join(args.data_dir, f) for f in listdir(args.data_dir) if
            f.endswith('.txt')]

    main(args.data_dir, to_annotate, args.affinity_cap, args.output_name)
