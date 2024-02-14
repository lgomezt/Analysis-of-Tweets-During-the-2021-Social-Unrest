# Mathematical and Data Managment
import numpy as np
import pandas as pd

# Graph Managment
import graph_tool.all as gt
from utils.Functions import *

#=========================================================================================================================
def Freeman_Classic(G: gt.Graph, types:str) -> float:
    """
    Classic Freeman Segregation Index for Unweighted Graphs. This calculates the proprotion of cross ties in the graph as
    a fraction of the proportion of cross ties if the graph were randomly distributed.

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        groups (String): The name of the group To calculate the Segregation Index

    Returns:
        type: Segregation Index of Freeman from one group against all the other groups using a
            weighted adjacency matrix
    """
    g = G.copy()
    if g.is_directed():
        g.set_directed(False)
    else:
        pass      
        
    M = get_contact_layer(g, types=types)
    
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
def Freeman_Groups(G: gt.Graph, types:str, group:str) -> float:
    """
    Description of your function.

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        groups (String): The name of the group To calculate the Segregation Index

    Returns:
        type: Segregation Index of Freeman from one group against all the other groups

    """
    g = G.copy()
    # This Measure is for Undirected Graphs and Unweighted
    if g.is_directed():
        g.set_directed(False)
    else:
        pass 
    
    # get important stuff
    groups = get_types_index(g, types)
    groups_list = get_types_dict(g, types=types)[group]
    group_index = groups[group]
    
    # Calculate contact Matrix, me vs others
    me_vs_others_matrix = me_vs_others(g, group_index, types)
    
    # Getting group sizes
    total = g.num_vertices()
    nodes_in_group = sum(groups_list)
    nodes_out_group = g.num_vertices() - nodes_in_group
    
    # Calculating P (Proportion of Between group edges)
    P = me_vs_others_matrix[0,1] / np.sum(me_vs_others_matrix)
    
    # Calculating Pi (Expected Proportion of Between-group ties in random graph)
    Pi = (2 * nodes_in_group * nodes_out_group) / (total * (total - 1))
    return (Pi-P)/Pi

# =========================================================================================================================
def Freeman_Global(G: gt.Graph, types:str) -> float:
    """
    Global Freeman Segregation Index for more than 2 groups. This is based on the Bojanoski Formula from his paper.

    Args:
        g (Graph): The Graph object to analize.
        types (String): The name of the PropertyMap where the tipification of the nodes groups resides.

    Returns:
        type: Segregation Index of Freeman

    """
    g = G.copy()
    if G.is_directed():
        g.set_directed(False)
    else:
        pass  
    
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
        g.set_directed(False)
    else:
        pass      
    
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
def Freeman_homophily(G: gt.Graph, type:str, group1:str, group2:str):
    """
    Calculates the homophily Index

    Args:
        g (Graph): The Graph object to analize.
        property_name (String): The name of the PropertyMap where the tipification of the nodes groups resides.

    Returns:
        type: dict with some things XD
    """
    # Filter Graph
    filter = G.new_vp('bool')
    filter.a = False
    
    for v in G.vertices():
        if G.vp[type][v] == group1 or G.vp[type][v] == group2:
            filter[v] = True
    
    sub = gt.GraphView(G, vfilt = filter, directed = True)
    
    cross_in_ties = 0
    cross_out_ties = 0
    same_ties = 0
    for e in sub.edges():
        if sub.vp[group1][e.source()]:
            if sub.vp[group1][e.target()]:
                same_ties += 0
            else:
                cross_out_ties += 1
        else:
            if sub.vp[group1][e.target()]:
                cross_in_ties += 1
            else:
                same_ties += 1
    
    edges = sub.num_edges()
    nodes = sub.num_vertices()
    
    P_in = cross_in_ties/edges
    P_out = cross_out_ties/edges
    
    n_1 = sum(sub.vp[group1].a)
    n_2 = sum(sub.vp[group2].a)
    
    Pi = (2*n_1*n_2)/(nodes * (nodes - 1))
    
    return {'Homophily in': (P_in/Pi), 'Homophily out': (P_out/Pi)}