"""
Code to calculate an IAA for relation annotations. 

Calculates F1 with 2 kinds of tolerances. 
    (1) STRICT. a relation is the same only if the type and direction of the 
        relation are the same. Entities  must have overlapping span boundaries, 
        but entity types can be different.
    (2) LOOSE. a relation is the same only if the relation connects
        two entities that are considered equivalent. Relation type can be different,
        and entities are considered the same if they overlap.

Assumes the following directory structure:

    top_level_dir 
        └── annotator-1
            └── iaa_dir 
                ├── doc-1.ann
                └── doc-1.txt
        └── annotator-2
            └── iaa_dir 
                ├── doc-1.ann
                └── doc-1.txt

The file reading procedure here is not nearly as nice or generous as the one 
for bratiaa; the iaa_dirs must all have the same name, and you have to 
provide that name, and annotator directories have to be in the first level 
of the overall directory, and the iaa_dir must be in the first level of the 
annotator directories. The iaa_dir must also contain the same files for all
annotators; this script doesn't handle non-overlapping files or missing files.

Author: Serena G. Lotreck
"""
import argparse
import os

import re
import itertools
import pandas as pd 


def get_iaa_stats(annotator_pairs_iaas):
    """
    Calculate mean and SD for the IAA's for each pair, and also 
    over all annotators.
    
    parameters:
        annotator_pairs_iaas, dict of dict: key is annotator pair, value
            is a dict where key is document name and value is the iaa score for that document
    
    Prints a report with the per-doc and overall iaa 
    """
    # Make nested dict into a multiindex dataframe for more efficient handling
    reformed = {(outerKey, innerKey): values for outerKey, innerDict 
            in annotator_pairs_iaas.items() for innerKey, values 
            in innerDict.items()}
    iaas_df = pd.DataFrame(reformed).T.rename({0:'iaa'}, axis=1)

    # Get the per-document iaa 
    per_doc = iaas_df.groupby(level=1).agg({'iaa':['mean', 'std']})

    # Get the overall iaa 
    overall = iaas_df.agg({'iaa':['mean','std']})
    
    # Print report 
    print('Relation IAA report')
    print('-----------------------------------------')
    print('Per-Document IAA:')
    print(per_doc)
    print('-----------------------------------------')
    print('Overall IAA:')
    print(overall)


def calculate_f1(a,b,c):
    """
    Calculate balanced F1 score for a pair of docs.

    parameters: 
        a, int: number of annotations both annotators agree on
        b, int: number of annotations annotator 2 has that annotator 1 does not
        c, int: number of annotations annotator 1 has that annotator 2 does not 

    returns:
        f1, float: balanced F1 score. If there are no relations annotated in
            either document, returns an F-score of 1 for complete agreement.
    """
    if a + b + c != 0:
        return (2*a)/(2*a + b + c)
    else: return 1


def compare_offsets(offsets_1, offsets_2):
    """
    Helper for compare_relations. Determines if there is 
    a set of overlapping offsets for two entities.

    parameters:
        offsets_1, list of tuple: offsets from first arg
        offsets_2, list of tuple: offsets from second arg

    returns: 
        True if the args overlap, False otherwise
    """
    overlap = False
    for offset_1 in offsets_1:
        for offset_2 in offsets_2:
            if ((offset_1[0] <= offset_2[0] <= offset_1[1]) or 
                    (offset_2[0] <= offset_1[0] <= offset_2[1])):
                overlap = True

    return overlap 


def compare_relations(rel_1, rel_2, symm=False, tolerance='STRICT'):
    """
    Helper function for the two agreement_table functions.

    parameters:
        rel_1, df row: first relation to compare
        rel_2, df row: second relation to compare
        symm, bool: whether or not relation order matters, default False
        tolerance, str: 'STRICT' or 'LOOSE', default 'STRICT'
    
    returns:
        True if the relations are equivalent under the given 
            tolerance, False otherwise 
    """
    offset_match = False 
    # Compare offsets
    arg1_ann1_offsets = rel_1.Arg1[0]
    arg2_ann1_offsets = rel_1.Arg2[0]
    arg1_ann2_offsets = rel_2.Arg1[0]
    arg2_ann2_offsets = rel_2.Arg2[0]
    

    if not symm:
        arg1_compare = compare_offsets(arg1_ann1_offsets, arg1_ann2_offsets)
        arg2_compare = compare_offsets(arg2_ann1_offsets, arg2_ann2_offsets)

        if arg1_compare and arg2_compare:
            offset_match = True

    else: 
        arg1_compare1 = compare_offsets(arg1_ann1_offsets, arg1_ann2_offsets)
        arg1_compare2 = compare_offsets(arg1_ann1_offsets, arg2_ann2_offsets)
        arg2_compare2 = compare_offsets(arg2_ann1_offsets, arg2_ann2_offsets)
        arg2_compare1 = compare_offsets(arg2_ann1_offsets, arg1_ann2_offsets)

        if (arg1_compare1 or arg1_compare2) and (arg2_compare2 or arg2_compare1):
            offset_match=True
    # If matching offsets and tolerance is STRICT, compare types 
    if offset_match and tolerance == 'STRICT':
        if rel_1.Type == rel_2.Type:
            return True
    elif offset_match and tolerance == 'LOOSE':
        return True
    else: 
        return False


def get_loose_agreement_table(ann_df1, ann_df2):
    """
    Get the values in the agreement table for two documents according to
    the loose tolerance. 
    
    parameters:
        ann_df1, df: df of .ann file for rater 1
        ann_df2, df: df of .ann file for rater 2
    
    returns:
        a, b, c: ints, the values from the agreement table 
    """
    a = 0
    # Get combinations of indices to compare 
    with_id = list(itertools.combinations(([f'{i}_df1' for i in ann_df1.index.tolist()] +
                [f'{i}_df2' for i in ann_df2.index.tolist()]), 2))
    
    # Only want to compare relations across dataframes, so eliminate ones 
    # with the same tag 
    to_compare = []
    for i in with_id:
        if i[0][-4:] != i[1][-4:]:
            to_compare.append((int(i[0][:-4]), int(i[1][:-4])))

    # Assumes that the first element in the tuple is always from df1, this 
    # appears to be the case upon observation 
    for rel_pair_idx in to_compare:

        rel_1 = ann_df1.loc[rel_pair_idx[0], :] 
        rel_2 = ann_df2.loc[rel_pair_idx[1], :]
        
        comparison = compare_relations(rel_1, rel_2, symm=True, tolerance='LOOSE')
        if comparison: a += 1

    # Get the remaining (different) relations in the two annotator dfs,
    # These are b and c 
    b = ann_df1.shape[0] - a
    c = ann_df2.shape[0] - a

    return a, b, c


def get_strict_agreement_table(ann_df1, ann_df2, symm_rels):
    """
    Get the values in the agreement table for two documents according to
    the strict tolerance. 
    
    parameters:
        ann_df1, df: df of .ann file for rater 1
        ann_df2, df: df of .ann file for rater 2
        symm_rels, list of str: relations for which order doesn't matter
    returns:
        a, b, c: ints, the values from the agreement table 
    """
    # Compare all relations with same type 
    rel_types = set(ann_df1.Type.values.tolist() + ann_df2.Type.values.tolist())
    a = 0
    for rel_type in rel_types:

        # Determine if order matters for this relation type 
        if rel_type in symm_rels: 
            symm = True
        else: symm = False
        
        # Subset dataframes by type 
        type_df1 = ann_df1.loc[ann_df1['Type'] == rel_type]
        type_df2 = ann_df2.loc[ann_df2['Type'] == rel_type]

        # Get combinations of indices to compare 
        with_id = list(itertools.combinations(([f'{i}_df1' for i in type_df1.index.tolist()] + 
            [f'{i}_df2' for i in type_df2.index.tolist()]), 2))
        
        # Only want to compare relations across dataframes, so eliminate ones 
        # with the same tag 
        to_compare = []
        for i in with_id:
            if i[0][-4:] != i[1][-4:]:
                to_compare.append((int(i[0][:-4]), int(i[1][:-4])))

        # Assumes that the first element in the tuple is always from df1, this 
        # appears to be the case upon observation 
        for rel_pair_idx in to_compare:
            rel_1 = type_df1.loc[rel_pair_idx[0], :] 
            rel_2 = type_df2.loc[rel_pair_idx[1], :]
            
            comparison = compare_relations(rel_1, rel_2, symm=symm, tolerance='STRICT')
            if comparison: a += 1
    
    # Get the remaining (different) relations in the two annotator dfs,
    # These are b and c 
    b = ann_df1.shape[0] - a
    c = ann_df2.shape[0] - a

    return a, b, c


def calculate_iaa(ann_df1, ann_df2, symm_rels, tolerance='STRICT'):
    """
    Calculate IAA for a pair of documents. The default tolerance for the 
    calculation is STRICT, where entities must have the same span boundaries 
    and the same types, and relations must have the same type and point the 
    same direction.

    parameters:
        ann_df1, df: df of .ann file for rater 1
        ann_df2, df: df of .ann file for rater 2
        symm_rels, list of str: list of relation types for which order doesn't matter.
        tolerance, str: tolerance with which to calculate IAA. Options are 
            STRICT, SEMI-STRICT, RELATION-LOOSE, ENTITY-LOOSE
    """
    print('\nCalculating IAA for document pair...') 
    # Get agreement values
    if tolerance == 'STRICT':
        a, b, c = get_strict_agreement_table(ann_df1, ann_df2, symm_rels)
    elif tolerance == 'LOOSE':
        a, b, c = get_loose_agreement_table(ann_df1, ann_df2)

    # Calculate F1
    return calculate_f1(a, b, c)


def get_offsets(ent_str, offsets):
    """
    Helper for format_relation. 

    Recursive function that gets all character offsets for a given entity, 
    accounting for the fact that there may be multiple character offsets for 
    a given entity, separated by semicolons. 
    
    parameters:
        ent_str, str: string with character offsets, where first character is 
            the start of the first offset (e.g. no tab or space beginning)
        offsets, list: list of two-tuples, where each tuple is 
            (start_offset, end_offset). On the first call this will be empty.

    returns: 
        offsets, list of two-tuples: list of (start_offset, end_offset)
    """
    # Base case 
    if ';' not in ent_str:
        start_offset = ent_str[:ent_str.index(' ')]
        end_offset = ent_str[ent_str.index(' ')+1:ent_str.index('\t')]
        offsets.append((start_offset, end_offset))
        return offsets
    # Recursive case 
    else:
        start_offset = ent_str[:ent_str.index(' ')]
        end_offset = ent_str[ent_str.index(' ')+1:ent_str.index(';')]
        offsets.append((start_offset, end_offset))
        return get_offsets(ent_str[ent_str.index(';')+1:], offsets)


def format_relation(entry, line_dict):
    """
    Helper for make_ann_df. 

    parameters:
        entry, str: the relation line from the .ann file, starting with the 
            first tab character
        line_dict, dict: keys are ID's from the .ann file, values are the 
            lines starting with the first tab character

    returns:
        relation, list: relation with components as list elements 

    I'm sorry world for writing such an ugly function >.<
    """
    relation = []
    
    # Get index of first space, this is the end of the type 
    type_end_idx = entry.index(' ')
    
    # Put type in relation list 
    relation.append(entry[:type_end_idx].strip())
    
    # Look for first argument in dict 
    arg1_start_idx = type_end_idx + 6
    arg1_end_idx = entry.index(' ', type_end_idx+1)
    arg1_id = entry[arg1_start_idx:arg1_end_idx]
    arg1_entry = line_dict[arg1_id] 

    # Look for second argument in dict
    arg2_start_idx = arg1_end_idx + 6
    arg2_id = entry[arg2_start_idx:].strip()
    arg2_entry = line_dict[arg2_id]
    
    # Format args 
    for arg_entry in (arg1_entry, arg2_entry): 
        
        # Get type 
        first_space = arg_entry.index(' ')
        ent_type = arg_entry[:first_space].strip()
        
        # Drop all characters from string before the first offset 
        offsets_str = arg_entry[first_space+1:]

        # Get entity offsets
        offsets = [] 
        offsets = get_offsets(offsets_str, offsets)

        # Make tuple and add to relation entry
        relation.append((offsets, ent_type))

    return relation 


def make_ann_df(ann):
    """
    Converts a brat standoff formatted .ann  file into a dataframe of the form:

    |  Type  |  Arg1  |  Arg2  |

    where Arg1 and Arg2 are entities of the form 
        ([(start_offset, end_offset), ...], TYPE)
    The list of tuples is to account for the fact that some entities
    may have multiple start and end offsets if the annotator labeled
    the same exact span multiple times in the same document.
    
    parameters:
        ann, str: path to .ann file to convert 

    returns: 
        ann_df, df: dataframe version of the .ann file 
    """
    print('\nMaking annotator dataframe...')

    # Read in file 
    with open(ann) as myf:
        file_lines = myf.readlines()
    
    # Make a dict where the ID (T1, R2, etc) are keys and the rest of the line
    # minus the leading \t are values 
    line_dict = {}
    for line in file_lines:
        # Get the index of the tab character
        ID_end_idx = line.index('\t')
        line_dict[line[:ID_end_idx]] = line[ID_end_idx:]
    
    # Format relations for df 
    df_lines = []
    for ID, entry in line_dict.items():
        if ID[0] == 'R':
            
            # Format relation 
            relation = format_relation(entry, line_dict)
            
            # Add relation to overall list 
            df_lines.append(relation)
        
    # Make dataframe 
    ann_df = pd.DataFrame(df_lines, columns=['Type', 'Arg1', 'Arg2'])
    
    print(f'Snapshot of annotator df: \n{ann_df.head()}')
    return ann_df


def get_overlapping_docs(annotator1, annotator2, iaa_dir_name):
    """
    Get the file names for the files that the two annotators have done in common,
    that are found in the iaa_dir_name directory.
    """
    from os.path import isfile, join
    
    # Get full paths to docs 
    ann1_path = join(annotator1, iaa_dir_name)
    ann2_path = join(annotator2, iaa_dir_name)

    ann1_files = [f for f in os.listdir(ann1_path) if isfile(join(ann1_path, f))]
    ann2_files = [f for f in os.listdir(ann2_path) if isfile(join(ann2_path, f))]

    files_in_common = [f for f in ann1_files if f in ann2_files if f[-4:] == '.ann']

    return files_in_common


def main(project_root, iaa_dir_name, annotation_conf, tolerance):
        
    # Get annotators 
    print('\nSearching for annotators...')
    annotator_paths = [f.path for f in os.scandir(project_root) \
            if f.is_dir() and iaa_dir_name in os.listdir(f)]
    print(f'Annotator directories are: {annotator_paths}')

    # Get all combinations of pairs 
    print('\nGetting all combinations of annotators..') 
    annotator_pairs = itertools.combinations(annotator_paths, 2)

    # Read annotation_conf to look for symmetric relations 
    print('\nSearching for symmetric relations in annotation.conf...')
    with open(annotation_conf) as myf:
        file_lines = myf.readlines()
    
    symm_rels = []
    for line in file_lines:
        if '<REL-TYPE>:symmetric' in line:
            non_whitespace = len(re.match(r"\s*", line, re.UNICODE).group(0))
            end_tab = line.index('\t', non_whitespace)
            relation_type = line[non_whitespace:end_tab]
            if relation_type[0] == '!':
                relation_type = relation_type[1:]
            symm_rels.append(relation_type)
    print(f'Found {len(symm_rels)} symmetric relations. They are:\n{symm_rels}')

    # Get IAA for each pair of annotators 
    print('\nCalculating IAA for all annotator pairs...')
    annotator_pairs_iaas = {}
    for pair in annotator_pairs:
        print(f'\nCalculating IAA for pair {pair}')
        # Get overlapping docs for the annotators 
        print('\nGetting overlapping documents between annotators...')
        files_in_common = get_overlapping_docs(pair[0], pair[1], iaa_dir_name)
        print(f'Files in common are: {files_in_common}')

        # Get IAA for files 
        iaas = {}
        for f in files_in_common:
            print(f)
            # Get df for each one 
            ann_df1 = make_ann_df(f'{pair[0]}/{iaa_dir_name}/{f}')
            ann_df2 = make_ann_df(f'{pair[1]}/{iaa_dir_name}/{f}')

            # Calculate f1 for this doc pair  
            iaa = calculate_iaa(ann_df1, ann_df2, symm_rels, tolerance=tolerance)
            iaas[f] = [iaa]
        
        # Put the pairs' per-doc scores in the dict
        annotator_pairs_iaas[pair] = iaas

    # Calculate statistics 
    print('\nCalculating overall statistics...')
    get_iaa_stats(annotator_pairs_iaas)

    print('\nDone!')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Calculate relation IAA')

    parser.add_argument('project_root', type=str,
            help='Path to top-level directory containing all annotators')
    parser.add_argument('iaa_dir_name', type=str,
            help='Name of the directory that all annotator have in common, '
                'on which IAA should be calculated.')
    parser.add_argument('annotation_conf', type=str,
            help='Path to the annotation.conf file for the project.')
    parser.add_argument('tolerance', type=str,
            help='What tolerance to use for the calculation. Options are '
            'STRICT, SEMI-STRICT, RELATION-LOOSE, ENTITY-LOOSE')
            
    args = parser.parse_args()

    args.project_root = os.path.abspath(args.project_root)
    args.annotation_conf = os.path.abspath(args.annotation_conf)

    main(args.project_root, args.iaa_dir_name, args.annotation_conf, args.tolerance)
