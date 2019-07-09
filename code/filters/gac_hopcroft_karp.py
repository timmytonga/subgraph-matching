import numpy as np
import networkx as nx
from hopcroftkarp import HopcroftKarp

def gac_hopcroft_karp(tmplt, world, candidates, *,
                       changed_cands=None, verbose=False):
    """ Naive implementaion """
    # Nodes in bipartite sets must have different names
    graph = {"T"+str(tmplt_idx): set(np.argwhere(candidates[tmplt_idx]).flat)
             for tmplt_idx in range(tmplt.n_nodes)}
    marked = candidates.copy()
    for tmplt_idx, cand_idx in np.argwhere(candidates):
        print("Checking:", tmplt_idx, cand_idx)
        if ~marked[tmplt_idx, cand_idx]:
            continue
        graph_copy = graph.copy()
        graph_copy[tmplt_idx] = set([cand_idx])
        match = HopcroftKarp(graph_copy).maximum_matching()
        if len(match) != tmplt.n_nodes * 2:
            candidates[tmplt_idx, cand_idx] = False
            marked[tmplt_idx, cand_idx] = False
        else:
            for src, dst in match.items():
                if str(src)[0] == "T":
                    src = int(src[1:])
                    marked[src, dst] = False
    return tmplt, world, candidates

def gac_hopcroft_karp2(tmplt, world, candidates, *,
                       changed_cands=None, verbose=False):
    """ Implementation of algorithm 4 from The Alldifferent Constraint: A Survey (Van Hoeve)
    """
    # Nodes in bipartite sets must have different names
    graph = {"T"+str(tmplt_idx): set(np.argwhere(candidates[tmplt_idx]).flat)
             for tmplt_idx in range(tmplt.n_nodes)}
    marked = candidates.copy()
    match = HopcroftKarp(graph).maximum_matching()
    if len(match) != tmplt.n_nodes * 2:
        candidates[:,:] = False
        return tmplt, world, candidates
    total_nodes = tmplt.n_nodes + world.n_nodes
    adj_mat = np.eye(total_nodes, dtype=np.bool)
    # First rows are tmplt nodes, remaining are candidates
    adj_mat[tmplt.n_nodes:, :tmplt.n_nodes] = np.ones((world.n_nodes, tmplt.n_nodes), dtype=np.bool)#candidates.T
    m_free = np.ones(total_nodes, dtype=np.bool)
    for src, dst in match.items():
        if str(src)[0] == "T":
            src = int(src[1:])
            marked[src, dst] = False
            m_free[src] = False
            m_free[tmplt.n_nodes+dst] = False
            # Reverse the edge
            adj_mat[src, tmplt.n_nodes+dst] = True
            adj_mat[tmplt.n_nodes+dst, src] = False
    # Find strongly connected components
    G = nx.DiGraph(adj_mat)
    sccs = nx.strongly_connected_components(G)
    for scc in sccs:
        # Mark all edges contained within the scc
        tmplt_idxs = [idx for idx in scc if idx < tmplt.n_nodes]
        cand_idxs = [idx-tmplt.n_nodes for idx in scc if idx >= tmplt.n_nodes]
        marked[np.ix_(tmplt_idxs, cand_idxs)] = False
    # perform breadth first search starting from M-free vertices
    curr_node_set = m_free
    old_node_set = np.zeros(total_nodes, dtype=np.bool)
    while np.any(curr_node_set != old_node_set):
        old_node_set = curr_node_set.copy()
        curr_node_set = np.any(adj_mat[curr_node_set, :], axis=0)
    marked[:, curr_node_set[tmplt.n_nodes:]] = False

    # Any remaining marked edges are not viable and should be removed
    candidates[marked] = False
    return tmplt, world, candidates
