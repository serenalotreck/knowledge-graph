"""
Fit word2vec on subset of abstracts

Author: Harry Shomer
"""
import os
import json
import argparse
from tqdm import tqdm
from gensim.models import Word2Vec, KeyedVectors

import prep_data

FILE_DIR = os.path.dirname(os.path.realpath(__file__))  # Directory of this file



def get_model_indicator(model_type):
    """
    Word2vec can either be fit using skip-gram of CBOW. The gensim implementation (for some reason), encodes a 1 for skip-gram
    and 0 for cbow. Here we convert the cmd line arg to the proper number and raise an error for an invalid model type

    raises:
        ValueError: when input isn't one of 'skip' or 'cbow'

    parameters:
        model_type, str: Either 'skip' or 'cbow'
    
    returns:
        model_indicator: int, 1 for skip-gram and 0 for cbow
    """
    model_type = model_type.lower()

    if model_type == "cbow":
        return 0
    if model_type == "skip":
        return 1
    
    raise ValueError(f"Argument model-type must be either 'skip' or 'cbow'. {model_type} is an invalid value.")


def fit_word2vec(abstracts, model_type, ngrams, out_dir):
    """
    Fit word2vec on the set of abstracts

    parameters:
        abstracts_text, list of list of str: list of abstract texts
        model_type, str: Either 'skip' or 'cbow'
        ngrams, int: Size of n-grams
        out_dir, str: Directory to save output file in
    
    returns:
        model: gensim.models.Word2Vec: model object for word2vec 
    """
    # TODO: Default params for now...
    model = Word2Vec(sg=get_model_indicator(model_type))
    model.build_vocab(abstracts)

    print(f"Training word2vec on {len(abstracts)} abstracts...")
    model.train(abstracts, total_examples=model.corpus_count, epochs=30, report_delay=1)

    file_path = os.path.join(out_dir, f"{model_type}_{ngrams}-gram.wordvectors")

    print(f"Saving model as {file_path}")
    model.wv.save(file_path)

    return model


def main():
    parser = argparse.ArgumentParser(description='Word2vec on abstracts')

    parser.add_argument("--abstract-path", help='path to dir with abstracts you want to cluster', type=str, default=None)
    parser.add_argument("--keywords-path", help='path to dir with planteome keywords', type=str, default=None)

    parser.add_argument("--ngrams", help="Length of possible grams to create (i.e. 'n'). Defaults to 1.", type=int, default=1)
    parser.add_argument("--model-type", help="'skip' for Skip-gram and 'cbow' for CBOW. Defaults to 'cbow'", type=str, default="cbow")

    parser.add_argument("--out-dir", help="Directory to save model in", type=str, default=os.path.join(FILE_DIR, "word2vec_models"))

    args = parser.parse_args()

    abstracts, keywords = prep_data.get_data(args.abstract_path, args.keywords_path, args.ngrams)
    fit_word2vec(abstracts, args.model_type, args.ngrams, args.out_dir)


if __name__ == "__main__":
    main()
