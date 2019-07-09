from utils import data
import uclasm
from filters.counting import count_isomorphisms

# load the data
tmplts, world = data.gordian_v5(5)
tmplt = tmplts[0]

# the cheap filters are sufficient in this case
uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)

# # counting isomorphisms is cheap since there should be only 1

from matplotlib import pyplot as plt
tmplt.plot()
plt.savefig("gordian_v5_5k.png")
# count = count_isomorphisms(tmplt, world)
# print("There are {} isomorphisms".format(count))
# assert count == 1
