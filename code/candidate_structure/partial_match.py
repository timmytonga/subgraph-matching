""" by Tim Nguyen (7/17/19)
PartialMatch class: Data structure for matching algorithm to modify, update, restore partial matches """


from .supernodes import Supernode


class PartialMatch:
    """ This data structure stores the matching between template nodes and world nodes
     It provides utilities like:
        - rm_last_match (for the DFS tree to minimize space)
        - rm_node (to remov
        - get_matched_dictionary (returns a dictionary of Supernode and matched world node)
        - add_match     (add a new match and keeps track of the order of adding) """

    def __init__(self):
        # dictionary of Supernode to a set of matched nodes of same size as supernode
        # #Note that __hash__ is defined in Supernode
        self.matches = {}
        self.node_stack = []

    # ========== METHODS ===========
    def rm_last_match(self):
        pass

    def rm_match(self, name_of_node: Supernode):
        """ Given a supernode remove it from the matches
            can be a risky method """
        assert name_of_node in self.matches, "PartialMatch.rm_match: Trying to remove a node (%s) that has not \
                                            been matched. "
        self.matches.pop(name_of_node)

    def add_match(self, new_match: (Supernode, "world node")):
        """ add the new_match to the matches. this function does not check for constraint but rather blindly adds it
        to the matches. It is up to the user to check before adding """
        pass

    # =========== QUERIES ==========
    def get_matched_dictionary(self):
        return self.matches

    def __str__(self):
        """ Gives the string of the matched dictionary """
        return str(self.matches)

    def is_joinable(self, cs, new_match: (Supernode, "world node")) -> bool:
        """ Given a cs structure and a new_match (tuple of Supernode and world node,
        returns a bool if the new match satisfies the homomorphism and the alldifferent constraints"""
        pass

