"""
Check if files are missing columns (should have 18) or if the date is
misformatted.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath

import pandas as pd


def main(file_list):

    print('\nReading in file names...')
    with open(file_list) as f:
        problematic_files = f.readlines()

    print('\nMaking dfs from files')
    for i, f in enumerate(problematic_files):
        print(f'Working on file {i} of {len(problematic_files)}')
        start_line = 0
        with open(f.rstrip()) as myf:
            lines = myf.readlines()
            for line in lines:
                if line[0] == '!':
                    start_line = lines.index(line)
                else:
                    break
        print(lines[start_line+1])
        #print('\n'.join(lines))
        try:
            df = pd.read_csv(f.rstrip(), sep='\t', skiprows=start_line+1, header=None)
            print(f'\n\n\n{f}')
            print(df.head())
        except:
            print('ouch')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Check bad GAF files')

    parser.add_argument('file_list', type=str,
            help='Path to .txt file where each line is a problematic file')

    args = parser.parse_args()

    args.file_list = abspath(args.file_list)

    main(args.file_list)
