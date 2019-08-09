""" by Tim Nguyen (7/17/19)
*anytree library: https://anytree.readthedocs.io/en/2.6.0/index.html

This is a solution tree for the subgraph isomorphism problem.
Inherit from Graph. Given a fixed ordering of the template's nodes (equiv classes)
A solution of the subgraph matching problem is a path of this tree from the root to a leaf
We enumerate all the possible isomorphisms this way as well as provide an easy way
to count the total number of isomorphisms.

Attribute:
	- root
	- adj_dictionary (of supernodes?)
	- 
Queries:
	- print_tree				(print the tree in a nicely formatted form)
	- iterate_isomorphisms 		(return an iterator that gives ALL the valid matching)
	- get_isomorphisms_count 	(return a number of total number of isomorphisms)
	- get_signal_nodes			(return a set of all nodes in the world graph participating in some signal)
	- get_min_complete_cand_set	(return a dictionary of 
									"supernode (equiv classes)": min complete cand set )
Methods:
	- add_solution 
"""

from .supernodes import Supernode, SuperTemplateNode
from .partial_match import PartialMatch
from anytree import Node, RenderTree, DoubleStyle 		# we use the anytree library for tree
import math 		# for factorial
from uclasmcode.candidate_structure.logging_utils import log_solutions


class SolutionNode(Node):
	""" A custome node for this problem """
	def __init__(self, sn: Supernode = None, parent=None, name=None):
		self.supernode = sn
		if name is None:
			name = str(sn.name)
		Node.__init__(self, name, parent, supernode=sn)

	def __hash__(self):
		return hash(self.supernode)

	def same_super_node(self, other) -> bool:
		""" Returns whether two SolutionNode has the same supernode """
		# what if other.supernode is not good...
		return self.supernode == other.supernode


class SolutionTree(object):
	""" Solution tree contains a tree representation of solutions to the subgraph isomorphism problem
	This class also provides queries to obtain other information about the solution space of related problems
	"""

	def __init__(self, ordering: [SuperTemplateNode], name_dict: {int: str} = None, count_only=False):
		""" ordering specifies an ordering of the template nodes in form of a list
		ideally should be to minimize the width of the tree """
		self.root = SolutionNode(name="root") 	# this is the main tree
		self.num_isomorphisms = 0 	# counter used to with add
		# the dictionary below stores the nodes at the level matching the ordering
		self.template_candidate_dict = {i: set() for i in ordering}
		self.template_node_ordering = ordering
		self.num_tmplt_nodes = len(self.template_node_ordering)
		self.name_dict = name_dict  # this is world.node_idxs
		self.count_only = count_only

	# ###### QUERIES #########
	def print_tree(self):  # nice fancy function from library
		pass

	def iterate_isomorphisms(self):
		pass

	def get_isomorphisms_count(self):
		return self.num_isomorphisms

	def get_signal_nodes(self):
		""" returns a set of signal nodes """
		return set.union(*list(self.template_candidate_dict.values()))

	def get_min_complete_cand_set(self):
		""" Returns a list of sets"""
		return [(i, j) for i, j in self.template_candidate_dict.items()]

	# ###### METHODS #########
	def add_solution(self, matching: PartialMatch) -> None:
		""" This should add the matching to the main solution tree"""
		assert len(matching) == self.num_tmplt_nodes, "Must have enough matches"
		match_dict = matching.get_matches()
		log_solutions(str(matching))
		# first we update the counter
		self._increase_counter(match_dict)
		# now we add the solution to the tree
		if not self.count_only:
			self._append_to_tree(match_dict)

	# # PRIVATE
	def _append_to_tree(self, match_dict: {SuperTemplateNode: Supernode}) -> None:
		""" Given a match from template nodes to set of world node
		Append it to tree and add appropriate nodes to dictionary"""
		prev_node = self.root  # we start at the root
		# then we traverse the tree in the same order we were given with
		for i in range(self.num_tmplt_nodes):  # iterate over all tmplt nodes
			curr_tmplt_node = self.template_node_ordering[i]  # the current node
			match = match_dict[curr_tmplt_node]  # we change the matching set to a supernode
			# given the hash is correct, we should add each match only once
			self.template_candidate_dict[curr_tmplt_node].add(match)
			# now we check if there's a child already on this path
			child_flag = False
			for child in prev_node.children:  # child is a SolutionNode(match)
				if match == child.supernode:  # if it exists already
					child_flag = True
					prev_node = child  # we want to keep the same child for next layer
					break
			if not child_flag:  # if there's no child, create one and set it as that for next run
				prev_node = SolutionNode(
					match, name=str(match.name),
					parent=prev_node)

	def _increase_counter(self, match_dict: {Supernode: set}) -> None:
		""" Given a matching in a form of dictionary, we increase the isomorphism count appropriately"""
		temp = 1
		for sn, matches in match_dict.items():
			temp *= math.factorial(len(matches))
		self.num_isomorphisms += temp

	# ### UTILITIES

	def __str__(self):
		"""
		:return: a nicely printed tree format of the solution tree
		"""
		if self.num_isomorphisms == 0:
			return "UNSATISFIABLE PROBLEM: NO ISOMORPHISM FOUND."
		result = f"ISOMORPHISM COUNT: {self.get_isomorphisms_count()}. TEMPLATE NODES ORDER:\n"
		result += str([str(i.name) for i in self.template_node_ordering]) + "\n"
		for pre, _, node in RenderTree(self.root, style=DoubleStyle):
			result += ("%s%s\n" % (pre, node.name))
		return result

	def __repr__(self):
		""" Returns the num_isomorphisms, template_candidate_dict, and
		template_node_ordering"""
		result = "Num isomorphisms: {}".format(self.num_isomorphisms)
		result += "\nTemplate node ordering: {}".format(str([i for i in self.template_node_ordering]))
		result += "\nTemplate candidate dictionary: {}".format(
			str({str(u): str(v) for u, v in self.template_candidate_dict.items()}))
		return result

	def __len__(self):
		""" Returns the total number of isomorphisms i.e. leaf nodes"""
		return self.num_isomorphisms
