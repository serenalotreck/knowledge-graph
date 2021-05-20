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
    Compares two lists of base file names (strings) obtained from data 
    directories for overlap. Returns a list of the overlapping abstract names.

    parameters:
        dir1_names, list of str: list of basenames from dir1
        dir2_names, list of str: list of basenames from dir2

    returns:
        a list of str that are names of overlapping abstracts, if there are 
            overlaps, otherwise, returns the string 'No data overlap!'
    """
    # Do a simple boolean check, if True, get specific names
    
    dir1_set = set(dir1_names)
    dir2_set = set(dir2_names)
    
    if bool(dir1_set & dir2_set):
        return list(dir1_set & dir2_set)
    else:
        return 'No data overlap!'


def get_names(tr, te, ap):
    """
    Gets the file names in the directories for each dataset.

    parameters:
        tr, te, ap: str, paths to directories with data to compare 

    returns:
        fnames, dict of list of str: keys are dataset names, values 
            are lists of the base file names in each dataset
    """
    dsets = {'train':tr, 'test':te, 'apply':ap}
    fnames = {}
    for name, dataset in dsets.items():
        files = [f for f in os.listdir(dataset) 
                if os.path.isfile(os.path.join(dataset, f))]
        basenames = [os.path.splitext(f)[0] for f in files]
        fnames[name] = basenames

    return fnames


def main(tr, te, ap, out_loc):

    # Get a list of names in the directories
    fnames = get_names(tr, te, ap)

    # Check for overlap 
    dsets = {'train':tr, 'test':te, 'apply':ap}
    comparisons = [] 
    for i,x in enumerate(dsets.keys()): 
        for j,y in enumerate(dsets.keys()):
            if (y, x) not in comparisons and i != j:
                comparisons.append((x,y))
    
    overlaps = {}
    for dir1, dir2 in comparisons:
        print('---------------------------------------')
        print(f'\nComparing {dir1} and {dir2}:\n')
        overlap = compare_two_dirs(fnames[dir1], fnames[dir2])
        if overlap != 'No data overlap!':
            print(f'Overlap found between {dir1} and {dir2}. See output '
                    'file for details.\n')
        else: 
            print('No overlap found!\n')
        overlaps[f'{dir1}-{dir2}'] = overlap

    # Write out file 
    print('\nWriting output file...')
    with open(f'{out_loc}/check_overlap_file.txt', 'w') as f:
        for key, value in overlaps.items():
            f.write(f'Overlapping abstracts between {key}:\n')
            f.write(f'{value}\n\n')

    print('\nDone!')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Check for document overlap in datasets.')

    parser.add_argument('-tr','--train_dir', type=str, 
            help='Path to directory containing training data.')
    parser.add_argument('-te', '--test_dir', type=str,
            help='Path to directory containing test data.')
    parser.add_argument('-ap', '--apply_dir', type=str, 
            help='Path to directory containing training data')
    parser.add_argument('-out_loc', type=str, 
            help='Path to save output file')

    args = parser.parse_args()

    args.train_dir = os.path.abspath(args.train_dir)
    args.test_dir = os.path.abspath(args.test_dir)
    args.apply_dir = os.path.abspath(args.apply_dir)
    args.out_loc = os.path.abspath(args.out_loc)

    main(args.train_dir, args.test_dir, args.apply_dir, args.out_loc)
