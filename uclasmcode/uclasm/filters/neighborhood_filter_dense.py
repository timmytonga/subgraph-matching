from queue import Queue

import numpy as np
from scipy.optimize import linear_sum_assignment

BIG_VALUE = 1e6

# Global queue used for neighborhood filter
# These are going to be bigger than necessary
filter_queue = Queue(1000)
marked_to_filter = np.zeros(1000, dtype=np.bool)


def dequeue():
	v = filter_queue.get()
	marked_to_filter[v] = False
	return v


def enqueue(v):
	if marked_to_filter[v]:
		return
	marked_to_filter[v] = True
	filter_queue.put(v)


def compute_matched_neighbors(graph, vert, matching, unmatched=False):
	"""
	Compute the vertices adjacent to vert which are matched already

	Args:
		graph (Graph): Either the template or the world graph
		vert (int): The index of the vertex in graph
		matching (np.array): An array mapping the index of vert to its
			corresponding vertex in the tmplt (if graph is world) or world
			(if graph is tmplt), if unmatched the value should be -1
		unmatched (bool): If True, return the unmatched neighbors
	"""
	matched_verts = matching != -1

	mask = np.zeros(graph.n_nodes, dtype=np.bool)
	nbrs = graph.neighbors[vert]
	mask[nbrs] = True
	if unmatched:
		matched_nbrs = (mask & ~matched_verts).nonzero()[0]
	else:
		matched_nbrs = (mask & matched_verts).nonzero()[0]
	return matched_nbrs


def compute_cost(tmplt, world, t_vert, w_vert, matching):
	"""
	Compute the cost of matching t_vert to w_vert. This checks how
	many edges must be missed from neighbors that are already matched
	so that t_vert can be matched to w_vert.
	"""
	cost = 0
	matched_t_nbrs = compute_matched_neighbors(tmplt, t_vert, matching, unmatched=False)

	for t_nbr in matched_t_nbrs:
		w_nbr = matching[t_nbr]
		for channel in tmplt.channels:
			t_adj = tmplt.ch_to_adj[channel]
			t_out = t_adj[t_vert, t_nbr]
			t_in = t_adj[t_nbr, t_vert]

			w_adj = world.ch_to_adj[channel]
			w_out = w_adj[w_vert, w_nbr]
			w_in = w_adj[w_nbr, w_vert]

			cost += max(t_out - w_out, 0) + max(t_in - w_in, 0)
	return cost


def invert_matching(world, matching):
	inv_matching = np.zeros(world.n_nodes) - 1
	inv_matching[matching[matching != -1]] = np.nonzero(matching != -1)[0]
	return inv_matching


def compute_cost_matrix(tmplt, world, t_vert, w_vert, matching):
	"""
	Construct the cost matrix of associating t_vert with w_vert for
	each unmatched neighbor of t_vert to be mapped to each unmatched
	neighbor of w_vert.

	This will return a matrix and the two lists which describe what the
	indices of the matrix refer to. If we denote the matrix C, then
	C[i,j] will be the cost of mapping t_nbrs[i] to w_nbrs[j].
	It will also return t_column, a vector where t_column[i] is the cost
	of mapping t_nbrs[i] to a vertex not adjacent to t_vert
	"""
	# We look at the nbrs which have not yet been matched
	t_nbrs = compute_matched_neighbors(tmplt, t_vert, matching, unmatched=True)
	if len(t_nbrs) == 0:
		return None
	inv_matching = invert_matching(world, matching)
	w_nbrs = compute_matched_neighbors(world, w_vert, inv_matching, unmatched=True)

	cost_matrix = np.zeros((len(t_nbrs), len(w_nbrs)))

	t_column = np.zeros(len(t_nbrs))
	for channel in tmplt.channels:
		# We reshape the arrays to take advantage of broadcasting
		t_adj = tmplt.ch_to_adj[channel]
		t_out_counts = t_adj[t_vert, t_nbrs].reshape((len(t_nbrs), 1))
		t_in_counts = t_adj[t_nbrs, t_vert].reshape((len(t_nbrs), 1))

		w_adj = world.ch_to_adj[channel]
		w_out_counts = w_adj[w_vert, w_nbrs].reshape((1, len(w_nbrs)))
		w_in_counts = w_adj[w_nbrs, w_vert].reshape((1, len(w_nbrs)))

		# There should be no advantage to having more edges then necessary
		# so we lowerbound the arrays at 0
		cost_matrix += np.maximum(t_in_counts - w_in_counts, 0)
		cost_matrix += np.maximum(t_out_counts - w_out_counts, 0)
		t_column += t_in_counts.reshape(-1) + t_out_counts.reshape(-1)

	return cost_matrix, t_nbrs, w_nbrs, t_column


def check_LAD(tmplt, world, cand_matrix, t_vert, w_vert, matching, allowable_noise=0):
	"""
	Check that the mapping from t_vert to w_vert has an injection from
	neighbors of t_vert to neighbors of w_vert up to the allowable noise
	"""
	# Check if the degree of the vertex is less than allowable noise
	# if it is, we return True since we can remove all incident edges without
	# problem
	t_degree = sum(tmplt.degree[channel][t_vert] for channel in tmplt.channels)
	if t_degree <= allowable_noise:
		return True

	# This is the cost incurred from already matched vertices
	cost = compute_cost(tmplt, world, t_vert, w_vert, matching)

	# If this cost is already too high, we don't need to continue
	if cost > allowable_noise:
		return False

	# This returns None if the t_vert has no unmatched neighbors
	output = compute_cost_matrix(tmplt, world, t_vert, w_vert, matching)
	# If the current vertex has no non-matched neighbors, we don't need
	# to bother checking for an injection
	if output is None:
		return True

	# Otherwise, we can extract a cost matrix from output
	cost_matrix, t_nbrs, w_nbrs, t_column = output
	t_column = t_column.reshape(-1, 1)

	# We heavily penalize mapping a neighbor to a world vertex for which
	# it is not a candidate so that it will not happen
	nbr_cands = cand_matrix[t_nbrs, :][:, w_nbrs]
	cost_matrix += BIG_VALUE * ~nbr_cands

	# To account for the possibility that neighbors of t_vert
	# can be mapped to vertices which aren't adjacent to w_vert
	# We just need to pad the number of columns in the cost matrix
	# so that there is at least as many as there are neighbors of the
	# tmplt vertex. These columns will just be the cost of assigning
	# the vertex to a not adjacent neighbor.
	additional_columns = [t_column for _ in range(len(t_nbrs), len(w_nbrs))]
	cost_matrix = np.hstack([cost_matrix] + additional_columns)

	row_ind, col_ind = linear_sum_assignment(cost_matrix)
	cost += cost_matrix[row_ind, col_ind].sum()
	return cost <= allowable_noise


def domain_1_vertices(tmplt, cand_matrix, matching):
	"""
	Return unmatched vertices which have domain size 1
	"""
	matched_t_vertices = matching != -1
	dom_1_verts = np.argwhere(cand_matrix.sum(axis=1) == 1)
	mask = np.zeros(tmplt.n_nodes, dtype=np.bool)
	mask[dom_1_verts] = True
	unmatched_dom_1_verts = np.argwhere(~matched_t_vertices & mask)
	if len(unmatched_dom_1_verts) > 0:
		return unmatched_dom_1_verts[0]
	else:
		return []


def propagate_FC_edge(tmplt, world, cand_matrix, t_vert, w_vert, matching, allowable_noise=0):
	"""
	Propagate the FC edge constraint after mapping t_vert to w_vert. This
	says that any neighbor of t_vert must be mapped to a neighbor of
	w_vert up to a certain level of noise.
	"""
	output = compute_cost_matrix(tmplt, world, t_vert, w_vert, matching)
	# if t_vert has no unmatched neighbors, nothing to propagate
	if output is None:
		return
	# t_nbrs, w_nbrs are unmatched nbrs of t_vert and w_vert respectively
	# t_column is the cost of mapping each vertex to a not-adjacent vertex
	# of w_vert
	cost_matrix, t_nbrs, w_nbrs, t_column = output

	# Anywhere the cost is > the noise level is not a candidate
	bad_indices = np.argwhere(cost_matrix > allowable_noise)
	t_nbr_indices = t_nbrs[bad_indices[:, 0]]
	w_nbr_indices = w_nbrs[bad_indices[:, 1]]

	mask = np.ones((tmplt.n_nodes, world.n_nodes), dtype=np.bool)
	mask[t_nbr_indices, w_nbr_indices] = False

	# We set for all adjacent tmplt verts that world verts not adjacent
	# to w_vert are not candidates. This is done for each adjacent
	# tmplt vert for which it is impossible to map to a vertex not connected
	# to w_vert without violating the noise level
	bad_indices = t_nbrs[t_column > allowable_noise]
	w_not_nbrs = np.ones(world.n_nodes, dtype=np.bool)
	w_not_nbrs[world.neighbors[w_vert]] = False

	# We don't want to apply the mask to already matched world vertices
	matched_w_vertices = np.zeros(world.n_nodes, dtype=np.bool)
	matched_w_vertices[matching[matching != -1]] = 1
	w_unmatched_not_nbrs = w_not_nbrs & matched_w_vertices

	mask[bad_indices.reshape((-1, 1)), w_unmatched_not_nbrs] = False
	changed_cands = cand_matrix & ~mask
	for (t, w) in zip(*changed_cands.nonzero()):
		remove_value(tmplt, cand_matrix, t, w)


def propagate_FC_diff(tmplt, cand_matrix, t_vert, w_vert):
	"""
	Propagate the FC diff constraint after mapping t_vert to w_vert. This
	just removes w_vert from the domain of every template
	"""
	remove_all_but_one_value(tmplt, cand_matrix, t_vert, w_vert)
	for t_vert2 in cand_matrix[:, w_vert].nonzero()[0]:
		if t_vert == t_vert2:
			continue
		remove_value(tmplt, cand_matrix, t_vert2, w_vert)


def match(tmplt, world, cand_matrix, t_vert, w_vert, matching, allowable_noise, verbose=0):
	"""
	This function will try to match t_vert to w_vert in the
	partial match. To do this, it removes all values but the world vert
	from the domain of t_vert.

	After matching, this will match any unmatched vertices that are
	now domain 1 after propagating FC(diff) and FC(edge).

	Args:
		t_vert (int): The index of the template vertex
		w_vert (int): The index of the world vertex
		verbose (int): The level (0-2) of verbosity, 0 is None, 2 is max
	"""
	if verbose == 2:
		print("Attempting Mapping {} -> {}".format(t_vert, w_vert))

	# Cost of matching t_vert to w_vert
	match_cost = compute_cost(tmplt, world, t_vert, w_vert, matching)
	if match_cost > allowable_noise:
		if verbose == 2:
			print("Match Fail: cost={}>{}".format(match_cost, allowable_noise))
		return False

	matching[t_vert] = w_vert
	propagate_FC_diff(tmplt, cand_matrix, t_vert, w_vert)
	propagate_FC_edge(tmplt, world, cand_matrix, t_vert, w_vert, matching, allowable_noise)

	# If any template vertex has 0 candidates, we report a Failure
	zero_cands = np.argwhere(cand_matrix.sum(axis=1) == 0)
	if len(zero_cands) > 0:
		if verbose == 2:
			print("Match Fail: {} have 0 candidates".format(zero_cands))
		return False
	if verbose == 2:
		print("Match Success")

	domain_1_verts = domain_1_vertices(tmplt, cand_matrix, matching)
	while len(domain_1_verts) > 0:

		t = domain_1_verts[0]
		w = np.argwhere(cand_matrix[t])[0][0]
		if verbose == 2:
			print("Attempting Mapping {} -> {}".format(t, w))

		# Add Cost of matching t to w
		match_cost += compute_cost(tmplt, world, t, w, matching)
		# If making the match causes too much noise, we report a failure
		if match_cost > allowable_noise:
			if verbose == 2:
				print("Match Fail: cost={}>{}".format(match_cost, allowable_noise))
			return False

		matching[t] = w
		propagate_FC_diff(tmplt, cand_matrix, t, w)
		propagate_FC_edge(tmplt, world, cand_matrix, t, w, matching, allowable_noise)

		# If any template vertex has 0 candidates, we report a Failure
		zero_cands = np.argwhere(cand_matrix.sum(axis=1) == 0)
		if len(zero_cands) > 0:
			if verbose == 2:
				print("Match Fail: {} have 0 candidates".format(zero_cands))
			return False
		if verbose == 2:
			print("Match Success")

		domain_1_verts = domain_1_vertices(tmplt, cand_matrix, matching)

	return True


def remove_all_but_one_value(tmplt, cand_matrix, t_vert, w_vert):
	"""
	Remove all but one value from the domain of t_vert.
	"""
	new_row = np.zeros(cand_matrix.shape[1])
	new_row[w_vert] = True
	cand_matrix[t_vert, :] = new_row
	for nbr in tmplt.neighbors[t_vert]:
		enqueue(nbr)


def remove_value(tmplt, cand_matrix, t_vert, w_vert):
	cand_matrix[t_vert, w_vert] = False
	for nbr in tmplt.neighbors[t_vert]:
		enqueue(nbr)


def neighborhood_filter(tmplt, world, cand_matrix, matching, allowable_noise=0, verbose=0):
	for v in range(tmplt.n_nodes):
		enqueue(v)

	while not filter_queue.empty():
		t_vert = dequeue()

		# If already matched, don't bother checking
		if matching[t_vert] != -1:
			continue

		domain_sizes = cand_matrix.sum(axis=1)
		old_size = domain_sizes[t_vert]
		new_size = old_size

		if verbose == 2:
			print("Checking LAD for {}".format(t_vert))
			print("Old Domain Size {}".format(old_size))
		# For each candidate, check if it passes LAD
		w_cands = cand_matrix[t_vert].nonzero()[0]
		for cand_vert in w_cands:
			if check_LAD(tmplt, world, cand_matrix, t_vert, cand_vert, matching, allowable_noise):
				pass
			else:
				remove_value(tmplt, cand_matrix, t_vert, cand_vert)
				new_size -= 1

		if verbose == 2:
			print("New Domain Size {}".format(new_size))
		# If reduced the size of the domain to 1, attempt to match
		if new_size == 1 and old_size > 1:
			w_vert = int(np.argwhere(cand_matrix[t_vert]))
			if not match(tmplt, world, cand_matrix, t_vert, w_vert, matching, allowable_noise, verbose):
				cand_matrix[...] = False
				break

		domain_sizes = cand_matrix.sum(axis=1)
		# This means that we have reached an inconsistency and must
		# backtrack
		if domain_sizes[t_vert] == 0:
			cand_matrix[...] = False
			break

	return tmplt, world, cand_matrix
