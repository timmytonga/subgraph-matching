from utils import data
import uclasm
from filters.counting import count_isomorphisms

# load the data
tmplts, world = data.gordian_v4_probabilistic(5000)
tmplt = tmplts[0]

# the cheap filters are sufficient in this case
uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)

# counting isomorphisms is cheap since there should be only 1

count = count_isomorphisms(tmplt, world)
print("There are {} isomorphisms".format(count))
assert count == 1
