"""
Script to confirm no overlap between training, test and apply datasets
for doc2vec.py

Walks through document names in the three directories and checks for overlap.

Author: Serena G. Lotreck
"""
import os
import argparse


def compare_two_dirs(dir1_names, dir2_names):
    """
    Compares two lists of base file names (strings) obtained from data directories
    for overlap. Prints a report of the name of the datasets that have overlap and 
    the specific overlapping abstract names.

    parameters:
        dir1_names, list of str: list of basenames from dir1
        dir2_names, list of str: list of basenames from dir2

    returns: None
    """
    # Do a simple boolean check, if True, get specific names
    
    dir1_set = set(dir1_names)
    dir2_set = set(dir2_names)
    
    if bool(dir1_set & dir2_set):
        print('Overlap found. Overlapping documents are:')
        print(f'{dir1_set & dir2_set}')
        print('Please revise your data before proceeding to document clustering.\n')

    else:
        print('No data overlap! Safe to proceed to next step.\n')


def main(tr, te, ap):

    # Get a list of names in the directories
    dsets = {'train':tr, 'test':te, 'apply':ap}
    fnames = {}
    for name, dataset in dsets.items():
        files = [f for f in os.listdir(dataset) if os.path.isfile(os.path.join(dataset, f))]
        basenames = [os.path.splitext(f)[0] for f in files]
        fnames[name] = basenames

    # Check for overlap and report if there are files with the same base name in the directories
    for dir1, dir2 in [(x, y) for i,x in enumerate(dsets.keys()) 
                        for j,y in enumerate(dsets.keys()) if i != j]:
        print('---------------------------------------')
        print(f'\nComparing {dir1} and {dir2}:\n')
        compare_two_dirs(fnames[dir1], fnames[dir2])

    print('\nDone!')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Check for document overlap in datasets.')

    parser.add_argument('-tr','--train_dir', type=str, 
            help='Path to directory containing training data.')
    parser.add_argument('-te', '--test_dir', type=str,
            help='Path to directory containing test data.')
    parser.add_argument('-ap', '--apply_dir', type=str, 
            help='Path to directory containing training data')

    args = parser.parse_args()

    args.train_dir = os.path.abspath(args.train_dir)
    args.test_dir = os.path.abspath(args.test_dir)
    args.apply_dir = os.path.abspath(args.apply_dir)

    main(args.train_dir, args.test_dir, args.apply_dir)
