# Mathematical and Data Managment
import numpy as np
import pandas as pd

# Graph Managment
import graph_tool.all as gt
from utils.Functions import * 

# ========================================================================================
def individual_attention_to_h(G: gt.Graph, v_index:int, property_label:str, group:str, in_attention = True): 
    """
     Individual Attention Index: This index calculates the proximity from and individual to a political group
    Args:
        G (Graph): The Graph object to analize.
        property_name (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        weights (String): The name of the EdgePropertyMap where the weights of the edges resides
        g (String): name of the group g
        in_attention (bool): boolean that specifes if you want the attention from g to h or from h to g
    Returns:
        index (float): The Attention Index 
    """
    individual_weight = 0
    v = G.vertex(v_index)
    for e in v.out_edges():
        if G.vp[property_label][e.target()] == group:
            individual_weight += G.ep['Normal Weight'][e]
    
    return individual_weight

# ========================================================================================
def attention_g_others(G: gt.Graph, property_label:str, weights:str, g:str, in_attention=True):
    """
    Attention Index that group g devotes to all other groups (-g). This index takes in count
    weight and of the edges and directionality
    Args:
        G (Graph): The Graph object to analize.
        property_name (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        weights (String): The name of the EdgePropertyMap where the weights of the edges resides
        g (String): name of the group g
        in_attention (bool): boolean that specifes if you want the attention from g to h or from h to g
    Returns:
        index (float): The Attention Index 
    """
    active_nodes = set()
    sum_weight = 0
    for e in G.edges():
        if G.vp[property_label][e.source()] == g:
            active_nodes.add(int(e.source()))
        if in_attention:
            if G.vp[property_label][e.source()] == g and G.vp[property_label][e.target()] != g:
                sum_weight += G.ep[weights][e]
        else:
            if G.vp[property_label][e.source()] != g and G.vp[property_label][e.target()] == g:
                sum_weight += G.ep[weights][e]
    N_active_nodes = len(active_nodes)

    return sum_weight/N_active_nodes

#=========================================================================================================================
def attention_g_h(G, property_label:str, weights:str, g:str, h:str, in_attention = True):
    """
    Attention Index that group g devotes to group h. This index takes in count
    weight and of the edges and directionality
    Args:
        - G (Graph): The Graph object to analize.
        - property_name (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        - weights (String): The name of the EdgePropertyMap where the weights of the edges resides
        - g (String): name of the group g
        - h (String): name of the group h
        - in_attention (bool): boolean that specifes if you want the attention from g to h or from h to g

    Returns:
        index (float): The Attention Index 
    """
    active_nodes = set()
    sum_weight = 0
    for e in G.edges():
        if G.vp[property_label][e.source()] == g:
            active_nodes.add(int(e.source()))
        if in_attention:
            if G.vp[property_label][e.source()] == g and G.vp[property_label][e.target()] == h:
                sum_weight += G.ep[weights][e]
        else:
            if G.vp[property_label][e.source()] == h and G.vp[property_label][e.target()] == g:
                sum_weight += G.ep[weights][e]
    N_active_nodes = len(active_nodes)
    
    return sum_weight/N_active_nodes

#=========================================================================================================================
def at_random_scenario(G:gt.Graph, property_label:str, group:str, use_case:str):
    tweets_numerador = 0 
    tweets = 0
    for v in G.vertices():
        tweets += (G.vp['Tweets'][v])
        # Condicional para índice de atención a otros. Cuenta Tweets del grupo (-g)
        if use_case == 'Proximity to Others':
            if G.vp[property_label][v] != group:
                tweets_numerador += (G.vp['Tweets'][v])
        # Condicional para índice de atención a cierto grupo h. Cuenta Tweets del grupo (h)
        elif use_case == 'Proximity to Group':
            if G.vp[property_label][v] == group:
                tweets_numerador += (G.vp['Tweets'][v])
        
    return tweets_numerador/tweets

#=========================================================================================================================
def homophily_index(graph: gt.Graph, property_name: str) -> dict:
    """
    Calculates the homiphily Index

    Args:
        g (Graph): The Graph object to analize.
        property_name (String): The name of the PropertyMap where the tipification of the nodes groups resides.

    Returns:
        type: dict with somethings XD
    """
    prop_map = graph.vp[property_name]

    # Extraigamos las categorías disponibles
    labels = [prop_map[v] for v in graph.vertices()]
    categorias = np.unique(labels)
    # Contemos cuantos nodos tenemos
    N = len(labels)

    # Extraigamos todos los tipos de enlaces
    edges_data = []
    for e in graph.edges():
        source_type = prop_map[e.source()]
        target_type = prop_map[e.target()]
        edges_data.append((source_type, target_type))

    enlaces = pd.DataFrame(edges_data, columns = ["Source", "Target"])


    w_i = dict()
    s_i = dict()
    d_i = dict()
    H_i = dict()
    IH_i = dict()
    for c in categorias:
        # Calculate w_i
        w_i[c] = labels.count(c)/N
        # Calculate s_i and d_i 
        s_i[c] = enlaces[(enlaces["Source"] == c) & (enlaces["Target"] == c)].shape[0]/enlaces.shape[0]
        d_i[c] = enlaces[(enlaces["Source"] == c) & (enlaces["Target"] != c)].shape[0]/enlaces.shape[0]
        # Calculate Homophily index
        H_i[c] = s_i[c]/(s_i[c] + d_i[c])
        # Calculate Coleman's inbreeding Homophily Index
        IH_i[c] = (H_i[c] - w_i[c])/(1 - w_i[c])

    return {"w_i": w_i, "s_i": s_i, "d_i": d_i, "H_i": H_i, "IH_i": IH_i}

#=========================================================================================================================
def SSI(g:gt.Graph, type:str):
    # Get undirected graph
    g_undir = g.copy()
    g_undir.set_directed(False)

    # Normalize adjacency
    adj = get_adjacency(g_undir)
    adj_norm = adj / adj.sum(axis=1, keepdims=True)

    # Get B matrix
    tipos = g.vp[type].a
    B = adj_norm[tipos.astype(bool)][:, tipos.astype(bool)]
    B.shape

    # Add edges to the graph based on the weighted adjacency matrix
    idx = B.nonzero()
    weights = B[idx]
    sub = gt.Graph(directed = False)
    sub.add_edge_list(np.transpose(idx))
    ew = sub.new_edge_property("double")
    ew.a = weights 
    sub.ep['weights'] = ew

    # Get connected components
    components, hist = gt.label_components(sub)
    del hist
    eigvals_CC = {}
    eigvect_CC = {}

    for label in np.unique(components.a):
        # Prepare filter map
        filtered_nodes = sub.new_vertex_property("bool")
        filtered_nodes.a = False
        
        for v in sub.vertices():
            if components[v] == label:
                filtered_nodes[v] = True
        
        # create a new subgraph object for each of the components
        subgraph = gt.GraphView(sub, vfilt=filtered_nodes)
        B_CC = get_adjacency(subgraph, 'weights')
        
        # Get igen values and vector. Store the biigest eigenvalue with its vector
        eigenvalues, eigenvectors = np.linalg.eig(B_CC)
        node_level_seg = eigenvectors[np.argmax(eigenvalues)]
        SSI_CC = np.max(eigenvalues)
        eigvals_CC[f"Component {label}"] = SSI_CC
        eigvect_CC[f"Component {label}"] = node_level_seg
    
    return eigvals_CC, eigvect_CC