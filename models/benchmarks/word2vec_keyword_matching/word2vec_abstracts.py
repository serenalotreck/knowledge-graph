"""
Fit word2vec on subset of abstracts
"""
import os
import json
import argparse
from tqdm import tqdm
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from gensim.models import Word2Vec
from gensim.models.phrases import Phrases, Phraser


def read_abstracts(abstract_path):
    """
    Read in abstract text from files.
    
    Also applies preprocessing by:
        1. Remove stopwords
        2. Convert all words to lowercase
        2. Remove non-alphabetic words/letters

    parameters:
        abstract_path, str: path to dir containing abstracts

    returns:
        abstracts_text, list of list of str: list of abstract texts
    """
    abstracts_text = []
    stopwords_dict = {w: None for w in stopwords.words('english')}  # makes lookup O(1) instead of O(n)

    for abstract_file in tqdm(os.listdir(abstract_path), desc="Reading & cleaning abstracts"):
        with open(os.path.join(abstract_path, abstract_file), "r") as f:
            abs_words = word_tokenize(f.read())
            abs_text = [word.lower() for word in abs_words if word not in stopwords_dict and word.isalpha()]
            abstracts_text.append(abs_text)
    
    return abstracts_text


def add_ngrams(abstracts, n):
    """
    Add n-grams up to size n

    parameters:
        abstracts_text, list of str: list of abstract texts
        n, int: Up to what "n" n-grams we should add
    
    returns:
        ngram_phrases, list of list of str: Original abstract text with added ngrams
    """
    # TODO: Modify params of Phrases?

    ngram_phrases = Phrases(abstracts, min_count=5)

    for _ in range(n-2): # 2 because we already have unigram and bigram
        ngram_phrases = Phrases(ngram_phrases[abstracts], min_count=5)
    
    return ngram_phrases


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
    
    return ValueError(f"Argument model-type must be either 'skip' or 'cbow'. {model_type} is an invalid value.")


def fit_word2vec(abstracts, model_type):
    """
    Fit word2vec on the set of abstracts

    parameters:
        abstracts_text, list of list of str: list of abstract texts
        model_type, str: Either 'skip' or 'cbow'
    
    returns:

    """
    # TODO: Default params for now...
    model = Word2Vec(sg=get_model_indicator(model_type))
    model.build_vocab(abstracts)

    print("Training word2vec on abstracts...")
    model.train(abstracts, total_examples=model.corpus_count, epochs=30, report_delay=1)

    # print("\n\n")

    # for i in ["salicylic", "ethylene", "jasmonic", "gibberellic", "plant", "hormone", "acid"]:
    #     print("===>", i)
    #     print(model.wv.most_similar(positive=[i]))
    #     print("\n")


def main():
    parser = argparse.ArgumentParser(description='Word2vec on abstracts')

    parser.add_argument("--abstract-path", help='path to dir with abstracts you want to cluster', type=str, default=None)
    parser.add_argument("--model-type", help="'skip' for skip-gram and 'cbow' for CBOW", type=str, default="cbow")
    parser.add_argument("--ngrams", help="Whether to use bigrams", type=int, default=1)
    parser.add_argument("--trigrams", help="Whether to use trigrams", action='store_true', default=False)

    args = parser.parse_args()

    abstracts = read_abstracts(args.abstract_path)

    if args.ngrams > 1:
        ngrams_phrases = add_ngrams(abstracts, args.ngrams)
        abstracts = list(ngrams_phrases[abstracts])
        #print([i for i in ngrams_phrases[abstracts]][:5])


    fit_word2vec(abstracts, args.model_type)


if __name__ == "__main__":
    main()
