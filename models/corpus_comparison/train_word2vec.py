"""
Script to train a word2vec model on the corpora to compare, and save the
wordvectors from the trained model for future use.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath

import jsonlines
from gensim.models import Word2Vec
from nltk.util import ngrams
from dataset import Dataset


def read_datasets(corpora):
    """
    Read in datasets as Dataset objects.

    parameters:
        corpora, list of str: list of paths to read

    returns:
        corpora_objs, list of Dataset objs: the processed corpora
    """
    corpora_objs = []
    for corpus in corpora:
        corpus_list = []
        with jsonlines.open(corpus) as reader:
            for obj in reader:
                corpus_list.append(obj)
        corpus_obj = Dataset(processed_dataset=corpus_list)
        corpora_objs.append(corpus_obj)

    return corpora_objs


def build_train_set(corpora):
    """
    Creates a training set formatted for word2vec from the supplied corpora.
    Inspired by code from
    https://suyashkhare619.medium.com/how-to-deal-with-multi-word-phrases-or-n-grams-while-building-a-custom-embedding-eec547d1ab45

    parameters:
        corpora, list: list of paths to the datasets

    returns:
        train_set, list of list: sentences containing uni-, bi- and trigrams
            for training word2vec
    """
    # Read in the datasets
    datasets = read_datasets(corpora)

    # Generate training data
    train_set = []
    for dset in datasets:
        for sentence in dset.get_dataset_sents():
            uni = sentence
            bi = ['_'.join(ngr) for ngr in ngrams(uni, 2)]
            tri = ['_'.join(ngr) for ngr in ngrams(uni, 3)]
            data = uni + bi + tri
            train_set.append(data)

    return train_set


def main(corpora, out_loc, out_prefix):

    # Make training set
    verboseprint('\nBuilding training set...')
    train_set = build_train_set(corpora)
    verboseprint('Trainset complete! Example sentence:')
    verboseprint(train_set[0])

    # Train model
    verboseprint('\nTraining model...')
    model = Word2Vec(train_set, sg=1) # sg=1 sets skip-gram

    # Save wordvectors
    verboseprint('\nSaving word vectors...')
    save_name = f'{out_loc}/{out_prefix}_word2vec_skipgram.wordvectors'
    model.wv.save(save_name)
    verboseprint(f'Vectors saved as {save_name}')
    verboseprint('\nDone!\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train word2vec')

    parser.add_argument('-corpora', nargs='+',
            help='List of paths to corpora to use in training set')
    parser.add_argument('-out_loc', type=str,
            help='Path to save the trained model')
    parser.add_argument('-out_prefix', type=str,
            help='String to prepend to save name')
    parser.add_argument('-v', '--verbose', action='store_true',
            help='Whether ror not to print updates to stdout')

    args = parser.parse_args()

    args.corpora = [abspath(p) for p in args.corpora]
    args.out_loc = abspath(args.out_loc)

    verboseprint = print if args.verbose else lambda *a, **k: None

    main(args.corpora, args.out_loc, args.out_prefix)
