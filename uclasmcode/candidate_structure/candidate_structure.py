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
# from .logging_utils import print_debug
from .supernodes import Supernode, SuperTemplateNode
from itertools import combinations  # for getting all subsets
from uclasmcode.uclasm.filters.run_filters_cs import run_filters
from uclasmcode import uclasm


# TODO: Make new graph datastructure without using Sparse Matrices
# TODO: Make Subgraph Matcher class for logistics
# TODO: Implement world equivalence (and prove before)


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
		self._equiv_size_array = []

	def copy(self):
		""" We need to copy the world_graph since tmplt is never modified """
		temp = CandidateStructure(
			self.tmplt_graph, self.world_graph.copy(),
			self.candidates_array.copy(), self.equiv_classes)
		temp._supernodes = self._supernodes
		temp.non_trivial_supernodes = self.non_trivial_supernodes
		return temp

	@property
	def supernodes(self) -> {str: SuperTemplateNode}:
		""" Return a set of SuperTemplateNodes that contains extra info than supernode like
		clique and root"""
		if len(self._supernodes) == 0:
			for ec in self.equiv_classes.classes():
				root = self.equiv_classes.compress_to_root(next(iter(ec)))
				temp = (SuperTemplateNode(
					ec, self._get_equiv_class_clique_dict(ec),
					name=[self.tmplt_graph.nodes[i] for i in ec],
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
	def get_candidate_combination(self, sn):
		""" Get the combinations of candidates of a supernode"""
		candidates = self._get_cand_list(sn)
		return combinations(candidates, len(sn))  # this is a generator

	def update_candidates(self, last_match: (SuperTemplateNode, Supernode)) -> bool:
		""" Given a last match, update the candidates_array to reflect that last match
		Modifies candidates_array and world_graph
		:return: bool indicating if there was any change (True if changed, False if not changed)"""
		if last_match is None:
			return False
		sn, match = last_match
		# print_debug(f"update_candidate: candidates_array before\n{str(self.candidates_array)}")
		# make an np array of shape (len(sn), world.n_nodes) to all False
		toset = np.zeros((len(sn), self.num_world_nodes), dtype=np.bool)
		world_idx = self.get_vertices_from_names(match.name)
		toset[:, world_idx] = True  # set only the matching vertices to True
		# then set the appropriate rows and columns
		no_change = np.all(self.candidates_array[np.ix_(sn.vertices, range(self.num_world_nodes))] == toset)
		self.candidates_array[np.ix_(sn.vertices, range(self.num_world_nodes))] = toset
		return not no_change

	def run_cheap_filters(self, verbose=False) -> int:
		""" Not sure if we should modify the current structure directly and store the changes
			somewhere for restore or if we should make a new structure entirely """
		# TODO: Modify filters to only run on root node of supernodes (minor speed up??)
		# TODO: Modify topology filter to take into account of edge multiplicity in supernodes
		# TODO: Neighborhood filter for cliques (union)
		# TODO: topology filter still slow
		before = self.world_graph.n_nodes
		_, self.world_graph, self.candidates_array = run_filters(
			self.tmplt_graph, self.world_graph,
			candidates=self.candidates_array, filters=uclasm.cs_filters,
			verbose=verbose)
		return self.world_graph.n_nodes - before

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
			# print_debug(f"CandidateStructure.has_cand_edge: False because {str(c1)} and {str(c2)} has intersecting nodes.")
			return False
		multiplicity_of_super_edge = self.get_superedge_multiplicity(t1, t2, channel)
		if multiplicity_of_super_edge == 0:
			# print_debug(f"has_cand_edge: False because no superedge between {str(t1)} and {str(t2)}.")
			return False
		# check all edges in the world graph
		world_matrix = self.world_graph.ch_to_adj[channel].A
		vertices_of_c1 = self.get_vertices_from_names(c1.name)
		vertices_of_c2 = self.get_vertices_from_names(c2.name)
		connection_mat = world_matrix[np.ix_(vertices_of_c1, vertices_of_c2)]
		if not np.all((connection_mat >= multiplicity_of_super_edge)):
			# each connection from c1 to c2 must be greater than or equals to the multiplicity super edge
			return False
		return True  # pass all checks means True

	def get_candidates(self, sn: SuperTemplateNode) -> [Supernode]:
		""" Returns an iterator of candidates of a given supernode
		Iterates through subsets of nodes for supernodes rather than permutations
		Yields singleton for trivial supernodes """
		# IMPORTANT: must use yield for iterator.... can be complicated wrt storage
		# TODO: Equivalent classes in world nodes
		if sn.is_trivial():
			for n in self._get_cand_list(sn):  # n is a string
				n = [n]
				idxs = self.get_vertices_from_names(n)
				yield Supernode(idxs, name=n)
		else:  # n is not trivial
			for n in self.get_candidate_combination(sn):  # n is a tuple
				idxs = self.get_vertices_from_names(n)
				yield Supernode(idxs, name=list(n))

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
					self.world_graph.ch_to_adj[ch].A,
					self.get_vertices_from_names(cand_node.name))
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
	def get_vertices_from_names(self, name_list: [str]) -> [int]:
		""" Returns the correct indices in the world graph given the name of world nodes"""
		if type(name_list[0]) is tuple:
			toreturn = [self.world_graph.node_idxs[j] for j in name_list]
		else:
			toreturn = [self.world_graph.node_idxs[i] for i in name_list]
		return toreturn

	def get_names_from_vertices(self, vertices: [int]) -> [str]:
		""" Return the name of the given indices... have to be careful"""
		if type(vertices) is int:
			return [self.world_graph.nodes[vertices]]
		return [self.world_graph.nodes[i] for i in vertices]

	def _get_cand_list(self, sn: SuperTemplateNode) -> [str]:
		""" Return the names of the candidates of sn"""
		idxs = [int(i[0]) for i in np.argwhere(self.candidates_array[sn.get_root()])]
		return self.get_names_from_vertices(idxs)

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
		result = {}
		for sn in self.supernodes.values():
			result[sn] = self.get_candidates_count(sn) 
		return result

	def get_supernodes_degrees(self) -> {SuperTemplateNode: int}:
		""" Returns a dictionary of supernodes and degree """
		return {sn: self.get_degree(sn) for sn in self.supernodes.values()}

	def get_supernodes_nbr_count(self) -> {SuperTemplateNode: int}:
		""" Returns a dictionary of supernodes and their neighbor counts"""
		return {sn: self.get_nbr_count(sn) for sn in self.supernodes.values()}
