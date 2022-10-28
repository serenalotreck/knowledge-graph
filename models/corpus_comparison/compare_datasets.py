"""
Script to compare two datasets. Outputs a summary file and plots where
appropriate.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath

import jsonlines
from dataset import Dataset


def quantify_out_of_vocab(dset1, dset2):
    """
    Quantify metrics about how much of each dataset is out of the vocabulary of
    the other. Calculates:
        * Fraction of dset1 that is OOV for dset2
        * Fraction of dset2 that is OOV for dset1
        * TODO decide if there are other metrics I'd like to see

    parameters:
        dset1, Dataset obj: first dataset
        dset2, Datasetobj: second dataset

    returns:
        metrics, dict: contains the metrics. Keys are metric names and values
            are the metrics.
        oov, dict: contains the words that are oov for each dset
    """
    # Get the vocabularies
    dset1_vocab = dset1.get_dataset_vocab()
    dset2_vocab = dset2.get_dataset_vocab()

    # Compare
    oov_dset1 = dset1_vocab - dset2_vocab
    oov_dset2 = dset2_vocab - dset1_vocab

    # Get fraction
    oov_dset1_frac = len(oov_dset1)/len(dset1_vocab)
    oov_dset2_frac = len(oov_dset2)/len(dset2_vocab)

    # Make dicts
    dset1_name = dset1.get_dataset_name()
    dset2_name = dset2.get_dataset_name()
    metrics = {f'{dset1_name}_oov_frac':oov_dset1_frac,
            f'{dset2_name}_oov_frac':oov_dset2_frac}
    oov = {f'{dset1_name}_oov_words':oov_dset1,
            f'{dset2_name}_oov_words':oov_dset2}

    return metrics, oov

def read_dset(path, dset_name):
    """
    Read in a dataset as a Dataset object from a file path..

    parameters:
        path, str: absolute path to the dataset jsonl file
        dset_name, str: name of the dataset
    returns:
        dset, Dataset object: dataset object for this dataset
    """
    dset_list = []
    with jsonlines.open(path) as reader:
        for obj in reader:
            dset_list.append(obj)
    dset = Dataset(dset_name, dset_list)

    return dset


def main(dset1_name, dset1_path, dset2_name, dset2_path, out_loc, out_prefix):

    # Read in the datasets
    dset1 = read_dset(dset1_path, dset1_name)
    dset2 = read_dset(dset2_path, dset2_name)

    # Look for out-of-vocabulary words
    metrics, oov = quantify_out_of_vocab(dset1, dset2)
    ## Printing for now just to see if it works
    print(metrics)
    # Compare token embeddings
    ## TODO

    # Compare document embeddings
    ## TODO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Compare two annotated datasets')

    parser.add_argument('dset1_name', type=str,
            help='String identifying dataset 1')
    parser.add_argument('dset1', type=str,
            help='Path to jsonl file containing the first dataset to compare')
    parser.add_argument('dset2_name', type=str,
            help='String identifying dataset 2')
    parser.add_argument('dset2', type=str,
            help='Path to jsonl file containing the second dataset to compare')
    parser.add_argument('out_loc', type=str,
            help='Path to save output')
    parser.add_argument('out_prefix', type=str,
            help='String to prepend to all output file names')

    args = parser.parse_args()

    args.dset1 = abspath(args.dset1)
    args.dset2 = abspath(args.dset2)
    args.out_loc = abspath(args.out_loc)

    main(args.dset1_name,  args.dset1, args.dset2_name, args.dset2,
            args.out_loc, args.out_prefix)
