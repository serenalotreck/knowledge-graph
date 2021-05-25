# Document selection with doc vector representations 
In order to choose a semantically diverse selection of abstracts for either an annotated corpus or a body of documents for applying KG models downstream, this code generates vector representations of the provided documents, clusters the vectors, and selects a given number of abstracts evenly across the clusters. 

## Pipelined usage
`doc_clustering.py` runs the other scripts in the directory to obtain selected abstracts in an end-to-end pipeline. Example usage after obtaining abstracts via the script in `knowledge-graph/data_retreival/abstracts_only/`:

```
python doc_clustering.py -data path/to/data/ -num_abstracts 8000 -out_loc path/to/save/ -new_dir_name my_abstracts
```

## Independent usage 
Each of the other scripts can also be run standalone. Example usages:

```
python doc2vec.py -data path/to/data/ -use_trained path/to/pretrained_model/ -vector_size 50 -model_type 'DBOW' -out_loc path/to/save/
```

```
python cluster_docs.py -vecs /path/to/vecs.csv -num 8000 -out_loc path/to/save/
```

```
python dump_abstracts.py -abstract_list path/to/chosen_abstracts.csv -parent_dir path/to/make/new/dir/ -new_dir_name my_new_dir 
```
