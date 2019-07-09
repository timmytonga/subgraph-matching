from utils import data
from filters.all_filters import all_filters
import random

"""
candidates_of_hub = {'0','1','12','14','15','18','19','2','20','21','24','27',
'29','3','32','33','35','36','37','4','40','41','42','44','45','48','49','5',
'50','52','54','57','58','6','60','61','62','66','7','8','9'}

"""
# # The following are used to get valid choices of node 169 given different
# # choices of node 4:
#
# nodes_of_interest = {'0', '1', '2', '24', '3', '4', '48', '5', '6', '7'}
# result = {}
#
# for node in nodes_of_interest:
#
#     tmplts, world = data.ivysys_v7()
#     tmplt = tmplts[0]
#
#     tmplt.update_node_candidates("4", [node])
#     all_filters(tmplt, world, verbose=False, neighborhood=False)
#     print ("set node 4 to", node)
#
#     cand169 = tmplt.candidate_sets["169"].copy()
#
#     worked = set()
#
#     for cand in cand169:
#
#         tmplts, world = data.ivysys_v7()
#         tmplt = tmplts[0]
#         tmplt.update_node_candidates("4", [node])
#         tmplt.update_node_candidates("169", [cand])
#         all_filters(tmplt, world, verbose=False, neighborhood=False)
#
#         if len(tmplt.candidate_sets["50"]) > 0:
#             # tmplt.summarize_candidate_sets()
#             print ("Work for", cand)
#             worked.add(cand)
#         else:
#             print ("Choosed", cand, "and it won't work")
#
#     result[node] = worked


candidates_of_hub = {'5', '3'}
result = {'5': {'0', '7'},
          '3': {'0', '15', '19', '5', '6'}}
"""
result = {'0': {'19', '3', '4', '5', '6', '7'},
          '5': {'0', '7'},
          '24': {'7'},
          '2': {'6', '7'},
          '3': {'0', '15', '19', '5', '6'},
          '6': {'0', '1', '19', '2', '24', '3', '4', '7'}
          }
"""

have_isomorphisms = set()
no_isomorphisms = set()

for cand in candidates_of_hub:

    iter = 0
    while iter < 50:

        tmplts, world = data.ivysys_v7()
        tmplt = tmplts[0]

        # choose a candidate for "4"
        print ("Start the experiment by setting 4 =", cand)
        tmplt.update_node_candidates("4", [cand])
        all_filters(tmplt, world, verbose=False, neighborhood=False)

        iter += 1
        print ("Experiment", iter, "for 4 =", cand)
        failat = "-1"

        # Check by specifying the center node
        # tmplt.update_node_candidates("4", ["4"])
        # all_filters(tmplt, world, verbose=False)
        print("Now start random selection")

        for n in ["169", "50", "127", "20", "384", "2328", "1", "264", "325",
                  "43", "208", "0", "227", "2"]:
        # for n in ["50", "169", "127", "20", "384", "2328", "1", "264", "325",
        #           "43", "208", "0", "227", "2"]:
            # If fails at some nodes
            if len(tmplt.candidate_sets[n]) == 0:
                print ("failed at the selection of", n)
                failat = n
                break

            # If we are selectint the second node, we select fron nodes
            # we already know that would work
            if n == "169":
                rand = random.choice(tuple(result[cand]))
            else:
                rand = random.choice(tuple(tmplt.candidate_sets[n]))

            tmplt.update_node_candidates(n, [rand])
            print("randomly select", rand, "as the candidate for", n)
            all_filters(tmplt, world, verbose=False, neighborhood=False)

        if failat == "169":
            # Choosing the candidate to 4 alone leads to no isomorphisms
            print ("This choice of node 4 have no isomorpisms")
            no_isomorphisms.add(cand)
            break
        elif failat == "-1":
            # we've run through all random selections and found an isomorphism
            print ("Succeeded in finding an isomorphism")
            have_isomorphisms.add(cand)
            tmplt.summarize_candidate_sets()
            break
        else:
            print ("Now try again")


import IPython
IPython.embed()

# tmplt.update_node_candidates("4",["7"])
# tmplt.update_node_candidates("169",["5"])
# tmplt.update_node_candidates("50",["0"])
# tmplt.update_node_candidates("127",["8"])
# tmplt.update_node_candidates("20",["3"])
# tmplt.update_node_candidates("384",["61"])
# tmplt.update_node_candidates("2328",["23"])
# tmplt.update_node_candidates("1",["6"])
# tmplt.update_node_candidates("264",["45"])
# tmplt.update_node_candidates("325",["541"])
# tmplt.update_node_candidates("43",["16"])
# tmplt.update_node_candidates("208",["29"])
# tmplt.update_node_candidates("0",["33"])
# tmplt.update_node_candidates("227",["48"])
# tmplt.update_node_candidates("137",["20"])
