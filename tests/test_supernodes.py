""" Test basic supernodes """

from uclasmcode.candidate_structure.supernodes import Supernode

def test_create():
    s = Supernode([1,2])
    t = Supernode([2,1])
    u = Supernode([2,3,4])
    assert s == t
    assert not s != t
    assert s != u


def test_eq():
    assert Supernode([1,2,3]) == Supernode([2,1,3])
    assert Supernode([3,2,1]) == Supernode({3,2,1})
    assert Supernode([2]) == Supernode(2)
    assert Supernode([2,3,1]) in {Supernode({1,2,3})}
    t = {Supernode([2,3,4]): 'hello', Supernode({4,5,6}): 'world'}
    assert t[Supernode({4,5,6})] == 'world'



