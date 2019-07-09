from utils import data
import uclasm
from filters.counting import count_isomorphisms
import time

#TODO: why is counting so slow?

tmplts, world = data.pnnl_v2(7)
tmplt = tmplts[0]

uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)

print("Starting isomorphism count")
start_time = time.time()

count = count_isomorphisms(tmplt, world)
print("There are {} isomorphisms.".format(count))
print("Counting took {} seconds".format(time.time()-start_time))

assert count == 358396779779461184918283580992568541483963096116212081273419851911351003606905773945604439642143727072860747057532499340304654990572306459465368474756684228241379980512925070440395477096466399959875082594689560523291065571375447130773887619338693750293185248854394107219122894343702598123520000000000000000000000000000000000000000000000
