import random as rdm
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


def generate_template(root_id,size,graph):
    vertexid=root_id
    idlist=np.zeros(size)
    
    for i in range(size):
        idlist[i]=vertexid
        #Visualize the vertex neighborhood
        dests= [n for n in graph.neighbors(vertexid)]
        predecessors=[m for m in graph.predecessors(vertexid)]
        #Choose a vertex from the vertex neighborhood to start the next random walk
        neighbors=dests+predecessors
        vertexid = rdm.choice(neighbors)
    
    transport_Template=np.zeros((size-1,3))
    
    for i in range(size-1):
        try:
            transport_Template[i][0]=idlist[i]
            transport_Template[i][1]=idlist[i+1]
            transport_Template[i][2]= graph[idlist[i]][idlist[i+1]]['layer']
    
        except:
            transport_Template[i][0]=idlist[i+1]
            transport_Template[i][1]=idlist[i]
            transport_Template[i][2]= graph[idlist[i+1]][idlist[i]]['layer']
           
        
    output=np.zeros((size-1,3))   
    j=0
    
    
    for i in range(size-1):
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
    return unique


# also it makes no sense for nodes to transport to itself it is on the same layer
# we take every self edge exisitence to be in channel 6
# there are no different inter layer edges other than these self edges
# thus these self edges are mapped into channel 6
# we choose the first nodes randomly from channel 6 node
# because there is a larger chance that these nodes are going to exist in different layer
# we notice also there is no 


# TODO: this ugly uclasmcode need revision, but I am too late to revise it now 
# ( it needs to be more generic according to its layer, but since we only need 3 example, whatever QWQ)

world=pd.read_csv('transportation_world.csv')
bg_graph=np.array(world.values)
source=np.array(bg_graph[:,0]).astype(int)
dest=np.array(bg_graph[:,1]).astype(int)
channel=np.array(bg_graph[:,2]).astype(int)
channel[source==dest]=6

Whole = nx.MultiGraph()

for i in range(len(source)):
    Whole.add_edge(source[i],dest[i],layer=channel[i])

sourceA=source[channel==0]
destA=dest[channel==0]
channelA=channel[channel==0]

sourceB=source[channel==1]
destB=dest[channel==1]
channelB=channel[channel==1]

sourceC=source[channel==2]
destC=dest[channel==2]
channelC=channel[channel==2]

sourceD=source[channel==3]
destD=dest[channel==3]
channelD=channel[channel==3]

sourceE=source[channel==4]
destE=dest[channel==4]
channelE=channel[channel==4]

sourceF=source[channel==5]
destF=dest[channel==5]
channelF=channel[channel==5]

sourceG=source[channel==6]
destG=dest[channel==6]
channelG=channel[channel==6]

A=nx.DiGraph()
B=nx.DiGraph()
C=nx.DiGraph()
D=nx.DiGraph()
E=nx.DiGraph()
F=nx.DiGraph()
G=nx.DiGraph()

for i in range(len(sourceA)):
    A.add_edge(sourceA[i],destA[i],layer=channelA[i])

for i in range(len(sourceB)):
    B.add_edge(sourceB[i],destB[i],layer=channelB[i])
    
for i in range(len(sourceC)):
    C.add_edge(sourceC[i],destC[i],layer=channelC[i])
    
for i in range(len(sourceD)):
    D.add_edge(sourceD[i],destD[i],layer=channelD[i])

for i in range(len(sourceE)):
    E.add_edge(sourceE[i],destE[i],layer=channelE[i])
    
for i in range(len(sourceF)):
    F.add_edge(sourceF[i],destF[i],layer=channelF[i])
    
for i in range(len(sourceG)):
    G.add_edge(sourceG[i],destG[i],layer=channelG[i])


# There are no nodes that appear in all layer
# So we try to choose the more the better, for example, 28163 and 42649 appear in all of the other layer other than 1
# and {13745, 35743, 42918}, apear in all layer other than layer 0
# For example, we can seek node that are important, and it is free to say that these nodes are important
a=set(A.nodes())
b=set(B.nodes())
c=set(C.nodes())
d=set(D.nodes())
e=set(E.nodes())
f=set(F.nodes())
g=set(G.nodes())

zero_five=list(f.intersection(a))
one_five=list(f.intersection(b))
two_five=list(f.intersection(c))
three_five=list(f.intersection(d))
four_five=list(f.intersection(e))
six_five=list(f.intersection(g))

zero=f.intersection(a)
one=f.intersection(b)
two=f.intersection(c)
three=f.intersection(d)
four=f.intersection(e)
six=f.intersection(g)

other_than_one=list(zero.intersection( two, three, four,six))
other_than_zero=list(one.intersection( two, three, four,six))
city_one=28163
city_two=13745
paths=nx.all_simple_paths(Whole,28163,13745,cutoff=3)
# i.e. we take these nodes: 13745, 25380, 41487, 28163 as our template root nodes and random walk based on these nodes
# especially based on 28163 in 0, 2,3,4,5,6
# based on 13745 in 1,2,3,4,5,6
# based on 25380 in layer 5
# based on 41487 in layer 5
# then we take this template as our template and assume that this template as a template that shows how to travel to location 1
# and location 2 and also how to travel from other part of the country to this two region

SIZE=20

template_1=generate_template(city_two,SIZE,B)
template_2=generate_template(city_two,SIZE,C)
template_3=generate_template(city_two,SIZE,D)
template_4=generate_template(city_two,SIZE,E)
template_5=generate_template(city_two,SIZE,F)


output=np.concatenate((template_1,template_2,template_3,template_4,template_5),axis=0)
pd.DataFrame(output).to_csv("new_transportation_template.csv")
