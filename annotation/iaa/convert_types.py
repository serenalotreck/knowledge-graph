"""
Convert types in a brat .ann file to just ENTITY.

Makes a new directory with a copy of all files, rather than changing in place.

Author: Serena G. Lotreck 
"""
import argparse
from os.path import abspath

from shutil import copytree
from os import listdir, scandir
from os.path import basename, isdir, isfile, splitext, join
import pandas as pd 


def main(project_root, iaa_dir_name, out_loc):

    # Make a copy of the directory in out_loc
    root_base = basename(project_root)
    new_root_name = f'{out_loc}/{root_base}_one_entity_type'
    copytree(project_root, new_root_name)
    print(f'\nCopied directory is {new_root_name}')

    # Replace entity types 
    print('\nReplacing entity types...')
    # Look for annotation directories
    annotator_paths = [f.path for f in scandir(new_root_name) \
                     if f.is_dir() and iaa_dir_name in listdir(f)]
    for path in annotator_paths:
        for filename in listdir(f'{path}/{iaa_dir_name}'):
            # Look for .ann files 
            if splitext(filename)[1] == '.ann':
                # Read in the lines of the .ann file
                with open(join(path, iaa_dir_name, filename)) as f:
                    lines = f.readlines()
                # Update the lines 
                updated_lines = []
                for line in lines:
                    if line[0] == 'T':
                        parts = line.split('\t')
                        middle = parts[1].split(' ')
                        middle[0] = 'ENTITY'
                        middle = ' '.join(middle)
                        parts[1] = middle
                        updated_line = '\t'.join(parts)
                        updated_lines.append(updated_line)
                    else: updated_lines.append(line)
                # Write lines back to file 
                with open(join(path, iaa_dir_name, filename), 'w') as f:
                    f.writelines(updated_lines)

    print('\nDone!')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Change all ent types to ENTITY')

    parser.add_argument('project_root', type=str,
            help='Path to top-level directory containing all annotators')
    parser.add_argument('iaa_dir_name', type=str,
            help='Name of the directory that all annotators have in common.')
    parser.add_argument('out_loc', type=str,
            help='Path to save the copy of the project_root and child directories.')

    args = parser.parse_args()

    args.project_root = abspath(args.project_root)
    args.out_loc = abspath(args.out_loc)

    main(args.project_root, args.iaa_dir_name, args.out_loc)

