import numpy as np
import seaborn as sns
import math
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import sys
sys.path.append('../')
import uclasm

from . import results_dir

def plot_heatmap(candidates, data_name, cache=None):
    """
    Plot the heatmap of number of candidates shared by template nodes
    """
    if cache is not None:
        candidates = \
            np.load('/s2/scr/reu_data/darpa_maa/Qinyi/saved_data/{}_after_elim_candidates.npy'.format(cache))

    cands = candidates.sum(axis=1)
    x = sorted(range(candidates.shape[0]), key=lambda idx: cands[idx])

    # First re-arrange is_cand by the number of candidates
    is_cand = np.array([candidates[i,:] for i in x])

    f = lambda i, j: len(np.intersect1d(is_cand[i,:].nonzero()[0],is_cand[j,:].nonzero()[0]))
    matrix = np.fromfunction(np.vectorize(f), (candidates.shape[0], candidates.shape[0]), dtype=int)+1

    sns.set()
    log_norm = LogNorm(vmin=matrix.min().min(), vmax=matrix.max().max())
    cbar_ticks = [math.pow(10, i) for i in range(math.floor(math.log10(matrix.min().min())), \
                                                1+math.ceil(math.log10(matrix.max().max())))]
    ax = sns.heatmap(matrix, norm=log_norm,cbar_kws={"ticks": cbar_ticks})
    plt.title('Number of Candidates Shared by the Template Nodes', fontsize=10)
    plt.savefig("{}/{}_heatmap.png".format(results_dir, data_name))
