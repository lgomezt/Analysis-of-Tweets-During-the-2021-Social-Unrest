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