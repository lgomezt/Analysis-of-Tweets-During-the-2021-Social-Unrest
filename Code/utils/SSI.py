import graph_tool.all as gt
from Code.utils.Bojanowski import *

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