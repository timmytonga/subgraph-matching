from utils import data
import uclasm
from filters.counting import count_isomorphisms
import time


print("Starting data loading")
start_time = time.time()
tmplts, world = data.pnnl_v4(0)
tmplt = tmplts[0]
print("Loading took {} seconds".format(time.time()-start_time))

# Cheat by giving the answer to the permutable nodes
tmplt.update_node_candidates("9454", ["9454"])
tmplt.update_node_candidates("9443", ["9443"])
tmplt.update_node_candidates("9458", ["9458"])
tmplt.update_node_candidates("9445", ["9445"])
tmplt.update_node_candidates("9440", ["9440"])
tmplt.update_node_candidates("9457", ["9457"])
tmplt.update_node_candidates("9463", ["9463"])
tmplt.update_node_candidates("9464", ["9464"])

print("Starting filters")
start_time = time.time()
uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)
print("Filtering took {} seconds".format(time.time()-start_time))

print("Starting isomorphism count")
start_time = time.time()

count = count_isomorphisms(tmplt, world)*720*2
print("There are {} isomorphisms.".format(count))
print("Counting took {} seconds".format(time.time()-start_time))

assert count == 57139200
