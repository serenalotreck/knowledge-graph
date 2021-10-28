"""
Extract entities based on keywords from the Planteome database

Adds a .ann file to the txt_dir for each .txt file with the same
name, containing the annotations based on keywords for that file.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, splitext, join
from os import listdir
import string
import time

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


def main(txt_dir, keyword_path, use_scispacy):

    # Read in the keywords
    print('\nReading in keywords...')
    with open(keyword_path) as f:
         keywords = strip_keywords([key.rstrip() for key in f.readlines()])

    # Initialize a spacy model
    print('\nInitializing spacy model...')
    nlp_name = "en_core_sci_sm" if use_scispacy else "en_core_web_sm"
    nlp = spacy.load(nlp_name)

    # Initialize Matcher and define patterns
    print('\nAdding keyword patterns to the Matcher...')
    start_matcher = time.perf_counter()
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(key) for key in keywords]
    matcher.add("Keywords", patterns)
    end_matcher = time.perf_counter()
    print(f'Added all {len(patterns)} patterns to matcher in {end_matcher-start_matcher}')

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
        matches = matcher(doc)

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
    parser.add_argument('keyword_path', type=str,
            help='Path to .txt file containing one keyword per line')
    parser.add_argument('--use_scispacy', action='store_true',
            help='If provided, use scispacy to do tokenization')

    args = parser.parse_args()

    args.txt_dir = abspath(args.txt_dir)
    args.keywords = abspath(args.keyword_path)

    main(args.txt_dir, args.keyword_path, args.use_scispacy)
