"""
Code to calculate an IAA for relation annotations. 

Calculates F1 with 4 kinds of tolerances. 
    (1) STRICT. a relation is the same only if the type of the entities and
        relation are the same. Entities  must have the same span boundaries.
    (2) SEMI-STRICT. a relation is the same only if the type of the entiies
        and relation are the same.  Entities can have different span boundaries, 
        and are considered the same if they overlap.
    (3) RELATION-LOOSE. a relation is the same only if the relation connects
        two entities that are considered equivalent. Relation type can be different,
        and entities are considered the same if they have the same  type and overlap.
    (4) ENTITY-LOOSE. a relation is the same if it has the same type and direction, 
        but the argument entities can have different types & only have to overlap.

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
    print(f'Mean: {overall.mean}, Standard deviation: {overall.std}')


def calculate_f1(a,b,c):
    """
    Calculate balanced F1 score for a pair of docs.

    parameters: 
        a, int: number of annotations both annotators agree on
        b, int: number of annotations annotator 2 has that annotator 1 does not
        c, int: number of annotations annotator 1 has that annotator 2 does not 

    returns:
        f1, float: balanced F1 score
    """
    return (2*(a/(a+b))*(a/(a+c)))/((a/(a+b))+(a/(a+c)))


def get_strict_agreement_table(ann_df1, ann_df2):
    """
    Get the values in the agreement table for two documents according to
    the strict tolerance. 
    
    parameters:
        ann_df1, df: df of .ann file for rater 1
        ann_df2, df: df of .ann file for rater 2
    
    returns:
        a, b, c: ints, the values from the agreement table 
    """
    # Number of rows that are the same between the two is a
    ## Approach: Combine the two dataframes and used the duplicated()
    ## method to get the number of rows that are duplicates 
    combined = ann_df1.append(ann_df2)
    a = (combined.duplicated().value_counts().loc[True])

    # Number of rows that ann_df1 has that ann_df2 does not is b 
    ## Approach: subtract a from the number of rows 
    b = len(ann_df1) - a

    # Number of rows that ann_df2 has that ann_df1 does not is c  
    ## Approach: subtract b from the number of rows 
    c = len(ann_df2) - a

    return a, b, c


def calculate_iaa(ann_df1, ann_df2, tolerance='STRICT'):
    """
    Calculate IAA for a pair of documents. The default tolerance for the 
    calculation is STRICT, where entities must have the same span boundaries 
    and the same types, and relations must have the same type and point the 
    same direction.

    parameters:
        ann_df1, df: df of .ann file for rater 1
        ann_df2, df: df of .ann file for rater 2
        tolerance, str: tolerance with which to calculate IAA. Options are 
            STRICT, SEMI-STRICT, RELATION-LOOSE, ENTITY-LOOSE
    """
    # Get agreement values
    if tolerance == 'STRICT':
        a, b, c = get_strict_agreement_table(ann_df1, ann_df2)
    elif tolerance == 'SEMI-STRICT':
        pass
    elif tolerance == 'RELATION-LOOSE':
        pass
    elif tolerance == 'ENTITY-LOOSE':
        pass

    # Calculate F1
    return calculate_f1(a, b, c)


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
    relation.append(entry[:type_end_idx])
    
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
        
        if ';' not in arg_entry:
            
            # Get entity offsets
            print(arg_entry)
            start_offset_start_idx = arg_entry.index(' ') + 1
            in_between_space = arg_entry.index(' ', start_offset_start_idx)
            end_offset_end_idx = arg_entry.index('\t', in_between_space+1)
            start_offset = int(arg_entry[start_offset_start_idx:in_between_space])
            print(arg_entry[in_between_space+1:end_offset_end_idx])
            end_offset = int(arg_entry[in_between_space+1:end_offset_end_idx])
            
            # Get entity type 
            ent_type = arg_entry[:start_offset_start_idx-1]
            
            # Make tuple and add to relation entry
            relation.append((start_offset, end_offset, ent_type))
      
      else:
          num_semicolons = arg_entry.count(';')
          ## TODO: come up with a way to deal with multiple spans 


    return relation 


def make_ann_df(ann):
    """
    Converts a brat standoff formatted .ann  file into a dataframe of the form:

    |  TYPE  |  Arg1  |  Arg2  |

    where Arg1 and Arg2 are entities of the form (start_offset, end_offset, TYPE)
    
    parameters:
        ann, str: path to .ann file to convert 

    returns: 
        ann_df, df: dataframe version of the .ann file 
    """
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


def main(project_root, iaa_dir_name, tolerance):
        
    # Get annotators 
    annotator_paths = [f.path for f in os.scandir(project_root) if f.is_dir()]

    # Get all combinations of pairs 
    annotator_pairs = itertools.combinations(annotator_paths, 2)

    # Get IAA for each pair of annotators 
    annotator_pairs_iaas = {}
    for pair in annotator_pairs:
        print(pair)
        # Get overlapping docs for the annotators 
        files_in_common = get_overlapping_docs(pair[0], pair[1], iaa_dir_name)

        # Get IAA for files 
        iaas = {}
        for f in files_in_common:
            print(f)
            # Get df for each one 
            ann_df1 = make_ann_df(f'{pair[0]}/{iaa_dir_name}/{f}')
            ann_df2 = make_ann_df(f'{pair[1]}/{iaa_dir_name}/{f}')

            # Calculate f1 for this doc pair  
            iaa = calculate_iaa(ann_df1, ann_df2, tolerance=tolerance)
            iaas[f] = iaa
        
        # Put the pairs' per-doc scores in the dict
        annotator_pairs_iaas[pair] = iaas

    # Calculate statistics 
    get_iaa_stats(annotator_pairs_iaas)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Calculate relation IAA')

    parser.add_argument('project_root', type=str,
            help='Path to top-level directory containing all annotators')
    parser.add_argument('iaa_dir_name', type=str,
            help='Name of the directory that all annotator have in common, '
                'on which IAA should be calculated.')
    parser.add_argument('tolerance', type=str,
            help='What tolerance to use for the calculation. Options are '
            'STRICT, SEMI-STRICT, RELATION-LOOSE, ENTITY-LOOSE')
            
    args = parser.parse_args()

    args.project_root = os.path.abspath(args.project_root)

    main(args.project_root, args.iaa_dir_name, args.tolerance)
