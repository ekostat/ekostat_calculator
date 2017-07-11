# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 09:50:06 2017

@author: a001985
"""

###############################################################################
class Information(object):
    """
    Holds various information and status of a process. 
    Information can be different for different sources. 
    Permanent information is:
        information_source
        status = None
    """
    def __init__(self, information_source): 
        self.information_source = information_source
        self.status = None