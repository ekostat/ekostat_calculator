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
    Data filter is built up with several files listed in the given directory. 
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
        
        self.int_filters = ['MYEAR']
        
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
#        print('¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤')
#        print('\n'*5)
#        print(parameter)
#        print(value_list)
#        print('\n'*5)
        return df[parameter].astype(str).isin(value_list)
    
    
        
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
                print(par)
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
    def reset_filter(self, include_filters=[], exclude_filters=[]): 
        """
        Created 20180608    by Magnus Wenzer 
        Updated 
        
        Resets the data filter in include_filters and exclude_filters. 
        If arguments=True all filters in group are reset. 
        """
        if include_filters == True:
#            print('include_list_filter', self.include_list_filter)
            include_filters = self.include_list_filter.keys()
            
        if exclude_filters == True:
            exclude_filters = self.exclude_list_filter.keys()
            
        for f in include_filters:
            self.set_include_list_filter(filter_name=f, 
                                         filter_list=[], 
                                         save_files=True, 
                                         append_items=False)
            
            
        for f in exclude_filters:
            self.set_exclude_list_filter(filter_name=f, 
                                         filter_list=[], 
                                         save_files=True, 
                                         append_items=False)
        
        
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
    
        # Convert
#        data = self._convert(filter_name=filter_name, data=data)

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
        
    
#    #==========================================================================
#    def _convert(self, filter_name=None, data=None): 
#        """
#        Created     20180611    by Magnus Wenzer
#        Updated     
#        """
#        
##        print('¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤')
##        print('\n'*10)
##        print(filter_name)
##        print(data)
##        print('\n'*10)
#        
#        if filter_name in self.int_filters:
#            data = map(int, data)
#            
#        return data
        
        
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
#        print('***')
#        print(self.include_list_filter[filter_name])
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
    Created                by Magnus Wenzer
    Updated     20180612   by Magnus Wenzer
        
    Holds Settings file information. Reading and writing file. Basic file handling. 
    
    Updates: 
        20180605 MW: Added level columns
    """
    #==========================================================================
    def __init__(self, file_path, mapping_objects=None):
        self.file_path = file_path 
        self.indicator = os.path.basename(file_path)[:-4]
        
        self.mapping_objects = mapping_objects
        self.mapping_water_body = mapping_objects['water_body']
        self.homogeneous_parameters_dict = mapping_objects['indicator_settings_homogeneous_parameters']
        self.match_columns_list = mapping_objects['indicator_settings_matching_columns']
        
        self.int_columns = [] 
        self.float_columns = [] 
        self.str_columns = [] 
        
        self.interval_columns = []
        self.list_columns = [] 
        
        self.EQR_columns = []
        self.refvalue_column = []
        
        self.filter_columns = [] 
        self.ref_columns = [] 
        self.tolerance_columns = []
        self.level_columns = []
        
        self.connected_to_filter_settings_object = False
        self.connected_to_ref_settings_object = False
        self.connected_to_tolerance_settings_object = False
        
        self._prefix_list = ['FILTER', 'REF', 'TOLERANCE', 'LEVEL'] 
        self._suffix_list = ['INT', 'EQ', 'FLOAT']
        
        self._load_file()    
    
    
    #==========================================================================
    def _load_file(self):
        """
        Created:        xxxxxxxx     by Magnus
        Last modified:  20180605     by Magnus
        """
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
            elif prefix == 'LEVEL': 
                self.level_columns.append(variable)
            
            #------------------------------------------------------------------
            # Suffix
            if suffix == 'STR': 
                self.str_columns.append(variable)
            elif suffix == 'INT': 
                self.int_columns.append(variable) 
            elif suffix == 'FLOAT': 
                self.float_columns.append(variable)
            
            #------------------------------------------------------------------
            # Contains
            if 'INTERVAL' in variable:
                self.interval_columns.append(variable) 
                
            if 'LIST' in variable:
                self.list_columns.append(variable)
                
            if 'EQR' in variable:
                self.EQR_columns.append(variable)
                
            if 'REF_VALUE' in variable:
                self.refvalue_column.append(variable)
                #check length
                if len(self.refvalue_column) != 1:
                    raise ValueError('Trying to add more than one column for reference value from settings file')
            
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
        """
        Created:        20180612     by Magnus
        Last modified:  
        """
        
        self._remove_viss_eu_cd_matching_type_area()
        
        if not file_path:
            file_path = self.file_path
        # Rename columns 
        print(len(self.df.columns))
        print(self.df.columns)
        print(len(self.columns_in_file))
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
    def get_viss_eu_cd_list(self): 
        """
        Created     20180611    by Magnus Wenzer
        Updated     
        """
        return sorted([item for item in self.df['VISS_EU_CD'] if item != 'unspecified'])
    
    
    #==========================================================================
    def get_value(self, variable=None, type_area=None, water_body=None, return_series=True): 
        """
        Created:        xxxxxxxx     by Magnus
        Last modified:  20180615     by Magnus
        returns value from settings file by given arguments
        if variable and water_body is given returns single value
        if variable and type_area is given returns single value when there is only one setting for the given type_area, else return pandas series for given variable (MW: If return_series==True (default) else return "result")
        if no variable i given return pandas dataframe with all columns in object for the lines corresponding to given water_body or type_area
        Do not give both type_area and water_body , if both type_area and water_body is given type_area is replaces by type_area from mapping_water_body to be sure they are consistent
        """ 
        
        if water_body:
            try:
                type_area = self.mapping_water_body.get_type_area_for_water_body(water_body, include_suffix=True)
            except AttributeError as e:
                print(e)
                print('waterbody matching file does not recognise water body with VISS_EU_CD {}'.format(water_body))
                return False
        num, suf = get_type_area_parts(type_area)
        
        var = variable 
        self.var = var
        if variable is None:
            var = self.df.columns
        if variable not in self.df.columns:
            var = self.df.columns
        
        if water_body:
            value_series = self.df.loc[(self.df['VISS_EU_CD']==water_body), var]
#            print(water_body)
#            print(self.df['VISS_EU_CD'].unique())
#            print('. . . . .')
#            print(value_series)
#            print(len(value_series))
#            print('. . . . .')
            if not len(value_series):
                if suf and suf in self.df.loc[(self.df['TYPE_AREA_NUMBER']==num), 'TYPE_AREA_SUFFIX'].values:
                    value_series = self.df.loc[(self.df['TYPE_AREA_NUMBER']==num) & \
                                               (self.df['TYPE_AREA_SUFFIX']==suf) & \
                                               (self.df['VISS_EU_CD'] == 'unspecified'), var]
                else:
                    value_series = self.df.loc[(self.df['TYPE_AREA_NUMBER']==num) & \
                                               (self.df['VISS_EU_CD'] == 'unspecified'), var]
        else:
            # 20180615 MW: added (self.df['VISS_EU_CD'] == 'unspecified')
            if suf:
                value_series = self.df.loc[(self.df['TYPE_AREA_NUMBER']==num) & \
                                           (self.df['TYPE_AREA_SUFFIX']==suf) & \
                                           (self.df['VISS_EU_CD'] == 'unspecified'), var]
            else:
                value_series = self.df.loc[(self.df['TYPE_AREA_NUMBER']==num) & \
                                           (self.df['VISS_EU_CD'] == 'unspecified'), var]
        self.suf = suf
        self.num = num
#        print('----')
#        print('water_body {}, type_area {}, variable {}'.format(water_body, type_area, variable))
#        print('num {}, suf {}, suf? {}'.format(num, suf, self.df.loc[self.df['TYPE_AREA_NUMBER']==num, 'TYPE_AREA_SUFFIX'].values))
#        print(value_series, type(value_series))
#        print(value_series.values, type(value_series.values))
        
        # if no variable is given, return dataframe
        if variable is None:
            return value_series
        # if no variable not in columns, return dataframe
        if variable not in self.df.columns:
            return value_series
        # Try to return single value, list or interval
        return_value = [] 
        self.value_series = value_series
        for value in value_series.values:              
            if variable in self.list_columns: 
                value = self._get_list_from_string(value, variable)
            elif variable in self.interval_columns: 
                value = self._get_interval_from_string(value, variable)
            elif variable in self.refvalue_column:
                print('value {} in refvalue_column'.format(value))
                if variable.isnumeric():
                    value = float(value)
                else:
                    value = value
            else:
                value = self._convert(value, variable.upper())
            return_value.append(value)
            # TODO: return dataframe?
        # if only one row for given type_area or water_body, return as single value, else return as pandas series
        print('return_value', return_value)
        if len(return_value) == 1:
            return return_value[0]
        elif len(return_value) > 1 and all(x == return_value[0] for x in return_value):
            return return_value[0]
        elif not return_value:
            return False
        else:
            if return_series:
                return value_series
            else:
                return return_value


    #==========================================================================
    def has_depth_interval(self): 
        """
        Created     20180606   by Magnus Wenzer
        """
        if 'DEPH_INTERVAL' in self.df.columns:
            return True
        else:
            return False
    
    
    #==========================================================================
    def set_value(self, type_area=None, variable=None, value=None, viss_eu_cd=None): 
        """
        Updated     20180621   by Magnus Wenzer
        
        20180612: MW added viss_eu_cd
        20180621: MW added the posibility to add new viss_eu_cd 
        
        value can be int/float/str och list. 
        If list len(value) must be equal to the number of rows for the "match" 
        on type_area or viss_eu_cd. 
        
        """
        if not all([variable, value]):
            return False
        if not any([type_area, viss_eu_cd]):
            return False
        
        if type(value) != list:
            value = [value]
        
        new_value = []
        for val in value:
            if variable in self.list_columns: 
                print('List column', val)
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
        
        if type_area:
            print('Value to set for type_area "{}" and variable "{}": {}'.format(type_area, variable, new_value))
            num, suf = get_type_area_parts(type_area)
            if suf:
                self.df.loc[(self.df['TYPE_AREA_NUMBER']==num) & (self.df['TYPE_AREA_SUFFIX']==suf), variable] = new_value 
            else:
                self.df.loc[self.df['TYPE_AREA_NUMBER']==num, variable] = new_value
            
        elif viss_eu_cd: 
            if viss_eu_cd not in self.df['VISS_EU_CD'].values:
                self._add_new_rows_for_viss_eu_cd(viss_eu_cd=viss_eu_cd)
            print('Value to set for water body (viss_eu_cd) "{}" and variable "{}": {}'.format(viss_eu_cd, variable, new_value))
            self.df.loc[self.df['VISS_EU_CD']==viss_eu_cd, variable] = new_value
        
        return True
        
    
    #==========================================================================
    def old_set_value(self, type_area=None, variable=None, value=None, viss_eu_cd=None): 
        """
        Updated     20180620   by Magnus Wenzer
        
        20180612: MW added viss_eu_cd
        20180620: MW added the posibility to add new viss_eu_cd
        """
        if not all([variable, value]):
            return False
        if not any([type_area, viss_eu_cd]):
            return False
        
        if type(value) != list:
            value = [value]
            
        if type(value[0]) != list:
            value = [value]
        
        new_value = []
        for val in value:
            if variable in self.list_columns: 
                print('List column', val)
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
        
        if type_area:
            print('Value to set for type_area "{}" and variable "{}": {}'.format(type_area, variable, new_value))
            num, suf = get_type_area_parts(type_area)
            if suf:
                self.df.loc[(self.df['TYPE_AREA_NUMBER']==num) & (self.df['TYPE_AREA_SUFFIX']==suf), variable] = new_value 
            else:
                self.df.loc[self.df['TYPE_AREA_NUMBER']==num, variable] = new_value
            
        elif viss_eu_cd: 
            if viss_eu_cd not in self.df['VISS_EU_CD'].values:
                self._add_new_rows_for_viss_eu_cd(viss_eu_cd=viss_eu_cd)
            print('Value to set for water body (viss_eu_cd) "{}" and variable "{}": {}'.format(viss_eu_cd, variable, new_value))
            self.df.loc[self.df['VISS_EU_CD']==viss_eu_cd, variable] = new_value
        
        return True
    
        
        
    #==========================================================================
    def _add_new_rows_for_viss_eu_cd(self, viss_eu_cd, nr_rows=1): 
        """
        Created     20180612   by Magnus Wenzer
        Updated     20180613   by Magnus Wenzer
        
        Method to add new rows to the settings file. 
        The type area row corresponding to the viss_eu_cd is copied. 
        """
        # Find the corresponding type_area 
        type_area = self.mapping_water_body.get_type_area_for_water_body(viss_eu_cd, include_suffix=True)
        water_body_name = self.mapping_water_body.get_display_name(water_body=viss_eu_cd)
        if not type_area:
            return False
        
        # Find line for type_area 
        series = get_matching_rows_in_indicator_settings(type_area=type_area, df=self.df)
        
#        series = self.df.loc[((self.df['TYPE_AREA_NUMBER'].astype(str) + \
#                               self.df['TYPE_AREA_SUFFIX'])==type_area) & \
#                                (self.df['VISS_EU_CD']=='unspecified')].copy()
        
        
        # Change VISS_EU_CD and name in series
        series['VISS_EU_CD'] = viss_eu_cd
        series['WATERBODY_NAME'] = water_body_name
        
        
        # Add new line(s) with copy of type_area
        self.df = self.df.append(series)
        
        self.df.reset_index(inplace=True, drop=True)
        
        return True
        
    
    #==========================================================================
    def _remove_viss_eu_cd_matching_type_area(self): 
        """
        Created     20180612   by Magnus Wenzer
        Updated     20180615   by Magnus Wenzer
        
        Removes all lines for a viss_eu_cd if data in te corresponding type_area is the same. 
        
        """
        
        for viss_eu_cd in set(self.df['VISS_EU_CD']):
            if viss_eu_cd =='unspecified':
                continue 
            type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(viss_eu_cd, include_suffix=True).replace('-', '')
            type_area_series = get_matching_rows_in_indicator_settings(type_area=type_area, df=self.df)
            
            viss_eu_cd_boolean = self.df['VISS_EU_CD']==viss_eu_cd
            viss_eu_cd_series = self.df.loc[viss_eu_cd_boolean, :] 
            
            # Compare. If all values are the same remove viss_eu_cd lines 
            equal_list = []
            for col in self.match_columns_list:
                if col not in viss_eu_cd_series.columns:
                    continue
                if list(viss_eu_cd_series[col].values) == list(type_area_series[col].values): 
#                    print('='*50)
#                    print(viss_eu_cd_series[col].values)
#                    print()
#                    print(type_area_series[col].values)
#                    print('-'*50)
                    equal_list.append(True)
                else:
                    equal_list.append(False)
            
            if all(equal_list):
                self.df = self.df.drop(np.where(viss_eu_cd_boolean)[0])
                self.df.reset_index(inplace=True, drop=True) 
                
            
        
        
        
    #==========================================================================
    def set_values(self, value_dict, allowed_variables): 
        """
        Updated     20180615   by Magnus Wenzer
        
        Sets values for several type_areas and variables. 
        Values to be set are given in dict like: 
            value_dict[area][variable] = value 
            area could be type_area or water_body (viss_eu_cd)
        """
        print('set_values')
        print(allowed_variables)
        all_ok = True
        for area in value_dict.keys():
            print('AREA:', area, type(area))
            for variable in value_dict[area].keys(): 
                if variable not in allowed_variables:
#                    print('Not allowed to change variable "{}". Allowed variables to change are:\n{}\n'.format(variable, '\n'.join(allowed_variables)))
                    continue
                value_list = value_dict[area][variable] 
                
                # Three cases when data i set
                if area in (self.df['TYPE_AREA_NUMBER'].astype(str) + self.df['TYPE_AREA_SUFFIX']).values:
                    print('1')
                    # Area is type_area which should always be present in settings file 
                    if not self.set_value(type_area=area, variable=variable, value=value_list, viss_eu_cd=None):
                        all_ok = False
                elif area in self.df['VISS_EU_CD'].values:
                    print('2')
                    # Area is VISS_EU_CD and present in settings file
                    if not self.set_value(type_area=None, variable=variable, value=value_list, viss_eu_cd=area):
                        all_ok = False
                else:
                    print('3333333333')
                    # Area is new VISS_EU_CD NOT present in settings file
                    self._add_new_rows_for_viss_eu_cd(viss_eu_cd=area)
                    if not self.set_value(type_area=None, variable=variable, value=value_list, viss_eu_cd=area):
                        all_ok = False
        return all_ok
    
    
#        all_ok = True
#        for type_area in value_dict.keys():
#            for variable in value_dict[type_area].keys(): 
#                if variable not in allowed_variables:
##                    print('Not allowed to change variable "{}". Allowed variables to change are:\n{}\n'.format(variable, '\n'.join(allowed_variables)))
#                    continue
#                value = value_dict[type_area][variable]
#                if not self.set_value(type_area, variable, value):
#                    all_ok = False
#        return all_ok
    
    
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
        if variable in self.float_columns:
            return float(value)
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
    def get_filter_boolean_for_df(self, df=None, water_body = None): 
        """
        Updated     20180326    by Lena Viktorsson
        
        Get boolean tuple to use for filtering
        """
        combined_boolean = ()
        if water_body:
            combined_boolean = df['VISS_EU_CD'] == water_body
        else:
            raise InputError('In SettingsFile get_filter_boolean_for_df','Must provide water_body for settings filter')
            
       
        for variable in self.filter_columns: 
            if variable in self.interval_columns:
                boolean = self._get_boolean_from_interval(df=df,
                                                          water_body = water_body,
                                                          variable=variable)
                self.temp_boolean_interval = boolean
            elif variable in self.list_columns:
                boolean = self._get_boolean_from_list(df=df,
                                                      water_body = water_body,
                                                      variable=variable)
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
            combined_boolean = combined_boolean
        if len(combined_boolean) == 0: 
            combined_boolean = pd.Series(np.ones(len(df), dtype=bool)) 
            
        return combined_boolean
    #==========================================================================
    def old_get_filter_boolean_for_df(self, df=None, water_body = None, type_area=None, level=None): 
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
    def _get_boolean_from_interval(self, df=None, type_area=None, water_body = None, variable=None): 
        """
        Updated     20180322    by Magnus Wenzer
        """
        
        result = self.get_value(type_area=type_area, water_body = water_body,
                                    variable=variable)

        #print('RESULT', result)
        # Must check if there are several results. For example BQI has two depth intervalls.  
        if type(result) is list or result is False:
            if not result:
                return False
            from_value, to_value = result
        else:
            raise InputError('in filters.py _get_boolean_from_interval()', 'Returned multiple values from get_value, do not know which one do use')

        parameter = variable.split('_')[0]
        
        return (df[parameter] >= from_value) & (df[parameter] <= to_value)
    #==========================================================================
    def old_get_boolean_from_interval(self, df=None, type_area=None, variable=None, level=None): 
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
    def old_get_boolean_from_list(self, df=None, type_area=None, variable=None, level=None): 
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
        
    #==========================================================================
    def _get_boolean_from_list(self, df=None, type_area=None, water_body = None, variable=None): 
        """
        Updated     20180322    by Magnus Wenzer
        """
        
        result = self.get_value(type_area=type_area, water_body = water_body,
                                    variable=variable)
        
        # Must check if there are several results. For example BQI has two depth intervalls.  
        
        print('RESULT', result)
#        print(len(result))
        
        
        if type(result) is list or result is False:
            if not result:
                return False
            value_list = result
        else:
            raise InputError('in filters.py _get_boolean_from_interval()', 'Returned multiple values from get_value, do not know which one do use')

#            if not type_area:
#                    type_area = self.mapping_water_body.get_type_area_for_water_body(water_body, include_suffix=True)
#            num, suf = get_type_area_parts(type_area)
#            if suf:
#                value_string = result.loc[(result['VISS_EU_CD'] == 'unspecified') & (self.df['TYPE_AREA_NUMBER']==num) & (self.df['TYPE_AREA_SUFFIX']==suf), variable].values[0]
#                #value_series = self.df.loc[(self.df['TYPE_AREA_NUMBER']==num) & (self.df['TYPE_AREA_SUFFIX']==suf), variable]
#            else:
#                value_string = result.loc[(result['VISS_EU_CD'] == 'unspecified') & (self.df['TYPE_AREA_NUMBER']==num), variable].values[0]
#                #value_series = self.df.loc[self.df['TYPE_AREA_NUMBER']==num, variable]
#            value_list = self._get_list_from_string(value_string)    
        
        parameter = variable.split('_')[0] 

        return df[parameter].isin(value_list)
    
        
        

###############################################################################
class SettingsBase(object): 
    
    #==========================================================================
    def set_value(self, type_area=None, variable=None, value=None, viss_eu_cd=None): 
        """
        Created     20180620    by Magnus Wenzer
        """
        
        self.settings.set_value(type_area=type_area, variable=variable, value=value, viss_eu_cd=viss_eu_cd)
        self.settings.save_file()
        
        
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
    def get_value(self, type_area=None, variable=None, water_body=None, return_series=True): 
        """
        Created     20180321    by Magnus Wenzer
        Updated     20180606    by Magnus (Added return_series option)
        """
  
        return self.settings.get_value(variable=variable, type_area=type_area, water_body=water_body, return_series=return_series) 
    
    
    #==========================================================================
    def get_type_area_list(self): 
        """
        Created     20180323    by Magnus Wenzer
        Updated     20180323    by Magnus Wenzer
        """
        return self.settings.get_type_area_list()
    
    
    #==========================================================================
    def get_viss_eu_cd_list(self): 
        """
        Created     20180615    by Magnus Wenzer
        Updated     
        """
        return self.settings.get_viss_eu_cd_list()
    
    
    #==========================================================================
    def has_depth_interval(self):
        return self.settings.has_depth_interval()
        
    
    
###############################################################################
class SettingsRef(SettingsBase):
    """
    Handles ref settings. 
    """
    #==========================================================================
    def __init__(self, settings_file_object): 
        """
        Updated     20180615    by Magnus Wenzer
    
        """
        super().__init__()
        self.filter_type = 'reference'
        self.settings = settings_file_object 
        self.settings.connected_to_ref_settings_object = True
        self.allowed_variables = self.settings.ref_columns
    
     
    #==========================================================================    
    def get_ref_value(self, type_area = None, water_body = None, salinity = None):
        """
        Created     20180326    by Lena Viktorsson
        Updated     20180418    by Lena Viktorsson
        """

        if len(self.settings.refvalue_column) == 0:
            return False
        if water_body:
            ref_value = self.get_value(variable = self.settings.refvalue_column[0], water_body = water_body)
        else:
            ref_value = self.get_value(variable = self.settings.refvalue_column[0], type_area = type_area)
        
        if type(ref_value) is float:
            ref_value = ref_value
        elif type(ref_value) is str:
            try: 
                s = salinity
                ref_value = eval(ref_value) 
            except TypeError as e:
                raise TypeError('{}\nSalinity TypeError, salinity must be int, float or nan but is {}'.format(e, repr(s)))
                #TODO: add closes matching salinity somewhere here
        elif not ref_value:
            return False
        elif type(ref_value) is pd.Series:
            raise InputError('In SettingsRef get_ref_value','returned pd.Series for ref_value, give more specific info to get the right row')
        else:
            raise TypeError('Unknown Type of reference value, must be either equation as string or float. Given reference value {} is {}. Or salinity missing, given salinity value is {}'.format(ref_value, type(ref_value), salinity))
        
        return ref_value
    
    
    #==========================================================================    
    def get_ref_value_type(self, type_area = None, water_body = None):
        """
        Created     20180403    by Lena Viktorsson
        Updated     20180418    by Lena Viktorsson     
        """
        if len(self.settings.refvalue_column) == 0:
            return False
        
        if water_body:
            ref_value = self.get_value(variable = self.settings.refvalue_column[0], water_body = water_body)
        else:
            ref_value = self.get_value(variable = self.settings.refvalue_column[0], type_area = type_area)
        
        if type(ref_value) is float:
            return 'float'
        elif type(ref_value) is str:
            return 'str'
        elif not ref_value:
            return False
        else:
            raise TypeError('unknown referencevalue type {}: {}'.format(type(ref_value),ref_value))
        
        
###############################################################################
class SettingsDataFilter(SettingsBase):
    """
    Handles filter settings. 
    """
    #==========================================================================
    def __init__(self, settings_file_object): 
        """
        Updated     20180615    by Magnus Wenzer
    
        """
        super().__init__() 
        self.filter_type = 'data'
        self.settings = settings_file_object 
        self.settings.connected_to_filter_settings_object = True 
        self.allowed_variables = self.settings.filter_columns + self.settings.level_columns
        
    #==========================================================================
    def get_filter_boolean_for_df(self, df=None, water_body=None, **kwargs): 
        """
        Get boolean pd.Series to use for filtering. 
        Name of this has to be the same as the one in class DataFilter. 
        """
        print('Water body', water_body)
#        get_type_area_for_water_body(wb, include_suffix=False)
        return self.settings.get_filter_boolean_for_df(df=df, 
                                                       water_body=water_body)


###############################################################################
class SettingsTolerance(SettingsBase):
    """
    Handles tolerance settings. 
    """
    #==========================================================================
    def __init__(self, settings_file_object): 
        """
        Updated     20180615    by Magnus Wenzer
    
        """
        super().__init__()
        self.filter_type = 'tolerance'
        self.settings = settings_file_object 
        self.settings.connected_to_tolerance_settings_object = True
        self.allowed_variables = self.settings.tolerance_columns
        
    def get_min_nr_years(self, type_area = None, water_body = None):
        
        get_variable = 'MIN_NR_YEARS'
        if get_variable in self.allowed_variables:
            return self.get_value(variable = get_variable, type_area = type_area, water_body = water_body)
        else:
            raise NameError('MIN_NR_YEARS not in tolerance settings')
    
    
    def get_min_nr_values(self, type_area = None, water_body = None):
        
        get_variable = 'MIN_NR_VALUES'
        if get_variable in self.allowed_variables:
            return self.get_value(variable = get_variable, type_area = type_area, water_body = water_body)
        else:
            raise NameError('MIN_NR_VALUES not in tolerance settings')

###############################################################################
class WaterBodyFilter(object): 
    """
    Class to get boolean for given water body in given df
    water_body is given as VISS_EU_CD string
    and df is the pandas dataframe for which to return the boolean 
    """
        
    def get_filter_boolean_for_df(self, df = None, water_body = None, **kwargs):
       """
       get boolean for given water_body, must be given as a VISS_EU_CD string
       """
       
       boolean = df['VISS_EU_CD'] == water_body
            
       return boolean                    
                                 
###############################################################################
class WaterBodyStationFilter(object): 
    """
    Class to hold filters linked to water body. 
    Files in settings/water_body can specify which stations should be included 
    or excluded in the water body. 
    All communication is directly with the files, no data is stored in instance. 
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
            
        self.water_body_parameter = 'VISS_EU_CD'
        
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

class InputError(Exception):

    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message            
        
        
###############################################################################
def get_type_area_parts(type_area): 
    """
    Returns a tuple like (type_area_number, type_area_suffix)
    """
    type_area = str(type_area)
    if type_area[-1].isalpha():
        suf = type_area[-1] 
    else:
        suf = ''
    
    return re.findall('\d+', type_area)[0], suf
        

###############################################################################
def get_matching_rows_in_indicator_settings(type_area=None, df=None): 
    """
    Created     20180612   by Magnus Wenzer
    Updated     
        
    """
    s = df.loc[((df['TYPE_AREA_NUMBER'].astype(str) + df['TYPE_AREA_SUFFIX'])==type_area) & (df['VISS_EU_CD']=='unspecified')].copy(deep=True)
    if not len(s):
        type_area = re.findall('\d+', type_area)[0]
        s = df.loc[((df['TYPE_AREA_NUMBER'].astype(str) + df['TYPE_AREA_SUFFIX'])==type_area) & (df['VISS_EU_CD']=='unspecified')].copy(deep=True)
    return s
    

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
    
    
    
    
    
    
    
    
    
    
        