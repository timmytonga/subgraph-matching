from utils import data
import uclasm
import time
import matplotlib.pyplot as plt
import equivalence_partition

tmplts, world = data.pnnl_v6(0)
tmplt  = tmplts[0]

result = {} # stores 'ch': equivalence classes
nodes = range(0,74)
graph = tmplt
for ch, sparse_mat in graph.ch_to_adj.items():
    adj_matrix = sparse_mat.toarray() # this might be too big... 
    result[ch] = equivalence_partition.partition_vertices(nodes, adj_matrix)
    adj_matrix = tmplt.ch_to_adj['5'].toarray()
