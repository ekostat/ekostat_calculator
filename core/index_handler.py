# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 14:02:13 2017

@author: a002028
"""

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
sys.path.append(current_path)

import pandas as pd
import numpy as np
import time

import utils
import core

"""
#TODO Levels ska heta step.. step 1 är första under subset
"""

"""
#==============================================================================
#==============================================================================
"""
class BooleanFilter(object):
    """
    Kan detta vara en idee....
    """
    def __init__(self):
        self.current_level = 0
        self.current_subset = 0
        
    def add_filter(self): 
        pass

"""
#==============================================================================
#==============================================================================
"""
class IndexHandler(object):
    """
    - Ska kunna ta emot filterobject
    - Summera index arrayer
    - Utgår från föregående index.array för det specifika subsetet.. Indicator.index 
    - Pratar med DataHandler och dess DataFrame för att plocka fram index 
    - select by columns
    """
    def __init__(self, workspace_object=None, data_handler_object=None):
        self.workspace_object = workspace_object
        self.data_handler_object = data_handler_object 
        
    #==========================================================================
    def _initiate_attributes(self):
        self.filter = {}
        self.first_filter = None 
        
        self.subset_filter = None # This is just for testing to combine first filter and the first subset filter. 
        
    #==========================================================================
    def add_filter(self, filter_object=None, filter_level=None, subset=None, indicator=None, water_body=None): 
        """
        For now only first filter applied
        """
        df = self.data_handler_object.get_all_column_data_df()
        # TODO: handle levels, subsets and indicator input  
        if filter_level == 0:
            self.first_filter = filter_object.get_filter_boolean_for_df(df)
            # TODO: reset later filters
            return True
        elif filter_level == 1 and subset == 'A': # Temporary!! Structure is not ready! 
            self.subset_filter = filter_object.get_filter_boolean_for_df(df)
            return True
        
        elif indicator and water_body: # Or something...
            pass
        
        
        return False
        
    #==========================================================================
    def get_filtered_data(self, level=None, subset=None): 
        """
        Returns filtered data for the given level...
        """
        # TODO: this leads to empty first filter returning False! Empty filters should return all data?
        if type(self.first_filter) != pd.Series:
            print('index_handler.get_filtered_data: this is where it goes wrong')
            return False
        
        # Temp! Structure is not ready!!!
        if level == 1 and subset == 'A': 
            boolean_filter = self.first_filter & self.subset_filter
            return self.data_handler_object.get_all_column_data_df(boolean_filter)
        else:
            boolean_filter = self.first_filter
            return self.data_handler_object.get_all_column_data_df(boolean_filter)

        return False


