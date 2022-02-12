"""
Script to obtain keywords from a directory of .assoc files, in this case
downloaded from Planteome.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, join
from os import listdir
import json
from collections import defaultdict

from goatools.anno.gaf_reader import GafReader
from tqdm import tqdm


def main(planteome_dir, output_dir, file_prefix):

    # Get names of GAF files
    print('\nGetting names of .assoc files...')
    gaf_files = []
    for f in listdir(planteome_dir):
        if f.endswith('.assoc'):
            gaf_files.append(join(planteome_dir, f))

    # Read in GAF files
    print('\nReading in files...')
    gaf_dicts = {}
    problem_files = []
    for f in tqdm(gaf_files):
        try:
            gaf = GafReader(f)
        except:
            print(f'Exception raised in GAF parsing, skipping file')
            problem_files.append(f)
        else:
            gaf_dicts[f] = gaf

    # Get keywords
    print('\nGetting keywords...')
    names = defaultdict(set)
    for f, gaf in tqdm(gaf_dicts.items()):
        for namedTup in gaf.associations:
            name = namedTup.DB_Name
            syns = namedTup.DB_Synonym
            names[f].update(name)
            names[f].update(syns)
    for key, value in names.items():
        names[key] = list(value)

    # Write out files
    print('\nWriting output files...')
    with open(f'{output_dir}/{file_prefix}_keywords.json', 'w') as f:
        json.dump(names, f, indent=4)
    with open(f'{output_dir}/{file_prefix}_problem_files.txt', 'w') as f:
        f.write('\n'.join(problem_files))


    print('\nDone!')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get Planteome keywords')

    parser.add_argument('planteome_dir', type=str,
            help='Path to directory with .assoc files')
    parser.add_argument('output_dir', type=str,
            help='Path to save output')
    parser.add_argument('-file_prefix', type=str, default='Planteome',
            help='String to prepend to output filename, default is Planteome')

    args = parser.parse_args()

    args.planteome_dir = abspath(args.planteome_dir)
    args.output_dir = abspath(args.output_dir)

    main(args.planteome_dir, args.output_dir, args.file_prefix)
