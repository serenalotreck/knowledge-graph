# knowledge-graph
Code exploring the creation of knowledge graphs from plant science papers
## Usage
### getPapers.py
This script retrieves a subset of the [PubMed Open Access Subset](https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/), based on the results of an arbitrary search. After searching a term of interest, save the search results in the PMID format. This file is then used in this script to obtain downloads (including .nxml files and PDFs if available, more details on the contents of downloads can be found [here](https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/)) of those search results available in the Open Access Subset.<br>

This procedure additionally needs the csv version of the file index. Note that the example below uses the index for the full OA subset. If you need papers with only commercial or non-commercial use licenses, use the respective index files.<br>

The baseURL for PubMed is ftp://ftp.ncbi.nlm.nih.gov/pub/pmc.<br>

The order of arguments is as follows:
```
python getPapers.py <list of PMID from PubMed search results> <open access csv index file> <directory to put zipped and unzipped retrieved filed> <base URL for PubMed ftp>
```
Example usage of getPapers.py:
```
  python getPapers.py /mnt/scratch/lotrecks/kg-pubmed-data/JA_test/pmid-jasmonicac-set.txt /mnt/scratch/lotrecks/kg-pubmed- data/JA_test/oa_file_list.csv /mnt/scratch/lotrecks/kg-pubmed-data/JA_test/ ftp://ftp.ncbi.nlm.nih.gov/pub/pmc
```
