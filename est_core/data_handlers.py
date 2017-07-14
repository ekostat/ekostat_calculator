# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:49:03 2017

@author: a001985
"""

import pandas as pd
import numpy as np

###############################################################################
class DataHandler(object): 
    """
    Class to hold data.  
    """
    def __init__(self, source):
        self.source = source
        self.column_data = pd.DataFrame()
        self.row_data = pd.DataFrame()  
    
    #==========================================================================
    def add_txt_file(self, file_path, data_type): 
        data = pd.read_csv(file_path, sep='\t', encoding='cp1252')
        self.add_df(data, data_type)
        # TODO: Check if all is ok
    
    #==========================================================================
    def add_df(self, pd_df, data_type):
        """
        Adds data to the internal data structure. 
        """
        # Add columns (time etc.)
        self._add_columns(pd_df)
        
        if 'col' in data_type:
            self.column_data = self.column_data.append(pd_df)
        elif 'row' in data_type:
            self.row_data = self.row_data.append(pd_df)
#        print(self.data_phys_chem.head()) 

    #==========================================================================
    def _add_columns(self, df): 
        df['TIME'] = pd.Series(pd.to_datetime(df['SDATE'] + df['STIME'], format='%Y-%m-%d%H:%M'))
        
    #==========================================================================
    def filter_data(self, data_filter_object, filter_id=''):
        """
        Filters data according to data_filter_object. 
        data_filter_object is a est_core.filters.DataFilter-object. 
        Returns a DataHandler object with the filtered data. 
        """
        new_data_handler = DataHandler(self.source + '_filtered_%s' % filter_id)
        if len(self.column_data):
            df = self._filter_column_data(self.column_data, data_filter_object)
            new_data_handler.add_df(df, 'column')
        if len(self.row_data):
            df = self._filter_row_data(self.row_data, data_filter_object)
            new_data_handler.add_df(df, 'row')
        
        return new_data_handler
    
    #==========================================================================
    def _filter_column_data(self, df, data_filter_object): 
        """
        Filters column file data and retuns resulting dataframe
        """
        df = self._filter_column_data_on_depth_interval(df, data_filter_object)
        df = self._filter_column_data_on_month(df, data_filter_object)
        df = self._filter_column_data_on_year(df, data_filter_object)
        return df
    
        
        
    #==========================================================================
    def _filter_column_data_on_depth_interval(self, df, data_filter_object): 
        """
        Keeps data from the depth interval in the list [from, to] under data_filter_object['DEPTH_INTERVAL']
        """
        if 'DEPTH_INTERVAL' not in data_filter_object.keys() or not data_filter_object['DEPTH_INTERVAL']:
            return df
        min_depth, max_depth = map(float, data_filter_object['DEPTH_INTERVAL'])
        df = df.loc[df.index[(df['DEPH'] >= min_depth) & (df['DEPH'] <= max_depth)], :] 
        return df
    
    #==========================================================================
    def _filter_column_data_on_month(self, df, data_filter_object): 
        """
        Keeps data from all months in the list under data_filter_object['MONTH']
        """
        if 'MONTH' not in data_filter_object.keys() or not data_filter_object['MONTH']:
            return df
#        print('_filter_column_data_on_months')
        month_list = map(float, data_filter_object['MONTH'])
        df = df.loc[df.index[df['MONTH'].isin(month_list)], :] 
        return df
    
    #==========================================================================
    def _filter_column_data_on_year(self, df, data_filter_object): 
        """
        Keeps data from all months in the list under data_filter_object['MYEAR']
        """
        if 'MYEAR' not in data_filter_object.keys() or not data_filter_object['MYEAR']:
            return df
#        print('_filter_column_data_on_year')
        month_list = map(float, data_filter_object['MYEAR'])
        df = df.loc[df.index[df['MYEAR'].isin(month_list)], :] 
        return df
        
    #==========================================================================
    def _filter_column_data_on_type_area(self, data_filter_object, df):
        new_df = df
        
        return new_df
        
    
    #==========================================================================
    def _filter_row_data(self, data_filter_object):
        pass
    
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
    def get_station_list(self):
        """
        Returns a list of all stations that has data of the current parameter (self.internal_name). 
        """
        if not self.internal_name or not self.data:
            return False
        
        # TODO: Does this work for row data as well?
        return sorted(set(self.data.loc[self.data.index[~self.data[self.internal_name].isnull()], 'STATN']))
    
    