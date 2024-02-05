import concurrent.futures
import graph_tool as gt
from glob import glob

XD = 2
def process_graph(file_path):
    g = gt.load_graph(file_path)
    edge = g.num_edges()
    print(edge + XD)

def main():
    files = files = glob('/mnt/disk2/Data/3_Day_Graphs/*.graphml')  # Your actual file paths
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(process_graph, files)

if __name__ == '__main__':
    main()