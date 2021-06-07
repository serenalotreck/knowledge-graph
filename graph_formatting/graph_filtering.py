"""
Script with various options for filtering down a large KG.

A new DOT file (.gv) is saved, with comments at the top
specifying what filters have been applied. 

The same base filename is used, with '_filtered' appended.

Author: Serena G. Lotreck
"""
import argparse 
from os.path import abspath
from os.path import basename
from os.path import splitext

import pygraphviz as pgv
from random import sample


def keyword_direct_filter(graph, keywords):
    """
    Filter graph by a set of keywords, keeping only triples and 
    entities that include the keywords. 

    parameters:
        graph, pgv AGraph instance: the complete graph to filter 
        keywords, list of str: list of keywords to filter by 

    returns:
        graph_copy, pgv AGraph instance: the filtered graph
    """
    graph_copy = graph.copy()

    for node in graph_copy.nodes():
        
        # Check if the node is one of the keywords
        if node not in keywords:

            # Check if it connects to a keyword directly
            connected = False
            done = False
            while not done: # Until we find a connection to a keyword, 
                            # or go through all keywords
                for keyword in keywords:
                    
                    # Check if it's connected to this keyword
                    if graph_copy.has_neighbor(node, keyword):

                        connected = True
                        done = True
                done = True

            if not connected:
                graph_copy.delete_node(node)

    return graph_copy


def keyword_cluster_filter(graph, keywords):
    """
    Filter graph by a set of keywords, keeping only triples and
    entities that eventually connect back to one of the keywords.

    parameters:
        graph, pgv AGraph instance: the complete graph to filter 
        keywords, list of str: list of keywords to filter by 

    returns:
        graph_copy, pgv AGraph instance: the filtered graph
    """
    graph_copy = graph.copy()
    for node in graph_copy.nodes():

        # Account for the fact that we might have deleted this with another cluster
        if node in graph_copy.nodes():
            
            # Check if node is one of the keywords
            if node not in keywords:

                # Check if any keywords are connected to the node
                if graph_copy.neighbors(node) != []:
                    
                    connected = False
                    done = False
                    
                    while not done: # Until we find a connection to a keyword, 
                                    # or go through all keywords 
                        for keyword in keywords:
                            
                            # Check if it's connected to this keyword
                            if (keyword in graph_copy.predecessors(node)) or  \
                                    (keyword in graph_copy.successors(node)):
                                
                                connected = True
                                done = True
                        
                        done = True
                    
                    if not connected:
                        
                        all_connections = graph_copy.predecessors(node) + \
                                            graph_copy.successors(node)
                        graph_copy.delete_nodes_from(all_connections)
                
                else: 
                    
                    graph_copy.delete_node(node)

        return graph_copy 


def random_num_filter(graph, num):
    """
    Filter graph by randomly selecting a given number of triples and entities.
    Selects the given number of entities randomly, and then randomly selects 
    one connection if multiple connections are present. If one selected node 
    is connected to another selected nodes, the second one will be dropped and 
    a new one chosen.

    parameters:
        graph, pgv AGraph instance: the complete graph to filter 
        num, int: the number of selections to make

    returns:
        new_graph, pgv AGraph instance: the filtered graph
    """
    # Get random nodes and leftovers 
    all_nodes = graph.nodes()
    random_nodes = sample(all_nodes, num)
    not_selected_nodes = [node for node in all_nodes if node not in random_nodes]
    
    # Make new graph to add the chosen nodes and triples 
    new_graph = pgv.AGraph()

    # Add nodes to new graph 
    for node in random_nodes:

        neighbors = graph.neighbors(node)
        # If the node has neighbors, choose random triple
        if neighbors != []:
            
            # Choose random neighbor & get its edge label 
            random_neighbor = sample(neighbors, 1)[0]

            # Check if random choice is in the original list of len(num)
            if random_neighbor in random_nodes:
                # Remove it and replace it with another 
                new_node = sample(not_selected_nodes, 1)[0] # Get new node 
                not_selected_nodes.remove(new_node)      # Remove from those not selected
                random_nodes.remove(node)                # Remove the old node from chosen list
                random_nodes.append(new_node)            # Add new node to chosen list
            
            # Get edge label & add triple to new graph
            if random_neighbor in graph.predecessors(node):
                edge = graph.get_edge(random_neighbor, node)
            else:
                edge = graph.get_edge(node, random_neighbor)
            edge_label = edge.attr["label"]
            new_graph.add_edge(node, random_neighbor, label=edge_label) # Nodes are added if not 
                                                                        # already present
        # If it's just a loose entity, add it 
        else:

            new_graph.add_node(node)

    return new_graph


def read_dot(dot_file, remove_ents):
    """
    Read in triples from a DOT file. If remove_ents is True, leaves 
    loose entities out when reading file. 

    parameters;
        dot_file, str: path to valid DOT file
        remove_ents, bool: if True, remove entities while reading

    returns: 
        graph, pgv AGraph instance: the graph from the DOT file, with 
            loose entities removed if remove_ents == True  
    """
    # Read in the full graph 
    base_graph_name = basename(dot_file)
    base_graph_name = splitext(base_graph_name)[0]
    graph = pgv.AGraph(dot_file, name=base_graph_name, directed=True)

    # Remove loose entities if specified
    if remove_ents:
        for node in graph.nodes():
            if graph.neighbors(node) == []:
                graph.delete_node(node)
    
    return graph


def check_number(graph, num):
    """
    Asserts that the number to select doesn't exceed the size 
    of the graph. Assumes that all chosen nodes will be members of triples, 
    and therefore the maximum number of nodes that can be chosen is 
    the total number of nodes divided by 2.

    parameters:
        graph, pgv AGraph instance: compelte graph 
        num, int: the number of nodes to choose
    
    returns: None
    """
    nodes = graph.nodes()

    assert num <= len(nodes)/2, ('The number you have chosen is greater '
                                f'than the allowed maximum: {num} selected, '
                                f'{len(nodes)/2} is the maximum.')


def check_keywords(graph, keywords):
    """
    Asserts that all keywords are indeed nodes in the graph.
    Raises an AssertionError if they aren't.

    parameters:
        graph, pgv AGraph instance: the complete graph 
        keywords, list of str: keywords to check 
    
    returns: None
    """
    nodes = graph.nodes()
    keywords_present = True
    problem_words = []
    for keyword in keywords:
        if keyword not in nodes:
            keywords_present = False
            problem_words.append(keyword)
    assert keywords_present, ('The following keywords are not nodes in '
                                f'the graph: {problem_words}')

            
def main(dot_file, filter_type, keywords, num, remove_ents, out_loc):

    # Read in dot file 
    print('\nReading in dot file...\n')
    graph = read_dot(dot_file, remove_ents)
    
    # Get name for "full" graph file 
    if remove_ents:
        ent_name = 'no_loose_ents'
    else: ent_name = 'all_ents'

    # Get basename for later 
    print('\nGetting basename...')
    base_graph_name = basename(dot_file)
    base_graph_name = splitext(base_graph_name)[0]
    print(f'Basename is {base_graph_name}\n')

    # Filter 
    print('\nFiltering graph...')
    if filter_type == "all":
       
        # Do a keyword and number warning 
        check_keywords(graph, keywords)
        print(f'Keywords are: {keywords}')
        check_number(graph, num)

        print('Performing keyword direct filter...')
        key_direct_graph = keyword_direct_filter(graph, keywords)
        print('Performing keyword cluster filter...')
        key_cluster_graph = keyword_cluster_filter(graph, keywords)
        print('Performing random number filter...')
        random_num_graph = random_num_filter(graph, num)

        graphs = {f'{ent_name}_{base_graph_name}':graph,
                    f'keyword_direct_{base_graph_name}':key_direct_graph,
                    f'keyword_cluster_{base_graph_name}':key_cluster_graph,
                    f'random_num_{base_graph_name}':random_num_graph}
    else: 

        if filter_type == "keyword_direct":
            
            # Keyword check 
            check_keywords(graph, keywords)
            print(f'Keywords are: {keywords}')
            print('Performing keyword direct filter...')

            key_direct_graph = keyword_direct_filter(graph, keywords)
            
            graphs = {f'{ent_name}_{base_graph_name}':graph,
                        f'keyword_direct_{base_graph_name}':key_direct_graph}
    
        elif filter_type == "keyword_cluster":
            
            # Keyword check
            check_keywords(graph, keywords)
            print(f'Keywords are: {keywords}')

            print('Performing keyword cluster filter...')
            
            key_cluster_graph = keyword_cluster_filter(graph, keywords)

            graphs = {f'{ent_name}_{base_graph_name}':graph,
                        f'keyword_cluster_{base_graph_name}':key_cluster_graph}

        elif filter_type == "random_num":

            # Number check
            check_number(graph, num)
            
            print('Performing random number filter...')

            random_num_graph = randon_num_filter(graph, num)
            
            graphs = {f'full_{base_graph_name}':graph,
                        f'random_num_{base_graph_name}':random_num_graph}
        
    # Save 
    print('\n\nSaving files...')
    print(base_graph_name)
    for graph_name, graph_instance in graphs.items():

        graph_instance.write(f'{out_loc}/{graph_name}.gv')
        
        print(f'File saved as {out_loc}/{graph_name}.gv')

    print('\n\nDone!')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Filter down DOT file')

    parser.add_argument('-dot_file', type=str,
            help='Path to dot file to filter')
    parser.add_argument('-filter_type', type=str,
            help='Options are "keyword_direct", "keyword_cluster", ' 
                '"random_num" and "all". "keyword_direct" gives only triples '
                'that have the keyword as one of the participating entities. '
                '"keyword_cluster" gives all triples connected by any path to '
                'the keyword. "random_num" gives the specified '
                'number of entries, randomly selected from the whole file. '
                '"all" does all options and returns a separate graph for each. '
                'Default is "all".',
            default="all")
    parser.add_argument('-keywords', nargs='+',
            help='Keywords to filter by. Example usage: -keywords JA GA. '
                'Required if -filter_type is "keyword_direct" or '
                '"keyword_cluster".', default=[])
    parser.add_argument('-num', type=int,
            help='Number of entries to select. Required if -filter_type is '
                '"random_num".', default=0)
    parser.add_argument('--remove_ents', action='store_true',
            help='Removes loose entities from the graph if this flag is '
            'specified.')
    parser.add_argument('-out_loc', type=str,
            help='Path to save the filtered dot file')


    args = parser.parse_args()

    args.dot_file = abspath(args.dot_file)
    args.out_loc  = abspath(args.out_loc)

    main(**vars(args))
