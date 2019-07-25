from utils import data
import uclasm
import time

import matplotlib.pyplot as plt


print("Starting data loading")
start_time = time.time()
tmplts, world = data.pnnl_rw()
tmplt = tmplts[0]
print("Loading took {} seconds".format(time.time()-start_time))


print("Starting filters")
start_time = time.time()
tmplt, world, candidates = uclasm.run_filters(tmplt, world,
                                              filters=uclasm.all_filters,
                                              verbose=True)
print("Filtering took {} seconds".format(time.time()-start_time))

print("Starting isomorphism count")
start_time = time.time()
count = uclasm.count_isomorphisms(tmplt, world, candidates=candidates)
print("There are {} isomorphisms.".format(count))
print("Counting took {} seconds".format(time.time()-start_time))
