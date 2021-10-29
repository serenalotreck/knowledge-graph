## Keyword matching with the Planteome database 
The code in this directory is for a simple named entity recognition (NER) pipeline that uses rule-based matching of terms from the [Planteome](https://planteome.org/) database. The names and name synonyms recorded in the [databse files](http://palea.cgrb.oregonstate.edu/viewsvn/associations/) are obtained and used with spaCy's [PhraseMatcher](https://spacy.io/api/phrasematcher/) to efficiently match terms in a given set of abstracts. The final product is a set of `.ann` files that can be visualized in the [brat annotation tool](https://brat.nlplab.org/).

### Usage 
#### Getting Planteome
The entirety of the Planteome database can be downloaded using the following command:
```
wget -r -nH --cut-dirs=2 -l2 -np "http://palea.cgrb.oregonstate.edu/svn/associations" -A "*.assoc"
```
If you need the modify date to be the date you downloaded the files (for example, if you're working with a scratch system that automatically deletes files older than a certain age), you can add the flag `--no-use-server-timestamps` to have the modify date be the date you downloaded the files, rather than the date they were last modified on the server. 

#### Getting keywords from Planteome
The script `get_keywords.py` get the databse names and synonyms from the [GAF-formatted](http://geneontology.org/docs/go-annotation-file-gaf-format-2.1/) `.assoc` files. The general usage of this script is:
```
python get_keywords.py <path to directory with .assoc files> <output directory> -file_prefix <name to prepend to file names>
```
**TODO:** Modify this script to recursively search a directory tree, rather than just one directory

#### Matching keywords 
The script `phrasematch_keywords.py` uses the PhraseMatcher to efficiently match terms from the keywords in a set of abstracts. The script outputs a set of `.ann` files, which are [brat standoff format](https://brat.nlplab.org/standoff.html) files encoding the annotations of which text spans in the documents are entities. The `.ann` files are saved back to the same directory that the original `.txt` files are in, which allows easy visualization with brat. Usage:
```
python phrasematch_keywords.py <Path to directory with .txt files> <Set of paths for keyword files, can be more than one file> --use_scispacy
```
If the `--use_scispacy` flag is specified, [scispacy](https://allenai.github.io/scispacy/) wil be used for tokenization.
