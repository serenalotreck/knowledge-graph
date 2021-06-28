"""
Script to auto-generate .ann files and corresponding text files for sentences 
with relations that have been extracted by DyGIE++. The .ann file is compatible
with the brat annotation software.

Creates one .txt file of the form: 

    Sentence 1 says this. (PMID123)\n
    \n
    Sentence 2 says this. (PMID345)\n

And one .ann file of the form: 

    T1\tTYPE\sstart_offset\send_offset\tTEXT\n
    T2...

Since brat's .ann standoff format's relation ID (R<number>) is specific to 
relations that are non-text bound, here I will be including text-bound verbs
as "entities" (the "T<number>" ID is for text-bound entities) with the 
special type of RELATION.

More details on the .ann standoff format can be found at: 
    https://brat.nlplab.org/standoff.html

Author: Serena G. Lotreck
"""
import argparse
import os 
import jsonlines

def main(dygiepp_output, out_loc):

    # Read in dygiepp output 
    dygiepp_dicts = []
    with jsonlines.open(dygiepp_output) as reader:
        for obj in reader:
            dygiepp_dicts.append(obj)




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get relational verbs')

    parser.add_argument('dygiepp_output', type=str, 
            help='Path to dygiepp output file to be parsed')
    parser.add_argument('-out_loc', type=str, 
            help='Path to save the output')

    args = parser.parse_args()

    args.dygiepp_output = os.path.abspath(args.dygiepp_output)
    args.out_loc = os.path.abspath(args.out_loc)

    main(**vars(args))
