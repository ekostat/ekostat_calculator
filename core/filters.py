# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 11:04:47 2017

@author: a001985
"""
import os
import codecs  
import pandas as pd
import numpy as np
import utils
import re

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
    def __init__(self, 
                 filter_directory, 
                 mapping_objects={}): 
        self.filter_directory = filter_directory
        self.filter_file_paths = {} 
        self.include_list_filter = {} 
        self.exclude_list_filter = {} 
        self.include_header_filter = {}
        self.exclude_header_filter = {}
        self.all_filters = {}
        
        self.mapping_water_body = mapping_objects['water_body']
        
        self.load_filter_files()
        
    #==========================================================================
    def _get_filter_boolean_for_df_from_exclude_list(self, df=None, parameter=None): 
        parameter = parameter.upper()
        value_list = self.get_exclude_list_filter(parameter)
        if not value_list:
            return False
        return ~df[parameter].astype(str).isin(value_list)
    
    #==========================================================================
    def _get_filter_boolean_for_df_from_include_list(self, df=None, parameter=None): 
        parameter = parameter.upper()
        value_list = self.get_include_list_filter(parameter)
        if not value_list:
            return False
        return df[parameter].astype(str).isin(value_list)

    
    #==========================================================================
    def deprecate_include_statn(self, statn, include_current=False):
        """
        statn => water_body => type_area => water_district
        Makes sure that the water_body containing the station is included in the include_water_body filter. 
        include_current nor used
        """
        if type(statn) != list:
            statn = list(statn) 
        
        statn = sorted(set([item.strip() for item in statn]))
        self.include_list_filter['STATN'] = statn
         
        water_body_list = self.include_list_filter['WATER_BODY_NAME'][:] 
        # Add water bodies
        for s in statn: 
            #TODO: Link between statn and water body
            water_body_list.append('')
             
        self.include_water_body(water_body_list)
        
    
    #==========================================================================
    def deprecate_include_type_area(self, type_area, include_current=False): 
        """
        type_area => water_district
        include_current nor used
        """
        if type(type_area) != list:
            type_area = list(type_area) 
        
        type_area = sorted(set([item.strip() for item in type_area]))
        self.include_list_filter['TYPE_AREA_NUMBER'] = type_area 
         
        water_district_list = self.include_list_filter['WATER_DISTRICT_NAME'][:] 
        # Add water districts
        for ta in type_area: 
            #TODO: Link between type area and water district
            water_district_list.append('')

        self.include_water_district(water_district_list)

    #==========================================================================
    def deprecate_include_water_district(self, water_district, include_current=False): 
        """
        water_district
        include_current nor used
        """
        water_district = sorted(set([item.strip() for item in water_district]))
        self.include_list_filter['WATER_DISTRICT_NAME'] = water_district
        
    #==========================================================================
    def deprecate_include_water_body(self, water_body, include_current=False): 
        """
        water_body => type_area => water_district
        include_current nor used
        """
        if type(water_body) != list:
            water_body = list(water_body) 
        
        water_body = sorted(set([item.strip() for item in water_body]))
        self.include_list_filter['WATER_BODY_NAME'] = water_body[:]
        
        # Get current type areas
        type_area_list = self.include_list_filter['TYPE_AREA_NUMBER'][:] 
        
        for wb in water_body:
            type_area_list.append(self.mapping_water_body.get_type_area_for_water_body(wb, include_suffix=True))
             
        self.include_type_area(type_area_list)
        
    #==========================================================================
    def get_filter_boolean_for_df(self, df=None, **kwargs): 
        """
        Get boolean tuple to use for filtering. 
        kwargs here so that all methods named get_filter_boolean_for_df can be treeted the same way. 
        """
        combined_boolean = ()
        
        #----------------------------------------------------------------------
        # Filter exclude list 
        for par in sorted(self.exclude_list_filter.keys()): 
            boolean = self._get_filter_boolean_for_df_from_exclude_list(df=df, parameter=par)

            if not type(boolean) == pd.Series:
                continue            
            if type(combined_boolean) == pd.Series:
                combined_boolean = combined_boolean & boolean
            else:
                combined_boolean = boolean 
        
        #----------------------------------------------------------------------
        # Filter include list 
        for par in sorted(self.include_list_filter.keys()):
            boolean = self._get_filter_boolean_for_df_from_include_list(df=df, parameter=par)

            if not type(boolean) == pd.Series:
                continue            
            if type(combined_boolean) == pd.Series:
                combined_boolean = combined_boolean & boolean
            else:
                combined_boolean = boolean 
                
        if len(combined_boolean) == 0: 
            combined_boolean = pd.Series(np.ones(len(df), dtype=bool))
            
        return combined_boolean

    #==========================================================================
    def get_filter_header_for_df(self, df=None):
        
        self.df = self.df.drop(columns, axis=1, errors='ignore')

    #==========================================================================
    def get_exclude_header_filter(self, filter_name):
        return self.exclude_header_filter.get(filter_name.upper(), False)
    
    #==========================================================================
    def get_include_header_filter(self, filter_name):
        return self.include_header_filter.get(filter_name.upper(), False)
     
    #==========================================================================
    def get_exclude_list_filter(self, filter_name):
        return self.exclude_list_filter.get(filter_name.upper(), False)
    
    #==========================================================================
    def get_exclude_list_filter_names(self):
        return sorted(self.exclude_list_filter.keys())
    
    #==========================================================================
    def get_include_list_filter(self, filter_name):
        return self.include_list_filter.get(filter_name.upper(), False)
        
    #==========================================================================
    def get_include_list_filter_names(self):
        return sorted(self.include_list_filter.keys())
        
    #==========================================================================
    def get_filter_info(self):
        return self.all_filters 
    
    #==========================================================================
    def load_filter_files(self): 
        self.filter_file_paths = {}
        self.include_list_filter = {}
        self.exclude_list_filter = {}
        self.all_filters = {}
        for file_name in [item for item in os.listdir(self.filter_directory) if item.endswith('.fil')]: 
#            print('-'*70)
            file_path = os.path.join(self.filter_directory, file_name).replace('\\', '/')
            long_name = file_name[:-4].upper()
#            print('load:', filter_name)
            
            # Save filter path
            self.filter_file_paths[long_name] = file_path
            
            # Load filters 
            if long_name.startswith('areas'):
                pass
            elif long_name.startswith('LIST_'):
                filter_name = long_name[5:] 
                with codecs.open(file_path, 'r', encoding='cp1252') as fid: 
                    if filter_name.startswith('EXCLUDE_'): 
                        self.exclude_list_filter[filter_name[8:]] = [item.strip() for item in fid.readlines()]
                    elif filter_name.startswith('INCLUDE_'): 
                        self.include_list_filter[filter_name[8:]] = [item.strip() for item in fid.readlines()]
#            print('Loaded list:', self.include_list_filter[filter_name]) 
        
        #----------------------------------------------------------------------
        # Add info to self.all_filters
        # Exclude list 
        self.all_filters['exclude_list'] = self.get_exclude_list_filter_names()
        
        # Include list 
        self.all_filters['include_list'] = self.get_include_list_filter_names()
        
            
    #==========================================================================
    def save_filter_files(self): 
            
        # Exclude list filter 
#        print(self.exclude_list_filter.keys())
        for filter_name in self.exclude_list_filter.keys(): 
            long_name = 'LIST_EXCLUDE_' + filter_name
            file_path = self.filter_file_paths[long_name]
#            print('Save: "{}" to file: "{}"'.format(filter_name, file_path))
            with codecs.open(file_path, 'w', encoding='cp1252') as fid: 
                for item in self.exclude_list_filter[filter_name]:
                    fid.write(item)
                    fid.write('\n')
                    
        # Include list filter 
#        print(self.include_list_filter.keys())
        for filter_name in self.include_list_filter.keys(): 
            long_name = 'LIST_INCLUDE_' + filter_name
            file_path = self.filter_file_paths[long_name.upper()]
#            print('Save: "{}" to file: "{}"'.format(filter_name, file_path))
            with codecs.open(file_path, 'w', encoding='cp1252') as fid: 
                for item in self.include_list_filter[filter_name]:
                    fid.write(item)
                    fid.write('\n')
              
    #==========================================================================
    def set_filter(self, filter_type=None, filter_name=None, data=None, save_filter=True, append_items=False): 
        """
        Sets the given filter_name of the given filter_type to data. 
        Option to save or not. 
        filter_types could be: 
            include_list
            exclude_list 
        OBS! 
        Files are not loaded before change. 
        This means that changes in files will not be seen by the object if working in self updating notebook. 
        """
#        print('11')
#        print(filter_type) 
#        print(filter_name)
#        print(data)
#        print(save_filter)
        if filter_type == 'exclude_list':
            return self.set_exclude_list_filter(filter_name=filter_name, 
                                                filter_list=data, 
                                                save_files=save_filter, 
                                                append_items=append_items)
        elif filter_type == 'include_list':
            return self.set_include_list_filter(filter_name=filter_name, 
                                                filter_list=data, 
                                                save_files=save_filter, 
                                                append_items=append_items)
        
    #==========================================================================
    def set_include_list_filter(self, filter_name=None, filter_list=None, save_files=True, append_items=False): 
        """
        Created     ????????    by Magnus Wenzer
        Updated     20180315    by Magnus Wenzer
        """
        filter_name = filter_name.upper()
        if filter_name not in self.include_list_filter.keys():
            return False

#        if filter_name == 'WATER_BODY_NAME':
#            self.include_water_body(filter_list)
#        else:
#            filter_list = sorted(set([item.strip() for item in filter_list]))
#                
#            self.include_list_filter[filter_name] = filter_list

        if append_items:
            filter_list = filter_list + self.get_include_list_filter(filter_name)
#        print('filter_list'.upper(), filter_list)
        filter_list = sorted(set([item.strip() for item in map(str, filter_list)]))
        self.include_list_filter[filter_name] = filter_list
        
        if save_files: 
            self.save_filter_files() 
        return True
    
    #==========================================================================
    def set_exclude_list_filter(self, filter_name, filter_list, save_files=True, append_items=False): 
        if filter_name not in self.exclude_list_filter.keys():
            return False
        if append_items:
            filter_list = filter_list + self.get_exclude_list_filter(filter_name)
        filter_list = sorted(set([item.strip() for item in filter_list]))
        self.exclude_list_filter[filter_name] = filter_list
        if save_files: 
            self.save_filter_files()
        return True
    

###############################################################################
class DataFilterFile(object):
    """
    Get and write information to data filet file. 
    """
    def __init__(self, file_path=None, directory=None, file_name=None, string_in_file='ekostat'): 
        if file_path:
            if not string_in_file in os.path.basename(file_path):
                self.file_path = None 
            else:
                self.file_path = file_path.replace('\\', '/') 
        elif directory and file_name: 
            if not string_in_file in file_name:
                self.file_path = None 
            else:
                self.file_path = '{}/{}'.format(directory, file_name).replace('\\', '/')
            
        else:
            self.file_path = None 
            
        
        # string_in_file is for safety. Files not containing string_in_file will be discarded. 
        self.string_in_file = string_in_file 
            
    #==========================================================================
    def set_filter(self, data_list): 
        if not self.file_path:
            return False
        if type(data_list) == str: 
            data_list = [data_list]
        with codecs.open(self.file_path, 'w', encoding='cp1252') as fid: 
            fid.write('\n'.join(data_list)) 
        return True
            
    #==========================================================================
    def get_filter(self): 
        if not self.file_path:
            return False
        elif not os.path.exists(self.file_path): 
            return []
        
        data_list = []
        with codecs.open(self.file_path, 'r', encoding='cp1252') as fid: 
            data_list.append(fid.readline().strip())
        return data_list 
    
    #==========================================================================
    def clear_filter(self): 
        if not self.file_path:
            return False
        elif not os.path.exists(self.file_path): 
            return False 
        # Remove file 
        os.remove(self.file_path)
        
    
###############################################################################
class SettingsFile(object):
    """
    Holds Settings file information. Reading and writing file. Basic file handling. 
    """
    #==========================================================================
    def __init__(self, file_path, mapping_objects=None):
        self.file_path = file_path 
        self.indicator = os.path.basename(file_path)[:-4]
        
        self.mapping_objects = mapping_objects
        self.mapping_water_body = mapping_objects['water_body']
        
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
        suffix_list = []
        for val in self.df['TYPE_AREA_SUFFIX'].astype(str):
            if val == 'nan':
                suffix_list.append('')
            else:
                suffix_list.append(val)
        self.df['TYPE_AREA_SUFFIX'] = suffix_list
        # Oklart med dtype här. Battre inlasning kravs! MW
#        self.type_area_list = list(self.df['TYPE_AREA_NUMBER'])
        
        
        
    #==========================================================================
    def change_path(self, new_file_path):
#        if not os.path.exists(new_file_path): 
#            print('Invalid file_path for file: {}\nOld file_path is {}'.format(new_file_path, self.file_path))
#            return False
        self.file_path = new_file_path
        return True
        
    #==========================================================================
    def save_file(self, file_path=None):
        if not file_path:
            file_path = self.file_path
        # Rename columns 
        self.df.columns = self.columns_in_file 
        
        self.df.to_csv(file_path, sep='\t', encoding='cp1252', index=False) 
        
        self.df.columns = self.columns

    #==========================================================================
    def old_get_value(self, filter_dict=None, variable=None): 
        """
        get value from settings file
        filter_dict: keys and values to filter on
        variable: settings variable to get value for 
        """ 
        
#        print(filter_dict)
#        print(variable)
        if 'TYPE_AREA_NUMBER' in list(filter_dict.keys()): 
            if filter_dict['TYPE_AREA_NUMBER'][0] not in self.type_area_list:
                return False
        
        variable = variable.upper() 
        assert all(['TYPE_AREA_NUMBER' in list(filter_dict.keys()), variable]), 'Must provide: type_area number in filter_dict and variable' 
        assert variable.upper() in self.df.columns, 'Must provide filtervariable from settingsfile\n\t{}'.format(self.df.columns)
        boolean_list = utils.set_filter(df = self.df, filter_dict = filter_dict, return_dataframe = False)
        # TODO: How made this with utils.set_filter. Dont think we need this? /MW
        
        
        value = self.df.loc[boolean_list, variable.upper()].values  
        
        assert len(value) == 1, 'More than one setting for given filter_dict\n{}'.format(value)
        
        value = value[0]    
        if variable in self.list_columns: 
            value = self._get_list_from_string(value, variable)
        elif variable in self.interval_columns: 
            value = self._get_interval_from_string(value, variable)
        else:
            value = self._convert(value, variable.upper())
        return value
    
    #==========================================================================
    def get_type_area_list(self): 
        """
        Created     20180323    by Magnus Wenzer
        Updated     20180323    by Magnus Wenzer
        """
        return self.df['TYPE_AREA_NUMBER'] + self.df['TYPE_AREA_SUFFIX'].astype(str)
    
    
    #==========================================================================
    def get_value(self, variable=None, type_area=None): 
        print(type_area)
        print(self.df.columns)        
        num, suf = get_type_area_parts(type_area)

        if suf:
            value_series = self.df.loc[(self.df['TYPE_AREA_NUMBER']==num) & (self.df['TYPE_AREA_SUFFIX']==suf), variable]
        else:
            value_series = self.df.loc[self.df['TYPE_AREA_NUMBER']==num, variable]
        
#        print('----')
#        print(value_series, type(value_series))
#        print(value_series.values, type(value_series.values))
        
#        assert len(value) == 1, 'More than one setting for given filter_dict\n{}'.format(value)
        
        # If len(value) > 1 we need to return data from two rows 
        return_value = []
        for value in value_series.values:  
#            print(value)   
#            print(value)
#            print(variable)
            
            if variable in self.list_columns: 
                value = self._get_list_from_string(value, variable)
#                print('=', value, type(value[0]))
            elif variable in self.interval_columns: 
                value = self._get_interval_from_string(value, variable)
#                print('=', value, type(value[0]))
    #            esf
            else:
                value = self._convert(value, variable.upper())
            return_value.append(value)
        return return_value
    
    #==========================================================================
    def set_value(self, type_area=None, variable=None, value=None): 
        """
        Updated     20180323   by Magnus Wenzer
        """
        if not all([type_area, variable, value]):
            return False
        
        new_value = []
        for val in value:
            if variable in self.list_columns: 
                print('List column')
                val = self._get_string_from_list(val, variable)
            elif variable in self.interval_columns: 
                print('Interval column')
                val = self._get_string_from_interval(val, variable) 
            elif variable in self.tolerance_columns: 
                print('Tolerance column')
                val = str(val)
            
            if val == False: 
                print('Value could not be changed!')
                return False
            new_value.append(val)
        else:
            print('Value to set for type_area "{}" and variable "{}": {}'.format(type_area, variable, new_value))
#            print('type_area', type_area)
            num, suf = get_type_area_parts(type_area)
            if suf:
                self.df.loc[(self.df['TYPE_AREA_NUMBER']==num) & (self.df['TYPE_AREA_SUFFIX']==suf), variable] = new_value 
            else:
                self.df.loc[self.df['TYPE_AREA_NUMBER']==num, variable] = new_value
            return True
        
    #==========================================================================
    def set_values(self, value_dict, allowed_variables): 
        """
        Sets values for several type_areas and variables. 
        Values to be set are given in dict like: 
            value_dict[type_area][variable] = value 
        """
#        print('#'*40)
#        print(value_dict)
        all_ok = True
        for type_area in value_dict.keys():
            for variable in value_dict[type_area].keys(): 
                if variable not in allowed_variables:
                    print('Not allowed to change variable "{}". Allowed variables to change are:\n{}\n'.format(variable, '\n'.join(allowed_variables)))
                    continue
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
    def get_filter_boolean_for_df(self, df=None, water_body = None, type_area=None, level=None): 
        """
        Updated     20180326    by Lena Viktorsson
        
        Get boolean tuple to use for filtering
        """
        #TODO: add filter on type_area, as for now it only adds a key to boolean_dict for each type_area but the boolean under that key is the same as on step 2
        combined_boolean = ()
        if water_body:
            type_area = self.mapping_water_body.get_type_area_for_water_body(water_body, include_suffix=True)
            combined_boolean = df['VISS_EU_CD'] == water_body
        else:
            combined_boolean = ()
            
       
        if type_area == None:
            # you can not create a settingsfilter without specifying type_area
            combined_boolean = ()
        else:
            for variable in self.filter_columns: 
                if variable in self.interval_columns:
                    boolean = self._get_boolean_from_interval(df=df,
                                                              type_area=type_area,
                                                              variable=variable, 
                                                              level=level)
                    self.temp_boolean_interval = boolean
                elif variable in self.list_columns:
                    boolean = self._get_boolean_from_list(df=df,
                                                          type_area=type_area,
                                                          variable=variable, 
                                                          level=level)
                    self.temp_boolean_list = boolean
                else:
                    print('No boolean for "{}"'.format(variable))
                    continue
                
                if not type(boolean) == pd.Series:
                    continue            
                if type(combined_boolean) == pd.Series:
                    combined_boolean = combined_boolean & boolean
                else:
                    combined_boolean = boolean 
                
        if len(combined_boolean) == 0: 
            combined_boolean = pd.Series(np.ones(len(df), dtype=bool)) 
            
        return combined_boolean
    
    #==========================================================================
    def _get_boolean_from_interval(self, df=None, type_area=None, variable=None, level=None): 
        """
        Updated     20180322    by Magnus Wenzer
        """
        
        result = self.get_value(type_area=type_area, 
                                variable=variable)
        
        # Must check if there are several results. For example BQI has two depth intervalls.  
        print('RESULT', result)
        if not len(result):
            return False
        elif len(result) == 1:
            from_value, to_value = result[0]
        else:
            if level == None:
                return None
            from_value, to_value = result[level]
            
            
        parameter = variable.split('_')[0]
#        print(df[parameter])
#        print(type(df[parameter][0]))
#        print('variable', parameter)
#        print('from_value', from_value, type(from_value))

        # TODO: Remove astype(float) when this is changed in data handler
#        print('='*50)
#        print('parameter', parameter)
#        print(type(df[parameter].values[0]), df[parameter]) 
        return (df[parameter] >= from_value) & (df[parameter] <= to_value)
#        return (df[parameter].astype(float) >= from_value) & (df[parameter].apply(float) <= to_value)
#        return (df[parameter].apply(lambda x: float(x) if x else np.nan) >= from_value) & \
#                (df[parameter].apply(lambda x: float(x) if x else np.nan) <= to_value) # No depth for Chl. Can't float. 

    #==========================================================================
    def _get_boolean_from_list(self, df=None, type_area=None, variable=None, level=None): 
        """
        Updated     20180322    by Magnus Wenzer
        """
        result = self.get_value(type_area=type_area, 
                                    variable=variable)
        
        # Must check if there are several results. For example BQI has two depth intervalls.  
        if not len(result):
            return False
        elif len(result) == 1:
            value_list = result[0]
        else:
            if level == None:
                return None
            value_list = result[level]
        
        parameter = variable.split('_')[0] 

        return df[parameter].isin(value_list)
    
        
        

###############################################################################
class SettingsBase(object): 
    
    #==========================================================================
    def set_values(self, value_dict): 
        """
        Sets values for several type_areas and variables. 
        Values to be set are given in dict like: 
            value_dict[type_area][variable] = value 
        """
        self.settings.set_values(value_dict, self.allowed_variables) 
        self.settings.save_file()
        
    #==========================================================================
    def get_value(self, type_area=None, variable=None): 
        """
        Created     20180321    by Magnus Wenzer
        Updated     20180321    by Magnus Wenzer
        """
  
        return self.settings.get_value(variable=variable, type_area=type_area) 
    
    #==========================================================================
    def get_type_area_list(self): 
        """
        Created     20180323    by Magnus Wenzer
        Updated     20180323    by Magnus Wenzer
        """
        return self.settings.get_type_area_list()
    
###############################################################################
class SettingsRef(SettingsBase):
    """
    Handles ref settings. 
    """
    #==========================================================================
    def __init__(self, settings_file_object): 
        super().__init__()
        self.settings = settings_file_object 
        self.settings.connected_to_ref_settings_object = True
        self.allowed_variables = self.settings.ref_columns
        
    #==========================================================================    
    def get_ref_value(self, type_area):
        """
        Created     20180326    by Lena Viktorsson
        Updated     20180326    by Lena Viktorsson
        """
        try: 
            self.settings.df[self.settings.ref_columns]['EKV Ref']
            self.get_value(variable = 'EKV Ref', type_area = type_area)
        except KeyError:
            pass
            
        
###############################################################################
class SettingsDataFilter(SettingsBase):
    """
    Handles filter settings. 
    """
    #==========================================================================
    def __init__(self, settings_file_object): 
        super().__init__()
        self.settings = settings_file_object 
        self.settings.connected_to_filter_settings_object = True 
        self.allowed_variables = self.settings.filter_columns
        
    #==========================================================================
    def get_filter_boolean_for_df(self, df=None, water_body=None, type_area=None, level=None, **kwargs): 
        """
        Get boolean pd.Series to use for filtering. 
        Name of this has to be the same as the one in class DataFilter. 
        """
        print('Water body', water_body)
#        get_type_area_for_water_body(wb, include_suffix=False)
        return self.settings.get_filter_boolean_for_df(df=df, 
                                                       water_body=water_body, 
                                                       type_area=type_area, 
                                                       level=level)


###############################################################################
class SettingsTolerance(SettingsBase):
    """
    Handles tolerance settings. 
    """
    #==========================================================================
    def __init__(self, settings_file_object): 
        super().__init__()
        self.settings = settings_file_object 
        self.settings.connected_to_tolerance_settings_object = True
        self.allowed_variables = self.settings.tolerance_columns

  
       
###############################################################################
class WaterBodyStationFilter(object): 
    """
    Class to hold filters linked to water body. 
    Files in settings/water_body can specify which stations should be included 
    or excluded in the water body. 
    All cuminication is directly with the files, no data is stored in instance. 
    Is water_body_mapping_object going to hold link between STATN and Water Body? 
    """
    def __init__(self, water_body_settings_directory=None, 
                       mapping_objects=None):
        water_body_settings_directory = water_body_settings_directory.replace('\\', '/')
        if not water_body_settings_directory.endswith('/water_body'):
            print('Invalid directory given to WaterBodyFilter. Must end with "/water_body"')
            self.directory = None 
            self.mapping_objects = None
            self.mapping_water_body = None
        else:
            self.directory = water_body_settings_directory
            self.mapping_objects = mapping_objects
            self.mapping_water_body = mapping_objects['water_body']
            
        self.water_body_parameter = 'WATER_BODY_NAME'
        
    #==========================================================================
    def clear_filter(self): 
        for name in os.listdir(self.directory): 
            if not name.startswith('wb_'):
                continue
            file_path = '{}/{}'.format(self.directory, name)
            os.remove(file_path)
        
    #==========================================================================
    def get_list(self, include=True, water_body=None): 
        
        key, file_path = self._get_file_path(wb=water_body, include=include)
        filter_object = DataFilterFile(file_path=file_path, string_in_file='wb_') 
        return filter_object.get_filter()
        
    #==========================================================================
    def get_filter_boolean_for_df(self, df=None, water_body=None): 
        """
        Get boolean tuple to use for filtering on "area". 
        Boolean is true for matching water_body excluding the stations in the wb exclude list. 
        Stations in the wb include list are also True
        """ 
        # Check include and exclude list
        include_stations = self.get_list(include=True, water_body=water_body)
        exclude_stations = self.get_list(include=False, water_body=water_body)
        print(include_stations)
        print(exclude_stations)
        # self.water_body_parameter is set above. Could be name or number...
        boolean = ((df[self.water_body_parameter] == water_body) | \
                  (df['STATN'].isin(include_stations))) & \
                  (~df['STATN'].isin(exclude_stations ))
        print(set(df['STATN'][boolean]))
        return boolean
        
        
    #==========================================================================
    def include_stations_in_water_body(self, station_list=None, water_body=None): 
        """
        Adds information on which stations to include in the given water_body. 
        """ 
        key, file_path = self._get_file_path(wb=water_body, include=True)
        filter_object = DataFilterFile(file_path=file_path, string_in_file='wb_') 
        filter_object.set_filter(station_list)
        
    #==========================================================================
    def exclude_stations_in_water_body(self, station_list=None, water_body=None): 
        """
        Adds information on which stations to excludeclude in the given water_body. 
        This is probably nopt used. Instead this can be filterd in step_1 data filter. 
        """ 
        key, file_path = self._get_file_path(wb=water_body, include=False)
        filter_object = DataFilterFile(file_path=file_path, string_in_file='wb_') 
        filter_object.set_filter(station_list)
    
    #==========================================================================
    def _get_file_path(self, wb=None, include=True): 
        # TODO: Here it might be sutible with something that converts wb name to wb number
        wb = wb.replace('.', '#').replace(' ', '_')
        if include:
            include = 'include'
        else:
            include = 'exclude'
        key = 'wb_{}_{}'.format(include, wb)
        file_path = '{}/{}.fil'.format(self.directory, key) 
        return key, file_path
        
        
    #==========================================================================
    def _get_file_path_list(self): 
        if not self.directory:
            return False
        
        all_file_names = os.listdir(self.directory)
        file_path_list = []
        for name in all_file_names:
            file_path_list.append('{}/{}'.format(self.directory, name)) 
            
        return file_path_list
    
    #==========================================================================
    def change_path(self, directory):
#        if not os.path.exists(directory): 
#            print('Invalid directory: {}\nOld file_path is {}'.format(directory, self.directory))
#            return False
        self.directory = directory
        return True
            
        
###############################################################################
def get_type_area_parts(type_area): 
    """
    Returns a tuple like (type_area_number, type_area_suffix)
    """
#    print(type_area)
    type_area = str(type_area)
    if type_area[-1].isalpha():
        suf = type_area[-1] 
    else:
        suf = ''
    print('type_area_type_area', type_area)
    return re.findall('\d+', type_area)[0], suf
        
###############################################################################
if __name__ == '__main__':
    nr_marks = 60
    print('='*nr_marks)
    print('Running module "filters.py"')
    print('-'*nr_marks)
    print('')   
    
    root_directory = os.path.dirname(os.path.abspath(__file__))[:-5]
    print('root directory is "{}"'.format(root_directory))
    
    
    if 0: 
        root_directory = os.getcwd()
        workspace_directory = root_directory + '/workspaces' 
        resource_directory = root_directory + '/resources'
        
        
        
        default_workspace = core.WorkSpace(name='default', 
                                           parent_directory=workspace_directory, 
                                           resource_directory=resource_directory) 
        
        workspace = core.WorkSpace(name='jj', 
                                   parent_directory=workspace_directory, 
                                   resource_directory=resource_directory) 
        
        workspace.add_files_from_workspace(default_workspace, overwrite=True)
        
        workspace.load_all_data()

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
    
        
        sf = SettingsDataFilter(s)
    
    
    
    
    
    if 0:
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
    
    
    
    
    
    
    
    
    
    
        