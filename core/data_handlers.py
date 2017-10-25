# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:49:03 2017

@author: a001985
"""

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))[:-5]
sys.path.append(current_path)

import pandas as pd
import numpy as np
import time

import utils
import core

"""#========================================================================"""
class DataFrameHandler(object):
    """
    Holds functions to handle DataFrame operations
    """
    def __init__(self):
        super().__init__()

    #==========================================================================
    def _check_nr_of_parameters(self, params_to_use):
        """
        If one_parameter: We only need to set filter to keep parameter. No need 
        to use pivot_table..
        """
        if len(params_to_use) == 1:
            self.one_parameter=True
        else:
            self.one_parameter=False
            
    #==========================================================================
    def convert_format(self, df, key_list, as_type=np.unicode):
        """
        """
        for key in key_list:
            if key and key in df:
                try:
                    df[key] = df[key].astype(as_type)
                except:
                    print(u'Could not convert format for:', key, u'in DataFrame')
        return df

    #==========================================================================
    def delete_columns_from_df(self, df, columns=[]):
        """
        """
        return df.drop(columns, axis=1, errors='ignore') # inplace=True ?
         
    #==========================================================================
    def get_dict(self, df, drop_nans=True):
        """
        """
        if drop_nans:
            # Index does not matter for the returned dictionary
            return { key : list(df.get(key).dropna(axis=0)) for key in df }
        else:
            return { key : list(df.get(key)) for key in df }
    
    #==========================================================================
    def get_index_fields(self, fp=None, data_keys=[], extra_field=[]):
        """ 
        fp: filter_parameters 
        """
        exclude_params = fp[u'fields_index'] + \
                           fp[u'fields_value'] + \
                             fp[u'fields_qflag']
                             
        return list(p for p in fp[u'compulsory_fields'] \
                    if p not in exclude_params and p in data_keys) + \
                    fp[u'fields_index'] + extra_field
    
    #==========================================================================
    def _map_parameter_list(self, params_in_df, params_to_use, map_object):
        p_map = map_object.get_parameter_mapping(params_in_df)
        return p_map, list(p for p in p_map if p_map[p] in params_to_use)            
            
    #==========================================================================
    def merge_df_string_columns(self, df, col_to_merge, sep=None):
        """
        """
        return df.get(col_to_merge[0]).astype(str).str.cat([df.get(key).astype(str) \
                      for key in col_to_merge[1:] if key in df], sep=sep)

    #==========================================================================
    def _one_parameter_df_adjustments(self, df, fp):
        """ 
        fp: filter_parameters 
        """
        map_dict = {fp['fields_value'][0]: fp['use_parameters'][0], 
                    fp['fields_qflag'][0]: 'Q_'+fp['use_parameters'][0]}
        
        df = self.delete_columns_from_df(df, columns=fp['fields_parameter'])
        df = self.rename_columns_of_DataFrame(df, map_dict)
        return df
    
    #==========================================================================
    def read_filter_file(self, fid, get_as_dict=False):
        data = pd.read_csv(fid, sep='\t',  encoding='cp1252')       
        if get_as_dict:
            data = self.get_dict(data)
        return data
    
    #==========================================================================
    def rename_columns_of_DataFrame(self, df, mapping_dict):
        """
        """
        return df.rename(index=str, columns=mapping_dict)

    #==========================================================================
    def select_columns_from_df(self, df, columns=[]):
        """
        """
        return self.delete_columns_from_df(df, columns=list(x for x in \
                                               df.keys() if x not in columns))
    
    #==========================================================================
    def select_parameters(self, df, parameter_head, params_to_use, map_object):
        """
        """
        self._check_nr_of_parameters(params_to_use)
        p_map, p_list = self._map_parameter_list(df.get(parameter_head).unique(), 
                                                 params_to_use, 
                                                 map_object)
        
        self.para_list = map_object.map_parameter_list(p_list)
        
        for para in p_list:
            df[parameter_head] = np.where(df[parameter_head]==para, 
                                          p_map[para], 
                                          df[parameter_head])
        #TODO Use Filter object instead ?...
#        indices = np.where( df[parameter_head] == params_to_use[:,None] )[0]
        indices = np.where( df[parameter_head].isin(self.para_list) )[0]
        return df.iloc[indices,:]
    
    #==========================================================================
    def seperate_para_value_from_qflag(self, df, params, sep=''):
        """
        """
        for para in params: 
            if np.any(df[para]):
                length = len(df[para][df.index[df[para].notnull()][0]].split(sep))
                break
            
        if not 'length' in locals():
            raise UserWarning('No data in file?')
            
        for para in params:
            df[para] = df[para].apply(lambda x: x.split(sep) if x else ['']*length)
            df[[para,'Q_'+para]] = pd.DataFrame(df.get(para).values.tolist())
    
        return df

    #==========================================================================
    def set_column_table_from_pivot_table(self, df_pivot, fp, sort=True):
        """
        fp: filter_parameters
        """
        df_col = df_pivot.unstack()
        df_col = df_col.reset_index()
        if sort:
            return self.sort_dict_by_keys(df_col, 
                                          sort_order=fp['sort_by_fields'],
                                          ascending_list=[True]*len(fp['sort_by_fields']), 
                                          depth_head=fp['depth_key'][0],
                                          serno_head=fp['visit_id_key'][0])
        else:
            return df_col
            
    #==========================================================================
    def set_pivot_table(self, df, values, index):
        """
        """
        return pd.pivot_table(df, values=values, index=index, aggfunc='first')
        
    #==========================================================================
    def sort_dict_by_keys(self, 
                          df, 
                          sort_order=[], 
                          ascending_list=[], 
                          depth_head=None,
                          serno_head=None):
        """
        sort_order:     key list in sorting order
                        ['key_1','key_2','key_3']
                        
        ascending_list: ascending sorting or not (key specific)
                        [True,False,True]
                        
        return_as_dataframe: return as pandas Dataframe
        """
        print(u'Sorting..')
        if any([depth_head, serno_head]):
            df = self.convert_format(df, [depth_head, serno_head], as_type=np.float)
            
        df = df.sort_values(sort_order, ascending=ascending_list)
        
        if any([depth_head, serno_head]):
            df = self.convert_format(df, [depth_head, serno_head], as_type=np.unicode)
        
        return df.reset_index().drop([u'index'], axis=1)
    
    #==========================================================================
    def stack_columns(self, df, columns):
        """
        """
        return np.dstack([df.get(key) for key in columns])
    
    #==========================================================================
    def stack_columns_to_tuple(self, df, columns):
        """
        """
        return list(zip(df.get(key) for key in columns))

    #==========================================================================
    


###############################################################################
class DataHandler(DataFrameHandler): 
    """
    Class to hold data.  
    """
    def __init__(self, source):
        
        super().__init__()
        self.source = source
        self.column_data = pd.DataFrame()
        self.row_data = pd.DataFrame()  
    
    #==========================================================================
#    def add_txt_file(self, file_path, data_type): 
    def add_txt_file(self, file_path, data_type, map_object=None): 

        data = pd.read_csv(file_path, sep='\t', encoding='cp1252')
        if not map_object == None:
            map_dict = map_object.get_parameter_mapping( data.columns.values )
            data = self.rename_columns_of_DataFrame( data, map_dict )

        self.add_df(data, data_type)
        # TODO: Check if all is ok


    #==========================================================================
    def add_df(self, pd_df, data_type, add_columns=False):
        """
        Adds data to the internal data structure. 
        """
        # Add columns (time etc.)
        if add_columns:
            self._add_columns(pd_df)
        
        if 'col' in data_type:
            self.column_data = self.column_data.append(pd_df)
        elif 'row' in data_type:
            self.row_data = self.row_data.append(pd_df).fillna('')
#        print(self.data_phys_chem.head()) 

    #==========================================================================
    def _add_columns(self, df): 
        df['time'] = pd.Series(pd.to_datetime(df['SDATE'] + df['STIME'], format='%Y-%m-%d%H:%M'))
        
        df['latit_dec_deg'] = df['LATIT'].apply(utils.decmin_to_decdeg)
        df['longi_dec_deg'] = df['LONGI'].apply(utils.decmin_to_decdeg)
        
        df['profile_key'] = df['time'].apply(str) + \
                            ' ' + \
                            df['LATIT'].apply(str) + \
                            ' ' + \
                            df['LONGI'].apply(str)
        
    #==========================================================================
    def filter_data(self, data_filter_object, filter_id=''):
        """
        Filters data according to data_filter_object. 
        data_filter_object is a core.filters.DataFilter-object. 
        Returns a DataHandler object with the filtered data. 
        """
        new_data_handler = DataHandler(self.source + '_filtered_%s' % filter_id)
        if len(self.column_data):
#            print( 'data_filter_object', data_filter_object)
            df = self._filter_column_data(self.column_data, data_filter_object)
            if data_filter_object.parameter:
#                print('df', df.columns)
#                print('data_filter_object.parameter:', data_filter_object.parameter)
                for col in list(df.columns):
                    if col not in core.ParameterList().metadata_list + [data_filter_object.parameter]:
                        df = df.drop(col, 1)
            new_data_handler.add_df(df, 'column')
        if len(self.row_data):
            df = self._filter_row_data(self.row_data, data_filter_object)
            new_data_handler.add_df(df, 'row')
        
        return new_data_handler
    
    #==========================================================================
    def _filter_column_data(self, df, data_filter_object): 
        """
        Filters column file data and returns resulting dataframe
        """
        boolean = data_filter_object.get_boolean(df)
        
        if not len(boolean):
            return df
        return df.loc[df.index[boolean], :]
        
#        df = self._filter_column_data_on_depth_interval(df, data_filter_object)
#        df = self._filter_column_data_on_month(df, data_filter_object)
#        df = self._filter_column_data_on_year(df, data_filter_object)
#        return df
    
        
        
#    #==========================================================================
#    def _filter_column_data_on_depth_interval(self, df, data_filter_object): 
#        """
#        Keeps data from the depth interval in the list [from, to] under data_filter_object['DEPTH_INTERVAL']
#        """
#        
#        if 'DEPTH_INTERVAL' not in data_filter_object.keys() or not data_filter_object['DEPTH_INTERVAL']:
#            return df
#        min_depth, max_depth = map(float, data_filter_object['DEPTH_INTERVAL'])
#        df = df.loc[(df['DEPH'] >= min_depth) & (df['DEPH'] <= max_depth), :]
##        df = df.loc[df.index[(df['DEPH'] >= min_depth) & (df['DEPH'] <= max_depth)], :]
#        return df
#    
#    #==========================================================================
#    def _filter_column_data_on_month(self, df, data_filter_object): 
#        """
#        Keeps data from all months in the list under data_filter_object['MONTH']
#        """
#        if 'MONTH' not in data_filter_object.keys() or not data_filter_object['MONTH']:
#            return df
##        print('_filter_column_data_on_months')
#        month_list = map(float, data_filter_object['MONTH'])
##        df = df.loc[df.index[df['MONTH'].isin(month_list)], :] 
#        df = df.loc[df['MONTH'].isin(month_list), :] 
#        return df
#    
#    #==========================================================================
#    def _filter_column_data_on_year(self, df, data_filter_object): 
#        """
#        Keeps data from all months in the list under data_filter_object['MYEAR']
#        """
#        if 'MYEAR' not in data_filter_object.keys() or not data_filter_object['MYEAR']:
#            return df
##        print('_filter_column_data_on_year')
#        year_list = map(float, data_filter_object['MYEAR'])
#        df = df.loc[df['MYEAR'].isin(year_list), :] 
##        df = df.loc[df.index[df['MYEAR'].isin(month_list)], :] 
#        return df
#        
#    #==========================================================================
#    def _filter_column_data_on_type_area(self, data_filter_object, df):
#        new_df = df
#        
#        return new_df
        
    
    def _filter_row_data(self, data_filter_object=None, fp=None, map_object=None):
        """
        fp: filter_parameters
        """
        self.row_data = self.select_columns_from_df(self.row_data, 
                                                    columns=fp['compulsory_fields']) # use only default fields
        
        self.row_data = self.select_parameters(self.row_data,
                                               fp['fields_parameter'][0],
                                               fp['use_parameters'],
                                               map_object)
        if self.one_parameter:
            self.row_data = self._one_parameter_df_adjustments(self.row_data, fp)            
        else:
            self.row_data['TEMP_VALUE'] = self.merge_df_string_columns(self.row_data, 
                                                                       fp['fields_value'] + fp['fields_qflag'], 
                                                                       sep='__')
            index_fields = self.get_index_fields(fp=fp, 
                                                 data_keys=self.row_data.keys())
            
            self.row_data = self.set_pivot_table(self.row_data, 
                                                 'TEMP_VALUE', 
                                                 index_fields)

    #==========================================================================
    def get_column_data_format(self, df_pivot, fp):
        """
        fp: filter_parameters
        """
        if not self.one_parameter:

            df_col = self.set_column_table_from_pivot_table(df_pivot, 
                                                            fp, 
                                                            sort=True)
            
            df_col = self.seperate_para_value_from_qflag(df_col, 
                                                         self.para_list, 
                                                         sep='__')
            self.add_df(df_col, 'col', add_columns=False)
        else:
            self.add_df(df_pivot, 'col', add_columns=False)
    
    #==========================================================================
    def load_data(self, directory):
        try:
            column_file_path = directory + '/column_data.txt'
            self.column_data = pd.read_csv(column_file_path, sep='\t', encoding='cp1252')
        except:
            pass
        
        try:
            row_file_path = directory + '/row_data.txt'
            self.row_data = pd.read_csv(row_file_path, sep='\t', encoding='cp1252')
        except:
            pass

    #==========================================================================
    def save_data(self, directory):
        column_file_path = directory + '/column_data.txt'
        self.column_data.to_csv(column_file_path, sep='\t', encoding='cp1252', index=False)
        
        row_file_path = directory + '/row_data.txt'
        self.row_data.to_csv(row_file_path, sep='\t', encoding='cp1252', index=False)
    
    #==========================================================================
    def get_profile_key_list(self, year=None):
        """
        Returns a list och unique combinations of pos and time. 
        """
        if year:
            return sorted(set(self.column_data.loc[self.column_data['MYEAR'] == year, 'profile_key'])) 
        else:
            return sorted(set(self.column_data['profile_key']))
    
    #==========================================================================
    def get_index_for_profile_key(self, profile_key):
        """
        Method to get index for a unique profile key. 
        profile_key is "time LATIT LONGI"
        """
        return self.column_data.index[self.column_data['profile_key'] == profile_key]
    
###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "data_handler.py"')
    print('-'*50)
    print('')
    
    raw_data_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/raw_data/data_BAS_2000-2009.txt'
    first_filter_directory = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filtered_data' 
    
    # Handler
    raw_data = core.DataHandler('raw')
    raw_data.add_txt_file(raw_data_file_path, data_type='column') 
    
    print('-'*50)
    print('done')
    print('-'*50)
    
    
    
    
    
    
    
    
    
    
    
    
    
    