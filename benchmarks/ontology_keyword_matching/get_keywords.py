"""
Script to obtain keywords from a directory of .assoc files, in this case
downloaded from Planteome.

Author: Serena G. Lotreck
"""
import pdb
import argparse
from os.path import abspath, join
from os import listdir
from goatools.anno.gaf_reader import GafReader


def main(planteome_dir, output_dir, file_prefix):

    # Get names of GAF files
    print('\nGetting names of .assoc files...')
    gaf_files = []
    for f in listdir(planteome_dir):
        if f.endswith('.assoc'):
            gaf_files.append(join(planteome_dir, f))

    # Read in GAF files
    print('\nReading in files...')
    gaf_dicts = []
    problem_files = []
    for i, f in enumerate(gaf_files):
        print(f'Reading in file {i} of {len(gaf_files)-1}')
        #pdb.set_trace()
        try:
            gaf = GafReader(f)
        except:
            print(f'Exception raised in GAF parsing, skipping file')
            problem_files.append(f)
        else:
            gaf_dicts.append(gaf)

    # Get keywords
    print('\nGetting keywords...')
    names = set()
    for i, gaf in enumerate(gaf_dicts):
        print(f'Getting keywords from file {i} of {len(gaf_dicts)-1}')
        for namedTup in gaf.associations:
            name = namedTup.DB_Name
            syns = namedTup.DB_Synonym
            names.update(name)
            names.update(syns)

    # Write out as a single column .txt file
    print('\nWriting output files...')
    with open(f'{output_dir}/{file_prefix}_keywords.txt', 'w') as f:
        f.write('\n'.join(names))
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
