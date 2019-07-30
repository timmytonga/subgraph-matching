from uclasmcode.candidate_structure.partial_match import *


equiv_classes = [0, 1, (2, 3), 4, 5, 6, 7, 8, 9, 10]
template_nodes = [Supernode(i) for i in equiv_classes]
new_match = [{0}, {2}, {4, 5}, {1}, {3}, {6}, {7}, {8}, {9}, {10}]


def create_partial_match(n):
    assert n >= 1
    partial_match = PartialMatch()
    for i in range(n):
        partial_match.add_match(SuperTemplateNode(equiv_classes[i]), Supernode(new_match[i]))
    return partial_match


def test_eq():
    assert create_partial_match(5) == create_partial_match(5)
    assert create_partial_match(10) != create_partial_match(9)


def test_create():
    five_match = create_partial_match(5)  # 5 matches
    four_match = create_partial_match(4)
    five_match.rm_last_match()
    assert five_match.matches == four_match.matches
    assert five_match.node_stack == four_match.node_stack
    four_match.add_match(SuperTemplateNode(equiv_classes[4]),
                         Supernode(new_match[4]))
    assert four_match == create_partial_match(5)
