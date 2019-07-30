import numpy as np
from uclasmcode.candidate_structure.candidate_structure import *
from uclasmcode.utils import data
from uclasmcode import uclasm
from uclasmcode import equivalence_partition


tmplts, world = data.tim_test_graph_1()
tmplt = tmplts[0]
tmplt, world, candidates = uclasm.run_filters(tmplt, world,
                                              filters=uclasm.cheap_filters,
                                              verbose=False)
equiv_classes = equivalence_partition.partition_multichannel(tmplt.ch_to_adj)
cs = CandidateStructure(tmplt, world, candidates, equiv_classes.classes())


def test_get_submatrix():
    y = np.arange(25).reshape(5, 5)
    vertices = [0, 2, 4]
    assert np.all(
        CandidateStructure._get_submatrix(y, vertices) == np.array([[0,  2,  4], [10, 12, 14], [20, 22, 24]]))


def test_create():
    assert cs.get_supernodes_count() == 2
    assert cs.get_template_nodes_count() == 4


def test_supernode_clique_and_candnode_clique():
    for sn in cs.supernodes:
        if sn.is_clique('1'):
            assert cs.supernode_clique_and_cand_node_clique(
                sn, Supernode([0, 4])
            )


