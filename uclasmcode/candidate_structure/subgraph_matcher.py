""" A class to help organize all the logistics of running subgraph matching
Options:
	- Logging customization (set names, rotater, etc.)
	- Caching already filtered datasets
	- Running all the partitioning and such
	- Set stopping point for matcher: matchcount, isocount, etc.
	- Checkpoints for filtering/matching/solution (save solution every x matches)
	- Save solution object and load"""

from .candidate_structure import CandidateStructure
from .partial_match import PartialMatch
from .solution_tree import SolutionTree
from .match_subgraph_utils import Ordering, is_joinable
from .logging_utils import print_info, print_debug
import uclasmcode.candidate_structure.logging_utils as simple_utils
import time

NUM_THREADS = 1
STOP_FLAG = False  # a flag to stop matching
VERBOSE_FLAG = False
filter_verbose_flag = False
BRAKE = None

total_filter_time = 0
LEVEL = 0
match_count = 0


class SubgraphMatcher(object):
	""" A matching engine that runs the subgraph matching algorithm and
	ability to control the process"""

	def __init__(self, cs):
		pass

	def match_subgraph(
			self, cs: CandidateStructure, pm: PartialMatch,
			solution: SolutionTree, ordering: Ordering) -> None:
		""" pm: dictionary of supernode and matched nodes for partial matches
			Require a solution tree to be initialized as a global variable with name solution"""
		global total_filter_time, LEVEL, STOP_FLAG
		if STOP_FLAG:  # something wants us to stop
			return

		# BASE CASE: if pm has enough matched nodes
		if len(pm) == cs.get_supernodes_count():
			# this means we have a matching
			solution.add_solution(pm)
			print_info(f"FOUND a match. Current iso count: {str(solution.get_isomorphisms_count())} ")
			level -= 1
			if BRAKE is not None and solution.get_isomorphisms_count() > BRAKE:
				STOP_FLAG = True
			return  # here we should return to the previous state to try other candidates

		print_debug(f"Beginning to run update_cadidates at level {level}")
		# We haven't finished the match. We must find another one to add onto the match until we have enough
		# Need something like CandidateStructure.run_cheap_filters(partialMatch)
		# todo: if there's no update then do not run filters...
		if cs.update_candidates(pm.get_last_match()):  # this modifies candidates_array
			st1 = time.time()
			print_info(f"Beginning to run filters at level {level}")
			# only run the filters if there was any change
			num_removed = cs.run_cheap_filters(filter_verbose_flag)  # this modifies world_graph and candidates_array
			total_filter_time += time.time() - st1
			print_info(f"Ran filter during tree search: took {time.time() - st1}s; removed {num_removed} world nodes")
		else:
			print_debug("No update_candidates this level")

		# see if this is satisfiable
		if not cs.check_satisfiability():
			# if it's unsatisfiable and we are only at the first level then we can remove it as candidate
			level -= 1
			return

		# Now we pick a good next supernode to consider candidates from
		next_supernode = ordering.get_next_cand(pm)
		print_info(f"Current Level = {level} and next supernode is {next_supernode.name} ")
		# copy_of_post_filtering_cs = cs.copy()
		# TODO: Can parallelize this for loop (mutex solution and need to duplicate pm/cs/ordering/iterator/etc.)
		# TODO: This might be taking up a lot of memory for huge tree and because of combinations
		# --> solution: index pointer, candidates equiv.
		get_cand = cs.get_candidates(next_supernode)
		for cand in get_cand:  # get the candidates of our chosen supernode
			print_debug(f"Looping with pair {(str(next_supernode), repr(cand))};")
			# cand can be a singleton or a larger subset depending on the size of the supernode.
			# get_candidates in cs will take care of either case and return an appropriate iterator
			# this iterator guarantees we do not
			# todo: make sure is_joinable is correct when we modify cs above
			if is_joinable(pm, cs, supernode=next_supernode, candidate_node=cand):  # check
				# if we can join, we add it to the partial match and recurse until we have a full match
				pm.add_match(supernode=next_supernode, candidate_node=cand)  # we have a bigger partial match to explore
				ordering.increment_index()
				level += 1
				self.match_subgraph(  # this recursion step guarantees we have a DFS search. This tree is huge
					cs.copy(), pm, solution, ordering)
				# if the above run correctly, we should have already explored all the branches below given a partial match
				# we return to get back to the top level, but before doing so, we must restore our data structure.
				ordering.decrement_index()
				debugvalue = pm.rm_last_match()
		level -= 1
		return


def initialize_solution_tree(good_ordering, cs: CandidateStructure, count_only=False) -> SolutionTree:
	""" Given a cs, find a good ordering of the template nodes and initialize the solution tree"""
	sol = SolutionTree(good_ordering, cs.world_graph.nodes, count_only=count_only)
	return sol


def find_isomorphisms(
		candstruct: CandidateStructure, verbose=True, debug=True, count_only=False,
		filter_verbose=False, cap_iso=None, cap_matches=None
) -> SolutionTree:
	""" Given a cs, find all solutions and append them to a solution tree
	for returning"""
	global total_filter_time, VERBOSE_FLAG, filter_verbose_flag, BRAKE
	verbose_flag = verbose
	total_filter_time = 0
	filter_verbose_flag = filter_verbose
	brake = cap_iso
	simple_utils.VERBOSE = verbose
	simple_utils.DEBUG = debug
	print_info("======= BEGINNING FIND_ISOMORPHISM =====")
	ordering = Ordering(candstruct)
	print_info(f"Initialized an initial ordering: {str(ordering)}")
	good_ordering = ordering.initial_ordering
	sol = initialize_solution_tree(good_ordering, candstruct, count_only)
	partial_match = PartialMatch()
	print_info("======= BEGIN SUBGRAPH MATCHING =======")
	SubgraphMatcher.match_subgraph(candstruct.copy(), partial_match, sol, ordering)
	print_info(f"- Total filter time: {total_filter_time}s")
	print_info(f"====== Finished subgraph matching. Returning solution tree. =====")
	return sol
