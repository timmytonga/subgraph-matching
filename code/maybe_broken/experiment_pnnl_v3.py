from utils import data
import uclasm

tmplts, world = data.pnnl_v3(0)
print("there are", len(tmplts), "templates")

import IPython
IPython.embed()
