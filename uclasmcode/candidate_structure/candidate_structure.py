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
from .logging_utils import print_debug
from .supernodes import Supernode, SuperTemplateNode
from itertools import combinations  # for getting all subsets
from uclasmcode import uclasm


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
		self.candidates_array = candidates  # a 2D boolean array of shape (#TemplateNode, #WorldNodes) indicate candidates
		self.equiv_classes = equiv_classes  # store the equivalent classes information to check equiv.

		self.non_trivial_supernodes: {SuperTemplateNode} = set()  # a set of all the nontrivial supernodes (size >1)
		self._supernodes = {}  # a dict storing root: SuperTemplateNode
		# a dict storing the candidates (subsets) of nontrivial supernodes.
		self._non_triv_candidates: {SuperTemplateNode: [Supernode]} = {}
		self._equiv_size_array = []

	def copy(self):
		""" We need to copy the world_graph since tmplt is never modified """
		temp = CandidateStructure(
			self.tmplt_graph, self.world_graph.copy(),
			self.candidates_array.copy(), self.equiv_classes)
		temp._supernodes = self._supernodes
		temp.non_trivial_supernodes = self.non_trivial_supernodes
		temp._non_triv_candidates = self._non_triv_candidates.copy()
		return temp

	@property
	def non_triv_candidates(self) -> {SuperTemplateNode: [Supernode]}:
		""" Dictionary of non trivial supernodes with list of subsets of possible candidates"""
		if len(self._non_triv_candidates) == 0:
			assert len(self.non_trivial_supernodes) != 0, "Supernodes haven't been initialized"
			for sn in self.non_trivial_supernodes:  # this has potential to be empty
				candidates = self._get_cand_list(sn)  # this is a list of idxs of candidates
				self._non_triv_candidates[sn] = list(combinations(candidates, len(sn)))
		return self._non_triv_candidates

	@property
	def supernodes(self) -> {SuperTemplateNode}:
		""" Return a set of SuperTemplateNodes that contains extra info than supernode like
		clique and root"""
		if len(self._supernodes) == 0:
			for ec in self.equiv_classes.classes():
				root = self.equiv_classes.compress_to_root(next(iter(ec)))
				temp = (SuperTemplateNode(
					ec, self._get_equiv_class_clique_dict(ec),
					name=str([self.tmplt_graph.nodes[i] for i in ec]),
					root=root))
				self._supernodes[root] = temp
				if len(ec) > 1:
					self.non_trivial_supernodes.add(temp)
		return self._supernodes

	@property
	def channels(self):
		return self.tmplt_graph.channels

	@property
	def num_world_nodes(self):
		return self.world_graph.n_nodes

	@property
	def equiv_size_array(self):
		"""
		:return: An array of shape tmplt node that contains the size of equiv classes
		"""
		if len(self._equiv_size_array) == 0:
			self._equiv_size_array = np.array(
				[self.equiv_classes.root_size_map[self.equiv_classes.compress_to_root(i)] for i in
				 range(self.tmplt_graph.n_nodes)]
			)
		return self._equiv_size_array

	# matching algorithm should have some good ordering to follow candidate-edges
	# heap sorts only order but how to take into account edge information.... BFS search ordering... 
	# 	obtain neighbor list of current node -> sort and append to order  (how to get neighbors?)
	# ========== METHODS ==========
	def update_candidates(self, match_dict: {SuperTemplateNode: Supernode}) -> None:
		""" Given a match dictionary, update the candidates_array to reflect the matches"""
		for sn, match in match_dict.items():
			# make an np array of shape (len(sn), world.n_nodes) to all False
			toset = (np.zeros((len(sn), self.num_world_nodes), dtype=np.bool))
			toset[:, match.vertices] = True  # set only the matching vertices to True
			# then set the appropriate rows and columns
			self.candidates_array[np.ix_(sn.vertices, range(self.num_world_nodes))] = toset

	def run_cheap_filters(self) -> None:
		""" Not sure if we should modify the current structure directly and store the changes
			somewhere for restore or if we should make a new structure entirely """
		# TODO: Modify filters to only run on root node of supernodes (minor speed up??)
		# TODO: Modify topology filter to take into account of edge multiplicity in supernodes
		# TODO: Neighborhood filter for cliques (union)
		# TODO: topology filter still slow
		_, self.world_graph, self.candidates_array = uclasm.run_filters(
			self.tmplt_graph, self.world_graph,
			candidates=self.candidates_array, filters=uclasm.cheap_filters)

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

	def has_cand_edge(
			self, m1: (SuperTemplateNode, Supernode), m2: (SuperTemplateNode, Supernode),
			channel: str) -> bool:
		""" Given two matches, check if the matching cand_nodes have candidate edge
		Return a bool specifying if there is a candidate edge from t1 to t2
		"""
		t1: SuperTemplateNode = m1[0]
		c1: Supernode = m1[1]
		t2: SuperTemplateNode = m2[0]
		c2: Supernode = m2[1]
		if len(set(c1.vertices) & set(c2.vertices)) > 0:  # cannot have intersecting nodes!
			print_debug(f"CandidateStructure.has_cand_edge: False because {str(c1)} and {str(c2)} has intersecting nodes.")
			return False
		multiplicity_of_super_edge = self.get_superedge_multiplicity(t1, t2, channel)
		if multiplicity_of_super_edge == 0:
			print_debug(f"has_cand_edge: False because no superedge between {str(t1)} and {str(t2)}.")
			return False
		# check all edges in the world graph
		world_matrix = self.world_graph.ch_to_adj[channel]
		connection_mat = world_matrix[np.ix_(c1.get_vertices(), c2.get_vertices())]
		if not np.all((connection_mat.A >= multiplicity_of_super_edge)):
			# each connection from c1 to c2 must be greater than or equals to the multiplicity super edge
			return False
		return True  # pass all checks means True

	def get_candidates(self, sn: SuperTemplateNode) -> iter:
		""" Returns an iterator of candidates of a given supernode
		Iterates through subsets of nodes for supernodes rather than permutations
		Yields singleton for trivial supernodes """
		# IMPORTANT: must use yield for iterator.... can be complicated wrt storage
		# TODO: Equivalent classes in world nodes
		if sn.is_trivial():
			cand_list = self._get_cand_list(sn)
		else:
			cand_list = self.non_triv_candidates[sn]
		for n in cand_list:
			yield Supernode(n)

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
		return True  # here we have passed all channels clique test

	def check_satisfiability(self) -> bool:
		""" Returns a bool indicating with the current
		candidate structure, a solution is possible.
		Just check if any cand_count = 0. This is called ideally after filtering"""
		return np.all(self.get_cand_count() >= self.equiv_size_array)  # returns False if any cand is 0

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

	def get_supernode_by_idx(self, idx: int) -> SuperTemplateNode:
		""" Given the index of a node, return the supernode"""
		return self.supernodes[self.equiv_classes.compress_to_root(idx)]

	def get_supernode_by_name(self, name: str) -> SuperTemplateNode:
		""" Given a name of a node, return the supernode"""
		idx = self.tmplt_graph.node_idxs[name]
		return self.get_supernode_by_idx(idx)

	def _get_cand_list(self, sn: SuperTemplateNode) -> [int]:
		""" Return the indices of the candidates of sn"""
		return list(i[0] for i in np.argwhere(self.candidates_array[sn.get_root()]))

	def __str__(self):
		return str(self.equiv_classes)  # for now

	# === NUMBER QUERIES ====
	def get_superedge_multiplicity(self, t1: SuperTemplateNode, t2: SuperTemplateNode, channel: str) -> int:
		""" Returns whether two SuperTemplateNode has an edge in a specific channel in the template graph
		O(1) """
		return self.tmplt_graph.ch_to_adj[channel][t1.get_root(), t2.get_root()]

	def get_supernodes_count(self):
		"""Return the total number of super nodes in the candidate structure.
		Should be the same as the number of equivalent classes """
		return len(self.supernodes)

	def get_template_nodes_count(self):
		"""Return the total number of template node.
		Should be the same as the size of the union of all nodes in the supernodes"""
		return self.tmplt_graph.n_nodes

	def get_candidates_count(self, supernode: SuperTemplateNode) -> int:
		""" Returns the number of candidates that supernode has"""
		return int(np.sum(self.candidates_array[supernode.get_root()]))

	def get_degree(self, supernode: SuperTemplateNode) -> int:
		""" Returns the degree (in+out) of a supernode"""
		return int(np.sum(self.tmplt_graph.sym_composite_adj[supernode.get_root()], axis=1))

	def get_nbr_count(self, supernode: SuperTemplateNode):
		""" Returns the number of neighbors of a supernode"""
		return int(np.sum(self.tmplt_graph.is_nbr[supernode.get_root()], axis=1))

	def get_cand_count(self) -> np.ndarray:
		""" Returns an array where each index specify the number of candidates
		This is just for individual node and not taken into account equiv classes"""
		return np.sum(self.candidates_array, axis=1)

	def get_supernodes_cand_count(self) -> {SuperTemplateNode: int}:
		""" Returns a dictionary of supernodes and their candidate counts
		This time we take into account of subsets and such"""
		return {sn: self.get_candidates_count(sn) for sn in self.supernodes.values()}

	def get_supernodes_degrees(self) -> {SuperTemplateNode: int}:
		""" Returns a dictionary of supernodes and degree """
		return {sn: self.get_degree(sn) for sn in self.supernodes.values()}

	def get_supernodes_nbr_count(self) -> {SuperTemplateNode: int}:
		""" Returns a dictionary of supernodes and their neighbor counts"""
		return {sn: self.get_nbr_count(sn) for sn in self.supernodes.values()}
