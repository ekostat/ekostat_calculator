# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 08:10:06 2017

@author: a002028
"""

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
sys.path.append(current_path)

import pandas as pd
import numpy as np
import time

import utils
import core

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
        self._organize_data_format()
    
    #==========================================================================
    def _calculate_data(self):
        """ Can be overwritten from child """
        pass
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
        Can be rewritten in child-class, eg. DataHandlerPhytoplankton
        """
        self.source = file_path
        self.raw_data_copy = raw_data_copy
        self.df = core.Load().load_txt(file_path, sep=sep, encoding=encoding, fill_nan=u'')
        self._remap_header()
        self._recognize_format()
        self._apply_field_filter()

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
    def __init__(self, filter_path=u'', 
                 export_directory='',
                 parameter_mapping=None):
        
        super().__init__()
        self.dtype = u'PhysicalChemical'
        self.export_directory = export_directory
        self.read_filter_file(file_path=filter_path)
        self.parameter_mapping = parameter_mapping
        
        self.column_data = {} #pd.DataFrame()
        self.row_data = {} #pd.DataFrame()

    #==========================================================================
    def _calculate_data(self):
        """ Rewritten from parent """
        self.calculate_din()
        
    #==========================================================================
    def calculate_din(self, ignore_qf_list=['B','S']):
        """ 
        Returns a vector calculated DIN. 
        If NO3 is not present value is np.nan 
        """
        din_list = []
        for no2, no3, nox, nh4 in zip(self.get_float_list(key=u'NTRI', ignore_qf=ignore_qf_list), 
                                      self.get_float_list(key=u'NTRA', ignore_qf=ignore_qf_list), 
                                      self.get_float_list(key=u'NTRZ', ignore_qf=ignore_qf_list),
                                      self.get_float_list(key=u'AMON', ignore_qf=ignore_qf_list)):

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
        return utils.get_float_list_from_str(df=self.column_data[self.source], 
                                             key=key, ignore_qf=ignore_qf)
    
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
        self.dtype = u'Zoobenthos'
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
        self.dtype = u'Chlorophyll' # Only Tube samples ? 
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
        self.dtype = u'Phytoplankton'
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
        # keys could be set in filter_parameters instead..
#        print(self.df.get(samp_key).unique)
        for sample in self.df.get(samp_key).unique():
            
            boolean = utils.set_filter(df=self.df, 
                                       filter_dict={samp_key:sample})
            
            tot_value = self.df.loc[boolean,self.filter_parameters.value_key].astype(np.float).sum(skipna=True)
            
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
        
        
        self.physical_chemical = DataHandlerPhysicalChemical(filter_path=path_fields_filter+'filter_fields_physical_chemical.txt',
                                                             export_directory=self.export_directory,
                                                             parameter_mapping=self.parameter_mapping)
        
        
        self.phytoplankton = DataHandlerPhytoplankton(filter_path=path_fields_filter+u'filter_fields_phytoplankton.txt',
                                                      export_directory=self.export_directory,
                                                      parameter_mapping=self.parameter_mapping)
        
        
        self.zoobenthos = DataHandlerZoobenthos(filter_path=path_fields_filter+'filter_fields_zoobenthos.txt',
                                                export_directory=self.export_directory,
                                                parameter_mapping=self.parameter_mapping)
        
        
        self.all_data = None

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
        - Do we need to sort all_data ?
        - Merge data from different datatypes for the same visit ?
        """
        self.all_data = pd.DataFrame()
        
        # All datatypes that might include data for setting ecological status
        all_datatypes = [u'chlorophyll',
                         u'physical_chemical',
                         u'phytoplankton',
                         u'zoobenthos']
        
        for dtype in all_datatypes:
            if dtype in dir(self):
                # Appends dataframes from each datatype into one dataframe
                for source in self.__getattribute__(dtype).column_data:
                    # Each datatype might have multiple sources..
                    # .column_data is a dict
                    self.all_data = self.all_data.append(self.__getattribute__(dtype).column_data[source], 
                                                         ignore_index=True)
        
        # MW: Add mont column 
        self.all_data['MONTH'] = self.all_data['SDATE'].apply(lambda x: int(x[5:7]))
        
        if save_to_txt:
            self.save_data(df=self.all_data, 
                           file_name='all_data.txt')
            
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
    def save_data(self, df=None, directory=u'', file_name=u''):
        
        if not directory: 
            directory = self.export_directory
#            directory = os.path.dirname(os.path.realpath(__file__))[:-4] + 'test_data\\test_exports\\'
            
        if not directory.endswith(('/','\\')):
            directory = directory + '/'
        
        file_path = directory + file_name
        
        print(u'Saving data to:',file_path)
        
        df.to_csv(file_path, sep='\t', encoding='cp1252', index=True)
        
#        column_file_path = directory + '/column_data.txt'
#        self.column_data.to_csv(column_file_path, sep='\t', encoding='cp1252', index=False)
#        
#        row_file_path = directory + '/row_data.txt'
#        self.row_data.to_csv(row_file_path, sep='\t', encoding='cp1252', index=False)
    
    #==========================================================================

if __name__ == '__main__':
    print('='*50)
    print('Running module "data_handler.py"')
    print('-'*50)
    print('')
    
    raw_data_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/raw_data/data_BAS_2000-2009.txt'
    first_filter_directory = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filtered_data' 
    
    
    # Handler
#    raw_data = core.DataHandler('raw')
#    raw_data.add_txt_file(raw_data_file_path, data_type='column')
    
    print('-'*50)
    print('done')
    print('-'*50)


    
    
    
    
    
    
    
    
    
    