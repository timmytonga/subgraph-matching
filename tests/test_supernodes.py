""" Test basic supernodes """

from uclasmcode.candidate_structure.supernodes import Supernode

def test_create():
    s = Supernode([1,2])
    assert str(s) == str((1,2))
    t = Supernode([2,1])
    u = Supernode([2,3,4])
    assert s == t
    assert not s != t
    assert s != u


