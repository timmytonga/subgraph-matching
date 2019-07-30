from uclasmcode import equivalence_partition
from uclasmcode.utils import data
import uclasmcode.uclasm as uclasm
import time

verbose = True


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_stats(partition, graph, detailed=True, name=False):
    equiv_classes = partition.classes()
    # compute some stats
    print("==== GENERAL-STATS =====")
    # the number of nodes
    print("Total number of original nodes: " + str(len(partition))    )
    # the number of equiv classes
    print("Total number of equiv classes: " + str(len(equiv_classes)))
    # compression percentage
    compression_percentage = 1- len(equiv_classes)/len(partition)
    print("Compression percentage (1 - equiv_classes/total_number_of_nodes): %4.2f"%(compression_percentage))
    equiv_classes = partition.classes()
    equiv_classes_name = []
    for s in equiv_classes:
        equiv_classes_name.append({graph.nodes[i] for i in s})
    if detailed:
        print("===== EQUIVALENCE CLASSES ===== ")
        if name:
            print(equiv_classes_name)
        else:
            print(equiv_classes)

    print("===== NON-TRIVIAL EQUIV CLASSES ===== ")
    non_triv = [i for i in equiv_classes if len(i) > 1]
    non_triv_name = []
    for s in non_triv:
        non_triv_name.append({graph.nodes[i] for i in s})
    if detailed:
        if name:
            print(non_triv_name)
        else:
            print(non_triv)
    print("Number of non-trivial equiv classes: %d"%len(non_triv))

    sizes = [len(l) for l in non_triv]
    if detailed:
        print("Sizes of equiv classes: "+ str(sizes))
        print("Largest equiv size: %d"%(max(sizes)))


def compute_non_trivial(adj_matrix):
    result = []
    for i in range(adj_matrix.shape[0]):
        if adj_matrix[i].any() or adj_matrix[:,i].any():
            result.append(i)
    return result


def experiment(graph):
    print("Size of graph: " + str(graph.n_nodes))
    results = {}  # stores 'ch': partition
    time_mat = {}  # stores 'ch' : time to compute partition

    # to compute non-trivial
    non_triv = {}

    for ch, sparse_mat in graph.ch_to_adj.items():
        # preprocessing
        adj_matrix = sparse_mat.toarray()  # this might be too big for certain dataset
        # compute non-triv
        non_triv[ch] = compute_non_trivial(adj_matrix)
        # compute equivalence classes
        start_time = time.time()
        results[ch] = equivalence_partition.partition_vertices(adj_matrix)
        time_mat[ch] = time.time() - start_time  # save the time took to compute the partition
        print("Finished channel: " + ch + ". Took %5f seconds" % (time_mat[ch]))

    equivpartition = equivalence_partition.combine_channel_equivalence(results)
    return equivpartition


def test_tim_test_graph_1():
    print("Starting data loading")
    start_time = time.time()
    tmplts, world = data.tim_test_graph_1()
    tmplt = tmplts[0]
    print("Loading took {} seconds".format(time.time() - start_time))

    part = experiment(tmplt)
    print_stats(part, tmplt, True, True)
    assert len(part.classes()) == 2
    non_triv = [len(i) for i in part.classes() if len(i) > 1]
    assert sorted(non_triv) == [2, 2]



