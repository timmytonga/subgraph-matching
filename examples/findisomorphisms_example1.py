from uclasmcode.utils import data
import uclasmcode.uclasm as uclasm
import time
from uclasmcode import equivalence_partition
from uclasmcode.candidate_structure.find_isomorphisms import *
from uclasmcode.candidate_structure.logging_utils import print_stats

# d = data.pnnl_v6()
# d = data.ivysys_v7()
d = data.gordian_v7()

print("Loading data...")
st = time.time()
tmplts, world = d
print("Took %f seconds to load data" % (time.time() - st))

print("\nRunning Cheap Filters")
st = time.time()
tmplt = tmplts[0]
tmplt, world, candidates = uclasm.run_filters(tmplt, world,
                                              filters=uclasm.cheap_filters,
                                              verbose=False)
print("Took %f seconds to run cheap filters" % (time.time() - st))

print("\nPartioning Equiv Classes and Making Candidate Structure")
st = time.time()
equiv_classes = equivalence_partition.partition_multichannel(tmplt.ch_to_adj)
cs = CandidateStructure(tmplt, world, candidates, equiv_classes)
print("Took %f seconds to partition and make cs" % (time.time() - st))

print_stats(equiv_classes, tmplt)

print("Starting isomorphism count")
start_time = time.time()
sol = find_isomorphisms(cs, verbose=True, debug=False)
print("There are {} isomorphisms.".format(sol.get_isomorphisms_count()))
print("Counting took {} seconds".format(time.time() - start_time))
