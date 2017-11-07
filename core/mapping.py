# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 14:57:56 2017

@author: a002028
"""
import pandas as pd
import numpy as np

"""#========================================================================"""
class AttributeDict(dict):
    """    
    Base class for attribute dictionary. 
    """
    def __init__(self): 
        super().__init__() 
        
    #==========================================================================
    def _add_entries(self, **entries):
        """
        Turns elements in arrays into attributes with a corresponding official 
        field name 
        """
        for key, array in entries.items():
            setattr(self, key, key)
            setattr(self, key.lower(), key)
            for value in array.values:
                if not pd.isnull(value):
                    setattr(self, value.lower(), key)
                    
    #==========================================================================
    def _add_arrays_to_entries(self, **entries): 
        for key, array in entries.items():
            if len(array)==1:
                array = array[0]
            setattr(self, key, array)
                    
    #==========================================================================
    def keys(self):
        return list(self.__dict__.keys())
        
    #==========================================================================
    def get(self, key):
        return getattr(self, key.lower())
        
    #==========================================================================
    def get_list(self, key_list):
        return list(self.get(key) for key in key_list)
        
    #==========================================================================
    def get_mapping_dict(self, key_list):
        return dict(list((key, self.get(key)) for key in key_list))
        
    #==========================================================================
    def __getitem__(self, key):
        return getattr(self, key)
        
    #==========================================================================
    

"""#========================================================================"""
class ParameterMapping(AttributeDict):
    """
    Load file to map data fields and parameters to a standard setting format
    """
    def __init__(self):
        super().__init__()
        
    #==========================================================================
    def load_mapping_settings(self, file_path=u'',sep='\t',encoding='cp1252'):
        """ Reading csv/txt files """
        self.mapping_file = pd.read_csv(file_path, sep=sep, encoding=encoding)
        self._add_entries(**self.mapping_file)
        
    #==========================================================================
    def map_parameter_list(self, para_list, ext_list=False):
        return self.get_list(para_list)
        
    #==========================================================================
    def get_parameter_mapping(self, para_list, ext_list=False):
        return self.get_mapping_dict(para_list)
        
    #==========================================================================
    

"""#========================================================================"""
if __name__ == '__main__':
    print('='*50)
    print('Running module "mapping.py"')
    print('-'*50)
    print('')
    
    first_filter_directory = 'D:/Utveckling/GitHub/ekostat_calculator/test_data/mappings/mapping_parameter_dynamic_extended.txt' 
    
    # Mapping
    p_map = ParameterMapping()
    p_map.load_mapping_settings(file_path=first_filter_directory)
    print(p_map.map_parameter_list(['myear', u'ammonium nh4-n']))
    print(p_map.get_parameter_mapping(['myear', u'ammonium nh4-n']))
    
    print('-'*50)
    print('done')
    print('-'*50)
    
#    for k in p_map.keys():
#        if k.startswith('sili'):
#            print(k, len(k), p_map.get(k))
    
