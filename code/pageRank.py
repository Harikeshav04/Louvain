import time
import numpy as np

def print_timestamp(info_string):
    current_time = time.strftime("%H:%M:%S ->\t", time.localtime())
    print(f"{current_time}{info_string}")

def page_rank(nb_nodes, nb_edges, adj, degree):
    d = 0.85
    iter_max = 100
    rank_v1 = np.ones(nb_nodes)
    rank_v2 = np.ones(nb_nodes)
    rank_v3 = np.ones(nb_nodes)
    rank_v4 = np.ones(nb_nodes)
    
    for _ in range(iter_max):
        tmp_v1 = np.zeros(nb_nodes)
        tmp_v2 = np.zeros(nb_nodes)
        tmp_v3 = np.zeros(nb_nodes)
        tmp_v4 = np.zeros(nb_nodes)
        
        for i in range(nb_nodes):
            for j in range(nb_nodes):
                if adj[j][i] > 0:
                    tmp_v1[i] += rank_v1[j] / degree[j]
                    tmp_v2[i] += rank_v2[j] / degree[j]
                    tmp_v3[i] += adj[j][i] * rank_v3[j] / degree[j]
                    tmp_v4[i] += adj[j][i] * rank_v4[j] / degree[j]
                    
        rank_v1 = (1 - d) / nb_nodes + d * tmp_v1
        rank_v2 = (1 - d) + d * tmp_v2
        rank_v3 = (1 - d) + d * tmp_v3
        rank_v4 = (1 - d) / nb_nodes + d * tmp_v4
        
    return rank_v1, rank_v2, rank_v3, rank_v4

def main():
    import sys
    if len(sys.argv) != 6:
        print("Usage: python pageRank.py <nb_nodes> <nb_edges> <input_file> <output_file> <directed|undirected>")
        return 1
    
    nb_nodes = int(sys.argv[1])
    nb_edges = int(sys.argv[2])
    inname = sys.argv[3]
    outname = sys.argv[4]
    graph_type = sys.argv[5]
    
    # Initialize adjacency matrix and degree arrays
    adj = np.zeros((nb_nodes, nb_nodes))
    in_degree = np.zeros(nb_nodes, dtype=int)
    out_degree = np.zeros(nb_nodes, dtype=int)
    
    print_timestamp("Reading the input file")
    
    try:
        with open(inname, "r") as infile:
            for line in infile:
                parts = line.strip().split()
                if len(parts) != 3:
                    print(f"Error reading line: {line}")
                    return 4
                node1, node2, edge_weight = int(parts[0]) - 1, int(parts[1]) - 1, float(parts[2])
                if node1 >= nb_nodes or node2 >= nb_nodes or node1 < 0 or node2 < 0:
                    print(f"Node index out of bounds: {node1 + 1}, {node2 + 1}")
                    return 4
                adj[node1][node2] = edge_weight
                if graph_type == "undirected":
                    adj[node2][node1] = edge_weight
    except FileNotFoundError:
        print(f"Couldn't open {inname} for reading")
        return 2
    
    print_timestamp("Calculating degrees")
    
    for n in range(nb_nodes):
        out_degree[n] = np.count_nonzero(adj[n])
        in_degree[n] = np.count_nonzero(adj[:,n])
    
    print_timestamp("Computing PageRank")
    
    rank_v1, rank_v2, rank_v3, rank_v4 = page_rank(nb_nodes, nb_edges, adj, out_degree)
    
    print_timestamp("Saving results")
    
    try:
        with open(outname, "w") as outfile:
            outfile.write("Node\tIn\tOut\tRank_1\tRank_2\tRank_3\tRank_4\n")
            for n in range(nb_nodes):
                outfile.write(f"{n + 1}\t{in_degree[n]}\t{out_degree[n]}\t{rank_v1[n]}\t{rank_v2[n]}\t{rank_v3[n]}\t{rank_v4[n]}\n")
    except IOError:
        print(f"Couldn't open {outname} for writing")
        return 3
    
    print_timestamp("Done.")
    return 0

if __name__ == "__main__":
    main()
