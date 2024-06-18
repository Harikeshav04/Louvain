from ast import literal_eval

def convert_to_undirected(input_file, output_file):
    try:
        inFile = open(input_file, 'r')
        
        min_node = float('inf')
        max_node = float('-inf')
        edges = {}

        # Read input file and process edges
        for line in inFile:
            temp_array = line.rstrip().split("\t")
            node1 = literal_eval(temp_array[0])
            node2 = literal_eval(temp_array[1])
            weight = literal_eval(temp_array[2])
            edges[f"{node1}-{node2}"] = weight
            if node1 > max_node:
                max_node = node1
            if node1 < min_node:
                min_node = node1
            if node2 > max_node:
                max_node = node2
            if node2 < min_node:
                min_node = node2
        
        inFile.close()

        # Write output to the specified file
        with open(output_file, 'w') as outFile:
            for i in range(min_node, max_node + 1):
                for j in range(i + 1, max_node + 1):
                    weight = 0.0
                    edge1 = f"{i}-{j}"
                    edge2 = f"{j}-{i}"
                    if edge1 in edges:
                        weight += edges[edge1]
                    if edge2 in edges:
                        weight += edges[edge2]
                    if weight > 0:
                        outFile.write(f"{i}\t{j}\t{weight / 2}\n")

        print(f"Conversion completed. Output saved to '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except IOError as e:
        print(f"Error: Unable to open or write to file '{output_file}': {e}")

# Example usage:
if __name__ == "__main__":
    # Example input and output file paths
    input_files = [
        "d:/Harikeshav/Networks/Test3/final_code/code/Sample_dig.txt",
        # Add more input file paths as needed
    ]

    output_files = [
        "d:/Harikeshav/Networks/Test3/final_code/data/subchallenge1/Sample_undig.txt",
        # Corresponding output file paths for each input file
    ]

    # Process each pair of input and output files
    for i in range(len(input_files)):
        convert_to_undirected(input_files[i], output_files[i])
