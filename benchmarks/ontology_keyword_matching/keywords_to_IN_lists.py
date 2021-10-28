"""
Preprocess the keywords into a jsonlines file that can be read to make
efficient spacy patterns. The tokenizer used should be the same as what
will be used downstream in match_keywords.py.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, basename, splitext
import string

import spacy
import jsonlines
from tqdm import tqdm


def get_key_dicts(keywords):
    """
    Given a list of spacy-tokenized keywords, return a list of dict where
    one dict contains the lists to be passed as "IN" for that position in
    the pattern.

    parameters:
        keywords, list of spacy Doc objects: tokenized keywords

    returns:
        key_dicts, list of dict: dicts with token lists for ecah position
    """
    longest_keyword_len = len(max(keywords, key=len))
    key_dicts = []
    for key_len in range(1, longest_keyword_len+1):
        # Get all keywords of that length 
        keys = [key for key in keywords if len(key) == key_len]
        # Get the words in each position and make into a dict 
        if len(keys) > 0:
            key_dict = {}
            for position in range(key_len):
                pos_toks = [key[position].text for key in keys]
                key_dict[f'word_{position}'] = pos_toks
            key_dicts.append(key_dict)

    return key_dicts


def strip_keywords(keywords):
    """
    Strip keywords of all non-.!? punctuation in order to accurately match
    the text, which has been stripped by stripPunct.py.

    parameters:
        keywords, list of str: keywords to strip

    returns:
        stripped_keywords, list of str: stripped keywords
    """
    to_strip = (string.punctuation[1:13]  +
                string.punctuation[14:20] +
                string.punctuation[21:])

    stripped_keywords = []
    for keyword in keywords:
        stripped_keyword = keyword.translate(str.maketrans('', '', to_strip))
        stripped_keywords.append(stripped_keyword)

    return stripped_keywords


def main(keyword_path, out_loc, use_scispacy):

    # Read in, strip \n and irrelevant punctuation and lowercase
    print('\nReading in keywords...')
    with open(keyword_path) as f:
        keywords = [keyword.rstrip().lower() for keyword in f.readlines()]
    keywords = strip_keywords(keywords)

    # Tokenize keywords
    print('\nTokenizing keywords...')
    nlp_name = "en_core_sci_sm" if use_scispacy else "en_core_web_sm"
    nlp = spacy.load(nlp_name)
    keywords = [nlp(keyword) for keyword in tqdm(keywords)]

    # Make a dict for each keyword set 
    print('\nGetting key dicts...')
    key_dicts = get_key_dicts(keywords)

    # Write to output file
    print('\nWriting to output...')
    out_basename = splitext(basename(keyword_path))[0]
    out_name = f'{out_loc}/{out_basename}_preprocessed.jsonl'
    with jsonlines.open(out_name, mode='w') as writer:
        write.write(key_dicts)

    print('\nDone!')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Preprocess keywords')

    parser.add_argument('keyword_path', type=str,
            help='Path to keywords txt file, one keyword per line')
    parser.add_argument('out_loc', type=str,
            help='Path to save output')
    parser.add_argument('--use_scispacy', action='store_true',
            help='If provided, use scispacy to do the tokenization')

    args = parser.parse_args()

    args.keywords = abspath(args.keyword_path)
    args.out_loc = abspath(args.out_loc)

    main(args.keyword_path, args.out_loc, args.use_scispacy)
