'''
    Graph Tool.py
-------------------------------------------------------------
In this Notebook, we construct the graph of the Rt's Users
during the Paro Nacional. Each graph corresponds to the Rt Network
in moving windows of three days between April 28 of 2021 and June 30 of 2021
---------------------------------------------------------------
This Script Will be run using sudo because of permission issues
'''

# -----------------------
# LIBRARIES
# -----------------------
import pickle
from glob import glob
import numpy as np
import pandas as pd
import graph_tool as gt
from datetime import datetime
from tqdm import tqdm
from scipy.sparse import csr_matrix
from scipy.sparse import lil_matrix

# -----------------------
# LOAD FILES
# -----------------------
with open('/mnt/disk2/Data/Pickle/user_indices.pkl','rb') as file:
    user_indices = pickle.load(file)

with open('/mnt/disk2/Data/Pickle/user_to_party_paro.pkl','rb') as file:
    user_to_party_paro = pickle.load(file)

# from user_indices we transform the keys as values and the values as keys
user_indices_2 = {value: key for key, value in user_indices.items()}

# This is the end of the 3 day window considered for the graphs
start = '2021-04-30 23:59:59'
end = '2021-06-29 23:59:59'
date_list = pd.date_range(start = start, end = end, freq = 'D')


# -----------------------
# GRAPH CREATION IN FOR LOOP
# -----------------------
k = 1
files = glob('/mnt/disk2/Data/Matrices/*.npz')
for file in tqdm(files):
    
    # First, we load the stored info into a normal CSR matrix.
    data = np.load(file)
    indices = data['indices']
    indptr = data['indptr']
    shape = data['shape']
    data = data['data']
    A = csr_matrix((data, indices, indptr), shape = shape)
    
    # Now we can create the graph using 'graph_tool'.
    idx = A.nonzero()
    weights = A[idx]
    g = gt.Graph(directed = False)
    g.add_edge_list(np.transpose(idx))
    ew = g.new_edge_property("double")
    ew.a = weights 
    g.ep['edge_weight'] = ew

    date = date_list[k] # This gets the end of day date of every graph to store it.
    date = datetime.strftime(date, '%d-%m-%Y')
    
    # Finally we save the graph in .graphml format.
    filename = f'graph_{date}.graphml'
    output_filepath = '/mnt/disk2/Data/Graphs_2/' + filename
    print(output_filepath)
    g.save(output_filepath)
    print(f"File '{filename}' successfully created and stored.")
    k += 1