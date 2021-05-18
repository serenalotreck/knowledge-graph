"""
A module for obtaining Doc2Vec representations of abstracts. Outputs a file 
containing the vector representations of the apply data.

Uses gensim's implementation of Paragraph Vector, with command line options to 
choose between the DM and DBOW implementations.

A pretrained model can be loaded or used, or training and test data can be 
provided to train a new model. A newly trained model will automatically be saved.

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


def test_check(test_docs, test, train_docs, model, out_loc):
    """
    Output a document where the user can check manually if documents 
    assigned as similar by the model are actually similar. Randomly 
    chooses 10 documents for comparison.
    
    parameters:
        test_docs, list of list: test documents
        test, str: path to test doc directory
        train_docs, list of TaggedDocument: list of training documents
        model: the model
        out_loc, str: path to save the output file

    returns: None
    """
    names = get_tags(test)

    with open(f'{out_loc}/doc2vec_test_output.txt', 'w') as myfile:
        for i in range(10):
            doc_idx = random.randint(0, len(test_docs) - 1)
            inferred_vector = model.infer_vector(test_docs[doc_idx])
            sims = model.dv.most_similar([inferred_vector], topn=len(model.dv))
            
            myfile.write(f'Test Document ({names[doc_idx]}): «{" ".join(test_docs[doc_idx])}»\n\n')
            myfile.write(f'SIMILAR/DISSIMILAR DOCS PER MODEL {model}\n\n')
            for label, index in [('MOST', 0), ('MEDIAN', len(sims)//2), ('LEAST',len(sims) - 1)]:
                target_tag = sims[index][0]
                target_object = [obj for obj in train_docs if obj.tags[0] == target_tag]
                myfile.write(f'{label}, similarity measure sims[index][1], '
                        f'doc name {sims[index][0]}:\n '
                        f'«{" ".join(target_object[0].words)}»\n\n')


def common_sense_check(train_docs, model):
    """
    Check model performance by treating training data as unseen data and looking
    for most similar documents in training set. Prints a percentage that represents
    how frequently a document is found to be most similar to itself - higher values 
    indicate better performance.

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
    print(f'{percent_correct:.2f}% of training documents were found to be most similar '
            'to themselves.\n')


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
    model.train(train_docs, total_examples=model.corpus_count, epochs=model.epochs)

    return model


def get_tags(data):
    """
    Get the names of the unlabeled test/apply data.

    parameters:
        data, str: path to directory containing data

    returns:
        names, list of str: the file names (stripped of file ext)
            of the files in the data directory
    """

## TODO: Need to write a test making sure that this actually corresponds to the 
## order of docs in the processed list

    # Get list of files in data directory
    files = [f for f in os.listdir(data) if os.path.isfile(os.path.join(data, f))]
    
    # Get names
    names = [os.path.splitext(f)[0] for f in files]

    return names


def preprocess_data(data, train=False):
    """
    Prep data for input into gensim PV.

    Tokenizes input documents, and associates a tag with each doc if train = True.
    Tags are the name of the document without the file extension.

    parameters:
        data, str: path to directory containing data 
        train, bool: True if the data is the training set and should have tags, 
            False otherwise. 

    returns:
        a generator containing the documents
    """
    # Get list of files in data directory
    files = [f for f in os.listdir(data) if os.path.isfile(os.path.join(data, f))]
    
    # Make token names for training data 
    if train:
        names = [os.path.splitext(f)[0] for f in files]
    
    # Tokenize documents & add tags if training data
    for i, f in enumerate(files):
        with smart_open.open(f'{data}/{f}', encoding='iso-8859-1') as myfile:
            line = myfile.read().replace("\n", " ")
            tokens = gensim.utils.simple_preprocess(line)
            if train:
                yield gensim.models.doc2vec.TaggedDocument(tokens, [names[i]])
            else:
                yield tokens


def main(training, test, to_apply, use_trained, vector_size, model_type, out_loc):

    # Prepare and preprocess training, test & apply data
    print('\nPreprocessing data...\n')
    if not use_trained:
        train_docs = list(preprocess_data(training, 'True'))
        test_docs = list(preprocess_data(test))
    
    apply_docs = list(preprocess_data(to_apply))

    # Train the model
    if not use_trained:
        print('\nTraining model...\n')
        model = train_model(train_docs, vector_size, model_type)
        print(f'Saving trained model as {out_loc}/doc2vec_model')
        model.save(f'{out_loc}/doc2vec_model')

    # Assess model performance
    ## Common-sense check with training data 
    if not use_trained:
        print('\nPerforming common-sense check...\n')
        common_sense_check(train_docs, model)
    ## Manual check with test data 
    if not use_trained:
        print('\nWriting test data check file...\n')
        test_check(test_docs, test, train_docs, model, out_loc)
        print(f'Test check file has been written to {out_loc}/doc2vec_test_output.txt\n')

    # Load model 
    if use_trained:
        print('\nLoading saved model...\n')
        model = gensim.models.doc2vec.Doc2Vec.load(use_trained)

    # Apply model
    print('\nApplying model...\n')
    names = get_tags(to_apply)
    apply_vectors = {}
    for name, doc in zip(names, apply_docs):
        vector = model.infer_vector(doc)
        apply_vectors[name] = vector

    # Write out vectors to a file
    print('\nWriting out vectors...\n')
    df = pd.DataFrame.from_dict(apply_vectors, orient='index', 
            columns=[f'vector_dim{i}' for i in range(vector_size)])
    print(df.head())
    df.to_csv(f'{out_loc}/apply_vectors.csv')
    print(f'Vector file has been written to {out_loc}/apply_vectors.csv\n')

    print('\nDone!\n')


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Run Doc2Vec on abstracts')

    parser.add_argument('-training', type=str, help='Path to a directory with training documents. '
            'Required if -use_trained is False (default)', default=None)
    parser.add_argument('-test', type=str, help='Path to directory containing test documents. '
            'Required if -use_trained is False (default)', default=None)
    parser.add_argument('-use_trained', type=str, help='Path to a pre-trained gensim model.', 
            default='False')
    parser.add_argument('-to_apply', type=str, help='Path to directory containing documents on '
            'which to apply the model & clustering')
    parser.add_argument('-vector_size', type=int, help='Number of dimensions for doc2vec vectors.',
            default=50)
    parser.add_argument('-model_type', type=str, help='Which implementation of gensim Paragraph '
            'Vector to use. Options are DM and DBOW', default='DM') 
    parser.add_argument('-out_loc', type=str, help='Path to save output')

    args = parser.parse_args()

    if args.training and args.test is not None:
        args.training = os.path.abspath(args.training)
        args.test = os.path.abspath(args.test)
    if args.use_trained != 'False':
        args.use_trained = os.path.abspath(args.use_trained)
    else: args.use_trained = False
    args.to_apply = os.path.abspath(args.to_apply)
    args.out_loc = os.path.abspath(args.out_loc)
    
    main(args.training, args.test, args.to_apply, args.use_trained, args.vector_size, 
            args.model_type, args.out_loc)



