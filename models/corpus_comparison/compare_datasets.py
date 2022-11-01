"""
Script to compare two datasets. Outputs a summary file and plots where
appropriate.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath

import jsonlines
from dataset import Dataset
from gensim.models import KeyedVectors


def get_gram_embeddings(dset1, dset2, word2vecs):
    """
    Sorts vordvectors from model into separate dicts for each dataset, and
    combines them into a dict of dicts where they overall keys are the dataset
    names.

    parameters:
        dset1, Dataset obj: obj for dataset1 with vocab already set
        dset2, Dataset obj: obj for dataset2 with vocab already set
        word2vecs, str: path to vectors from pretrained word2vec model

    returns:
        sep_vecs, dict of dict: keys are dset names, values are dicts where keys
            are ngrams and values are their vectors
    """
    # Load vectors
    vecs = KeyedVectors.load(word2vecs)

    # Sort them by dataset
    sep_vecs = {}
    for dset in [dset1, dset2]:
        dset_combined_vocab = dset.vocab['unigrams'] + dset.vocab['bigrams'] \
                + dset.vocab['trigrams']
        dset_vecs = {k:vec for k, vec in vecs.items() if k in
                dset_combined_vocab}
        sep_vecs[dset.get_dset_name()] = dset_vecs

    return sep_vecs


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
        oov, dict: contains the words that are oov for each dset
        oov_fracs, dict: contains the metrics. Keys are metric names and values
            are the metrics.
    """
    # Define names for dsets 1 & 2
    dset1_name = dset1.get_dataset_name()
    dset2_name = dset2.get_dataset_name()

    # Get the vocabularies
    dset1_vocab = dset1.get_dataset_vocab()
    dset2_vocab = dset2.get_dataset_vocab()

    # Compare
    oovs = {}
    for key in dset1_vocab.keys():
        oov_dset1 = dset1_vocab[key] - dset2_vocab[key]
        oov_dset2 = dset2_vocab[key] - dset1_vocab[key]
        oovs[f'{key}_oov_{dset1_name}'] = oov_dset1
        oovs[f'{key}_oov_{dset2_name}'] =  oov_dset2

    # Get fraction
    oov_fracs = {}
    for key in oovs.keys():
        gram_num = key.split('_')[0]
        if dset1_name in key:
            oov_frac = len(oovs[key])/len(dset1_vocab[gram_num])
        elif dset2_name in key:
            oov_frac = len(oovs[key])/len(dset2_vocab[gram_num])
        oov_fracs[f'{key}_frac'] = oov_frac

    return oovs, oov_fracs


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


def main(dset1_name, dset1_path, dset2_name, dset2_path,
        word2vecs, out_loc, out_prefix):

    # Read in the datasets
    verboseprint('\nReading in the datasets...')
    dset1 = read_dset(dset1_path, dset1_name)
    dset2 = read_dset(dset2_path, dset2_name)

    # Look for out-of-vocabulary words
    verboseprint('\nComparing out-of-vocabulary words...')
    oov, oov_fracs = quantify_out_of_vocab(dset1, dset2)
    oov_save_name = f'{out_loc}/{out_prefix}_oov_comparison.jsonl'
    with jsonlines.open(oov_save_name, mode='w') as writer:
        writer.write([oov_fracs, oov])
    verboseprint('Saved out-of-vocabulary comparison as {oov_save_name}')

    # Compare token embeddings
    verboseprint('\nGetting uni-, bi-, and trigram embeddings...')
    word_vecs = get_gram_embeddings(dset1, dset2, word2vecs)
    word_vec_save_name = f'{out_loc}/{out_prefix}_word_vec_per_dset.jsonl'
    with jsonlines.open(word_vec_save_name, mode='w') as writer:
        writer.write(word_vecs)
    verboseprint('Saved wordvec comparison as {word_vev_save_name}')
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
    parser.add_argument('word2vecs', type=str,
            help='Path to vectors from pretrained word2vec model to use for '
            'token embedding comparison')
    parser.add_argument('out_loc', type=str,
            help='Path to save output')
    parser.add_argument('out_prefix', type=str,
            help='String to prepend to all output file names')

    args = parser.parse_args()

    args.dset1 = abspath(args.dset1)
    args.dset2 = abspath(args.dset2)
    args.word2vecs = abspath(args.word2vecs)
    args.out_loc = abspath(args.out_loc)

    main(args.dset1_name,  args.dset1, args.dset2_name, args.dset2,
            args.word2vecs, args.out_loc, args.out_prefix)
