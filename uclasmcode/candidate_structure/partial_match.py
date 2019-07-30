""" by Tim Nguyen (7/17/19)
PartialMatch class: Data structure for matching algorithm to modify, update, restore partial matches """


from .candidate_structure import SuperTemplateNode
from .simple_utils import print_info
from .supernodes import Supernode


class PartialMatch(object):
    """ This data structure stores the matching between template nodes and world nodes
     It provides utilities like:
        - rm_last_match (for the DFS tree to minimize space)
        - rm_match      (for removing a match)
        - get_matches   (returns a dictionary of Supernode and matched world node)
        - add_match     (add a new match and keeps track of the order of adding) """

    def __init__(self):
        """ """
        # dictionary of Supernode to a set of matched nodes of same size as supernode
        # #Note that __hash__ is defined in Supernode
        self.matches = {}  # {SuperTemplateNode: Supernode}
        self.node_stack = []
        self.already_matched_world_nodes = set()  # for checking alldiff

    # ========== METHODS ===========
    def rm_last_match(self) -> (SuperTemplateNode, Supernode):
        """ pop the last match from the stack and returns it """
        return self.matches.pop(self.node_stack.pop())

    def rm_match(self, name_of_node: SuperTemplateNode) -> None:
        """ Given a supernode remove it from the matches
            can be a risky method """
        assert name_of_node in self.matches, "PartialMatch.rm_match: Trying to remove a node (%s) that has not \
                                            been matched. "
        self.matches.pop(name_of_node)

    def add_match(self, supernode: SuperTemplateNode, candidate_node: Supernode):
        """ add the new_match to the matches. """
        assert supernode not in self.matches, "PartialMatch.add_match: Trying to add an already added node"
        print_info(f"Adding ({str(supernode)},{str(candidate_node)}) to {str(self)}\n")
        assert len(supernode) == len(candidate_node), "Invalid matching: matching must be a set of equal len"
        # push the new matches onto the stack
        self.node_stack.append(supernode)
        self.matches[supernode] = candidate_node
        self.already_matched_world_nodes.update(candidate_node.get_vertices())

    # =========== QUERIES ==========
    def get_matches(self) -> {SuperTemplateNode: {Supernode}}:
        """ Returns a dictionary of matches of this partial match"""
        return self.matches

    def print_match_stack(self) -> str:
        """ Return a nicely formatted match stack for debugging mainly """
        return str([str(i) for i in self.node_stack])

    # === utils ====
    def __str__(self):
        """ Gives the string of the matched dictionary """
        return str([(str(u), str(v)) for u, v in self.matches.items()])

    def __repr__(self):
        """ Gives some useful info for debugging """
        result = self.print_match_stack()
        result += "\nMatches dictionary: {}".format(
            str({str(u): str(v) for u, v in self.matches.items()}))
        return result

    def __eq__(self, other):    # mainly for debugging
        return self.matches == other.matches and self.node_stack == other.node_stack

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self.matches)
