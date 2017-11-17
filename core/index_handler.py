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
    """
    def __init__(self, workspace_object=None, data_handler_object=None):
        self.workspace_object = workspace_object
        self.data_handler_object = data_handler_object 
        
    #==========================================================================
    def _initiate_attributes(self):
        self.filter = {}
        
    #==========================================================================
    def add_filter(self, filter_object=None, filter_level=None, indicator=None, subset=None): 
        """
        For now only first filter applied
        """
        # TODO: handle levels and subsets 
        if filter_level == 0:
            df = self.data_handler_object.get_all_column_data_df()
            self.first_filter = filter_object.get_filter_boolean_for_df(df) 
            # TODO: reset later filters
        
    #==========================================================================
    def get_filtered_data(self, level=None): 
        """
        mw
        Returns filtered data for the given level...
        """
        if type(self.first_filter) != pd.Series:
            return False
        
        boolean_filter = self.first_filter
        return self.data_handler_object.get_all_column_data_df(boolean_filter) 
