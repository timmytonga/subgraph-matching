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
from .logging_utils import print_info, print_debug, print_warning
from ..equivalence_partition.equivalence_data_structure import Equivalence
from .. equivalence_partition.multichannel_structural_equivalence import partition_multichannel
import uclasmcode.candidate_structure.logging_utils as simple_utils
import time

NUM_THREADS = 1
STOP_FLAG = False  # a flag to stop matching
verbose_flag = False
filter_verbose_flag = False
brake = None

total_filter_time = 0
level = 0
match_count = 0


def match_subgraph(
        cs: CandidateStructure, pm: PartialMatch,
        solution: SolutionTree, ordering: Ordering) -> None:
    """ pm: dictionary of supernode and matched nodes for partial matches
        Require a solution tree to be initialized as a global variable with name solution"""
    global total_filter_time, level, STOP_FLAG
    if STOP_FLAG:  # something wants us to stop
        return

    # BASE CASE: if pm has enough matched nodes
    if len(pm) == cs.get_supernodes_count():
        # this means we have a matching
        solution.add_solution(pm)
        print_warning(f"FOUND a match. Current iso count: {str(solution.get_isomorphisms_count())} ")
        level -= 1
        if brake is not None and solution.get_isomorphisms_count() > brake:
            STOP_FLAG = True
        return  # here we should return to the previous state to try other candidates

    # We haven't finished the match. We must find another one to add onto the match until we have enough
    if cs.update_candidates(pm.get_last_match()):  # this modifies candidates_array
        st1 = time.time()
        print_debug(f"Beginning to run filters at level {level}")
        # only run the filters if there was any change
        num_removed = cs.run_cheap_filters(filter_verbose_flag)  # this modifies world_graph and candidates_array
        total_filter_time += time.time() - st1
        print_debug(f"Ran filter during tree search: took {time.time() - st1}s;")
        if num_removed != 0:
            print_debug(f"Level {level}: removed {num_removed} world nodes")

    # see if this is satisfiable
    if not cs.check_satisfiability():
        # if it's unsatisfiable and we are only at the first level then we can remove it as candidate
        level -= 1
        print_debug(f"NOT SATISFIABLE. RETURNING to level {level}")
        return

    # Now we pick a good next supernode to consider candidates from
    next_supernode = ordering.get_next_cand(pm)
    cand_count = cs.get_candidates_count(next_supernode)
    print_info(f"Level={level}. World-size={cs.world_graph.n_nodes}. Next supernode is {next_supernode.name} with"
               f" {cand_count} candidates")
    # TODO: Can parallelize this for loop (mutex solution and need to duplicate pm/cs/ordering/iterator/etc.)
    # TODO: This might be taking up a lot of memory for huge tree and because of combinations
    # WORLD NODE EQUIV: get the world nodes that participate in the next supernode and partition them
    cand_vertices = Equivalence(cs.get_cand_list_idxs(next_supernode))
    cand_vertices.partition(cs.candidate_equivalence, next_supernode)  # partition it according to the candidate equiv. relationship
    # cand_vertices = partition_multichannel(cs.world_graph.ch_to_adj, cand_vertices)
    print_info("new" + repr(cand_vertices))

    for cand in cs.get_candidates(next_supernode):  # get the candidates of our chosen supernode
        if STOP_FLAG:
            level -= 1
            return
        print_debug(f"Level={level}({cand_count}): Looping with pair {(str(next_supernode), str(cand))};", end="")
        # cand can be a singleton or a larger subset depending on the size of the supernode.
        # get_candidates in cs will take care of either case and return an appropriate iterator
        if is_joinable(pm, cs, supernode=next_supernode, candidate_node=cand):  # check
            # if we can join, we add it to the partial match and recurse until we have a full match
            print_debug(" and they were JOINABLE!")
            pm.add_match(supernode=next_supernode, candidate_node=cand)  # we have a bigger partial match to explore
            ordering.increment_index()
            level += 1
            match_subgraph(
                cs.copy(), pm, solution,
                ordering)  # this recursion step guarantees we have a DFS search. This tree is huge
            # if the above run correctly, we should have already explored all the branches below given a partial match
            # we return to get back to the top level, but before doing so, we must restore our data structure.
            ordering.decrement_index()
            pm.rm_last_match()
        else:
            print_debug(" and NOT JOINABLE.")
    level -= 1
    print_debug(f"Bottom level. Finished for loop. RETURNING to level {level}.")
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
    global total_filter_time, verbose_flag, filter_verbose_flag, brake
    verbose_flag = verbose
    total_filter_time = 0
    filter_verbose_flag = filter_verbose
    brake = cap_iso
    simple_utils.VERBOSE = verbose
    simple_utils.DEBUG = debug
    print_info("======= BEGINNING FIND_ISOMORPHISM =====")
    ordering = Ordering(candstruct)
    good_ordering = ordering.initial_ordering
    sol = initialize_solution_tree(good_ordering, candstruct, count_only)
    partial_match = PartialMatch()
    print_info("======= BEGIN SUBGRAPH MATCHING =======")
    match_subgraph(candstruct.copy(), partial_match, sol, ordering)
    print_info(f"- Total filter time: {total_filter_time}s")
    print_info(f"====== Finished subgraph matching. Returning solution tree. =====")
    return sol
