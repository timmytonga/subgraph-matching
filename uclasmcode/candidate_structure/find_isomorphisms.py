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

from .candidate_structure import CandidateStructure
from .partial_match import PartialMatch
from .solution_tree import SolutionTree
from .match_subgraph_utils import Ordering, is_joinable
from .logging_utils import print_info, print_debug
import uclasmcode.candidate_structure.logging_utils as simple_utils

NUM_THREADS = 1
STOP_FLAG = False  # a flag to stop matching


def match_subgraph(
		cs: CandidateStructure, pm: PartialMatch,
		solution: SolutionTree, ordering: Ordering) -> None:
	""" pm: dictionary of supernode and matched nodes for partial matches
		Require a solution tree to be initialized as a global variable with name solution"""
	# print_debug(
	# 	f"MATCH_SUBGRAPH: Current partial match {str(pm)} and current candidates array \n"
	# 	f"{str(cs.candidates_array)}")
	if STOP_FLAG:  # something wants us to stop
		return

	# BASE CASE: if pm has enough matched nodes
	if len(pm) == cs.get_supernodes_count():
		# this means we have a matching
		solution.add_solution(pm)
		print_info(f"FOUND a match. Current iso count: {str(solution.get_isomorphisms_count())}")
		# maybe restore candidate structure here if modified below
		return  # here we should return to the previous state to try other candidates

	# We haven't finished the match. We must find another one to add onto the match until we have enough
	# Need something like CandidateStructure.run_cheap_filters(partialMatch)
	copy_of_cs = cs.copy()  # first make a copy
	# todo: if there's no update then do not run filters...
	if cs.update_candidates(pm.get_last_match()):  # this modifies candidates_array
		# only run the filters if there was any change
		cs.run_cheap_filters()  # this modifies world_graph and candidates_array

	# see if this is satisfiable
	if not cs.check_satisfiability():
		return

	# Now we pick a good next supernode to consider candidates from
	next_supernode = ordering.get_next_cand(pm)  # todo: better order???
	print_debug(f"The current next_supernode is: {str(next_supernode)}")
	copy_of_post_filtering_cs = cs.copy()
	# TODO: Can parallelize this for loop (mutex solution and need to duplicate pm/cs/ordering/iterator/etc.)
	# TODO: This might be taking up a lot of memory for huge tree and because of combinations
	# --> solution: index pointer, candidates equiv.
	for cand in cs.get_candidates(next_supernode):  # get the candidates of our chosen supernode
		print_debug(f"Looping with pair {(str(next_supernode), str(cand))}; currmatch {str(pm)}")
		# cand can be a singleton or a larger subset depending on the size of the supernode.
		# get_candidates in cs will take care of either case and return an appropriate iterator
		# this iterator guarantees we do not
		if is_joinable(pm, cs, supernode=next_supernode, candidate_node=cand):  # check
			# if we can join, we add it to the partial match and recurse until we have a full match
			pm.add_match(supernode=next_supernode, candidate_node=cand)  # we have a bigger partial match to explore
			ordering.increment_index()
			match_subgraph(
				cs, pm, solution, ordering)  # this recursion step guarantees we have a DFS search. This tree is huge
			# if the above run correctly, we should have already explored all the branches below given a partial match
			# we return to get back to the top level, but before doing so, we must restore our data structure.
			ordering.decrement_index()
			pm.rm_last_match()
			cs = copy_of_post_filtering_cs
		else: 	# do we need to do anything if a candidate is not joinable?
			print_debug(f"{str(cand)} not joinable with {str(pm)}")
	cs = copy_of_cs  # restore the cs before returning
	return


def initialize_solution_tree(good_ordering, cs: CandidateStructure, count_only=False) -> SolutionTree:
	""" Given a cs, find a good ordering of the template nodes and initialize the solution tree"""
	sol = SolutionTree(good_ordering, cs.world_graph.nodes, count_only=count_only)
	return sol


def find_isomorphisms(
		candstruct: CandidateStructure, verbose=True, debug=True, count_only=False
) -> SolutionTree:
	""" Given a cs, find all solutions and append them to a solution tree
	for returning"""
	simple_utils.VERBOSE = verbose
	simple_utils.DEBUG = debug
	print_info("======= BEGINNING FIND_ISOMORPHISM =====")
	ordering = Ordering(candstruct)
	print_info(f"Initialized an initial ordering: {str(ordering)}")
	good_ordering = ordering.initial_ordering
	sol = initialize_solution_tree(good_ordering, candstruct, count_only)
	partial_match = PartialMatch()
	print_info("======= BEGIN SUBGRAPH MATCHING =======")
	match_subgraph(candstruct, partial_match, sol, ordering)
	print_info(f"====== Finished subgraph matching. Returning solution tree. =====")
	return sol
