# knowledge-graph
Code exploring the creation of knowledge graphs from plant science papers
## Usage
### TODO
--------
Make a script for conda environment once all modules have been decided upon 
### getPapers.py
----------------
This script retrieves tar.gz files from some online source and extracts the downloads. <br>

#### PubMed-specific behaviors
This script is designed specifically for use with the [PubMed Open Access Subset](https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/), and is designed to obtain a group of open access papers based on the results of an arbitrary search. To use the tool this way, start by performing a PubMed search on your keywords of interest. After searching, save the search results in the PMID format. This file is then used in this script (the `-searchPMIDs` argument) to obtain downloads (including .nxml files and PDFs if available, more details on the contents of downloads can be found [here](https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/)) of those search results available in the Open Access Subset.<br>

In addition to the search results PMID file, the PubMed download procedure requires the csv version of the OA file index. Note that the default value for `-oa_index` is the full OA subset. If you need papers with only commercial or non-commercial use licenses, use the respective index files, all of which can be found [here](https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/). <br>

The baseURL for PubMed is ftp://ftp.ncbi.nlm.nih.gov/pub/pmc, and this is the default for the `-baseRUL` argument.<br>

Example usage for the PubMed strategy:
```
python getPapers.py -searchPMIDs /myHomeDir/pubmed-data/pmid-jasmonicac-set.txt -oa_index /myHomeDir/pubmed-data/oa_file_list.csv -dest_dir /myHomeDir/pubmed-data/ -baseURL ftp://ftp.ncbi.nlm.nih.gov/pub/pmc -download t -extract t
```

#### General behaviors
In order to use this script to get files from another source, use the `-files` argument instead of `-searchPMIDS` and `-oa_index`. This script was designed for the characteristics of the PubMed OA Subset, so there are some particulars that must be observed when using it for another source. In order to get the desired behavior, you must:
1. *Only* pass `-files`, not `-searchPMIDS` and `-oa_index`
2. Provide a `-files` that is a single column csv or txt file with no header, containing the filenames. If the filenames include the baseURL, be sure to pass `-baseURL ''`.
3. If `-files` is not comma-separated, be sure to provide the `-sep` argument.
4. If you want to download *and* extract, ensure that the files you are downloading are in `tar.gz` format: this is the only format that this module supports unzipping.

This script can also be used to simply extract `tar.gz` files. To do so, don't pass any of the three arguments `-files`, `-searchPMIDS`, and `-oa_index`. This will prompt the unpacking of all `tar.gz` files in the directory `-dest_dir`. <br> 

Example usage for a non-PubMed source:
```
python getPapers.py -file_list myFiles.csv -dest_dir /myHomeDir/papers/ -baseURL '' -download t -extract f
```

Example of `tar.gz` unpacking usage:
```
python getPapers.py -dest_dir /myHomeDir/papers/ -baseURL '' -download t -extract f
```
