"""
Given a set of annotations that have already been changed to have only one
entity type by convert_types.py, put all annotations in one .ann file for each
.txt document.

Copies the .txt files to a new directory, and makes a .ann file for each, with
all of the annotators' annotations in them. The types will be left as ENTITY;
the purpose of this script is simply to put all of the annotations in one
place such that the person unifying them can just delete or modify existing
annotations with all of them in sight.

Makes a new directory within out_loc of f'{iaa_dir_name}_unified' for the
new unity annotation.

IMPORTANT: Assumes there are only entities (ID starting with T) in the files.

Author: Serena G. Lotreck
"""
import argparse
from os import scandir, listdir, mkdir
from os.path import abspath, splitext
import shutil
import pdb


def main(project_root, iaa_dir_name, out_loc):

    # Get paths to relevant folders
    annotator_paths = [f.path for f in scandir(project_root)
                        if f.is_dir() and iaa_dir_name in listdir(f)]

    # Make new output directory
    out_path = f'{out_loc}/{iaa_dir_name}_unified'
    mkdir(out_path)

    # Copy .txt files that overlap in all annotator_paths
    overlap = set()
    for annotator_path in annotator_paths:
        files = [f for f in listdir(f'{annotator_path}/{iaa_dir_name}')
                if f.endswith('.txt')]
        overlap.update(files)
    for f in overlap:
        fullpath = f'{annotator_paths[0]}/{iaa_dir_name}/{f}'
        shutil.copy(fullpath, out_path)

    # Make a .ann file for each .txt doc with all of the annotations
    #pdb.set_trace()
    for f in overlap:
        ann_str = ''
        ent_num = 0
        for i, annotator_path in enumerate(annotator_paths):
            f_root = splitext(f)[0]
            with open(f'{annotator_path}/{iaa_dir_name}/{f_root}.ann') as myf:
                current_ann_lines = myf.readlines()
            for line in current_ann_lines:
                # Replace the entity number in the ID
                ent_num += 1
                line_elts = line.split('\t')
                line_elts[0] = f'T{ent_num}'
                line = '\t'.join(line_elts)
                # Make sure the previous one ended with a newline
                if i > 0:
                    try:
                        assert ann_str[-1] == '\n'
                    except AssertionError:
                        ann_str += '\n'
                ann_str += line
        with open(f'{out_path}/{f_root}.ann', 'w') as myf:
            myf.write(ann_str)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Unify annotations')

    parser.add_argument('project_root', type=str,
            help='Path to top-level directory containing all annotators')
    parser.add_argument('iaa_dir_name', type=str,
            help='Name of the directory that all annotators have in common')
    parser.add_argument('out_loc', type=str,
            help='Path to save the new annotations')

    args = parser.parse_args()

    args.project_root = abspath(args.project_root)
    args.out_loc = abspath(args.out_loc)

    main(args.project_root, args.iaa_dir_name, args.out_loc)
