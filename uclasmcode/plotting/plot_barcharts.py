import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
import uclasm

from . import results_dir
print(results_dir)

from filters.validation_filter import validation_filter

def plot_barcharts(tmplt, world, data_name, cache=None, validation=False):
    """
    Plot (1) number of candidates of each template node (2) number of template
    nodes that each world node is the candidate of
    """

    filters = [uclasm.stats_filter]
    tmplt, world, candidates = uclasm.run_filters(tmplt, world, filters=filters,
                                                  verbose=True, reduce_world=False)
    cands_stats = candidates.sum(axis=1)
    cinvs_stats = candidates.sum(axis=0)

    filters.append(uclasm.topology_filter)
    tmplt, world, candidates = uclasm.run_filters(tmplt, world, candidates=candidates,
                                                  filters=filters, verbose=True, reduce_world=False)
    cands_topo = candidates.sum(axis=1)
    cinvs_topo = candidates.sum(axis=0)

    if cache is not None:
        print ("Saved data read.")
        candidates = \
            np.load('/s2/scr/reu_data/darpa_maa/Qinyi/saved_data/{}_after_elim_candidates.npy'.format(cache))
        # candidates = np.load(cache)
    else:
        filters.append(uclasm.elimination_filter)
        tmplt, world, candidates = uclasm.run_filters(tmplt, world, candidates=candidates, filters=filters, reduce_world=False)

    cands_elim = candidates.sum(axis=1)
    cinvs_elim = candidates.sum(axis=0)

    if validation == True:
        if cache is not None:
            print ("Saved data read.")
            candidates = \
                np.load('/s2/scr/reu_data/darpa_maa/Qinyi/saved_data/{}_after_valid_candidates.npy'.format(cache))
            # candidates = np.load(cache)
        else:
            tmplt, world, candidates = validation_filter(tmplt, world, candidates=candidates, verbose=False, reduce_world=False)

        cands_valid = candidates.sum(axis=1)
        cinvs_valid = candidates.sum(axis=0)

    # TODO: Add order without validation filter
    # Sort by # of candidates left after elim, topo, stats
    if validation == True:
        order_tmplt = sorted(range(len(tmplt.nodes)), \
            key=lambda idx: (cands_valid[idx], cands_elim[idx], \
                            cands_topo[idx], cands_stats[idx]))

        order_world = sorted(range(len(world.nodes)), \
            key=lambda idx: (cinvs_valid[idx], cinvs_elim[idx], \
                            cinvs_topo[idx], cinvs_stats[idx]))
    else:
        order_tmplt = sorted(range(len(tmplt.nodes)), \
            key=lambda idx: (cands_elim[idx], \
                            cands_topo[idx], cands_stats[idx]))

        order_world = sorted(range(len(world.nodes)), \
            key=lambda idx: (cinvs_elim[idx], \
                            cinvs_topo[idx], cinvs_stats[idx]))

    # Reorganize the candidates
    cands_stats = np.array([cands_stats[i] for i in order_tmplt])
    cands_topo = np.array([cands_topo[i] for i in order_tmplt])
    cands_elim = np.array([cands_elim[i] for i in order_tmplt])

    cinvs_stats = np.array([cinvs_stats[i] for i in order_world])
    cinvs_topo = np.array([cinvs_topo[i] for i in order_world])
    cinvs_elim = np.array([cinvs_elim[i] for i in order_world])

    # Keep only the world nodes that are still candidates to at least one tmplt node after topology filter
    world_to_keep = np.nonzero(cinvs_topo)[0]
    cinvs_stats = cinvs_stats[world_to_keep]
    cinvs_topo = cinvs_topo[world_to_keep]
    cinvs_elim = cinvs_elim[world_to_keep]

    if validation:
        cands_valid = np.array([cands_valid[i] for i in order_tmplt])
        cinvs_valid = np.array([cinvs_valid[i] for i in order_world])
        cinvs_valid = cinvs_valid[world_to_keep]

    y1 = np.arange(len(tmplt.nodes))
    y2 = np.arange(len(world_to_keep))

    # Plot tmplt bars
    plt.figure()
    plt.rcParams.update({'font.size': 16})
    plt.rcParams["font.family"] = "DejaVu Serif"
    plt.bar(y1, height=cands_stats, align='center', color='royalblue', \
                alpha=1, width=1, label='Statistics')
    plt.bar(y1, height=cands_topo,  align='center', color='lightseagreen', \
                alpha=1, width=1, label='Statistics, Topology')
    plt.bar(y1, height=cands_elim, align='center', color='red', \
                alpha=1, width=1, \
                label='Statistics, Topology,\nElimination')
    if validation:
        plt.bar(y1, height=cands_valid, align='center', color='orange', \
                    alpha=1, width=1, \
                    label='Statistics, Topology,\nElimination, Validation')
    plt.yscale('log')
    plt.xlabel('Template Node No.', fontsize=16)
    plt.ylabel('Number of Candidates', fontsize=16)
    # plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.4), ncol=1, fancybox=True, shadow=True)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig('{}/{}_tmplt_bars.png'.format(results_dir, data_name), bbox_inches='tight')
    plt.close()

    # Plot world bars
    plt.figure()
    plt.bar(y2, height=cinvs_stats, align='center', color='royalblue', \
                alpha=1, width=1, label='Statistics')
    plt.bar(y2, height=cinvs_topo, align='center',color='lightseagreen', \
                alpha=1, width=1, label='Statistics, Topology')
    plt.bar(y2, height=cinvs_elim, align='center', color='red', \
                alpha=1, width=1, \
                label='Statistics, Topology,\nElimination')
    if validation:
        plt.bar(y2, height=cinvs_valid, align='center', color='orange', \
                    alpha=1, width=1,
                    label='Statistics, Topology,\nElimination, Validation')
    plt.xlabel('World Node No.', fontsize=16)
    plt.ylabel('Number of Template Nodes', fontsize=16)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig('{}/{}_world_bars.png'.format(results_dir, data_name),bbox_inches='tight')
    plt.close()
