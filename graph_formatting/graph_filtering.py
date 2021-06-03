"""
Script with various options for filtering down a large KG.

A new DOT file (.gv) is saved, with comments at the top
specifying what filters have been applied. 

The same base filename is used, with '_filtered' appended.

Author: Serena G. Lotreck
"""
import argparse 
from os.path import abspath

def keyword_filter(graph, filter_type, kewyord):
    """
    Filter graph by a set of keywords 
    """

def num_filter(graph, filter_type, num)
def read_dot(dot_file, remove_ents):
    """
    Read in triples from a DOT file. If remove_ents is True, leaves 
    loose entities out when reading file. 

    parameters;
        dot_file, str: path to valid DOT file
        remove_ents, bool: if True, remove entities while reading

    returns: 
        graph, list: triples are 4-tuples (head, rel, tail, weight) and 
            loose entities, if included, are strings 
    """
    graph = []
    
    with open(dot_file) as f:
        
        lines = f.readlines()
        
        for line in lines:
            if '->' in line: # If it's a triple
                start_arrow = line.find('->') # Would fail if a head ent had this in it
                head = line[:start_arrow-1].replace('"','') # Remove double quotes to avoid 
                                                            # propogating them
                start_attrs = line.find('[label=') 
                tail = line[start_arrow+2:start_attrs-1]
                
                end_label = line.find(',', start_attrs)
                rel = line[start_attrs+len('[label="'):end_label-1]

                end_weight = line.find(']', end_label) # Would fail if a relation name included ]
                weight = line[end_label+1+len(' weight='):end_weight]

                triple = (head, rel, tail, weight)
                graph.append(triple)

            else:
                if not remove_ents:
                    ent = line.replace('"', '')
                    graph.append(ent)


    return graph

            
def main(dot_file, filter_type, keyword, num, remove_ents, out_loc):

    # Read in dot file 
    graph = read_dot(dot_file, remove_ents)

    # Filter 
    if filter_type == "keyword_direct" or "keyword_cluster":
        filtered_graph = keyword_filter(graph, filter_type, kewyord)

    else: filtered_graph = num_filter(graph, filter_type, num)
   
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Filter down DOT file')

    parser.add_argument('-dot_file', type=str,
            help='Path to dot fiel to filter')
    parser.add_argument('-filter_type', type=str,
            help='Options are "keyword_direct", "keyword_cluster", "top_num", ' 
                '"random_num". "keyword_direct" gives only triples that have '
                'the keyword as one of the participating entities. '
                '"keyword_cluster" gives all triples connected by any path to '
                'the keyword. "top_num" gives the first specified number of '
                'entries in the graph, while "random_num" gives the specified '
                'number of entries, randomly selected from the whole file.')
    parser.add_argument('-keywords', nargs='+',
            help='Keywords to filter by. Example usage: -keywords JA GA. '
                'Required if -filter_type is "keyword_direct" or '
                '"keyword_cluster".', default=[])
    parser.add_argument('-num', type=int,
            help='Number of entries to select. Required if -filter_type is '
                '"top_num" or "random_num".', default=0)
    parser.add_argument('-remove_ents', action='store_true',
            help='True/False, Removes loose entities from the graph. Default '
            'is True.')
    parser.add_argument('-out_loc', type=str,
            help='Path to save the filtered dot file')


    args = parser.parse_args()

    args.dot_file = abspath(args.dot_file)
    args.out_loc  = abspath(args.out_loc)

    main(**vars(args))
