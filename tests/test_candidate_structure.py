from uclasmcode import equivalence_partition
from uclasmcode import uclasm
from uclasmcode.candidate_structure.candidate_structure import *
from uclasmcode.utils import data

# set up datasets
tmplts, world = data.tim_test_graph_1()
tmplt = tmplts[0]
tmplt, world, candidates = uclasm.run_filters(tmplt, world,
                                              filters=uclasm.cheap_filters,
                                              verbose=False)
equiv_classes = equivalence_partition.partition_multichannel(tmplt.ch_to_adj)
cs = CandidateStructure(tmplt, world, candidates, equiv_classes)  # cs of b0


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


def test_get_supernode_by_name():
    assert cs.get_supernode_by_name('A') == cs.get_supernode_by_name('B')
    assert cs.get_supernode_by_name('C') == cs.get_supernode_by_name('D')
    assert cs1.get_supernode_by_name('A') == cs1.get_supernode_by_name('B')


def test_supernode_clique_and_candnode_clique():
    for sn in cs.supernodes.values():
        if not sn.is_trivial() and sn.is_clique('1'):
            print(f"Testing {sn}")
            assert cs.supernode_clique_and_cand_node_clique(
                sn, Supernode([0, 4])
            )
            assert not cs.supernode_clique_and_cand_node_clique(
                sn, Supernode([0, 1])
            )


def test_equiv_size_array():
    assert np.all(cs.equiv_size_array == np.array([2, 2, 2, 2]))
    assert np.all(cs1.equiv_size_array == np.array([2, 1, 1, 1, 2]))


def test_check_satisfiability():
    assert cs.check_satisfiability()
    temp = cs.candidates_array.copy()
    cs.candidates_array[0, 0] = False
    assert not cs.check_satisfiability()
    cs.candidates_array = temp
    assert cs.check_satisfiability()
    assert cs1.check_satisfiability()
    temp = cs1.candidates_array.copy()
    cs1.candidates_array[3, 3] = False
    assert not cs1.check_satisfiability()
    cs1.candidates_array = temp


def test_has_cand_edge():
    snA = cs.get_supernode_by_name('A')
    snC = cs.get_supernode_by_name('C')
    mA = Supernode([0, 4])
    mC = Supernode([1, 2])
    mF = Supernode([0, 1])
    assert cs.has_cand_edge((snA, mA), (snC, mC), '1')
    assert not cs.has_cand_edge((snA, mA), (snC, mF), '1')

    snA = cs1.get_supernode_by_name('A')
    snC = cs1.get_supernode_by_name('C')  # a single (trivial) node
    snE = cs1.get_supernode_by_name('E')
    mA = Supernode([0,4])
    mC = Supernode([1])
    mA2 = Supernode([4,0])
    mC2 = Supernode(2)
    mE = Supernode(3)  # node 5
    assert cs1.has_cand_edge((snA, mA), (snC, mC), '0')
    assert cs1.has_cand_edge((snA, mA2), (snC, mC2), '0')
    assert cs1.has_cand_edge((snA, mA), (snE, mE), '1')
    assert not cs1.has_cand_edge((snA, mA), (snE, mE), '0')


def test_superedge_multiplicity():
    snA = cs.get_supernode_by_name('A')
    snC = cs.get_supernode_by_name('C')
    assert cs.get_superedge_multiplicity(snA, snC, '1') == 1

    snA = cs1.get_supernode_by_name('A')
    snC = cs1.get_supernode_by_name('C')  # a single (trivial) node
    assert cs1.get_superedge_multiplicity(snA, snC, '0') == 2
    assert cs1.get_superedge_multiplicity(snA, snC, '1') == 0



