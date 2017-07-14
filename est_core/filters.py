# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 11:04:47 2017

@author: a001985
"""

###############################################################################
class FilterBase(dict):
    """
    Base class to hold common methodes for filters. 
    """
    def __init__(self): 
        super().__init__() 
    
    #==========================================================================
    def _pop_all_self(self):
        for i in range(len(self))[::-1]:
            self.pop(i)
            

###############################################################################
class DataFilter(FilterBase):
    """
    Class to hold data filter settings.  
    Typically this information is read from a file. 
    Maybe this filter should be different for different 
    """
    def __init__(self, source): 
        super().__init__() 
        self.source = source
        self._initate_filter_items()
        self.load_dummy_settings()
        
    #==========================================================================
    def _initate_filter_items(self):
        self.filter_list = ['DEPTH_INTERVAL', 'TYPE_AREA', 'MONTH', 'MYEAR']
        
        
    #==========================================================================
    def load_data_filter_file(self, file_path):
        """
        Filter items are saved in self (dict). 
        """ 
        self._pop_all_self()
        self.filter_list = []
        self.file_path = file_path 
        # TODO: Decide structure of data filter file and load filter
        
    #==========================================================================
    def save_data_filter_file(self, file_path):
        self.file_path = file_path
        
    #==========================================================================
    def set_filter(self, filter_type, value): 
        filter_type = filter_type.upper().replace(' ', '_')
        if filter_type not in self.filter_list:
            return False
        # TODO: Make checks for different kinds of filters. 
        self[filter_type] = value
        return True
        
    #==========================================================================
    def load_dummy_settings(self): 
        """
        Temporary method to have attributes to play with during development. 
        """
        self._pop_all_self()
        for item in self.filter_list:
            self[item] = None
        self['DEPTH_INTERVAL'] = [0, 10]
        self['TYPE_AREA'] = '7' 
        
    
        
        
###############################################################################
class ToleranceFilter(FilterBase):
    """
    Class to hold tolerance filter settings.  
    Typically this information is read from a file. 
    """
    def __init__(self, parameter): 
        self.parameter = parameter 
        self._initate_filter_items()
        self.load_dummy_settings()
        
    #==========================================================================
    def _initate_filter_items(self):
        self.filter_items = ['MIN_NR_VALUES']
        
    #==========================================================================
    def load_settings_from_file(self, file_path):
        self.file_path = file_path 
        
    #==========================================================================
    def write_settings_to_file(self, file_path):
        self.file_path = file_path
        
    #==========================================================================
    def set_filter(self, filter_type, value): 
        filter_type = filter_type.upper().replace(' ', '_')
        if filter_type not in self.filter_list:
            return
        # TODO: Make checks for different kinds of tolerance. 
        self[filter_type] = value
        
    #==========================================================================
    def load_dummy_settings(self): 
        """
        Temporary method to have attributes to play with during development. 
        """
        self._pop_all_self()
        self['MIN_NR_VALUES'] = 3 
        
        
        
        