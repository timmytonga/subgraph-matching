"""Data structure to hold candidate and matching order scheme
	The structure is very similar to the template graph except that each node (called supernode)
	will be an array of vertices and there will be superedges between the nodes corresponding
	to the edges in the template graph (this is where the BFS tree comes from?)

	Also, the candidates in each node will contain edges in each other.
	# should store in this structure? Or should query from the existing world graph 
	An edge between two candidates in two supernodes exists iff a 
	superedge exist in their containing supernodes as well as if there is an edge 
	between those candidates in the world graph


by Tim Nguyen
Last update: 7/17/19 """

from .supernodes import Supernode
from .partial_match import PartialMatch
from uclasm.utils.data_structures import Graph
import numpy as np
from typing import Iterable


class SuperTemplateNode(Supernode):
	""" A class to contain information about the super template nodes
	Each node is an equivalent class and contains additional information
	about clique and connectivity """
	def __init__(self, equiv_class, clique_dict: {str: bool}):
		self.supernode = Supernode.__init__(equiv_class)
		# a dictionary of channel and a bool specifying if this equiv class forms a clique in that channel
		self.clique_dict = clique_dict

	def is_clique(self, channel) -> bool:
		""" Returns whether this supernode is a clique or not (only relevant for size >1)
		"""
		return self.clique_dict[channel]

	def get_root(self) -> int:
		""" This method is for obtaining one node in the supernode
		Since everything is sorted, this method will always return the same value for the same supernode
		and different values for different supernode in the same problem"""
		return self.get_vertices()[0]

	def get_size(self) -> int:
		""" Same as len but maybe easier to understand """
		return len(self)


class CandidateStructure(object):
	"""Contains 	supernodes: corresponding to template's nodes (with candidates)
					superedges (between super nodes): corresponding to template's edges
					candidate-edges: between two candidates in two supernodes
						-> exists iff superedge exists and world edge exists between the two candidates """

	# how to match using this candidate structure? --> tree search, ordering, etc. 
	def __init__(
			self, template: Graph, world: Graph,
			candidates: np.array, equiv_classes: set
	):
		assert len(equiv_classes) != 0, "Empty equivalent classes!"
		self.tmplt_graph = template  # store references for important info
		self.world_graph = world
		self.candidates_array = candidates
		self.supernodes = {SuperTemplateNode(i) for i in equiv_classes}

	# matching algorithm should have some good ordering to follow candidate-edges
	# heap sorts only order but how to take into account edge information.... BFS search ordering... 
	# 	obtain neighbor list of current node -> sort and append to order  (how to get neighbors?)

	# ========== METHODS ==========
	def run_cheap_filters(self, partial_match: PartialMatch) -> "Some sort of ways to rep. candidates":
		""" Not sure if we should modify the current structure directly and store the changes
			somewhere for restore or if we should make a new structure entirely """
		pass

	def restore_changes(self):
		""" Not sure what this does yet but we might need to restore some changes say by the filters """
		pass

	# ========== QUERIES ==========
	def has_cand_edge(self, t_u: (SuperTemplateNode, int), t_v: (SuperTemplateNode, int), channel: str or int) -> bool:
		""" Input: CandidateStructure.has_edge( (t_i,u), (t_j,v) )
		Output: Returns True if (t_i, t_j) not in E(T) or
							if (t_i, t_j) in E(T) and (u,v) in E(W)
				Returns False if (t_i, t_j) in E(T) and (u,v) not in E(W)"""
		if self.has_super_edge(t_u[0], t_v[0], channel):
			pass  # TODO


	def has_super_edge(self, t1: SuperTemplateNode, t2: SuperTemplateNode, channel: str or int) -> bool:
		""" Returns whether two SuperTemplateNode has an edge in a specific channel in the template graph
		O(1) """
		return self.tmplt_graph.ch_to_adj[channel][t1.get_root(), t2.get_root()] > 0

	def get_supernodes_count(self):
		"""Return the total number of super nodes in the candidate structure.
		Should be the same as the number of equivalent classes """
		return len(self.supernodes)

	def get_template_nodes_count(self):
		"""Return the total number of template node.
		Should be the same as the size of the union of all nodes in the supernodes"""
		return self.tmplt_graph.n_nodes

	def get_candidates(self, supernode) -> Iterable[{int}]:
		""" Returns an iterator of candidates of a given supernode
		Iterates through subsets of nodes for supernodes rather than permutations
		Yields singleton for trivial supernodes """
		# IMPORTANT: must use yield for iterator.... can be complicated wrt storage
		pass

	def get_candidates_count(self, supernode: SuperTemplateNode) -> int:
		""" Returns the number of candidates that supernode has"""
		return int(np.sum(self.candidates_array[supernode.get_root()]))
