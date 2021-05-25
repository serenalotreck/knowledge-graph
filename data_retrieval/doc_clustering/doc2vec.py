"""
A module for obtaining Doc2Vec representations of abstracts. Outputs a file 
containing the vector representations of the apply data.

Uses gensim's implementation of Paragraph Vector, with command line options to 
choose between the DM and DBOW implementations.

A pretrained model can be loaded or used, or provided data can be 
used to train a new model. A newly trained model will automatically be saved.

All gensim Doc2Vec code based on: 
https://radimrehurek.com/gensim/auto_examples/tutorials/run_doc2vec_lee.html

Author: Serena G. Lotreck
"""
import os
import argparse

import gensim
import smart_open
import collections
import random
import pandas as pd


def common_sense_check(train_docs, model):
    """
    Check model performance by treating training data as unseen data and looking
    for most similar documents in training set. Prints a percentage that 
    represents how frequently a document is found to be most similar to 
    itself - higher values indicate better performance.

    parameters:
        train_docs, list of TaggedDocument: training documents
        model: the model

    returns: None
    """
    # Get the similarity ranks for each doc
    ranks = []
    second_ranks = []
    for doc in train_docs:
        inferred_vector = model.infer_vector(doc.words)
        sims = model.dv.most_similar([inferred_vector], topn=len(model.dv))
        rank = [docid for docid, sim in sims].index(doc.tags[0])
        ranks.append(rank)

        second_ranks.append(sims[1])

    # Count how many of the docs were matched as most similar with themselves 
    counter = collections.Counter(ranks)
    percent_correct = (counter[0]/(counter[0]+counter[1]))*100
    print(f'{percent_correct:.2f}% of training documents were found to be most '
            'similar to themselves.\n')


def train_model(train_docs, vector_size, model_type):
    """
    Instantiate and train a Doc2Vec model. 

    parameters:
        train_docs, list of TaggedDocument objects: training data
        vector_size, int: number of dimensions for the vectors in Doc2Vec
        model_type, str: DM or DBOW, which implementation of PV to use
    
    returns:
        model: a trained model
    """
    # Convert model type to int
    if model_type == 'DM':
        model_type = 1
    else:
        model_type = 0
    
    # Instantiate model
    model = gensim.models.doc2vec.Doc2Vec(vector_size=vector_size, 
            min_count=2, dm=model_type, epochs=20)

    # Build a vocabulary 
    model.build_vocab(train_docs)

    # Train the model
    model.train(train_docs, total_examples=model.corpus_count, 
            epochs=model.epochs)

    return model


def get_tags(data):
    """
    Get the names of the unlabeled test/apply data.

    parameters:
        data, str: path to directory containing data

    returns:
        names, list of str: the file names 
            of the files in the data directory
    """

## TODO: Need to write a test making sure that this actually corresponds to the 
## order of docs in the processed list

    # Get list of files in data directory
    # These are the names
    names = [f for f in os.listdir(data) 
            if os.path.isfile(os.path.join(data, f))]
    
    return names


def preprocess_data(data, train=True):
    """
    Prep data for input into gensim PV.

    Tokenizes input documents, and associates a tag with each doc if 
    train = True. Tags are the name of the document file.

    parameters:
        data, str: path to directory containing data 
        train, bool: True if the data is the training set and should have tags, 
            False otherwise. 

    returns:
        a generator containing the documents
    """
    # Get list of files in data directory
    # These are the tags
    names = get_tags(data)

    # Tokenize documents & add tags if training data
    for i, f in enumerate(names):
        with smart_open.open(f'{data}/{f}', encoding='iso-8859-1') as myfile:
            line = myfile.read().replace("\n", " ")
            tokens = gensim.utils.simple_preprocess(line)
            if train:
                yield gensim.models.doc2vec.TaggedDocument(tokens, [names[i]])
            else:
                yield tokens


def main(data, use_trained, vector_size, model_type, out_loc):

    print('\n======> Generating vector representations <======\n')

    # Prepare and preprocess data
    print('\nPreprocessing data...\n')
    if not use_trained:
        train_docs = list(preprocess_data(data))
    else:
        apply_docs = list(preprocess_data(data, False))

    # Train the model
    if not use_trained:
        print('\nTraining model...\n')
        model = train_model(train_docs, vector_size, model_type)
        print(f'Saving trained model as {out_loc}/doc2vec_model')
        model.save(f'{out_loc}/doc2vec_model')

    # Common-sense check
    if not use_trained:
        print('\nPerforming common-sense check...\n')
        common_sense_check(train_docs, model)

    # Load model 
    if use_trained:
        print('\nLoading saved model...\n')
        model = gensim.models.doc2vec.Doc2Vec.load(use_trained)

    # Get learned vectors
    print('\nGetting vectors from model...\n')
    if not use_trained:
        names = model.dv.index_to_key
        vectors = {}
        for name in names:
            vector = model.dv[name]
            vectors[name] = vector
    else:
        names = get_tags(data)
        vectors = {}
        for name, doc in zip(names, apply_docs):
            vector = model.infer_vector(doc)
            vectors[name] = vector

    # Write out vectors to a file
    print('\nWriting out vectors...\n')
    df = pd.DataFrame.from_dict(vectors, orient='index', 
            columns=[f'vector_dim{i}' for i in range(vector_size)])
    print('Snapshot of vectors:\n')
    print(df.head())
    df.to_csv(f'{out_loc}/doc2vec_vectors.csv')
    print(f'Vector file has been written to {out_loc}/doc2vec_vectors.csv\n')

    print('\nDone!\n')
    return f'{out_loc}/doc2vec_vectors.csv' # For use in doc_clustering.py

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Run Doc2Vec on abstracts')

    parser.add_argument('-data', type=str, 
            help='Path to a directory with documents. ', default=None)
    parser.add_argument('-use_trained', type=str, 
            help='Path to a pre-trained gensim model.', 
            default='False')
    parser.add_argument('-vector_size', type=int, 
            help='Number of dimensions for doc2vec vectors.',
            default=50)
    parser.add_argument('-model_type', type=str, 
            help='Which implementation of gensim Paragraph '
            'Vector to use. Options are DM and DBOW', default='DM') 
    parser.add_argument('-out_loc', type=str, help='Path to save output')

    args = parser.parse_args()

    if args.data is not None:
        args.data = os.path.abspath(args.data)
    if args.use_trained != 'False':
        args.use_trained = os.path.abspath(args.use_trained)
    else: args.use_trained = False
    args.out_loc = os.path.abspath(args.out_loc)
    
    main(args.data, args.use_trained, args.vector_size, args.model_type, 
            args.out_loc)


    
