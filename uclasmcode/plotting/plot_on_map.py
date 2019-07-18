# -*- coding: utf-8 -*-
"""
Created on Sun May  5 13:51:15 2019

@author: hexie
"""

import folium
import numpy as np

import pandas as pd


tmplt=pd.read_csv('transportation_template.csv')
tp_graph=np.array(tmplt.values) 
tmplt_source=np.array(tp_graph[:,0]).astype(int)
tmplt_dest=np.array(tp_graph[:,1]).astype(int)
tmplt_node=np.hstack((tmplt_source,tmplt_dest)) 
tmplt_node=np.unique(tmplt_node)


world=pd.read_csv('nodes.csv')
bg_graph=np.array(world.values)

node_id=np.array(bg_graph[:,0]).astype(int)
node_lon=np.array(bg_graph[:,3]).astype(float)
node_lat=np.array(bg_graph[:,2]).astype(float)
node_layer=np.array(bg_graph[:,1]).astype(int)


nodes=np.vstack((node_id,node_lon,node_lat))
nodes=np.transpose(nodes)


#%%

data_filter=np.array([0,0.1,0.1])

for i in tmplt_node:
    itemindex = np.where(node_id==i)[0][0]
    q=np.hstack((node_id[itemindex],node_lat[itemindex],node_lon[itemindex]))
    data_filter=np.vstack((data_filter,q))

#%%

name=data_filter[1:,0]
lat=data_filter[1:,1]
lon=data_filter[1:,2]
#%%

name=np.array(name).astype(str)

#%%


data = pd.DataFrame({
'lat':lon, 'lon':lat, 'name':name})
data
 
# Make an empty map
m = folium.Map(location=[20, 0], tiles="Mapbox Bright", zoom_start=2)
 
# I can add marker one by one on the map
for i in range(0,len(data)):
    folium.Marker([data.iloc[i]['lon'], data.iloc[i]['lat']], popup=data.iloc[i]['name']).add_to(m)
 
# Save it as html
m.save('transportation_on_map.html')
