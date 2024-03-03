import graph_tool.all as gt
import numpy as np
import pandas as pd

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