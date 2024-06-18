import sys


def calculate_nodes_edges(infile):
    edges = 0
    nodelist = set()
    dir_data = "../data/subchallenge1/"
    file_path = dir_data + infile + ".txt"
    with open(file_path, 'r') as f:
        for edge in f:
            if edge.strip():
                node1, node2 = edge.strip().split()
                nodelist.add(node1)
                nodelist.add(node2)
                edges += 1
    nodes = len(nodelist)
    return edges, nodes


if len(sys.argv) != 2:
    print("\nUsage: python calculate_node_edge.py <in_file>")
    quit()

infile = sys.argv[1]
edges, nodes = calculate_nodes_edges(infile)
print(f"Nodes: {nodes}")
print(f"Edges: {edges}")
