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

    returns list with elements:
        prec_CI, tuple of float: CI for precision
        rec_CI, tuple of float: CI for recall
        f1_CI, tuple of float: CI for F1 score
    """
    alpha = 0.05
    CIs = {}
    for name, samp_set in {'prec_samples':prec_samples,
                           'rec_samples':rec_samples,
                           'f1_samples':f1_samples}.items():
        lower_bound = np.percentile(samp_set, 100*(alpha/2))
        upper_bound = np.percentile(samp_set, 100*(1-alpha/2))
        name = name.split('_')[0] + '_CI'
        CIs[name] = (lower_bound, upper_bound)

    return [CIs['prec_CI'], CIs['rec_CI'], CIs['f1_CI']]


def check_rel_matches(pred, gold_sent):
    """
    Checks for order-agnostic matches of pred in gold_sent.

    Note that pred/gold are relative, can be swapped to get false negatives by
    comparing a "pred" from the gold standard against the "gold_sent" of
    predictions from the model, as is done in get_f1_input.

    parameters:
        pred, list: 4 integers (entity bounds) and a string (relation type)
        gold_sent, list of list: internal lists are relation representations
            with the same format as pred

    returns:
        True if an order-agnostic match exists in gold_sent, False otherwise
    """
    # Make all preds into strings of chars to make it easier to
    # search for character pairs
    gold_rel_strs = []
    for rel in gold_sent:
        rel_str = ' '.join([str(i) for i in rel[:4]])
        gold_rel_strs.append(rel_str)
    # Make each ent in the predicted rel into a separate string so
    # we can search order-agnostically
    pred_ent_1_str = ' '.join([str(i) for i in pred[:2]])
    pred_ent_2_str = ' '.join([str(i) for i in pred[2:4]])
    # Check if ent 1 is in one of the relations
    ent1_list = [True if pred_ent_1_str
            in i else False for i in gold_rel_strs]
    # Check if ent 2 is in one of the relations
    ent2_list = [True if pred_ent_2_str in i
            else False for i in gold_rel_strs]
    # Indices that both have True in them are matches
    matches_list = [True if (ent1_list[i] & ent2_list[i]) else False
            for i in range(len(gold_rel_strs))]
    # This should at maximum have one match, delete once you've
    # written tests
    assert matches_list.count(True) <= 1

    # Determine return type
    if matches_list.count(True) == 1:
        return True
    else:
        return False


def get_doc_ent_counts(doc, gold_std, ent_pos_neg):
    """
    Get the true/false positives and false negatives for entity prediction for
    a single document.

    parameters:
        doc, dict: dygiepp-formatted dictionary, with keys "predicted_ner" and
            "ner"
        gold_std, dict, dygiepp-formatted dicitonary with gold standard for
            this doc, same key requirements as doc
        ent_pos_neg, dict: keys are "tp", "fp", "fn". Should keep passing the
            same object for each doc to get totals for the entire set of
            documents.

    returns:
        ent_pos_neg, dict: updated match counts for entities
    """
    # Go through each sentence for entities
    for pred_sent, gold_sent in zip(doc['predicted_ner'], gold_std['ner']):
        # Iterate through predictions and check for them in gold standard
        for pred in pred_sent:
            found = False
            for gold_ent in gold_sent:
                if pred[:2] == gold_ent[:2]:
                    ent_pos_neg['tp'] += 1
                    found = True
            if not found:
                ent_pos_neg['fp'] += 1
        # Iterate through gold standard and check for them in predictions
        for gold in gold_sent:
            found = False
            for pred in pred_sent:
                if gold[:2] == pred[:2]:
                    found = True
            if not found:
                ent_pos_neg['fn'] += 1

    return ent_pos_neg


def get_doc_rel_counts(doc, gold_std, rel_pos_neg):
    """
    Get the true/false positives and false negatives for relation prediction for
    a single document.

    parameters:
        doc, dict: dygiepp-formatted dictionary, with keys "predicted_relations"
            and "relations"
        gold_std, dict, dygiepp-formatted dicitonary with gold standard for
            this doc, same key requirements as doc
        rel_pos_neg, dict: keys are "tp", "fp", "fn". Should keep passing the
            same object for each doc to get totals for the entire set of
            documents.

    returns:
        rel_pos_neg, dict: updated match counts for relations
    """
    # Go through each sentence for relations
    for pred_sent, gold_sent in zip(doc['predicted_relations'],
            gold_std['relations']):
        # Iterate through the predictions and check for them in the gold
        # standard. Need to allow for the relations to be in a different
        # order than in the gold standard
        for pred in pred_sent:
            matched = check_rel_matches(pred, gold_sent)
            if matched:
                rel_pos_neg['tp'] += 1
            else:
                rel_pos_neg['fp'] += 1
        # Iterate through gold standard and check for them in predictions.
        # Still need to allow for the relations to be in a different order.
        for gold in gold_sent:
            matched = check_rel_matches(gold, pred_sent)
            if matched:
                continue
            else:
                rel_pos_neg['fn'] += 1

    return rel_pos_neg


def get_f1_input(gold_standard_dicts, prediction_dicts, input_type):
    """
    Get the number of true and false postives and false negatives for the
    model to calculate the following inputs for compute_f1 for both entities
    and relations:
        predicted = true positives + false positives
        gold = true positives + false negatives
        matched = true positives

    parameters:
        gold_standard_dicts, list of dict: dygiepp formatted annotations
        prediction_dicts, list of dict: dygiepp formatted predictions
        input_type, str: 'ent' or 'rel', determines which of the prediction
            types will be evaluated
    returns:
        predicted, int
        gold, int
        matched, int
    """
    pos_neg = {'tp':0, 'fp':0, 'fn':0}

    # Rearrange gold standard so that it's a dict with keys that are doc_id's
    gold_standard_dict = {d['doc_key']: d for d in gold_standard_dicts}

    # Go through the docs
    for doc in prediction_dicts:
        # Get the corresponding gold standard
        try:
            gold_std = gold_standard_dict[doc['doc_key']]
        except KeyError:
            verboseprint(
                f'Document {doc["doc_key"]} is not in the gold standard. '
                'Skipping this document for performance calculation.')
            continue
        # Get tp/fp/fn counts for this document
        if input_type == 'ent':
            pos_neg = get_doc_ent_counts(doc, gold_std, pos_neg)

        elif input_type == 'rel':
            pos_neg = get_doc_rel_counts(doc, gold_std, pos_neg)

    predicted = pos_neg['tp'] + pos_neg['fp']
    gold = pos_neg['tp'] + pos_neg['fn']
    matched = pos_neg['tp']

    return (predicted, gold, matched)


def draw_boot_samples(pred_dicts, gold_std_dicts, num_boot, input_type):
    """
    Draw bootsrtap samples.

    parameters:
        pred_dicts, list of dict: dicts of model predictions
        gold_std_dicts, list of dict: dicts of gold standard annotations
        num_boot, int: number of bootstrap samples to draw
        input_type, str: 'ent' or 'rel'

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
        # Since the lists are sorted the same, can use indices to get equivalent docs in gold std
        gold_samp = np.array([gold_std_dicts[i] for i in idx_list])
        # Calculate performance for the sample
        pred, gold, match = get_f1_input(gold_samp, pred_samp, input_type)
        prec, rec, f1 = compute_f1(pred, gold, match)
        # Append each of the performance values to their respective sample lists
        prec_samples.append(prec)
        rec_samples.append(rec)
        f1_samples.append(f1)

    return (prec_samples, rec_samples, f1_samples)


def get_performance_row(pred_file, gold_std_file, bootstrap, num_boot):
    """
    Gets performance metrics and returns as a list.

    parameters:
        pred_file, str: name of the file used for predictions
        gold_std_file, str: name of the gold standard file
        bootstrap, bool, whether or not to bootstrap a confidence interval
        num_boot, int: if bootstrap is True, how many bootstrap samples to take

    returns:
        row, list: [pred file name, gold std file name, ent/rel_precision,
            ent/rel_recall, ent/rel_f1] if bootstrap is false, same columns
            plus [ent/rel_prec_CI, ent/rel_rec_CI, ent/rel_f1_CI] if bootstrap
            is true
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

    # Check if the predictions include relations
    pred_rels = True
    try:
        [d['predicted_relations'] for d in pred_dicts]
    except KeyError:
        pred_rels = False

    # Bootstrap sampling
    if bootstrap:
        ent_boot_samples = draw_boot_samples(pred_dicts,
                                    gold_std_dicts, num_boot, 'ent')
        if pred_rels:
            rel_boot_samples = draw_boot_samples(pred_dicts,
                                    gold_std_dicts, num_boot, 'rel')

        # Calculate confidence interval
        ent_CIs = calculate_CI(ent_boot_samples[0], ent_boot_samples[1],
                ent_boot_samples[2])

        if pred_rels:
            rel_CIs = calculate_CI(rel_boot_samples[0],  rel_boot_samples[1],
                    rel_boot_samples[2])
        else:
            rel_CIs = [np.nan for i in range(3)]

        # Get means
        ent_means = [np.mean(samp) for samp in ent_boot_samples]
        if pred_rels:
            rel_means = [np.mean(samp) for samp in rel_boot_samples]
        else:
            rel_means = [np.nan for i in range(3)]

        return [
            basename(pred_file),
            basename(gold_std_file)] + ent_means + ent_CIs + rel_means + rel_CIs

    else:
        # Calculate performance
        pred_ent, gold_ent, match_ent = get_f1_input(gold_samp, pred_samp, 'ent')
        ent_means = compute_f1(pred_ent, gold_ent, match_ent)
        if pred_rels:
            pred_rel, gold_rel, match_rel = get_f1_input(gold_samp, pred_samp,
                    'rel')
            rel_means = compute_f1(pred_rel, gold_rel, match_rel)
        else:
            rel_means = [np.nan for i in range(3)]

        return [
            basename(pred_file),
            basename(gold_std_file)] + ent_means + rel_means


def main(gold_standard, out_name, predictions, bootstrap, num_boot):

    # Calculate performance
    verboseprint('\nCalculating performance...')
    df_rows = []
    for model in predictions:
        df_rows.append(get_performance_row(model, gold_standard,
                                           bootstrap, num_boot))

    verboseprint(df_rows)

    # Make df
    verboseprint('\nMaking dataframe...')
    if bootstrap:
        cols = ['pred_file', 'gold_std_file', 'ent_precision', 'ent_recall',
                'ent_F1', 'rel_precision', 'rel_precision', 'rel_f1',
                'ent_precision_CI', 'ent_recall_CI', 'ent_F1_CI',
                'rel_precision_CI', 'rel_recall_CI', 'rel_F1_CI']
    else:
        cols = ['pred_file', 'gold_std_file', 'ent_precision', 'ent_recall',
                'ent_F1', 'rel_precision', 'rel_recall', 'rel_F1']
    df = pd.DataFrame(
        df_rows,
        columns=cols)
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
    parser.add_argument('--bootstrap', action='store_true',
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
    args.prediction_dir = abspath(args.prediction_dir)

    verboseprint = print if args.verbose else lambda *a, **k: None

    pred_files = [
        join(args.prediction_dir, f) for f in listdir(args.prediction_dir)
        if f.startswith(args.use_prefix)
    ]

    main(args.gold_standard, args.out_name, pred_files, args.bootstrap, args.num_boot)
