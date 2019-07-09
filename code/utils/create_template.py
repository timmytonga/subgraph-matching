import random as rdm
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

import pandas as pd

world=pd.read_csv('foodweb_world.csv')
bg_graph=np.array(world.values)

source=np.array(bg_graph[:,0]).astype(int)
dest=np.array(bg_graph[:,1]).astype(int)
# here is a choice for simplicity to reduce complexity
# since not all source and destination appear on every channel
# however there exist inter layer edges
# so we do this to reduce complexity by assuming everything is on every layer aka channel
channel=np.array(bg_graph[:,2]).astype(int)

D = nx.DiGraph()

for i in range(len(source)):
    D.add_edge(source[i],dest[i],layer=channel[i])

#Choose a random node to start

vertexid=rdm.choice(source)
idlist=np.zeros(50)
edgetype=np.zeros(50)

for i in range(50):
    idlist[i]=vertexid
    #Visualize the vertex neighborhood
    dests= [n for n in D.neighbors(vertexid)]
    predecessors=[m for m in D.predecessors(vertexid)]
    #Choose a vertex from the vertex neighborhood to start the next random walk
    neighbors=dests+predecessors
    vertexid = rdm.choice(neighbors)

transport_Template=np.zeros((49,3))

for i in range(49):
    try:
        transport_Template[i][0]=idlist[i]
        transport_Template[i][1]=idlist[i+1]
        transport_Template[i][2]= D[idlist[i]][idlist[i+1]]['layer']
    except:
        transport_Template[i][0]=idlist[i+1]
        transport_Template[i][1]=idlist[i]
        transport_Template[i][2]= D[idlist[i+1]][idlist[i]]['layer']

output=np.zeros((49,3))   
j=0


for i in range(49):
    if transport_Template[i][0]!=transport_Template[i][1]:
            output[j,:]=transport_Template[i,:]
            j+=1

seen = set()
unique = []
for x in output:
    srtd = tuple(sorted(x))
    if srtd not in seen:
        unique.append(x)
        seen.add(srtd)

unique=np.array(unique)
pd.DataFrame(unique).to_csv("template.csv")
##Draw graph to a window
#nx.draw_circular(G)
#
#plt.savefig('myfig')
#plt.show()
