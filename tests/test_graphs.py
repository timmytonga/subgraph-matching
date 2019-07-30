from uclasmcode.utils import data
import time

print("Starting data loading")
start_time = time.time()
tmplts, world = data.tim_test_graph_1()
tmplt = tmplts[0]
print("Loading took {} seconds".format(time.time()-start_time))

