from utils import data
import uclasm

tmplts, world = data.ivysys_v8()
tmplt = tmplts[0]

uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)

# import IPython
# IPython.embed()
