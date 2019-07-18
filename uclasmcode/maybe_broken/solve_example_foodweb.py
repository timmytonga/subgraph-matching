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
tmplts, world = data.foodweb(0)
tmplt = tmplts[0]
print("Loading took {} seconds".format(time.time()-start_time))

print (len(tmplt.nodes))
print (len(world.nodes))
print (sum([adj.sum() for adj in tmplt.adjs]))
print (sum([adj.sum() for adj in world.adjs]))

print("Starting filters")
start_time = time.time()
uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)
print("Filtering took {} seconds".format(time.time()-start_time))

print("Starting isomorphism count")
start_time = time.time()

count = count_isomorphisms(tmplt, world)
print("There are {} isomorphisms.".format(count))
print("Counting took {} seconds".format(time.time()-start_time))

tmplt.plot()
plt.savefig("foodweb.png")