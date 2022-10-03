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
import numpy as np


def calculate_CI(prec_samples, rec_samples, f1_samples):
    """
    Calculates CI from bootstrap samples using the percentile method with
    alpha = 0.05 (95% CI).
    
    parameters:
        prec_samples, list of float: list of precision values for bootstraps
        rec_samples, list of float: list of recall values for bootstraps
        f1_samples, list of float: list of f1 values for bootstraps
        
    returns:
        prec_CI, tuple of float: CI for precision
        rec_CI, tuple of float: CI for recall
        f1_CI, tuple of float: CI for F1 score
    """
    CIs = {}
    for name, samp_set in {'prec_samples':prec_samples,
                           'rec_samples':rec_samples, 'f1_samples':f1_samples}:
        lower_bound = np.percentile(samp_set, 100*(alpha/2))
        upper_bound = np.percentile(samp_set, 100*(1-alpha/2))
        name = name.split('_')[0] + '_CI'
        CIs[name] = (lower_bound, upper_bound)
        
    return CIs['prec_CI'], CIs['rec_CI'], CIs['f1_CI']


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


def draw_boot_samples(pred_dicts, gold_std_dicts, num_boot):
    """
    Draw bootsrtap samples.
    
    parameters:
        pred_dicts, list of dict: dicts of model predictions
        gold_std_dicts, list of dict: dicts of gold standard annotations
        num_boot, int: number of bootstrap samples to draw
        
    returns:
        prec_samples, list of float: list of precision values for bootstraps
        rec_samples, list of float: list of recall values for bootstraps
        f1_samples, list of float: list of f1 values for bootstraps
    """
    prec_samples = []
    rec_samples = []
    f1_samples = []
    for _ in range(num_boot):
        # Sample prediction dicts with replacement
        pred_samp = np.random.choice(pred_dicts, size=len(pred_dicts), replace=True)
        # Get indices of the sampled instances in the pred_dicts list
        idx_list = [pred_dicts.index(i) for i in pred_samp]
        # Since the two lists are sorted the same, can use indices to get equivalent docs in gold std
        gold_samp = np.array([gold_std_dicts[i] for i in idx_list])
        # Calculate performance for the sample
        predicted, gold, matched = get_f1_input(gold_samp, pred_samp)
        precision, recall, f1 = compute_f1(predicted, gold, matched)
        # Append each of the performance values to their respective sample lists
        prec_samples.append(precision)
        rec_samples.append(recall)
        f1_samples.append(f1)
        
    return prec_samples, rec_samples, f1_samples


def get_performance_row(pred_file, gold_std_file, bootstrap, num_boot):
    """
    Gets performance metrics and returns as a list.

    parameters:
        pred_file, str: name of the file used for predictions
        gold_std_file, str: name of the gold standard file
        bootstrap, bool, whether or not to bootstrap a confidence interval
        num_boot, int: if bootstrap is True, how many bootstrap samples to take

    returns:
        row, list: [pred file name, gold std file name, precision, recall, f1]
            if bootstrap is false, same columns plus [prec_CI, rec_CI, f1_CI]
            if bootstrap is true
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

    # Sort the pred and gold lists by doc key to make sure they're in the same order
    gold_std_dicts = sorted(gold_std_dicts, key=lambda d: d['doc_key'])
    pred_dicts = sorted(pred_dicts, key=lambda d: d['doc_key'])
    
    # Bootstrap sampling
    if boostrap:
        prec_samples, rec_samples, f1_samples = draw_boot_samples(pred_dicts, gold_std_dicts, num_boot)

        # Calculate confidence interval
        prec_CI, rec_CI, f1_CI = calculate_CI(prec_samples, rec_samples, f1_samples)

        # Get means
        precision = np.mean(prec_samples)
        recall = np.mean(rec_samples)
        f1 = np.mean(f1_samples)

        return [
            basename(pred_file),
            basename(gold_std_file), precision, recall, f1, prec_CI, rec_CI, f1_CI
        ]
    
    else:
        # Calculate performance
        predicted, gold, matched = get_f1_input(gold_std_dicts, pred_dicts)
        precision, recall, f1 = compute_f1(predicted, gold, matched)

        return [
            basename(pred_file),
            basename(gold_std_file), precision, recall, f1
        ]


def main(gold_standard, out_name, predictions, boostrap, num_boot):

    # Calculate performance
    verboseprint('\nCalculating performance...')
    df_rows = []
    for model in predictions:
        df_rows.append(get_performance_row(model, gold_standard,
                                           bootstrap, num_boot))

    verboseprint(df_rows)

    # Make df
    verboseprint('\nMaking dataframe...')
    df = pd.DataFrame(
        df_rows,
        columns=['pred_file', 'gold_std_file', 'precision', 'recall', 'F1', 
                 'precision_CI', 'recall_CI', 'F1_CI'])
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
        'prediction_paths',
        type=str,
        help='Path to .txt file containing full paths to dygiepp-formatted model '
        'outputs, one on each line')
    parser.add_argument('--boostrap', action='store_true',
                        help='Whether or not to bootstrap a confidence interval '
                        'for performance metrics. Specify for deterministic model '
                        'output.')
    parser.add_argument(
        '-num_boot',
        type=int,
        help='Number of bootstrap samples to use for calculating CI, '
        'default is 500',
        default=500)
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
    args.prediction_paths = abspath(args.prediction_paths)

    verboseprint = print if args.verbose else lambda *a, **k: None

    with open(args.prediction_paths) as myf:
        pred_paths = myf.readlines()
    pred_files = [
        join(args.prediction_paths, f) for f in listdir(args.prediction_paths)
        if f.startswith(args.use_prefix)
    ]

    main(args.gold_standard, args.out_name, pred_files, args.bootstrap, args.num_boot)
