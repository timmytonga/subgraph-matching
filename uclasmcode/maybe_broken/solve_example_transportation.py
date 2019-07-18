# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 22:11:10 2019

@author: hexie
"""

from utils import data
import uclasm
from filters.counting import count_isomorphisms
import time

import matplotlib.pyplot as plt
plt.switch_backend('agg')

print("Starting data loading")
start_time = time.time()
tmplts, world = data.transportation(0)
tmplt = tmplts[0]
print("Loading took {} seconds".format(time.time()-start_time))


print("Starting filters")
start_time = time.time()
uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)
print("Filtering took {} seconds".format(time.time()-start_time))

# print("Starting isomorphism count")
# start_time = time.time()
# 
# count = count_isomorphisms(tmplt, world)
# print("There are {} isomorphisms.".format(count))
# print("Counting took {} seconds".format(time.time()-start_time))
#
#assert count == 57139200

