# Data Retreival
This directory contains two methods for obtaining text data from articles on PubMed: `oa_subset` and `abstracts_only`, as well as the code to select abstracts for a corpus by clustering the vector representations of abstracts. 
>
`oa_subset` contains two scripts to pull full `.nxml` files from the [PubMed Open Access Subset](https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/) and extract plain text. Details on usage can be found in the `README` in that directory.
>
`abstracts_only` contains a script to get plain text abstracts directly from a PubMed search. Usage: 
```
python getAbstracts.py -abstracts_txt /path/to/PubMed/file.txt -dest_dir path/to/save/folder/
```
The PubMed file is obtained by saving search results in "PubMed" format.
>
`doc_clustering` contains scripts and a README with instructions about how to use the scripts to cluster and select from the abstracts obtained from `abstracts_only`. 
