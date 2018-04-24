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
        self.water_body_mapping = self.workspace_object.mapping_objects['water_body']
        self._initiate_attributes()
        
        
    #==========================================================================
    def old_add_boolean_to_dict(self, *args, filter_object=None, df=None, wb=None, level=None): #  **kwargs ?
        """
        Updated     20180322    by Magnus Wenzer
        
        *args: step_0, subset, step_1, step_2, water_body, indicator
        Uses bool_dict as a dynamic reference to a specific part of self.booleans
        
        #TODO Should we be able to apply different booleas from one filter-object ? 
        """

        bool_dict = self.booleans
        
        use_keys = {'keys':[key for key in reversed(args) if key],
                    'keys_in_booleans':list(self._get_keys_from_dict(self.booleans))}
        
        for key in args:
            if not key in use_keys.get('keys_in_booleans'):
                raise UserWarning(key,'should be included in IndexHandler, perhaps we are jumping to far ahead?')
                
            if key in use_keys.get('keys')[0]:
                
                if bool_dict.get('boolean') is not None:
                    # Merge boolean from parent with new boolean from filter_object
                    bool_dict[key]['boolean'] = bool_dict.get('boolean') & filter_object.get_filter_boolean_for_df(df, water_body=wb, level=level)
                    
                else:
                    # No boolean from parent, use new boolean from filter_object
                    # This one should only be possible fro 'step_0' due to else-sats below..
                    bool_dict[key]['boolean'] = filter_object.get_filter_boolean_for_df(df, water_body=wb, level=level)
                break
            
            else:
                # If we do not have a boolean for this key we copy from key before
                if bool_dict[key].get('boolean') is None:
                    bool_dict[key]['boolean'] = bool_dict.get('boolean').copy()
                
                # "dynamic reference" to a specific part of self.booleans
                bool_dict = bool_dict[key]
    #==========================================================================
    def _add_boolean_to_dict(self, step_0 = None, subset = None, step_1 = None, step_2 = None, 
                             water_body = None, indicator = None,
                             filter_object=None, df=None): #  **kwargs ?
        """
        Updated     20180423    by Lena Viktorsson
        
        boolean_dict_keys in order: step_0, subset, step_1, step_2, type_area, indicator
        Uses bool_dict as a dynamic reference to a specific part of self.booleans
        
        #TODO Should we be able to apply different booleans from one filter-object ? 
        """
        bool_dict = self.booleans
        
        #boolean_dict_keys = [step_0, subset, step_1, step_2, type_area, indicator]
        boolean_dict_keys = [step_0, subset, step_1, step_2, water_body, indicator]
        
        use_keys = {'keys':[key for key in reversed(boolean_dict_keys) if key],
                    'keys_in_booleans':list(self._get_keys_from_dict(self.booleans))}
        
        for key in boolean_dict_keys:
            if not key in use_keys.get('keys_in_booleans'):
                raise UserWarning(key,'should be included in IndexHandler, perhaps we are jumping to far ahead?')
                
            if key in use_keys.get('keys')[0]:
                
                if bool_dict.get('boolean') is not None:
                    # Merge boolean from parent with new boolean from filter_object, filter_object is either DataFilter or SettingsDataFilter
                    bool_dict[key]['boolean'] = bool_dict.get('boolean') & filter_object.get_filter_boolean_for_df(df, water_body = water_body, indicator = indicator)
                    
                else:
                    # No boolean from parent, use new boolean from filter_object
                    # This one should only be possible from 'step_0' due to else-sats below..
                    bool_dict[key]['boolean'] = filter_object.get_filter_boolean_for_df(df, water_body = water_body, indicator = indicator)
                break
            
            else:
                # If we do not have a boolean for this key we copy from key before
                if bool_dict[key].get('boolean') is None:
                    bool_dict[key]['boolean'] = bool_dict.get('boolean').copy()
                
                # "dynamic reference" to a specific part of self.booleans
                bool_dict = bool_dict[key]
            
    #==========================================================================
    def old__add_boolean_to_dict(self, step_0 = None, subset = None, step_1 = None, step_2 = None, 
                             type_area = None, indicator = None, level=None,
                             filter_object=None, df=None): #  **kwargs ?
        """
        Updated     20180326    by Lena Viktorsson
        
        boolean_dict_keys in order: step_0, subset, step_1, step_2, type_area, indicator, level
        Uses bool_dict as a dynamic reference to a specific part of self.booleans
        
        #TODO Should we be able to apply different booleans from one filter-object ? 
        """
        bool_dict = self.booleans
        
        boolean_dict_keys = [step_0, subset, step_1, step_2, type_area, indicator]
        
        use_keys = {'keys':[key for key in reversed(boolean_dict_keys) if key],
                    'keys_in_booleans':list(self._get_keys_from_dict(self.booleans))}
        
        for key in boolean_dict_keys:
            if not key in use_keys.get('keys_in_booleans'):
                raise UserWarning(key,'should be included in IndexHandler, perhaps we are jumping to far ahead?')
                
            if key in use_keys.get('keys')[0]:
                
                if bool_dict.get('boolean') is not None:
                    # Merge boolean from parent with new boolean from filter_object, filter_object is either DataFilter or SettingsDataFilter
                    bool_dict[key]['boolean'] = bool_dict.get('boolean') & filter_object.get_filter_boolean_for_df(df, type_area = type_area, level = level)
                    
                else:
                    # No boolean from parent, use new boolean from filter_object
                    # This one should only be possible from 'step_0' due to else-sats below..
                    bool_dict[key]['boolean'] = filter_object.get_filter_boolean_for_df(df, type_area = type_area, level = level)
                break
            
            else:
                # If we do not have a boolean for this key we copy from key before
                if bool_dict[key].get('boolean') is None:
                    bool_dict[key]['boolean'] = bool_dict.get('boolean').copy()
                
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
        # MW:  Added [] as defaul so that if no filter applied lenght is 0
        return bool_dict.get('boolean', [])
        
        
    #==========================================================================
    def _get_keys_from_dict(self, dictionary):
        """
        generator, generates a list of all the keys within a dictionary,
        flat or nested.
        key_list = list(get_keys_from_nested_dictionary(h))
        """
        for key, value in dictionary.items():
            if isinstance(value, dict):
                yield key
                yield from self._get_keys_from_dict(value)
            else:
                yield key    
                
                
    #==========================================================================
    def _get_steps(self, step=''):
        if step=='step_0':
            return step, None, None
        elif step=='step_1':
            return 'step_0', step, None
        elif step=='step_2':
            return 'step_0', 'step_1', step
        else:
            raise UserWarning('Step definition is incorrect. Acceptable step is step_0, step_1 or step_2')
        
        
    #==========================================================================
    def _initiate_attributes(self):
        """ 
        - The intended structure of self.booleans is as follows:
        {'step_0':{'boolean':bool,
                   'subset_A':{'boolean':None,
                               'step_1':{'boolean':bool,
                                         'step_2':{'boolean':bool,
                                                   'type_area_X':{'boolean':bool,
                                                                   'indicator_X':{'boolean':bool}
                                                                   }
                                                   'type_area_Y':{'boolean':bool,
                                                                   'indicator_X':{'boolean':bool}
                                                                   }
                                                   }
                                         }
                               }
                   'subset_B':{'boolean':bool,
                               'step_1':{'boolean':bool,
                                         'step_2':{'boolean':bool,
                                                   'type_area_X':{'boolean':bool,
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
    def _get_default_boolean(self):
        """
        - Sets up a dictionary including key 'boolean' containing None
        """
        return {'boolean':None}
    
    
    #==========================================================================
    def _set_dict(self, *args):
        """
        *args: step_0, subset, step_1, step_2, type_area, indicator
        - Set reference of master booleans dictionary, bool_dict.  
          bool_dict will change dynamically depending on key..
        - Sets up a dictionary including key 'boolean' containing None
        """
        bool_dict = self.booleans
        for key in args:
            if key and key not in bool_dict:
                bool_dict[key] = self._get_default_boolean()
                bool_dict = bool_dict[key]
            elif key:
                bool_dict = bool_dict[key]
            else:
                break


    #==========================================================================
    def old_add_filter(self, filter_object=None, subset=None, step=None, water_body=None, indicator=None): 
        """
        - Get reference of master DataFrame, df
        - Set up step sequence: step_0, step_1, step_2
        - Set up a dictionary including key 'boolean' containing None
        - Add boolean to the given subset, step, water_body or indicator
        
        If water_body is given: subset and step must also be given
        """
        df = self.data_handler_object.get_all_column_data_df()
        print('step', step)
        step_0, step_1, step_2 = self._get_steps(step=step)
        
#        print(step_0, subset, step_1, step_2, water_body, indicator)
        
        self._set_dict(step_0, subset, step_1, step_2, water_body, indicator)
        
#        print(self.booleans)
        
        self._add_boolean_to_dict(step_0, subset, step_1, step_2, water_body, indicator,
                                  filter_object=filter_object, 
                                  df=df,
                                  wb=water_body)
        
    #==========================================================================
    def add_filter(self, filter_object=None, subset=None, step=None, water_body = None, indicator=None, **kwargs): 
        """
        Updated     20180423    by Magnus Wenzer
        
        - Get reference of master DataFrame, df
        - Set up step sequence: step_0, step_1, step_2
        - Set up a dictionary including key 'boolean' containing None
        - Add boolean to the given subset, step, type_area (given as input), indicator and level
        
        If type_area is given: subset and step must also be given
        If indicator is given: water_body must also be given
        """
        print('add filter for step: {}, type area: {}, indicator: {}'.format(step, water_body, indicator))
        df = self.data_handler_object.get_all_column_data_df()

        step_0, step_1, step_2 = self._get_steps(step=step)
        
#        print(step_0, subset, step_1, step_2, type_area, indicator)

        self._set_dict(step_0, subset, step_1, step_2, water_body, indicator)
        
#        print(self.booleans)
        
        self._add_boolean_to_dict(step_0, subset, step_1, step_2, water_body, indicator,
                                  filter_object=filter_object, 
                                  df=df, **kwargs)
    #==========================================================================
    def old_add_filter(self, filter_object=None, subset=None, step=None, type_area=None, indicator=None, level=None): 
        """
        Updated     20180322    by Magnus Wenzer
        
        - Get reference of master DataFrame, df
        - Set up step sequence: step_0, step_1, step_2
        - Set up a dictionary including key 'boolean' containing None
        - Add boolean to the given subset, step, type_area (given as input), indicator and level
        
        If type_area is given: subset and step must also be given
        If indicator is given: type_area must also be given
        """
        print('add filter for step: {}, type area: {}, indicator: {}, level: {}'.format(step, type_area, indicator, level))
        df = self.data_handler_object.get_all_column_data_df()

        step_0, step_1, step_2 = self._get_steps(step=step)
        
#        print(step_0, subset, step_1, step_2, type_area, indicator)

        self._set_dict(step_0, subset, step_1, step_2, type_area, indicator)
        
#        print(self.booleans)
        
        self._add_boolean_to_dict(step_0, subset, step_1, step_2, type_area, indicator, level,
                                  filter_object=filter_object, 
                                  df=df)

        
    #==========================================================================
    def old_get_filtered_data(self, subset=None, step=None, water_body=None, indicator=None): 
        """
        Returns filtered data for the given boolean specification
        """
        step_0, step_1, step_2 = self._get_steps(step=step)
        
        boolean = self._get_boolean(step_0, subset, step_1, step_2, water_body, indicator)
        
        return self.data_handler_object.get_all_column_data_df(boolean_filter=boolean)


    #==========================================================================
    def get_filtered_data(self, subset=None, step=None, water_body=None, indicator=None): 
        """
        Updated     20180326    by Magnus Wenzer
        Returns filtered data for the given boolean specification
        Takes input arguments: subset, step, water_body and indicator
        """
        
        step_0, step_1, step_2 = self._get_steps(step=step)
        
        boolean = self._get_boolean(step_0, subset, step_1, step_2, water_body, indicator)
        
        return self.data_handler_object.get_all_column_data_df(boolean_filter=boolean)
    
    
    #==========================================================================
    def reset_booleans(self, subset=None, step=None):
        """
        All keys that shall be kept should be specified in *args. 
        When a key doesnt exists we reset the dict for the key before and break
        Example: args = ['step_0', 'default_subset', 'step_1', None] (we want 
        to reset 'step_1')
                Save a temporary reference part of self.booleans to bool_dict 
                for each loop iteration. If key==None we assume the boolean 
                from the key before should be reset and will hence do so, break..
                
        """ 
        step_0, step_1, step_2 = self._get_steps(step=step)
        args = [step_0, subset, step_1, step_2]
        
        bool_dict = self.booleans
        for key in args:
            if key:
                bool_dict = bool_dict[key]
            else:
                bool_dict = self._get_default_boolean()
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