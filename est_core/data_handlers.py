# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:49:03 2017

@author: a001985
"""

import pandas as pd

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
    
    #==========================================================================
    def add_df(self, pd_df, data_type):
        """
        Adds data to the internal data structure. 
        """
        # TODO: check 
        if 'col' in data_type:
            self.column_data = self.column_data.append(pd_df)
        elif 'row' in data_type:
            self.row_data = self.row_data.append(pd_df)
#        print(self.data_phys_chem.head()) 

    #==========================================================================
    def filter_data(self, data_filter_object):
        """
        Filters data according to data_filter_object. 
        data_filter_object is a est_core.filters.DataFilter-object. 
        Returns a DataHandler object with the filtered data. 
        """
        new_data_handler = DataHandler(self.source + '_filtered')
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
        return df
        
    #==========================================================================
    def _filter_column_data_on_depth_interval(self, df, data_filter_object): 
        if 'DEPTH_INTERVAL' not in data_filter_object.keys():
            return
        min_depth, max_depth = map(float, data_filter_object['DEPTH_INTERVAL'])
        df = df.loc[df.index[(df['DEPH'] >= min_depth) & (df['DEPH'] <= max_depth)], :] 
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
    
    
    
    