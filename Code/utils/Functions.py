import numpy as np
import graph_tool.all as gt
from datetime import datetime
import pandas as pd
import networkx as nx
import random
import math

def get_adjacency(g : gt.Graph, weight = None) -> np.ndarray:
    """
    Gets the Adjacency Matrix of the graph as an array. rows are Source nodes and columns are Target Nodes

    Args:
        g (Graph): The Graph object to analize.
        weight (String): The name of the PropertyMap where eights of the edges resides.

    Returns:
        ndarray: Adjcancecy Matrix

    """
    # Get EdgePropertyMap for Weights in Adjacency
    if weight is not None:
        weights = g.ep[weight]
    else: weights = weight

    adj = gt.adjacency(g, weight = weights).T
    return adj.toarray()

def get_types_array(g: gt.Graph, property_label:str) -> np.ndarray:
    """
    Gets the array of nodes with the the value of the property label of the nodes in each entry

    Args:
        g (Graph): The Graph object to analize.
        property_label (String): The name of the PropertyMap where tipification of the groups resides.

    Returns:
        ndarray: Array for the nodes where each element of the array corresponds to its type

    """
    property_map = g.vp[property_label]
    if "vector" in property_map.value_type() or 'string' in property_map.value_type():
        t = property_map.get_2d_array([0])[0]
    else:
        t = property_map.a
    return t

def get_types_dict(g: gt.Graph, types:str) -> dict:
    """
    gets the Dictionary where the keys are groups and the values are arrays.
        Each array has a 1 if that node corresponds to that group and 0 if not

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where tipification of the groups resides.

    Returns:
        ndarray: Dictionary where the keys are groups and the values are arrays.
        Each array has a 1 if that node corresponds to that group and 0 if not

    """
    # Get array of types
    t = get_types_array(g,types)
    T = {}
    for tipo in np.unique(t):
        row=[]
        for i in t:
            if i == tipo:
                row.append(1)
            else:
                row.append(0)        
        T[str(tipo)] = row
    return T

def get_types_index(g: gt.Graph, types:str) -> dict:
    """
    gets the Dictionary where the keys are groups and the values are the indexes in the contact and
    non contact layer. Also have the indexes for the types matrix.

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where tipification of the groups resides.

    Returns:
        dict: Dictionary where the keys are groups and the values are the indexes in the contact and
        non contact layer. Also have the indexes for the types matrix.

    """
    T = get_types_dict(g, types)
    Type_to_row = {k:v for v,k in enumerate(T.keys())}
    return Type_to_row

def get_types_matrix(g:gt.Graph , types:str) -> np.ndarray:
    """
    Calculate a matrix of shape (N,G) where each column is a types vector from the types dict.

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where tipification of the groups resides.

    Returns:
        ndarray: Matrix of shape (N,G) where each column is a types vector from the types dict.

    """
    types_dict = get_types_dict(g,types = types)
    types_vector = list(types_dict.values())
    if g.vp[types].value_type() == 'bool':
        types_vector = types_vector[::-1]
    return np.array(types_vector).T

def get_contact_layer(g, property_label:str , weights = None) -> np.ndarray:
    """
    Receives a graph and creates a contact layer

    Args:
        g (Graph): The Graph object to analize.
        property_label (String): The name of the PropertyMap where tipification of the groups resides.
        weight (String): The name of the PropertyMap where weights of the edges resides.

    Returns:
        ndarray: Matrix of shape (G,G) where each entry cof the matrix calculates the number of ties between or witthin groups.
        See Bojanowski for more info. If weights provided, it calculates the summ of the weights between or within groups.

    """
    adj = get_adjacency(g, weights)
    types_matrix = get_types_matrix(g, property_label)
    M = types_matrix.T.dot(adj).dot(types_matrix)

    if g.is_directed():
        return M
    else: 
        M_undir = np.copy(M)
        M_undir[np.tril_indices(M.shape[0], k=-1)] = 0
        np.fill_diagonal(M_undir, M_undir.diagonal() / 2)
        return M_undir

def get_non_contact_layer(g, property_label = None) -> np.ndarray:
    """
    Receives a graph and creates a non contact layer

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where tipification of the groups resides.

    Returns:
        ndarray: Matrix of shape (G,G) where each entry of the matrix calculates the number of NON ties between or within groups.
        See Bojanowski for more info.

    """
    adj_1 = get_adjacency(g)
    adj = 1 - adj_1
    
    types_matrix = get_types_matrix(g, property_label = property_label)
    M = types_matrix.T.dot(adj).dot(types_matrix)
    M_1 = types_matrix.T.dot(adj_1).dot(types_matrix)
    contact_diag = np.diag(M_1)
    
    total_dyads = []
    for g in range(types_matrix.shape[1]):
        G_g = np.sum(types_matrix[:, g])
        if G_g < 2:
            M_gg = 0
        else:
            M_gg = math.perm(G_g,2)
        total_dyads.append(M_gg)
    non_contact_diag = np.array(total_dyads) - contact_diag
    np.fill_diagonal(M, non_contact_diag)
        
    return M
      
def me_vs_others(g: gt.Graph, group_index: int, property_label:str, weights = None) -> np.ndarray:
    """
    Calculates the Me Vs Others Matrix. This is a 2 by 2 Matrix based on the Contact Layer of a Graph.
    Takes in account one posible label of the groups partition of nodes, lets call it g
    this is a Contact Layer that aggregates all the other groups besides g as one whole group.
    Then returns the Contact Layer of the graph as if it only were two groups. g and the Others.

    Args:
        g (Graph): The Graph object to analize.
        group_index (int): index of the group to create the matrix
        property_label (str): The name of the PropertyMap where tipification of the groups resides.
        weights (str): The name of the PropertyMap where weights of the edges resides.

    Returns:
        ndarray: Matrix of shape (2,2) that summarizes a contact layer from G groups into two groups. It takes one,
        specific group in particular and aggregates all the other groups as one. Calculates the contact layer for this case.

    """
    M = get_contact_layer(g, property_label, weights=weights)
    
    if M.shape[0] == M.shape[1] == 2:
        return M
    
    M_11 = M[group_index, group_index]
    M_12 = np.sum(M[group_index,:]) - M_11
    M_21 = np.sum(M[:, group_index]) - M_11
    not_me_contact = np.delete(np.delete(M, group_index, axis=0), group_index, axis=1)
    M_22 = np.sum(not_me_contact)
    me_vs_others = np.array([[M_11, M_12],[M_21,M_22]])
    
    if g.is_directed():
        return me_vs_others
    else:
        me_vs_others[0, 1] += me_vs_others[1, 0]
        me_vs_others[1, 0] = 0
        return me_vs_others

def diametros(g: gt.Graph, w = None) -> pd.DataFrame:
    if w==None:
        weights = None
        name = 'Diametro Simple'
    else:
        weights =g.ep[w]
        name = f'Diametro de {w}'
    diametros= []
    for v in g.vertices():
        d = gt.pseudo_diameter(g, source = v, weights = weights)
        diametros.append(d)

    diametros = pd.DataFrame(diametros, columns = [name, 'Edge'])
    return diametros.drop(columns='Edge')

def descriptive(g: gt.Graph, w=None) -> pd.DataFrame:
    # Date
    date = g.ep['Ending date'][g.edges().next()]
    date = datetime.strptime(date, '%Y-%m-%d')
    
    # Edges, Nodes and Dyads
    nodes = g.num_vertices()
    edges = g.num_edges()
    dyads = edges/2
    density = (edges) / (nodes * nodes -1)
    
    # Connected Components 
    SCC, hist = gt.label_components(g, directed=True)
    WCC, hist = gt.label_components(g, directed=False)
    
    N_SCC = len(set(SCC.a))
    N_WCC = len(set(WCC.a))
    
    # Diameter simple
    diametros_df = diametros(g)
    diametro_simple = float(diametros_df.max(axis=0).iloc[0])
        
    results = {
        'Graph Date': date,
        'Nodes': nodes,
        'Edges': edges,
        'Dyads': dyads,
        'Density': density,
        'Strongly Connected Components': N_SCC,
        'Weakly Connected Components': N_WCC,
        'Diametro Simple': diametro_simple
    }
    
    # Diametro con pesos
    if w is not None:
        diametros_w = diametros(g,w)
        diametro = float(diametros_w.max(axis=0).iloc[0])
        tipo_de_diametro = diametro.max(axis=0).index[0]
        
        results[tipo_de_diametro] = diametro
    
    df = pd.DataFrame([results]).set_index('Graph Date')
        
    return df

def to_networkx(g: gt.Graph) -> nx.Graph:
    """
    Based on an instance of a Graph class from graph-tool library. creates a new graph using the NetworkX framework
    preserving all nodes, edges and graph attributes.

    Args:
        g (graph-tool Graph): The Graph object to transform

    Returns:
        G (NetworkX Graph)
    """
    if g.is_directed():
        nx_graph = nx.DiGraph()
    else:
        nx_graph = nx.Graph()

    # Add nodes with their properties to the NetworkX graph
    for v in g.vertices():
        node_properties = {prop_name: g.vp[prop_name][v] for prop_name in g.vp}
        nx_graph.add_node(int(v), **node_properties)

    # Add edges with their properties to the NetworkX graph
    for e in g.edges():
        edge_properties = {prop_name: g.ep[prop_name][e] for prop_name in g.ep}
        nx_graph.add_edge(int(e.source()), int(e.target()), **edge_properties)
    
    for key, value in dict(g.gp).items():
        nx_graph.graph[key] = value
    
    return nx_graph

def infer_property_type(value):
    """
    Infers the graph-tool property type based on the value's Python type.
    Adjust or extend the type mappings as needed.
    """
    if isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "double"
    elif isinstance(value, str):
        return "string"
    else:
        # Default to string for types not explicitly handled
        return "string"

def to_graphtool(G):
    """
    Based on an instance of a Graph class from NetwrokX library. creates a new graph using the graph-tool framework
    preserving all nodes, edges and graph attributes.

    Args:
        g (NetworkX Graph): The Graph object to transform

    Returns:
        G (graph-tool Graph)
    """
    g = gt.Graph(directed=G.is_directed())

    # Add all vertices
    gt_vertices = {}
    for nx_node in G.nodes():
        v = g.add_vertex()
        gt_vertices[nx_node] = v

    # Add all edges
    for edge in G.edges():
        g.add_edge(gt_vertices[edge[0]], gt_vertices[edge[1]])
    
    if len(list(G.nodes(data=True))[0]) > 1:
        for vp, val in list(G.nodes(data=True))[0][1].items():
            vprop = g.new_vertex_property(infer_property_type(val))
            for n in G.nodes(data=True):
                vprop[n[0]] = n[1][vp]
            g.vp[vp] = vprop
    
    if len(list(G.edges(data=True))[0]) > 2:
        for ep, val in list(G.edges(data=True))[0][2].items():
            eprop = g.new_edge_property(infer_property_type(val))
            for e in list(G.edges(data=True)):
                eprop[(e[0],e[1])] = e[2][ep]
            g.ep[ep] = eprop
    
    if len(G.graph) > 0:
        for key, val in G.graph.items():
            gprop = g.new_gp(infer_property_type(val))
            gprop[g] = val
            g.gp[key] = gprop
    
    return g

def fraction_graph(G: gt.Graph, percentage:float, seed=437):
    """
    This Functions selects a random fraction of the graph, filter thegraph and return this fraction.
    Randomly get a fraction of total amount of nodes.
    The amount of nodes to be selected is given by the percentage parameter

    Args:
        g (Graph): The Graph object to analize.
        weight (String): The name of the PropertyMap where eights of the edges resides.

    Returns:
        ndarray: Adjcancecy Matrix

    """
    if percentage == 100:
        return G
    elif percentage > 100:
        return None
    else:
        random.seed(seed)
        # Get the total number of vertices and edges
        vertex_list = list(G.iter_vertices())

        # Calculate the number of vertices and edges for the subgraph
        num_subgraph_vertices = int(len(vertex_list) * (percentage / 100))

        # Get random indices for vertices and edges
        selected_vertices = random.sample(vertex_list, num_subgraph_vertices)

        # Filter nodes with label type
        filtered_nodes = G.new_vertex_property("bool")
        filtered_nodes.a = False
                
        for v in G.iter_vertices():
            if v in selected_vertices:
                vertex = G.vertex(v)
                filtered_nodes[vertex] = True

        subgraph = gt.GraphView(G,vfilt=filtered_nodes)
    
    return subgraph