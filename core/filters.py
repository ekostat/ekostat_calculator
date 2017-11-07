# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 11:04:47 2017

@author: a001985
"""
import os
import codecs  
import pandas as pd

#if current_path not in sys.path: 
#    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

try:
    import core
except:
    pass
###############################################################################
class DataFilter(object):
    """
    Holds information about data filter. 
    Data filter is built up with several files listed in the given direktory. 
    """
    #==========================================================================
    def __init__(self, filter_directory): 
        self.filter_directory = filter_directory
        self.filter_file_paths = {} 
        self.list_filter = {} 
        
        self.load_filter_files()
        
    #==========================================================================
    def get_list_filter(self, filter_name):
        return self.list_filter.get(filter_name, False)
        
    #==========================================================================
    def load_filter_files(self): 
        self.filter_file_paths = {} 
        self.list_filter = {} 
        for file_name in [item for item in os.listdir(self.filter_directory) if item.endswith('.fil')]: 
#            print('-'*70)
            file_path = os.path.join(self.filter_directory, file_name).replace('\\', '/') 
            filter_name = file_name[:-4] 
#            print('load:', filter_name)
            
            # Save filter path
            self.filter_file_paths[filter_name] = file_path
            
            # Load filters 
            if filter_name == 'areas':
                pass
            elif filter_name.startswith('list_'):
                with codecs.open(file_path, 'r', encoding='cp1252') as fid: 
                    self.list_filter[filter_name] = [item.strip() for item in fid.readlines()]
#            print('Loaded list:', self.list_filter[filter_name]) 
            
    #==========================================================================
    def save_filter_files(self): 
        for filter_name in self.list_filter.keys():
            print('save:', filter_name)
            if filter_name == 'areas':
                pass
            elif filter_name.startswith('list_'): 
                with codecs.open(self.filter_file_paths[filter_name], 'w', encoding='cp1252') as fid: 
                    for item in self.list_filter[filter_name]:
                        fid.write(item) 
                        fid.write('\n')
                    
    #==========================================================================
    def set_list_filter(self, filter_name, filter_list, save_files=True): 
        if filter_name not in self.list_filter.keys():
            return False
        filter_list = sorted(set([item.strip() for item in filter_list]))
        self.list_filter[filter_name] = filter_list
        if save_files: 
            self.save_filter_files()
                    
        
###############################################################################
class SettingsFile(object):
    """
    Holds Settings file information. Reading and writing file. Basic file handling. 
    """
    #==========================================================================
    def __init__(self, file_path):
        self.file_path = file_path 
        self.indicator = os.path.basename(file_path)[:-4]
        
        self.int_columns = [] 
        self.str_columns = [] 
        
        self.interval_columns = []
        self.list_columns = [] 
        
        self.filter_columns = [] 
        self.ref_columns = [] 
        self.tolerance_columns = []
        
        self.connected_to_filter_settings_object = False
        self.connected_to_ref_settings_object = False
        self.connected_to_tolerance_settings_object = False
        
        self._prefix_list = ['FILTER', 'REF', 'TOLERANCE'] 
        self._suffix_list = ['INT', 'EKV']
        
        self._load_file()
    
    
    #==========================================================================
    def _load_file(self):
        self.df = pd.read_csv(self.file_path, sep='\t', dtype='str', encoding='cp1252') 
        
        # Save columns
        self.columns_in_file = list(self.df.columns)
        self.columns = []
        for col in self.df.columns: 
            col = col.upper() 
            
            parts = col.split('_') 
            # First check if col has prefix or suffix 
            if parts[0] not in self._prefix_list:
                col = '_' + col 
            if parts[-1] not in self._suffix_list:
                col = col + '_'
            
            # Now split again and extracts part 
            parts = col.split('_') 
            variable = '_'.join(parts[1:-1])
            prefix = parts[0]
            suffix = parts[-1]
            
            #------------------------------------------------------------------
            # Prefix 
            if prefix == 'FILTER':
                self.filter_columns.append(variable)
            elif prefix == 'REF': 
                self.ref_columns.append(variable) 
            elif prefix == 'TOLERANCE': 
                self.tolerance_columns.append(variable)
            
            #------------------------------------------------------------------
            # Suffix
            if suffix == 'STR': 
                self.str_columns.append(variable)
            elif suffix == 'INT': 
                self.int_columns.append(variable) 
            
            #------------------------------------------------------------------
            # Contains
            if 'INTERVAL' in variable:
                self.interval_columns.append(variable) 
                
            if 'LIST' in variable:
                self.list_columns.append(variable)
            
            self.columns.append(variable)
            
        # Set new column names 
        self.df.columns = self.columns 
        
        self.type_area_list = list(self.df['TYPE_AREA'])
        
        
    #==========================================================================
    def change_path(self, new_file_path):
        if not os.path.exists(new_file_path): 
            print('Invalid file_path for file: {}\nOld file_path is {}'.format(new_file_path, self.file_path))
            return False
        self.file_path = new_file_path
        
    #==========================================================================
    def save_file(self, file_path=None):
        if not file_path:
            file_path = self.file_path
        # Rename columns 
        self.df.columns = self.columns_in_file 
        
        self.df.to_csv(file_path, sep='\t', encoding='cp1252', index=False) 
        
        self.df.columns = self.columns

    #==========================================================================
    def get_value(self, type_area=None, variable=None): 
        if type_area not in self.type_area_list:
            return False
        variable = variable.upper() 
        assert all([type_area, variable]), 'Must provide: type_area and variable' 
        value = self.df.loc[self.df['TYPE_AREA']==type_area, variable.upper()].values[0]
        if variable in self.list_columns: 
            value = self._get_list_from_string(value, variable)
        elif variable in self.interval_columns: 
            value = self._get_interval_from_string(value, variable)
        else:
            value = self._convert(value)
        return value
    
    #==========================================================================
    def set_value(self, type_area=None, variable=None, value=None): 
        if type_area not in self.type_area_list:
            return False
        if variable in self.list_columns: 
            print('List column')
            value = self._get_string_from_list(value, variable)
        elif variable in self.interval_columns: 
            print('Interval column')
            value = self._get_string_from_interval(value, variable) 
        
        if value == False: 
            print('Value could not be changed!')
            return False
        else:
            print('Value to set for type_area "{}" and variable "{}": {}'.format(type_area, variable, value))
            self.df.loc[self.df['TYPE_AREA']==type_area, variable] = value
            return True
        
    #==========================================================================
    def set_values(self, value_dict): 
        """
        Sets values for several type_areas and variables. 
        Values to be set are given in dict like: 
            value_dict[type_area][variable] = value 
        """
        all_ok = True
        for type_area in value_dict.keys():
            for variable in value_dict[type_area].keys(): 
                value = value_dict[type_area][variable]
                if not self.set_value(type_area, variable, value):
                    all_ok = False
        return all_ok
    
    #==========================================================================
    def _get_list_from_string(self, value, variable): 
        return_list = []
        for item in value.split(';'):
            item = self._convert(item.strip(), variable)
            return_list.append(item)
        return return_list
    
    #==========================================================================
    def _get_interval_from_string(self, value, variable): 
        return_list = []
        for item in value.split('-'):
            item = self._convert(item.strip(), variable)
            return_list.append(item)
        return return_list
    
    #==========================================================================
    def _get_string_from_list(self, value, variable): 
        item_list = []
        for item in value:
            if not self._valid_value(item, variable):
                return False
            else:
                item_list.append(str(item))
        return ';'.join(item_list)
    
    #==========================================================================
    def _get_string_from_interval(self, value, variable): 
        item_list = []
        for item in value:
            if not self._valid_value(item, variable):
                return False
            else:
                item_list.append(str(item))
        return '-'.join(item_list)

    #==========================================================================
    def _convert(self, value, variable):
        if variable in self.int_columns: 
            return int(value)
        return value
    
    #==========================================================================
    def _valid_value(self, value, variable): 
        """
        Checks the validity of a value based on the variable. 
        """
        if 'MONTH' in variable: 
            if int(value) not in list(range(1,13)):
                return False
        return True
    
    #==========================================================================
    def get_filter_boolean(self, df=None, type_area=None, parameter=None): 
        """
        Get boolean tuple to use for filtering
        """
        combined_boolean = ()
        for variable in self.filter_columns: 
            if variable in self.interval_columns:
                boolean = self._get_boolean_from_interval(df=df, 
                                                          type_area=type_area, 
                                                          variable=variable) 
            elif variable in self.list_columns:
                boolean = self._get_boolean_from_list(df=df, 
                                                      type_area=type_area, 
                                                      variable=variable) 
            else:
                print('No boolean for "{}"'.format(variable))
                continue
            
            if not type(boolean) == pd.Series:
                continue            
            if type(combined_boolean) == pd.Series:
                combined_boolean = combined_boolean & boolean
            else:
                combined_boolean = boolean 
        return combined_boolean
    
    #==========================================================================
    def _get_boolean_from_interval(self, df=None, type_area=None, variable=None, parameter=None): 
        from_value, to_value = self.get_value(type_area=type_area, 
                                              variable=variable)
        return (self.df[parameter] >= from_value) & (df[variable] <= to_value)

    #==========================================================================
    def _get_boolean_from_list(self, df=None, type_area=None, variable=None, parameter=None):
        value_list = self.get_value(type_area=type_area, 
                                    variable=variable)
        return df[parameter].isin(value_list)
    
    
###############################################################################
class SettingsRef(object):
    """
    Handles ref settings. 
    """
    #==========================================================================
    def __init__(self, settings_file_object): 
        self.settings = settings_file_object 
        self.settings.connected_to_ref_settings_object = True
        
        
###############################################################################
class SettingsFilter(object):
    """
    Handles filter settings. 
    """
    #==========================================================================
    def __init__(self, settings_file_object): 
        self.settings = settings_file_object 
        self.settings.connected_to_filter_settings_object = True
        
    #==========================================================================
    def get_column_data_boolean(self, df=None, type_area=None): 
        """
        Get boolean tuple to use for filtering
        """
        return self.settings.get_filter_boolean(df=df, 
                                                type_area=type_area)
        

    #==========================================================================
    def set_values(self, value_dict): 
        """
        Sets values for several type_areas and variables. 
        Values to be set are given in dict like: 
            value_dict[type_area][variable] = value 
        """
        self.settings.set_values(value_dict) 
        self.settings.save_file()


###############################################################################
class SettingsTolerance(object):
    """
    Handles tolerance settings. 
    """
    #==========================================================================
    def __init__(self, settings_file_object): 
        self.settings = settings_file_object 
        self.settings.connected_to_tolerance_settings_object = True



###############################################################################
class old_SingleFilter(object):
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
class old_DataFilter(FilterBase):
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
    def get_column_data_boolean(self, df): 
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
    
    root_directory = os.path.dirname(os.path.abspath(__file__))[:-5]
    print('root directory is "{}"'.format(root_directory))
    
    
    
    ###########################################################################
    if 0:
        # MW test for SetingsFile 
        raw_data_file_path = root_directory + '/test_data/raw_data/data_BAS_2000-2009.txt'
        first_data_filter_file_path = root_directory + '/resources/indicator_settings/first_data_filter.txt' 
        
        raw_data = core.DataHandler('raw')
        raw_data.add_txt_file(raw_data_file_path, data_type='column') 
        
        # Use first filter 
        print('{}\nApply data filters\n'.format('*'*nr_marks))
        first_filter = core.DataFilter('First filter', file_path=first_data_filter_file_path)
        filtered_data = raw_data.filter_data(first_filter) 
        
        file_path = root_directory + '/resources/indicator_settings/din_winter_settings.txt'
        output_file_path = root_directory + '/resources/indicator_settings/din_winter_settings_save.txt'
        s = SettingsFile(file_path) 
        
        month = s.get_value('2', 'MONTH_LIST')
        s.set_value('2', 'MONTH_LIST', [1,2,3])
        
        set_value_dict = {'1n': {'DEPTH_INTERVAL': [0, 20], 
                                 'MONTH_LIST': [3,4,5]}, 
                          '3': {'MIN_NR_VALUES': 10}}
        s.set_values(set_value_dict)
        s.save_file(output_file_path)
    
        
        sf = SettingsFilter(s)
    
    
    
    
    
    if 1:
        filter_directory = 'D:/Utveckling/g_ekostat_calculator/ekostat_calculator_lena/workspaces/default/step_0/data_filters' 
        d = DataFilter(filter_directory) 
        y = d.get_list_filter('list_year') 
        y.append('2017') 
        d.set_list_filter('list_year', y)
    
    
    
    
    
    
    ###########################################################################
    if 0:
        root_directory = os.path.dirname(os.path.abspath(__file__))[:-9]
        
        print(root_directory)
        
        data_filter_file_path = root_directory + '/test_data/filters/data_filter_template.txt'
        f = DataFilter('test', file_path=data_filter_file_path)
        f.set_filter('YEAR_INTERVAL', '2000-2006')
    
    
    print('-'*nr_marks)
    print('done')
    print('-'*nr_marks)
    
    
    
    
    
    
    
    
    
    
        