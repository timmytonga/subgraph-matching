# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 13:43:43 2019

@author: hexie
"""
import pandas as pd
import numpy as np

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295     #Pi/180
    a = 0.5 - np.cos((lat2 - lat1) * p)/2 + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    return 12742 * np.arcsin(np.sqrt(a)) #2*R*asin...
# produce the distance from km


# radius is in km centered around each template node
def attribute_filter(tmplt, world, candidates=None, radius=5):
    if candidates is None:
        candidates = np.ones((tmplt.n_nodes, world.n_nodes), dtype=np.bool)
    
    world_coords=pd.read_csv('/s2/scr/reu_data/darpa_maa/data/EXAMPLE/V0/world_coord.csv')
    bg_graph=np.array(world_coords.values)
    world_id=np.array(bg_graph[:,2]).astype(int).astype(str)
    world_lon=np.array(bg_graph[:,1]).astype(float)
    world_lat=np.array(bg_graph[:,0]).astype(float)
    
    tmplt_coords=pd.read_csv('/s2/scr/reu_data/darpa_maa/data/EXAMPLE/V0/tmplt_coord.csv')
    tp_graph=np.array(tmplt_coords.values)
    tmplt_id=np.array(tp_graph[:,2]).astype(int).astype(str)
    tmplt_lon=np.array(tp_graph[:,1]).astype(float)
    tmplt_lat=np.array(tp_graph[:,0]).astype(float)

    for i in range(len(tmplt_id)):
        print(i, "of", tmplt.n_nodes)
        for j in range(len(world_id)):
            if distance(world_lat[j],world_lon[j],tmplt_lat[i],tmplt_lon[i]) > radius:
                if tmplt_id[i] in tmplt.node_idxs and world_id[j] in world.node_idxs:
                    candidates[tmplt.node_idxs[tmplt_id[i]], world.node_idxs[world_id[j]]] = False
    
    
    return tmplt, world, candidates


# now we know which world nodes are close enough to which template nodes.