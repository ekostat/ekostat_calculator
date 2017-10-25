# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 17:32:56 2017

@author: a002028
"""

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
import datetime
import core

import pandas as pd 
import numpy as np
import time


# Directories 
export_directory = u'D:\\Utveckling\\GitHub\\ekostat_calculator\\test_data\\test_exports\\'
filter_parameters_directory = 'D:/Utveckling/GitHub/ekostat_calculator/test_data/filters/' 
first_filter_directory = 'D:/Utveckling/GitHub/ekostat_calculator/test_data/filtered_data' 
raw_data_file_path = 'D:/Utveckling/GitHub/ekostat_calculator/test_data/raw_data/'
mapping_directory = 'D:/Utveckling/GitHub/ekostat_calculator/test_data/mappings/mapping_parameter_dynamic_extended.txt' 

#filter_parameters_file = u'filter_fields_zoobenthos.txt'
filter_parameters_file = u'filter_fields_physical_chemical.txt'

# Row data
#fid = u'zoobenthos_2016_row_format_2.txt'
fid = u'BOS_HAL_2015-2016_row_format_2.txt'

# Parameter mapping
parameter_mapping = core.ParameterMapping()
parameter_mapping.load_mapping_settings(file_path=mapping_directory)

filter_parameters = core.data_handlers.DataFrameHandler().read_filter_file(filter_parameters_directory + filter_parameters_file, get_as_dict=True)

# Handler
raw_data = core.DataHandler('raw')
raw_data.add_txt_file(raw_data_file_path + fid, data_type='row', map_object=parameter_mapping)

# Row data handling
raw_data._filter_row_data(fp=filter_parameters, map_object=parameter_mapping)
raw_data.get_column_data_format(raw_data.row_data, filter_parameters)
raw_data.save_data(export_directory)



"""
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
"""
#wd = u'D:/Utveckling/GitHub/ekostat_calculator/test_data/johannes/'
#fid = u'BOS_HAL_2015-2016_row_format.txt'
##fid = u'zoobenthos_2016_row_format.txt'
#
#fid_filter_para = u'filter_fields_physical_chemical.txt'
##fid_filter_para = u'filter_fields_zoobenthos.txt'
##fid = u'test_data_format_converter.txt'
#para_mapping = u'mapping_parameter_dynamic_extended.txt'

##==============================================================================
#class AttributeDict(object):
#    """    
#    
#    #mapping_file = pd.read_csv(wd+para_mapping, encoding="cp1252", sep='\t')# .fillna('')
#    #g = AttributeDict(**mapping_file)
#    #g['myear']
#    #h = g.keys()
#    """
#    def __init__(self, **entries):
#        self._add_entries(**entries)
#        
#    #==========================================================================
#    def _add_entries(self, **entries):
#        """
#        Turns elements in arrays into attributes with a corresponding official 
#        field name 
#        """
#        for key, array in entries.items():
#            setattr(self, key, key) # better? why?.. 
##            self.__dict__[key] = key # overriding __setattr__.. not good?
#            for value in array.values:
#                if not pd.isnull(value):
#                    setattr(self, value, key)
##                    self.__dict__[value] = key
#                    
#    #==========================================================================
#    def keys(self):
#        return list(self.__dict__.keys())
#        
#    #==========================================================================
#    def get(self, key):
#        return getattr(self, key.lower())
#
#    #==========================================================================
#    def get_list(self, key_list):
#        return list(self.get(key.lower()) for key in key_list)
#
#    #==========================================================================
#    def get_mapping_dict(self, key_list):
#        return dict(list((key, self.get(key.lower())) for key in key_list))
#        
#    #==========================================================================
#    def __getitem__(self, key):
#        return getattr(self, key)
#        
##==============================================================================
#
##==============================================================================
#class ParameterMapping():
#    """
#    #p_map = ParameterMapping()
#    #p_map.load_mapping_settings(file_path=wd+para_mapping)
#    #p_map.map_parameter_list(['myear', u'ammonium nh4-n'])
#    #p_map.get_parameter_mapping(['myear', u'ammonium nh4-n'])
#    """
#    def __init__(self):
#        pass
#        
#    #==========================================================================
#    def load_mapping_settings(self, file_path=u'',sep='\t',encoding='cp1252'):
#        """ Reading csv/txt files """
#        self.mapping_file = pd.read_csv(file_path, sep=sep, encoding=encoding)
#        self._set_mapping_structure()
#        
#    #==========================================================================
#    def _set_mapping_structure(self):    
#        self.dict = AttributeDict(**self.mapping_file)
#        
#    #==========================================================================
#    def map_parameter_list(self, para_list, ext_list=False):
#        return self.dict.get_list(para_list)
#
#    #==========================================================================
#    def get_parameter_mapping(self, para_list, ext_list=False):
#        return self.dict.get_mapping_dict(para_list)
#       
##==============================================================================
#
##=========================================================================
#def convert_format(df, key_list, as_type=np.unicode):
##    print(df.keys())
##    print(key_list)
#    for key in key_list:
##        print(key)
#        
#        if key and key in df:
#            try:
#                df[key] = df[key].astype(as_type)
#            except:
#                print(u'Could not convert format for:', key, u'in DataFrame')
#    return df
#
##=========================================================================
#def sort_dict_by_keys(df, 
#                      sort_order=[], 
#                      ascending_list=[], 
#                      depth_head=None,
#                      serno_head=None):
#    """
#    sort_order:     key list in sorting order
#                    ['key_1','key_2','key_3']
#                    
#    ascending_list: ascending sorting or not (keys specific)
#                    [True,False,True]
#                    
#    return_as_dataframe: return as pandas Dataframe
#    #---------------------------------------------------------------------
#    Example:
#            d =  {'a':[8,7,7,9],'b':['f','b','a','v'],'c':[1,4,2,3]}
#            d = sort_dict_by_keys(data_dict=d, 
#                                  sort_order=['a','b'], 
#                                  ascending_list=[True,True], 
#                                  return_as_dataframe=False)
#    """
#    print(u'Sorting..')
#    if any([depth_head, serno_head]):
#        df = convert_format(df, [depth_head, serno_head], as_type=np.float)
#        
#    df = df.sort_values(sort_order, ascending=ascending_list)
#    
#    if any([depth_head, serno_head]):
#        df = convert_format(df, [depth_head, serno_head], as_type=np.unicode)
#    
#    return df.reset_index().drop([u'index'], axis=1)
#
##==============================================================================
#def get_dict(df, drop_nans=True):
#    """
#    """
#    if drop_nans:
#        # Index does not matter for the returned dictionary
#        return { key : list(df.get(key).dropna(axis=0)) for key in df }
#    else:
#        return { key : list(df.get(key)) for key in df }
#
##==============================================================================
#def delete_columns_from_df(df, columns=[]):
#    return df.drop(columns, axis=1, errors='ignore') # inplace=True ?
#     
#
##==============================================================================
#def select_columns_from_df(df, columns=[]):
#    return delete_columns_from_df(df, columns=list(x for x in df.keys() if x not in columns))
#    
##==============================================================================
#def select_parameters(df, parameter_head, params_to_use):
#    print(params_to_use)
#    params_to_use = np.array(params_to_use)
#    # Gets you all indices where df[parameter_head] equals values from list
#    # params_to_use
#    indices = np.where( df[parameter_head] == params_to_use[:,None] )[0]
##    indices = np.where( df[parameter_head].isin(params_to_use))[0]
#    print(indices)
#    return df.iloc[indices,:]
#    
##==============================================================================
#def rename_columns_of_DataFrame(df, mapping_dict):
#    return df.rename(index=str, columns=mapping_dict)
#
##==============================================================================
#def get_index_fields(fp=None, data_keys=[], extra_field=[]):
#    """ fp: filter_parameters """
#    exclude_params = fp[u'fields_index']+fp[u'fields_value']+fp[u'fields_qflag']
#    return list(p for p in fp[u'compulsory_fields'] if p not in exclude_params and p in data_keys) + fp[u'fields_index'] + extra_field
#
##    return_params = fp[u'fields_index'] + [p for p in fp[u'compulsory_fields'] if p not in exclude_params and p in data_keys]
#
##==============================================================================
#def merge_df_string_columns(df, col_to_merge, sep=None):
#    return df.get(col_to_merge[0]).astype(str).str.cat([df.get(key).astype(str) \
#                  for key in col_to_merge[1:] if key in df], sep=sep)#.astype(np.unicode))
#    
##==============================================================================
#def stack_columns(df, columns):
#    return np.dstack([df.get(key) for key in columns])
#
##==============================================================================
#def stack_columns_to_tuple(df, columns):
#    return list(zip(df.get(key) for key in columns))
#
##==============================================================================
#def seperate_para_value_from_qflag(df, params, sep=''):
#    """
#    df = pd.DataFrame({'a':['sth*st','sth*sthsh','cvb*gfht', None]})
#    df['a'].loc[pd.isnull(df['a'])] = '*'
#    df["a"], df["row_name"] = zip(*df["a"].str.split('*').tolist())
#    """
#    for para in params:
#        print(para)
#        if np.any(df_pivot_col[para]):
#            length = len(df[para][df.index[df[para].notnull()][0]].split(sep))
#            break
#        
#    if not 'length' in locals():
#        raise UserWarning('No data in file?')
#        
#    for para in params:
#        #Faster
##        df['QFLAG_'+para] = df[para].apply(lambda x: x.split(sep)[1] if x else None)
##        df[para] = df[para].apply(lambda x: x.split(sep)[0] if x else None)
#
##        print(para)
##        print(para in df)
##        df[para] = df[para].apply(lambda x: x.split(sep) if x else ['',''])#['']*length)
#        df[para] = df[para].apply(lambda x: x.split(sep) if x else ['']*length)
#        df[[para,'QFLAG_'+para]] = pd.DataFrame(df.get(para).values.tolist())
#
#        #Slower
##        df[para].loc[pd.isnull(df[para])] = sep
##        df[para], df['QFLAG_'+para] = zip(*df[para].str.split(sep).tolist())
#
#    return df
#
##==============================================================================
#def get_parameter_field(df, parameter_fields):
#    if u'TEMP_PARAMETER_FIELD' in df:
#        return df.get(u'TEMP_PARAMETER_FIELD').unique()
#    else:
#        return data.get(parameter_fields[0]).unique()
#
##==============================================================================  



#start_time = time.time()

#filter_parameters = pd.read_csv(wd+fid_filter_para, 
#                                sep='\t', 
#                                encoding='cp1252')
#
#
#
#filter_parameters = get_dict(filter_parameters)
#
#p_map = ParameterMapping()
#p_map.load_mapping_settings(file_path=wd+para_mapping)
#
#data = pd.read_csv(wd+fid,
#                   sep='\t',
#                   encoding='cp1252',
#                   dtype=np.unicode).fillna('')
#
#mapping_dict = p_map.get_parameter_mapping( data.columns.values )
#data = rename_columns_of_DataFrame( data, mapping_dict )
#
#"""#=============================================================================="""
#data = delete_columns_from_df(data, 
#                              columns=filter_parameters['delete_fields']) # use only default fields
#
#data = select_columns_from_df(data,
#                              columns=filter_parameters['compulsory_fields']) # use only default fields
#
##data = select_parameters(data,
##                         filter_parameters['fields_parameter'],
##                         filter_parameters['use_parameters'])
#                              
#data['TEMP_VALUE'] = merge_df_string_columns(data, 
#                                             filter_parameters['fields_value'] + filter_parameters['fields_qflag'], 
#                                             sep='__')
#
#index_fields = get_index_fields(fp=filter_parameters, 
#                                data_keys=data.keys())#, 
##                                extra_field=extra_field)
##
##print(data.keys())
#
#df_pivot_row = pd.pivot_table(data,
#                              values='TEMP_VALUE',
#                              index=index_fields,
#                              aggfunc='first')
#
##print(df_pivot_row.keys())
#df_pivot_col = df_pivot_row.unstack()
#df_pivot_col = df_pivot_col.reset_index()
#df_pivot_col = sort_dict_by_keys(df_pivot_col, 
#                                 sort_order=filter_parameters['sort_by_fields'],
#                                 ascending_list=[True]*len(filter_parameters['sort_by_fields']), 
#                                 depth_head=filter_parameters['depth_key'][0],
#                                 serno_head=filter_parameters['visit_id_key'][0])
#
## Change column names after parameters have been moved from row value under PARAM to column names
## We do this with parameter mapping class
#start_time = time.time()
#
##unique_parameters = get_parameter_field(df_pivot_col, filter_parameters['fields_parameter'])
#unique_parameters = data.get('PARAM').unique()
#
##print(df_pivot_col.keys())
#
#
#df_pivot_col = seperate_para_value_from_qflag(df_pivot_col, 
#                                              unique_parameters,  
#                                              sep='__')
##print(df_pivot_col.get('H2S_SMELL'))
#print("--%.5f sec" % (time.time() - start_time))
#start_time = time.time()
#
#df_pivot_col.to_csv(wd+'out_test_fyskem.txt', 
#                    sep='\t', 
#                    encoding='cp1252', 
#                    index=False)

"""
#==============================================================================

TODO

#==============================================================================
"""


# TESTSING ####################################################################
"""
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
"""



"""
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
"""  

    