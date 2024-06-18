import os
import sys
import subprocess
from time import localtime, strftime
from ast import literal_eval

def run_command(cmd):
    print(f"Running command: {cmd}")
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(f"stdout: {stdout.decode()}")
    print(f"stderr: {stderr.decode()}")

import os

def safe_delete(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted {filepath}")
        else:
            print(f"File {filepath} does not exist.")
    except Exception as e:
        print(f"Error deleting {filepath}: {e}")


def runLouvain_PR(dirL, graphL, weightsL, treeL, commL, netName, partName):
    # Convert network using main_convert
    cmd = f'"{os.path.join(dirL, "main_convert")}" -i "{netName}" -o "{graphL}" -w "{weightsL}"'
    run_command(cmd)

    # Run Louvain using main_community
    cmd = f'"{os.path.join(dirL, "main_louvain")}" "{graphL}" -l -1 -q 0 -w "{weightsL}" -p "{partName}" > "{treeL}"'
    run_command(cmd)

    # Analyze hierarchy using main_hierarchy
    cmd = f'"{os.path.join(dirL, "main_hierarchy")}" "{treeL}"'
    run_command(cmd)

    # Extract communities at level 1 using main_hierarchy
    cmd = f'"{os.path.join(dirL, "main_hierarchy")}" "{treeL}" -l 1 > "{commL}"'
    run_command(cmd)

    # Clean up intermediate files
    safe_delete(graph_louvain)
    safe_delete(weights_louvain)
    safe_delete(tree_louvain)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("\nUsage: " + sys.argv[0] + " <network> <threshold for recursion>")
        quit()

    network_name = sys.argv[1]
    size_threshold_for_recursion = literal_eval(sys.argv[2])

    dir_script = os.path.dirname(os.path.abspath(__file__))
    dir_final_code = os.path.dirname(dir_script)
    dir_louvain = os.path.join(dir_script, "generic/src/")
    dir_data = os.path.join(dir_final_code, "data/subchallenge1/")

    print(strftime("%H:%M:%S", localtime()) + ": Loading the input network")
    neighbours = {}
    weights = {}

    filename = os.path.join(dir_data, network_name + ".txt")

    with open(filename, "r") as inFile:
        print(strftime("%H:%M:%S", localtime()) + ": Loading the PageRank results")
        
        for line in inFile:
            line = line.rstrip()
            if line.strip():  # Check if the line is not empty after stripping whitespace
                temp_array = line.split("\t")
                if len(temp_array) == 2:
                    node1 = temp_array[0]
                    node2 = temp_array[1]
                    weight = 1  # Default weight for unweighted edge
                elif len(temp_array) == 3:
                    node1 = temp_array[0]
                    node2 = temp_array[1]
                    try:
                        weight = float(temp_array[2])  # Convert weight to float
                    except ValueError:
                        print(f"Ignoring line due to non-numeric weight: {line}")
                        continue
                else:
                    print(f"Ignoring line due to unexpected format: {line}")
                    continue

                neighbours.setdefault(node1, []).append(node2)
                weights[node1 + "-" + node2] = weight
                neighbours.setdefault(node2, []).append(node1)
                weights[node2 + "-" + node1] = weight

    print("Graph loaded successfully.")

    PageRank = {}

    print(strftime("%H:%M:%S", localtime()) + ": Loading the PageRank results")

    with open(os.path.join(dir_data, "PR_" + network_name + ".txt"), 'r') as inFile:
        lines = inFile.readlines()[1:]  # Skip header line
        for line in lines:
            temp_array = line.rstrip().split("\t")
            node = temp_array[0]
            PR = literal_eval(temp_array[4])
            PageRank[node] = PR

    print(strftime("%H:%M:%S", localtime()) + ": Generating initial partition")

    with open(os.path.join(dir_final_code, "partition_" + network_name + ".txt"), 'w') as outFile:
        for n in neighbours:
            max_PR = PageRank[n]
            max_node = n
            for node in neighbours[n]:
                if PageRank[node] > max_PR:
                    max_PR = PageRank[node]
                    max_node = node
            outFile.write(n + " " + max_node + "\n")

    print(strftime("%H:%M:%S", localtime()) + ": Running Louvain")

    graph_louvain = os.path.join(dir_louvain, network_name + "_graph")
    weights_louvain = os.path.join(dir_louvain, network_name + "_weights")
    tree_louvain = os.path.join(dir_louvain, network_name + "_tree")
    comm_louvain = os.path.join(dir_louvain, "Sample_undig_node2comm_level1.txt")
    part_louvain = os.path.join(dir_final_code, "partition_" + network_name + ".txt")

    runLouvain_PR(dir_louvain, graph_louvain, weights_louvain, tree_louvain, comm_louvain, os.path.join(dir_data, network_name + ".txt"), part_louvain)

    print(strftime("%H:%M:%S", localtime()) + ": Loading the communities")

    communities = dict()
    communities_needing_recursion = []

    with open(comm_louvain, 'r') as inFile:
        for line in inFile:
            temp_array = line.rstrip().split(" ")
            node = temp_array[0]
            community = temp_array[1]
            if community not in communities:
                communities[community] = []
            communities[community].append(node)

    print(strftime("%H:%M:%S", localtime()) + ": (" + str(len(communities)) + " communities)")

    print(strftime("%H:%M:%S", localtime()) + ": Processing")

    comm_louvain_analysis = os.path.join(dir_louvain, network_name + "_allValidCommunities.txt")

    with open(comm_louvain_analysis, 'w') as outFile:
        nb_main_comm = 0
        nb_invalid_comm = 0

        for comm in communities:
            connectivity = 0.0
            weighted_connectivity = 0.0
            if len(communities[comm]) > size_threshold_for_recursion:
                communities_needing_recursion.append(communities[comm])
            elif len(communities[comm]) > 2:
                nb_main_comm += 1
                txt = ""
                for node1 in communities[comm]:
                    txt += node1 + "\t"
                    for node2 in communities[comm]:
                        if node1 in neighbours[node2]:
                            connectivity += 1
                            weighted_connectivity += weights[node1 + "-" + node2]
                connectivity = connectivity / (len(communities[comm]) * (len(communities[comm]) - 1))
                weighted_connectivity = weighted_connectivity / (len(communities[comm]) * (len(communities[comm]) - 1))
                outFile.write("m" + str(nb_main_comm) + "\t" + str(weighted_connectivity) + "\t" + txt.rstrip() + "\n")
            else:
                nb_invalid_comm += 1

    print(strftime("%H:%M:%S", localtime()) + ": " + str(nb_main_comm) + " communities extracted, " + str(len(communities_needing_recursion)) + " sent to recursion")

    print(strftime("%H:%M:%S", localtime()) + ": Recursion")

    i = 0
    while i < len(communities_needing_recursion):
        comm = str(i + 1)
        print(strftime("%H:%M:%S", localtime()) + ":\tSubcommunity " + comm + "/" + str(len(communities_needing_recursion)) + " (" + str(len(communities_needing_recursion[i])) + " nodes)")

        print(strftime("%H:%M:%S", localtime()) + ":\t\tSubnetwork extraction")

        subnetwork = os.path.join(dir_louvain, network_name + "_subnetwork_community_" + comm + ".txt")
        with open(subnetwork, 'w') as outFileSN, open(os.path.join(dir_data, network_name + ".txt"), 'r') as inFile:
            for line in inFile:
                temp_array = line.rstrip().split("\t")
                node1 = temp_array[0]
                node2 = temp_array[1]
                if node1 in communities_needing_recursion[i] and node2 in communities_needing_recursion[i]:
                    outFileSN.write(line)

        print(strftime("%H:%M:%S", localtime()) + ":\t\tLoading the PageRank results")

        PageRankSN = dict()
        with open(os.path.join(dir_data, "PR_" + network_name + ".txt"), 'r') as inFile:
            lines = inFile.readlines()
            for l in range(1, len(lines)):
                temp_array = lines[l].rstrip().split("\t")
                node = temp_array[0]
                PR = literal_eval(temp_array[5])
                if node in communities_needing_recursion[i]:
                    PageRankSN[node] = PR

        print(strftime("%H:%M:%S", localtime()) + ":\t\tGenerating initial partition")

        part_louvain = os.path.join(dir_louvain, "partition_" + network_name + "_" + comm + ".txt")
        with open(part_louvain, 'w') as outFileSN:
            for n in communities_needing_recursion[i]:
                max_PR = PageRankSN[n]
                max_node = n
                for node in neighbours[n]:
                    if node in communities_needing_recursion[i]:
                        if PageRankSN[node] > max_PR:
                            max_PR = PageRankSN[node]
                            max_node = node
                outFileSN.write(n + " " + max_node + "\n")

        print(strftime("%H:%M:%S", localtime()) + ":\t\tRunning Louvain")

        graph_louvain = os.path.join(dir_louvain, network_name + "_subnetwork_community_" + comm + "_graph.bin")
        weights_louvain = os.path.join(dir_louvain, network_name + "_subnetwork_community_" + comm + "_graph.weights")
        tree_louvain = os.path.join(dir_louvain, network_name + "_subnetwork_community_" + comm + "_graph.tree")
        comm_louvain = os.path.join(dir_louvain, network_name + "_subnetwork_community_" + comm + "_graph_node2comm_level1")

        runLouvain_PR(dir_louvain, graph_louvain, weights_louvain, tree_louvain, comm_louvain, subnetwork, part_louvain)

        print(strftime("%H:%M:%S", localtime()) + ":\t\tProcessing the results")

        subcommunities = dict()
        with open(comm_louvain, 'r') as inFile:
            for line in inFile:
                temp_array = line.rstrip().split(" ")
                node = temp_array[0]
                community = temp_array[1]
                if community not in subcommunities:
                    subcommunities[community] = []
                subcommunities[community].append(node)

        comm_louvain_analysis = os.path.join(dir_louvain, network_name + "_analysis_subcommunities_" + comm + ".txt")

        nb_subcomm = 0
        nb_added_for_recursion = 0

        for subcomm in subcommunities:
            if len(subcommunities[subcomm]) > size_threshold_for_recursion:
                if len(subcommunities[subcomm]) < len(communities_needing_recursion[i]):
                    nb_added_for_recursion += 1
                    communities_needing_recursion.append(subcommunities[subcomm])
            elif len(subcommunities[subcomm]) > 2:
                nb_subcomm += 1
                txt = ""
                connectivity = 0.0
                weighted_connectivity = 0.0
                for node1 in subcommunities[subcomm]:
                    txt += node1 + "\t"
                    for node2 in subcommunities[subcomm]:
                        if node1 in neighbours[node2]:
                            connectivity += 1
                            weighted_connectivity += weights[node1 + "-" + node2]
                connectivity = connectivity / (len(subcommunities[subcomm]) * (len(subcommunities[subcomm]) - 1))
                weighted_connectivity = weighted_connectivity / (len(subcommunities[subcomm]) * (len(subcommunities[subcomm]) - 1))
                with open(comm_louvain_analysis, 'a') as outFile:
                    outFile.write("s" + str(i + 1) + "\t" + str(weighted_connectivity) + "\t" + txt.rstrip() + "\n")
            else:
                nb_invalid_comm += 1

        print(strftime("%H:%M:%S", localtime()) + ":\t\t" + str(nb_subcomm) + " subcommunities extracted, " + str(nb_added_for_recursion) + " sent to recursion")

        if nb_subcomm + nb_invalid_comm + nb_added_for_recursion == 1:
            print(strftime("%H:%M:%S", localtime()) + ": Done. (safety break)")
            quit()

        i += 1

    print(strftime("%H:%M:%S", localtime()) + ": Done.")
