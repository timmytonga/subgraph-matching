from uclasmcode.utils import data
import uclasmcode.uclasm as uclasm
import time
from uclasmcode import equivalence_partition
from uclasmcode.candidate_structure.find_isomorphisms import *
from uclasmcode.candidate_structure.simple_utils import print_stats, print_info

# d = data.pnnl_v6()
# d = data.ivysys_v7()
d = data.gordian_v7()

print_info("Loading data...")
st = time.time()
tmplts, world = d
print_info("Took %f seconds to load data" % (time.time() - st))

print_info("\nRunning Cheap Filters")
st = time.time()
tmplt = tmplts[0]
tmplt, world, candidates = uclasm.run_filters(tmplt, world,
                                              filters=uclasm.cheap_filters,
                                              verbose=False)
print_info("Took %f seconds to run cheap filters" % (time.time() - st))

print_info("\nPartioning Equiv Classes and Making Candidate Structure")
st = time.time()
equiv_classes = equivalence_partition.partition_multichannel(tmplt.ch_to_adj)
cs = CandidateStructure(tmplt, world, candidates, equiv_classes)
print_info("Took %f seconds to partition and make cs" % (time.time() - st))

print_stats(equiv_classes, tmplt)

print_info("Starting isomorphism count")
start_time = time.time()
sol = find_isomorphisms(cs, verbose=True, debug=False)
print_info("There are {} isomorphisms.".format(sol.get_isomorphisms_count()))
print_info("Counting took {} seconds".format(time.time() - start_time))
