import os
current_directory = os.path.dirname(os.path.abspath(__file__))
relative_dir_louvain = "./generic/src/"
dir_louvain = os.path.join(current_directory, relative_dir_louvain)



networks_in = ["Sample_undig_normalised_allValidCommunities.txt"]

networks_out = ["Sample_undig_final.txt"]
for i in range(0,len(networks_in)):
    inFile = open(dir_louvain+networks_in[i],'r')
    outFile = open(dir_louvain+networks_out[i],'w')
    j=1
    for line in inFile:
        ID = line.rstrip().split("\t")[0]
        outFile.write(str(j)+line[len(ID):])
        j+=1
    inFile.close()
    outFile.close()

