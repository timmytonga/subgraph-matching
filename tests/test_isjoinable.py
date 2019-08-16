import pytest

from uclasmcode import equivalence_partition
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


def test_isjoinable0():
    """ Test on B0 """
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
    with pytest.raises(AssertionError):
        assert not is_joinable(pm, cs, snC, mC)
    pm.rm_last_match()
    print(pm)
    assert is_joinable(pm, cs, snC, mC)
    pm.add_match(snC, mC)

    assert not is_joinable(pm2, cs, snA, mC)
    assert not is_joinable(pm2, cs, snA, mF)
    assert is_joinable(pm2, cs, snC, mC)
    pm2.add_match(snC, mC)
    assert is_joinable(pm2, cs, snA, mA)
    with pytest.raises(AssertionError):
        assert not is_joinable(pm2, cs, snC, mF)
    assert not is_joinable(pm2, cs, snA, mC)
    pm2.add_match(snA, mA)
    with pytest.raises(AssertionError):
        assert not is_joinable(pm2, cs, snC, mC)


def test_isjoinable1():
    """ Test for B1"""
    pm = PartialMatch()
    snA = cs1.get_supernode_by_name('A')
    snC = cs1.get_supernode_by_name('C')  # a single (trivial) node
    snE = cs1.get_supernode_by_name('E')
    snD = cs1.get_supernode_by_name('D')

    mA = Supernode([0, 4])
    mC = Supernode([1])
    mA2 = Supernode([4, 0])
    mC2 = Supernode(2)
    mE = Supernode(3)  # node 5
    assert is_joinable(pm, cs1, snA, mA)
    assert is_joinable(pm, cs1, snA, mA2)
    pm.add_match(snA, mA)
    assert is_joinable(pm, cs1, snC, mC)
    assert is_joinable(pm, cs1, snC, mC2)
    assert is_joinable(pm, cs1, snD, mC)
    assert not is_joinable(pm, cs1, snE, mC)
    assert is_joinable(pm, cs1, snE, mE)
    pm.add_match(snC, mC)
    assert is_joinable(pm, cs1, snD, mC2)
    assert not is_joinable(pm, cs1, snD, mC)
    pm.add_match(snD, mC2)
    assert is_joinable(pm, cs1, snE, mE)
    pm.add_match(snE, mE)
    with pytest.raises(AssertionError):
        assert not is_joinable(pm, cs1, snE, mC)
    pm.rm_last_match()
    assert is_joinable(pm, cs1, snE, mE)
    pm.rm_last_match()
    assert is_joinable(pm, cs1, snD, mC2)
    assert not is_joinable(pm, cs1, snD, mC)
    pm.rm_last_match()  # back to only A
    assert is_joinable(pm, cs1, snC, mC)
    assert is_joinable(pm, cs1, snC, mC2)
    assert is_joinable(pm, cs1, snD, mC)
    assert not is_joinable(pm, cs1, snE, mC)
    assert is_joinable(pm, cs1, snE, mE)


if __name__ == "__main__":
    test_isjoinable0()
    test_isjoinable1()
