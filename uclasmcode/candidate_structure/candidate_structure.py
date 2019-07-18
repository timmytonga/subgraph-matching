''' Data structure to hold candidate and matching order scheme 
	The structure is very similar to the template graph except that each node (called supernode)
	will be an array of vertices and there will be superedges between the nodes corresponding
	to the edges in the template graph (this is where the BFS tree comes from?)

	Also, the candidates in each node will contain edges in each other.
	# should store in this structure? Or should query from the existing world graph 
	An edge between two candidates in two supernodes exists iff a 
	superedge exist in their containing supernodes as well as if there is an edge 
	between those candidates in the world graph


by Tim Nguyen
Last update: 7/17/19 ''' 
from .supernodes import Supernode
from .partial_match import PartialMatch

class CandidateStructure:
	''' Contains 	supernodes: corresponding to template's nodes (with candidates)
					superedges (between super nodes): corresponding to template's edges
					candidate-edges: between two candidates in two supernodes
						-> exists iff superedge exists and world edge exists between the two candidates '''

	# how to match using this candidate structure? --> tree search, ordering, etc. 
	def __init__(self, template, world, candidates):
		# make proper structure here....
		pass

	# matching algorithm should have some good ordering to follow candidate-edges
	# heap sorts only order but how to take into account edge information.... BFS search ordering... 
	# 	obtain neighbor list of current node -> sort and append to order  (how to get neighbors?)
	#

	# ========== METHODS ==========
	def run_cheap_filters(self, partial_match: PartialMatch) -> "Some sort of ways to rep. candidates":
		""" Not sure if we should modify the current structure directly and store the changes
			somewhere for restore or if we should make a new structure entirely """
		pass

	def restore_changes(self):
		""" Not sure what this does yet but we might need to restore some changes say by the filters """
		pass

	# ========== QUERIES ==========
	def get_supernodes_count(self):
		"""Return the total number of super nodes in the candidate structure.
		Should be the same as the number of equivalent classes """
		pass 

	def get_template_nodes_count(self):
		"""Return the total number of template node.
		Should be the same as the size of the union of all nodes in the supernodes"""
		pass

	def get_candidates(self, supernode):
		""" Returns an iterator of candidates of a given supernode"""
		# IMPORTANT: must use yield for iterator.... can be complicated wrt storage
		pass
