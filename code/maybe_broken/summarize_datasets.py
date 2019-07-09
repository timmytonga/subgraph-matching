from utils import data
import uclasm
from filters.counting import count_isomorphisms

import time
import numpy as np
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt
plt.switch_backend('agg')

"""
We summarize all the info we have on a dataset.
python summarize_datasets.py > dataset_info.txt
"""

# Note: I made certain changes in all_filter (have it return the sequence of filter)
# TODO: need to change counting such that it quits after a certain amt of time

def summarize_dataset(tmplt, world, dataset_name, tmplt_ind=0, counting=False):

    print ("Now summarizing tmplt {} of {}\n".format(tmplt_ind, dataset_name))

    # Run filtering
    start_time = time.time()
    filters_used = all_filters(tmplt, world, verbose=False)
    print ("Filtering took --- %s seconds ---" % (time.time() - start_time))
    tmplt.summarize_candidate_sets()
    print ("The filters used are:", filters_used)
    print ("Stats filter:", filters_used.count('stats'))
    print ("Topology filter:", filters_used.count('topology'))

    print ("Number of world nodes:", len(world.nodes))
    print ("Number of tmplt nodes:", len(tmplt.nodes))
    print ("Number of world edges:", np.sum(world.composite_adj))
    print ("Number of tmplt edges:", np.sum(tmplt.composite_adj))
    print ("Number of distinct world edges:", world.composite_adj.count_nonzero())
    print ("Number of distinct tmplt edges:", tmplt.composite_adj.count_nonzero())
    print ("Number of channels:", len(world.channels))

    for i in range(len(world.channels)):
        print ("Number of world edges in channel %d:" %(i), np.sum(world.adjs[i]))
        print ("Number of tmplt edges in channel %d:" %(i), np.sum(tmplt.adjs[i]))

    # Plot candidates
    
    tmplt.plot()
    plt.savefig(dataset_name+"_tmplt"+str(tmplt_ind)+"_cands.png")

    # Counting isomorphism
    # if counting:
    #     start_time = time.time()
    #     count = count_isomorphisms(tmplt, world, verbose=False)
    #     print ("There are {} isomorphisms".format(count))
    #     print ("Counting took --- %s seconds ---" % (time.time() - start_time))

    # Check whether any template nodes are permutable
    permutability = tmplt.get_permutability()
    permutable_lsts = []
    num_of_perm_nodes = np.sum(permutability, axis=0)

    # Categroize the permutable nodes
    for i in range(len(tmplt.nodes)):
        if num_of_perm_nodes[i] > 1:
            lst = np.nonzero(permutability[i])[0].tolist()
            if lst not in permutable_lsts:
                permutable_lsts.append(lst)

    print ("Nodes with permutability:")
    for node_lst in permutable_lsts:
        print ([tmplt.nodes[i] for i in node_lst])

    # If the length of set of permutabel nodes is the same as the number
    # of their candidates, we can then assign them their true identities

    used_permutation = False
    for node_lst in permutable_lsts:
        ind = node_lst[0]
        cands = tmplt.candidate_sets[tmplt.nodes[ind]]
        if len(cands) == len(node_lst):
            used_permutation = True
            for node in node_lst:
                tmplt.update_node_candidates(str(tmplt.nodes[node]),[str(tmplt.nodes[node])])
                print ("Assigned node {} its true identity".format(tmplt.nodes[node]))
        else:
            continue

    if used_permutation:
        all_filters(tmplt, world, verbose=False)
        print ("Candidate sets after dealing with permutatable nodes:")
        tmplt.summarize_candidate_sets()

    if counting:
        start_time = time.time()
        count = count_isomorphisms(tmplt, world, verbose=False)
        print ("There are {} isomorphisms".format(count))
        print ("Counting took --- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    # for dataset, name in zip(data.all, data.names):
    #     tmplts, world = dataset()
        # for i in range(len(tmplts)):
        #     tmplt = tmplts[i]
        #     summarize_dataset(tmplt, world, name, tmplt_ind=i)

    tmplts, world = data.pnnl_v4(0)
    for i in range(len(tmplts)):
        tmplt = tmplts[i]
        summarize_dataset(tmplt, world, 'pnnl_v4', tmplt_ind=i, counting=True)
