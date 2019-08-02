from uclasmcode.utils import data
import uclasmcode.uclasm as uclasm
import time
from uclasmcode import equivalence_partition
from uclasmcode.candidate_structure.find_isomorphisms import *
from uclasmcode.candidate_structure.logging_utils import print_stats, print_info
from uclasmcode.candidate_structure import logging_utils
import pickle  # in case we already filter

d = data.ivysys_v7()

# setup logging
logging_utils.set_name("ivysys_v7")
logging_utils.init_logger()

print_info("Loading data...")
st = time.time()
tmplts, world = d
print_info("Took %f seconds to load data" % (time.time() - st))

tmplt = tmplts[0]

print_info("\nPartioning Equiv Classes and Making Candidate Structure")
st = time.time()
equiv_classes = equivalence_partition.partition_multichannel(tmplt.ch_to_adj)
print_info("Took %f seconds to partition and make cs" % (time.time() - st))
print_stats(equiv_classes, tmplt)

cs = None
print_info("Attempting to get cs...")
try:
    cs = pickle.load(open("ivysysv7_candidate_structure.p", "rb"))
    print_info("LOADED saved candidate_structure successfully!")
except FileNotFoundError:
    print_info("\nRunning Cheap Filters")
    st = time.time()
    tmplt, world, candidates = uclasm.run_filters(tmplt, world,
                                                  filters=uclasm.cheap_filters,
                                                  verbose=True)
    print_info("Took %f seconds to run cheap filters" % (time.time() - st))
    cs = CandidateStructure(tmplt, world, candidates, equiv_classes)
    pickle.dump(cs, open("ivysysv7_candidate_structure.p", "wb"))


print_info("Starting isomorphism count")
start_time = time.time()
sol = find_isomorphisms(cs, verbose=True, debug=True)

# save our precious solution
pickle.dump(sol, open("ivysysv7_solution_tree.p", "wb"))
print_info("There are {} isomorphisms.".format(sol.get_isomorphisms_count()))
print_info("Counting took {} seconds".format(time.time() - start_time))
