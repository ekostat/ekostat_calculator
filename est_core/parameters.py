# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 16:07:18 2017

@author: a001985

Python3
""" 
import pandas as pd
import numpy as np
import datetime

import est_core     
import est_utils   

###############################################################################
class ParameterBase(object):
    """
    Base-class to describe and hold base information about Parameters. 
    """
    def __init__(self):
        self._initiate_attributes()
    
    #==========================================================================
    def _initiate_attributes(self): 
        self.data_holder = None # Dedicated for a DataHolder obejct. This is the source data. 
        
        self.data = None        # Dedicated for a pandas dataframe. Hold data to work with. 
        
        self.area = None        # Dedicated for a est_core.Area object 
        self.time = None        # Dedicated for a ext_core.Time object
        
        self.info = None        # Dedicated for a ParameterGetInformation object
        
        self.internal_name = ''
        self.display_name = ''
        self.unit = ''
        
        self.is_calculated = False
        
    #==========================================================================
    def set_data_handler(self, data_handler): 
        """
        Set data_handler to work with. 
        This is not the data that will be looked in by the get-methodes. 
        To create this data 
        Data might look different depending on the source. 
        """
        self.data_handler = data_handler 
        self.data_handler_source = data_handler.source 
        return True
        
    #==========================================================================
    def drop_data_handler(self): 
        self.data_handler = None 
        self.data_handler_source = None 
        
    #==========================================================================
    def drop_data(self): 
        self.data = None
        
    #==========================================================================
    def reset_all_data(self): 
        self.drop_data()
        self.drop_data_handler()
        
    #==========================================================================
    def filter_data(self, data_filter_object):
        self.data_filter_object = data_filter_object
#        print('filter_data')
#        print(data_filter_object.keys())
#        print('filter_data:', self.internal_name)
        data_filter_object.parameter = self.internal_name
        self.data = self.data_handler.filter_data(data_filter_object)
        # TODO: Check if all is ok 
        return True
        
    #==========================================================================
    def get_data(self, **kwargs): 
        """
        Loads data from DataHandler object self.data and returns result. 
        This method is overwritten in subclasses. 
        """
        if not self.data: 
            return    
        
    
    
    
###############################################################################
class ParameterBasePhysicalChemical(ParameterBase):
    """
    Base-class to describe and hold base information about PhysicalChemical Parameters. 
    """
    def __init__(self):
        super().__init__() 
       
#    #==========================================================================
#    def _get_closest_match_in_time(self, datetime_object=None, tolerance_filter=None, boolean=True, df=False):
#        """
#        Look for data in self.data.column_data if df not given
#        """ 
#        if not df:
#            df = self.data.column_data
#            
#        if not all([datetime_object, tolerance_filter]):
#            return None
#            
#        time_delta = (df['time'] - datetime_object).apply(abs)
#        min_time_delta = min(time_delta)
#        
#        if 'TIME_DELTA' in tolerance_filter and tolerance_filter['TIME_DELTA'].value < min_time_delta.seconds/3600:
#            print('No match: TIME_DELTA < %s' % (min_time_delta.seconds/3600.))
#            return None
#        
#        b = time_delta == min_time_delta
#        if boolean:
#            return b
#        else:
#            return df.loc[df.index[b], :]
            
    #==========================================================================
    def _get_closest_match_in_pos(self, lat=None, lon=None, tolerance_filter=None, boolean=True, df=False): 
        """
        
        """ 
        def calc_dist(x): 
            # First check if equal. Faster?
            if lat == x[0] and lon == x[1]:
                return 0
            return est_utils.latlon_distance([lat, lon], 
                                             [x[0], x[1]])
        
        if type(df) == bool:
            df = self.data.column_data
            
        if not all([lat, lon, tolerance_filter]):
            return None
        
        # Check match in position
        self.df = df
        dist_series = df[['latit_dec_deg', 'longi_dec_deg']].apply(calc_dist, axis=1)
        min_dist = min(dist_series)
        self.dist_series = dist_series
#        print('dist_series', dist_series)
#        print('=', tolerance_filter['POS_RADIUS'].value, type(tolerance_filter['POS_RADIUS'].value))
#        print('=', min_dist, type(min_dist))
        
        if 'POS_RADIUS' in tolerance_filter and tolerance_filter['POS_RADIUS'].value < min_dist:
            print('No match: POS_RADIUS < %s' % min_dist)
            return None
        
        b = dist_series == min_dist
        if boolean:
            return b
        else:
            return df.loc[df.index[b], :] 
        
        
    #==========================================================================
    def _get_closest_match_in_depth(self, depth=None, tolerance_filter=None, boolean=True, df=False): 
        """
        
        """         
        if type(df) == bool:
            df = self.data.column_data
            
        if not all([depth, tolerance_filter]):
            if depth == None:
                return None
        
        # Check match in position
        dist_depth = (df['DEPH'] - depth).apply(abs)
        min_dist = min(dist_depth)
        
        if 'DEPTH' in tolerance_filter and tolerance_filter['DEPTH'].value < min_dist:
            print('No match: DEPTH < %s' % min_dist)
            return None
        
        b = dist_depth == min_dist
        if boolean:
            return b
        else:
            return df.loc[df.index[b], :] 
            
    
    #==========================================================================
    def _get_all_match_in_time(self, datetime_object=None, tolerance_filter=None, boolean=True, df=False): 
        """
        Look for data in self.data.column_data if df not given
        """ 
        if type(df) == bool:
            df = self.data.column_data
            
        if not all([datetime_object, tolerance_filter]):
            return None
        
        time_delta = (df['time'] - datetime_object).apply(abs)
        self.time_delta = time_delta
#        print("time_delta", time_delta.head())
#        print("tolerance_filter['TIME_DELTA'].value", tolerance_filter['TIME_DELTA'].value)
        time_delta_hours = time_delta.apply(lambda x: x/np.timedelta64(1, 'h'))
        self.time_delta_hours = time_delta_hours
#        b = pd.Series([1 if (dt.seconds/3600) <= tolerance_filter['TIME_DELTA'].value else 0 for dt in time_delta], dtype=bool)
        b = time_delta_hours <= tolerance_filter['TIME_DELTA'].value
        if boolean:
            return b
        else:
            return df.loc[df.index[b], :]

    #==========================================================================
    def _get_all_match_in_pos(self, lat=None, lon=None, tolerance_filter=None, boolean=True, df=False): 
        """
        
        """ 
        def calc_dist(x): 
            # First check if equal. Faster?
            if lat == x[0] and lon == x[1]:
                return 0
            return est_utils.latlon_distance([lat, lon], 
                                             [x[0], x[1]])
        
        if type(df) == bool:
            df = self.data.column_data
            
        if not all([lat, lon, tolerance_filter]):
            return None
        
        # Check match in position
        dist_series = df[['latit_dec_deg', 'longi_dec_deg']].apply(calc_dist, axis=1)
        
        b = dist_series <= tolerance_filter['POS_RADIUS'].value
        if boolean:
#            print('¤'*50)
#            print(type(b))
#            print('¤'*50, b)
            return b
        else:
            return df.loc[df.index[b], :] 
        
    #==========================================================================
    def _get_all_match_in_depth(self, depth=None, tolerance_filter=None, boolean=True, df=False): 
        """
        
        """         
        if type(df) == bool:
            df = self.data.column_data
            
        if not all([depth, tolerance_filter]):
            if depth == None:
                return None
        
        # Check match in position
        dist_depth = (df['DEPH'] - depth).apply(abs)
        
        b = dist_depth <= tolerance_filter['DEPTH'].value
        if boolean:
            return b
        else:
            return df.loc[df.index[b], :] 
        
    #==========================================================================
    def _get_boolean_for_has_data(self): 
        return self.data.column_data[self.internal_name].apply(lambda x: 0 if np.isnan(x) else 1) == 1
  
    #==========================================================================
    def get_matching_data(self, df_row=pd.Series(), tolerance_filter=None): 
        """
        Returns the dataframe that matches the criteria given in tolerance_filter. 
        Several profiles can be matching here. 
        False is returned if no match. 
        """         
        if not all([len(df_row), tolerance_filter, self.data]):
            return None
        
        #----------------------------------------------------------------------
        # Check pos
        lat = df_row['latit_dec_deg']
        lon = df_row['longi_dec_deg']
        
        pos_boolean = self._get_all_match_in_pos(lat=lat, lon=lon, tolerance_filter=tolerance_filter, boolean=True) 
        if type(pos_boolean) == bool:
            return False
        
        #----------------------------------------------------------------------
        # Check time 
        datetime_object = df_row['time']
        time_boolean = self._get_all_match_in_time(datetime_object=datetime_object, tolerance_filter=tolerance_filter, boolean=True)
        
        if type(time_boolean) == bool:
            return False
        
        #----------------------------------------------------------------------
        # Check depth 
        depth = df_row['DEPH']
        depth_boolean = self._get_all_match_in_depth(depth=depth, tolerance_filter=tolerance_filter, boolean=True)
        
        if type(depth_boolean) == bool:
            return False
        
#        print('PASSED')
        #----------------------------------------------------------------------
        # Check value
        value_boolean = self._get_boolean_for_has_data()
        
#        print(type(pos_boolean), pos_boolean.head())
#        print(type(time_boolean), time_boolean.head())
#        print(type(depth_boolean), depth_boolean.head())
        self.pos_boolean = pos_boolean
        self.time_boolean = time_boolean
        self.depth_boolean = depth_boolean
        self.value_boolean = value_boolean
        
        boolean = pos_boolean & time_boolean & depth_boolean & value_boolean
        
        self.boolean = boolean
        
        if not any(boolean):
            return False
        
        return self.data.column_data.loc[self.data.column_data.index[boolean], :]

#        dh = est_core.DataHandler('matching_data')
#        dh.add_df(self.data.column_data.loc[self.data.column_data.index[boolean], :], 'col')
#        return dh
    
    #==========================================================================
    def get_closest_matching_data(self, df_row=[], tolerance_filter=None): 
        """
        Returns the pandas.DataFrame containing the closest profile that matches the 
        criteria given in tolerance_filter. 
        False is returned if no match. 
        """         
        if not all([len(df_row), tolerance_filter]):
            return None
        
        # First get a dataframe that matches ALL the criteria given in tolerance_filter. 
        df = self.get_matching_data(df_row=df_row, tolerance_filter=tolerance_filter) 
        if type(df) == bool:
            return pd.Series()
        
        # We have found one or several mathing "values"
        # Now check the profile that is closest in position.  
        lat = df_row['latit_dec_deg']
        lon = df_row['longi_dec_deg']
        prof_df = self._get_closest_match_in_pos(lat=lat, 
                                                 lon=lon, 
                                                 tolerance_filter=tolerance_filter, 
                                                 boolean=False, 
                                                 df=df)
        self.prof_df = prof_df
        
        # prof_df contains the closest valid profile. Now get the value for the specific depth. 
        depth = df_row['DEPH']
        depth_df = self._get_closest_match_in_depth(depth=depth, tolerance_filter=tolerance_filter, boolean=False, df=prof_df)
        
        if type(depth_df) == pd.DataFrame:
            # Several rows might be found here if depht tolerance is large enough. 
            # Regardless, we return the first Series in the DataFrame. 
            depth_df = depth_df.loc[depth_df.index[0],:]
        self.depth_df = depth_df
        return depth_df 
        
        
    #==========================================================================
    def get_index_list(self):
        """
        Returns a list of the index in self.data. 
        """
        return self.data.column_data.index
    
    #==========================================================================
    def get_df_row_for_index(self, index): 
        return self.data.column_data.loc[index, :]
    
    #==========================================================================
    def get_station_list(self):
        """
        Returns a list of all stations that has data of the current parameter (self.internal_name). 
        """
        if not self.internal_name or not self.data:
            return False
        
        # TODO: Does this work for row data as well?
        return sorted(set(self.data.column_data.loc[self.data.index[~self.data[self.internal_name].isnull()], 'STATN']))
        
    #==========================================================================
    def get_profile_key_list(self, year=None):
        """
        Returns a list och unique combinations of pos and time. 
        """
        return self.data.get_profile_key_list(year=year)
    
    #==========================================================================
    def get_index_for_profile_key(self, profile_key):
        """
        Method to get index for a unique profile key. 
        profile_key is "time LATIT LONGI"
        """ 
        return self.data.get_index_for_profile_key(profile_key)

        
###############################################################################
class CalculatedParameterPhysicalChemical(ParameterBasePhysicalChemical):
    """
    Class to describe and hold information about calculated PhysicalChemical Parameters. 
    """
    def __init__(self):
        super().__init__() 
        self.is_calculated = True
        
###############################################################################
class CalculatedParameterDIN(CalculatedParameterPhysicalChemical):
    """
    Class to describe and handle DIN. 
    Parameter is calculated once the object is created. 
    """
    def __init__(self, ntra=None, ntri=None, amon=None):
        super().__init__()
        
        self.internal_name = 'DIN'
        self.external_name = 'Dissolved inorganic nitrogen' 
        self.unit = 'umol/l' 
        
        self.ntra = ntra
        self.ntri = ntri 
        self.amon = amon 
        
        if all([ntra, ntri, amon]):
            self._calculate_din()
        
    #==========================================================================
    def _calculate_din(self):
        
        #----------------------------------------------------------------------
        # Merge ntra, ntri and amon on index 
        # All data is found in column data
        ntra = pd.Series(self.ntra.column_data.loc[:, 'NTRA']) 
        ntri = pd.Series(self.ntri.column_data.loc[:, 'NTRI']) 
        amon = pd.Series(self.amon.column_data.loc[:, 'AMON']) 
        df = pd.DataFrame({'NTRA':ntra, 'NTRI':ntri, 'AMON':amon})
        
        #----------------------------------------------------------------------
        # Calculate DIN 
        # TODO: Where do we exclude qf and should we look at H2S? 
        din_list = []
        for no3, no2, nh4 in zip(df['NTRA'], df['NTRI'], df['AMON']): 
            din = np.nan
            if not np.isnan(no3):
                din = no3
                if not np.isnan(no2):
                    din += no2
                if not np.isnan(nh4):
                    din += nh4
            din_list.append(din)
        
        df_din = pd.DataFrame({'DIN':din_list}, index=df.index) 
        
        # Use data handler for NTRA as base for the DIN data handler
        din_df = self.ntra.column_data.copy(deep=True)
        new_df = pd.concat([din_df, df_din], axis=1)
#        new_df = pd.concat([self.ntra.column_data, df_din], axis=1)
        
        
        #----------------------------------------------------------------------
        # Create data handler and add df 
        # self.data will be a copy of self.data_handler 
        self.data_handler = est_core.DataHandler('calculated_din')
        self.data_handler.add_df(new_df, 'col')
        
        self.data = est_core.DataHandler('calculated_din')
        self.data.add_df(new_df, 'col') 
            
###############################################################################
class ParameterDIN(ParameterBasePhysicalChemical):
    """
    Class to describe and handle Nitrate. 
    """
    def __init__(self):
        super().__init__()
        
        self.internal_name = 'DIN'
        self.external_name = 'Dissolved inorganic nitrogen' 
        self.unit = 'umol/l' 
        
###############################################################################
class ParameterNTRA(ParameterBasePhysicalChemical):
    """
    Class to describe and handle Nitrate. 
    """
    def __init__(self):
        super().__init__()
        
        self.internal_name = 'NTRA'
        self.external_name = 'Nitrate' 
        self.unit = 'umol/l'
        
###############################################################################
class ParameterNTRI(ParameterBasePhysicalChemical):
    """
    Class to describe and handle Nitrite. 
    """
    def __init__(self):
        super().__init__()
        
        self.internal_name = 'NTRI'
        self.external_name = 'Nitrite' 
        self.unit = 'umol/l'
        
###############################################################################
class ParameterAMON(ParameterBasePhysicalChemical):
    """
    Class to describe and handle Ammonium. 
    """
    def __init__(self):
        super().__init__()
        
        self.internal_name = 'AMON'
        self.external_name = 'Ammonium' 
        self.unit = 'umol/l'
        
###############################################################################
class ParameterTN(ParameterBasePhysicalChemical):
    """
    Class to describe and handle Ammonium. 
    """
    def __init__(self):
        super().__init__()
        
        self.internal_name = 'NTOT'
        self.external_name = 'Total nitrogen' 
        self.unit = 'umol/l'
        
###############################################################################
class ParameterSALT_CTD(ParameterBasePhysicalChemical):
    """
    Class to describe and handle Ammonium. 
    """
    def __init__(self):
        super().__init__()
        
        self.internal_name = 'SALT_CTD'
        self.external_name = 'Salinity' 
        self.unit = 'psu'



###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "parameters.py"')
    print('-'*50)
    print('')
    
    est_core.ParameterList()
    
    raw_data_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/raw_data/data_BAS_2000-2009.txt'
    
    first_data_filter_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filters/first_data_filter.txt'
    first_filter = est_core.DataFilter('First filter', file_path=first_data_filter_file_path)
    
    winter_data_filter_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filters/winter_data_filter.txt'
    winter_filter_1 = est_core.DataFilter('winter_filter', file_path=winter_data_filter_file_path)
    
    tolerance_filter_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filters/tolerance_filter_template.txt'
    tolerance_filter = est_core.ToleranceFilter('test_tolerance_filter', file_path=tolerance_filter_file_path)
    
    raw_data = est_core.DataHandler('raw')
    raw_data.add_txt_file(raw_data_file_path, data_type='column') 
    
    filtered_data = raw_data.filter_data(first_filter)
    
    
    tn = ParameterTN()
    tn.set_data_handler(filtered_data)
    tn.filter_data(winter_filter_1)
    
    df_row = pd.Series(tn.get_df_row_for_index(0))
    
    t = pd.Timestamp(datetime.datetime(2000, 1, 17, 9))
    df_row['time'] = t
    
#    m = tn._get_closest_match_in_time(datetime_object=t, tolerance_filter=tolerance_filter)
    
    value_row = tn.get_closest_matching_data(df_row=df_row, tolerance_filter=tolerance_filter) 
    
    if type(value_row) != bool:
        print('='*50)
#        print(value_row.name)
        print('TIME', t)
        print('-'*50)
        for col in sorted(value_row.index):
            print(col.ljust(20), value_row[col])
    #    print('VALUE:', value_row)
        print('-'*50)
    else:
        print('No match')
    
    
    