"""
Extract entities based on keywords from the Planteome database

Refined to account for erroneously matching simple words and for
certain comma-separated fields.

Adds a .ann file to the txt_dir for each .txt file with the same
name, containing the annotations based on keywords for that file.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, splitext, join
from os import listdir
import string
import time
import json

import spacy
from spacy.matcher import PhraseMatcher


def matches_to_brat(matches, doc):
    """
    Converts output from spacy Matcher to brat annotation format.

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


def strip_keywords(keywords):
    """
    Strip keywords of all non-.!? punctuation in order to accurately
    match the text, which has been stripped by stripPunct.py.

    parameters:
        keywords, list of str: keywords to strip

    returns:
        stripped_keywords, list of str: stripped keywords
    """
    to_strip = (string.punctuation[1:13] +
                string.punctuation[14:20] +
                string.punctuation[21:])

    stripped_keywords = []
    for keyword in keywords:
        stripped_keyword = keyword.translate(str.maketrans('','', to_strip))
        stripped_keywords.append(stripped_keyword)

    return stripped_keywords


def main(txt_dir, keyword_paths, use_scispacy):

    # Read in the keywords
    print('\nReading in keywords...')
    keywords = []
    for keyword_path in keyword_paths:
        with open(keyword_path) as f:
            path_keywords = json.load(f)
            for filepath, words in path_keywords.items():
                keywords += words
    keywords = strip_keywords(keywords)

    # Initialize a spacy model
    print('\nInitializing spacy model...')
    nlp_name = "en_core_sci_sm" if use_scispacy else "en_core_web_sm"
    nlp = spacy.load(nlp_name)

    # Initialize Matcher and define patterns
    print('\nAdding keyword patterns to the Matcher...')
    start_matcher = time.perf_counter()
    matcher1 = PhraseMatcher(nlp.vocab, attr="LOWER")
    ################# Additions to deal with edge cases ######################
    matcher2 = PhraseMatcher(nlp.vocab) # Case-sensitive matcher
    lower_patterns = []
    sensitive_patterns = []
    for key in keywords:
        if ', putative, expressed' in key:
            key = key[:-len(', putative, expressed')-1]
        key_doc = nlp.make_doc(key)
        if (len(key_doc) == 1) and (not key_doc[0].is_digit): # Skip if just made of digits
            if key_doc[0].is_upper: # Case-sensitive match for all-uppercase
                sensitive_patterns.append(key_doc)
            else: # All other single word tokens
                lower_patterns.append(key_doc)
        else: # All multi-word tokens
            lower_patterns.append(key_doc)
    ##########################################################################
    matcher1.add("Keywords", lower_patterns)
    matcher2.add("Keywords", sensitive_patterns)
    end_matcher = time.perf_counter()
    print(f'Added all {len(lower_patterns) + len(sensitive_patterns)} '
            f'patterns to matchers in {end_matcher-start_matcher:.2f} seconds')

    # Get valid files for matching
    print('\nFinding files to match...')
    txt_files = []
    for f in listdir(txt_dir):
        if f.endswith('.txt'):
            txt_files.append(join(txt_dir, f))

    # Get matches and make .ann file for each doc in txt_dir
    print('\nGetting matches...')
    for f in txt_files:
        # Get text, tokenize, and get matches
        with open(f) as myf:
            text = myf.read()
        doc = nlp(text)
        matches = matcher1(doc) + matcher2(doc)

        # Convert matches to brat format 
        brat_str = matches_to_brat(matches, doc)

        # Save as .ann file with same name as txt file
        basename = splitext(f)[0]
        with open(f'{basename}.ann', 'w') as myf:
            myf.write(brat_str)

    print('\nDone!')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Macth planteome keywords')

    parser.add_argument('txt_dir', type=str,
            help='Path to directory containing txt files to match')
    parser.add_argument('keyword_paths', nargs='+',
            help='Paths to .json file containing file names as keys and '
            'lists of keywords as values')
    parser.add_argument('--use_scispacy', action='store_true',
            help='If provided, use scispacy to do tokenization')

    args = parser.parse_args()

    args.txt_dir = abspath(args.txt_dir)
    args.keyword_paths = [abspath(path) for path in args.keyword_paths]

    main(args.txt_dir, args.keyword_paths, args.use_scispacy)
