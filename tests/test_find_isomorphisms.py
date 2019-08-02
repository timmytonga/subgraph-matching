from uclasmcode.utils import data
from uclasmcode import equivalence_partition
from uclasmcode.candidate_structure.candidate_structure import *
from uclasmcode.candidate_structure.find_isomorphisms import *

tmplts, world = data.tim_test_graph_1()
tmplt = tmplts[0]
tmplt, world, candidates = uclasm.run_filters(
	tmplt, world, filters=uclasm.cheap_filters, verbose=False)
equiv_classes = equivalence_partition.partition_multichannel(tmplt.ch_to_adj)
cs = CandidateStructure(tmplt, world, candidates, equiv_classes)

tmplts1, world1 = data.tim_test_graph_1(1)
tmplt1 = tmplts1[0]
tmplt1, world1, candidates1 = uclasm.run_filters(
	tmplt1, world1, filters=uclasm.cheap_filters, verbose=False)
equiv_classes1 = equivalence_partition.partition_multichannel(tmplt1.ch_to_adj)
cs1 = CandidateStructure(tmplt1, world1, candidates1, equiv_classes1)


# tmplts2, world2 = data.pnnl_v6()
# tmplt2 = tmplts[0]
# tmplt2, world2, candidates2 = uclasm.run_filters(
# 	tmplt2, world2, filters=uclasm.cheap_filters, verbose=False)
# equiv_classes2 = equivalence_partition.partition_multichannel(tmplt2.ch_to_adj)
# cs2 = CandidateStructure(tmplt2, world2, candidates2, equiv_classes2)


def test_find_isomorphism0():
	sol = find_isomorphisms(cs, False, False)
	assert sol.get_isomorphisms_count() == 12


def test_find_isomorphism1():
	sol = find_isomorphisms(cs1, True, True)
	assert sol.get_isomorphisms_count() == 4

#
# def test_find_iso_pnnlv6():
# 	sol = find_isomorphisms(cs2)
# 	assert sol.get_isomorphisms_count() == 1152
