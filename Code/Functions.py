import numpy as np
import graph_tool.all as gt
from datetime import datetime
import pandas as pd
import networkx as nx
import random
import math

# GETTING A FRACTION OF THE GRAPH
def fraction_graph(g: gt.Graph, percentage:float, seed=437):
 
    random.seed(seed)
    # Get the total number of vertices and edges
    edge_list = list(g.iter_edges())
    vertex_list = list(g.iter_vertices())

    # Calculate the number of vertices and edges for the subgraph
    num_subgraph_vertices = int(len(vertex_list) * (percentage / 100))
    num_subgraph_edges = int(len(edge_list) * (percentage / 100))

    # Get random indices for vertices and edges
    selected_vertices = random.sample(vertex_list, num_subgraph_vertices)
    selected_edges = random.sample(edge_list, num_subgraph_edges)

    # Filter edges connected to nodes labeled type
    filtered_edges = g.new_edge_property("bool")
    filtered_edges.a = False

    # Filter nodes with label type
    filtered_nodes = g.new_vertex_property("bool")
    filtered_nodes.a = False
            
    for v in g.iter_vertices():
        if v in selected_vertices:
            vertex = g.vertex(v)
            filtered_nodes[vertex] = True
            for e in vertex.out_edges():
                edge_tuple = [int(e.source()), int(e.target())]
                if edge_tuple in selected_edges:
                    filtered_edges[e] = True

    subgraph = gt.GraphView(g,vfilt=filtered_nodes, efilt=filtered_edges)
    
    return subgraph

def get_adjacency(g : gt.Graph, weight = None) -> np.ndarray:
    # Get EdgePropertyMap for Weights in Adjacency
    if weight is not None:
        weights = g.ep[weight]
    else: weights = weight

    adj = gt.adjacency(g, weight = weights).T
    return adj.toarray()

def get_types_array(g: gt.Graph, types:str) -> np.ndarray:
    t = g.vp[types].get_2d_array([0])[0]
    return t

def get_types_dict(g: gt.Graph, types:str) -> dict:
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
    T = get_types_dict(g, types)
    Type_to_row = {k:v for v,k in enumerate(T.keys())}
    return Type_to_row

def get_types_matrix(g:gt.Graph , types:str) -> np.ndarray:
    types_dict = get_types_dict(g,types = types)
    types_vector = types_dict.values()
    return np.array(list(types_vector)).T

def get_contact_layer(g, types:str , weights = None) -> np.ndarray:
    adj = get_adjacency(g, weights)
    types_matrix = get_types_matrix(g, types)
    M = types_matrix.T.dot(adj).dot(types_matrix)

    if g.is_directed():
        return M
    else: 
        M_undir = np.copy(M)
        M_undir[np.tril_indices(M.shape[0], k=-1)] = 0
        np.fill_diagonal(M_undir, M_undir.diagonal() / 2)
        return M_undir

def get_non_contact_layer(g, types = None) -> np.ndarray:
    adj_1 = get_adjacency(g)
    adj = 1 - adj_1
    
    types_matrix = get_types_matrix(g, types = types)
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
      
def me_vs_others(M: np.array, group_index: int) -> np.array:
    M_11 = M[group_index, group_index]
    M_12 = np.sum(M[group_index,:]) - M_11
    M_21 = np.sum(M[:, group_index]) - M_11
    not_me_contact = np.delete(np.delete(M, group_index, axis=0), group_index, axis=1)
    M_22 = np.sum(not_me_contact)
    
    me_vs_others = np.array([[M_11, M_12],[M_21,M_22]])
    
    return me_vs_others

def diametros(g: gt.Graph, w = None):
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

# FILTERING A GRAPH BASED ON VERTEX PROPERTY
def filter_graph(g:gt.Graph, label:str, type:str) -> gt.Graph:
    # Filter edges connected to nodes labeled type
    filtered_edges = g.new_edge_property("bool")
    filtered_edges.a = False

    # Filter nodes with label type
    filtered_nodes = g.new_vertex_property("bool")
    filtered_nodes.a = False

    for v in g.vertices():
        if g.vertex_properties[label][v] == type:
            filtered_nodes[v] = True
            for edge in v.out_edges():
                if g.vertex_properties[label][edge.target()] == type:
                    filtered_edges[edge] = True

    # Generate the subgraph using the filtered nodes and edges
    subgraph = gt.GraphView(g, vfilt=filtered_nodes, efilt=filtered_edges)
    return subgraph

def to_networkx(g: gt.Graph) -> nx.Graph:
    
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
    
    return nx_graph

def look_up_graph(g: gt.Graph, idx:int):
    array = list(g.vp['name'].a)
    in_graph = array.index(idx)
    return in_graph