# Retreiving text from the PubMed OA Subset 
These scripts allow the retreival of full text and abstracts from the PubMed OA subset based on a list of PMID's. These ID's can be obtained in any way, so long as they are passed as a single column `.txt` file. The easiest way to obtain this file is to use the results of a PubMed search, selecting those results which should be included and downloading the list of PMID's from PubMed's search interface. However, it should be noted that even if the "Free full text" option is checked in the search options, many of those papers will not be available in the OA Subset, and the number of papers extracted with this process will be fewer than the number of PMID's in the original list. 

## `getPapers.py`
This script retrieves and unzips the folders containing the `.pdf`, `.nxml`, and other files associated with each paper. This script uses the `.csv` version of the `oa_index` file. 
>
Usage:
```
python getPapers.py -searchPMIDs /myHomeDir/pubmed-data/pmid-jasmonicac-set.txt -oa_index /myHomeDir/pubmed-data/oa_file_list.csv -dest_dir /myHomeDir/pubmed-data/ -baseURL ftp://ftp.ncbi.nlm.nih.gov/pub/pmc -download t -extract t
```

## `extractText.py`
This script extracts plain text from the `.nxml` file included in each unzipped directory. It created two files, one for the abstract and one for the full text. 
>
Usage;
```
python extractText.py -top_dir /dir/with/unzipped/folders/
```

The files are saved with the PMCID as the prefix and with either `_abstract.txt` or `_fullText.txt` as the suffix.
