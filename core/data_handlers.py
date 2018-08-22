# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 08:10:06 2017

@author: a002028
"""

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
if current_path not in sys.path:
    sys.path.append(current_path)

import pandas as pd
import numpy as np
import time
import pickle

import utils
import core

import core.exceptions as exceptions
"""
#==============================================================================
#==============================================================================
"""
class ColumnDataHandler(object):
    """
    """
    def __init__(self):
        super().__init__()
"""
#==============================================================================
#==============================================================================
"""
class RowDataHandler(object):
    """
    """
    def __init__(self):
        super().__init__()

    #==========================================================================
    def _get_index_fields(self, data_keys=[], extra_field=[]):
        """ 
        fp: filter_parameters 
        """
        exclude_params = list(self.filter_parameters.fields_index) + \
                             [self.filter_parameters.value_key] + \
                             [self.filter_parameters.qflag_key]
                             
        return list(p for p in self.filter_parameters.compulsory_fields \
                    if p not in exclude_params and p in data_keys) + \
                    self.filter_parameters.fields_index + extra_field
                    
    #==========================================================================
    def _merge_df_string_columns(self, col_to_merge, new_key=u'new_key', sep=u'__'):
        """
        """
        self.df[new_key] = self.df.get(col_to_merge[0]).astype(str).str.cat([ \
               self.df.get(key).astype(str) for key in col_to_merge[1:] if key in self.df], sep=sep)
            
    #==========================================================================
    def _one_parameter_df_adjustments(self):
        """ 
        fp: filter_parameters 
        """
        map_dict = {self.filter_parameters.value_key: self.filter_parameters.use_parameters, 
                    self.filter_parameters.qflag_key: 'Q_'+self.filter_parameters.use_parameters}

        # Deleting column that only contains parameter name
        self._delete_columns_from_df(columns=self.filter_parameters.parameter_key)
        
        # Changing column "VALUE" to parameter name and column "QFLAG" to Q_"parameter_name"
        self._rename_columns_of_DataFrame(map_dict)
        
    #==========================================================================
    def _seperate_para_value_from_qflag(self, sep=''):
        """
        """
        # Simply get the length of one seperated string 
        for para in self.para_list: 
            if np.any(self.df[para]):
                length = len(self.df[para][self.df.index[self.df[para].notnull()][0]].split(sep))
                break
            
        if not 'length' in locals():
            raise UserWarning('No data in file?')
            
        for para in self.para_list:
            self.df[para] = self.df[para].apply(lambda x: x.split(sep) if x else ['']*length)
            self.df[[para,'Q_'+para]] = pd.DataFrame(self.df.get(para).values.tolist())

    #==========================================================================
    def _set_column_table_from_pivot_table(self, sort=True):
        """
        fp: filter_parameters
        """
        df_col = self.df.unstack() # necessary to create a new local dataframe here
        df_col = df_col.reset_index()
        self.df = df_col
        if sort:
            self.sort_dict_by_keys(sort_order=self.filter_parameters.sort_by_fields,
                                   ascending_list=[True]*len(self.filter_parameters.sort_by_fields), 
                                   depth_head=self.filter_parameters.depth_key,
                                   serno_head=self.filter_parameters.visit_id_key)

    #==========================================================================
    def _set_pivot_table(self, values, index):
        """
        """
        self.df = pd.pivot_table(self.df, values=values, index=index, aggfunc='first')
    
    #==========================================================================
    def filter_row_data(self, data_filter_object=None, map_object=None):
        """
        """
        if self.one_parameter:
            self._one_parameter_df_adjustments()
        else:
            self._merge_df_string_columns([self.filter_parameters.value_key, self.filter_parameters.qflag_key], 
                                          new_key=u'TEMP_VALUE',
                                          sep='__')
            index_fields = self._get_index_fields(data_keys=self.df.keys())
            print(len(index_fields), index_fields)
            self._set_pivot_table(u'TEMP_VALUE', index_fields)

    #==========================================================================
    def get_column_data_format(self):
        """
        """
        if self.one_parameter:
            pass
        else:
            self._set_column_table_from_pivot_table(sort=True)
            self._seperate_para_value_from_qflag(sep='__')
#            self.add_df(df_col, 'col', add_columns=False)

    #==========================================================================

"""
#==============================================================================
#==============================================================================
"""
#class DataFrameHandler(object):
class DataFrameHandler(ColumnDataHandler, RowDataHandler):
    """
    Holds functions to handle DataFrame operations
    """
    def __init__(self):
        super().__init__()

    #==========================================================================
    def _add_columns(self): 
        print('in _add_columns')
        self.df['time'] = pd.Series(pd.to_datetime(self.df['SDATE'] + self.df['STIME'], format='%Y-%m-%d%H:%M'))

#        df['latit_dec_deg'] = df['LATIT'].apply(utils.decmin_to_decdeg)
#        df['longi_dec_deg'] = df['LONGI'].apply(utils.decmin_to_decdeg)
        
        if not 'LATIT_DD' in self.df and 'LATIT_DM' in self.df:
            self.df['LATIT_DD'] = self.df['LATIT_DM'].apply(utils.decmin_to_decdeg)
        if not 'LONGI_DD' in self.df and 'LONGI_DM' in self.df:
            self.df['LONGI_DD'] = self.df['LONGI_DM'].apply(utils.decmin_to_decdeg)
        
        if 'LATIT_DD' in self.df and 'LONGI_DD' in self.df:
            self.df['profile_key'] = self.df['time'].apply(str) + \
                                ' ' + \
                                self.df['LATIT_DD'].apply(str) + \
                                ' ' + \
                                self.df['LONGI_DD'].apply(str)
    
    #==========================================================================
    def _add_field(self):
        if self.filter_parameters.add_parameters:
            self.df[self.filter_parameters.add_parameters] = ''

    #==========================================================================
    def _additional_filter(self):
        """ Can be overwritten from child """
        pass
    
    #==========================================================================
    def _apply_field_filter(self):
        """
        """
        self._select_columns_from_df() # use only default fields 
        self._add_origin_columns(dtype=self.dtype, file_path=self.source) # MW
        self._organize_data_format()
    
    #==========================================================================
    def _calculate_data(self):
        """ Can be overwritten from child """
        pass
    
    #==========================================================================
    def _add_origin_columns(self, dtype='', file_path=''):
        """ 
        Created     20180419    by Magnus Wenzer
        Updated     20180419    by Magnus Wenzer 
        
        Adds collumns for origin_dtype and origin_file_path
        """
        self.df['origin_dtype'] = dtype
        self.df['origin_file_path'] = os.path.basename(file_path)

    
    #==========================================================================
    def _check_nr_of_parameters(self):
        """
        If one_parameter: We only need to set filter to keep parameter. No need 
        to use pivot_table..
        """
        if type(self.filter_parameters.use_parameters) != list:
            self.one_parameter=True
        else:
            self.one_parameter=False
            
    #==========================================================================
    def _convert_format(self, key_list, as_type=np.unicode):
        """
        """
        for key in key_list:
            if key and key in self.df:
                try:
                    self.df[key] = self.df[key].astype(as_type)
                except:
                    print(u'Could not convert format for:', key, u'in DataFrame')

    #==========================================================================
    def _delete_columns_from_df(self, columns=[]):
        """
        """
        self.df = self.df.drop(columns, axis=1, errors='ignore') # inplace=True ?

    #==========================================================================
    def _drop_duplicates(self, based_on_column=''):
        self.df.drop_duplicates(subset=based_on_column, inplace=True)
    
    #==========================================================================
    def _filter_column_data(self, df, data_filter_object): 
        """
        Filters column file data and returns resulting dataframe
        """
        boolean = data_filter_object.get_boolean(df)
        
        if not len(boolean):
            return df
        return df.loc[df.index[boolean], :]

    #==========================================================================
    def _handle_column_data(self):
        """
        """
#        cdh = ColumnDataHandler(DataFrameHandler)
        self.sort_columns_of_df()
        self.add_column_df()
        self._calculate_data()
        
    #==========================================================================
    def _handle_row_data(self, append_row_data=True):
        """
        """
        
        self._select_parameters()
        
        if append_row_data:
            self.add_row_df()
            
        if self.raw_data_copy:
            self.save_data_as_txt(directory=self.export_directory, 
                                  prefix=u'Raw_format')
            
#        rdh = RowDataHandler(DataFrameHandler)
        self._additional_filter()
        self.filter_row_data()
        self.get_column_data_format()
#        print(self.df.get('BQIm'))
        self.sort_columns_of_df()
        self.add_column_df()
#        self.add_row_df()
        self._calculate_data()

    #==========================================================================
    def _include_empty_cells(self, data=dict):
        # if data is dataframe.. but not working properly
#        mask = np.column_stack([data[col].str.contains('"empty"', na=False) for col in data])
#        data.loc[mask.any(axis=1)] = ''
        #TODO Make it nicer :D
        for key in data.keys():
            for i, value in enumerate(data.get(key)):
                if value == '"empty"':
                    data[key][i] = ''
        return data
        
    #==========================================================================
    def _map_parameter_list(self):
        """
        """
        
        # TODO: for rowdata this row results in None type calling unique()
        p_map = self.parameter_mapping.get_parameter_mapping(self.df.get(self.filter_parameters.parameter_key).unique())
        return p_map, list(p for p in p_map if p_map[p] in self.filter_parameters.use_parameters)

    #==========================================================================
    def _organize_data_format(self):
        """
        """
        if self.raw_data_format == 'row':
            self._handle_row_data()

        elif self.raw_data_format == 'column':
            self._handle_column_data()

    #==========================================================================
    def _recognize_format(self):
        """
        recognize row or column format and sets raw_data attribute
        """
        # TODO why is parameter_key attribute a list for rowdata?
#        print(self.filter_parameters.parameter_key)
#        print(self.df.keys())
        if self.filter_parameters.parameter_key in self.df: #'PARAM' in data header
            self.raw_data_format = 'row'
        else:
            self.raw_data_format = 'column'
        #TODO elif recognize netcdf..

    #==========================================================================        
    def _remap_header(self):
#        for k in self.df.columns.values:
#            print(k)
        map_dict = self.parameter_mapping.get_parameter_mapping(self.df.columns.values)
        self._rename_columns_of_DataFrame(map_dict)
        
    #==========================================================================
    def _rename_columns_of_DataFrame(self, mapping_dict):
        """
        """
        self.df = self.df.rename(index=str, columns=mapping_dict)
        
    #==========================================================================
    def _select_columns_from_df(self):
        """
        """
        if self.raw_data_format == 'row':
            self._delete_columns_from_df(columns=list(x for x in \
                                         self.df.keys() if x not in self.filter_parameters.compulsory_fields))
            
        elif self.raw_data_format == 'column':
            self._delete_columns_from_df(columns=list(x for x in \
                                         self.df.keys() if x not in \
                                         self.filter_parameters.compulsory_fields + \
                                         self.filter_parameters.use_parameters + \
                                         [u'Q_'+p for p in self.filter_parameters.use_parameters]))

    #==========================================================================
    def _select_parameters(self):
        """
        Can be rewritten in child-class, eg. DataHandlerPhytoplankton
        """
        self._check_nr_of_parameters()
        p_map, p_list = self._map_parameter_list()
        self.para_list = self.parameter_mapping.map_parameter_list(p_list)

        for para in p_list:
            # Change parameter name according to parameter codelist
            self.df[self.filter_parameters.parameter_key] = np.where(self.df[self.filter_parameters.parameter_key]==para, 
                                                                     p_map[para], 
                                                                     self.df[self.filter_parameters.parameter_key])

#        indices = np.where( self.df[parameter_head] == params_to_use[:,None] )[0]
#        indices = np.where( self.df[self.filter_parameters.parameter_key].isin(self.para_list) )[0]
#        self.df = self.df.iloc[indices,:]
        boolean = self.df[self.filter_parameters.parameter_key].isin(self.para_list)
        self.df = self.df.loc[boolean,:]
                            
    #==========================================================================
    def add_column_df(self, add_columns=False):
        """
        Adds data to the internal data structure. 
        """
        # Add columns (time etc.)
        if add_columns:
            self._add_columns()
        
        self.column_data[self.source] = self.df.copy(deep=True) # One DataFrame per source
#        self.column_data = self.column_data.append(self.df, ignore_index=True).fillna('')
                                
    #==========================================================================
    def add_row_df(self, add_columns=False):
        """
        Adds data to the internal data structure. 
        """
        # Add columns (time etc.)
        if add_columns:
            self._add_columns()
            
        self.row_data[self.source] = self.df.copy(deep=True)
#        self.row_data = self.row_data.append(self.df, ignore_index=True).fillna('')
            
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
    def get_dict(self, data, drop_nans=True, drop_empty=True):
        """
        """
        if drop_nans:
            # Index does not matter for the returned dictionary
            return { key : list(data.get(key).dropna(axis=0)) for key in data}
        else:
            return { key : list(data.get(key)) for key in data}
        
    #==========================================================================
    def get_index_for_profile_key(self, profile_key):
        """
        Method to get index for a unique profile key. 
        profile_key is "time LATIT LONGI"
        """
        return self.column_data.index[self.column_data['profile_key'] == profile_key]  
    
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
    def load_source(self, file_path=u'', sep='\t', encoding='cp1252', raw_data_copy=False):
        """
        Created                 by Johannes 
        Updated     20180419    by Magnus Wenzer
        
        Can be rewritten in child-class, eg. DataHandlerPhytoplankton
        """
        self.source = file_path
        self.raw_data_copy = raw_data_copy
        self.df = core.Load().load_txt(file_path, sep=sep, encoding=encoding, fill_nan=u'')
        self._remap_header()
        self._recognize_format()
        self._apply_field_filter()
        
    
    #==========================================================================    
    def delete_source(self, file_path):
        """
        Created     20180422    by Magnus Wenzer 
        Updated     20180422    by Magnus Wenzer 
        
        Deletes a sourcs in the data handler. 
        """
        if file_path in self.column_data.keys():
            self.column_data.pop(file_path)
        

    #==========================================================================
    def read_filter_file(self, file_path=u'', get_as_dict=True):
        """
        """
        data = core.Load().load_txt(file_path, fill_nan=np.nan)
        if get_as_dict:
            data = self.get_dict(data)
            
        data = self._include_empty_cells(data=data)
#        print(data)
        self.filter_parameters = core.AttributeDict()
        self.filter_parameters._add_arrays_to_entries(**data)

    #==========================================================================
    def save_data_as_txt(self, directory=u'', prefix=u''):   
        """
        """
        if not directory:
            return False
#            directory = os.path.dirname(os.path.realpath(__file__))[:-4] + 'test_data\\test_exports\\'
            
        if not directory.endswith(('/','\\')):
            directory = directory + '/'
            
        file_path = directory + '_'.join([prefix, self.dtype, 'data.txt'])
        print(u'Saving data to:',file_path)
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        self.df.to_csv(file_path, sep='\t', encoding='cp1252', index=False)
        
    
    #==========================================================================
    def save_column_data(self, file_path):
        """
        Created:        20180422    by Magnus Wenzer
        Last modified:  20180422    by Magnus Wenzer
        """
        pickle.dump(self.column_data, open(file_path, "wb"))
        
        
    #==========================================================================
    def sort_dict_by_keys(self,
                          sort_order=[],
                          ascending_list=[],
                          depth_head=None,
                          serno_head=None,
                          drop_index=True):
        """
        sort_order:     key list in sorting order
                        ['key_1','key_2','key_3']
                        
        ascending_list: ascending sorting or not (key specific)
                        [True,False,True]
                        
        return_as_dataframe: return as pandas Dataframe
        """
        print(u'Sorting..')
        if any([depth_head, serno_head]):
            self._convert_format([depth_head, serno_head], as_type=np.float)
            
        self.df = self.df.sort_values(sort_order, ascending=ascending_list)
        
        if any([depth_head, serno_head]):
            self._convert_format([depth_head, serno_head], as_type=np.unicode)
            
        if drop_index:
            print(u'Resetting and Dropping INDEX')
            self.df = self.df.reset_index().drop([u'index'], axis=1)
        
    #==========================================================================
    def sort_columns_of_df(self):
        
        sort_order = [key for key in self.filter_parameters.compulsory_fields if key in self.df]

        if utils.is_sequence(self.filter_parameters.use_parameters):
            for para in self.filter_parameters.use_parameters:
                if para in self.df:
                    sort_order.append(para)
                    if 'Q_'+para in self.df:
                        sort_order.append('Q_'+para)
        else:
            if self.filter_parameters.use_parameters in self.df:
                sort_order.append(self.filter_parameters.use_parameters)
            if 'Q_'+self.filter_parameters.use_parameters in self.df:
                sort_order.append('Q_'+self.filter_parameters.use_parameters)
        
        sort_order.extend(['origin_dtype', 'origin_file_path'])
        self.df = self.df[sort_order]
#        self.df = self.df.ix[:, sort_order]
#        self.df.reindex_axis(sort_order, axis=1) # DOES NOT WORK PROPERLY
                           
    #==========================================================================
    
    
"""
#==============================================================================
#==============================================================================
"""
class NETCDFDataHandler(DataFrameHandler):
    """
    """
    def __init__(self,
                 export_directory=''):
        super().__init__()
        self.export_directory = export_directory
        
    #==========================================================================    
    def load_nc(self):
        pass



"""
#==============================================================================
#==============================================================================
"""
class DataHandlerPhysicalChemical(DataFrameHandler):
    """
    """
    def __init__(self, 
                 filter_path=u'',
                 export_directory='',
                 parameter_mapping=None,
                 no_qflags=False): # no_qflags for data that has no quality flags (model data..)
        
        super().__init__()
        self.dtype = 'physicalchemical'
        self.export_directory = export_directory
        self.read_filter_file(file_path=filter_path)
        self.parameter_mapping = parameter_mapping
        self.no_qflags = no_qflags
        
        self.column_data = {} #pd.DataFrame()
        self.row_data = {} #pd.DataFrame()

    #==========================================================================
    def _calculate_data(self):
        """ 
        Rewritten from parent
        If there are no quality flags in data self.no_qflags is initialized 
        as True
        """
#        print('_calculate_data')
        if self.no_qflags:
            self.calculate_din()
        else:
            self.calculate_din(ignore_qf_list=['B','S']) 

        
    #==========================================================================
    def calculate_din(self, ignore_qf_list=[]):
        """ 
        Returns a vector calculated DIN. 
        If NO3 is not present, value is np.nan 
        """
        din_list = []
        
        for no2, no3, nox, nh4 in zip(*self.get_nxx_lists(ignore_qf_list)):

            if np.isnan(nox):
                din = np.nan
                if not np.isnan(no3):
                    din = no3                    
                    if not np.isnan(no2):
                        din += no2
                    if not np.isnan(nh4):
                        din += nh4
            else:
                din = nox
                if not np.isnan(nh4):
                    din += nh4
            
            if np.isnan(din):
                din=''
            else:
                din = str(round(din, 2))
            din_list.append(din)
            
        if not 'DIN' in self.column_data:
            self.column_data[self.source]['DIN'] = din_list
        else:
            self.column_data[self.source]['DIN_calulated'] = din_list
                            
    #==========================================================================
    def get_float_list(self, key, ignore_qf=[]):
        """
        Get all values as floats
        """
        return utils.get_float_list_from_str(df=self.column_data[self.source], 
                                             key=key, ignore_qf=ignore_qf)
    
    #==========================================================================
    def get_nxx_lists(self, ignore_qf_list):
        """
        Returns 4 equal in length arrays for NO2, NO3, NO23, NH4..
        If a parameter does not excist in the loaded dataset, an array filled 
        with NaNs is returned for that specific parameter
        """
        if 'NTRI' in self.column_data[self.source]:
            ntri = self.get_float_list(key='NTRI', ignore_qf=ignore_qf_list)
        else:
            ntri = [np.nan]*self.column_data[self.source].shape[0]
        if 'NTRA' in self.column_data[self.source]:
            ntra = self.get_float_list(key='NTRA', ignore_qf=ignore_qf_list)
        else:
            ntra = [np.nan]*self.column_data[self.source].shape[0]
        if 'NTRZ' in self.column_data[self.source]:
            ntrz = self.get_float_list(key='NTRZ', ignore_qf=ignore_qf_list)
        else:
            ntrz = [np.nan]*self.column_data[self.source].shape[0]
        if 'AMON' in self.column_data[self.source]:
            amon = self.get_float_list(key='AMON', ignore_qf=ignore_qf_list)
        else:
            amon = [np.nan]*self.column_data[self.source].shape[0]
        return ntri, ntra, ntrz, amon
    
    #==========================================================================
                                      
"""
#==============================================================================
#==============================================================================
"""
class DataHandlerZoobenthos(DataFrameHandler):
    """
    """
    def __init__(self, filter_path=u'',
                 export_directory='', 
                 parameter_mapping=None):
        
        super().__init__()
        self.dtype = 'zoobenthos'
        self.export_directory = export_directory
        self.read_filter_file(file_path=filter_path)
        self.parameter_mapping = parameter_mapping
        
        self.column_data = {} #pd.DataFrame()
        self.row_data = {} #pd.DataFrame()
        
    #==========================================================================    
        
"""
#==============================================================================
#==============================================================================
"""
class DataHandlerChlorophyll(DataFrameHandler):
    """
    """
    def __init__(self, filter_path=u'', 
                 export_directory='',
                 parameter_mapping=None):
        
        super().__init__()
        self.dtype = 'chlorophyll' # Only Tube samples ? 
        self.export_directory = export_directory
        self.read_filter_file(file_path=filter_path)
        self.parameter_mapping = parameter_mapping
        
        self.column_data = {} #pd.DataFrame()
        self.row_data = {} #pd.DataFrame()
        
    #==========================================================================   

"""
#==============================================================================
#==============================================================================
"""
class DataHandlerPhytoplankton(DataFrameHandler):
    """
    """
    def __init__(self, filter_path=u'', 
                 export_directory='',
                 parameter_mapping=None):
        
        super().__init__()
        self.dtype = 'phytoplankton'
        self.export_directory = export_directory
        self.read_filter_file(file_path=filter_path)
        self.parameter_mapping = parameter_mapping
        
        self.column_data = {} #pd.DataFrame()
        self.row_data = {} #pd.DataFrame()
    
    #==========================================================================
    def _additional_filter(self):
        self._delete_columns_from_df(columns=self.filter_parameters.extra_fields + [self.filter_parameters.value_key])
        self._drop_duplicates(based_on_column='SHARKID_MD5')
        self.filter_parameters.use_parameters = 'BIOV_CONC_ALL'

    #==========================================================================
    def _extended_filter_for_phytoplanton_data(self):     
        """
        Selects parameters and TROPHIC-status according to 
        self.filter_parameters
        """
        self.df = utils.set_filter(df=self.df, 
                                   filter_dict={self.filter_parameters.parameter_key : self.para_list, 
                                                self.filter_parameters.trophic_key : self.filter_parameters.use_trophic},
                                   return_dataframe=True)
        
    #==========================================================================
    def _get_total_biovolume(self, samp_key=''):
        """
        Created:    2017        by Johannes Johansson
        Modified:   20180320    by Lena Viktorsson (changes df.astype(np.float) to pd.to_numeric(df))
        """
        # keys could be set in filter_parameters instead..
#        print(self.df.get(samp_key).unique)
        for sample in self.df.get(samp_key).unique():
            
            boolean = utils.set_filter(df=self.df, 
                                       filter_dict={samp_key:sample})
            
            #tot_value = self.df.loc[boolean,self.filter_parameters.value_key].astype(np.float).sum(skipna=True)
            tot_value = pd.to_numeric(self.df.loc[boolean,self.filter_parameters.value_key]).sum(skipna=True)            
            
            self.df.loc[boolean, self.filter_parameters.add_parameters] = str(tot_value)

    #==========================================================================
    def _select_parameters(self):
        """
        Rewritten from parent-class
        """
        #spara undan och sedan delete .extra_fields
        # spara undan som kolumnformat
        
        self._check_nr_of_parameters()
        p_map, p_list = self._map_parameter_list()
        self.para_list = self.parameter_mapping.map_parameter_list(p_list)

        for para in p_list:
            # Change parameter name according to parameter codelist
            #TODO CHeck if this variant of np.where works with pandas irregular index..
            self.df[self.filter_parameters.parameter_key] = np.where(self.df[self.filter_parameters.parameter_key]==para, 
                                                                     p_map[para],
                                                                     self.df[self.filter_parameters.parameter_key])
        self._extended_filter_for_phytoplanton_data()
        self._add_field()
        self._get_total_biovolume(samp_key='SHARKID_MD5')
            
    #==========================================================================   
"""
#==============================================================================
#==============================================================================
"""
class DataHandler(object): 
    """
    Class to hold data.  
    """
    #TODO metod för att kontrollera odeffinerade datafiler, vilken datatyp är 
    #det som gäller? input från användaren eller datafilen.. finns inte datatyp 
    #i filen? säg till användaren.. när vi vet datatyp, spara filnamn i fil
    #TODO check dubblett 
    def __init__(self, 
                 input_data_directory=None, 
                 resource_directory=None): 
#        print(input_data_directory, resource_directory)
        assert all([input_data_directory, resource_directory])
        super().__init__()
#        self.source = source
#        self.column_data = pd.DataFrame()
#        self.row_data = pd.DataFrame() 
        
        self.input_data_directory = input_data_directory 
        self.resource_directory = resource_directory
        
        # TODO: Maybe WorkSpace should specify these too
        self.raw_data_directory = self.input_data_directory + '/raw_data'
        self.export_directory = self.input_data_directory + '/exports'

        path_parameter_mapping = self.resource_directory + '/mappings/mapping_parameter_dynamic_extended.txt'
        path_fields_filter = self.resource_directory + '/filters/'
    
#        path_parameter_mapping = current_path + u'/test_data/mappings/mapping_parameter_dynamic_extended.txt'
#        path_fields_filter = current_path + u'/test_data/filters/'        
        
        
        self._load_field_mapping(file_path=path_parameter_mapping)
        
        
        #TODO lägg in datatypsobject i dict ? seperate sources as keys... 'phyche_source' DONE!
        
        
        self.chlorophyll = DataHandlerChlorophyll(filter_path=path_fields_filter+u'filter_fields_chlorophyll_integrated.txt',
                                                  export_directory=self.export_directory,
                                                  parameter_mapping=self.parameter_mapping)
        
        
        self.physicalchemical = DataHandlerPhysicalChemical(filter_path=path_fields_filter+'filter_fields_physical_chemical.txt',
                                                             export_directory=self.export_directory,
                                                             parameter_mapping=self.parameter_mapping)

        self.physicalchemicalmodel = DataHandlerPhysicalChemical(filter_path=path_fields_filter+'filter_fields_physical_chemical_model.txt',
                                                                   export_directory=self.export_directory,
                                                                   parameter_mapping=self.parameter_mapping,
                                                                   no_qflags=True)        
        
        self.phytoplankton = DataHandlerPhytoplankton(filter_path=path_fields_filter+u'filter_fields_phytoplankton.txt',
                                                      export_directory=self.export_directory,
                                                      parameter_mapping=self.parameter_mapping)
        
        
        self.zoobenthos = DataHandlerZoobenthos(filter_path=path_fields_filter+'filter_fields_zoobenthos.txt',
                                                export_directory=self.export_directory,
                                                parameter_mapping=self.parameter_mapping)
        
        
#        self.all_data = None
        self.all_data = pd.DataFrame() # MW

    #==========================================================================
    def _load_field_mapping(self, file_path=u''):
        """
        """
        self.parameter_mapping = core.ParameterMapping()
        self.parameter_mapping.load_mapping_settings(file_path=file_path)


    #==========================================================================
    def add_df(self, pd_df, data_type, add_columns=False):
        """
        Adds data to the internal data structure. 
        """
        # Add columns (time etc.)
        if add_columns:
            self._add_columns(pd_df)
        
        if 'col' in data_type:
            self.column_data = self.column_data.append(pd_df, ignore_index=True)
        elif 'row' in data_type:
            self.row_data = self.row_data.append(pd_df, ignore_index=True).fillna('')
#        print(self.data_phys_chem.head())
    

    #==========================================================================
#    def add_txt_file(self, file_path, data_type): 
    def add_txt_file(self, file_path, data_type, map_object=None): 

        data = pd.read_csv(file_path, sep='\t', encoding='cp1252')
        if map_object != None:
            map_dict = map_object.get_parameter_mapping( data.columns.values )
            data = self._rename_columns_of_DataFrame( data, map_dict )

        self.add_df(data, data_type)
        # TODO: Check if all is ok
        
        
#    #==========================================================================
#    def filter_data(self, data_filter_object, filter_id=''):
#        """
#        Filters data according to data_filter_object. 
#        data_filter_object is a core.filters.DataFilter-object. 
#        Returns a DataHandler object with the filtered data. 
#        """
#        new_data_handler = DataHandler(self.source + '_filtered_%s' % filter_id)
#        if len(self.column_data):
##            print( 'data_filter_object', data_filter_object)
#            df = self._filter_column_data(self.column_data, data_filter_object)
#            if data_filter_object.parameter:
##                print('df', df.columns)
##                print('data_filter_object.parameter:', data_filter_object.parameter)
#                for col in list(df.columns):
#                    if col not in core.ParameterList().metadata_list + [data_filter_object.parameter]:
#                        df = df.drop(col, 1)
#            new_data_handler.add_df(df, 'column')
#        if len(self.row_data):
#            df = self._filter_row_data(self.row_data, data_filter_object)
#            new_data_handler.add_df(df, 'row')
#        
#        return new_data_handler


#    #==========================================================================
#    def _filter_column_data(self, df, data_filter_object): 
#        """
#        Filters column file data and returns resulting dataframe
#        """
#        #TODO kolla på flera DF ? annan struktur ? 
#        boolean = data_filter_object.get_column_data_boolean(df)
#        
#        if not len(boolean):
#            return df
#        return df.loc[df.index[boolean], :]

    #==========================================================================
    def get_all_column_data_df(self, boolean_filter=[]): 
        """
        mw
        Returns a pandas dataframe that contains all data in column format. 
        boolean_filter is a pd.Series. If not given the whole df is returned. 
        """
        if len(boolean_filter): 
            # TODO: Check length
            return self.all_data.loc[boolean_filter, :]
        else: 
            return self.all_data
    
        
    #==========================================================================
    def merge_all_data(self, save_to_txt=False):
        """
        Created:        
        Last modified:  20180720    by Magnus Wenzer
        
        - Do we need to sort all_data ?
        - Merge data from different datatypes for the same visit ?
        """
        self.all_data = pd.DataFrame()
        
        # All datatypes that might include data for setting ecological status
        all_datatypes = [u'chlorophyll',
                         u'physicalchemical',
                         u'physicalchemicalmodel',
                         u'phytoplankton',
                         u'zoobenthos']
        
        mandatory_keys = ['DEPH']
        for dtype in all_datatypes:
            if dtype in dir(self):
                #print(dtype)
                #print(self.__getattribute__(dtype).column_data)
                # Appends dataframes from each datatype into one dataframe
                for source in self.__getattribute__(dtype).column_data:
                    # Each datatype might have multiple sources..
                    # .column_data is a dict 
                    df = self.__getattribute__(dtype).column_data[source] 
                    if not all([item in df.columns for item in mandatory_keys]):
                        raise exceptions.MissingKeyInData(message=os.path.basename(source))
                    self.all_data = self.all_data.append(df, 
                                                         ignore_index=True)
        if not len(self.all_data):
            print('No data available after "merge_all_data"!')
            return False
        
        # Save pkl-file for all_data_raw. Updated 20180525    by Magnus Wenzer
        sld_object = core.SaveLoadDelete(self.export_directory)
        sld_object.save_df(self.all_data, file_name='all_data_raw', force_save_txt=True, only_pkl=not save_to_txt)
#        pickle.dump(self.all_data, open(self.export_directory + "/all_data_raw.pickle", "wb"))
#        if save_to_txt:
#            save_data_file(df=self.all_data, 
#                           directory=self.export_directory, 
#                           file_name='all_data.txt')
            
        # Load data again. This way we can treet new and old 
        #"self.all_data" the same way 
        self.all_data = pd.DataFrame()
        self.load_all_datatxt()
       

    #==========================================================================
    def load_datatypetxt(self, datatype, sep='\t', encoding='cp1252'):
        """
        loads existing data files for the given datatype from export directory (from pickle if existing, otherwise from txt)
        Created:        20180422    by Magnus Wenzer
        Last modified:  20180422    by Magnus Wenzer
        """
        # Column data file 
        try:
            file_path = '{}/column_format_{}_data.pickle'.format(self.export_directory, datatype)
            self.column_data = pickle.load(open(file_path, "rb")) 
            return True
        except (OSError, IOError) as e: 
            return False
#            try:
#                file_path = '{}/column_format_{}_data.txt'.format(self.export_directory, datatype)
#                self.column_data = load_data_file(file_path)
#            except:
#                return False
        
#        # Raw data file 
#        file_path = '{}/raw_format_{}_data.txt'.format(self.export_directory, datatype)
#        try:
#            self.row_data = load_data_file(file_path)
#        except (OSError, IOError) as e:
#            return False
#        
#        return True
        
    #==========================================================================
    def load_all_datatxt(self, sep='\t', encoding='cp1252'):
        """
        loads existing all_data file from export directory (from pickle if existing, otherwise from txt)
        Created:        20180318    by Lena Viktorsson 
        Last modified:  20180525    by Magnus Wenzer
        """
        def float_convert(x):
            try:
                return float(x)
            except:
#                print('float_convert')
                return np.nan 
            
            
        def str_convert(x):
            x = str(x)
            if x == 'nan':
                x = ''
            return x
        
        print('self.all_data', len(self.all_data))
        if len(self.all_data): 
            return False, False
        else:
            sld_object = core.SaveLoadDelete(self.export_directory) # 20180525    by Magnus Wenzer
            try:
                self.all_data = sld_object.load_df('all_data', load_txt=False) # 20180525    by Magnus Wenzer
#                print()
#                with open(self.export_directory + "/all_data.pkl", "rb") as fid:
#                    self.all_data = pickle.load(fid)
                filetype = 'pickle'
            except (FileNotFoundError, UnboundLocalError) as e: 
                # UnboundLocalError is for when df was not created in sld_object.load_df()
                print('MMMMMMMMM')
                try: 
                    self.all_data = sld_object.load_df('all_data_raw', load_txt=False) # 20180525    by Magnus Wenzer
#                    self.all_data = pickle.load(open(self.export_directory + "/all_data_raw.pickle", "rb"))
                except (OSError, IOError) as e:
                    raise(OSError, IOError, 'Raw data pickle file does not exist! This is created during in "merge_all_data".')
#                    self.all_data = load_data_file(self.export_directory + '/all_data.txt')
#                self.all_data = core.Load().load_txt(self.export_directory + '/all_data.txt', sep=sep, encoding=encoding, fill_nan=u'')
                #TODO: better way to say which columns should be converted to float and int?
                self.all_data['MONTH'] = self.all_data['SDATE'].apply(lambda x: int(x[5:7])) 
                self.all_data['YEAR'] = self.all_data['SDATE'].apply(lambda x: int(x[0:4]))
                self.all_data['MYEAR'] = self.all_data['MYEAR'].astype(int)
#                self.all_data['YEAR'] = self.all_data['SDATE'].apply(lambda x: int(x[0:4])).astype(int)
                self.all_data['DEPH'] = self.all_data['DEPH'].apply(lambda x: float(x) if x else np.nan) 
                self.all_data['POSITION'] = self.all_data.apply(lambda x: '{0:.2f}'.format(float_convert(x.LATIT_DD)) + '_' + '{0:.2f}'.format(float_convert(x.LONGI_DD)), axis = 1)
                
                if 'MNDEP' not in self.all_data.columns: 
                    self.all_data['MNDEP'] = np.nan
                    self.all_data['MXDEP'] = np.nan
                
                # MW: Add visit_id
                self.all_data['visit_id_str'] = self.all_data['POSITION'] + \
                                                self.all_data['SDATE'] + \
                                                self.all_data['STIME']
#                self.all_data['visit_id_str'] = self.all_data['LATIT_DD'] + \
#                                                self.all_data['LONGI_DD'] + \
#                                                self.all_data['SDATE'] + \
#                                                self.all_data['STIME']
#                depth_interval=[0, 10]           
#                #--------------------------------------------------------------
#                par_boolean = ~self.all_data['CPHL_BTL'].isnull() 
#        
#                depth_boolean = (self.all_data['DEPH'] >= depth_interval[0]) & \
#                                (self.all_data['DEPH'] <= depth_interval[1])
#                par_boolean = par_boolean & depth_boolean
#                
#                visit_boolean = self.all_data['visit_id_str'] == '58.9113311.187502017-08-0111:40'
#                
#                print('='*50)
#                print('BEFORE')
#                print('='*50)
#                print(self.all_data.loc[visit_boolean & par_boolean, ['index_column', 'DEPH', 'CPHL_BTL', 'Q_CPHL_BTL']])
#                print('-'*50)
#                #--------------------------------------------------------------
                
                

                

                for col in self.all_data.columns:
                    if col.startswith('Q_'): 
                        par = col[2:]
#                        print(par)
                        self.all_data[par] = self.all_data[par].apply(float_convert)
                        self.all_data[col] = self.all_data[col].apply(str_convert)
#                        try:
#                            self.all_data[par] = self.all_data[par].apply(lambda x: float(x) if x else np.nan) 
#                        except ValueError as e:
#                            self.all_data[par] = self.all_data[par].apply(convert)
                            #TODO: send info to user
                    elif col in ['DIN', 'CPHL_BTL']: 
#                        print(col)
                        self.all_data[col] = self.all_data[col].apply(float_convert)
#                        try:
#                            self.all_data[par] = self.all_data[par].apply(lambda x: float(x) if x else np.nan) 
#                        except ValueError as e:
#                            self.all_data[par] = self.all_data[par].apply(convert)
                    elif col == 'VISS_EU_CD':
                        self.all_data[col] = self.all_data[col].apply(lambda x: 'SE' + x if 'SE' not in x else x)
                        
                
                self.all_data['STIME'] = self.all_data['STIME'].apply(lambda x: x[:5])
                
                # MW 20180716 
                self.all_data['date'] = pd.to_datetime(self.all_data['SDATE'])
                
#                # MW: Add visit_id
#                self.all_data['visit_id_str'] = self.all_data['LATIT_DD'] + \
#                                                self.all_data['LONGI_DD'] + \
#                                                self.all_data['SDATE'] + \
#                                                self.all_data['STIME']
                
                # MW: Add prioritized salinity 
                self._add_prioritized_parameter('SALT', 'SALT_BTL', 'SALT_CTD') 
                
                # MW: Add prioritized temperature 
                self._add_prioritized_parameter('TEMP', 'TEMP_BTL', 'TEMP_CTD')
                
                # MW: Add prioritized oxygen 
                self._add_prioritized_parameter('DOXY', 'DOXY_BTL', 'DOXY_CTD')
                
#                #--------------------------------------------------------------
#                par_boolean = ~self.all_data['CPHL_BTL'].isnull() 
#        
#                depth_boolean = (self.all_data['DEPH'] >= depth_interval[0]) & \
#                                (self.all_data['DEPH'] <= depth_interval[1])
#                par_boolean = par_boolean & depth_boolean
#                
#                visit_boolean = self.all_data['visit_id_str'] == '58.9113311.187502017-08-0111:40'
#                
#                print('='*50)
#                print('AFTER')
#                print('='*50)
#                print(self.all_data.loc[visit_boolean & par_boolean, ['index_column', 'DEPH', 'CPHL_BTL', 'Q_CPHL_BTL']])
#                print('-'*50)
#                #--------------------------------------------------------------
                
                if 1:
                    # MW: Add integrated chlorophyl from CHPL_BTL
                    self._add_integrated_calc(use_par='CPHL_BTL', 
                                              new_par='CPHL_INTEG_CALC', 
                                              depth_interval=[0, 10], 
                                              exclude_qf=[u'?',u'B',u'S'], 
                                              min_nr_values=2)
                
                
                sld_object.save_df(self.all_data, file_name='all_data', force_save_txt=True, only_pkl=False) # 20180525    by Magnus Wenzer
#                self.df = 
#                with open(self.export_directory + "/all_data.pkl", "rb") as fid:
#                    pickle.dump(self.all_data, fid, "wb")
#                core.load.save_data_file(df=self.all_data, 
#                               directory=self.export_directory, 
#                               file_name='all_data.txt')
                filetype = 'txt'
            return True, filetype
        
        
    
    #==========================================================================
    def _add_prioritized_parameter(self, new_par, primary_par, secondary_par, exclude_qf=['B', 'S']):
        """
        Created:        20180413    by Magnus Wenzer
        Last modified:  20180419    by Magnus Wenzer
        
        Adds the parameter <new_par_name> by combining the parameters in args. 
        The first parameter in args that is not have a quality flag listed in exclude_qf
        will be prioritized. 
        Three columns are added to self.all_data: 
        <new_par_name> 
        Q_<new_par_name>
        source_<new_par_name>
        
        """
        t0 = time.time()
        primary_par_qf = 'Q_' + primary_par
        secondary_par_qf = 'Q_' + secondary_par
        
        if not all([True if item in self.all_data.columns else False \
                    for item in [primary_par, primary_par_qf, secondary_par, secondary_par_qf]]): 
            return False
        
        q_new_par = 'Q_'+new_par
        source_new_par = 'source_'+new_par
        self.all_data[new_par] = np.nan
        self.all_data[q_new_par] = ''
        self.all_data[source_new_par] = ''
        
        
        # Find where primary is valid 
        primary_valid = ~pd.isnull(self.all_data[primary_par]) & \
                        ~self.all_data[primary_par_qf].isin(exclude_qf)
        
        # Add where primary is valid 
        self.all_data.loc[primary_valid, new_par] = self.all_data.loc[primary_valid, primary_par]
        self.all_data.loc[primary_valid, q_new_par] = self.all_data.loc[primary_valid, primary_par_qf]
        self.all_data.loc[primary_valid, source_new_par] = primary_par
                         
        # Find where primary is not valid and secondary is
        add_secondary_valid = ~pd.isnull(self.all_data[secondary_par]) & \
                              ~self.all_data[secondary_par_qf].isin(exclude_qf) & \
                               ~primary_valid
        
        # Add where primary is not valid and secondary is
        self.all_data.loc[add_secondary_valid, new_par] = self.all_data.loc[add_secondary_valid, secondary_par]
        self.all_data.loc[add_secondary_valid, q_new_par] = self.all_data.loc[add_secondary_valid, secondary_par_qf]
        self.all_data.loc[add_secondary_valid, source_new_par] = secondary_par
        
        print('time for _add_prioritized_parameter {} is: {}'.format(new_par, time.time()-t0))
        
    
    #===========================================================================
    def get_exclude_index_array(self, df): 
        """
        Created:        20180423    by Magnus Wenzer
        Last modified:  20180423    by Magnus Wenzer
        """
        exclude_list = []
        for col in df.columns:
            if 'Q_' in col:
                exclude_list.append(col[2:])
                exclude_list.append(col)
            elif 'source' in col:
                exclude_list.append(col) 
                
        exclude_index_list = [True if par in exclude_list else False for par in df.columns]
        return np.array(exclude_index_list)


    #===========================================================================
    def _add_integrated_calc(self, 
                            use_par=None, 
                            new_par=None, 
                            depth_interval=[0, 10], 
                            exclude_qf=[u'?',u'B',u'S'], 
                            min_nr_values=2):
        
        """
        Created:        20180423    by Magnus Wenzer
        Last modified:  20180423    by Magnus Wenzer
        """
        #----------------------------------------------------------------------
        def calculate(df):
            if len(df) < min_nr_values:
                #print(len(df))
                return False
            # Extrac data lists
            depth_list = list(df['DEPH'].values) 
            value_list = list(df[use_par].values) 
            
            t_calc_integ = time.time()
            mean_value = utils.get_integrated_mean(depth_list, 
                                                   value_list, 
                                                   depth_interval)
            time_list_calc_integ.append(time.time() - t_calc_integ)
            
            t_add_row = time.time()
            # Add info to row
            new_row_series = df.loc[df.index[0], :].copy(deep=True)
            new_row_series[new_par] = mean_value
            new_row_series[new_par_depths] = ';'.join(map(str, depth_list))
            new_row_series[new_par_values] = ';'.join(map(str, value_list))
            new_row_series['MNDEP'] = depth_interval[0]
            new_row_series['MXDEP'] = depth_interval[1]
            #print('df.columns', len(df.columns))
            #print(df.columns)
            new_row = np.array(new_row_series)
            new_row[exclude_index_array] = np.nan
        
            new_list_to_append.append(list(new_row)) 
            time_list_add_row.append(time.time() - t_add_row)
            
            return True
        #----------------------------------------------------------------------
        
        
        
        new_par_depths = new_par + '_depths'
        new_par_values = new_par + '_values' 

        new_list_to_append = [] # list of lists with the new rows to be added to all_data once all calculations are done
        # new_df = pd.DataFrame(columns=all_data.columns)
        
        time_list_group_data = []
        time_list_calc_integ = []
        time_list_add_row = [] 
        
        
        
        t_tot = time.time()
        t_preparations = time.time()
        # Add result columns
        self.all_data[new_par] = np.nan 
        self.all_data[new_par_depths] = np.nan
        self.all_data[new_par_values] = np.nan
        
        
        exclude_index_array = self.get_exclude_index_array(self.all_data) 
        # print(len(exclude_index_array))
        # print(len(all_data.columns))
        
        # Narrow the data to only include lines where par is present and depth is in range
        use_par_boolean = ~self.all_data[use_par].isnull() 
        depth_boolean = (self.all_data['DEPH'] >= depth_interval[0]) & \
                        (self.all_data['DEPH'] <= depth_interval[1]) 
            
        active_boolean = use_par_boolean & depth_boolean
        time_preparations = time.time() - t_preparations
        
        
        t_group_data = time.time()
        grouped_data = self.all_data.loc[active_boolean, :].groupby('visit_id_str')
        time_list_group_data.append(time.time() - t_group_data)
        
        t_iterator = time.time()
        calculations = (calculate(group) for visit_id, group in grouped_data)
        time_iterator = time.time() - t_iterator
        
        t_all_calculation = time.time()
        result = list(calculations)
        time_all_calculation = time.time() - t_all_calculation
        
                              
        # Add new rows to self.all_data 
        t_add_data = time.time()
        add_lines_df = pd.DataFrame(new_list_to_append, columns=self.all_data.columns)
        self.all_data = self.all_data.append(add_lines_df) 
        self.all_data.reset_index(drop=True, inplace=True)
        time_add_data = time.time() - t_add_data
                                 
        time_total = time.time() - t_tot
        print('-'*50)
        print('Total time:', time_total)
        print('time_preparations'.ljust(30), time_preparations)
        print('time_list_group_data:'.ljust(30), sum(time_list_group_data))
        print('time_list_calc_integ:'.ljust(30), sum(time_list_calc_integ))
        print('time_list_add_row:'.ljust(30), sum(time_list_add_row)) 
        print('time_all_calculations:'.ljust(30), time_all_calculation)
        print('time_iterator:'.ljust(30), time_iterator)
        print('time_add_data:'.ljust(30), time_add_data)
        print('Done adding integrated_calc "{}" using parameter "{}"'.format(new_par, use_par))
        print('time for integrated_calc "{}" using parameter "{} is: {}'.format(new_par, use_par, time_total))
        
        
    #===========================================================================
    def old_add_integrated_calc(self, 
                            par, 
                            new_par_name, 
                            depth_interval=[0, 10], 
                            exclude_qf=[u'?',u'B',u'S'], 
                            min_nr_values=2):
        
        """
        Created:        20180420    by Magnus Wenzer
        Last modified:  20180420    by Magnus Wenzer
        """
        
        def calculate(current_visit_id):
#            print(current_visit_id)
            visit_boolean = self.all_data['visit_id_str'] == current_visit_id
            index = par_boolean & visit_boolean 
            
            # Extrac data lists
            depth_list = list(self.all_data.loc[index, 'DEPH'].values) 
            value_list = list(self.all_data.loc[index, par].values) 
            
            # Continue if not enough data to calculate 
#            if len(depth_list) < min_nr_values:
#                return False

            mean_value = utils.get_integrated_mean(depth_list, 
                                                   value_list, 
                                                   depth_interval)
            
            new_row = [] 
            for parameter, value in zip(self.all_data.columns, self.all_data.loc[visit_boolean,:].values[0]):
                if parameter == 'MNDEP': 
                    new_row.append(depth_interval[0])
                elif parameter == 'MXDEP': 
                    new_row.append(depth_interval[1])
                elif parameter == new_par_name: 
                    new_row.append(mean_value)
                elif parameter == new_par_name_depth: 
                    new_row.append(';'.join(map(str, depth_list)))
                elif parameter == new_par_name_values: 
                    new_row.append(';'.join(map(str, value_list)))
                elif parameter in exclude_list: 
                    new_row.append(np.nan) 
                else:
                    new_row.append(value) 
            
#            print(len(self.all_data)+1)
            self.all_data.loc[max(self.all_data)+1, :] = new_row    
            return True
        
        
        
        
        new_par_name_depth = new_par_name + '_depths'
        new_par_name_values = new_par_name + '_values'
        
        # Add new columns to dataframe 
        self.all_data[new_par_name] = np.nan
        self.all_data[new_par_name_depth] = '' 
        self.all_data[new_par_name_values] = ''
                     
        # Check columns to exclude in row 
        exclude_list = [] 
        for item in self.all_data.columns: 
            if item.startswith('Q_'):
                exclude_list.append(item[2:])
                exclude_list.append(item)
            elif item.startswith('source_'): 
                exclude_list.append(item)
        
        
        # Create boolen where par has values
        par_boolean = ~self.all_data[par].isnull() 
        
        #----------------------------------------------------------------------
        # Depth boolean to reduce nr of unique visits. 
        # This has to be removed/changed if halocline depth should be used 
        # instead of fixed depth interval. 
        # OBS! also used below! 
        depth_boolean = (self.all_data['DEPH'] >= depth_interval[0]) & \
                        (self.all_data['DEPH'] <= depth_interval[1])
        par_boolean = par_boolean & depth_boolean
        #----------------------------------------------------------------------
        
        
        # Get list och unique visits 
        unique_visit_id_list = list(set(self.all_data.loc[par_boolean, 'visit_id_str']))
        
        temp = list(map(calculate, unique_visit_id_list))
#        return 
##        # Get next index in self.all_data . Increment this after adding new line to save time 
##        next_index = max(self.all_data.index) + 1 
##                        
##                        
##        #----------------------------------------------------------------------
##        input_dict = {'current_visit_id': current_visit_id, 
##                      }
##        
##        
##        df_list = [by_year_pos.loc[by_year_pos.YEAR == year]['position_mean']]*n
##        def bootstrap(df):
##            return df.sample(frac = 1, replace = True).mean()
##             
##        BQIsim = map(bootstrap, df_list)
#        #----------------------------------------------------------------------
#
#
#        
#        
#        # Loop unique visits 
#        for k, current_visit_id in enumerate(unique_visit_id_list):
#            if not k%100:
#                print(k, current_visit_id)
##            # Create boolen where par has values
##            par_boolean = ~self.all_data[par].isnull() 
##            
##            #----------------------------------------------------------------------
##            # Depth boolean to reduce nr of unique visits. 
##            # This has to be removed/changed if halocline depth should be used 
##            # instead of fixed depth interval. 
##            # OBS! also used below! 
##            depth_boolean = (self.all_data['DEPH'] >= depth_interval[0]) & \
##                            (self.all_data['DEPH'] <= depth_interval[1])
##            par_boolean = par_boolean & depth_boolean
##            #----------------------------------------------------------------------
#            
#        
#            visit_boolean = self.all_data['visit_id_str'] == current_visit_id
#            index = par_boolean & visit_boolean 
#            
#            # Extrac data lists
#            depth_list = list(self.all_data.loc[index, 'DEPH'].values) 
#            value_list = list(self.all_data.loc[index, par].values) 
#            
#            # Continue if not enough data to calculate 
#            if len(depth_list) < min_nr_values:
#                continue
#            
##            #--------------------------------------------------------------
##            par_boolean = ~self.all_data['CPHL_BTL'].isnull() 
##    
##            depth_boolean = (self.all_data['DEPH'] >= depth_interval[0]) & \
##                            (self.all_data['DEPH'] <= depth_interval[1])
##            par_boolean = par_boolean & depth_boolean
##            
##            visit_boolean = self.all_data['visit_id_str'] == '58.9113311.187502017-08-0111:40'
##            
##            print('='*50)
##            print('1')
##            print('='*50)
##            print(self.all_data.loc[visit_boolean & par_boolean, ['index_column', 'DEPH', 'CPHL_BTL', 'Q_CPHL_BTL']])
##            print('-'*50)
##            #--------------------------------------------------------------
#            #--------------------------------------------------------------
#            
##            print('='*50)
##            print('2')
##            print('='*50)
##            print(self.all_data.loc[index, ['index_column', 'DEPH', 'CPHL_BTL', 'Q_CPHL_BTL']])
##            print('-'*50)
##            #--------------------------------------------------------------
##            
##            
##            print('-'*50)
##            print(current_visit_id)
##            print(par)
##            print(np.where(visit_boolean))
##            print(np.where(visit_boolean))
##            print(depth_list)
##            print(value_list)
##            print(depth_interval)
##            print(len(self.all_data) )
##            print(len(par_boolean))
#            
#            mean_value = utils.get_integrated_mean(depth_list, 
#                                                   value_list, 
#                                                   depth_interval)
#            
#            new_row = [] 
#            for parameter, value in zip(self.all_data.columns, self.all_data.loc[visit_boolean,:].values[0]):
#                if parameter == 'MNDEP': 
#                    new_row.append(depth_interval[0])
#                elif parameter == 'MXDEP': 
#                    new_row.append(depth_interval[1])
#                elif parameter == new_par_name: 
#                    new_row.append(mean_value)
#                elif parameter == new_par_name_depth: 
#                    new_row.append(';'.join(map(str, depth_list)))
#                elif parameter == new_par_name_values: 
#                    new_row.append(';'.join(map(str, value_list)))
#                elif parameter in exclude_list: 
#                    new_row.append(np.nan)
#                else:
#                    new_row.append(value)
#            
#            self.all_data.loc[next_index, :] = new_row 
#                  
#            next_index += 1
        
            
        
#        class Calculations():
#            def __init__(self):
#                pass
#        
#        based_on_par_boolean = ~self.all_data[based_on_par].isnull() 
#        
#        
#        
#        
#        depths = self.get_float_array(u'DEPH', ignore_qf=exclude_qf)
#        index = np.where((depths >= depth_interval[0]) & (depths <= depth_interval[-1]))[0]
#        depths = depths[index]
#        values = self.get_float_array(par, ignore_qf=exclude_qf)[index]
#        
#        
#        # First remove empty values and nan
#        missing_data_at_depth = []
#        depth_list = [] 
#        value_list = []
#        for d, v in zip(depths, values):
#            if not np.isnan(d) and not np.isnan(v):
#                depth_list.append(d) 
#                value_list.append(v)
#            else:
#                missing_data_at_depth.append(d)
#        
#        sum_list = []
#        if len(depth_list) >= min_nr_values:  
#            # Make sure to integrate the whole surface lager if selected
#            if depth_list[0] != depth_interval[0]:
#                depth_list.insert(0, depth_interval[0])
#                value_list.insert(0, value_list[0])
#            if depth_list[-1] != depth_interval[-1]:
#                depth_list.append(depth_interval[-1])
#                value_list.append(value_list[-1])
#            
#            for z0, z1, v0, v1 in zip(depth_list[:-1], depth_list[1:], 
#                                      value_list[:-1], value_list[1:]):
#                
#                part_sum = 0.5*(v1+v0)*(z1-z0)
#                
#                sum_list.append(part_sum)
#                
#            mean_value = sum(sum_list)/(depth_list[-1]-depth_list[0])
#        else:
#            if missing_value != None:
#                mean_value = missing_value
#            else:
#                mean_value = np.nan
#        
#        calculations = Calculations()
#        calculations.exclude_qf = exclude_qf
#        calculations.min_nr_values = min_nr_values
#        calculations.depth_interval = depth_interval
#        calculations.used_values = [round(v, 2) for v in value_list]
#        calculations.used_depths = depth_list
#        calculations.nr_values_used = len(calculations.used_values)
#        calculations.segments = sum_list
#        calculations.missing_data_at_depth = missing_data_at_depth
#        calculations.value = mean_value
#        
#        return calculations
    
    
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
        
        

    


if __name__ == '__main__':
    print('='*50)
    print('Running module "data_handler.py"')
    print('-'*50)
    print('')
    
#    
#    raw_data_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/raw_data/data_BAS_2000-2009.txt'
#    first_filter_directory = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filtered_data' 
    
    
    # Handler
#    raw_data = core.DataHandler('raw')
#    raw_data.add_txt_file(raw_data_file_path, data_type='column')
#    
    print('-'*50)
    print('done')
    print('-'*50)


    
    
    
    
    
    
    
    
    
    