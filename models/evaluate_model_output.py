"""
Given the output of a model in DyGIE++ format and a gold standard entity set,
calculate precision, recall and F1 for entity prediction.

Prints to stdout, use > to pipe output to a file

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, basename, join
from os import listdir

from dygie.training.f1 import compute_f1  # Must have dygiepp developed in env
import jsonlines
import pandas as pd


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
    gold_standard_dict = {d['doc_key']: d for d in gold_standard_dicts}

    # Go through the docs
    for doc in prediction_dicts:
        # Get the corresnponding gold standard
        try:
            gold_std = gold_standard_dict[doc['doc_key']]
        except KeyError:
            verboseprint(
                f'Document {doc["doc_key"]} is not in the gold standard. '
                'Skipping this document for performance calculation.')
            continue
        # Go through each sentence
        for sent1, sent2 in zip(doc['predicted_ner'], gold_std['ner']):
            # Make the lists into a dict where the key is the sentence idx and
            # the value is the start and end token indices
            gold_sent = {i: l[:2] for i, l in enumerate(sent2)}
            pred_sent = {i: l[:2] for i, l in enumerate(sent1)}
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


def get_performance_row(pred_file, gold_std_file):
    """
    Gets performance metrics and returns as a list.

    parameters:
        pred_file, str: name of the file used for predictions
        gold_std_file, str: name of the gold standard file

    returns:
        row, list: [pred file name, gold std file name, precision, recall, f1]
    """
    # Read in the files
    gold_std_dicts = []
    with jsonlines.open(gold_std_file) as reader:
        for obj in reader:
            gold_std_dicts.append(obj)
    pred_dicts = []
    with jsonlines.open(pred_file) as reader:
        for obj in reader:
            pred_dicts.append(obj)

    pred_names = [pred["doc_key"] for pred in pred_dicts]
    gold_std_names = [gold["doc_key"] for gold in gold_std_dicts]

    # Calculate performance
    predicted, gold, matched = get_f1_input(gold_std_dicts, pred_dicts)
    precision, recall, f1 = compute_f1(predicted, gold, matched)

    return [
        basename(pred_file),
        basename(gold_std_file), precision, recall, f1
    ]


def main(gold_standard, out_name, predictions):

    # Calculate performance
    verboseprint('\nCalculating performance...')
    df_rows = []
    for model in predictions:
        df_rows.append(get_performance_row(model, gold_standard))

    verboseprint(df_rows)

    # Make df
    verboseprint('\nMaking dataframe...')
    df = pd.DataFrame(
        df_rows,
        columns=['pred_file', 'gold_std_file', 'precision', 'recall', 'F1'])
    verboseprint(f'Snapshot of dataframe:\n{df.head()}')

    # Save
    verboseprint(f'\nSaving file as {out_name}')
    df.to_csv(out_name, index=False)

    verboseprint('\nDone!\n')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Calculate performance')

    parser.add_argument('gold_standard',
                        type=str,
                        help='Path to dygiepp-formatted gold standard data')
    parser.add_argument('out_name',
                        type=str,
                        help='Name of save file for output (including path)')
    parser.add_argument(
        'prediction_dir',
        type=str,
        help='Path to directory with dygiepp-formatted model outputs')
    parser.add_argument(
        '-use_prefix',
        type=str,
        help='If a prefix is provided, only calculates performance for '
        'files beginning with the prefix in the directory.',
        default='')
    parser.add_argument('--verbose',
                        '-v',
                        action='store_true',
                        help='If provided, script progress will be printed')

    args = parser.parse_args()

    args.gold_standard = abspath(args.gold_standard)
    args.out_name = abspath(args.out_name)
    args.prediction_dir = abspath(args.prediction_dir)

    verboseprint = print if args.verbose else lambda *a, **k: None

    pred_files = [
        join(args.prediction_dir, f) for f in listdir(args.prediction_dir)
        if f.startswith(args.use_prefix)
    ]

    main(args.gold_standard, args.out_name, pred_files)
