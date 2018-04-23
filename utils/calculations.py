# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 09:43:01 2018

@author: a001985
"""
import numpy as np 

#==============================================================================
def get_integrated_mean(depth_list, 
                        value_list, 
                        depth_interval):
    """ 
    Created:                    by Magnus Wenzer
    Last modified:  20180423    by Magnus Wenzer 
    
    This seem slower than "get_integrated_mean"
    """
#    depth_list = list(depth_list)
#    value_list = list(value_list)
    sum_list = []
    # Make sure to integrate the whole surface layer if selected
    if depth_list[0] != depth_interval[0]:
        depth_list.insert(0, depth_interval[0])
        value_list.insert(0, value_list[0])
    if depth_list[-1] != depth_interval[-1]:
        depth_list.append(depth_interval[-1])
        value_list.append(value_list[-1])

    for z0, z1, v0, v1 in zip(depth_list[:-1], depth_list[1:], 
                              value_list[:-1], value_list[1:]):
        
#        print(v0, v1, z0, z1)
#        print(type(v0), type(v1), type(z0), type(z1))
        part_sum = 0.5*(v1+v0)*(z1-z0)

        sum_list.append(part_sum)

    return sum(sum_list)/(depth_list[-1]-depth_list[0]) 


#==============================================================================
def get_integrated_mean_using_arrays(depth_list, 
                                     value_list, 
                                     depth_interval):
    """ 
    Created:        20180423    by Magnus Wenzer
    Last modified:  20180423    by Magnus Wenzer 
    
    This seem slower than "get_integrated_mean"
    """
    
    sum_list = []
    # Make sure to integrate the whole surface layer if selected
    if depth_list[0] != depth_interval[0]:
        depth_list = np.insert(depth_list, depth_interval[0])
        value_list = np.insert(value_list, value_list[0])
    if depth_list[-1] != depth_interval[-1]:
        depth_list = np.append(depth_list, depth_interval[-1])
        value_list = np.append(value_list, value_list[-1])
    
    sum_list = np.sum(0.5*(value_list[1:]+value_list[:-1])*(depth_list[1:]-depth_list[:-1]))

    return sum_list/(depth_list[-1]-depth_list[0])