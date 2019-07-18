"""
test the filters and data loaders on the first instance from each dataset by running

    python run_tests.py
    
if you want to skip any datasets (for example, pnnl v3), pass the names of the
datasets you would like to skip as command line arguments. For example, to skip
pnnl v3:

    python run_tests.py pnnl_v3
"""

from utils import data
import uclasm
from inspect import getmembers, isfunction
import time
import sys

# TODO: test counting

if __name__ == "__main__":
    for func_name, get_graphs in getmembers(data, isfunction)[::-1]:
        if func_name in sys.argv:
            continue
        
        # Ensures every member function of data corresponds to a dataset
        try:
            start_time = time.time()
            print("loading from", func_name.replace("_", " "), end="", flush=1)
            tmplts, world = get_graphs(verbose=False)
            print(" took", time.time() - start_time, "seconds.")
        except KeyboardInterrupt:
            print("skipping", func_name)
            continue

        for tmplt in tmplts:
            world_copy = world.copy()
            
            try:
                start_time = time.time()
                print("filtering", func_name.replace("_", " "), end="", flush=1)
                all_filters(tmplt, world_copy, verbose=False)
                print(" took", time.time() - start_time, "seconds.")
            except KeyboardInterrupt:
                print("skipping filters")
            
            for tmplt_node in tmplt.nodes:
                candidates = tmplt.candidate_sets[tmplt_node]
                
                # Check if the filter actually filtered anything out
                if len(candidates) == len(world_copy.nodes):
                    print("node", tmplt_node, "has every world node as a cand")
                    
                # Check if filter killed any signal nodes
                if tmplt_node not in candidates:
                    print("node", tmplt_node,
                          "in world is not a cand for", tmplt_node,
                          "in tmplt.")
            
