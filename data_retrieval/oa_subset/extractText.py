"""
Given a directory of unzipped folders scraped from the PubMed OA subset, extract plain text from PubMed 
nxml file in each subdirectory. Extracts the abstract to one file and full text to another, using the 
name of the directory (the PMCID) as a base identifier, and stores them in the same directory as the 
nxml from which they are extracted. 

Author: Serena G. Lotreck 
Date last modified: 13 Jan 2020
"""
import os
import argparse 

import pubmed_parser as pp


def extractAbstract(full_path, paper_dir, nxml_file):
	"""
	Extract abstract from nxml_file and write as .txt to paper_dir
	"""
	# Run parser 
	pubmed_xml_dict = pp.parse_pubmed_xml(f'{full_path}/{nxml_file}')
	
	# Write out abstract 
	with open(f'{full_path}/{paper_dir}_abstract.txt', 'w') as text_file:
		text_file.write(pubmed_xml_dict['abstract'])
	
	print('\nAbstract written!')


def extractFullText(full_path, paper_dir, nxml_file):
	"""
	Extract full text from nxml_file and write as .txt to paper_dir
	""" 
	# Run parser to get full text for all paragraphs 
	paragraph_dict_list = pp.parse_pubmed_paragraph(f'{full_path}/{nxml_file}', all_paragraph=True)

	# Concat paragraphs into full text 
	full_text = ''
	for paper_dict in paragraph_dict_list:
		full_text += ('\n\n' + paper_dict['text'])

	# Write out full text 
	with open(f'{full_path}/{paper_dir}_fullText.txt', 'w') as text_file:
		text_file.write(full_text)

	print('\nFull text written!')


def main(top_dir):
	"""
	Iterates over the directories pertaining to each paper, and extracts full text and abstract.

	parameters:
		top_dir, str: path to the directory containing extracted folders pertaining to papers
	"""
	# Get list of all subdirectories that begin with 'PMC'
	paper_dirs = [d for d in os.listdir(top_dir) if os.path.isdir(f'{top_dir}/{d}') 
			and d[0:3] == 'PMC']
	print(f'\nPaper directories found:\n{paper_dirs}')	

	# Extract full text and abstract for each paper 
	for paper_dir in paper_dirs:
		# Get full path 
		full_path = f'{top_dir}/{paper_dir}'
		# Get the nxml file 
		nxml_file = [f for f in os.listdir(full_path) if f.endswith('.nxml')]
		# Assert that there's only one .nxml
		assert (len(nxml_file) == 1), f'More than one nxml file for the directory {paper_dir}!'
		nxml_file = nxml_file[0]

		# Extract plain text
		print(f'\nExtracting text for paper {paper_dir}...')
		extractAbstract(full_path, paper_dir, nxml_file)
		extractFullText(full_path, paper_dir, nxml_file)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Extract full text from PubMed xml')

	parser.add_argument('-top_dir', type=str, help='Path to directory where PubMed unzipped '
				'directories are stored')

	args = parser.parse_args()

	args.top_dir = os.path.abspath(args.top_dir)

	main(args.top_dir) 
