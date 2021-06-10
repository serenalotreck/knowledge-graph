"""
Quick and dirty script to remove newline characters that come between the 
label and weight attributes in the dot files produced by pygraphviz.

Example: 

    nodeA -- nodeB [label="label", 
            weight=num];

causes Cytoscape to not be able to read in the file. Need to change this to

    nodeA -- nodeB [label="label", weight=num];

The newline characters don't pose an issue for using actual GraphViz, but
it prevents the import to Cytoscape. Unclear why this is the case, but rather 
than delving into dot-app/Cytoscape troubleshooting, writing this quick and 
dirty way of dealing with the issue for now.

Removes all newlines that don't directly follow a semicolon.
Makes new file with the name "noNewline_{original file name}"

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, isdir, isfile, join, basename, splitext
from os import listdir

import re 


def remove_nuisance_newlines(file_text):
    """
    Remove newlines & following spaces that come between the edge label and 
    edge weight.

    parameters:
        file_text, dict: keys are filenames and values are strings of file 
            contents

    returns:
        file_text_cleaned, dict: keys are filenames, values are strings of 
            cleaned file contents
    """
    file_text_cleaned = {}
    
    regex = '(?<!;)\n[ \t]+'
    regex2 = '(?<=\{)\s'
    for fname, text in file_text.items():
        new_fname = f'{splitext(fname)[0]}_noNewlines{splitext(fname)[1]}'
        clean_text = re.sub(regex, ' ', text)
        clean_text_split = re.split(regex2, clean_text) # Fix the first line (janky, I know)
        clean_text = '\n\t'.join(clean_text_split)
        file_text_cleaned[new_fname] = clean_text

    return file_text_cleaned


def main(files):

    # Check if directory or list of files & get list of files w/ full path
    if len(files) == 1:
        if isdir(files[0]):
            file_dir = abspath(files[0])
            files = [join(file_dir, f) for f in listdir(file_dir) if isfile(join(file_dir, f))]
        else:
            file_dir = abspath(files[0])
            files = [join(file_dir, f) for f in files if isfile(abspath(f))]

    else:
        file_dir = abspath(files[0])
        files = [join(file_dir, f) for f in files if isfile(abspath(f))]
    
    # Read in files
    print('\nReading in files...')
    file_text = {}
    for f in files:
        with open(f) as myfile:
            file_text[f] = myfile.read()

    # Process files
    print('\nRemoving problematic newlines...')
    file_text_cleaned = remove_nuisance_newlines(file_text)

    # Write out files 
    print('\nWriting out files...')
    for fname, clean_text in file_text_cleaned.items():
        with open(fname, 'w') as myfile:
            myfile.write(clean_text)

    print('\nDone!')

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Remove buggy newlines')

    parser.add_argument('files', nargs='+', 
            help='A path to a directory or a list of files to process', 
            default=[])
    
    args = parser.parse_args()

    main(args.files)


