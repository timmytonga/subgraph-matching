# -*- coding: utf-8 -*-

from utils import data
import uclasm
from filters.counting import count_isomorphisms
import time

import matplotlib.pyplot as plt
plt.switch_backend('agg')

print("Starting data loading")
start_time = time.time()
tmplts, world = data.pnnl_rw_noisy()
tmplt = tmplts[0]
print("Loading took {} seconds".format(time.time()-start_time))


print("Starting filters")
start_time = time.time()
uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)
print("Filtering took {} seconds".format(time.time()-start_time))

# print("Starting isomorphism count")
# start_time = time.time()

# count = count_isomorphisms(tmplt, world)
# print("There are {} isomorphisms.".format(count))
# print("Counting took {} seconds".format(time.time()-start_time))

tmplt.plot()
plt.savefig("pnnl_rw_noisy")

# Create SignalNodes.txt and SignalEdges.txt
# Rank candidates by how many other candidates there are for their best template node
cand_ranks = {}
# List of all candidates that are candidates for at least one template node
valid_cands = []
# Order template nodes by their number of candidates, low to high
ordered_tmplt_nodes = sorted(tmplt.nodes,
        key=lambda x, cand_sets=tmplt.candidate_sets: len(cand_sets[x]))
with open('NoisySignalNodes.txt','w') as fout:
    for tmplt_node in ordered_tmplt_nodes:
        for cand in tmplt.candidate_sets[tmplt_node]:
            if cand not in valid_cands:
                valid_cands += [cand]
                cand_ranks[cand] = len(tmplt.candidate_sets[tmplt_node])
                fout.write(cand+"\n")
    for cand in tmplt.candidates:
        if cand not in valid_cands:
            fout.write(cand+"\n")

# Load edgelist with IDs
el_tuples = []
import csv
with open('/s2/scr/reu_data/darpa_maa/data/PNNL/VRW/NoisyComposite.csv','r') as fin:
    reader = csv.reader(fin)
    next(reader)
    for line in reader:
        # Format: source, channel, dest, edge ID
        el_tuples += [(line[0], line[1], line[2], line[3])]

# List of all edges where both source and destination are valid candidates
valid_el_tuples = []
for el_tuple in el_tuples:
    if el_tuple[0] in valid_cands and el_tuple[2] in valid_cands:
        valid_el_tuples += [el_tuple]

# Sort edges by the product of the ranking of their endpoints
ranked_el_tuples = sorted(valid_el_tuples,
                          key=lambda el_tuple, cand_ranks=cand_ranks:
                          cand_ranks[el_tuple[0]]*cand_ranks[el_tuple[2]])
written_edges = []
with open('NoisySignalEdges.txt','w') as fout:
    for el_tuple in ranked_el_tuples:
        fout.write(el_tuple[3]+"\n")
        written_edges += [el_tuple[3]]
    for el_tuple in el_tuples:
        if el_tuple[3] not in written_edges:
            fout.write(el_tuple[3]+"\n")
            written_edges += [el_tuple[3]]
