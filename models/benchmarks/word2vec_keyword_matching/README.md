## Keyword matching with word vector representations
The code in this directory is an extension of the basic, rules-based-only keyword mayching pipeline in the `ontology_keyword_matching` directory. This code also utilizes the keywords obtained by `get_keywords.py` (if you've come directly here without running that for the `ontology_keyword_matching` code yet, please see the [README](https://github.com/serenalotreck/knowledge-graph/blob/master/benchmarks/ontology_keyword_matching/README.md) for detail on how to run that before beginning here), but extends the simple rules-based matching scheme by incorporating word vectors, to match keywords that appear in semantically similar contexts, but may not specifically be keywords from Planteome.


## Usage

```
usage: word2vec_abstracts.py [-h] [--abstract-path ABSTRACT_PATH] [--keywords-path KEYWORDS_PATH] [--ngrams NGRAMS] [--model-type MODEL_TYPE] [--calc-keyword-sim]
                             [--sim-threshold SIM_THRESHOLD]

Word2vec on abstracts

optional arguments:
  -h, --help            show this help message and exit
  --abstract-path ABSTRACT_PATH
                        path to dir with abstracts you want to cluster
  --keywords-path KEYWORDS_PATH
                        path to dir with planteome keywords
  --ngrams NGRAMS       Length of possible grams to create (i.e. 'n'). Defaults to 1.
  --model-type MODEL_TYPE
                        'skip' for Skip-gram and 'cbow' for CBOW. Defaults to 'cbow'
  --calc-keyword-sim    When set, we get the words in vocab most similar to keywords
  --sim-threshold SIM_THRESHOLD
                        Similarity threshold when comparing keywords against vocab. Defaults to 0.75
```

Below is an example of fitting a CBOW word2vec model using bigrams. When finished the model is saved.
```
python word2vec_abstracts.py --abstract-path path/to/abstracts --keywords-path path/to/keywords --model-type cbow --ngrams 2
```

Once a model is trained, we can loop through all possible keywords in the vocabulary (words in abstracts) and find the other words that are most similar. This is done by:

1. Filtering for all planteome keywords that are in the vocabulary. If it's not in the vocab, we don't have a way of comparing to other words since no embedding exists. 
2. Compute the cosine similarity between the keyword and all other non-keywords in the vocabulary. Cosine similarity is a measure that ranges between 0 and 1 where 0 is dissimilar and 1 is highly similar.
3. Filter for all pairs when the cosine similarity is greater than a threshold set by the `--sim-threshold` argument. We assume if the score is greater than this, than they are sufficiently similar.

We can run this by setting the flag `--calc-keyword-sim`. This also assumes that a word2vec model for the specified `--model-type` and `--ngrams` is already trained and saved. Below is an example with a similarity threshold of 0.9:
```
python word2vec_abstracts.py --abstract-path path/to/abstracts --keywords-path path/to/keywords --model-type cbow --ngrams 2 --sim-threshold 0.9
```

This will output a file that contains the similar words to the keywords. It will output in the form of a json file called `{model_type}_{n}-gram_keyword_sim_{threshold}.json` (e.g. `skip_2-gram_keyword_sim_75`).

## TODO for word2vec:

1. Init with GLoVE?
