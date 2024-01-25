# Mathematical and Data Managment
import numpy as np
import pandas as pd

# Graph Managment
import graph_tool.all as gt
from utils.subutils.Functions import *

# =========================================================================================================================
def Freeman_Global_No_Weight(g: gt.Graph, types:str) -> float:
    """
    Global Freeman Segregation Index for more than 2 groups. This is based on the Bojanoski Formula from his paper.

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where the tipification of the nodes groups resides.

    Returns:
        type: Segregation Index of Freeman

    """
    # Get Relevant Matrices
    types_matrix = get_types_matrix(g, types = types)
    M = get_contact_layer(g, types = types)
    
    # We get the amount of vertices and groups
    N, K = types_matrix.shape
    
    # Get the amount of nodes per group
    n_k = []
    for k in range(K):
        n = np.sum(types_matrix[:, k])
        n_k.append(n)
    n_k = np.array(n_k)
    
    if g.is_directed():
        # Calculate In-Between edges
        M_up = np.triu(M,k=1)
        M_low = np.tril(M,k=1)
        between_edges = M_up.sum() + M_low.sum()
    else:
        M_up = np.triu(M,k=1)
        between_edges = M_up.sum()
    

    # Calculate P 
    P = between_edges / M.sum()

    # Prepare for calculation
    numerator = P * N * (N - 1)
    denominator = (n_k.sum() **2) - (np.sum(n_k **2))

    # calculate using the formula
    S = 1 - (numerator / denominator)
    
    return S


#=========================================================================================================================
def Freeman_Groups_No_Weight(g: gt.Graph, types:str, group:str) -> float:
    """
    Description of your function.

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        groups (String): The name of the group To calculate the Segregation Index

    Returns:
        type: Segregation Index of Freeman from one group against all the other groups

    """
    # get important stuff
    M = get_contact_layer(g, types=types)
    groups = get_types_index(g,types)
    groups_list = get_types_dict(g,types=types)[group]
    group_index = groups[group]
    
    # Calculate contact Matrix, me vs others
    me_vs_others_matrix = me_vs_others(M, group_index)
    
    # Getting group sizes
    total = g.num_vertices()
    nodes_in_group = sum(groups_list)
    nodes_out_group = g.num_vertices() - nodes_in_group
    
    # Calculating P (Proportion of Between group edges)
    P = me_vs_others_matrix[0,1] / np.sum(me_vs_others_matrix)
    
    # Calculating Pi (Expected Proportion of Between-group ties in random graph)
    Pi = (2 * nodes_in_group * nodes_out_group) / (total * (total - 1))
    return (Pi-P)/Pi

#=========================================================================================================================
def Freeman_Groups_Weight(g: gt.Graph, types:str, group:str, weights:str) -> float:
    """
    Calculates the Freeman Segregation Index without weights for graphs wtih more than 2 groups.
    This functions takes one of the groups and calculates the Segregation of this group against all other groups.
    This formula generalices the Classic Freeman Approuch for contact layers with more than 2 dimensions.

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        weights (String): The name of the EdgePropertyMap where the weights of the edges resides
        groups (String): The name of the group To calculate the Segregation Index

    Returns:
        type: Segregation Index of Freeman from one group against all the other groups using a
            weighted adjacency matrix
    """

    # get important stuff
    M = get_contact_layer(g, types=types, weights=weights)
    groups = get_types_index(g,types)
    groups_list = get_types_dict(g,types=types)[group]
    group_index = groups[group]

    # Calculate contact Matrix, Me Vs Others
    M_11 = M[group_index, group_index]
    M_12 = np.sum(M[group_index,:]) - M_11
    M_21 = np.sum(M[:, group_index]) - M_11
    not_me_contact = np.delete(np.delete(M, group_index, axis=0), group_index, axis=1)
    M_22 = np.sum(not_me_contact)

    me_vs_others = np.array([[M_11, M_12],[M_21,M_22]])

    # Calculate P
    P = me_vs_others[0,1] / np.sum(me_vs_others[1,:])
            
    # Calculate Pi
    nodes = g.num_vertices()
    nodes_in_group = np.sum(groups_list)
    nodes_out_group = nodes - nodes_in_group

    pi = nodes_out_group / nodes
            
    return 1 - (P / pi)

#=========================================================================================================================
def Freeman_Two_Groups(g: gt.Graph, types:str) -> float:
    """
    Classic Freeman Segregation Index for Unweighted Graphs. This calculates the proprotion of cross ties in the graph as
    a fraction of the proportion os cross ties if the graph were randomly distributed.

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        weights (String): The name of the EdgePropertyMap where the weights of the edges resides
        groups (String): The name of the group To calculate the Segregation Index

    Returns:
        type: Segregation Index of Freeman from one group against all the other groups using a
            weighted adjacency matrix
    """
    M = get_contact_layer(g, types=types)
    
    assert M.shape[0] == M.shape[1] == 2, 'Usar Freeman_Group_Global'
    
    cross_ties = M[0,1]
    edges = g.num_edges()
    nodes = g.num_vertices()
    
    P = cross_ties/edges
    types_matrix = get_types_matrix(g, types = types)
    
    n_1 = np.sum(types_matrix[:, 0])
    n_2 = np.sum(types_matrix[:, 1])
    
    Pi = (2*n_1*n_2)/(nodes * (nodes - 1))
    return 1 - (P / Pi) 

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