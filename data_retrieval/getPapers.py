"""
Module to obtain and extract relevant XML files from PubMed.

Standalone usage:
python getPapers.py <searchPMIDs path> <oa index path> <dest_dir> <baseURL>

Author: Serena G. Lotreck
Date began: 09Jun2020
"""
import os
import argparse

import pandas as pd
import wget
import shutil

def getPapersPubmed(paperIndex, searchResults, baseurlRemote, dest, download, extract):
	"""
	Using the PMID list from a given PubMed search, query the open
	access subset index to find the URL for each paper, and download to
	the destination directory.

	Each URL downloads a tar.gz file which contains an .nxml file for the
	article fulltext, image files from the article, graphics for display
	versions of equations or chemical schemes, supplementary data files,
	PDF if available, and converted video files. More information can
	be found at https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/

	parameters:
		paperIndex, df: dataframe made from oa_file_list.csv
		searchResults, df: dataframe of PMIDs from a PubMed search,
			made from the csv file downloaded after search
		baseurlRemote, str: the base URL that must preceed the filenames
			in paperIndex['filenames'] in order to use wget.
			For PubMed OA package files, the base URL is
			ftp://ftp.ncbi.nlm.nih.gov/pub/pmc
		dest, str: the directory to download and unpack tar.gz files
		download, str: t/f of whether to download new files
		extract, str: t/f of whether to extract files after downloading

	returns: a df containing the PMID's and PMCID's of the relevant papers
	"""
	# select only the rows that pertain to our search
	print('===> Filtering open access papers by PubMed search results <===')
	paperIndexSearch = paperIndex.loc[paperIndex['PMID'].isin(searchResults['PMID'])]

	# make the filename column into a list for easier use
	filenames = paperIndexSearch['filename'].tolist()

	# iterate through filename list and wget each one
	if download.lower() in ['t','true']:
		downloadFiles(filenames, baseurlRemote, dest)

	# extract all tar.gz files in dest
	if extract.lower() in ['t','true']:
		extract_all_targz(dest, dest)

	# make df with PMCID and PMID
	print('===> Making ID dataframe <===')
	IDnums = pd.concat([paperIndexSearch['PMCID'],paperIndexSearch['PMID']], axis=1)
	IDnums = IDnums.astype({'PMID':'Int64'})

	print('Done!')
	return IDnums


def getPapersElsewhere(files, baseurlRemote, dest, download, extract):
	"""
	Download and extract a list of files from a non-PubMed remote source.

	parameters:
		files, list of str: a list of files to get and extract
		baseurlRemote, str: the base URL that must preceed the filenames
			in paperIndex['filenames'] in order to use wget.
			For PubMed OA package files, the base URL is
			ftp://ftp.ncbi.nlm.nih.gov/pub/pmc
		dest, str: the directory to download and unpack tar.gz files
		download, str: t/f of whether to download new files
		extract, str: t/f of whether to extract files after downloading
	"""
	# iterate through filename list and wget each one
	if download.lower() in ['t','true']:
		downloadFiles(files, baseurlRemote, dest)

	# extract all tar.gz files in dest
	if extract.lower() in ['t','true']:
		extract_all_targz(dest, dest)


def downloadFiles(filenames, baseurlRemote, dest):
	"""
	Uses the python wget module to download files form source.

	parameters:
		filenames, list of str: list of files to wget
		baseurlRemote, str: the base URL that must preceed the filenames
			in paperIndex['filenames'] in order to use wget
		dest, str: the directory to download and unpack tar.gz files
	"""
	print('===> Wgetting files from source {baseURL} <==')
	print(f'Snapshot of files to be retrieved: {filenames[:5]}')
	for i, name in enumerate(filenames):
		url = os.path.join(baseurlRemote, name)
		print(f'\nFile number {i} of {len(filenames)}')
		filename = wget.download(url, out=dest)


def extract_all_targz(path_to_zips, extract_path):
	"""
	Unzips all tar.gz files in the directory path_to_zips to the directory
	extract_path

	parameters:
		path_to_zips, str: path to the files to be unzipped
		extract_path, str: the directory where unzipped files will be
			stored
	"""
	print(f'===> Extracting tar.gz files from {path_to_zips} <===')
	# identify which files to unzip
	filesToExtract = [os.path.join(path_to_zips, f) for f in os.listdir(path_to_zips) \
	if os.path.isfile(os.path.join(path_to_zips, f)) and 'tar.gz' in f]

	# check that there are files to unzip
	if filesToExtract == []:
		print('No tar.gz files available to unzip, exiting module')
	else:
		print(f'Snapshot of files to extract: {filesToExtract[:5]}')

		for i, filename in enumerate(filesToExtract):
			print(f'Unpacking file {filename}, file {i} of {len(filesToExtract)}')
			shutil.unpack_archive(filename, extract_path)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Obtain and unpack XML '
		'files from PubMed')
	parser.add_argument('-file_list', type=str, help='Path to csv containing '
		'one column with filenames to retrieve. Use if getting files from '
		'a source other than PubMed', default='')
	parser.add_argument('-sep', type=str, help='To be used with -files',
		default=',')
	parser.add_argument('-searchPMIDs', type=str, help='csv file '
		'downloaded from a PubMed search, with one column of PMIDs',
		default='')
	parser.add_argument('-oa_index', type=str, help='Path to PubMed open '
		'access index csv file. NOTE: csv contains one more col than '
		' the equivalent txt file, MUST use csv', default='')
	parser.add_argument('-dest_dir', type=str, help='Directory to place '
		'downloads and unzipped files,. default is cwd', default='')
	parser.add_argument('-baseURL', type=str, help='Base URL to prepend '
		'to filenames in order to wget. Default is baseURL from PubMed',
		default='ftp://ftp.ncbi.nlm.nih.gov/pub/pmc')
	parser.add_argument('-download', type=str, help='t/f to download files, '
		'if false, will use any tar.gz file in dest_dir for extraction', default='f')
	parser.add_argument('-extract', type=str, help='t/f to extract the '
		'downloaded files', default='f')

	args = parser.parse_args()

	# check what behaviors are requested and execute
	if (args.searchPMIDs == '' and args.oa_index == '') \
	and args.files != '': # non-PubMed search
		print('===> Initiating non-PubMed file extraction <===')
		files = pd.read_csv(args.files,sep=args.sep)
		# check that there is only one col
		if files.shape[1] > 1:
			print('Too many columns in files.csv, please try again')
		elif files.shape[1] == 1:
			filesList = files[0].tolist()
			getPapersElsewhere(filesList, args.baseURL, args.dest_dir,
			args.download, args.extract)

	elif (args.searchPMIDs != '' and args.oa_index != '') \
	and args.files == '': # PubMed search
		print('===> Initiating PubMed file extraction <===')
		getPapersPubmed(args.oa_index, args.searchPMIDs, args.baseURL,
		args.dest_dir, args.download, args.extract)

	elif (args.searchPMIDs == '' and args.oa_index == '') \
	and args.files == '':
		print(f'===> Initializing tar.gz file extraction from {args.dest_dir} <===')
		extract_all_targz(args.dest_dir, args.dest_dir)

	else:
		print('It is not clear based on the files you\'ve provided which search '
		'capability you want to use, please try again')
