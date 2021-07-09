"""
Given two directories, return True if there is any overlap in file names between
the two directories, False if there is not. Disregards subdirectories.
"""
import argparse 
import os 


def main(dir1, dir2):

    dir1_files = [f for f in os.listdir(dir1) if os.path.isfile(os.path.join(dir1, f))]
    dir2_files = [f for f in os.listdir(dir2) if os.path.isfile(os.path.join(dir2, f))]

    if len(set(dir1_files).intersection(dir2_files)) != 0:

        print('True')

    else: print('False')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get diff between two dirs')

    parser.add_argument('dir1', type=str)
    parser.add_argument('dir2', type=str)

    args = parser.parse_args()

    args.dir1 = os.path.abspath(args.dir1)
    args.dir2 = os.path.abspath(args.dir2)

    main(args.dir1, args.dir2)

