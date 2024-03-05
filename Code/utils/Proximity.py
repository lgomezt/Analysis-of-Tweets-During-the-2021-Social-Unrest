from utils.Bojanowski import * 
import graph_tool.all as gt

# ========================================================================================
def individual_proximity_to_h(G: gt.Graph, v_index:int, property_label:str, group:str, in_proximity = True): 
    """
     Individual Proximity Index: This index calculates the proximity from and individual to a political group
     
     W_jk
    Args:
        G (Graph): The Graph object to analize.
        property_name (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        weights (String): The name of the EdgePropertyMap where the weights of the edges resides
        g (String): name of the group g
        in_proximity (bool): boolean that specifes if you want the proximity from g to h or from h to g
    Returns:
        index (float): The Proximity Index 
    """
    individual_weight = 0
    if isinstance(v,gt.Vertex):
        pass
    else:
        v = G.vertex(v_index)
    if G.vp['Isolate'][v]:
        return np.nan
    for e in v.out_edges():
        if G.vp[property_label][e.target()] == group:
            individual_weight += G.ep['Normal Weight'][e]
    
    return individual_weight

# ========================================================================================
def individual_proximity_to_others(G: gt.Graph, v_index:int, property_label:str, in_proximity = True): 
    """
     Individual Proximity Index: This index calculates the proximity from and individual to a political group
     Different from its political group
     
     W_jk
    Args:
        G (Graph): The Graph object to analize.
        property_name (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        weights (String): The name of the EdgePropertyMap where the weights of the edges resides
        g (String): name of the group g
        in_proximity (bool): boolean that specifes if you want the proximity from g to h or from h to g
    Returns:
        index (float): The Proximity Index 
    """
    individual_weight = 0
    if isinstance(v_index, gt.Vertex):
        pass
    else:
        v = G.vertex(v_index)
    if G.vp['Isolate'][v]:
        return np.nan
    for e in v.out_edges():
        group = G.vp['Political Label'][v]
        if G.vp[property_label][e.target()] != group:
            individual_weight += G.ep['Normal Weight'][e]
    
    return individual_weight

# ========================================================================================
def proximity_g_others(G: gt.Graph, property_label:str, weights:str, g:str, in_proximity=True):
    """
    Proximity Index that group g devotes to all other groups (-g). This index takes in count
    weight and of the edges and directionality
    
    W_h-h
    Args:
        G (Graph): The Graph object to analize.
        property_name (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        weights (String): The name of the EdgePropertyMap where the weights of the edges resides
        g (String): name of the group g
        in_proximity (bool): boolean that specifes if you want the proximity from g to h or from h to g
    Returns:
        index (float): The Proximity Index 
    """
    active_nodes = set()
    sum_weight = 0
    for e in G.edges():
        if G.vp[property_label][e.source()] == g:
            active_nodes.add(int(e.source()))
        if in_proximity:
            if G.vp[property_label][e.source()] == g and G.vp[property_label][e.target()] != g:
                sum_weight += G.ep[weights][e]
        else:
            if G.vp[property_label][e.source()] != g and G.vp[property_label][e.target()] == g:
                sum_weight += G.ep[weights][e]
    N_active_nodes = len(active_nodes)

    return sum_weight/N_active_nodes

#=========================================================================================================================
def proximity_g_h(G, property_label:str, weights:str, g:str, h:str, in_proximity = True):
    """
    Proximity Index that group g devotes to group h. This index takes in count
    weight and of the edges and directionality
    
    W_hk
    Args:
        - G (Graph): The Graph object to analize.
        - property_name (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        - weights (String): The name of the EdgePropertyMap where the weights of the edges resides
        - g (String): name of the group g
        - h (String): name of the group h
        - in_proximity (bool): boolean that specifes if you want the proximity from g to h or from h to g

    Returns:
        index (float): The Proximity Index 
    """
    active_nodes = set()
    sum_weight = 0
    for e in G.edges():
        if G.vp[property_label][e.source()] == g:
            active_nodes.add(int(e.source()))
        if in_proximity:
            if G.vp[property_label][e.source()] == g and G.vp[property_label][e.target()] == h:
                sum_weight += G.ep[weights][e]
        else:
            if G.vp[property_label][e.source()] == h and G.vp[property_label][e.target()] == g:
                sum_weight += G.ep[weights][e]
    N_active_nodes = len(active_nodes)
    
    return sum_weight/N_active_nodes

#=========================================================================================================================
def at_random_scenario(G:gt.Graph, property_label:str, group:str, use_case:str):
    """
    We calculate the random scenario of the directed and weighted twitter network
    We use the amount of original tweets that the users make and we calculate the proportion
    of tweets from a particular group over the total number of tweets.
    This is just the denominator of the proximity index perse.
    
    W_hk
    Args:
        - G (Graph): The Graph object to analize.
        - property_name (String): The name of the PropertyMap where the tipification of the nodes groups resides.
        - g (String): name of the group
        - use_case (String): can be "Proximity to Others" or "Proximity to Group" depending on the index to analize

    Returns:
        index (float): Denominator for proximity Index 
    """
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