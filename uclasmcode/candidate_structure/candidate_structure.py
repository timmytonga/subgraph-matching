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

import numpy as np

from uclasmcode.equivalence_partition.equivalence_data_structure import Equivalence
from uclasmcode.uclasm.utils.data_structures import Graph
from .supernodes import Supernode


class SuperTemplateNode(Supernode):
	""" A class to contain information about the super template nodes
	Each node is an equivalent class and contains additional information
	about clique and connectivity """
	def __init__(
			self, equiv_class: set or tuple or int,
			clique_dict: {str: bool} = None, name: str = None, root=None):
		Supernode.__init__(self, equiv_class, name)
		# a dictionary of channel and a number specifying clique: 0 if not a clique
		# 	otherwise a number to indicate the number of edges that form the clique
		#   IMPORTANT: clique_dict will be of type None if the equiv class is trivial
		self.clique_dict = clique_dict
		self._root = root

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
		return self._root

	def get_size(self) -> int:
		""" Same as len but maybe easier to understand """
		return len(self)

	def is_trivial(self) -> bool:
		""" Returns whether if self is trivial i.e. equiv class of length 1"""
		return len(self) == 1  # is equivalent to checking self.clique_dict is None

	def __str__(self):
		return f"SuperTemplateNode({self.name})"

	def __repr__(self):
		return f"SuperTemplateNode{self.vertices} with cliques: {str(self.clique_dict)}"


class CandidateStructure(object):
	"""Contains 	supernodes: corresponding to template's nodes (with candidates)
					superedges (between super nodes): corresponding to template's edges
					candidate-edges: between two candidates in two supernodes
						-> exists iff superedge exists and world edge exists between the two candidates """

	# how to match using this candidate structure? --> tree search, ordering, etc. 
	def __init__(
			self, template: Graph, world: Graph,
			candidates: np.array, equiv_classes: Equivalence
	):
		assert len(equiv_classes) != 0, "Empty equivalent classes!"
		self.tmplt_graph = template  # store references for important info
		self.world_graph = world
		self.candidates_array = candidates
		self.equiv_classes = equiv_classes
		self._supernodes = {}

	@property
	def supernodes(self) -> {SuperTemplateNode}:
		""" Return a set of SuperTemplateNodes that contains extra info than supernode like
		clique and root"""
		if len(self._supernodes) == 0:
			for ec in self.equiv_classes.classes():
				root = self.equiv_classes.compress_to_root(next(iter(ec)))
				self._supernodes[root] = (SuperTemplateNode(
					ec, self._get_equiv_class_clique_dict(ec),
					name=str([self.tmplt_graph.nodes[i] for i in ec]),
					root=root))
		return self._supernodes

	@property
	def channels(self):
		return self.tmplt_graph.channels

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
	def get_incoming_neighbors(self, sn: SuperTemplateNode, channel: str) -> {SuperTemplateNode}:
		""" Given a supernode and a channel,
		returns a set of incoming supernode neighbors in that channel"""
		assert sn in self.supernodes.values()
		result = set()  # a set so we don't add duplicate nodes
		root = sn.get_root()
		adj = self.tmplt_graph.ch_to_adj[channel]
		for pin in np.argwhere(adj[:, root]):
			if not self.in_same_equiv_class(pin[0], root):
				result.add(self.get_supernode_by_idx(pin[0]))
		return result

	def get_outgoing_neighbors(self, sn: SuperTemplateNode, channel: str) -> {SuperTemplateNode}:
		""" Given a supernode,
		returns a set of outgoing supernode neighbors in that channel"""
		assert sn in self.supernodes.values()
		result = set()
		root = sn.get_root()
		adj = self.tmplt_graph.ch_to_adj[channel]
		for pin in np.argwhere(adj[root]):
			if not self.in_same_equiv_class(pin[1], root):
				result.add(self.get_supernode_by_idx(pin[1]))
		return result

	def has_cand_edge(self, t1: Supernode, t2: Supernode, channel: str) -> bool:
		""" Input: CandidateStructure.has_edge( (t_i,u), (t_j,v) )
		Output: Returns True if (t_i, t_j) not in E(T) or
							if (t_i, t_j) in E(T) and (u,v) in E(W)
				Returns False if (t_i, t_j) in E(T) and (u,v) not in E(W)"""
		pass

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
		assert len(supernode) == len(cand_node), "Supernode and candnode must have same length!"
		if supernode.is_trivial():
			return True
		for ch in self.tmplt_graph.channels:
			if supernode.is_clique(ch):  # only check for clique channels
				supernode_submatrix = self._get_submatrix(
					self.tmplt_graph.ch_to_adj[ch].A, supernode.get_vertices())
				candidate_node_submatrix = self._get_submatrix(
					self.world_graph.ch_to_adj[ch].A, cand_node.get_vertices())
				if not np.all(candidate_node_submatrix >= supernode_submatrix):
					# if our world graph does not contain a similar clique in that channel
					return False
		# here we passed all channels clique test
		return True

	# ===== helper ======
	def in_same_equiv_class(self, t1: int, t2: int) -> bool:
		""" Given two template nodes, return a bool specifying whether they
		are in the same supernode or not i.e. same equivalent class """
		return self.equiv_classes.in_same_class(t1, t2)

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
		for ch, adj in self.tmplt_graph.ch_to_adj.items():
			result[ch] = adj[first, second]  # 0 if not clique and number of edges otherwise
		return result

	@staticmethod
	def _get_submatrix(matrix: np.ndarray, idx: [int]) -> np.ndarray:
		""" Given a matrix and a list of coordinates, return the submatrix corresponding
		to the given coordinates (idx)"""
		return matrix[np.ix_(idx, idx)]

	def get_supernode_by_name(self, name: str) -> SuperTemplateNode:
		""" Given a name of a node, return the supernode"""
		idx = self.tmplt_graph.node_idxs[name]
		return self.get_supernode_by_idx(idx)

	def get_supernode_by_idx(self, idx: int) -> SuperTemplateNode:
		""" Given the index of a node, return the supernode"""
		return self.supernodes[self.equiv_classes.compress_to_root(idx)]

	def __str__(self):
		return str(self.equiv_classes)  # for now
