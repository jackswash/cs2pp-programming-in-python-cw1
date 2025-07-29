from collections import defaultdict

def file_to_edge_list(file_name='./data/dolphins.tsv'):
    """Method for converting a TSV representation into a tuple edge list.

    Parameters:
    file_name (str): Directory path to the TSV file.

    Returns:
    edge_list: A list of tuples (node1, node2) where they represent edges
    between nodes.
    """
    
    edge_list = []

    # Context manager opener from BB.
    with open(file_name, 'r') as file:
        for line in file:
            nodes = line.strip().split('\t')

            # Append edge list with node 1 and node 2 and store as tuple.
            edge_list.append((int(nodes[0]), int(nodes[1])))
    return edge_list

def edge_to_neighbour_list_1(edge_list):
    """Method for converting an edge list representation into an adjacency (
    neighbour) list

    Parameters:
    edge_list: A list of tuples (node1, node2) where they represent edges
    between themselves.

    Returns:
    neighbour_list (defaultdict): A dictionary representation of an edge list,
    where each key is a node.
    """

    # Dictionary to store neighbour_list using defaultdict.
    neighbour_list = defaultdict(set)

    # For each edge, pair them as neighbours.
    for node1, node2 in edge_list:
        # Node 2 becomes neighbours with Node 1.
        neighbour_list[node1].add(node2)
        # Node 1 becomes neighbours with Node 2.
        neighbour_list[node2].add(node1)
    return neighbour_list

def edge_to_neighbour_list_2(edge_list):
    """Method for converting an edge list representation into an adjacency (
    neighbour) list. A demonstratably less efficient method.

    Parameters:
    edge_list: A list of tuples (node1, node2) where they represent edges
    between themselves.

    Returns:
    neighbour_list (setdefault): A dictionary representation of an edge list,
    where each key is a node.
    """

    # Dictionary to store neighbour_list.
    neighbour_list = {}

    # For each edge, connect them.
    for node1, node2 in edge_list:
        # Add node 1 to set if it doesn't exist in the dictionary, then
        # pair it with node 2 as neighbours.
        neighbour_list.setdefault(node1, set()).add(node2)
        # Add node 2 to set if it doesn't exist in the dictionary, then
        # pair it with node 1 as neighbours.
        neighbour_list.setdefault(node2, set()).add(node1)
    return neighbour_list

def inspect_node(network, node):
    """Method for computing and calculating information about a node.

    Parameters:
    network (list/dict): A list or dictionary representation of a network.

    Returns:
    list: If edge list, returns a list of tuples (node1, node2) where they
    represent edges. If dict, returns a sorted list of node neighbours.
    """
    
    # If edge list.
    if isinstance(network, list):
        edges = []
        visited = set()

        # Iterate through edges in network.
        for edge in network:
            if node in edge:
                # Sorts edges in order.
                sorted_edge = tuple(sorted(edge))
                # Check to prevent duplicates.
                if sorted_edge not in visited:
                    visited.add(sorted_edge)
                    edges.append(edge)
        return edges

    # If dictionary.
    elif isinstance(network, dict):
        # Get neighbours as a set or create empty set if it doesn't exist.
        neighbours = network.get(node, set())
        # Return in sorted form.
        return sorted(neighbours)

def get_degree_statistics(neighbour_list):
    """Method for calculating statistics about the degree of each node in a
    network.

    Parameters:
    neighbour_list (list/dict): A dictionary representation of an edge list,
    where each key is a node.

    Returns:
    tuple: A 4-element tuple which calculates the minimum degree in a network
    (min_degree: int), the maximum degree in a network (max_degree: int), the
    average degree in a network (avg_degree: float), and the most common
    degree in a network (most_common_degree: int).
    """
    
    degrees = [len(neighbours) for neighbours in neighbour_list.values()]
    min_degree = min(degrees)
    max_degree = max(degrees)
    avg_degree = (lambda x: sum(x) / len(x))(degrees)

    # Dictionary for counting how often a degree appears.
    degree_counts = {}
    for degree in degrees:
        degree_counts[degree] = degree_counts.get(degree, 0) + 1

    # Calculate the most frequent degree.
    most_common_degree = max(degree_counts, key=degree_counts.get)

    # Return stats of degree.
    return min_degree, max_degree, avg_degree, most_common_degree

def get_clustering_coefficient(network, node):
    """Method for calculating the clustering coefficient of a node in a
    network.

    Parameters:
    network (list/dict): A list or dictionary representation of a network.
    node: The specific node to calculate the clustering coefficient for.

    Returns:
    float: The clustering coefficient. Returns 0 if the specified node has
    less than 2 neighbours.
    """

    # Load node neighbours.
    neighbours = inspect_node(network, node)

    num_neighbours = len(neighbours)
    # If less than 2 neighbours, cannot have a clustering coefficient.
    if num_neighbours < 2:
        return 0

    max_possible_edges = num_neighbours * (num_neighbours - 1) // 2

    # Count edges between neighbours.
    edges = 0
    for i in range(num_neighbours):
        # Get connections of current neighbour.
        connections = inspect_node(network, neighbours[i])

        for j in range(i + 1, num_neighbours):
            # Increment edges if an edge between two neighbours exists.
            if neighbours[j] in connections:
                edges += 1

    # Return clustering coefficient.
    return edges / max_possible_edges