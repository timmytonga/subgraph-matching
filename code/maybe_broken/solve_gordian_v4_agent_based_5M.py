from utils import data
import uclasm
from filters.counting import count_isomorphisms

tmplts, world = data.gordian_v4_agent_based(5)
tmplt = tmplts[0]

uclasm.run_filters(tmplt, world, uclasm.all_filters, verbose=True)

tmplt.summarize_candidate_sets()
