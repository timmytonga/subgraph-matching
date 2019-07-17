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

from .supernodes import Supernode
from .partial_match import PartialMatch
from anytree import Node, RenderTree 		# we use the anytree library for tree


class SolutionTree:
	""" Solution tree contains a tree representation of solutions to the subgraph isomorphism problem
	This class also provides queries to obtain other information about the solution space of related problems
	"""
	def __init__(self, ordering=None):
		self.root = Node("root") 	# this is the main tree

	# ###### QUERIES #########
	def print_tree(self):
		pass

	def iterate_isomorphisms(self):
		pass

	def get_isomorphisms_count(self):
		pass

	def get_signal_nodes(self):
		pass

	def get_min_complete_cand_set(self):
		pass

	# ###### METHODS #########
	def add_solution(self, matching: PartialMatch):
		""" This should add the matching to the main solution tree"""
		pass
