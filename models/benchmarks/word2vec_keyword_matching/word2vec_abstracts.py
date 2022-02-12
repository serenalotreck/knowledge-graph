"""
Fit word2vec on subset of abstracts

Author: Harry Shomer
"""
import os
import re
import json
import string
import argparse
from tqdm import tqdm
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from gensim.models import Word2Vec, KeyedVectors
from gensim.models.phrases import Phrases, Phraser


FILE_DIR = os.path.dirname(os.path.realpath(__file__))  # Directory of this file


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
    stopwords_dict = set(stopwords.words('english'))  # makes lookup O(1) instead of O(n)

    for abstract_file in tqdm(os.listdir(abstract_path), desc="Reading & cleaning abstracts"):
        with open(os.path.join(abstract_path, abstract_file), "r") as f:
            abs_words = word_tokenize(f.read())
            abs_text = [word.lower() for word in abs_words if word not in stopwords_dict and word.isalpha()]
            abstracts_text.append(abs_text)
    
    return abstracts_text


def read_keywords(keywords_dir):
    """
    Read in the Planteome keywords from keywords directory specified in args

    parameters:
        keywords_dir, str: Path to directory with keywords is in
    
    returns:
        keywords, list: list of all keywords
    """
    all_keywords = []

    with open(os.path.join(keywords_dir, "Planteome_keywords.json"), "r") as f:
        keywords_json = json.load(f)

        for file_keywords in tqdm(keywords_json.values(), desc="Retrieving all keywords"):
            all_keywords.extend(file_keywords)
    
    return all_keywords


# TODO: More?
def clean_keywords(keywords):
    """
    Keywords has a lot of nonsense in them

    Need to:
        2. Remove parentheses and contents
        1. Remove any punctuation issues from words (logic unashamedly borrowed from function 'strip_keywords' in the file ontology_keyword_matching.ontology_keyword_matching)
        3. Replace spaces with underscores. Proper format for ngrams in word2vec
        4. Lowercase!

    parameters:
        keywords, list of str: list of all planteome keywords
    
    returns:
        filtered_cleaned_keywords, list of str: Hopefully better than the original list
    """
    keep_punc = ("-", '.', '!', '?')  # These are ok
    remove_punc = [s for s in string.punctuation if s not in keep_punc] # These are not

    cleaned_keywords = []
    for kw in tqdm(keywords, desc="Cleaning keywords"):
        # 1. Remove parentheses and anything inside them
        # Logic = \( = match open parentheses, [^()] = Match everything except (), \) = match closing parentheses
        kw_new = re.sub(r'\([^()]*\)', '', kw)

        # 2. Remove unnecessry punctuation
        kw_new = re.sub(f"[{remove_punc}]", '', kw_new)
        
        # 3. Spaces -> Underscores
        kw_new = "_".join(kw_new.split())

        if kw_new != "":
            cleaned_keywords.append(kw_new.lower())
    
    return cleaned_keywords



def add_ngrams(abstracts, n):
    """
    Add n-grams up to size n. 
    
    Have to add them one at a time. So to get "n"-grams we need to keep passing to Phrases "n"-1 times. 

    parameters:
        abstracts_text, list of str: list of abstract texts
        n, int: Up to what "n" n-grams we should add
    
    returns:
        ngram_phrases, list of list of str: Original abstract text with added ngrams
    """
    # Get bigrams
    ngram_phrases = Phrases(abstracts, min_count=5)

    # 2 because we already have unigram and bigram
    for _ in range(n-2):
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
    
    raise ValueError(f"Argument model-type must be either 'skip' or 'cbow'. {model_type} is an invalid value.")


def get_data(abstract_path, keywords_path, ngrams):
    """
    Get and clean the abstracts and keywords data. 

    Also add ngrams to abstracts if n > 1

    parameters:
        abstract_path, str: path to directory of abstract data
        keywords_path, str: path to directory of keywords data
        ngrams, int: the "n" in ngrams. 

    returns:
        abstracts, keywords, tuple of lists: lists of abstracts and keywords 
    """
    abstracts = read_abstracts(abstract_path)
    keywords = read_keywords(keywords_path)
    keywords = clean_keywords(keywords)

    if ngrams > 1:
        ngrams_phrases = add_ngrams(abstracts, ngrams)
        abstracts = list(ngrams_phrases[abstracts])
    
    return abstracts, keywords


def fit_word2vec(abstracts, model_type, ngrams):
    """
    Fit word2vec on the set of abstracts

    parameters:
        abstracts_text, list of list of str: list of abstract texts
        model_type, str: Either 'skip' or 'cbow'
        ngrams, int: Size of n-grams
    
    returns:
        model: gensim.models.Word2Vec: model object for word2vec 
    """
    # TODO: Default params for now...
    model = Word2Vec(sg=get_model_indicator(model_type))
    model.build_vocab(abstracts)

    print("Training word2vec on abstracts...")
    model.train(abstracts, total_examples=model.corpus_count, epochs=30, report_delay=1)

    # TODO: Save this in its own directory or wherever
    model.wv.save(os.path.join(FILE_DIR, f"{model_type}_{ngrams}-gram.wordvectors"))

    return model


def match_keywords(keywords, word_vectors, file_name, sim_threshold=0):
    """
    For all the keywords in the vocab, get its similarity vs all other non-keyword vocab words.
    To filter, we only keep those that have a simialrity above a threshold.

    We both save and return the results because why not

    parameters:
        keywords, list: list of keywords
        w2v_model, gensim.models.KeyedVectors: Word vectors for all words trained in Word2vec model
        file_name, str: Name of file to save results in 
        sim_threshold, float: Threshold for similarity
    
    returns:
        most_similar_for_keys, dict: keywords -> words above threshold
    """
    w2v_vocab = set(word_vectors.key_to_index.keys())
    keywords_in_vocab = set([k for k in keywords if k in w2v_vocab])

    most_similar_for_keys = {}

    for keyword in tqdm(keywords_in_vocab, desc="Get words similiar to keywords"):
        # Sim of key vs all other words in vocab
        sim_vs_all_vocab = word_vectors.most_similar(positive=[keyword], topn=len(w2v_vocab))

        # Filter out words that are already keywords
        # Also extracts words with sim >= threshold
        sim_vs_non_keywords = [w for w in sim_vs_all_vocab if w[0] not in keywords_in_vocab and w[1] >= sim_threshold]

        most_similar_for_keys[keyword] = [w for w in sim_vs_non_keywords]
    
    # Store threshold as int. So instead of 0-1 -> 0-100
    file_name = f"{file_name}_keyword_sim_{int(sim_threshold * 100)}.json"

    with open(os.path.join(FILE_DIR, file_name), "w", encoding='utf-8') as f:
        json.dump(most_similar_for_keys, f, indent=4, ensure_ascii=False) 

    return most_similar_for_keys


def main():
    parser = argparse.ArgumentParser(description='Word2vec on abstracts')

    parser.add_argument("--abstract-path", help='path to dir with abstracts you want to cluster', type=str, default=None)
    parser.add_argument("--keywords-path", help='path to dir with planteome keywords', type=str, default=None)

    parser.add_argument("--ngrams", help="Length of possible grams to create (i.e. 'n'). Defaults to 1.", type=int, default=1)
    parser.add_argument("--model-type", help="'skip' for Skip-gram and 'cbow' for CBOW. Defaults to 'cbow'", type=str, default="cbow")

    parser.add_argument("--calc-keyword-sim", help="When set, we get the words in vocab most similar to keywords", action="store_true", default=False)
    parser.add_argument("--sim-threshold", help="Similarity threshold when comparing keywords against vocab. Defaults to 0.75", type=float, default=0.75)

    args = parser.parse_args()

    abstracts, keywords = get_data(args.abstract_path, args.keywords_path, args.ngrams)
    
    # When args.calc-keyword-sim flag is set, we assume the model has already be trained
    if args.calc_keyword_sim:
        base_file_name = f"{args.model_type}_{args.ngrams}-gram"        
        wv = KeyedVectors.load(os.path.join(FILE_DIR, f"{base_file_name}.wordvectors"), mmap='r')
        match_keywords(keywords, wv, base_file_name, args.sim_threshold)
    else:
        fit_word2vec(abstracts, args.model_type, args.ngrams)


if __name__ == "__main__":
    main()
