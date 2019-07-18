"""
Utilities functions for match_subgraph function. Includes:
    - pick_next_candidate
    - is_joinable
    -

"""

from .candidate_structure import CandidateStructure
from .partial_match import PartialMatch
from .supernodes import Supernode


def pick_next_candidate(candidateStruct: CandidateStructure, partial_match: PartialMatch) -> Supernode:
    """ The order changes each match.... """
    pass


def find_good_ordering_template(cs: CandidateStructure) -> [Supernode]:
    """ Gives a good ordering of the template node
    Probably use some ranking function to order the template node """
    pass


def rank_template_node(cs: CandidateStructure, sn: Supernode) -> int:
    """ Given a candidate structure and a supernode, returns a ranking integer
    Formula: degree/#candidates """
    pass