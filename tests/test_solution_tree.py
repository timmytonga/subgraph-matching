""" Testing modules for functions
For use with pytest"""


from uclasmcode.candidate_structure import solution_tree

def test_initializing_tree():
    a = solution_tree.SolutionTree()
    assert a.str() == 'test'

