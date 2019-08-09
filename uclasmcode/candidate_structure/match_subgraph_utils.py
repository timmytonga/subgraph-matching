"""
Utilities functions for match_subgraph function. Includes:
    - pick_next_candidate
    - is_joinable
"""

from .candidate_structure import CandidateStructure, SuperTemplateNode
from .partial_match import PartialMatch
from .supernodes import Supernode
import numpy as np
from collections import deque
from .logging_utils import print_debug, print_info, print_warning


def is_joinable(
        pm: PartialMatch, cs: CandidateStructure, supernode: SuperTemplateNode,
        candidate_node: Supernode) -> bool:
    """ Given a cs structure and a new_match (supernode and candidate_node),
    returns a bool if the new match satisfies isjoinable constraints"""
    # first assure that we are adding a new supernode (assertion because code is not supposed to call)
    assert supernode not in pm.matches, \
        "PartialMatch.is_joinable: Trying to join an existing match"
    assert len(candidate_node) == len(supernode), \
        f"PartialMatch.is_joinable: Trying to join a candidate_node of different length\n" \
            f"\t\tcandidate_node={repr(candidate_node)} and supernode={repr(supernode)}"

    # if the intersection is non-trivial i.e. does not satisfy the alldiff constraint
    if set(candidate_node.name) & pm.already_matched_world_nodes:
        # print_debug(f"ISJOINABLE(29): FAILED ALLDIFF")
        return False

    # check the clique condition
    if not cs.supernode_clique_and_cand_node_clique(supernode, candidate_node):
        # print_debug(f"ISJOINABLE(34): FAILED CLIQUE")
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
                # print_debug(f"ISJOINABLE(49): FAILED HOMO IN {inbr.name} {channel}")
                return False
        for onbr in matched_outgoing_nbr:
            if not cs.has_cand_edge(
                    (supernode, candidate_node), (onbr, pm.matches[onbr]), channel):
                # print_debug(f"ISJOINABLE(29): FAILED HOMO OUT")
                return False
    return True


class Ordering(object):
    """ A utility class for keeping track of orderings"""

    def __init__(self, cs: CandidateStructure):
        self.cs = cs
        # self.distances = {sn: self._get_distances_dict_from(sn) for sn in self.cs.supernodes.values()}
        self.initial_ordering = self.distance_ordering()
        assert len(self.initial_ordering) == self.cs.get_supernodes_count()
        self.index = 0

    # def get_next_cand(self, pm: PartialMatch) -> SuperTemplateNode:
    #     """ Given a partial match, return a good next candidate """
    #     to_return = self.initial_ordering[self.index]
    #     assert to_return not in pm.matches, "DEBUGGING: THIS SHOULD NOT HAPPEN..."
    #     return to_return

    def get_next_cand(self, pm: PartialMatch) -> SuperTemplateNode:
        """ Given a partial match, return a good next candidate """
        cand_counts = self.cs.get_supernodes_cand_count()
        # nbr = self.cs.get_supernodes_nbr_count()
        #
        # if distance:
        #     try:
        #         lastsn, _ = pm.get_last_match()
        #     except TypeError:
        #         return self.initial_ordering[0]
        #     distance_lastsn = self.distances[lastsn]
        #     # get the minimum candidate count, non-matched supernode
        #     toreturn = min(
        #         [(sn, cand_counts[sn], distance_lastsn[sn]) for sn in self.cs.supernodes.values() if sn not in pm.matches],
        #         key=lambda x: (x[1], x[2]))[0]
        #     return toreturn

        toreturn = min(
            [(sn, cc) for sn, cc in cand_counts.items() if sn not in pm.matches],
            key=lambda x: x[1])[0]
        return toreturn

    def increment_index(self):
        # print_debug(f"Incrementing ordering index to: {self.index+1}")
        self.index += 1

    def decrement_index(self):
        # print_debug(f"Decrementing ordering index to: {self.index-1}")
        self.index -= 1

    def cand_count_ordering(self) -> [SuperTemplateNode]:
        """ Gives an ordering of the template node
        according to the cand count"""
        cand_counts = self.cs.get_supernodes_cand_count()
        degrees = self.cs.get_supernodes_degrees()
        nbr = self.cs.get_supernodes_nbr_count()
        triple = [(sn, cand_counts[sn], len(sn), degrees[sn], nbr[sn]) for sn in self.cs.supernodes.values()]
        sorted_triple = sorted(triple, key=lambda x: (x[1], -x[2], -x[3], -x[4]))
        print_debug(f"CAND_COUNT ORDERING: {self._print_order_nicely2(sorted_triple)}")
        return [i[0] for i in sorted_triple]

    def distance_ordering(self) -> [SuperTemplateNode]:
        """ Get a good start node and compute the distance of the other nodes from
        that start node. Use that as the primary metric and we order the rest by their cand_counts"""
        # build a list (sn, distance_from_start, cand/degree)
        cand_counts = self.cs.get_supernodes_cand_count()
        degrees = self.cs.get_supernodes_degrees()
        nbr = self.cs.get_supernodes_nbr_count()
        scores = {sn: cand_counts[sn] / nbr[sn] for sn in self.cs.supernodes.values()}
        start_node = min(scores.items(), key=lambda x: x[1])[0]
        distances = self._get_distances_dict_from(start_node)
        to_order = [(sn, distances[sn], scores[sn], cand_counts[sn], degrees[sn]) for sn in self.cs.supernodes.values()]
        sorted_to_order = sorted(to_order, key=lambda x: (x[1], x[2], -x[4]))
        print_debug(f"DISTANCE ORDERING: {self._print_order_nicely(sorted_to_order)}")
        return [i[0] for i in sorted_to_order]

    def __str__(self):
        return str([str(i) for i in self.initial_ordering])

    def _get_neighbors(self, sn: SuperTemplateNode) -> {SuperTemplateNode}:
        """ Returns a set of neighbors of a given supernode"""
        root = sn.get_root()
        nbrs = set()
        for pin in np.argwhere(self.cs.tmplt_graph.sym_composite_adj[root]):
            if not self.cs.in_same_equiv_class(pin[1], root):
                nbrs.add(self.cs.get_supernode_by_idx(pin[1]))
        return nbrs

    def _get_distances_dict_from(self, sn: SuperTemplateNode) -> {SuperTemplateNode: int}:
        """ Given a start supernode sn, returns a dictionary containing the
        distance of the other supernodes...."""
        if not self.cs.tmplt_graph.is_connected():
            print_warning("TEMPLATE GRAPH NOT CONNECTED! DO NOT USE DISTANCE. HAVE NOT SUPPORTED")

        visited = {sn}
        result = {sn: 0}
        queue = deque()
        queue.append(sn)
        while len(queue) != 0:
            v = queue.popleft()
            for nbr in self._get_neighbors(v):  # distance
                if nbr not in visited:
                    result[nbr] = result[v]+1
                    visited.add(nbr)
                    queue.append(nbr)
        return result

    @staticmethod
    def _print_order_nicely(l: [(SuperTemplateNode, int, float)]) -> str:
        result = "\n"
        i = 0
        for sn, d, score, cc, deg in l:
            result += f"\t{i}.\t{sn.name}: dist={d}, cand_counts={cc}, score={score}\n"
            i += 1
        return result

    @staticmethod
    def _print_order_nicely2(l: [(SuperTemplateNode, int, int, int, int)]) -> str:
        result = "\n"
        i = 0
        for sn, cand_count, lensn, degree, nbr in l:
            result += f"\t{i}.\t{sn.name}: cand_count={cand_count}, " \
                f"lensn={lensn}, degree={degree}, nbr={nbr}\n"
            i += 1
        return result


def rank_template_node(cs: CandidateStructure, sn: SuperTemplateNode) -> int:
    """ Given a candidate structure and a supernode, returns a ranking integer
    Formula: degree/#candidates """
    return cs.get_candidates_count(sn)
