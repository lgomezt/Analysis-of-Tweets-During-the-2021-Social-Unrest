# Mathematical and Data Managment
import numpy as np
import pandas as pd

# Graph Managment
import graph_tool.all as gt
from utils.Functions import * 

# ========================================================================================
def attention_g_others(g, types, weights, group,in_attention=True):
    index = get_types_index(g,types)[group]
    M_v_others = me_vs_others(g, index, types, weights)
    
    active_nodes = set()
    for e in g.edges():
        active_nodes.add(int(e.source()))
    N_active_nodes = len(active_nodes)
    
    if in_attention:
        P = (M_v_others[0,1]) / N_active_nodes
    else:
        P = (M_v_others[1,0]) / N_active_nodes
    
    tweets_no_g = 0
    tweets = 0
    for v in g.vertices():
        tweets += (g.vp['Tweets'][v])
        if g.vp[types][v] != group:
            tweets_no_g += (g.vp['Tweets'][v])
    
    Pi = tweets_no_g/tweets
    
    return P/Pi

#=========================================================================================================================
def attention_g_h(g, types, weights, group1, group2, in_attention = True):
    M = get_contact_layer(g, types, weights)
    index_1 = get_types_index(g,types)[group1]
    index_2 = get_types_index(g,types)[group2]
    
    if in_attention:
        P = (M[index_1,index_2]) / np.sum(M)
    else:
        P = (M[index_2,index_1]) / np.sum(M)
    
    tweets_h = 0 # Contador para Retweets del grupo2
    tweets = 0 # Contador del total de Retweets
    for v in g.vertices():
        tweets += (g.vp['Tweets'][v])
        if g.vp[types][v] == group2:
            tweets_h += (g.vp['Tweets'][v])
            
    Pi = tweets_h/tweets
    
    return P/Pi

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