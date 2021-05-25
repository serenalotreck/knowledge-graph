"""
Script that uses the other scripts in this directory as modules to 
start-to-finish generate docvecs, cluster, and select documents.

Most args have reasonable defaults and do not need to be changed, but have
been included in case the user wants to make changes.

Author: Serena G. Lotreck
"""
from os.path import abspath 
import argparse 

import doc2vec 
import cluster_docs
import dump_abstracts


def main(data, num_abstracts, out_loc, new_dir_name, use_trained, vector_size, 
        model_type):

    # Get docvecs
    vec_path = doc2vec.main(data, use_trained, vector_size, model_type, 
            out_loc)
    vec_path = abspath(vec_path)

    # Cluster docs
    cluster_path = cluster_docs.main(vec_path, num_abstracts, out_loc)
    cluster_path = abspath(cluster_path)

    # Dump abstracts
    dump_abstracts.main(cluster_path, data, out_loc, new_dir_name)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get docs for corpus')

    # Required input 
    parser.add_argument('-data', type=str, 
            help='Path to directory with docs to cluster')
    parser.add_argument('-num_abstracts', type=int,
            help='Number of abstracts to select from original set')
    parser.add_argument('-out_loc', type=str,
            help='Path to directory where output should be saved. this will '
            'also be where the new directory for the chosen abstracts will be '
            'made.')
    parser.add_argument('-new_dir_name', type=str,
            help='Name for the new directory in which abstracts will be '
            'placed.')

    # Default args
    ## doc2vec.py
    parser.add_argument('-use_trained', type=str, 
            help='Path to a pre-trained gensim model to use rather than '
            'training a new model.', default='False')
    parser.add_argument('-vector_size', type=int, 
            help='Number of dimensions for doc2vec vectors. Default is 50.',
            default=50)
    parser.add_argument('-model_type', type=str, 
            help='Which implementation of gensim Paragraph '
            'Vector to use. Options are DM and DBOW, default is DM', 
            default='DM')
    
    args = parser.parse_args()

    args.data = abspath(args.data)
    args.out_loc = abspath(args.out_loc)
    if args.use_trained != 'False':
        args.use_trained = os.path.abspath(args.use_trained)
    else: args.use_trained = False

    main(args.data, args.num_abstracts, args.out_loc, args.new_dir_name, 
            args.use_trained, args.vector_size, args.model_type)
