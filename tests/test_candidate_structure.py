from uclasmcode.candidate_structure.candidate_structure import *
from uclasmcode import uclasm
from uclasmcode.candidate_structure.candidate_structure import *
from uclasmcode.utils import data

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


def test_get_submatrix():
    y = np.arange(25).reshape(5, 5)
    vertices = [0, 2, 4]
    assert np.all(
        CandidateStructure._get_submatrix(y, vertices) == np.array([[0,  2,  4], [10, 12, 14], [20, 22, 24]]))


def test_create():
    assert cs.get_supernodes_count() == 2
    assert cs.get_template_nodes_count() == 4
    assert cs1.get_template_nodes_count() == 5
    assert cs1.get_supernodes_count() == 4


def test_supernode_clique_and_candnode_clique():
    for sn in cs.supernodes:
        if not sn.is_trivial() and sn.is_clique('1'):
            print(f"Testing {sn}")
            assert cs.supernode_clique_and_cand_node_clique(
                sn, Supernode([0, 4])
            )
            assert not cs.supernode_clique_and_cand_node_clique(
                sn, Supernode([0, 1])
            )

