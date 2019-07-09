import numpy as np
import matplotlib.pyplot as plt
from utils import data
import uclasm
from filters.elimination_filter import elimination_filter

tmplts, world = data.ivysys_v7()
tmplt = tmplts[0]

uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)

x = tmplt.node_idxs_ordered_by_cands()
cands_before_elim = np.sum(tmplt.is_cand, axis=1)

elimination_filter(tmplt, world)
cands_after_elim = np.sum(tmplt.is_cand, axis=1)

y = np.arange(len(x))
cands1 = np.array([cands_before_elim[i] for i in x])
cands2 = np.array([cands_after_elim[i] for i in x])

plt.figure()
plt.bar(y, height=cands1, align='center', color='b', alpha=0.5, label='Statistics, Topology Filter')
plt.bar(y, height=cands2, align='center', color='r', alpha=0.5, label='Statistics, Topology, Elimination Filter')
plt.xlabel('Template Node No.', fontsize=10)
plt.ylabel('Number of Candidate Nodes', fontsize=10)
plt.title('Number of Candidates for Each Template Node Before v.s. After Elimination Filter', fontsize=10)
plt.legend()
plt.tight_layout()
plt.savefig('ivysys_cands')

import IPython
IPython.embed()
