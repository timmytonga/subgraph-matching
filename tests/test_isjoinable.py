import pytest

from uclasmcode import equivalence_partition
from uclasmcode import uclasm
from uclasmcode.candidate_structure.candidate_structure import *
from uclasmcode.candidate_structure.match_subgraph_utils import is_joinable
from uclasmcode.candidate_structure.partial_match import *
from uclasmcode.utils import data

# set up datasets
tmplts, world = data.tim_test_graph_1()
tmplt = tmplts[0]
tmplt, world, candidates = uclasm.run_filters(tmplt, world,
                                              filters=uclasm.cheap_filters,
                                              verbose=False)
equiv_classes = equivalence_partition.partition_multichannel(tmplt.ch_to_adj)
cs = CandidateStructure(tmplt, world, candidates, equiv_classes)


tmplts1, world1 = data.tim_test_graph_1(1)
tmplt1 = tmplts1[0]
tmplt1, world1, candidates1 = uclasm.run_filters(tmplt1, world1,
                                              filters=uclasm.cheap_filters,
                                              verbose=False)
equiv_classes1 = equivalence_partition.partition_multichannel(tmplt1.ch_to_adj)
cs1 = CandidateStructure(tmplt1, world1, candidates1, equiv_classes1)


def test_isjoinable1():
    # need to build partial match and test joinable
    pm = PartialMatch()
    pm2 = PartialMatch()
    snA = cs.get_supernode_by_name('A')
    snC = cs.get_supernode_by_name('C')
    mA = Supernode([0, 4])
    mC = Supernode([1, 2])
    mF = Supernode([0, 1])
    assert is_joinable(pm, cs, snA, mA)
    pm.add_match(snA, mA)
    assert is_joinable(pm, cs, snC, mC)
    assert not is_joinable(pm, cs, snC, mF)
    with pytest.raises(AssertionError):
        assert not is_joinable(pm, cs, snA, mC)
    pm.add_match(snC, mC)

    assert not is_joinable(pm2, cs, snA, mC)
    assert not is_joinable(pm2, cs, snA, mF)
    assert is_joinable(pm2, cs, snC, mC)
    pm2.add_match(snC, mC)
    assert is_joinable(pm2, cs, snA, mA)
    with pytest.raises(AssertionError):
        assert not is_joinable(pm, cs, snC, mF)
    assert not is_joinable(pm, cs, snA, mC)
    pm2.add_match(snA, mA)



