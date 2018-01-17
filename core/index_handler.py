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
    - Utgår från föregående boolean för det specifika subsetet.. 
    - Pratar med DataHandler och dess DataFrame för att plocka fram boolean 
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
    def _add_boolean_to_dict(self, *args, filter_object=None, df=None): #  **kwargs ?
        """
        *args: step_0, subset, step, water_body, indicator
        """
        bool_dict = self.booleans
        for key in reversed(args):
            if key:
                use_key=key
                break
                
        for key in args:
            if key == use_key:
                if bool_dict[key].get('boolean') != None:
                    bool_dict[key]['boolean'] = filter_object.get_filter_boolean_for_df(df)
                else:
                    bool_dict[key]['boolean'] = bool_dict[key].get('boolean') & filter_object.get_filter_boolean_for_df(df)
                break
            else:
                bool_dict = bool_dict[key]

                
    #==========================================================================
    def _get_boolean(self, *args):
        """
        *args: step_0, subset, step, water_body, indicator
        """
        bool_dict = self.booleans.copy()
        for key in args:
            if key and key in bool_dict:
                bool_dict = bool_dict[key]
            else:
                break
            
        return bool_dict.get('boolean')
        
    
    #==========================================================================
    def _initiate_attributes(self):
        """ self.booleans = {} """
        self.booleans = {}

    #==========================================================================
    def _reset_boolean(self):
        return {'boolean':None}
    
    #==========================================================================
    def _set_dict(self, *args):
        """
        
        """
        bool_dict = self.booleans
        for key in args:
            if key and key not in bool_dict:
                bool_dict[key] = self._reset_boolean()
                break
            elif key:
                bool_dict = bool_dict[key]
            else:
                break


    #==========================================================================
    def add_filter(self, filter_object=None, step_0=None, subset=None, step=None, water_body=None, indicator=None): 
        """
        
        """
        df = self.data_handler_object.get_all_column_data_df()
        
        self._set_dict(step_0, subset, step, water_body, indicator) # TRY
        
        self._add_boolean_to_dict(step_0, subset, step, water_body, indicator,
                                  filter_object=filter_object, df=df)

        
    #==========================================================================
    def get_filtered_data(self, step_0=None, subset=None, step=None, water_body=None, indicator=None): 
        """
        Returns filtered data for the given step or...
        """
        boolean = self._get_boolean(step_0, subset, step, water_body, indicator)
        
        return self.data_handler_object.get_all_column_data_df(boolean_filter=boolean)        


    #==========================================================================
    def reset_booleans(self, *args):
        """
        *args: step_0, subset, step, water_body, indicator
        All keys that shall be kept should be specified in *args. 
        When a key doesnt exists we reset the dict for the key before and break
        """ 
        bool_dict = self.booleans
        for key in args:
            if key:
                bool_dict = bool_dict[key]
            else:
                bool_dict = self._reset_boolean()
                break
            

    #==========================================================================

if __name__ == '__main__':
    print('='*50)
    print('Running module "index_handler.py"')
    print('-'*50)
    print('')
    
    raw_data_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/raw_data/data_BAS_2000-2009.txt'
    first_filter_directory = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filtered_data' 
    
    # Handler
#    raw_data = core.DataHandler('raw')
#    raw_data.add_txt_file(raw_data_file_path, data_type='column')
    
    print('-'*50)
    print('done')
    print('-'*50)