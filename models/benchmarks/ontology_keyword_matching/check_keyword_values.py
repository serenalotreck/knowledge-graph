"""
Explore what files have "silly words" (in, at, the, etc) as single keywords
to identify the source of errors in annotation.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, splitext
import json
from collections import defaultdict


def main(files):

    # Read in files
    file_dicts = {}
    for f in files:
        with open(f) as myf:
            data_dict = json.load(myf)
            file_dicts[f] = data_dict

    # Look for words in silly words list and entries with multiple commas
    silly_words = ['in', 'at', 'the', '17', 'green', 'may', 'but', 'and',
            'had', 'to']
    silly_file_dicts = defaultdict(lambda: defaultdict(list))
    comma_file_dicts = defaultdict(lambda: defaultdict(list))
    for json_path, myjson in file_dicts.items():
        for gaf_path, keywords in myjson.items():
            for keyword in keywords:
                for silly_word in silly_words:
                    if silly_word == keyword.lower():
                        silly_file_dicts[json_path][gaf_path].append(keyword)
                    if len(keyword.split(',')) > 2:
                        comma_file_dicts[json_path][gaf_path].append(keyword)

    # Write out findings
    for save_path, myjson in silly_file_dicts.items():
        save_path = f'{splitext(save_path)[0]}_silly_words.json'
        with open(save_path, 'w') as myf:
            json.dump(myjson, myf)
    for save_path, myjson in comma_file_dicts.items():
        save_path = f'{splitext(save_path)[0]}_comma_syns.json'
        with open(save_path, 'w') as myf:
            json.dump(myjson, myf)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Find silly words')

    parser.add_argument('files', nargs='+',
            help='Files to check')

    args = parser.parse_args()

    args.files = [abspath(f) for f in args.files]

    main(args.files)

