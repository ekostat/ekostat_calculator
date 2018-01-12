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
    
    Dictionary structure
    - Step 0 
    - Subset x
    - Step x
    - Water Body x
    - Indicator x
    
    """
    def __init__(self, workspace_object=None, data_handler_object=None):
        self.workspace_object = workspace_object
        self.data_handler_object = data_handler_object
        
    #==========================================================================
    def _initiate_attributes(self):
        """ self.booleans = {} """
        self.booleans = {}
#        self.first_filter = None
#        self.subset_filter = None # This is just for testing to combine first filter and the first subset filter. 

    #==========================================================================
#    def add_filter(self, filter_object=None, step_0=None, subset=None, step=None, water_body=None, indicator=None): 
#        """
#        For now only first filter applied
#        """
#        
#        df = self.data_handler_object.get_all_column_data_df()
#        # TODO: handle steps, subsets and indicator input
#        
##        self.set_dict([step_0, subset, step, water_body, indicator])
#        
#        self.set_step_0(step_0=step_0)
#        self.set_subset(step_0=step_0, subset=subset)
#        self.set_step(step_0=step_0, subset=subset, step=step)
#        self.set_water_body(step_0=step_0, subset=subset, step=step, water_body=water_body)
#        self.set_indicator(step_0=step_0, subset=subset, step=step, water_body=water_body, indicator=indicator)
#
#
#        if indicator:
#            self.add_filter(bool_dict=self.booleans[step_0][subset][step][water_body][indicator], 
#                            filter_object=filter_object, 
#                            df=df)
#        elif water_body:
#            self.add_filter(bool_dict=self.booleans[step_0][subset][step][water_body], 
#                            filter_object=filter_object, 
#                            df=df)
#        elif step:
#            self.add_filter(bool_dict=self.booleans[step_0][subset][step], 
#                            filter_object=filter_object, 
#                            df=df)
#        elif subset:
#            self.add_filter(bool_dict=self.booleans[step_0][subset], 
#                            filter_object=filter_object, 
#                            df=df)
#        elif step_0:
#            self.add_filter(bool_dict=self.booleans[step_0], 
#                            filter_object=filter_object, 
#                            df=df)
#        else:
#            pass
#        
##        if indicator:
##            self.add_indicator(step_0=step_0, subset=subset, step=step, water_body=water_body, indicator=indicator)
##        elif water_body:
##            self.add_water_body(step_0=step_0, subset=subset, step=step, water_body=water_body)
##        elif step:
##            self.set_step(step_0=step_0, subset=subset, step=step)
##        elif subset:
##            self.set_step(step_0=step_0, subset=subset)
##        elif step_0:
##            self.set_step(step_0=step_0)
##        else:
##            pass
#            
#        if filter_step == 0:
#            self.first_filter = filter_object.get_filter_boolean_for_df(df)
#            # TODO: reset later filters
#            return True
#        elif filter_step == 1 and subset == 'A': # Temporary!! Structure is not ready! 
#            self.subset_filter = filter_object.get_filter_boolean_for_df(df)
#            return True
#        
#        elif indicator and water_body: # Or something...
#            pass
#        
##        return False
#
#    #==========================================================================
#    def add_filter(self, bool_dict=None, filter_object=filter_object, df=df):
#        bool_dict = filter_object.get_filter_boolean_for_df(df)
        
        
#    #==========================================================================
#    def add_indicator(self, step_0=None, subset=None, step=None, water_body=None, indicator=None):
#        self.booleans[step_0][subset][step][water_body][indicator] 
#
#    #==========================================================================
#    def add_water_body(self, step_0=None, subset=None, step=None, water_body=None):
#        self.booleans[step_0][subset][step][water_body]
#        
#    #==========================================================================
#    def add_subset(self, step_0=None, subset=None):
#        self.booleans[step_0][subset] 
#        
#    #==========================================================================
#    def add_step(self, step_0=None, subset=None, step=None):
#        self.booleans[step_0][subset][step]  
#            
#    #==========================================================================
#    def add_step_0(self, step_0=None):
#        self.booleans[step_0]
            
            
            
            
    #==========================================================================
    # possibly a nicer way of setting all dicts... ?
#    def set_dict(key_list=[]):
#        for key in key_list:
#            if not key in origin_dict:
#                origin_dict[key] = {}
            
    #==========================================================================
    def set_indicator(self, step_0=None, subset=None, step=None, water_body=None, indicator=None):
        if not indicator in self.booleans[step_0][subset][step][water_body]:
            self.booleans[step_0][subset][step][water_body][indicator] = None  
                         
    #==========================================================================
    def set_water_body(self, step_0=None, subset=None, step=None, water_body=None):
        if not water_body in self.booleans[step_0][subset][step]:
            self.booleans[step_0][subset][step][water_body] = None
                         
    #==========================================================================
    def set_subset(self, step_0=None, subset=None):
        if not subset in self.booleans[step_0]:
            self.booleans[step_0][subset] = {}
        
    #==========================================================================
    def set_step(self, step_0=None, subset=None, step=None):
        if not step in self.booleans[step_0][subset]:
            self.booleans[step_0][subset][step] = {}        

    #==========================================================================
    def set_step_0(self, step_0=None):
        if not step_0 in self.booleans:
            self.booleans[step_0] = {}
            
            
            
    #==========================================================================
    def get_filtered_data(self, step=None, subset=None): 
        """
        Returns filtered data for the given step...
        """
        # TODO: this leads to empty first filter returning False! Empty filters should return all data?
        if type(self.first_filter) != pd.Series:
            print('index_handler.get_filtered_data: this is where it goes wrong')
            return False
        
        if step == 1 and subset == 'A':
            boolean_filter = self.first_filter & self.subset_filter
            return self.data_handler_object.get_all_column_data_df(boolean_filter=boolean_filter)
        else:
            boolean_filter = self.first_filter
            return self.data_handler_object.get_all_column_data_df(boolean_filter=boolean_filter)

        return False

    #==========================================================================
       
#    #==========================================================================
#    def add_filter(self, filter_object=None, filter_step=None, subset=None, indicator=None, water_body=None): 
#        """
#        For now only first filter applied
#        """
#        df = self.data_handler_object.get_all_column_data_df()
#        # TODO: handle levels, subsets and indicator input  
#        if filter_step == 0:
#            self.first_filter = filter_object.get_filter_boolean_for_df(df)
#            # TODO: reset later filters
#            return True
#        elif filter_step == 1 and subset == 'A': # Temporary!! Structure is not ready! 
#            self.subset_filter = filter_object.get_filter_boolean_for_df(df)
#            return True
#        
#        elif indicator and water_body: # Or something...
#            pass
#        
#        return False
#        
#    #==========================================================================
#    def get_filtered_data(self, step=None, subset=None): 
#        """
#        Returns filtered data for the given step...
#        """
#        # TODO: this leads to empty first filter returning False! Empty filters should return all data?
#        if type(self.first_filter) != pd.Series:
#            print('index_handler.get_filtered_data: this is where it goes wrong')
#            return False
#        
#        # Temp! Structure is not ready!!!
#        if step == 1 and subset == 'A':
#            boolean_filter = self.first_filter & self.subset_filter
#            return self.data_handler_object.get_all_column_data_df(boolean_filter)
#        else:
#            boolean_filter = self.first_filter
#            return self.data_handler_object.get_all_column_data_df(boolean_filter)
#
#        return False
#
#    #==========================================================================

