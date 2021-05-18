"""
Extract abstracts as .txt files from a PubMed-formatted .txt file resulting from a PubMed search. 

Author: Serena G. Lotreck
"""
import argparse 
import os 

def parse_abstracts(abstracts_txt, dest_dir):
        """
        Parse and save abstracts from a PubMed formatted .txt file. Gets PMID to use as file name.

        Note: does not clean (lowercase, strip newline) text.

        parameters:
                abstracts_txt, str: path to PubMed formatted .txt file containing abstracts 
                dest_dir, str: path to directory to save abstract files

        returns:
                None
        """
        print('\nLooking for abstracts...')

        # Keys are PMID's, values are abstracts
        abstracts = {}

        # Read through the file 
        with open(abstracts_txt) as myfile:
                all_lines = myfile.readlines()

                # Define housekeeping variables
                in_abstract = False
                abstract = ''
                pmid_found = False
                pmid = ''

                # Look for PMID and then abstract
                for line in all_lines:

                        # Look for next PMID
                        if not in_abstract and not pmid_found:
                                if line[:6] == 'PMID- ':
                                        pmid_found = True
                                        
                                        # Store PMID
                                        pmid = line[6:-1] # Drop newline character
                        
                        # Look for start of abstract 
                        elif not in_abstract and pmid_found:
                                if line[:6] == 'AB  - ':
                                        in_abstract = True
                                        
                                        # Add first line to abstract
                                        abstract += line[6:]

                        # Look for the end of the abstract
                        elif in_abstract and pmid_found:
                                
                                # Keep adding lines until the end 
                                if line[:6] == '      ':
                                        abstract += line[6:]
                                else:
                                        # Reset boolean housekeepers 
                                        in_abstract = False
                                        pmid_found = False
                                        
                                        # Add to abstracts dict 
                                        abstracts[f'PMID{pmid}'] = abstract
                                        print(f'\nSnapshot of abstract for PMID{pmid}:\n{abstract[:200]}...')

                                        # Reset information housekeepers
                                        abstract = ''
                                        pmid = ''

        # Save the abstracts as files
        print('\nSaving abstracts...')
        for pmid, abstract in abstracts.items():
                save_name = f'{dest_dir}/{pmid}_abstract.txt'

                with open(save_name, 'w') as text_file:
                        text_file.write(abstract) 

        print('\nDone!')


def main(abstracts_txt, dest_dir):
        """
        Get abstracts.

        parameters:
                abstracts_txt, str: path to PubMed formatted .txt file containing abstracts 
                dest_dir, str: path to directory to save abstract files

        returns:
                None
        """
        parse_abstracts(abstracts_txt, dest_dir)


if __name__ == '__main__':
        parser = argparse.ArgumentParser('Get abstracts from PubMed file')

        parser.add_argument('-abstracts_txt', type=str, help='Path to PubMed-formatted txt file containing abstracts')
        parser.add_argument('-dest_dir', type=str, help='Directory to save the abstracts')

        args = parser.parse_args()

        args.abstracts_txt = os.path.abspath(args.abstracts_txt)
        args.dest_dir = os.path.abspath(args.dest_dir)

        main(args.abstracts_txt, args.dest_dir)
        
