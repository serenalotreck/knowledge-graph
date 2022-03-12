"""
Get matches for word2vec model on abstracts and save as brat file

Author: Harry Shomer
"""
import os
import argparse
from tqdm import tqdm
from gensim.models import  KeyedVectors

import spacy 
from spacy.matcher import PhraseMatcher

import prep_data

FILE_DIR = os.path.dirname(os.path.realpath(__file__))  # Directory of this file


def match_keywords(w2v_file_path, keywords, sim_threshold):
    """
    For all the keywords in the vocab, get its similarity vs all other non-keyword vocab words.
    To filter, we only keep those that have a similarity above a threshold.

    parameters:
        w2v_file_path, str: file containing gensim.models.KeyedVectors of model
        keywords, list: list of keywords
        sim_threshold, float: Threshold for similarity
    
    returns:
        most_similar_for_keys, list: words above threshold
    """
    word_vectors = KeyedVectors.load(w2v_file_path, mmap='r')

    w2v_vocab = set(word_vectors.key_to_index.keys())
    keywords_in_vocab = set([k for k in keywords if k in w2v_vocab])

    most_similar_for_keys = []

    for keyword in tqdm(keywords_in_vocab, desc="Get words similiar to keywords"):
        # Sim of key vs all other words in vocab
        sim_vs_all_vocab = word_vectors.most_similar(positive=[keyword], topn=len(w2v_vocab))

        # Filter out words that are already keywords
        # Also extracts words with sim >= threshold
        most_similar_for_keys.extend([w[0] for w in sim_vs_all_vocab if w[0] not in keywords_in_vocab and w[1] >= sim_threshold])

    return most_similar_for_keys


def matches_to_brat(matches, doc):
    """
    Converts output from spacy Matcher to brat annotation format.
    
    NOTE: Taken from ../ontology_keyword_matching/phrasematch_keywords_refined.py

    parameters:
        matches, list of match tuples: (match_id, start, end),
            must all be from same document
        doc, spacy doc object: doc dobject corresponding to the matches

    returns:
        brat_str, str: a string encoding a valid brat .ann file for
            the mactches in question
    """
    brat_str = ''
    match_num = 1
    for match_id, start, end in matches:
        match_span = doc[start:end]
        start_char, end_char = match_span.start_char, match_span.end_char
        text = match_span.text
        match_type = 'ENTITY'
        brat_s = f'T{match_num}\t{match_type} {start_char} {end_char}\t{text}\n'
        brat_str += brat_s
        match_num += 1
    return brat_str



def match_abstracts(abstract_path, key_matches, use_scispacy):
    """
    Find matches in abstracts. Write output to BRAT file for each abstract
    
    Uses:
        1. Default vocab loaded by spacy. Either standard english or scispacy
        2. Similar words matched from word2vec model
    
    parameters:
        abstract_path, str: path to abstracts directory
        key_matches, list: List of similar words matched from keywords
        use_scispacy, bool: Whether to use scispacy or regular english vocab
    
    returns:
        none
    """
    key_matches = [k.replace("_", " ") for k in key_matches] # Convert from ngram form to original
    
    nlp_name = "en_core_sci_sm" if use_scispacy else "en_core_web_sm"
    nlp = spacy.load(nlp_name)

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    matcher.add("Keywords", [nlp.make_doc(key) for key in key_matches])

    abstract_files = [x for x in os.listdir(abstract_path) if x.endswith("txt")]

    for abstract_file in tqdm(abstract_files, desc="Getting abstract matches"):

        if not abstract_file.endswith("txt"):
            continue

        with open(os.path.join(abstract_path, abstract_file), "r") as f:
            abstract_text = f.read().lower()

        doc = nlp(abstract_text)
        matches = matcher(doc)

        # Convert matches to brat format 
        brat_str = matches_to_brat(matches, doc)

        # Save as .ann file with same name as txt file
        basename = os.path.join(abstract_path, os.path.splitext(abstract_file)[0])
        with open(f'{basename}.ann', 'w') as myf:
            myf.write(brat_str)


def main():
    parser = argparse.ArgumentParser(description='Word2vec on abstracts')

    parser.add_argument("--word2vec-path", help="Path of model file", type=str)
    parser.add_argument("--abstract-path", help='path to dir with abstracts you want to cluster', type=str, default=None)
    parser.add_argument("--keywords-path", help='path to dir with planteome keywords', type=str, default=None)
    parser.add_argument('--use-scispacy', action='store_true', help='If provided, use scispacy to do tokenization')

    parser.add_argument("--ngrams", help="Length of possible grams to create (i.e. 'n'). Defaults to 1.", type=int, default=1)
    parser.add_argument("--sim-threshold", help="Similarity threshold when comparing keywords against vocab. Defaults to 0.75", type=float, default=0.75)

    args = parser.parse_args()

    _, keywords = prep_data.get_data(args.abstract_path, args.keywords_path, args.ngrams)

    key_matches = match_keywords(args.word2vec_path, keywords, args.sim_threshold)
    match_abstracts(args.abstract_path, key_matches, args.use_scispacy)



if __name__ == "__main__":
    main()
