# Mathematical and Data Managment
import numpy as np
import pandas as pd
import scipy.sparse as sp

# Graph Managment
import graph_tool.all as gt
from Functions import *

# Data Visualization
import seaborn as sns
import matplotlib.pyplot as plt

# Miscellaneous
from glob import glob
from tqdm import tqdm
import random

# =========================================================================================================================
def Freeman_Global_No_Weight(g: gt.Graph, types:str) -> float:
    """
    Global freeman Segregation Index

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
    Description of your function.

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
    P = me_vs_others[1,1] / np.sum(me_vs_others[1,:])
            
    # Calculate Pi
    nodes = g.num_vertices()
    nodes_in_group = np.sum(groups_list)
    nodes_out_group = nodes - nodes_in_group

    pi = nodes_out_group / nodes
            
    return 1 - (P / pi)

#=========================================================================================================================
def Freeman_Two_Groups(g: gt.Graph, types:str):
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