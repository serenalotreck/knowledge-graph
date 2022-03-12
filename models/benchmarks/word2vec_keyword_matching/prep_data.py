"""
Prep abstract data for Word2Vec model

Call `get_data` function to do all data prepping (see function definition for more info)

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
from gensim.models.phrases import Phrases

FILE_DIR = os.path.dirname(os.path.realpath(__file__))  # Directory of this file


def read_abstracts(abstract_path, as_dict=False):
    """
    Read in abstract text from files.
    
    Also applies preprocessing by:
        1. Remove stopwords
        2. Convert all words to lowercase
        2. Remove non-alphabetic words/letters

    parameters:
        abstract_path, str: path to dir containing abstracts
        as_dict, bool: Whether to return as dictionary instead of a list
                       Usd when we want to preserve the file name for a given text

    returns:
        abstracts_text, list or dict: Words in abstract for each in directory
    """
    abstracts_text = {} if as_dict else []
    stopwords_dict = set(stopwords.words('english'))  # makes lookup O(1) instead of O(n)

    abstract_files = [x for x in os.listdir(abstract_path) if x.endswith("txt")]

    for abstract_file in tqdm(abstract_files, desc="Reading & cleaning abstracts"):

        with open(os.path.join(abstract_path, abstract_file), "r") as f:
            abs_words = word_tokenize(f.read())
            abs_text = [word.lower() for word in abs_words if word not in stopwords_dict and word.isalpha()]

            if as_dict:
                abstracts_text[abstract_file] = abs_text
            else:
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
