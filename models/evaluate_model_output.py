"""
Given the output of a model in DyGIE++ format and a gold standard entity set,
calculate precision, recall and F1 for entity prediction.

Prints to stdout, use > to pipe output to a file

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath

from dygie.training.f1 import compute_f1 # Must have dygiepp developed in env
import jsonlines


def get_f1_input(gold_standard_dicts, prediction_dicts):
    """
    Get the number of true and false postives and false negatives for the
    model to calculate the following inputs for compute_f1:
        predicted = true positives + false positives
        gold = true positives + false negatives
        matched = true positives

    parameters:
        gold_standard_dicts, list of dict: dygiepp formatted annotations
        prediction_dicts, list of dict: dygiepp formatted predictions

    returns:
        predicted, int
        gold, int
        matched, int
    """
    tp = 0
    fp = 0
    fn = 0

    # Rearrange gold standard so that it's a dict with keys that are doc_id's
    gold_standard_dict = {d['doc_key']:d for d in gold_standard_dicts}

    # Go through the docs
    for doc in prediction_dicts:
        # Get the corresnponding gold standard
        try:
            gold_std = gold_standard_dict[doc['doc_key']]
        except KeyError:
            print(f'Document {doc["doc_key"]} is not in the gold standard. '
                    'Skipping this document for performance calculation.')
            continue
        # Go through each sentence
        for sent1, sent2 in zip(doc['predicted_ner'], gold_std['ner']):
            # Make the lists into a dict where the key is the sentence idx and
            # the value is the start and end token indices
            gold_sent = {i:l[:2] for i, l in enumerate(sent2)}
            pred_sent = {i:l[:2] for i, l in enumerate(sent1)}
            # Iterate through predictions and check for them in gold standard
            for pred_idx, pred in pred_sent.items():
                if pred in gold_sent.values():
                    tp += 1
                else:
                    fp += 1
            for gold_idx, gold in gold_sent.items():
                if gold in pred_sent.values():
                    continue
                else:
                    fn += 1

    predicted = tp + fp
    gold = tp + fn
    matched = tp

    return predicted, gold, matched


def main(gold_standard, predictions):

    # Read in the files
    gold_standard_dicts = []
    with jsonlines.open(gold_standard) as reader:
        for obj in reader:
            gold_standard_dicts.append(obj)
    prediction_dicts = []
    with jsonlines.open(predictions) as reader:
        for obj in reader:
            prediction_dicts.append(obj)

    # Calculate performance
    predicted, gold, matched = get_f1_input(gold_standard_dicts,
                                            prediction_dicts)
    precision, recall, f1 = compute_f1(predicted, gold, matched)

    # Print to to stdout
    print('==================> Performance report <==================')
    print(f'\nPrediction file: {predictions}')
    print(f'Gold standard file: {gold_standard}\n')
    print(f'Precision: {precision}')
    print(f'Recall: {recall}')
    print(f'F1: {f1}')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Calculate performance')

    parser.add_argument('gold_standard', type=str,
            help='Path to dygiepp-formatted gold standard data')
    parser.add_argument('predictions', type=str,
            help='Path to dygiepp-formatted model output')

    args = parser.parse_args()

    args.gold_standard = abspath(args.gold_standard)
    args.predictions = abspath(args.predictions)

    main(args.gold_standard, args.predictions)
