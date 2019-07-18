"""
One size fits all data loaders
"""

# TODO: try using numpy.genfromtxt
# TODO: support pnnl v4.1, v5, v5.1
# TODO: switch from passing node lists everywhere to using node_to_idx

import csv
import numpy as np
import time
from scipy.sparse import csr_matrix

from .data_locations import NetFileGetter
import sys
sys.path.append("..")
import uclasm

from .data_caching import save_cache, load_cache

def from_edgelist(filepath,
                  nodes=None,
                  src_col=None,
                  dst_col=None,
                  channel_col=None,
                  encoding="utf8",
                  delimiter=",",
                  skip_lines=1,
                  edge_repair_func=None,
                  node_to_truth=None,
                  verbose=True,
                  cycle_buffer=False):
    """
    Reads the edgelist stored at `filepath` into a set of sparse adj mats.

    Returns a list of nodes, a list of channels, and a list of adj mats.
    """
    assert src_col is not None
    assert dst_col is not None

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
    channel_to_adj = {}

    dtypes = [np.uint8, np.uint16, np.uint32, np.uint64]

    num_lines = 0
    with open(filepath, "r", encoding=encoding) as fin:
        reader = csv.reader(fin, delimiter=delimiter)
        for i in range(skip_lines): next(reader)

        start_time = time.time()
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
                channel_to_edge_to_idx[channel] = {}
                channel_to_srcs[channel] = []
                channel_to_dsts[channel] = []
                channel_to_counts[channel] = []

            edge_to_idx = channel_to_edge_to_idx[channel]
            counts = channel_to_counts[channel]

            if edge not in edge_to_idx:
                channel_to_srcs[channel].append(node_to_idx[src])
                channel_to_dsts[channel].append(node_to_idx[dst])
                edge_to_idx[edge] = len(counts)
                counts.append(1)
            else:
                counts[edge_to_idx[edge]] += 1
            num_lines += 1
            if num_lines%1000000 == 0:
                print(num_lines, "lines read")
                # Stop the dictionary from consuming all memory by converting to
                # csr periodically
                if cycle_buffer:
                    n_nodes = len(node_to_idx)
                    for channel in channels:
                        srcs = channel_to_srcs[channel]
                        dsts = channel_to_dsts[channel]
                        counts = channel_to_counts[channel]
                        if len(counts) == 0:
                            continue
                        max_count = max(counts)
                        dtype = next(dt for dt in dtypes if np.iinfo(dt).max >= max_count)
                        if channel in channel_to_adj:
                            channel_to_adj[channel].resize((n_nodes, n_nodes))
                            channel_to_adj[channel] += csr_matrix((counts, (srcs, dsts)),
                                                             shape=(n_nodes, n_nodes),
                                                             dtype=dtype)
                        else:
                            channel_to_adj[channel] = csr_matrix((counts, (srcs, dsts)),
                                                             shape=(n_nodes, n_nodes),
                                                             dtype=dtype)
                        # Empty buffer
                        channel_to_edge_to_idx[channel] = {}
                        channel_to_srcs[channel] = []
                        channel_to_dsts[channel] = []
                        channel_to_counts[channel] = []

    if verbose:
        print("loading to dicts took {}".format(time.time() - start_time))
    start_time = time.time()

    n_nodes = len(node_to_idx)
    for channel in channels:
        srcs = channel_to_srcs[channel]
        dsts = channel_to_dsts[channel]
        counts = channel_to_counts[channel]
        if channel in channel_to_adj:
            channel_to_adj[channel].resize((n_nodes, n_nodes))
        if len(counts) == 0:
            continue
        max_count = max(counts)
        dtype = next(dt for dt in dtypes if np.iinfo(dt).max >= max_count)
        if channel in channel_to_adj:
            channel_to_adj[channel] += csr_matrix((counts, (srcs, dsts)),
                                             shape=(n_nodes, n_nodes),
                                             dtype=dtype)
        else:
            channel_to_adj[channel] = csr_matrix((counts, (srcs, dsts)),
                                             shape=(n_nodes, n_nodes),
                                             dtype=dtype)
    if verbose:
        print("converting to sparse mats took {}" \
              .format(time.time() - start_time))

    nodes = sorted(node_to_idx, key=lambda x: node_to_idx[x])

    return nodes, list(channel_to_adj.keys()), list(channel_to_adj.values())

def load_ground_truth(filepath):
    node_to_truth = {}
    with open(filepath) as fin:
        reader = csv.reader(fin)
        next(reader)
        for line in reader:
            node = line[0]
            truth = line[1]
            node_to_truth[node] = truth
    return node_to_truth

def get_graphs(file_getter,
               el_pattern_str,
               gt_pattern_str=None,
               one_el_per_graph=True,
               **from_el_kwargs):
    el_files = file_getter.get_files(el_pattern_str)

    graphs = []

    # if this flag is True, each el_file should be a separate graph
    if one_el_per_graph:
        for el_file in el_files:
            # Here each el_file should be the composite edgelist for a graph
            if gt_pattern_str is not None:
                ground_truth = file_getter.get_file(gt_pattern_str)
                node_to_truth = load_ground_truth(ground_truth)
                nodes, channels, adjs = from_edgelist(
                    el_file, node_to_truth=node_to_truth, **from_el_kwargs)
            else:
                nodes, channels, adjs = from_edgelist(
                    el_file, **from_el_kwargs)

            graphs.append((nodes, channels, adjs))
    else:
        # In this case, each el_file should be a separate channel within a
        # single graph.
        nodes = []
        all_channels = []
        all_adjs = []
        if gt_pattern_str is not None:
            ground_truths = file_getter.get_files(gt_pattern_str)
            if len(ground_truths) == len(el_files):
                for ground_truth, el_file in zip(ground_truths, el_files):
                    node_to_truth = load_ground_truth(ground_truth)
                    nodes, channels, adjs = from_edgelist(el_file, nodes=nodes,
                        node_to_truth=node_to_truth, **from_el_kwargs)
                    all_channels.extend(channels)
                    all_adjs.extend(adjs)
            else:
                raise Exception(
                    "Expected one ground truth file per edgelist file")
        else:
            for el_file in el_files:
                nodes, channels, adjs = from_edgelist(el_file, nodes=nodes,
                                                      **from_el_kwargs)
                all_channels.extend(channels)
                all_adjs.extend(adjs)

        for adj in all_adjs:
            adj.resize(len(nodes), len(nodes))

        graphs.append((nodes, all_channels, all_adjs))

    return graphs

def fill_empty_channels(all_channels, *graph_tuples):
    """
    adds an empty adj mat for any absent channels in each graph tuple
    """
    fixed_tuples = []
    for nodes, channels, adjs in graph_tuples:
        shape = (len(nodes), len(nodes))
        fixed_adjs = []
        for channel in all_channels:
            if channel in channels:
                fixed_adjs.append(adjs[channels.index(channel)])
            else:
                fixed_adjs.append(csr_matrix(shape, dtype=np.uint8))
        fixed_tuples.append((nodes, all_channels, fixed_adjs))

    return fixed_tuples

def get_dataset(file_getter,
                tmplt_from_el_kwargs,
                world_from_el_kwargs,
                from_el_kwargs,
                use_iter_stats=False,
                nl_pattern_str=None):
    cache_dir = file_getter.get_cache_dir()

    if file_getter.cache_exists():
        return load_cache(cache_dir)

    if use_iter_stats:
        from filters.iter_stats_filter import iter_stats_filter, get_node_list_and_channels
        world_file = file_getter.get_file(world_from_el_kwargs["el_pattern_str"])
        if file_getter.ta1_team == "PNNL":
            gt_files = file_getter.get_files(nl_pattern_str)
            node_list, _ = get_node_list_and_channels(gt_files, src_col=0, dst_col=None,
                                      channel_col=None,
                                      delimiter=from_el_kwargs.get("delimiter", ","),
                                      skip_lines=from_el_kwargs.get("skip_lines", 1))
            # Ground truth files for PNNL don't have channel, so we fill it in manually
            version = file_getter.version
            # Note: this is actually number of edge types, not channels
            num_channels = 4 if version == 2 else 6 if version == 4 else 7
            channels = [str(x) for x in range(num_channels)]
        else:
            node_list, channels = get_node_list_and_channels([world_file],
                                      src_col=from_el_kwargs["src_col"],
                                      dst_col=from_el_kwargs["dst_col"],
                                      channel_col=from_el_kwargs["channel_col"],
                                      delimiter=from_el_kwargs.get("delimiter", ","),
                                      skip_lines=from_el_kwargs.get("skip_lines", 1))
        candidates = set()
        tmplt_tuples = get_graphs(**tmplt_from_el_kwargs, **from_el_kwargs, file_getter=file_getter)
        tmplt_tuples = fill_empty_channels(channels, *tmplt_tuples)
        tmplts = [uclasm.Graph(*tt) for tt in tmplt_tuples]

        candidates = iter_stats_filter(tmplts, world_file, node_list, from_el_kwargs)

        if "edge_repair_func" in world_from_el_kwargs:
            old_edge_repair_func = world_from_el_kwargs["edge_repair_func"]
            filtered_edge_repair_func = lambda src, dst, channel: (None, None, None) \
                if src not in candidates or dst not in candidates else old_edge_repair_func(src, dst, channel)
            world_from_el_kwargs["edge_repair_func"] = filtered_edge_repair_func
        else:
            world_from_el_kwargs["edge_repair_func"] = lambda src, dst, channel: (None, None, None) \
                if src not in candidates or dst not in candidates else (src, dst, channel)

    from_el_kwargs["file_getter"] = file_getter
    world_tuples = get_graphs(**world_from_el_kwargs, **from_el_kwargs)
    assert len(world_tuples) == 1
    world = uclasm.Graph(*world_tuples[0])

    tmplt_tuples = get_graphs(**tmplt_from_el_kwargs, **from_el_kwargs)
    tmplt_tuples = fill_empty_channels(world.channels, *tmplt_tuples)

    tmplts = [uclasm.Graph(*tt) for tt in tmplt_tuples]

    save_cache(cache_dir, tmplts, world)

    return tmplts, world

def repair_pnnl_v2(src, dst, channel):
    """
    edges from channel 2 have sometimes been mislabeled as channel 3 somehow
    """
    if channel == "3":
        return src, dst, "2"

    return src, dst, channel

pnnl_v2 = lambda i=7, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="PNNL", version=2, instance=i),
    tmplt_from_el_kwargs={
        "el_pattern_str": "*Composite*-sigonly*.rdf",
        "gt_pattern_str": "*SignalMapping*.csv"},
    world_from_el_kwargs={"el_pattern_str": "*Composite*-sig-*.rdf"},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 2,
        "channel_col": 1,
        "delimiter": "\t",
        "skip_lines": 0,
        "edge_repair_func": repair_pnnl_v2,
        "verbose": verbose})

pnnl_v3 = lambda i=0, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="PNNL", version=3, instance=i),
    tmplt_from_el_kwargs={"el_pattern_str": "CompositeSignal-*/*.csv"},
    world_from_el_kwargs={"el_pattern_str": "Composite-*/*.csv"},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 2,
        "channel_col": 1,
        # "edge_repair_func": repair_pnnl_v4,
        "verbose": verbose})

def repair_pnnl_v4(src, dst, channel):
    """
    pnnl v4 data has self edges only on signal nodes. get rid of them.
    """
    if src == dst:
        return None, None, None

    return src, dst, channel

pnnl_v4 = lambda i=0, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="PNNL", version=4, instance=i),
    tmplt_from_el_kwargs={"el_pattern_str": "*Merged*.csv"},
    world_from_el_kwargs={"el_pattern_str": "*Composite*.csv"},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 2,
        "channel_col": 1,
        "edge_repair_func": repair_pnnl_v4,
        "verbose": verbose})

pnnl_v5 = lambda i=0, model="10K", verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="PNNL", version=5, model=model, instance=i),
    tmplt_from_el_kwargs={"el_pattern_str": "*Merged*.csv"},
    world_from_el_kwargs={"el_pattern_str": "*Composite*.csv"},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 2,
        "channel_col": 1,
        "verbose": verbose,
        "cycle_buffer": True},
    use_iter_stats=True,
	nl_pattern_str="*GroundTruth*.csv")

pnnl_v6 = lambda i=0, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="PNNL", version=6, instance=i),
    tmplt_from_el_kwargs={"el_pattern_str": "*Merged*.csv"},
    world_from_el_kwargs={"el_pattern_str": "*Composite*.csv"},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 2,
        "channel_col": 1,
#        "edge_repair_func": repair_pnnl_v4,
        "verbose": verbose})

pnnl_rw = lambda i=0, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="PNNL", version="RW"),
    tmplt_from_el_kwargs={"el_pattern_str": "FullSignalTemplate.csv"},
    world_from_el_kwargs={"el_pattern_str": "Composite.csv"},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 2,
        "channel_col": 1,
        "verbose": verbose})

def set_noisy_cache_dir(net_file_getter):
    # TODO: fix this later
    net_file_getter.ta1_team = "PNNL_RW_NOISY"
    return net_file_getter

pnnl_rw_noisy = lambda i=0, verbose=True: get_dataset(
    file_getter=set_noisy_cache_dir(NetFileGetter(ta1_team="PNNL", version="RW")),
    tmplt_from_el_kwargs={"el_pattern_str": "FullSignalTemplate.csv"},
    world_from_el_kwargs={"el_pattern_str": "NoisyComposite.csv"},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 2,
        "channel_col": 1,
        "verbose": verbose})

gordian_v4 = lambda model, i, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="GORDIAN", version=4,
                              model=model, instance=i),
    tmplt_from_el_kwargs={
        "el_pattern_str": "signal/aligned/*.csv",
        "one_el_per_graph": False},
    world_from_el_kwargs={
        "el_pattern_str": "background_signal/aligned/*.csv",
        "one_el_per_graph": False},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 1,
        "channel_col": 2,
        "verbose": verbose})

gordian_v4_agent_based = lambda i=5, verbose=True: gordian_v4(
    "agent-based", i, verbose=verbose)
gordian_v4_probabilistic = lambda i=5000, verbose=True: gordian_v4(
    "probabilistic", i, verbose=verbose)

def get_str_alignment(alignment, alignment_file, channels=range(5)):
    """ Load the alignment across channels sent to us by STR """
    # Maps tuples of (actor_id, channel) to merged_id
    with open(alignment_file) as fin:
        reader = csv.reader(fin)
        next(reader) # Skip header line
        for line in reader:
            merged_id = line[0]
            actor_idA = line[1]
            actor_idB = line[2]
            channelA = int(line[3])
            channelB = int(line[4])
            if not (actor_idA, channelA) in alignment:
                alignment[(actor_idA, channelA)] = merged_id
            if not (actor_idB, channelB) in alignment:
                alignment[(actor_idB, channelB)] = merged_id
    # Create dummy alignments for Facebook, Youtube, Twitter
    for website in ["www.youtube.com", "www.twitter.com", "www.facebook.com"]:
        new_id = len(set(alignment.values()))
        for channel in channels:
            alignment[(website, channel)] = new_id
    return alignment

# This uclasmcode uses a feature of Python default function argument values
# When a default argument is set that is a reference, all functions called
# with the default will default to the same reference, and thus the same object
def align_edge_str(src, dst, channel, alignment_file, alignment={}):
    if len(alignment) == 0:
        get_str_alignment(alignment, alignment_file)
    new_ids = []
    for node in [src, dst]:
        found = False
        if (node, channel) in alignment:
            new_ids.append(alignment[(node, channel)])
            found = True
        else:
            # Search for nodes with same ID in other channels
            for channel2 in range(5): # TODO: make more general
                if (node,channel2) in alignment:
                    found = True
                    new_ids.append(alignment[(node, channel2)])
                    break
        if not found:
            print("{} not found in alignment".format((node,channel)))
            new_ids.append(None)
    if None not in new_ids:
        return new_ids[0], new_ids[1], channel
    return None, None, None

def set_str_cache_dir(net_file_getter, consistent):
    # TODO: fix this later
    net_file_getter.ta1_team = "GORDIAN_STR" + ("_CONSISTENT" if consistent else "")
    return net_file_getter

gordian_v4_str = lambda consistent=False: get_dataset(
    file_getter=set_str_cache_dir(NetFileGetter(ta1_team="GORDIAN", version=4,
                              model="probabilistic", instance=5000), consistent=consistent),
    tmplt_from_el_kwargs={
        "el_pattern_str": "signal/aligned/*.csv",
        "one_el_per_graph": False},
    world_from_el_kwargs={
        "el_pattern_str": "background_signal/unaligned/*.csv",
        "one_el_per_graph": False,
        "edge_repair_func": lambda src, dst, channel: align_edge_str(src, dst, channel,
    alignment_file = "/s2/scr/reu_data/darpa_maa/data/GORDIAN/V4_STR/"+
        ("consistent_alignment.csv" if consistent else "nccv4probabilistic5k.csv")
    )},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 1,
        "channel_col": 2,
        "verbose": True})

gordian_v5 = lambda i, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="GORDIAN", version=5,
                              instance=i),
    tmplt_from_el_kwargs={
        "el_pattern_str": "signal/*_aligned.csv",
        "one_el_per_graph": False},
    world_from_el_kwargs={
        "el_pattern_str": "background_signal/aligned/*.csv",
        "one_el_per_graph": False},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 1,
        "channel_col": 2,
        "verbose": verbose})

gordian_v6 = lambda model="batch-1", i=50, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="GORDIAN", version=6,
                              model=model, instance=i),
    tmplt_from_el_kwargs={
        "el_pattern_str": "signal/*_aligned.csv",
        "one_el_per_graph": False},
    world_from_el_kwargs={
        "el_pattern_str": "background_signal/aligned/*.csv",
        "one_el_per_graph": False},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 1,
        "channel_col": 2,
        "verbose": verbose})

def get_str_alignment_v7(alignment, alignment_file, channels=range(11)):
    """ Load the alignment across channels sent to us by STR """
    # Maps tuples of (actor_id, channel) to merged_id
    with open(alignment_file) as fin:
        reader = csv.reader(fin)
        for line in reader:
            merged_id = line[0]
            channel = line[1]
            personNumber = line[2]
            generated_id = line[3]
            isSignalActor = line[4]
            if (generated_id, channel) not in alignment:
                alignment[(generated_id, channel)] = merged_id
    # Create dummy alignments for Facebook, Youtube, Twitter
    # for website in ["www.youtube.com", "www.twitter.com", "www.facebook.com"]:
    #     new_id = len(set(alignment.values()))
    #     for channel in channels:
    #         alignment[(website, channel)] = new_id
    return alignment

# This uclasmcode uses a feature of Python default function argument values
# When a default argument is set that is a reference, all functions called
# with the default will default to the same reference, and thus the same object
def align_edge_str_v7(src, dst, channel, alignment_file, alignment={}):
    if len(alignment) == 0:
        get_str_alignment_v7(alignment, alignment_file)
    new_ids = []
    for node in [src, dst]:
        found = False
        if (node, channel) in alignment:
            new_ids.append(alignment[(node, channel)])
            found = True
        else:
            # Search for nodes with same ID in other channels
            for channel2 in range(11): # TODO: make more general
                if (node, channel2) in alignment:
                    found = True
                    new_ids.append(alignment[(node, channel2)])
                    break
        if not found:
            print("{} not found in alignment".format((node,channel)))
            new_ids.append(None)
    if None not in new_ids:
        return new_ids[0], new_ids[1], channel
    return None, None, None

gordian_v7 = lambda model=1, i=100, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="GORDIAN", version=7,
                                model="batch-"+str(model), instance=i),
    tmplt_from_el_kwargs={
        "el_pattern_str": "signal/*_aligned.csv",
        "one_el_per_graph": False},
    world_from_el_kwargs={
        "el_pattern_str": "background_signal/unaligned/*.csv",
        "one_el_per_graph": False,
        "edge_repair_func": lambda src, dst, channel: align_edge_str_v7(src, dst, channel,
                            alignment_file = "/s1/scr/reu_data2/darpa_maa/data/GORDIAN/V7/100K-nodes/batch-"+
                            str(model)+"/identity_map/identity_map_"+str(model)+".csv")},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 1,
        "channel_col": 2,
        "verbose": verbose})

def repair_ivysys(src, dst, channel):
    """
    scrape the actual channel from the edgeid column, which we pretend is the
    channel column
    """
    for ch in ["Comm", "Fin", "Log", "Ema", "Sear"]:
        if ch in channel:
            return src, dst, ch

    print("broken line:", src, dst, channel)
    return None, None, None

ivysys_v4 = lambda version=4, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="IVYSYS", version=version),
    tmplt_from_el_kwargs={
        "el_pattern_str": "*threat-ground-truth.csv",
        "src_col": 2,
        "dst_col": 4,
        "channel_col": 1},
    world_from_el_kwargs={
        "el_pattern_str": "*Tx*.csv",
        "gt_pattern_str": "*Acct*.csv",
        "one_el_per_graph": False,
        "src_col": 1,
        "dst_col": 2,
        "channel_col": 0},
    from_el_kwargs={
        "edge_repair_func": repair_ivysys,
        "verbose": verbose})

ivysys_v6 = lambda version=6, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="IVYSYS", version=version),
    tmplt_from_el_kwargs={
        "el_pattern_str": "*threat-ground-truth.csv",
        "src_col": 2,
        "dst_col": 4,
        "channel_col": 1},
    world_from_el_kwargs={
        "el_pattern_str": "*Tx*.csv",
        "one_el_per_graph": False,
        "src_col": -2,
        "dst_col": -1,
        "channel_col": 0},
    from_el_kwargs={
        "edge_repair_func": repair_ivysys,
        "verbose": verbose})

ivysys_v7 = lambda verbose=True: ivysys_v6(version=7, verbose=verbose)

# Use same settings for V8 and V9
ivysys_v8 = lambda verbose=True: ivysys_v6(version=8, verbose=verbose)

ivysys_v9 = lambda verbose=True: ivysys_v6(version=9, verbose=verbose)

ivysys_v11 = lambda version=11, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="IVYSYS", version=version),
    tmplt_from_el_kwargs={
        "el_pattern_str": "*threat-ground-truth.csv",
        "src_col": 2,
        "dst_col": 4,
        "channel_col": 1},
    world_from_el_kwargs={
        "el_pattern_str": "*Tx*.csv",
        "gt_pattern_str": "*Acct*.csv",
        "one_el_per_graph": False,
        "src_col": -2,
        "dst_col": -1,
        "channel_col": 0},
    from_el_kwargs={
        "edge_repair_func": repair_ivysys,
        "verbose": verbose})

ivysys_v12 = lambda verbose=True: ivysys_v11(version=12, verbose=verbose)

transportation = lambda i=0, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="EXAMPLE", version=0, instance=i),
    tmplt_from_el_kwargs={"el_pattern_str": "transportation_template.csv"},
    world_from_el_kwargs={"el_pattern_str": "transportation_world.csv"},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 1,
        "channel_col": 2,
        "verbose": verbose})

foodweb = lambda i=0, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="EXAMPLE", version=1, instance=i),
    tmplt_from_el_kwargs={"el_pattern_str": "foodweb_template.csv"},
    world_from_el_kwargs={"el_pattern_str": "foodweb_world.csv"},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 1,
        "channel_col": 2,
        "verbose": verbose})

bench_mark = lambda i=0, verbose=True: get_dataset(
    file_getter=NetFileGetter(ta1_team="EXAMPLE", version=2, instance=i),
    tmplt_from_el_kwargs={"el_pattern_str": "bench_mark_template.csv"},
    world_from_el_kwargs={"el_pattern_str": "bench_mark_world.csv"},
    from_el_kwargs={
        "src_col": 0,
        "dst_col": 1,
        "channel_col": 2,
        "verbose": verbose})
