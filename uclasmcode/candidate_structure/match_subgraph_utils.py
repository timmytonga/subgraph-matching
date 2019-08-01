"""
Utilities functions for match_subgraph function. Includes:
    - pick_next_candidate
    - is_joinable
"""

from .candidate_structure import CandidateStructure, SuperTemplateNode
from .partial_match import PartialMatch
from .supernodes import Supernode
from .logging_utils import print_debug


def is_joinable(
        pm: PartialMatch, cs: CandidateStructure, supernode: SuperTemplateNode,
        candidate_node: Supernode) -> bool:
    """ Given a cs structure and a new_match (supernode and candidate_node),
    returns a bool if the new match satisfies isjoinable constraints"""
    # first assure that we are adding a new supernode (assertion because code is not supposed to call)
    assert supernode not in pm.matches, \
        "PartialMatch.is_joinable: Trying to join an existing match"
    assert len(candidate_node) == len(supernode), \
        "PartialMatch.is_joinable: Trying to join a candidate_node of different length"

    # if the intersection is non-trivial i.e. does not satisfy the alldiff constraint
    if set(candidate_node.vertices) & pm.already_matched_world_nodes:
        return False

    # check the clique condition
    if not cs.supernode_clique_and_cand_node_clique(supernode, candidate_node):
        return False

    # check the homomorphism condition
    for channel in cs.channels:
        matched_incoming_nbr = {  # set of incoming nbr that's already matched
            inbr for inbr in cs.get_incoming_neighbors(supernode, channel) \
            if inbr in pm.matches}
        matched_outgoing_nbr = {  # outgoing
            onbr for onbr in cs.get_outgoing_neighbors(supernode, channel) \
            if onbr in pm.matches}
        # for each neighbor, we must have a candidate edge between the two cand nodes
        for inbr in matched_incoming_nbr:
            if not cs.has_cand_edge(  # the order matters here because direction
                    (inbr, pm.matches[inbr]), (supernode, candidate_node), channel):
                return False
        for onbr in matched_outgoing_nbr:
            if not cs.has_cand_edge(
                    (supernode, candidate_node), (onbr, pm.matches[onbr]), channel):
                return False
    return True


class Ordering(object):
    """ A utility class for keeping track of orderings"""

    def __init__(self, cs: CandidateStructure):
        self.cs = cs
        self.initial_ordering = self.find_good_ordering_template()
        assert len(self.initial_ordering) == self.cs.get_supernodes_count()
        self.index = 0

    def get_next_cand(self, pm: PartialMatch) -> SuperTemplateNode:
        """ Given a partial match, return a good next candidate """
        # print_debug("Ordering.index = " + str(self.index))
        to_return = self.initial_ordering[self.index]
        assert to_return not in pm.matches, "DEBUGGING: THIS SHOULD NOT HAPPEN..."
        if to_return in pm.matches:  # why????
            self.index += 1
            to_return = self.initial_ordering[self.index]
        return to_return

    def increment_index(self):
        # print_debug(f"Incrementing ordering index to: {self.index+1}")
        self.index += 1

    def decrement_index(self):
        # print_debug(f"Decrementing ordering index to: {self.index-1}")
        self.index -= 1

    def find_good_ordering_template(self) -> [SuperTemplateNode]:
        """ Gives a good ordering of the template node
        Probably use some ranking function to order the template node """
        # need to build a tuple (SuperTemplateNode, cand_count, degree)
        cand_counts = self.cs.get_supernodes_count()
        degrees = self.cs.get_supernodes_degrees()
        nbr = self.cs.get_supernodes_nbr_count()
        triple = [(sn, cand_counts[sn], degrees[sn], nbr[sn]) for sn in self.cs.supernodes]
        return [i[0] for i in sorted(triple, key=lambda x: (x[1], -x[2], -x[3]))]

    def __str__(self):
        return str([str(i) for i in self.initial_ordering])


def rank_template_node(cs: CandidateStructure, sn: SuperTemplateNode) -> int:
    """ Given a candidate structure and a supernode, returns a ranking integer
    Formula: degree/#candidates """
    return cs.get_candidates_count(sn)
