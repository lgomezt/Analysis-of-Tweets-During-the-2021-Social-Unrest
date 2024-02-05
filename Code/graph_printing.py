# Mathematical and Data Managment
import numpy as np

# Graph Managment
import graph_tool.all as gt
import networkx as nx
from utils.subutils.Functions import *
from utils.Segregation import *

# Data Visualization
import matplotlib.pyplot as plt
from fa2.forceatlas2 import ForceAtlas2

# Miscellaneous
from glob import glob
import random
import time
from datetime import datetime, timedelta
import concurrent.futures

random.seed(2)
np.random.seed(2) 

# Create ForceAtlas2 object with desired parameters
forceatlas2 = ForceAtlas2(
                          # Behavior alternatives
                          outboundAttractionDistribution=True,  # Dissuade hubs
                          linLogMode=False,  # NOT IMPLEMENTED
                          adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
                          edgeWeightInfluence=1.0,

                          # Performance
                          jitterTolerance=1.0,  # Tolerance
                          barnesHutOptimize=True,
                          barnesHutTheta=1.2,
                          multiThreaded=False,  # NOT IMPLEMENTED

                          # Tuning
                          scalingRatio=2.0,
                          strongGravityMode=False,
                          gravity=1.0,

                          # Log
                          verbose=False)

initial_pos = {node: (random.random(), random.random()) for node in range(36964)}

def process_graph(file):  
    
    # LOAD GRAPH =============================================================
    t1 = time.perf_counter()  
    # Load Grap
    g = gt.load_graph(file)

    g.set_directed(False)
    g_nx = to_networkx(g)
    
    # CRTEATE LAYOUT ==========================================================                                         
    layout_g_nx = forceatlas2.forceatlas2_networkx_layout(g_nx, pos=initial_pos, iterations=200)
    
    # CREATE AESTHETICS ======================================================
    
    # Color
    color_map_dict = {
        'No Retweets': 'gray',
        'Izquierda': 'blue',
        'Derecha': 'red',
        'Centro': 'green'
    }
    color_map_node = [color_map_dict[g_nx.nodes[node]['Political Label']] for node in g_nx]
    #color_edge_map = [color_map_dict[g_nx.nodes(data=True)[edge[1]]['Political Label']] for edge in list(g_nx.edges(data=True))]

    # Alpha
    degrees = dict(g_nx.degree())
    max_degree = max(degrees.values())
    alpha_values = [(degree / max_degree) for degree in degrees.values()]

    # Size
    node_degrees = [g_nx.degree(node) * 100 for node in g_nx.nodes()]
    def normalize(x, max, min):
        return 100 * ((x - min)/(max - min))
    max_deg = max(node_degrees)
    min_deg = min(node_degrees)
    node_size = list(map(lambda x: normalize(x, max_deg, min_deg), node_degrees))
    
    # CIRCLE FILTER ================================================================================
    
    # Vamos a calcular el centroide de toda la red. Vamos a utilizar la mediana
    x = [layout_g_nx[i][0] for i in layout_g_nx.keys()]
    y = [layout_g_nx[i][1] for i in layout_g_nx.keys()]

    centroide_x = np.median(x)
    centroide_y = np.median(y)

    # Ahora vamos a construir círculos centrados en el centroide con diferentes radios. Con esto en mente 
    # queremos definir cual es la proporción de nodos dentro y fuera del circulo  

    # Para construir el circulo ideal vamos a revisar las distancias euclideana (eficientemente) de todos los puntos al centroide
    resta = np.array(list(zip(x, y))) - np.array((centroide_x, centroide_y))
    resta_cuadrado = resta**2
    suma_cuadrados = np.sum(resta_cuadrado, axis = 1)
    distancia_euclideana = np.sqrt(suma_cuadrados)
    
    # FILTER TO IMPORTANT NODES ===========================================================================

    filtro_r_12 = distancia_euclideana < 12000
    g_nx_r_12 = g_nx.copy()

    # Asegurarse de que la lista booleana tiene la misma longitud que el número de nodos en la red
    if len(filtro_r_12) == g_nx_r_12.number_of_nodes():
        # Identificar los nodos a eliminar
        nodos_a_eliminar = [nodo for nodo, mantener in zip(g_nx_r_12.nodes, filtro_r_12) if not mantener]
        porcentaje_eliminacion = len(nodos_a_eliminar)/g_nx_r_12.number_of_nodes()
        print("Vamos a eliminar el {:0.1%} de los nodos".format(porcentaje_eliminacion))
        # Eliminar los nodos
        g_nx_r_12.remove_nodes_from(nodos_a_eliminar)
    else:
        print("El filtro y el número de nodos tienen diferente tamaño!")

    # Escogemos las posiciones adecuadas, colores y tamaños
    pos_r_12 = {key: layout_g_nx[key] for key in g_nx_r_12.nodes}
    node_colors_r_12 = np.array(color_map_node)[filtro_r_12]
    node_sizes_r_12 = np.array(node_size)[filtro_r_12]*5
    
    date = g_nx_r_12.graph['Starting Date']
    
    # GRAAAAAAPH =====================================================================
    # Title
    starting_date_obj = datetime.strptime(date, '%Y-%m-%d')
    formatted_starting = starting_date_obj.strftime('%B %d, %Y')
    ending_date_obj = starting_date_obj + timedelta(days=3)
    formatted_ending = ending_date_obj.strftime('%B %d, %Y')
    
    plt.figure(figsize = (8, 10)) 

    # Draw nodes with specified size and color
    nx.draw_networkx_nodes(g_nx_r_12, pos_r_12, node_color = node_colors_r_12, node_size = node_sizes_r_12, alpha = 0.3);

    # Draw edges
    # nx.draw_networkx_edges(g, pos, alpha = 0.5, arrows = False)
    plt.title(f"Twitter Community. Data from {formatted_starting} to {formatted_ending}")

    plt.axis('off');
    plt.savefig(f"Results/3_Day_graphs_Viz/viz_graph_starting_{date}")
    
    t2 = time.perf_counter()
    print(f"saved graph from file {file.split('/')[-1]} lasting {(t2-t1)//60} Minutes'")
    print('-'*50)
    return None

def main():
    files = glob('/mnt/disk2/Data/3_Day_Graphs/*.graphml')
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(process_graph, files)

if __name__ == '__main__':
    main()


print('***************************Terminado******************************')
        