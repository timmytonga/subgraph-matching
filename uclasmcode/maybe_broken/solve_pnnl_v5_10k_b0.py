from utils import data
import uclasm
from filters.counting import count_isomorphisms
import time


print("Starting data loading")
start_time = time.time()
tmplts, world = data.pnnl_v5(0, model="10K")
tmplt = tmplts[0]
print("Loading took {} seconds".format(time.time()-start_time))

print("Starting filters")
start_time = time.time()
uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)
print("Filtering took {} seconds".format(time.time()-start_time))

# print("Starting isomorphism count")
# start_time = time.time()
# 
# count = count_isomorphisms(tmplt, world)*720*2
# print("There are {} isomorphisms.".format(count))
# print("Counting took {} seconds".format(time.time()-start_time))

# assert count == 57139200
