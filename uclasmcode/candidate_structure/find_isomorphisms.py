""" Tim Nguyen (7/17/19)
(For multichannel multidigraph) <- but other graphs are just special case of this
Given a candidate structure, return the solution tree to the problem.
	- The candidate structure should contain all the information about the world graph, the template graph,
		the candidates for each template node and the relationship between them.
The algorithm goes roughly as following:
	1. Initialize a structure for a partial match (initially empty list(?))
	2. Get the first element from the matching order or ranking (a supernode)
	3. Get the candidates from that first element and make a queue.
	4. Pop a candidate out and put that into the partial match if it's joinable
		- A candidate is joinable if it satisfies the homomorphism and the alldiff constraint
			with the existing nodes
	5. Look at the neighboring candidates of the neighboring supernodes.
	6. Pick one with best ranking and check if it's joinable.

Recursion step:
	0. We are given a partial m max length, add it to the solution tree and return.
	1.5. If not then we try to filter the other candidates of any bad ones.
	2. We consider which supernode to match next: (adaptive order)
		- it should be a new supatch and the candidate structure. 
	1. If the partial match has a node we have not matched with low candidate count as well
		as 
	3. Suppose we pick a good supernode to consider next. For all candidate of that node
		check if that candidate is joinable to the current partial matching
		- if it's joinable: recurse with the new partial match
		- if not then continue going through the candidates. 

"""

from . import match_subgraph_utils
from .candidate_structure import CandidateStructure
from .partial_match import PartialMatch
from .solution_tree import SolutionTree

NUM_THREADS = 1


def initialize_solution_tree(cs: CandidateStructure) -> SolutionTree:
	""" Given a cs, find a good ordering of the template nodes and initialize the solution tree"""
	good_ordering = match_subgraph_utils.find_good_ordering_template(cs)  #todo
	sol = SolutionTree(good_ordering)
	return sol


def match_subgraph(cs: CandidateStructure, pm: PartialMatch, solution: SolutionTree) -> None:
	""" pm: dictionary of supernode and matched nodes for partial matches
		Require a solution tree to be initialized as a global variable with name solution"""
	# BASE CASE: if pm has enough matched nodes
	if len(pm) == cs.get_template_nodes_count():
		# this means we have a matching
		# TODO: Optional count only (do not store solution tree)
		solution.add_solution(pm)
		# maybe restore candidate structure here if modified below
		pm.rm_last_match() 		# we need to remove last match before returning since we are only keeping one pm struct
		return  # here we should return to the previous state to try other candidates

	# We haven't finished the match. We must find another one to add onto the match until we have enough
	# Need something like CandidateStructure.run_cheap_filters(partialMatch)
	cs.run_cheap_filters(partial_match=pm)  # todo

	# Now we pick a good next supernode to consider candidates from
	next_supernode = match_subgraph_utils.pick_next_candidate(cs, pm)  #todo

	# TODO: Can parallelize this for loop (mutex solution and need to duplicate pm/cs)
	for cand in cs.get_candidates(supernode=next_supernode):  # get the candidates of our chosen supernode
		# cand can be a singleton or a larger subset depending on the size of the supernode.
		# get_candidates in cs will take care of either case and return an appropriate iterator
		# this iterator guarantees we do not
		if match_subgraph_utils.is_joinable(pm, cs, supernode=next_supernode, candidate_node=cand):  # check
			# if we can join, we add it to the partial match and recurse until we have a full match
			pm.add_match(supernode=next_supernode, candidate_node=cand)  # we have a bigger partial match to explore
			match_subgraph(cs, pm, solution)  # this recursion step guarantees we have a DFS search. This tree is huge
			# if the above run correctly, we should have already explored all the branches below given a partial match
			# we return to get back to the top level, but before doing so, we must restore our data structure.
			pm.rm_last_match()
		else: 	# do we need to do anything if a candidate is not joinable?
			pass
	# NOTE; need to have a change stack? or implement in cs? copy?
	cs.restore_changes() 	#todo # not sure which one we modify <- might be needed since we could've modified a lot
	return


def find_isomorphisms(candstruct: CandidateStructure) -> SolutionTree:
	""" Given a cs, find all solutions and append them to a solution tree
	for returning"""
	sol = initialize_solution_tree(candstruct)
	partial_match = PartialMatch()
	match_subgraph(candstruct, partial_match, sol)
	return sol
