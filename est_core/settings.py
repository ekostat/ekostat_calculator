# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 14:13:31 2017

@author: a001985
"""

###############################################################################
class FilterSettings(object):
    """
    Class to hold filter settings.  
    Typically this information is read from a file. 
    """
    def __init__(self): 
        pass
        
        self.load_dummy_settings()
        
    #==========================================================================
    def load_settings_from_file(self, file_path):
        self.file_path = file_path 
        
    #==========================================================================
    def write_settings_to_file(self, file_path):
        self.file_path = file_path
        
    #==========================================================================
    def load_dummy_settings(self): 
        """
        Temporary method to have attributes to play with during development. 
        """
        self.depth_interval = [0, 10]
        self.min_nr_values = 3