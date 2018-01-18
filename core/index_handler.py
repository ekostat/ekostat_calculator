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
    - step_0 
    - Subset (optional name)
    - step_1
    - step_2
    - Water Body (optional name)
    - Indicator (optional name)
    """
    def __init__(self, workspace_object=None, data_handler_object=None):
        self.workspace_object = workspace_object
        self.data_handler_object = data_handler_object
        self._initiate_attributes()
        
        
    #==========================================================================
    def _add_boolean_to_dict(self, *args, filter_object=None, df=None): #  **kwargs ?
        """
        *args: step_0, subset, step_1, step_2, water_body, indicator
        Uses bool_dict as a dynamic reference to a specific part of self.booleans
        """
        bool_dict = self.booleans
        for key in reversed(args):
            if key:
                use_key=key
                break
                
        for key in args:
            if key == use_key:
                if bool_dict.get('boolean') != None:
                    # Merge boolean from parent with new boolean from filter_object
                    bool_dict[key]['boolean'] = bool_dict.get('boolean') & filter_object.get_filter_boolean_for_df(df)
                else:
                    # No boolean from parent, use new boolean from filter_object
                    bool_dict[key]['boolean'] = filter_object.get_filter_boolean_for_df(df)

                break
            else:
                # "dynamic reference" to a specific part of self.booleans
                bool_dict = bool_dict[key]

                
    #==========================================================================
    def _get_boolean(self, *args):
        """
        *args: step_0, subset, step_1, step_2, water_body, indicator
        - Loop through *args, save a reference for the specific dictionary 
          within self.booleans
        - Return boolean for the specific argument input
        """
        bool_dict = self.booleans.copy()
        for key in args:
            if key and key in bool_dict:
                bool_dict = bool_dict[key]
            else:
                break
            
        return bool_dict.get('boolean')
        
    
    #==========================================================================
    def _get_steps(self, step=''):
        if step=='step_0':
            return step, None, None
        elif step=='step_1':
            return 'step_0', step, None
        elif step=='step_2':
            return 'step_0', 'step_1', step
        else:
            raise UserWarning('Step definition is incorrect. Acceptable step is step_x, where x equals 0-2')
        
        
    #==========================================================================
    def _initiate_attributes(self):
        """ 
        - The intended structure of self.booleans is as follows:
        {'step_0':{'boolean':bool,
                   'subset_A':{'boolean':bool,
                               'step_1':{'boolean':bool,
                                         'step_2':{'boolean':bool,
                                                   'water_body_X':{'boolean':bool,
                                                                   'indicator_X':{'boolean':bool}
                                                                   }
                                                   'water_body_Y':{'boolean':bool,
                                                                   'indicator_X':{'boolean':bool}
                                                                   }
                                                   }
                                         }
                               }
                   'subset_B':{'boolean':bool,
                               'step_1':{'boolean':bool,
                                         'step_2':{'boolean':bool,
                                                   'water_body_X':{'boolean':bool,
                                                                   'indicator_X':{'boolean':bool}
                                                                   }
                                                   }
                                         }
                               }
                   }
        }
        """
        self.booleans = {}


    #==========================================================================
    def _reset_boolean(self):
        """
        - Sets up a dictionary including key 'boolean' containing None
        """
        return {'boolean':None}
    
    
    #==========================================================================
    def _set_dict(self, *args):
        """
        *args: step_0, subset, step_1, step_2, water_body, indicator
        - Set reference of master booleans dictionary, bool_dict.  
          bool_dict will change dynamically depending on key..
        - Sets up a dictionary including key 'boolean' containing None
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
    def add_filter(self, filter_object=None, subset=None, step=None, water_body=None, indicator=None): 
        """
        - Get reference of master DataFrame, df
        - Set up step sequence: step_0, step_1, step_2
        - Set up a dictionary including key 'boolean' containing None
        - Add boolean to the given subset, step, water_body or indicator
        
        If water_body is given: subset and step must also be given
        """
        df = self.data_handler_object.get_all_column_data_df()
        
        step_0, step_1, step_2 = self._get_steps(step=step)
        
        self._set_dict(step_0, subset, step_1, step_2, water_body, indicator)
        
        self._add_boolean_to_dict(step_0, subset, step_1, step_2, water_body, indicator,
                                  filter_object=filter_object, 
                                  df=df)

        
    #==========================================================================
    def get_filtered_data(self, subset=None, step=None, water_body=None, indicator=None): 
        """
        Returns filtered data for the given boolean specification
        """
        step_0, step_1, step_2 = self._get_steps(step=step)
        
        boolean = self._get_boolean(step_0, subset, step_1, step_2, water_body, indicator)
        
        return self.data_handler_object.get_all_column_data_df(boolean_filter=boolean)        


    #==========================================================================
    def reset_booleans(self, subset=None, step=None, water_body=None, indicator=None):
        """
        All keys that shall be kept should be specified in *args. 
        When a key doesnt exists we reset the dict for the key before and break
        """ 
        step_0, step_1, step_2 = self._get_steps(step=step)
        args = [step_0, subset, step_1, step_2, water_body, indicator]
        
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