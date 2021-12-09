# knowledge-graph
Code for the project *Straying off-topic: Automated information extraction and knowledge graph construction in the plant sciences with out-of-domain pre-trained models*

## Respository contents
* `annotation`: Contains scripts for annotation-related tasks. These include utility scripts (`abstract_scripts`), experimental scripts (`verb_annotations`), scrupts to calulate IAA (`iaa`), and the most recent version of the `annotation.conf` files used for annotation in brat (`brat`)
* `data_retreival`: Contains scripts for obtaining raw text data. `abstracts_only` contains scripts to download abstracts from PubMed, and `doc_clustering` contains the scripts to choose from the downloaded abstracts for downstream use. `oa_subset` gets full text XML from the [PubMed Open Access Subset](https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/); this project is currently only using abstracts, so this code has not been utilized for downstream tasks.
* `graph_formatting`: Contains scripts for turning model output into the [GraphViz DOT format](https://graphviz.org/doc/info/lang.html) for visualization in cytoscape. This code currently has an issue where, although the output is compliant with DOT, it cannot be visualized in cytoscape; TODO resolve this issue
* `jupyter_notebooks`: Miscellaneous jupyter notebooks with data visualizations
* `models`: Contains code to run the various kinds of models, both `benchmarks` and `neual models`, as well as a script to evaluate performance model-agnostically. 
* `tests`: Unit tests 


