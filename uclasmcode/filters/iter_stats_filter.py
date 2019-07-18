import numpy as np
import csv
import time

def compute_features(graph, channels=None):
    """ For computing only the features of the template that we can compute
    for the background as well """
    features = []

    if channels is None:
        channels = graph.channels

    # Only 3 statistics are supported by iter_stats_filter
    # in/out degree and self edges
    for channel in channels:
        adj = graph.adjs[graph.channels.index(channel)]

        # in degree
        features.append(adj.sum(axis=0))

        # out degree
        features.append(adj.sum(axis=1).T)

        # self edges
        features.append(np.reshape(adj.diagonal(), (1, -1)))

    return np.stack(features)

def get_node_list_and_channels(filepaths, src_col, dst_col=None,
                  channel_col=None, delimiter=",", skip_lines=1):
    """ Reads edgelists or nodelists stored at filepaths and finds
    the list of all nodes
    Returns the list of all nodes and the list of channels"""
    node_set = set()
    channels = set()
    for filepath in filepaths:
        with open(filepath, "r") as fin:
            reader = csv.reader(fin, delimiter=delimiter)
            for i in range(skip_lines): next(reader)
            for line in reader:
                try:
                    src = line[src_col]
                    channel = None if channel_col is None else line[channel_col]
                    node_set.add(src)
                    if dst_col is not None:
                        dst = line[dst_col]
                        node_set.add(dst)
                    if channel not in channels:
                        channels.add(channel)
                except IndexError:
                    print(line)
                    continue
    return list(node_set), channels

def compute_features_from_edgelist(filepath,
                  nodes=None,
                  src_col=None,
                  dst_col=None,
                  channel_col=None,
                  delimiter=",",
                  skip_lines=1,
                  edge_repair_func=None,
                  node_to_truth=None,
                  cycle_buffer=False,
                  verbose=True):
    """
    Reads the edgelist stored at `filepath` and computes features
    Returns a 3C x N array of features, where C is the number of channels and
    N is the number of nodes
    """
    assert src_col is not None
    assert dst_col is not None

    # 3 features: in/out degree, self edges
    # Cannot compute nbrs or reciprocated edges with this method
    channel_to_features = {}
    # features = np.zeros(shape=(len(node_list), 3*len(channels)))

    if nodes is None:
        node_to_idx = {}
    else:
        node_to_idx = {node: i for i, node in enumerate(nodes)}

    # key is channel, value is dict mapping (src, dst) edge tuple to its count
    channels = set()
    channel_to_edge_to_idx = {}
    channel_to_srcs = {}
    channel_to_dsts = {}
    channel_to_counts = {}

    with open(filepath, "r") as fin:
        reader = csv.reader(fin, delimiter=delimiter)
        for i in range(skip_lines): next(reader)

        start_time = time.time()
        count = 0
        for line in reader:
            try:
                src = line[src_col]
                dst = line[dst_col]
            except IndexError:
                print(line)
                continue

            if node_to_truth is not None:
                src = node_to_truth.get(src, src)
                dst = node_to_truth.get(dst, dst)

            channel = None if channel_col is None else line[channel_col]

            if edge_repair_func is not None:
                src, dst, channel = edge_repair_func(src, dst, channel)
                if (src is None) or (dst is None):
                    continue

            # if we haven't seen these nodes before, stick them in the list
            if src not in node_to_idx: node_to_idx[src] = len(node_to_idx)
            if dst not in node_to_idx: node_to_idx[dst] = len(node_to_idx)

            edge = (node_to_idx[src], node_to_idx[dst])

            if channel not in channels:
                channels.add(channel)
                channel_to_features[channel] = np.zeros((3, len(nodes)),dtype=np.uint16)

            # Update in/out degree
            channel_to_features[channel][0,node_to_idx[src]] += 1
            channel_to_features[channel][1,node_to_idx[dst]] += 1
            # Update reciprocated edges
            if src == dst:
                channel_to_features[channel][2,node_to_idx[src]] += 1

            count += 1
            if count % 1000000 == 0:
                print(count)

    if verbose:
        print("computing features took {}".format(time.time() - start_time))

    channels = sorted(channels)

    return np.concatenate([channel_to_features[channel] for channel in channels])

def iter_stats_filter(tmplts, world_file, node_list, from_el_kwargs):
    """ Computes iterative statistics and returns an array of valid candidates """
    print("Computing world features")
    try:
        world_feats = np.load("world_feats.npy")
    except:
        world_feats = compute_features_from_edgelist(world_file, nodes=node_list, **from_el_kwargs)
        # TODO: change this so it saves to the cache directory
        np.save("world_feats.npy", world_feats)
    candidates = set()
    for idx, tmplt in enumerate(tmplts):
        print("Computing template features for template", idx)
        try:
            tmplt_feats = np.load("tmplt_feats_{}.npy")
        except:
            tmplt_feats = compute_features(tmplt)
            np.save("tmplt_feats_{}.npy".format(idx), world_feats)

        print("Template feats sum:", np.sum(tmplt_feats))
        print("Template feats adj:", np.sum(tmplt.adjs[0]))

        # for each template node, get its candidates and union them to find all
        # candidates that could match a template node
        any_cand = None
        for tmplt_node_idx, tmplt_node in enumerate(tmplt.nodes):
            tmplt_node_feats = tmplt_feats[:, tmplt_node_idx]
            is_cand = np.all((world_feats - tmplt_node_feats) >= 0, axis=0)
            if any_cand is None:
                any_cand = np.array(is_cand).ravel()
            else:
                any_cand |= np.array(is_cand).ravel()
        new_candidates = tmplt.candidates[any_cand]
        print("Candidate list: ", new_candidates)
        print(len(new_candidates), "candidates identified")
        np.save("candidates_{}.npy".format(idx), new_candidates)
        for candidate in tmplt.candidates[any_cand]:
            candidates.add(candidate)
    print("Final candidate list:", candidates)
    print(len(candidates), "candidates identified")
    np.save("final_candidates.npy", candidates)
    return candidates
