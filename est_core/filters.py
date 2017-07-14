# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 11:04:47 2017

@author: a001985
"""
import codecs 


###############################################################################
class SingleFilterBase(object):
    
    #==========================================================================
    def __init__(self, cls): 
        self.variable = str(self)
        self.value = None 
        self.filter_type = None
        self.dtype = None
        self.comment = ''
    
###############################################################################
class SingleFilter(object):
    """
    Holds information about a single filter. 
    """
    #==========================================================================
    def __new__(cls, data_type=None): 
        if dtype == 'str':
            return super(str, cls).__new__(cls)
        elif dtype == 'int':
            return super(int, cls).__new__(cls)
        elif dtype == 'float':
            return super(float, cls).__new__(cls)
#            return str.__new__(cls)
    
    def __init__(self, cls, data_type=None): 
        self.variable = str(self)
        self.value = None 
        self.filter_type = None
        self.dtype = None
        self.comment = ''

###############################################################################
class SingleFilterInt(int):
    """
    Holds information about a single filter. 
    """
    def __new__(cls, *args, **kw): 
        return int.__new__(cls, *args, **kw)
    
#    def __init__(self, cls): 
#        self.variable = int(self)
#        self.value = None 
#        self.filter_type = None
#        self.dtype = None
#        self.comment = ''

###############################################################################
class SingleFilterFloat(float):
    """
    Holds information about a single filter. 
    """
    def __new__(cls, *args, **kw): 
        return float.__new__(cls, *args, **kw)
    
#    def __init__(self, cls): 
#        self.variable = float(self)
#        self.value = None 
#        self.filter_type = None
#        self.dtype = None
#        self.comment = ''


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
            
    #==========================================================================
    def set_filter(self, filter_type, value): 
        filter_type = filter_type.upper().replace(' ', '_')
        if filter_type not in self.filter_list:
            return
        # TODO: Make checks for different kinds of tolerance. 
        self[filter_type] = value
            

###############################################################################
class DataFilter(FilterBase):
    """
    Class to hold data filter settings.  
    Typically this information is read from a file. 
    Maybe this filter should be different for different 
    """
    def __init__(self, source, file_path=None): 
        super().__init__() 
        self.source = source
        self._initate_filter_items()
        if file_path:
            self.load_data_filter_file(file_path)
        else:
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
        with codecs.open(self.file_path, 'r', encoding='cp1252') as fid: 
            for line in fid:
                line = line.lstrip('\n\r ')
                if line.startswith('#'):
                    continue 
                
                varaible, value, dtype, comment = line.split('\t')
                
                if '-' in value:
                    value = value.replace('-', ',')
                
                if dtype == 'int':
                    self[varaible] = [int(item.strip()) for item in value.split(',')]
                elif dtype == 'float':
                    self[varaible] = [float(item.strip()) for item in value.split(',')]
                else:
                    self[varaible] = [item.strip() for item in value.split(',')]
                    
                if len(self[varaible]) == 1:
                    self[varaible] = self[varaible][0]
        
    #==========================================================================
    def save_data_filter_file(self, file_path):
        self.file_path = file_path
        
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
    def __init__(self, source, file_path=None): 
        super().__init__() 
        self.source = source
        self._initate_filter_items()
        if file_path:
            self.load_tolerance_filter_file(file_path)
        else:
            self.load_dummy_settings()
        
    #==========================================================================
    def _initate_filter_items(self):
        self.filter_items = ['MIN_NR_VALUES', 'TIME_DELTA']  
        # Time delta in hours
        
    #==========================================================================
    def load_tolerance_filter_file(self, file_path):
        self.file_path = file_path 
        
        with codecs.open(self.file_path, 'r', encoding='cp1252') as fid: 
            for line in fid:
                line = line.lstrip('\n\r ')
                if line.startswith('#'):
                    continue 
                
                varaible, value, dtype, comment = line.split('\t')
                
                if dtype == 'int':
                    self[varaible] = [int(item.strip()) for item in value.split(',')]
                elif dtype == 'float':
                    self[varaible] = [float(item.strip()) for item in value.split(',')]
                else:
                    self[varaible] = [item.strip() for item in value.split(',')]
                    
                if len(self[varaible]) == 1:
                    self[varaible] = self[varaible][0]
        
    #==========================================================================
    def save_tolerance_filter_file(self, file_path):
        self.file_path = file_path
        
    #==========================================================================
    def load_dummy_settings(self): 
        """
        Temporary method to have attributes to play with during development. 
        """
        self._pop_all_self()
        self['MIN_NR_VALUES'] = 3 
        self['TIME_DELTA'] = 10
        
        
        
        