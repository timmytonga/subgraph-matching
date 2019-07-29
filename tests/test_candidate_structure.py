import numpy as np
from uclasmcode.candidate_structure.candidate_structure import *


def test_get_submatrix():
    y = np.arange(25).reshape(5, 5)
    vertices = [0, 2, 4]
    assert np.all(
        CandidateStructure._get_submatrix(y, vertices) == np.array([[0,  2,  4], [10, 12, 14], [20, 22, 24]]))


