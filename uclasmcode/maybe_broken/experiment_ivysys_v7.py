from utils import data
from filters.all_filters import all_filters

tmplts, world = data.ivysys_v7()
tmplt = tmplts[0]

all_filters(tmplt, world, verbose=True)

import IPython
IPython.embed()
