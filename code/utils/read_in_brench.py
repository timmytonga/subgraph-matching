# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 21:23:58 2019

@author: hexie
"""
import numpy as np
import pandas as pd

newDict = {}
with open('pattern', 'r') as f:
    lines= f.readlines()

source=[]
dest=[]
count=1

myrange= int(float(lines[0]))

for i in range(myrange):
    for item in lines[count].split()[1:]:
        source.append(count-1)
        dest.append(int(float(item)))
    count=count+1

layer=[0]*len(source)
source=np.array(source)
dest=np.array(dest)
output=np.vstack((source,dest,layer))
output=np.transpose(output)

pd.DataFrame(output).to_csv("bench_mark.csv")
