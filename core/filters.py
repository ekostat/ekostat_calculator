# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 11:04:47 2017

@author: a001985
"""
import os
import codecs  
import pandas as pd
    
###############################################################################
class SingleFilter(object):
    """
    Holds information about and methods for a single filter. 
    """
    #==========================================================================
    def __init__(self, line_dict, parameter):
        
        self.header = sorted(line_dict.keys())
        self.comment = line_dict['comment']
        self.variable = line_dict['variable']
        self.parameter = line_dict['parameter']
        if not self.parameter:
            self.par = parameter # This is to keep track of self in filter settings file
        else:
            self.par = self.parameter
        self.dtype = line_dict['dtype']
        self.variable_type = None
        
        value = line_dict['value']
        self.set_filter(value)
        
    #==========================================================================
    def set_filter(self, value): 
        """
        Determines if the filter is one given value, an interval or a list of values
        """
        if not value:
            self.value = value
        elif type(value) == list:
            self.variable_type = 'list' # LENA: added this, or is variable_type for this case already set?
            self.value = [self._convert(item) for item in value]
        elif '-' in value: 
            self.variable_type = 'interval'
            self.value = [self._convert(item) for item in value.split('-')] 
        elif ',' in value: 
            self.variable_type = 'list' 
            self.value = [self._convert(item) for item in value.split(',')] 
        else:
            self.variable_type = 'single value' # LENA: added this, or is variable_type for this case already set?
            self.value = self._convert(value)
        
    #==========================================================================
    def _convert(self, item):
        item = item.strip()
        if self.dtype == 'int':
            return int(item)
        elif self.dtype == 'float':
            return float(item) 
        return item
    
    #==========================================================================
    def get_boolean(self, df): 
        """
        Returns a boolean array for matching filter in dataframe. 
        """
        if not self.value:
            return False
        elif not self.par:
            return ()
        if self.variable_type == 'interval':
            return self._interval_boolean(df)
        elif self.variable_type == 'list':
            return self._list_boolean(df)
        
    #==========================================================================
    def _interval_boolean(self, df):
        return (df[self.par] >= self.value[0]) & (df[self.par] <= self.value[1])

    #==========================================================================
    def _list_boolean(self, df):
        return df[self.par].isin(self.value)
    
    #==========================================================================
    def write_to_fid(self, fid):
        item_list = []
        for item in self.header:
            value = getattr(self, item)
            if item == 'value':
                if self.variable_type == 'interval':
                    value = '-'.join(map(str, value))
                if self.variable_type == 'list':
                    value = ','.join(map(str, value))
            else:
                value = str(value)
            item_list.append(value)
        fid.write('\t'.join(item_list)) 
        
    
    
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
    def set_filter(self, filter_variable, value): 
        
        filter_variable = filter_variable.upper().replace(' ', '_')       
        self[filter_variable].set_filter(value)

    #==========================================================================
    def load_filter_file(self, file_path):
        """
        Filter items are saved in self (dict). 
        """ 
        self._pop_all_self()
        self.filter_list = []
        self.file_path = file_path 
        
        with codecs.open(self.file_path, 'r', encoding='cp1252') as fid: 
            for k, line in enumerate(fid):
                line = line.lstrip('\n\r ')
                if line.startswith('#'):
                    continue 
                split_line = [item.strip() for item in line.split('\t')]
                if k==0:
                    # Header
                    header = split_line
                else:
                    line_dict = dict(zip(header, split_line))
                    self[line_dict['variable']] = SingleFilter(line_dict, self.parameter)

        # Save attributes
        for item in self.keys():
            setattr(self, item, self[item])
            
        self.header = sorted(header)
        
        if self.filter_type == 'data':
            self.year_list = [y for y in range(self['YEAR_INTERVAL'].value[0], 
                                                   self['YEAR_INTERVAL'].value[1]+1)]
                    
    #==========================================================================
    def save_filter_file(self, file_path):
        self.file_path = file_path
        
        with codecs.open(self.file_path, 'w') as fid:
            fid.write('\t'.join(self.header))
            fid.write('\n')
            for item in sorted(self.keys()): 
                self[item].write_to_fid(fid)
                fid.write('\n')
                
    #==========================================================================
    def show_filter(self):
        for key, item in self.items():
            print(key, item.value)
        
###############################################################################
class DataFilter(FilterBase):
    """
    Class to hold data filter settings.  
    Typically this information is read from a file. 
    Maybe this filter should be different for different 
    """
    def __init__(self, source, parameter='', file_path=None): 
        """
        parameter is to specify the parameter that the filter is passed to. 
        """
        super().__init__() 
        self.filter_type = 'data'
        self.source = source
        self.parameter = parameter
        self._initate_filter_items()
        if file_path:
            self.load_filter_file(file_path)

    #==========================================================================
    def _initate_filter_items(self):
        # LENA: flytta MONTH_LIST och DEPTH_INTERVAL till tolerance filter
        # LENA: lägg till 'WATER_DISTRICTS' och 'WATER_BODIES', ändra till 'TYPE_AREAS'
        self.filter_list = ['DEPTH_INTERVAL', 
                            'TYPE_AREA', 
                            'MONTH_LIST', 
                            'YEAR_INTERVAL']
            
    #==========================================================================
    def get_boolean(self, df): 
        """
        Get boolean tuple to use for filtering
        """
        # LENA: Ska inte detta ligga i FilterBase, om inte varför? 
        # Behövs i tolerance filter också om vi flyttar month_list och depth_interval dit
        combined_boolean = ()
        for item in self.keys():
            boolean = self[item].get_boolean(df)
            if not type(boolean) == pd.Series:
                continue            
            if type(combined_boolean) == pd.Series:
#                print(len(combined_boolean), len(boolean))
                combined_boolean = combined_boolean & boolean
            else:
                combined_boolean = boolean
        return combined_boolean
        
        
###############################################################################
class ToleranceFilter(FilterBase):
    """
    Class to hold tolerance filter settings.  
    Typically this information is read from a file. 
    """
    def __init__(self, source, parameter='', file_path=None): 
        """
        parameter is to specify the parameter that the filter is passed to. 
        """
        super().__init__() 
        self.filter_type = 'tolerance'
        self.source = source
        self.parameter = parameter
        self._initate_filter_items()
        if file_path:
            self.load_filter_file(file_path)

    #==========================================================================
    def _initate_filter_items(self):
        # LENA: lägg till MONTH_LIST och DEPTH_INTERVAL till tolerance filter
        self.filter_items = ['MIN_NR_VALUES', 'TIME_DELTA']  
        # Time delta in hours
        
        
###############################################################################
if __name__ == '__main__':
    nr_marks = 60
    print('='*nr_marks)
    print('Running module "filters.py"')
    print('-'*nr_marks)
    print('')   
    
    root_directory = os.path.dirname(os.path.abspath(__file__))[:-9]
    
    print(root_directory)
    
    data_filter_file_path = root_directory + '/test_data/filters/data_filter_template.txt'
    f = DataFilter('test', file_path=data_filter_file_path)
    f.set_filter('YEAR_INTERVAL', '2000-2006')
    
    
    print('-'*nr_marks)
    print('done')
    print('-'*nr_marks)
    
    
    
    
    
    
    
    
    
    
        