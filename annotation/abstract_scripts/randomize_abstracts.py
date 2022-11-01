"""
Script to randomize abstracts in a directory, outputs results as txtf file with
a list of abstract PMIDs.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, isfile, splitext
from os import listdir
from random import shuffle


def main(abs_dir, out_loc, out_prefix):

    # Read in all files in directory
    dir_list = listdir(abs_dir)
    files = [f for f in dir_list if splitext(f)[1] == '.txt']

    # Randomize
    shuffle(files)

    # Write out
    with open(f'{out_loc}/{out_prefix}_randomized_abstracts.txt', 'w') as myf:
        myf.write('\n'.join(files))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Randomize abstracts')

    parser.add_argument('abs_dir', type=str,
            help='Path to directory to randomize')
    parser.add_argument('out_loc', type=str,
            help='Path to save results')
    parser.add_argument('out_prefix', type=str,
            help='String to prepend to output file name')

    args = parser.parse_args()

    args.abs_dir = abspath(args.abs_dir)
    args.out_loc = abspath(args.out_loc)

    main(args.abs_dir, args.out_loc, args.out_prefix)
