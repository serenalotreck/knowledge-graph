"""
Reads in document vectors produced by doc2vec.py, clusters them according to 
the user-chosen algorithm, and returns the file names of the number of abstracts
defined by the user. Abstracts are chosen by iterating over the resulting clusters
until the desired number is reached, taking one abstract from each cluster each time
until the cluster is exhausted.

Author: Serena G. Lotreck
"""
import os 
import argparse

import random
import numpy as np
import pandas as pd
from sklearn.cluster import MeanShift
from sklearn.mixture import GaussianMixture
from sklearn.cluster import DBSCAN


def choose_abstracts(cluster_lists, number_abstracts):
    """
    Choose abstracts from clusters. Iterates over clusters,
    randomly selecting one abstract from each cluster each time, 
    until the desired number of abstracts is reached, skipping
    clusters that have been exhausted.

    parameters:
        cluster_lists, dict of list: keys are cluster labels, values are lists of 
            PMID corresponding to that cluster
        number_abstracts, int: number of abstracts to select
    
    returns:
        abstract_names, list of str: base file names (PMIDs) of the selected abstracts
    """
    # Define housekeeping variables
    i = 0 # Number of abstracts that have been chosen
    abstract_names = []

    # Choose abstracts until the desired number is reached
    while i < number_abstracts:
        for cluster_name, cluster_contents in cluster_lists.items():
            if len(cluster_contents) > 0:
                # Randomly choose an element
                rand_elt = random.choice(cluster_contents)

                # Pop off the value and add to abstract_names list
                cluster_contents.pop(cluster_contents.index(rand_elt))
                abstract_names.append(rand_elt)

                # Up the counter
                i += 1
    
    print(f'{number_abstracts} have been selected!')
    return abstract_names
    

def make_cluster_lists(clusters):
    """
    Make a dictionary containing a list of PMID corresponding to each cluster.

    parameters:
        clusters, df: columns are 'doc_name' and 'cluster'

    returns:
        cluster_lists, dict of list: keys are cluster labels, values are lists of 
            PMID corresponding to that cluster
    """
    cluster_ids = np.unique(clusters.cluster)
    cluster_lists = {}
    for cluster_id in cluster_ids:
        id_df = clusters[clusters['cluster']==cluster_id]
        cluster_list = id_df['doc_name'].tolist()
        cluster_lists[cluster_id] = cluster_list

    return cluster_lists


def cluster_docvecs(vecs, algorithm):
    """
    Cluster document vectors according to the algorithm of choice. 
    
    Notes:
        - sklearn mean-shift is implemented with the estimate_bandwith
            option for estimating the neighborhood distance measure epsilon.
            estimate_bandwidth scales poorly compared to MeanShift, so this
            may need to be reassessed if runtime on larger datasets is slow.
        - EM-GMM can assign mixed membership, however, we only want each doc
            to be in one cluster. EM-GMM is being used instead of k-means 
            because the cluster shape is more flexible, but docs will be
            assigned only to the cluster to which they have the greatest 
            membership.
        
    parameters:
        vecs, df: dataframe with row indices as doc names, 
            and each column a dimension of the document vector
        algorithm, str: algorithm to use. Choices are MS (mean-shift),
            EMGMM (expectation-maximization with gaussian mixture models),
            or DBSCAN.

    returns: 
        
    """
    # Drop labels for training data
    vec_names = vecs.index.tolist()
    X = vecs.to_numpy()
    
    # MeanShift implementation
    if algorithm == 'MS':
        ms = MeanShift()
        cluster_labels = ms.fit_predict(X)

    # EM-GMM implementation
    if algorithm == 'EMGMM':
        pass

    # DBSCAN implementation
    if algorithm == 'DBSCAN':
        pass

    # Format and return clusters
    cluster_df = pd.DataFrame({'doc_name':vec_names, 'cluster':cluster_labels})

    return cluster_df


def main(vector_path, algorithm, number_abstracts, out_loc):
    
    # Read in vectors 
    print('\nReading in the document vectors...')
    vecs = pd.read_csv(vector_path, index_col=0)
    assert (vecs.shape[0] >= number_abstracts), ( 
            f'You\'ve asked for {number_abstracts} abstracts, but '
            'there are only {vecs.shape[0]} to choose from, please try again with a lower number.')
    
    # Cluster
    print('\nClustering document vectors...')
    clusters = cluster_docvecs(vecs, algorithm) 
    
    # Make a list of PMID for each cluster
    cluster_lists = make_cluster_lists(clusters)

    # Choose abstracts
    print('\nChoosing abstracts from clusters...')
    abstract_names = choose_abstracts(cluster_lists, number_abstracts)    
    abstract_names_df = pd.DataFrame(abstract_names, columns=['abstract_name'])
    print('Shapshot of chosen abstracts:\n')
    print(abstract_names_df.head())

    # Write out abstract names
    print('\nWriting out file with chosen abstract names...')
    abstract_names_df.to_csv(f'{out_loc}/{number_abstracts}_chosen_abstracts_{algorithm}.txt',
            index=False)

    print('\nDone!\n')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Cluster and choose abstracts')

    parser.add_argument('-vecs', '--vectors', type=str, help='Path to csv with doc vectors.')
    parser.add_argument('-alg', '--algorithm', type=str, 
        help='Clustering algorithm to use. Options are EM-GMM (EMGMM), DBSCAN, or mean-shift (MS). '
            'Default is mean-shift. Use visualize_clusters.py to determine if EM-GMM or '
            'DBSCAN is a better choice.', 
        default='MS')
    parser.add_argument('-num', '--number_abstracts', type=int, 
        help='Number of abstracts to select from clusters. Must be less than the total '
            'number of documents available.')
    parser.add_argument('-out_loc', type=str, help='Directory to save output file.')

    args = parser.parse_args()

    args.vectors = os.path.abspath(args.vectors)
    args.out_loc = os.path.abspath(args.out_loc)

    main(args.vectors, args.algorithm, args.number_abstracts, args.out_loc)
