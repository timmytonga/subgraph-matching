from utils import data
import uclasm

tmplts, world = data.ivysys_v4()
tmplt = tmplts[0]

uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)

import IPython
IPython.embed()
