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
#        print('filter_data')
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
        
    #==========================================================================
    def get_closest_profile_in_time(self, datetime_object=None, tolerance_filter=None):
        # Look for data in self.data.column_data
        if not all([datetime_object, tolerance_filter, self.data]):
            return None
        
        time_delta = (self.data.column_data['TIME'] - datetime_object).apply(abs)
        min_time_delta = min(time_delta)
        
        if 'TIME_DELTA' in tolerance_filter and tolerance_filter['TIME_DELTA'] < min_time_delta.seconds/3600:
            print('TIME_DELTA < %s' % min_time_delta.seconds/3600)
            return None

        boolean = time_delta == min_time_delta
        return self.data.column_data.loc[self.data.column_data.index[boolean], :]
        
    #==========================================================================
    def get_data(self, **kwargs): 
        if not self.data:
            return False
        
        

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
class ParameterSALT(ParameterBasePhysicalChemical):
    """
    Class to describe and handle Ammonium. 
    """
    def __init__(self):
        super().__init__()
        
        self.internal_name = 'SALT'
        self.external_name = 'Salinity' 
        self.unit = 'psu'



###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "parameters.py"')
    print('-'*50)
    print('')
    
    
    
    
    
    
    