# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 12:43:26 2017

@author: a001985
"""

import est_utils 



###############################################################################
@est_utils.singleton
class StationList(object): 
    """
    Singleton to hold station information. 
    """
    def __init__(self):
        pass
    
    

###############################################################################
@est_utils.singleton
class ParameterList(object): 
    """
    Singleton to hold parameter information. 
    """
    def __init__(self):
        pass
    
    
    
###############################################################################
@est_utils.singleton
class AreaList(object): 
    """
    Singleton to hold area information. 
    """
    def __init__(self):
        pass