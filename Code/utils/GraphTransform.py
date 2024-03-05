import graph_tool.all as gt
import networkx as nx

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