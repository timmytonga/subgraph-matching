from utils import data
import uclasm
import time

tmplts, world = data.ivysys_v5()
tmplt = tmplts[0]

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

import IPython
IPython.embed()
