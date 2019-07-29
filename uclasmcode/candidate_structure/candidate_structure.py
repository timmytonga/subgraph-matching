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
from uclasmcode.uclasm.utils.data_structures import Graph
import numpy as np


class SuperTemplateNode(Supernode):
	""" A class to contain information about the super template nodes
	Each node is an equivalent class and contains additional information
	about clique and connectivity """
	def __init__(self, equiv_class: set or tuple or int, clique_dict: {str: bool} = None):
		Supernode.__init__(self, equiv_class)
		# a dictionary of channel and a number specifying clique: 0 if not a clique
		# 	otherwise a number to indicate the number of edges that form the clique
		#   IMPORTANT: clique_dict will be of type None if the equiv class is trivial
		self.clique_dict = clique_dict

	def is_clique(self, channel) -> bool:
		""" Returns whether this supernode is a clique or not (only relevant for size >1)
		"""
		if self.is_trivial():  # a single node always forms a clique
			return True
		# the check above ensure the access below is valid
		return self.clique_dict[channel] > 0

	def get_root(self) -> int:
		""" This method is for obtaining one node in the supernode
		Since everything is sorted, this method will always return the same value for the same supernode
		and different values for different supernode in the same problem"""
		return self.get_vertices()[0]

	def get_size(self) -> int:
		""" Same as len but maybe easier to understand """
		return len(self)

	def is_trivial(self) -> bool:
		""" Returns whether if self is trivial i.e. equiv class of length 1"""
		return len(self) == 1  # is equivalent to checking self.clique_dict is None


class CandidateStructure(object):
	"""Contains 	supernodes: corresponding to template's nodes (with candidates)
					superedges (between super nodes): corresponding to template's edges
					candidate-edges: between two candidates in two supernodes
						-> exists iff superedge exists and world edge exists between the two candidates """

	# how to match using this candidate structure? --> tree search, ordering, etc. 
	def __init__(
			self, template: Graph, world: Graph,
			candidates: np.array, equiv_classes: [set]
	):
		assert len(equiv_classes) != 0, "Empty equivalent classes!"
		self.tmplt_graph = template  # store references for important info
		self.world_graph = world
		self.candidates_array = candidates
		self.equiv_classes = equiv_classes

		self._supernodes = set()

	@property
	def supernodes(self) -> {SuperTemplateNode}:
		""" Return a set of SuperTemplateNodes that contains extra info than supernode like
		clique and root"""
		for ec in self.equiv_classes:
			self._supernodes.add(SuperTemplateNode(ec, self._get_equiv_class_clique_dict(ec)))
		return self._supernodes

	# matching algorithm should have some good ordering to follow candidate-edges
	# heap sorts only order but how to take into account edge information.... BFS search ordering... 
	# 	obtain neighbor list of current node -> sort and append to order  (how to get neighbors?)

	# ========== METHODS ==========
	def run_cheap_filters(self, partial_match) -> "Some sort of ways to rep. candidates":
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

	def get_candidates(self, supernode):
		""" Returns an iterator of candidates of a given supernode
		Iterates through subsets of nodes for supernodes rather than permutations
		Yields singleton for trivial supernodes """
		# IMPORTANT: must use yield for iterator.... can be complicated wrt storage
		pass

	def get_candidates_count(self, supernode: SuperTemplateNode) -> int:
		""" Returns the number of candidates that supernode has"""
		return int(np.sum(self.candidates_array[supernode.get_root()]))

	def supernode_clique_and_cand_node_clique(self, supernode: SuperTemplateNode, cand_node: Supernode) -> bool:
		""" Returns a bool specifying if the given cand_node satisfy the clique condition of supernode:
		--> for every channel, if the supernode forms a clique with n edges,
		then the cand_node also form a clique with n edges"""
		if supernode.is_trivial():
			return True
		for ch in self.tmplt_graph.channels:
			if supernode.is_clique(ch):  # only check for clique channels
				supernode_submatrix = self._get_submatrix(
					self.tmplt_graph.ch_to_adj[ch], supernode.get_vertices())
				candidate_node_submatrix = self._get_submatrix(
					self.world_graph.ch_to_adj[ch], cand_node.get_vertices())
				if not np.all(candidate_node_submatrix >= supernode_submatrix):
					# if our world graph does not contain a similar clique in that channel
					return False
		# here we passed all channels clique test
		return True

	# ===== helper ======
	def _get_equiv_class_clique_dict(self, ec: set) -> {str: int}:
		""" Given an equivalent class as a set, check if it's a clique in a certain channel
		We can just check any entry """
		assert len(ec) > 0, "Empty equivalent class was passed ?!?!?"
		if len(ec) == 1:  # trivial clique should not access anywhere....
			return None
		result = {}
		get_elem = iter(ec)
		first = next(get_elem)
		second = next(get_elem)
		for ch, adj in self.tmplt_graph.ch_to_adj:
			result[ch] = adj[first, second]  # 0 if not clique and number of edges otherwise
		return result

	@staticmethod
	def _get_submatrix(matrix: np.ndarray, idx: [int]) -> np.ndarray:
		""" Given a matrix and a list of coordinates, return the submatrix corresponding
		to the given coordinates (idx)"""
		return matrix[np.ix_(idx, idx)]
