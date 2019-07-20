""" Testing modules for functions
For use with pytest"""


from uclasmcode.candidate_structure.solution_tree import *
from uclasmcode.candidate_structure.supernodes import *

def test_initializing_tree():
    a = SolutionTree([1,2,3])


def test_add_solution():
    # initialize tree
    template_nodes = [0, 1, (2, 3), 4]
    st = SolutionTree([Supernode(i) for i in template_nodes])
    st.root = SolutionNode(name="root")
    s0 = SolutionNode(Supernode(0), parent=st.root)
    s1 = SolutionNode(Supernode(1), parent=s0)
    s2 = SolutionNode(Supernode(2), parent=s0)
    s3 = SolutionNode(Supernode([3, 4]), parent=s1)
    s4 = SolutionNode(Supernode([3, 4]), parent=s2)
    s5 = SolutionNode(Supernode(5), parent=s3)
    s6 = SolutionNode(Supernode(6), parent=s3)
    s7 = SolutionNode(Supernode(5), parent=s4)


