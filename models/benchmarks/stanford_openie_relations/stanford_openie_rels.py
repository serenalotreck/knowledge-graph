"""
Script to perform open relation extraction on text using Stanford OpenIE and
convert the output to the dygiepp format.

Author: Serena G. Lotreck
"""
import argparse
from os import listdir
from os.path import abspath, join, splitext, basename
from collections import OrderedDict

import jsonlines
import stanza
stanza.install_corenlp()
from stanza.server import CoreNLPClient
from openie import StanfordOpenIE


def graph_annotations(text, properties, doc_key, graph_out_loc):
    """
    Use philipperemy's openie wrapper to make graphviz renderings of a set of
    annotations.

    parameters:
        text, str: text to anntoate and graph
        properties, dict: properties dict containing affinity cap
        doc_key, str: name of the document, used to create the output file name
        graph_out_loc, str, path to save the output file

    returns: None
    """
    save_name = f'{graph_out_loc}/{doc_key}_openie_graph.png'

    with StanfordOpenIE(properties=properties) as client:
        client.generate_graphviz_graph(text, save_name)


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
    prev_toks = 0 # Keep track of the number of tokens we've seen
    rels = []
    for sent in ann["sentences"]:
        sent_rels = []
        triples = sent["openie"]
        for triple in triples:
            # Dygiepp token indices are for the whole document, while stanford
            # openIE indices are on a sentence-level. Need to add the previous
            # number of tokens we've seen in order to get document-level
            # indices. The end indices in dygiepp are inclusive, whereas they
            # are not in stanford openIE, so also need to subtract 1 from end
            # idx
            rel = [triple["subjectSpan"][0] + prev_toks,
                   triple["subjectSpan"][1] + prev_toks - 1,
                   triple["objectSpan"][0] + prev_toks,
                   triple["objectSpan"][1] + prev_toks - 1,
                   triple["relation"]]
            sent_rels.append(rel)
        rels.append(sent_rels)
        prev_toks += len(sent["tokens"])

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
    prev_toks = 0 # Keep track of the number of tokens we've seen
    ents = []
    for sent in ann["sentences"]:
        sent_ents = []
        triples = sent["openie"]
        for triple in triples:
            # Dygiepp token indices are for the whole document, while stanford
            # openIE indices are on a sentence-level. Need to add the previous
            # number of tokens we've seen in order to get document-level
            # indices. The end indices in dygiepp are inclusive, whereas they
            # are not in stanford openIE, so also need to subtract 1 from end
            # idx
            for part in ['subject', 'object']:
                ent = [triple[f"{part}Span"][0] + prev_toks,
                       triple[f"{part}Span"][1] + prev_toks - 1,
                       'ENTITY']
                sent_ents.append(ent)
        # Remove duplicate entities that participated in multiple relations
        sent_ents = [tuple(x) for x in sent_ents]
        sent_ents = list(OrderedDict.fromkeys(sent_ents))
        sent_ents = [list(x) for x in sent_ents]

        ents.append(sent_ents)
        prev_toks += len(sent["tokens"])

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
        sent_list = []
        for idx in sent["tokens"]:
            sent_list.append(idx["originalText"])
        sents.append(sent_list)

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


def main(data_dir, to_annotate, affinity_cap, output_name, graph, graph_out_loc):

    properties = {'openie.affinity_probability_cap': affinity_cap}

    dygiepp_jsonl = []
    with CoreNLPClient(annotators=["openie"], output_format="json") as client:
        for doc in to_annotate:

            # Get the doc_key
            doc_key = splitext(basename(doc))[0]

            # Read in the text
            with open(doc) as f:
                text = " ".join(f.read().split('\n'))

            # Perform OpenIE
                ann = client.annotate(text)

            # Convert output to dygiepp format
            dygiepp_jsonl.append(openie_to_dygiepp(ann, doc_key))

            # Graph annotations if requested
            if graph:
                graph_annotations(text, properties, doc_key, graph_out_loc)

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
    parser.add_argument('--graph', action='store_true')
    parser.add_argument('-graph_out_loc', type=str, help='Path to save graphs '
            'if --graph is specified. Default is ""', default='')

    args = parser.parse_args()
    args.data_dir = abspath(args.data_dir)
    args.output_name = abspath(args.output_name)
    if args.graph:
        args.graph_out_loc = abspath(args.graph_out_loc)

    to_annotate = [join(args.data_dir, f) for f in listdir(args.data_dir) if
            f.endswith('.txt')]

    main(args.data_dir, to_annotate, args.affinity_cap, args.output_name,
            args.graph, args.graph_out_loc)
