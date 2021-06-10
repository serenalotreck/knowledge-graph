# `graph_formatting`
The scripts in this directory are for formatting the output of various NER/RE algorithms.

## Usage 
### `dygiepp_to_DOT.py` 
For use with the output of [dygiepp](https://github.com/dwadden/dygiepp). Makes a DOT-formatted file with the entire KG. Most likely this graph will be too big for rendering in any graph visualizer, so `graph_filtering.py` offers options to reduce the size of the graph. 
<br>
Usage: 
```
python dygiepp_to_DOT.py -dygiepp_preds ../data/first_manuscript_data/dygiepp/pretrained_output/no_punct_ACE05_predictions.jsonl -graph_name noPunct_ACE05_all -out_loc ../data/first_manuscript_data/dot_files/

```
### `graph_filtering.py` 
Offers several options for filtering the main KG produced by `dygiepp_to_DOT.py`. Options include:
* `"keyword_cluster"`: returns a graph with all nodes/edges that are connected to the keyword(s) provided
* `"keyword_direct"`: returns only nodes/edges that are connected to the keyword(s) provided
* `"random_num"`: returns the supplied number of triples/entities

By providing the argument `"all"`, all three of these options will be used to create three different graphs -- this is the default for the filtering option. There is also an option (specified by the flag `--remove_ents`) to completely exclude "loose" entities (entities not connected to any others). 
<br>
Usage: 
```
python graph_filtering.py -dot_file ../data/first_manuscript_data/dot_files/SciERC_graph_subset.dot -keywords photosynthesis pathways -num 5 --remove_ents -out_loc ../data/first_manuscript_data/dot_files/
```
**Note:** In order to pass entities that consist of multiple words (i.e. that have spaces in them), the spaces need to be escaled on the command line. For example, "jasmonic acid" becomes `jasmonic\ acid`. 
