"""
Strips all non-terminal punctuation from a set of .txt files. 

Specifically, this pscript removes all punctuation included in python's 
string.punctuation except for .!?

files will be saved with the same name and file ext as the original, with 
"_noPunct" appended to the end of the basename.

Author: Serena G. Lotreck
""" 
import argparse
from os import listdir
from os.path import abspath, basename, isfile, join, splitext

import string


def main(source_dir, out_dir):
    
    # Read in the files 
    print('\nReading in files...')
    
    onlytxtfiles = [f for f in listdir(source_dir) if isfile(join(source_dir, f)) 
                    and splitext(f)[1] == '.txt']
    
    print(f'{len(onlytxtfiles)} files found to process.')
    
    myfiles = {}
    for f in onlytxtfiles:
        
        fname = splitext(f)[0]
        
        with open(f'{source_dir}/{f}') as myf:
            fcontents = myf.read()
            myfiles[fname] = fcontents
    
    print(f'Successfully read in {len(myfiles.keys())} files!\n')

    # Strip punctuation 
    print('\nStripping non-terminal punctuation...')

    to_strip = string.punctuation[1:13] + string.punctuation[14:20] + string.punctuation[21:]
    
    print(f'The characters to be stripped are: {to_strip}')
    
    stripped_files = {}
    for name, text in myfiles.items():
        stripped_name = name + '_noPunct'
        stripped_text = text.translate(str.maketrans('','',to_strip))
        stripped_files[stripped_name] = stripped_text

    print(f'{len(stripped_files.keys())} files have been sucessfully cleaned!')

    # Write out the files
    print('\nWriting files...')
    print(f'Writing to {out_dir}')

    for stripped_name, stripped_text in stripped_files.items():
        with open(f'{out_dir}/{stripped_name}.txt', 'w') as myf:
            myf.write(stripped_text)

    print('\nDone!')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Strip non-terminal punctuation '
                                                'from .txt files')

    parser.add_argument('source_dir', type=str, 
            help='Path to directory containing txt files to process.')
    parser.add_argument('out_dir', type=str,
            help='Path to save files.')

    args = parser.parse_args()

    args.source_dir = abspath(args.source_dir)
    args.out_dir = abspath(args.out_dir)

    main(**vars(args))
