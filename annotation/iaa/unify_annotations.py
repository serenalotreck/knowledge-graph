"""
Given a set of annotations that have already been changed to have only one
entity type by convert_types.py, put all annotations in one .ann file for each
.txt document.

Copies the .txt files to a new directory, and makes a .ann file for each, with
all of the annotators' annotations in them. The types will be left as they are;
the purpose of this script is simply to put all of the annotations in one
place such that the person unifying them can just delete or modify existing
annotations with all of them in sight.

Annotations that are exactly the same (same start, end, type and text for
entities, type and args for relations) will be reduced to one annotation.

Makes a new directory within out_loc of f'{iaa_dir_name}_unified' for the
new unity annotation.

NOTE: Given that the workflow of this project involves unifying entity
annotations before returning them to annotators to be marked up with
relations, this script is designed to only unify one type of annotation
at a time, while ignoring anything that is not that kind of annotation.

TODO: Write the relation unification code

Author: Serena G. Lotreck
"""
import argparse
from os import scandir, listdir, mkdir
from os.path import abspath, splitext
import shutil
import pdb


def unify_ents(overlap, annotator_paths, iaa_dir_name, out_path):
    """
    Function to unify entity annotations. Ignores any annotation whose
    ID doesn't begin with a T.

    NOTE: Any non-entity annotations will not appear in the final .ann files.

    parameters:
        overlap, set of str: a set of the files to unify
        annotator_paths, list of str: paths for each annotator
        iaa_dir_name, str: name of the dire annotators have in common
        out_path, str: where to save the unified files
    """
    # Make a .ann file for each .txt doc with all of the annotations
    for f in overlap:
        ann_str = ''
        ent_num = 0
        for i, annotator_path in enumerate(annotator_paths):
            f_root = splitext(f)[0]
            with open(f'{annotator_path}/{iaa_dir_name}/{f_root}.ann') as myf:
                current_ann_lines = myf.readlines()
            for line in current_ann_lines:
                line_elts = line.split('\t')
                if line_elts[0][0] == 'T':
                    # Replace the entity number in the ID
                    ent_num += 1
                    line_elts[0] = f'T{ent_num}'
                    line = '\t'.join(line_elts)
                    # Check if this entity already exists in the same form
                    form = '\t'.join(line_elts[1:]) # Ignore the ID
                    if form in ann_str:
                        continue
                    else:
                    # Make sure the previous one ended with a newline
                        if ent_num > 1:
                            try:
                                assert ann_str[-1] == '\n'
                            except AssertionError:
                                ann_str += '\n'
                        ann_str += line
        with open(f'{out_path}/{f_root}.ann', 'w') as myf:
            myf.write(ann_str)


def unify_rels(overlap, annotator_paths, iaa_dir_name, out_path):
    """
    Function to unify relation annotations. Importantly, assumes that the Arg
    numbers (the ID's of the entities) are the same across all documents. If
    they aren't, semantically identical relations where the entities just have
    different ID's will all appear in the final document. Copies entity
    annotations over from the first annotator, so if entities are not the same
    across all annotators, may result in relations pointing to non-existent
    entities in the final documents.

    parameters:
        overlap, set of str: a set of the files to unify
        annotator_paths, list of str: paths for each annotator
        iaa_dir_name, str: name of the dire annotators have in common
        out_path, str: where to save the unified files
    """
    # Make a .ann file for each .txt doc with all of the annotations
    for f in overlap:
        ann_str = ''
        rel_num = 0
        for i, annotator_path in enumerate(annotator_paths):
            f_root = splitext(f)[0]
            with open(f'{annotator_path}/{iaa_dir_name}/{f_root}.ann') as myf:
                current_ann_lines = myf.readlines()
            ent_str = ''
            for line in current_ann_lines:
                line_elts = line.split('\t')
                if line_elts[0][0] == 'T':
                    if i == 0:
                        ent_str += line
                elif line_elts[0][0] == 'R':
                    # Replace the entity number in the ID
                    rel_num += 1
                    line_elts[0] = f'R{rel_num}'
                    line = '\t'.join(line_elts)
                    # Check if this relation already exists in the same form
                    form = '\t'.join(line_elts[1:]) # Ignore the ID
                    if form in ann_str:
                        continue
                    else:
                    # Make sure the previous one ended with a newline
                        if rel_num > 1:
                            try:
                                assert ann_str[-1] == '\n'
                            except AssertionError:
                                ann_str += '\n'
                        ann_str += line
            ann_str += ent_str

        with open(f'{out_path}/{f_root}.ann', 'w') as myf:
            myf.write(ann_str)


def main(project_root, iaa_dir_name, unify_type, out_loc):

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

    if unify_type == "ent":
        unify_ents(overlap, annotator_paths, iaa_dir_name, out_path)
    else:
        unify_rels(overlap, annotator_paths, iaa_dir_name, out_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Unify annotations')

    parser.add_argument('project_root', type=str,
            help='Path to top-level directory containing all annotators')
    parser.add_argument('iaa_dir_name', type=str,
            help='Name of the directory that all annotators have in common')
    parser.add_argument('unify_type', type=str,
            help='One of "ent" or "rel" to indicate which anns should be '
            'unified')
    parser.add_argument('out_loc', type=str,
            help='Path to save the new annotations')

    args = parser.parse_args()

    args.project_root = abspath(args.project_root)
    args.out_loc = abspath(args.out_loc)

    main(args.project_root, args.iaa_dir_name, args.unify_type, args.out_loc)
