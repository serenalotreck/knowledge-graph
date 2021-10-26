"""
Extract entities based on keywords from the Planteome database

Adds a .ann file to the txt_dir for each .txt file with the same
name, containing the annotations based on keywords for that file.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, splitext, join
from os import listdir

import spacy
from spacy.matcher import Matcher


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


def main(txt_dir, keywords, use_scispacy):

    # Read in the keywords
    with open(keywords) as f:
        keywords = [keyword.rstrip() for keyword in f.readlines()]

    # Initialize a spacy model
    nlp_name = "en_core_sci_sm" if use_scispacy else "en_core_web_sm"
    nlp = spacy.load(nlp_name)

    # Initialize Matcher and define patterns
    matcher = Matcher(nlp.vocab)
    patterns = []
    for keyword in keywords:
        key_toks = nlp(keyword)
        pattern = [{"LOWER": key_tok.text.lower()} for key_tok in key_toks]
        patterns.append(pattern)
    matcher.add("Keywords", patterns)

    # Get valid files for matching
    txt_files = []
    for f in listdir(txt_dir):
        if f.endswith('.txt'):
            txt_files.append(join(txt_dir, f))

    # Get matches and make .ann file for each doc in txt_dir
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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Macth planteome keywords')

    parser.add_argument('txt_dir', type=str,
            help='Path to directory containing txt files to match')
    parser.add_argument('keywords', type=str,
            help='Path to .txt file containing keywords, with one keyword '
            'per row')
    parser.add_argument('--use-scispacy', action='store_true',
            help='If provided, use scispacy to do tokenization')

    args = parser.parse_args()

    args.txt_dir = abspath(args.txt_dir)
    args.keywords = abspath(args.keywords)

    main(args.txt_dir, args.keywords, args.use-scispacy)
