import os
from glob import glob
import pickle
import numpy as np
from scipy import sparse
import sys
sys.path.append("..")
import uclasmcode.uclasm as uclasm

WORLD_PREFIX = "world"
TMPLT_PREFIX = "tmplt_{}"

def get_filenames(dirpath, prefix):
    return os.path.join(dirpath, prefix+"_nodes.npy"), \
           os.path.join(dirpath, prefix+"_channels.p"), \
           os.path.join(dirpath, prefix+"_channel_{}_adj.npz")

def save_graph(dirpath, prefix, graph):
    nodes_fp, channels_fp, adjs_fp = get_filenames(dirpath, prefix)

    np.save(nodes_fp, graph.nodes)
    pickle.dump(list(graph.channels), open(channels_fp, "wb"))
    for channel, adj in zip(graph.channels, graph.adjs):
        sparse.save_npz(adjs_fp.format(channel), adj)

def load_graph(dirpath, prefix):
    nodes_fp, channels_fp, adjs_fp = get_filenames(dirpath, prefix)

    nodes = np.load(nodes_fp)
    channels = pickle.load(open(channels_fp, "rb"))
    adjs = [sparse.load_npz(adjs_fp.format(channel)) for channel in channels]

    return nodes, channels, adjs

def save_candidates(dirpath, prefix, tmplt):
    np.save(os.path.join(dirpath, prefix+'_candidates.npy'), tmplt.is_cand)

def load_candidates(dirpath, prefix):
    return np.load(os.path.join(dirpath, prefix+'_candidates.npy'))

def save_cache(dirpath, tmplts, world):
    os.makedirs(dirpath, exist_ok=True)

    save_graph(dirpath, WORLD_PREFIX, world)

    for i, tmplt in enumerate(tmplts):
        save_graph(dirpath, TMPLT_PREFIX.format(i), tmplt)

def load_cache(dirpath):
    world = uclasm.Graph(*load_graph(dirpath, WORLD_PREFIX))
    i = 0
    tmplts = []
    while True:
        try:
            graph_tuple = load_graph(dirpath, TMPLT_PREFIX.format(i))
            tmplts.append(uclasm.Graph(*graph_tuple))
            i += 1
        except FileNotFoundError:
            break
    return tmplts, world
