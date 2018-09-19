# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:24:34 2017

@author: a001985
"""
import numpy as np
import pandas as pd
import warnings
import random
import time

import core 

###############################################################################
def timer(func):
    """
    Created     20180719    by Magnus Wenzer
        
    """
    def f(*args, **kwargs):
        from_time = time.time()
        rv = func(*args, **kwargs)
        to_time = time.time()
        print('"{.__name__}". Time for running method was {}'.format(func, to_time-from_time))
        return rv
    return f

###############################################################################
class ClassificationResult(dict):
    """
    Class to hold result from a classification. 
    """ 
    def __init__(self):
        super().__init__() 
        
        self['parameter'] = None 
        self['salt_parameter'] = None
        self['indicator'] = None
        self['all_data'] = None
        self['all_ok'] = False
        self['status_by_date'] = None#pd.DataFrame(columns = ['VISS_EU_CD', 'WATER_TYPE_AREA','SDATE', 'STATUS', 'REF VALUE', 'local_EQR','global_EQR'])
        self['status_by_year'] = None#pd.DataFrame(columns = ['VISS_EU_CD', 'WATER_TYPE_AREA','YEAR', 'STATUS', 'REF VALUE', 'local_EQR', 'global_EQR', 'Number of DATES', 'MONTHS INCLUDED'])
        self['status_by_period'] = None#pd.DataFrame(columns = ['VISS_EU_CD', 'WATER_TYPE_AREA','PERIOD', 'STATUS', 'global_EQR', 'Number of YEARS', 'YEARS INCLUDED'])
        
        self._set_attributes()
        
    #========================================================================== 
    def _set_attributes(self):
        for key in self.keys():
            setattr(self, key, self[key])
            
    #========================================================================== 
    def add_info(self, key, value): 
        try:
            existing_value = getattr(self, key)
#            if getattr(self, key) != value:
#                raise('Error: Trying to set new value to existing attribute. new value {} does not match old value {} for attribute {}'.format(value, existing_value, key))
        except AttributeError:
            #Varför både nyckel och attribut?
            self[key] = value
            setattr(self, key, value)
        

###############################################################################
class IndicatorBase(object): 
    """
    Class to calculate status for a specific indicator. 
    """ 
    def __init__(self, subset_uuid, parent_workspace_object, indicator):
        """
        setup indicator class attributes based on subset, parent workspace object and indicator name
        """
        self.name = indicator.lower()
        print('****INITIATING INDICATOR OBJECT FOR****')
        print(self.name)
        self.class_result = None
        self.subset = subset_uuid
        self.step = 'step_3'
        # from workspace
        self.parent_workspace_object = parent_workspace_object
        self.mapping_objects = self.parent_workspace_object.mapping_objects
        self.index_handler = self.parent_workspace_object.index_handler
        self.step_object = self.parent_workspace_object.get_step_object(step = 3, subset = self.subset)
        # from SettingsFile
        self.tolerance_settings = self.parent_workspace_object.get_step_object(step = 2, subset = self.subset).get_indicator_tolerance_settings(self.name)
        self.ref_settings = self.parent_workspace_object.get_step_object(step = 2, subset = self.subset).get_indicator_ref_settings(self.name)
        # To be read from config-file
        # TODO: Add 'ALABO' and 'TEMP'
        self.meta_columns = ['SDATE', 'YEAR', 'MONTH', 'STIME', 'POSITION', 'STATN', 'VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_DISTRICT',
       'WATER_TYPE_AREA', 'DEPH', 'RLABO', 'WADEP']
        self.parameter_list =  [item.strip() for item in self.mapping_objects['quality_element'].indicator_config.loc[self.name]['parameters'].split(', ')] #[item.strip() for item in self.parent_workspace_object.cfg['indicators'].loc[self.name][0].split(', ')]
        self.additional_parameter_list = []
        if type(self.mapping_objects['quality_element'].indicator_config.loc[self.name]['additional_parameters']) is str:
            self.additional_parameter_list =  [item.strip() for item in self.mapping_objects['quality_element'].indicator_config.loc[self.name]['additional_parameters'].split(', ')] #[item.strip() for item in self.parent_workspace_object.cfg['indicators'].loc[self.name][0].split(', ')]
        else:
            self.additional_parameter_list = []
        self.direction_good = self.mapping_objects['quality_element'].indicator_config.loc[self.name]['direction_good']
        self.column_list = self.meta_columns + self.parameter_list + self.additional_parameter_list
        #print(self.column_list)
        self.indicator_parameter = self.parameter_list[0]
        # attributes that will be calculated
        self.water_body_indicator_df = {}
#        self.classification_results = ClassificationResult()
        # perform checks before continuing
        self._check()
        self._set_directories()
        #paths and saving
        self.result_directory = self.step_object.paths['step_directory']+'/output/results/'
        self.sld = core.SaveLoadDelete(self.result_directory)        
        
    def _check(self):
        
        try:
            variable = self.tolerance_settings.allowed_variables[0]
            self.tolerance_settings.get_value(variable = variable, type_area = '1s')
        except AttributeError as e:
            raise AttributeError('Tolerance settings for indicator {} not in place. \n{}'.format(self.name, e))
        try:
            variable = self.ref_settings.allowed_variables[0]
            self.ref_settings.get_value(variable = variable, type_area = '1s')
        except AttributeError as e:
            raise AttributeError('Reference value settings for indicator {} not in place. \n{}'.format(self.name, e))
            
         
    #==========================================================================
    def _set_directories(self):
        #set paths
        self.paths = {}
        self.paths['output'] = self.step_object.paths['directory_paths']['output'] 
        self.paths['results'] = self.step_object.paths['directory_paths']['results']
    #==========================================================================
    def _add_wb_name_to_df(self, df, water_body):
        
        try:
            df['WATER_BODY_NAME'] = self.mapping_objects['water_body'][water_body]['WATERBODY_NAME']
        except AttributeError:
            df['WATER_BODY_NAME'] = 'unknown'
            print('waterbody matching file does not recognise water body with VISS_EU_CD {}'.format(water_body))
        
    #==========================================================================
    def _add_reference_value_to_df(self, df, water_body):    
        """
        Created:        20180426     by Lena
        Last modified:  
        add reference value to dataframe
        Nutrient reference values: Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vidvarje enskilt prov.
        Chl, Biov, Secchi in type 8, 12, 13, 24: Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vidvarje enskilt prov.
        """
        #print(water_body,len(self.ref_settings.settings.refvalue_column))
        if len(self.ref_settings.settings.refvalue_column) == 0:
            return df
        
        #print(self.get_ref_value_type(water_body = water_body))
        if self.get_ref_value_type(water_body = water_body) == 'str':
            #print('ref_value is str')
#            df.loc[:,'REFERENCE_VALUE'] = np.nan
            reference_values = []
            #print(df.VISS_EU_CD.unique())
            for ix in df.index:
                salinity = df[self.salt_parameter][ix]
#                #print(repr(salinity))
#                #if np.isnan(salinity):
#                #    df['REFERENCE_VALUE'].loc[ix] = np.nan
#                #else:
                reference_values.append(self.get_boundarie(water_body = water_body, salinity = salinity))
#                df['REFERENCE_VALUE'].loc[ix] = self.get_ref_value(water_body = water_body, salinity = salinity)
#            df['REFERENCE_VALUE'] = reference_values
            df.loc[:,'REFERENCE_VALUE'] = pd.Series(reference_values, index = df.index)
        else:
            df.loc[:,'REFERENCE_VALUE'] = self.get_ref_value(water_body)
                                    
        return df
    
    #==========================================================================
    def _add_boundaries_to_df(self, df, water_body):    
        """
        Created:        20180426     by Lena
        Last modified:  
        add reference value to dataframe
        Nutrient reference values: Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vidvarje enskilt prov.
        Chl, Biov, Secchi in type 8, 12, 13, 24: Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vidvarje enskilt prov.
        """
#         print('add_boundaries')
        #print(water_body,len(self.ref_settings.settings.refvalue_column))
        if len(self.ref_settings.settings.refvalue_column) == 0:
            return df

        #print(self.get_ref_value_type(water_body = water_body))
        if self.get_ref_value_type(water_body = water_body) == 'str':
            #print('ref_value is str')
#            df.loc[:,'REFERENCE_VALUE'] = np.nan
#             reference_values = []
#             hg_values = []
#             gm_values = []
#             mp_values = []
#             pb_values = []
#             print('this is where the SettingWithCopyWarning i raised')
            df.loc[:,'REFERENCE_VALUE'] = df[[self.salt_parameter, 'VISS_EU_CD']].apply(lambda x: self.get_boundarie(water_body = x['VISS_EU_CD'], salinity = x[self.salt_parameter], variable = 'REF_VALUE_LIMIT'), axis=1)
#             df.loc[:,'HG_VALUE_LIMIT'] = df[[self.salt_parameter, 'VISS_EU_CD']].apply(lambda x: self.get_boundarie(water_body = x['VISS_EU_CD'], salinity = x[self.salt_parameter], variable = 'HG_VALUE_LIMIT'), axis=1)
#             df.loc[:,'GM_VALUE_LIMIT'] = df[[self.salt_parameter, 'VISS_EU_CD']].apply(lambda x: self.get_boundarie(water_body = x['VISS_EU_CD'], salinity = x[self.salt_parameter], variable = 'GM_VALUE_LIMIT'), axis=1)
#             df.loc[:,'MP_VALUE_LIMIT'] = df[[self.salt_parameter, 'VISS_EU_CD']].apply(lambda x: self.get_boundarie(water_body = x['VISS_EU_CD'], salinity = x[self.salt_parameter], variable = 'MP_VALUE_LIMIT'), axis=1)
#             df.loc[:,'PB_VALUE_LIMIT'] = df[[self.salt_parameter, 'VISS_EU_CD']].apply(lambda x: self.get_boundarie(water_body = x['VISS_EU_CD'], salinity = x[self.salt_parameter], variable = 'PB_VALUE_LIMIT'), axis=1)
            
            if self.direction_good == 'positive':
                df.loc[:,'HG_VALUE_LIMIT'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']*self.ref_settings.get_value(variable = 'HG_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
                df.loc[:,'GM_VALUE_LIMIT'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']*self.ref_settings.get_value(variable = 'GM_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
                df.loc[:,'MP_VALUE_LIMIT'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']*self.ref_settings.get_value(variable = 'MP_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
                df.loc[:,'PB_VALUE_LIMIT'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']*self.ref_settings.get_value(variable = 'PB_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
            elif self.direction_good == 'negative':
                df.loc[:,'HG_VALUE_LIMIT'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']/self.ref_settings.get_value(variable = 'HG_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
                df.loc[:,'GM_VALUE_LIMIT'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']/self.ref_settings.get_value(variable = 'GM_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
                df.loc[:,'MP_VALUE_LIMIT'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']/self.ref_settings.get_value(variable = 'MP_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
                df.loc[:,'PB_VALUE_LIMIT'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']/self.ref_settings.get_value(variable = 'PB_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
 
            
#             df.loc[:,'HG_BOUNDARIE_VALUE'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']*self.ref_settings.get_value(variable = 'HG_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
#             df.loc[:,'GM_BOUNDARIE_VALUE'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']*self.ref_settings.get_value(variable = 'GM_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
#             df.loc[:,'MP_BOUNDARIE_VALUE'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']*self.ref_settings.get_value(variable = 'MP_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)
#             df.loc[:,'PB_BOUNDARIE_VALUE'] = df[['REFERENCE_VALUE', 'VISS_EU_CD']].apply(lambda x: x['REFERENCE_VALUE']*self.ref_settings.get_value(variable = 'PB_EQR_LIMIT', water_body = x['VISS_EU_CD']), axis=1)

#             df.loc[:,'GM_BOUNDARIE'] = pd.Series(gm_values, index = df.index)
#             df.loc[:,'MP_BOUNDARIE'] = pd.Series(mp_values, index = df.index)
#             df.loc[:,'PB_BOUNDARIE'] = pd.Series(pb_values, index = df.index)
#             for ix in df.index:
#                 salinity = df[self.salt_parameter][ix]
# #                #print(repr(salinity))
# #                #if np.isnan(salinity):
# #                #    df['REFERENCE_VALUE'].loc[ix] = np.nan
# #                #else:
#                 ref_value = self.get_boundarie(water_body = water_body, salinity = salinity, variable = 'REF_VALUE_LIMIT')
#                 reference_values.append(ref_value)
#                 hg_values.append(ref_value*self.ref_settings.get_value(variable = 'HG_EQR_LIMIT', water_body = water_body))
#                 gm_values.append(ref_value*self.ref_settings.get_value(variable = 'GM_EQR_LIMIT', water_body = water_body))
#                 mp_values.append(ref_value*self.ref_settings.get_value(variable = 'MP_EQR_LIMIT', water_body = water_body))
#                 pb_values.append(ref_value*self.ref_settings.get_value(variable = 'PB_EQR_LIMIT', water_body = water_body))
# #                hg_values.append(self.get_boundarie(water_body = water_body, salinity = salinity, variable = 'HG_VALUE_LIMIT'))
# #                gm_values.append(self.get_boundarie(water_body = water_body, salinity = salinity, variable = 'GM_VALUE_LIMIT'))
# #                mp_values.append(self.get_boundarie(water_body = water_body, salinity = salinity, variable = 'MP_VALUE_LIMIT'))
# #                pb_values.append(self.get_boundarie(water_body = water_body, salinity = salinity, variable = 'PB_VALUE_LIMIT'))
# #                df['REFERENCE_VALUE'].loc[ix] = self.get_ref_value(water_body = water_body, salinity = salinity)
# #            df['REFERENCE_VALUE'] = reference_values
#             df.loc[:,'REFERENCE_VALUE'] = pd.Series(reference_values, index = df.index)
#             df.loc[:,'HG_BOUNDARIE'] = pd.Series(hg_values, index = df.index)
#             df.loc[:,'GM_BOUNDARIE'] = pd.Series(gm_values, index = df.index)
#             df.loc[:,'MP_BOUNDARIE'] = pd.Series(mp_values, index = df.index)
#             df.loc[:,'PB_BOUNDARIE'] = pd.Series(pb_values, index = df.index)
        else:
            ref_value = self.get_boundarie(water_body, variable = 'REF_VALUE_LIMIT')
            df.loc[:,'REFERENCE_VALUE'] = ref_value
#             df.loc[:,'HG_BOUNDARIE_VALUE'] = self.ref_settings.get_value(variable = 'HG_EQR_LIMIT', water_body = water_body)
#             df.loc[:,'GM_BOUNDARIE_VALUE'] = self.ref_settings.get_value(variable = 'GM_EQR_LIMIT', water_body = water_body)
#             df.loc[:,'MP_BOUNDARIE_VALUE'] = self.ref_settings.get_value(variable = 'MP_EQR_LIMIT', water_body = water_body)
#             df.loc[:,'PB_BOUNDARIE_VALUE'] = self.ref_settings.get_value(variable = 'PB_EQR_LIMIT', water_body = water_body)
            if self.direction_good == 'positive':
                df.loc[:,'HG_VALUE_LIMIT'] = ref_value*self.get_boundarie(water_body, variable = 'HG_VALUE_LIMIT')
                df.loc[:,'GM_VALUE_LIMIT'] = ref_value*self.get_boundarie(water_body, variable = 'GM_VALUE_LIMIT')
                df.loc[:,'MP_VALUE_LIMIT'] = ref_value*self.get_boundarie(water_body, variable = 'MP_VALUE_LIMIT')
                df.loc[:,'PB_VALUE_LIMIT'] = ref_value*self.get_boundarie(water_body, variable = 'PB_VALUE_LIMIT')
            elif self.direction_good == 'negative':
                df.loc[:,'HG_VALUE_LIMIT'] = ref_value/self.get_boundarie(water_body, variable = 'HG_VALUE_LIMIT')
                df.loc[:,'GM_VALUE_LIMIT'] = ref_value/self.get_boundarie(water_body, variable = 'GM_VALUE_LIMIT')
                df.loc[:,'MP_VALUE_LIMIT'] = ref_value/self.get_boundarie(water_body, variable = 'MP_VALUE_LIMIT')
                df.loc[:,'PB_VALUE_LIMIT'] = ref_value/self.get_boundarie(water_body, variable = 'PB_VALUE_LIMIT')
                                    
#        return df

    #==========================================================================
    def _calculate_global_EQR_from_indicator_value(self, water_body = None, value = None, max_value = None, min_value = 0, **kwargs):
        """
        Calculates EQR from local_EQR values according to eq. 1 in WATERS final report p 153.
        Boundaries for all classes are read from RefSettings object
        boundarie_variable is used to retrieve class boundaries from settings file and must match the type of value
        This is only valid for values with increasing quality (higher value = higher EQR)
        """
        if not value:
            return False, False
        
        if np.isnan(value):
            global_EQR = np.nan
            status = ' '
            return global_EQR, status
        
        if value < 0:
            raise('Error: _calculate_global_EQR_from_indicator_value: {} value below 0.'.format(value))
        # Get EQR-class limits for the type area to be able to calculate the weighted numerical class
        def select_source(kwargs, key):
            if key in kwargs.keys():
                return kwargs[key]
            else:
                return self.ref_settings.get_value(variable = key, water_body = water_body)
        
        if 'REF_VALUE_LIMIT' in kwargs.keys():
            REF_VALUE = kwargs['REF_VALUE_LIMIT']
        else:
            REF_VALUE = self.ref_settings.get_ref_value(water_body = water_body)
            
        HG_VALUE_LIMIT = select_source(kwargs, 'HG_VALUE_LIMIT')
        GM_VALUE_LIMIT = select_source(kwargs, 'GM_VALUE_LIMIT')
        MP_VALUE_LIMIT = select_source(kwargs, 'MP_VALUE_LIMIT')
        PB_VALUE_LIMIT = select_source(kwargs, 'PB_VALUE_LIMIT')

#        HG_VALUE_LIMIT = self.ref_settings.get_value(variable = 'HG_VALUE_LIMIT', water_body = water_body)
#        GM_VALUE_LIMIT = self.ref_settings.get_value(variable = 'GM_VALUE_LIMIT', water_body = water_body)
#        MP_VALUE_LIMIT = self.ref_settings.get_value(variable = 'MP_VALUE_LIMIT', water_body = water_body)
#        PB_VALUE_LIMIT = self.ref_settings.get_value(variable = 'PB_VALUE_LIMIT', water_body = water_body)
        if not max_value:
            max_value = REF_VALUE
        
#        if self.name == 'BQI'  or self.name.lower() == 'oxygen':
        if HG_VALUE_LIMIT - GM_VALUE_LIMIT > 0:
            slope = 0.2
            if value > HG_VALUE_LIMIT: 
                status = 'HIGH'
                global_low = 0.8 
                high_value = max_value #REF_VALUE #This should be the highest value possible
                low_value = HG_VALUE_LIMIT
                
            elif value > GM_VALUE_LIMIT:
                status = 'GOOD'
                global_low = 0.6 
                high_value = HG_VALUE_LIMIT
                low_value = GM_VALUE_LIMIT
    
            elif value > MP_VALUE_LIMIT:
                status = 'MODERATE'
                global_low = 0.4 
                high_value = GM_VALUE_LIMIT
                low_value = MP_VALUE_LIMIT
                
            elif value > PB_VALUE_LIMIT:
                status = 'POOR'
                global_low = 0.2 
                high_value = MP_VALUE_LIMIT
                low_value = PB_VALUE_LIMIT
                
            else:
                status = 'BAD'
                global_low = 0 
                high_value = PB_VALUE_LIMIT
                low_value = 0
                
        else:
            slope = -0.2
            # When higher value means lower status (decreasing)
            if value > PB_VALUE_LIMIT:
                status = 'BAD'
                global_low = 0.2
                high_value = 1
                # om värde ist för ek ska ek_high vara ref_värdet eller Bmax värde
                low_value = PB_VALUE_LIMIT
                if value > max_value:
                    value = max_value
                
            elif value > MP_VALUE_LIMIT:
                status = 'POOR'
                global_low = 0.4 
                high_value = PB_VALUE_LIMIT
                low_value = MP_VALUE_LIMIT
                
            elif value > GM_VALUE_LIMIT:
                status = 'MODERATE'
                global_low = 0.6 
                high_value = MP_VALUE_LIMIT
                low_value = GM_VALUE_LIMIT

            elif value > HG_VALUE_LIMIT:
                status = 'GOOD'
                global_low = 0.8 
                high_value = GM_VALUE_LIMIT
                low_value = HG_VALUE_LIMIT
                
            else:
                status = 'HIGH'
                global_low = 1
                high_value = HG_VALUE_LIMIT 
                low_value = 0
                if value < 0:
                    value = 0
            #global_EQR = global_low + (ek - ek_low)/(ek_high-ek_low)*-0.2      
                    
#        print('******',REF_VALUE,'******')
#        print('-------', HG_VALUE_LIMIT - GM_VALUE_LIMIT , '-------')
#        print(global_low, value, low_value, high_value)
        # Weighted numerical class
        global_EQR = global_low + (value - low_value)/(high_value-low_value)*slope
        
        return global_EQR, status
    
#        self.classification_results[water_body].add_info('global_EQR', global_EQR)
#        self.classification_results[water_body].add_info('status', status)
    
    
    
    #==========================================================================
    def _calculate_global_EQR_from_local_EQR(self, local_EQR, water_body):
        """
        Calculates EQR from local_EQR values according to eq. 1 in WATERS final report p 153.
        Boundaries for all classes are read from RefSettings object
        boundarie_variable is used to retrieve class boundaries from settings file and must match the type of local_EQR_variable
        """
#        if not local_EQR:
#            local_EQR = getattr(self.classification_results[water_body], 'local_EQR')
#        else:
#            self.classification_results[water_body].add_info('local_EQR', local_EQR)
#       
        if np.isnan(local_EQR):
            global_EQR = np.nan
            status = ''
            return global_EQR, status
        if local_EQR < 0:
            raise Exception('Error: _calculate_global_EQR_from_indicator_value: {} local_EQR value below 0.'.format(local_EQR))
        
        # Get EQR-class limits for the type area to be able to calculate the weighted numerical class
        HG_EQR_LIMIT = self.ref_settings.get_value(variable = 'HG_EQR_LIMIT', water_body = water_body)
        GM_EQR_LIMIT = self.ref_settings.get_value(variable = 'GM_EQR_LIMIT', water_body = water_body)
        MP_EQR_LIMIT = self.ref_settings.get_value(variable = 'MP_EQR_LIMIT', water_body = water_body)
        PB_EQR_LIMIT = self.ref_settings.get_value(variable = 'PB_EQR_LIMIT', water_body = water_body)
        
        ek = local_EQR
#        if self.name == 'BQI' or self.name.lower() == 'secchi' or self.name.lower() == 'oxygen':
#            return False
#        else:
        if HG_EQR_LIMIT - GM_EQR_LIMIT > 0:
            # When higher EQR means higher status (increasing)
            if ek > HG_EQR_LIMIT: 
                status = 'HIGH'
                global_low = 0.8 
                ek_high = 1
                # om värde ist för ek ska ek_high vara ref_värdet eller Bmax värde
                ek_low = HG_EQR_LIMIT
                if ek > 1:
                    ek = 1
                
            elif ek > GM_EQR_LIMIT:
                status = 'GOOD'
                global_low = 0.6 
                ek_high = HG_EQR_LIMIT
                ek_low = GM_EQR_LIMIT
    
            elif ek > MP_EQR_LIMIT:
                status = 'MODERATE'
                global_low = 0.4 
                ek_high = GM_EQR_LIMIT
                ek_low = MP_EQR_LIMIT
                
            elif ek > PB_EQR_LIMIT:
                status = 'POOR'
                global_low = 0.2 
                ek_high = MP_EQR_LIMIT
                ek_low = PB_EQR_LIMIT
                
            else:
                status = 'BAD'
                global_low = 0 
                ek_high = PB_EQR_LIMIT
                ek_low = 0
                if ek < 0:
                    ek = 0
                
        else:
            # When higher EQR means lower status (decreasing)
            if ek > PB_EQR_LIMIT:
                status = 'BAD'
                global_low = 0.2
                ek_high = 1
                # om värde ist för ek ska ek_high vara ref_värdet eller Bmax värde
                ek_low = PB_EQR_LIMIT
                if ek > 1:
                    ek = 1
                
            elif ek > MP_EQR_LIMIT:
                status = 'POOR'
                global_low = 0.4 
                ek_high = PB_EQR_LIMIT
                ek_low = MP_EQR_LIMIT
                
            elif ek > GM_EQR_LIMIT:
                status = 'MODERATE'
                global_low = 0.6 
                ek_high = MP_EQR_LIMIT
                ek_low = GM_EQR_LIMIT

            elif ek > HG_EQR_LIMIT:
                status = 'GOOD'
                global_low = 0.8 
                ek_high = GM_EQR_LIMIT
                ek_low = HG_EQR_LIMIT
                
            else:
                status = 'HIGH'
                global_low = 1
                ek_high = HG_EQR_LIMIT 
                ek_low = 0
                #should this not be 1?
                if ek < 0:
                    ek = 0
        
        
        # Weighted numerical class
        global_EQR = global_low + (ek - ek_low)/(ek_high-ek_low)*0.2
        return global_EQR, status
        #self.classification_results[water_body].add_info('global_EQR', global_EQR)
        #self.classification_results[water_body].add_info('status', status)

        #OLD
#        if local_EQR >= indicator_EQR_REF_limit: #indicator_EQR_REF_limit: 
#            EQR = 1
#            status = 'High'
#        elif local_EQR >= HG_EQR_LIMIT: #indicator_EQR_HG_limit
#            EQR = 0.2*((local_EQR-HG_EQR_LIMIT)/(indicator_EQR_REF_limit-HG_EQR_LIMIT)) + 0.8
#            status = 'High'          
#        elif local_EQR >= GM_EQR_LIMIT: #indicator_EQR_GM_limit
#            EQR = 0.2*((local_EQR-GM_EQR_LIMIT)/(HG_EQR_LIMIT-GM_EQR_LIMIT)) + 0.6
#            status = 'Good'
#        elif local_EQR >= MP_EQR_LIMIT: #indicator_EQR_MP_limit
#            EQR = 0.2*((local_EQR-MP_EQR_LIMIT)/(GM_EQR_LIMIT-MP_EQR_LIMIT)) + 0.4
#            status = 'local_EQR'
#        elif local_EQR >= PB_EQR_LIMIT: #indicator_EQR_PB_limit
#            EQR = 0.2*((local_EQR-PB_EQR_LIMIT)/(MP_EQR_LIMIT-PB_EQR_LIMIT)) + 0.2
#            status = 'Poor'
#        elif local_EQR < PB_EQR_LIMIT: #indicator_EQR_PB_limit
#            EQR = 0.2*((local_EQR-0)/(indicator_EQR_PB_limit-0))
#            status = 'Bad'
#        else:
#            raise('Error: numeric class: {} incorrect.'.format(local_EQR))
#    
#        return EQR, status
           
    @timer    
    #==========================================================================
    def _set_water_body_indicator_df(self, water_body = None):
        """
        Created:        20180215     by Lena
        Last modified:  20180328     by Lena
        df should contain:
            - all needed columns from get_filtered_data
            - referencevalues
            - maybe other info needed for indicator functions
        skapa df utifrån:
        self.index_handler
        self.tolerance_settings
        self.indicator_ref_settings
        """
        #type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        if water_body:
            filtered_data = self.get_filtered_data(subset = self.subset, step = 'step_2', water_body = water_body, indicator = self.name).dropna(subset = [self.indicator_parameter])
            if len(filtered_data) == 0:
#            if water_body not in filtered_data.VISS_EU_CD.unique():
                print('no data for waterbody {}'.format(water_body))
                return False
            water_body_list = [water_body]
            
        else:
            water_body_list = self.get_filtered_data(subset = self.subset, step = 'step_2').dropna(subset = [self.indicator_parameter]).VISS_EU_CD.unique()
#        if water_body:
#        print('self.column_list', self.column_list) 
#        print(water_body_list)
        for water_body in dict.fromkeys(water_body_list, True):
            filtered_data = self.get_filtered_data(subset = self.subset, step = 'step_2', water_body = water_body, indicator = self.name)[self.column_list].copy()
            if filtered_data.empty:
                self.water_body_indicator_df[water_body] = filtered_data 
                continue           
            try:
                self.mapping_objects['water_body'][water_body]['WATERBODY_NAME']
            except AttributeError:
                self.water_body_indicator_df[water_body] = filtered_data.copy() 
                continue
            if len(filtered_data.VISS_EU_CD.unique()) > 1 or filtered_data.VISS_EU_CD.unique() != water_body:
                warnings.warn(message = 'Warning: get_filtered_data() returns {} waterbody. Input waterbody is {}'.format(filtered_data.VISS_EU_CD.unique(), water_body))
                #raise Exception('Error: get_filtered_data() returns {} waterbody. Input waterbody is {}'.format(df.VISS_EU_CD.unique(), water_body))
                df = filtered_data.iloc[0:0]
                self.water_body_indicator_df[water_body]
                continue
#            df = df[self.column_list]
            if self.name == 'indicator_chl':
                df = filtered_data.dropna(subset = self.parameter_list[0:1], how = 'all').copy()
            elif self.name == 'indicator_secchi':
                df = filtered_data.dropna(subset = [self.indicator_parameter]).drop_duplicates(subset = ['SDATE', 'VISS_EU_CD', 'SECCHI']).copy()
            elif self.name == 'indicator_oxygen':
                df = filtered_data.dropna(subset = [self.indicator_parameter]).copy()
                tol_BW = 5
                maxD = self.Hypsographs.get_max_depth_of_water_body(water_body)
                if maxD:
                    self.df_bottomwater[water_body] = df.loc[df['DEPH'] > maxD-tol_BW].copy()
                else:
                    self.df_bottomwater[water_body] = df.copy()
#                self.df_bottomwater[water_body] = df.loc[df['DEPH'] > maxD-tol_BW]
            else:
                df = filtered_data.dropna(subset = [self.indicator_parameter]).copy()
            if df.empty:
                self.water_body_indicator_df[water_body] = df 
                continue 
#            if hasattr(self, 'salt_parameter'):
            if self.name != 'indicator_oxygen':
#                 print('this is where the SettingCopyWithWarning is raised!!!')
                self._add_boundaries_to_df(df, water_body)
            self.water_body_indicator_df[water_body] = df 
            
    #==========================================================================
    def float_convert(self, x):
            try:
                return float(x)
            except:
                return np.nan         
    #==========================================================================
    def get_filtered_data(self, subset=None, step=None, water_body=None, indicator=None):
        """
        Filter for water_body and indicator means filters from indicator_settings are applied.
        But the filters are only applied if they first are added to the index_handler so need to check if water_body and indicator have filters added
        """

        return self.index_handler.get_filtered_data(subset, step, water_body, indicator)
   
#    #==========================================================================
#    def get_numerical_class(self, ek, water_body):
#        """
#        Calculates indicator class (Nklass) according to eq 2.1 in HVMFS 2013:19.
#        Returns a tuple with four values, low, ek_low, ek_heigh and the resulting Nklass.
#        This is specific for the nutrient and phytoplankton indicators.
#        There needs to be:
#            - one def to get nutrient num_class for nutrient indicators (this one as is)
#            - one def to get indicator class and value with the indicator specific EQR and the EQR transformed to the common scale
#            (for nutrients that is num_class on scale 0-4.99 for most others some values on a 0-1 scale)
#        """
#        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
#        # Get EQR-class limits for the type area to be able to calculate the weighted numerical class
#        HG_EQR_LIMIT = self.ref_settings.get_value(variable = 'HG_EQR_LIMIT', type_area = type_area)
#        GM_EQR_LIMIT = self.ref_settings.get_value(variable = 'GM_EQR_LIMIT', type_area = type_area)
#        MP_EQR_LIMIT = self.ref_settings.get_value(variable = 'MP_EQR_LIMIT', type_area = type_area)
#        PB_EQR_LIMIT = self.ref_settings.get_value(variable = 'PB_EQR_LIMIT', type_area = type_area)
#        
#        if self.name == 'BQI' or self.name.lower() == 'secchi' or self.name.lower() == 'oxygen':
#            return False
#        else:
#            if ek > HG_EQR_LIMIT: 
#                status = 'HIGH'
#                n_low = 4 
#                ek_high = 1
#                ek_low = HG_EQR_LIMIT
#                
#            elif ek > GM_EQR_LIMIT:
#                status = 'GOOD'
#                n_low = 3 
#                ek_high = HG_EQR_LIMIT
#                ek_low = GM_EQR_LIMIT
#    
#            elif ek > MP_EQR_LIMIT:
#                status = 'MODERATE'
#                n_low = 2 
#                ek_high = GM_EQR_LIMIT
#                ek_low = MP_EQR_LIMIT
#                
#            elif ek > PB_EQR_LIMIT:
#                status = 'POOR'
#                n_low = 1 
#                ek_high = MP_EQR_LIMIT
#                ek_low = PB_EQR_LIMIT
#                
#            else:
#                status = 'BAD'
#                n_low = 0 
#                ek_high = PB_EQR_LIMIT
#                ek_low = 0
#            
#            # Weighted numerical class
#            n_class = n_low + (ek - ek_low)/(ek_high-ek_low)
#            
#            return n_low, ek_low, ek_high, status, n_class
#    
    
    #==========================================================================        
    def get_ref_value_type(self, type_area = None, water_body = None):
        """
        Created:        20180328     by Lena
        Last modified:  
        Get referencevalue either from equation or directly from settings
        To get reference value from equation you need to supply both type_area and salinity
        """
        return self.ref_settings.get_ref_value_type(type_area = type_area, water_body = water_body)
    
    #==========================================================================        
    def get_boundarie(self, type_area = None, water_body = None, salinity = None, variable = None):
        """
        Created:        20180328     by Lena
        Last modified:  
        Get referencevalue either from equation or directly from settings
        To get reference value from equation you need to supply both type_area and salinity
        
        """
        return self.ref_settings.get_boundarie(type_area = type_area, water_body = water_body, salinity = salinity, variable = variable)
    
    #==========================================================================
    def get_water_body_indicator_df(self, water_body = None):
        """
        Created:        20180215     by Lena
        Last modified:  20180720     by Magnus
        df should contains:
            - all needed columns from get_filtered_data
            - referencevalues
        TODO: add other info needed for indicator functions
        """
        
        return self.water_body_indicator_df.get(water_body, False)
#        return self.water_body_indicator_df[water_body]

    #==========================================================================
    def get_status_from_global_EQR(self, global_EQR):
        
        if global_EQR >= 0.8:
            return 'HIGH'
        elif global_EQR >= 0.6:
            return 'GOOD'
        elif global_EQR >= 0.4:
            return 'MODERATE'
        elif global_EQR >= 0.2:
            return 'POOR'
        elif global_EQR >= 0:
            return 'BAD'
        else:
            return ''
    #==========================================================================  
    def get_closest_matching_salinity(self):
        """
        get closest matching salinity value when salinity is missing. 
        use tolerance info from settings file
        """
        print('method is not written yet')
        raise Exception

                                    
#    #==========================================================================
#    def get_ref_value_for_par_with_salt_ref(self, par=None, salt_par='SALT_CTD', indicator_name=None, tolerance_filter=None):
#        """
#        tolerance_filters is a dict with tolerance filters for the specific (sub) parameter. 
#        """
#        """
#        Vid statusklassificering
#        ska värden från ytvattnet användas (0-10 meter eller den övre vattenmassan
#        om språngskiktet är grundare än 10 meter).
#        
#        Om mätningar vid ett tillfälle är utförda vid diskreta djup, exempelvis 0, 5 och 10
#        meter ska EK-värde beräknas för varje mätning och ett medel–EK skapas för de tre
#        djupen.
#        """
##        class_result = ClassificationResult()
##        class_result.add_info('parameter', par)
##        class_result.add_info('salt_parameter', salt_par)
##        class_result.add_info('type_area', self.data_filter_object.TYPE_AREA.value)
#        
#        """
#        För kvalitetsfaktorn Näringsämnen: 
#        1) Beräkna EK för varje enskilt prov utifrån referensvärden i tabellerna 6.2-6.7.
#        Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vid
#        varje enskilt prov. Om mätningar är utförda vid diskreta djup, beräkna EKvärde
#        för varje mätning och sedan ett medel-EK för varje specifikt mättillfälle.
#        """
#        
#        ref_object = getattr(core.RefValues(), indicator_name.lower())[self.data_filter_object.TYPE_AREA.value]
##        self.ref_object = ref_object
#        par_object = getattr(self, par.lower())
#        salt_object = getattr(self, salt_par.lower())
#        self.par_object = par_object
#        self.salt_object = salt_object
#        
#        par_df = par_object.data.column_data.copy(deep=True)
#        salt_df = salt_object.data.column_data
#        
#        par_df['salt_value_ori'] = np.nan 
#        par_df['salt_value'] = np.nan 
#        par_df['salt_index'] = np.nan 
#        par_df['ref_value'] = np.nan 
#        #par_df['ek_value_calc'] = np.nan 
#        par_df['par_value'] = np.nan 
#        for i in par_df.index:
##            self.i = i
#            df_row = par_df.loc[i, :]
#            par_value = df_row[par]
#            if np.isnan(par_value):
#                ref_value = np.nan
#            else:
#                try:
#                    salt_df.loc[1, salt_par]
#                    first_salt = 1 
#                except KeyError:
#                    # TODO: Why was default set to 1?
#                    first_salt = salt_df.index[0]
#                if i in salt_df.index and not np.isnan(salt_df.loc[first_salt, salt_par]): 
#                    salt_value_ori = salt_df.loc[first_salt, salt_par]  # ska inte det vara: salt_df.loc[i, salt_par]?
#                    salt_index = i
#                else:
#                    # TODO: If not allowed to continue
#                    matching_salt_data = salt_object.get_closest_matching_data(df_row=df_row, 
#                                                                             tolerance_filter=tolerance_filter)
#                    if matching_salt_data.empty:
#                        salt_value_ori = np.nan
#                        salt_index = np.nan
#                        self.missing = df_row
#                    else:
#                        self.matching_salt_data = matching_salt_data
#                        salt_value_ori = matching_salt_data[salt_par]
#                        salt_index = matching_salt_data.name
#                        
#                # Check salt for maximum value
#                salt_value = ref_object.get_max_salinity(salt_value_ori)
#                
#                # Get ref value
#                ref_value = ref_object.get_ref_value(salt_value)
#                
#                # Get EK-value
#                
#                # TODO: This differs between indicators, some are ref/obs other obs/ref
#                # So this should not be in IndicatorBase, output from this def should be salt_val, ref_val och par_val
##                ek_value_calc = ref_value/par_value
#                
##                self.salt_value = salt_value
##                self.ek_value_calc = ek_value_calc
##                self.ref_value = ref_value
##                self.par_value = par_value
##            print('ref_value', ref_value, '=', value)
##            self.df_row = df_row
##            self.salt_value = salt_value
#            par_df.set_value(i, 'salt_value_ori', salt_value_ori) 
#            par_df.set_value(i, 'salt_value', salt_value) 
#            par_df.set_value(i, 'salt_index', salt_index)
#            par_df.set_value(i, 'ref_value', ref_value)
#            par_df.set_value(i, 'par_value', par_value)
#            
#            # Check ek_value_calc
##            ek_value = ek_value_calc
##            if ek_value > 1:
##                ek_value = 1
##            par_df.set_value(i, 'ek_value', ek_value)
#        return par_df        

###############################################################################
class IndicatorBQI(IndicatorBase): 
    """
    Class with methods for BQI indicator. 
    """
    
    def __init__(self, subset_uuid, parent_workspace_object, indicator):
        super().__init__(subset_uuid, parent_workspace_object, indicator) 
        self.indicator_parameter = self.parameter_list[0]
        #self.column_list.remove('DEPH')
        self.column_list = self.column_list + ['MNDEP', 'MXDEP']
        # Set dataframe to use        
        self._set_water_body_indicator_df(water_body = None)
        
    def _add_boundaries_to_df(self, df, water_body):
        self.stations = df.STATN.unique()
        df.loc[:, 'REFERENCE_VALUE'] = pd.Series(np.nan, index = df.index)
        df.loc[:, 'HG_VALUE_LIMIT'] = pd.Series(np.nan, index = df.index)
        df.loc[:, 'GM_VALUE_LIMIT'] = pd.Series(np.nan, index = df.index)
        df.loc[:, 'MP_VALUE_LIMIT'] = pd.Series(np.nan, index = df.index)
        df.loc[:, 'PB_VALUE_LIMIT'] = pd.Series(np.nan, index = df.index)
#        print(df.head())
        for station in self.stations:
            ix = df.index[df.STATN == station]
            station_values = df.loc[ix]
            
            mxdep_list = [self.float_convert(p) for p in station_values.MXDEP.unique()]
            mndep_list = [self.float_convert(p) for p in station_values.MNDEP.unique()]
            if np.isnan(mxdep_list).all and np.isnan(mndep_list).all:
#                print(mxdep_list)
                mxdep_list = [self.float_convert(p) for p in station_values.WADEP.unique()]
                if np.isnan(mxdep_list).all:
                    ref_value = np.nan
                    hg_value = np.nan
                    gm_value = np.nan
                    mp_value = np.nan
                    pb_value = np.nan
#                print('WADEP used', mxdep_list)
            if np.isnan(mxdep_list).all() and not np.isnan(mndep_list).all():
                mxdep_list = [max(mndep_list)]
            if np.isnan(mndep_list).all():
                mndep_list = [min(mxdep_list)]
            
            ref_value = self._get_value(water_body = water_body, variable = 'REF_VALUE_LIMIT', MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
#            ref_value, hg_value, gm_value, mp_value, pb_value = self._get_value(water_body = water_body, variable = ['REF_VALUE_LIMIT', 'HG_VALUE_LIMIT', 'GM_VALUE_LIMIT', 'MP_VALUE_LIMIT', 'PB_VALUE_LIMIT'], MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
#            hg_value = (ref_value*self.ref_settings.get_value(variable = 'HG_EQR_LIMIT', water_body = water_body))
#            gm_value = (ref_value*self.ref_settings.get_value(variable = 'GM_EQR_LIMIT', water_body = water_body))
#            mp_value = (ref_value*self.ref_settings.get_value(variable = 'MP_EQR_LIMIT', water_body = water_body))
#            pb_value = (ref_value*self.ref_settings.get_value(variable = 'PB_EQR_LIMIT', water_body = water_body))

            hg_value = self._get_value(water_body = water_body, variable = 'HG_VALUE_LIMIT', MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
            gm_value = self._get_value(water_body = water_body, variable = 'GM_VALUE_LIMIT', MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
            mp_value = self._get_value(water_body = water_body, variable = 'MP_VALUE_LIMIT', MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
            pb_value = self._get_value(water_body = water_body, variable = 'PB_VALUE_LIMIT', MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
#            if not ref_value:
#                print('no ref_value', df.WATER_BODY_NAME.unique(), df.WATER_TYPE_AREA.unique(), ref_value)
            df.loc[ix, 'REFERENCE_VALUE'] = pd.Series(ref_value, index = ix)
            df.loc[ix, 'HG_VALUE_LIMIT'] = pd.Series(hg_value, index = ix)
            df.loc[ix, 'GM_VALUE_LIMIT'] = pd.Series(gm_value, index = ix)
            df.loc[ix, 'MP_VALUE_LIMIT'] = pd.Series(mp_value, index = ix)
            df.loc[ix, 'PB_VALUE_LIMIT'] = pd.Series(pb_value, index = ix)
            
#            print(df.head())
#        print(df.head())
        
    def _get_deph_interval_list(self, water_body, MXDEP_list, MNDEP_list):
        
        interval = self.ref_settings.get_value(variable = 'DEPH_INTERVAL', water_body = water_body)
        if type(interval) is bool and not interval:
#            print('interval is', interval)
            return False 
        
        deph_interval_list = False
        if type(interval) is tuple:
            # check that position depths are within interval    
            if max(MXDEP_list) <= max(interval) and min(MNDEP_list) >= min(interval):
                deph_interval_list =  [str(interval[0]) +'-'+ str(interval[1])]
#        if np.isnan(min(MNDEP_list)):
#            MNDEP_list = [min(deph_interval_list)]
        else:
            for row in (interval.get_values()):
#                print('row is ',row)
                interval_list = [int(value) for value in row.split('-')]
#                print('interval_list is',interval_list)
#                print('min dep is ',min(MNDEP_list))
#                print('max dep is ',min(MXDEP_list))
#                print('check mxdep {} <= {} and mndep {} >= {}'.format(max(MXDEP_list), max(interval_list), min(MNDEP_list),min(interval_list)))
#                print(MXDEP_list, MNDEP_list)
                if max(MXDEP_list) <= max(interval_list) and min(MNDEP_list) >= min(interval_list):
                    deph_interval_list = [str(interval_list[0]) +'-'+ str(interval_list[1])]
                if deph_interval_list:
                    break
                
        return deph_interval_list
       
    def _get_settings_index(self, water_body, MXDEP_list, MNDEP_list): 
        
        deph_interval_list = self._get_deph_interval_list(water_body, MXDEP_list, MNDEP_list)
#        print('deph_interval_list', deph_interval_list)
        
        if deph_interval_list:
            df = self.ref_settings.get_value(water_body = water_body)
#            print(df['LEVEL_DEPH_INTERVAL'])
            ix = df.loc[df['DEPH_INTERVAL'] == deph_interval_list[0]].index
            return ix[0]
        else:
#            interval = self.ref_settings.get_value(variable = 'LEVEL_DEPH_INTERVAL', water_body = water_body)
#            print('deph_interval_list', deph_interval_list)
#            print('MXDEP_list {}, MNDEP_list {}'.format(MXDEP_list, MNDEP_list))
#            print('outside range {}'.format(interval))
            return False
                   
    def _get_value(self, water_body, variable, MXDEP_list, MNDEP_list):
        
        ix = self._get_settings_index(water_body, MXDEP_list, MNDEP_list)
        if ix:
            if type(variable) is list:
                results = []
                for var in variable:
                    results.append(float(self.ref_settings.get_value(water_body = water_body).loc[ix][var]))
                return tuple(results)
            return float(self.ref_settings.get_value(water_body = water_body).loc[ix][variable])
        else:
#            print(MXDEP_list, MNDEP_list, self.ref_settings.get_value(water_body = water_body))
            if type(variable) is list:
                return (False, )*len(variable)
            return False
        
    #===============================================================
    def calculate_status(self, water_body):
        """
        Calculates indicatotr EQR for BQI values using bootstrap method described in HVMFS 2013:19
        """
        # Set up result class
#        self.classification_results.add_info('parameter', self.indicator_parameter)

        # Set dataframe to use        
#        self._set_water_body_indicator_df(water_body)
        
        # Get type area and return False if there is not match for the given waterbody    
        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        if type_area == None:
            return False, False, False, False
        
        wb_name = self.mapping_objects['water_body'][water_body]['WATERBODY_NAME']
        
#        by_year = False
            
        def bootstrap(value_list, n):
            result2 = []
            for i in range(1,n):
                result1 = []
                for j in range(1,len(value_list)):
                    result1.append(value_list[random.randrange(0,len(value_list)-1)])
                result2.append(np.mean(result1))
            return result2
       
#        by_year_pos = df.groupby(['VISS_EU_CD','YEAR', 'STATN'])[self.indicator_parameter].agg(['count', 'min', 'max', 'mean']).reset_index()
#        by_year_pos.rename(columns={'mean':'position_mean', 'count': 'station_count', 'min': 'station_min', 'max': 'station_max'}, inplace=True)
#
#        by_year = by_year_pos.groupby(['VISS_EU_CD','YEAR']).position_mean.agg(['count', 'min', 'max', 'mean']).reset_index()

        # Random selection with replacement of as many values as there are station means (frac = 1)
        # TODO: spead-up! Is it possible more efficient way to get the list from the map object?
        
        # get data to be used for status calculation
        test = self.water_body_indicator_df[water_body].loc[self.water_body_indicator_df[water_body][self.indicator_parameter] == np.nan]
        df = self.water_body_indicator_df[water_body].dropna(subset = [self.indicator_parameter])#.copy(deep = True)
        self._add_wb_name_to_df(df, water_body)
        year_list = df.YEAR.unique()
        station_list = df.STATN.unique()
        
        n = 9999
        by_year_pos_result_list = []
        by_station_result_list = []
        for station in station_list:
            # All values at station
            station_values = df.loc[df.STATN == station]#.dropna(subset = [self.indicator_parameter])
            year_list = station_values.YEAR.unique()
            ref_value = station_values.REFERENCE_VALUE.unique()[0]
            hg_value = station_values.HG_VALUE_LIMIT.unique()[0]
            gm_value = station_values.GM_VALUE_LIMIT.unique()[0]
            mp_value = station_values.MP_VALUE_LIMIT.unique()[0]
            pb_value = station_values.PB_VALUE_LIMIT.unique()[0]
            # get station depths
#            mxdep_list = [self.float_convert(p) for p in station_values.MXDEP.unique()]
#            mndep_list = [self.float_convert(p) for p in station_values.MNDEP.unique()]
#            print(mndep_list)
#            print(df)
#            if np.isnan(min(mxdep_list)):
#                mxdep_list = [self.float_convert(p) for p in station_values.WADEP.unique()]
#            # get ref and boundaries
#            ref_value = self._get_value(water_body = water_body, variable = 'REF_VALUE_LIMIT', MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
#            hg_value = self._get_value(water_body = water_body, variable = 'HG_VALUE_LIMIT', MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
#            gm_value = self._get_value(water_body = water_body, variable = 'GM_VALUE_LIMIT', MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
#            mp_value = self._get_value(water_body = water_body, variable = 'MP_VALUE_LIMIT', MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
#            pb_value = self._get_value(water_body = water_body, variable = 'PB_VALUE_LIMIT', MXDEP_list = mxdep_list, MNDEP_list = mndep_list)
            ##### CALCLUTE MEAN BQI & EQR FOR EACH STATION  EACH YEAR #####
            station_mean_list = []
            for year in year_list:
                # all values at station in year
                station_year_values = station_values.loc[station_values.YEAR == year]   
                if station_year_values.empty:
                    station_mean= np.nan
                    #global_EQR = np.nan
                    by_year_pos_result_list.append((int(year), station, station_mean, np.nan, np.nan, ref_value, hg_value, gm_value, mp_value, pb_value))
                else:
                    station_mean = station_year_values[self.indicator_parameter].mean()
                    global_EQR, status = self._calculate_global_EQR_from_indicator_value(water_body = water_body, value = station_mean, 
                                                                                     REF_VALUE_LIMIT = ref_value, HG_VALUE_LIMIT = hg_value,
                                                                                     GM_VALUE_LIMIT = gm_value, MP_VALUE_LIMIT = mp_value,
                                                                                     PB_VALUE_LIMIT = pb_value)
                    by_year_pos_result_list.append((int(year), station, station_mean, global_EQR, status, ref_value, hg_value, gm_value, mp_value, pb_value))
                    station_mean_list.append(station_mean)
            if len(station_mean_list) > 1:
                BQIsim = bootstrap(station_mean_list, n)
            elif len(station_mean_list ) == 0:
                BQIsim = np.nan
            else:
                BQIsim = station_mean_list[0]
             
            percentile = np.percentile(BQIsim, 0.2)
            global_EQR, status = self._calculate_global_EQR_from_indicator_value(water_body = water_body, value = percentile, 
                                                                                     REF_VALUE_LIMIT = ref_value, HG_VALUE_LIMIT = hg_value,
                                                                                     GM_VALUE_LIMIT = gm_value, MP_VALUE_LIMIT = mp_value,
                                                                                     PB_VALUE_LIMIT = pb_value)
                               
            by_station_result_list.append((station, percentile, global_EQR, status, ref_value, hg_value, gm_value, mp_value, pb_value))
            
        ##### Create dataframes for saving #####
        by_year_pos = pd.DataFrame(data = by_year_pos_result_list, columns = ['YEAR', 'STATN', 'BQI_station_mean', 'global_EQR','STATUS','ref_value', 'hg_value', 'gm_value', 'mp_value', 'pb_value'])
        by_year_pos['WATER_BODY_NAME'] = wb_name
        by_year_pos['VISS_EU_CD'] = water_body
        by_year_pos['WATER_TYPE_AREA'] = type_area
                   
        by_pos = pd.DataFrame(data = by_station_result_list, columns = ['STATN', 'BQI_20th percentile', 'global_EQR', 'STATUS','ref_value', 'hg_value', 'gm_value', 'mp_value', 'pb_value'])
        by_pos['WATER_BODY_NAME'] = wb_name
        by_pos['VISS_EU_CD'] = water_body
        by_pos['WATER_TYPE_AREA'] = type_area
        
        global_EQR_by_period = np.mean(by_pos.global_EQR)
#         STATIONS_USED =  ', '.join(by_pos.STATN.unique())
#         STATN_count = len(by_pos.STATN.unique())
        status_by_period = self.get_status_from_global_EQR(global_EQR_by_period)
        by_period = pd.DataFrame({'VISS_EU_CD': [water_body], 'WATER_BODY_NAME': [wb_name],'WATER_TYPE_AREA': [type_area],
                                  'global_EQR': [global_EQR_by_period],  'STATUS': [status_by_period]})
        by_period['STATIONS_USED'] = ', '.join(by_pos.STATN.unique())
        by_period['STATN_count'] = len(by_pos.STATN.unique())
        
        min_nr_stations = self.tolerance_settings.get_min_nr_stations(water_body = water_body) 
        boolean_list = by_period['STATN_count'] >= min_nr_stations
        by_period['ok'] = False
        by_period.loc[boolean_list, 'ok'] = True                     
        
        by_period['variance'] = np.nan
        by_period['p_ges'] = np.nan
        return df, by_year_pos, by_pos, by_period
        
    
    def old_calculate_status(self, water_body):
        """
        Calculates indicatotr EQR for BQI values using bootstrap method described in HVMFS 2013:19
        """
        # Set up result class
        self.classification_results.add_info('parameter', self.indicator_parameter)

        # Set dataframe to use        
        self._set_water_body_indicator_df(water_body)
        # get data to be used for status calculation
        df = self.water_body_indicator_df[water_body].copy(deep = True)
#        year_list = df.YEAR.unique()
        # Get type area and return False if there is not match for the given waterbody    
        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        if type_area == None:
            return False, False, False, False
        
        wb_name = self.mapping_objects['water_body'][water_body]['WATERBODY_NAME']
        
        by_date = False
       
        by_year_pos = df.groupby(['VISS_EU_CD','YEAR', 'POSITION'])[self.indicator_parameter].agg(['count', 'min', 'max', 'mean']).reset_index()
        by_year_pos.rename(columns={'mean':'position_mean', 'count': 'position_count', 'min': 'position_min', 'max': 'station_max'}, inplace=True)

        by_year = by_year_pos.groupby(['VISS_EU_CD','YEAR']).position_mean.agg(['count', 'min', 'max', 'mean']).reset_index()

        # Random selection with replacement of as many values as there are station means (frac = 1)
        # TODO: spead-up! Is it possible more efficient way to get the list from the map object?
        def old_bootstrap(df):
            return df.sample(frac = 1, replace = True).mean()
        def bootstrap(value_list, n):
            result2 = []
            for i in range(1,n):
                result1 = []
                for j in range(1,len(value_list)):
                    result1.append(value_list[random.randrange(0,len(value_list)-1)])
                result2.append(np.mean(result1))
            return result2
        
        n = 9999
        BQIsim_year = []
        for ix, year in by_year.YEAR.items():
#            print('number of stations in year ({}): {}'.format(year,len(by_year_pos.loc[by_year_pos.YEAR == year]['position_mean'])))
#            print(by_year_pos.loc[by_year_pos.YEAR == year]['position_mean'])
#            df_list = [by_year_pos.loc[by_year_pos.YEAR == year]['position_mean'].dropna()]*n
            df_list = by_year_pos.loc[by_year_pos.YEAR == year]['position_mean'].dropna().tolist()
            no_stns = len(df_list)
#            print(df_list)
#            print(water_body)
            if no_stns > 1:
                BQIsim = bootstrap(df_list, n)
            else:
                BQIsim = df_list
#            BQIsim = [*map(bootstrap, df_list)]
#            BQIsim = []
#            for x in range(n):
#                BQIsim.append(by_year_pos.loc[by_year_pos.YEAR == year]['position_mean'].sample(frac = 1, replace = True).mean())
            percentile = np.percentile(BQIsim, 0.2) 
#            print(percentile)            
            BQIsim_year.append(percentile)
#        print(BQIsim_year)
        BQI_by_period = np.mean(BQIsim_year)
        
        by_period = pd.DataFrame({'VISS_EU_CD': [water_body], 'WATER_BODY_NAME': [wb_name],'WATER_TYPE_AREA': [type_area], 'BQI': [BQI_by_period]})
                                  #'GLOBAL_EQR': [global_EQR],  'STATUS': [status], })
        
        # TODO: Add BQImax to settingsfile (from handbok or ask Mats L). Call _calculate_global_EQR and add results to resul class
        return by_date, by_year_pos, by_year, by_period
        
###############################################################################
class IndicatorNutrients(IndicatorBase): 
    """
    Class with methods common for all nutrient indicators (TOTN, DIN, TOTP and DIP). 
    """
    
    def __init__(self, subset_uuid, parent_workspace_object, indicator):
        super().__init__(subset_uuid, parent_workspace_object, indicator)  
        self.indicator_parameter = self.parameter_list[0]
        self.salt_parameter = self.parameter_list[-1] 
        # Set dataframe to use        
        self._set_water_body_indicator_df(water_body = None)
        
    def _add_winter_year(self, df, winter_months):
        #print(winter_months)
        # add column for winter_YEAR
        df['winter_YEAR'] = df.apply(lambda row: row.YEAR+1 if (row.MONTH in winter_months) else row.YEAR, axis=1) 
        #if 'winter_YEAR' not in self.column_list:
        #    self.column_list = self.column_list + ['winter_YEAR']
        
    def calculate_status(self, water_body):
        """Calculates indicator Ecological Ratio (ER) values, for nutrients this means reference value divided by observed value.
           Transforms ER values to numeric class values (num_class)
        """
        """ Vid statusklassificering ska värden från ytvattnet användas (0-10 meter eller den övre vattenmassan om språngskiktet är grundare än 10 meter).
            Om mätningar vid ett tillfälle är utförda vid diskreta djup, 
            exempelvis 0, 5 och 10 meter ska EK-värde beräknas för varje mätning och ett medel–EK skapas för de tre djupen.
        """
        def set_value_above_one(x):
            #y = x.indicator_parameter/x.REFERENCE_VALUE
            if x > 1:
                return 1
            else:
                return x
        
        if 'winter_YEAR' in self.column_list:
            self.column_list.remove('winter_YEAR')
                    
        #self._set_water_body_indicator_df(water_body)
        # get data to be used for status calculation
        if water_body not in self.water_body_indicator_df.keys():
            return False, False, False, False
#        try:
#            df = self.water_body_indicator_df[water_body]
#        except KeyError:
#            if self._set_water_body_indicator_df(water_body):
#                df = self.water_body_indicator_df[water_body]
#            else:
#                return False, False, False, False
#        self._add_wb_name_to_df(df, water_body)
        df = self.water_body_indicator_df[water_body]
        if len(df) < 1 or 'unknown' in df.WATER_BODY_NAME.unique():
            return False, False, False, False
        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        if type_area == None:
            return False, False, False, False
            
        # Add column for winter year for winter indicators and set year_variable
        year_variable = 'YEAR'
        if 'winter' in self.name:
            month_list = self.parent_workspace_object.get_step_object(step = 2, subset = self.subset).get_indicator_data_filter_settings(self.name).get_value(variable = 'MONTH_LIST', water_body = water_body)
#            print('month_list', month_list)
            winter_months = [month for month in month_list if month > 10]
            #print(water_body, self.mapping_objects['water_body'][water_body]['WATERBODY_NAME'])
            self._add_winter_year(df, winter_months)
            year_variable = 'winter_YEAR' 
        
        
        
        """ Calculate local_EQR (EK-värde)
        """        
        
        
        
        """ 
        1) 
        TIDIGARE FÖRESKRIFTEN:
        Beräkna local_EQR (EK-värde) för varje enskilt prov utifrån (ekvationer för) referensvärden i tabellerna 6.2-6.7.
        Beräkna local_EQR (EK-värde) för varje mätning och sedan ett medel-EK för varje specifikt mättillfälle.
        NYA FÖRESKRIFTEN
        calculate local_EQR for mean of nutrient conc and salinity 0-10 m for each station.
        
        """
        # ENLIGT GAMLA FS SÅ SKA DETTA VARA LÄGSTA NIVÅN PÅ VILKEN DET GÖRS MEDELVÄRDEN.
        #df['local_EQR'] = df.REFERENCE_VALUE/df[self.indicator_parameter]
        #df['local_EQR'] = df['local_EQR'].apply(set_value_above_one) 
        #df['global_EQR'], df['STATUS'] = zip(*df['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
        
        
            
        # add dataframe to resultsclass
#        self.classification_results.add_info(water_body, df)
        #self.classification_results[water_body].add_info('all_data', df)
        
        # calculate mean, max, min and count for local_EQR per measurement occasion. Here measurements on one day count as one occasion
        # .reset_index keeps all df column headers
        # TODO: what about different stations in one waterbody?
        
        if len(df.VISS_EU_CD.unique()) > 1:
            #TODO hur ska vi hantera detta om vi tillåter val av stationer i angränsande waterbody?
            raise Exception('more than one waterbody in dataframe')
            
       
        agg_dict1 = {self.indicator_parameter: 'mean', self.salt_parameter: 'mean', 
                            'REFERENCE_VALUE': 'mean', 'HG_VALUE_LIMIT': 'mean', 'GM_VALUE_LIMIT': 'mean', 'MP_VALUE_LIMIT': 'mean', 'PB_VALUE_LIMIT': 'mean', 
                            'DEPH': 'count', 'VISS_EU_CD': 'max', 'WATER_BODY_NAME': 'max', 'WATER_TYPE_AREA': 'max'}       
        if year_variable == 'winter_YEAR':
            agg_dict1 = {self.indicator_parameter: 'mean', self.salt_parameter: 'mean', 
                            'REFERENCE_VALUE': 'mean', 'HG_VALUE_LIMIT': 'mean', 'GM_VALUE_LIMIT': 'mean', 'MP_VALUE_LIMIT': 'mean', 'PB_VALUE_LIMIT': 'mean', 
                         year_variable: 'mean', 'DEPH': 'count', 'VISS_EU_CD': 'max', 'WATER_BODY_NAME': 'max', 'WATER_TYPE_AREA': 'max'}       
        
        
        agg_dict2 = {key: 'mean' for key in self.additional_parameter_list}       
        
        by_date = df.groupby(['SDATE', 'YEAR', 'STATN']).agg({**agg_dict1, **agg_dict2}).reset_index()
        by_date.rename(columns={'DEPH':'DEPH_count'}, inplace=True)
        
               
        if type_area in ['1','1s','1n','2','3','4','5','6','25'] and 'winter' in self.name:
            if self.indicator_parameter == 'NTOT' or self.indicator_parameter == 'DIN':
                check_par = 'DIN'
            else:
                check_par = 'PHOS'
            by_date['highest_'+check_par] = False
            for name, group in by_date.groupby(['YEAR','STATN']):
                group[check_par].idxmax()
                by_date.loc[group[check_par].idxmax(), 'highest_'+check_par] = True 
            #print(by_date['highest_'+check_par])     
            by_date = by_date[by_date['highest_'+check_par]]
        
#        by_date = self._add_reference_value_to_df(by_date, water_body)
        by_date['local_EQR'] = by_date.REFERENCE_VALUE/by_date[self.indicator_parameter]
        by_date['local_EQR'] = by_date['local_EQR'].apply(set_value_above_one)
        by_date['global_EQR'], by_date['STATUS'] = zip(*by_date['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
        
        # Remove occations with not enough samples
        # Or use count as a flag for what to display for the user?
        
        
        
        """
        2) Medelvärdet av EK för varje parameter beräknas för varje år.
        """
        agg_dict1 = {'local_EQR': 'mean', 'SDATE': 'count', 'VISS_EU_CD': 'max', 'WATER_BODY_NAME': 'max', 'WATER_TYPE_AREA': 'max'}       
        
        by_year = by_date.groupby([year_variable]).agg({**agg_dict1}).reset_index() #, **agg_dict2
        by_year.rename(columns={'SDATE':'DATE_count'}, inplace=True)
        by_year['global_EQR'], by_year['STATUS'] = zip(*by_year['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
        by_year['STATIONS_USED'] = ', '.join(by_date.STATN.unique())

        
        """
        3) Medelvärdet av EK för varje parameter och vattenförekomst (beräknas för minst
        en treårsperiod)
        """
        agg_dict1 = {'local_EQR': 'mean', year_variable: 'count', 'WATER_TYPE_AREA': 'max', 'WATER_BODY_NAME': 'max',}       
        
        by_period = by_year.groupby(['VISS_EU_CD']).agg({**agg_dict1}).reset_index() #, **agg_dict2
        by_period.rename(columns={year_variable:'YEAR_count'}, inplace=True)
        
        by_period['global_EQR'], by_period['STATUS'] = zip(*by_period['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
        S = ', '.join(by_year.STATIONS_USED.unique())
        by_period['STATIONS_USED'] = ', '.join(set(S.split(', '))) 
        
        min_nr_years = self.tolerance_settings.get_min_nr_years(water_body = water_body) 
        boolean_list = by_period['YEAR_count'] >= min_nr_years
        by_period['ok'] = False
        by_period.loc[boolean_list, 'ok'] = True
         
        """
        4) Statusklassificeringen för respektive parameter görs genom att medelvärdet av
        EK jämförs med de angivna EK-klassgränserna i tabellerna 6.2-6.7. 
        """
        
        by_year_pos = False
        by_period['variance'] = np.nan
        by_period['p_ges'] = np.nan
        return by_date, by_year_pos, by_year, by_period
        # Add waterbody status to result class
#        self.classification_results[water_body].add_info('local_EQR_by_date', by_date)
#        self.classification_results[water_body].add_info('local_EQR_by_year', by_year)
#        self.classification_results[water_body].add_info('local_EQR_by_period', by_period['mean'].get_value('mean_local_EQR'))
#        self.classification_results[water_body].add_info('number_of_years', by_period['count'].get_value('mean_local_EQR'))
#        self.classification_results[water_body].add_info('all_ok', all_ok)
#                
        """
        5) EK vägs samman för ingående parametrar (tot-N, tot-P, DIN och DIP) enligt
        beskrivning i föreskrift för slutlig statusklassificering av hela kvalitetsfaktorn.
        Görs i quality_factors, def calculate_quality_factor()
        """
        
###############################################################################
class IndicatorOxygen(IndicatorBase): 
    """
    Class with methods for Oxygen indicator. 
    """
    
    def __init__(self, subset_uuid, parent_workspace_object, indicator):
        super().__init__(subset_uuid, parent_workspace_object, indicator)  
        self.indicator_parameter = self.parameter_list[0]
        self.Hypsographs = self.mapping_objects['hypsographs']
        self.column_list = self.column_list + ['source_DOXY']
        self.deficiency_limit = 3.5
        self.tol_BW = 10
        self.test1_result_array = []
        self.test1_no_yr = np.nan
        self.test2_result_array = []
        self.test1_no_yr = np.nan
        self.df_bottomwater = {}
        # Set dataframe to use        
        self._set_water_body_indicator_df(water_body = None)
        
    ############################################################################### 
    def _deprecated_get_status_from_classboundaries(self, value, water_body):
        """
        get status for given value and waterbody from classboundarie values (not EQR)
        """
    
        HG_VALUE_LIMIT = self.ref_settings.get_value(variable = 'HG_VALUE_LIMIT', water_body = water_body)
        GM_VALUE_LIMIT = self.ref_settings.get_value(variable = 'GM_VALUE_LIMIT', water_body = water_body)
        MP_VALUE_LIMIT = self.ref_settings.get_value(variable = 'MP_VALUE_LIMIT', water_body = water_body)
        PB_VALUE_LIMIT = self.ref_settings.get_value(variable = 'PB_VALUE_LIMIT', water_body = water_body)

        if value > HG_VALUE_LIMIT:
            status = 'HIGH'
        elif value > GM_VALUE_LIMIT:
            status = 'GOOD'
        elif value > MP_VALUE_LIMIT:
            status = 'MODERATE'  
        elif value > PB_VALUE_LIMIT:
            status = 'POOR'
        else:
            status = 'BAD'
        
        return status, value, GM_VALUE_LIMIT     
    
    ###############################################################################        
    def _get_affected_area_fraction(self, df, water_body):
       
        # df = df[df['MONTH'].isin(list(range(1,5+1)))]
#        maxD = self.Hypsographs.get_max_depth_of_water_body(water_body)
        minimum_deficiency_depth = df.loc[df[self.indicator_parameter] <= self.deficiency_limit, 'DEPH'].min()
        if minimum_deficiency_depth > self.maxD:
            minimum_deficiency_depth = self.maxD
        self.minimum_deficiency_depth = minimum_deficiency_depth
#        print(minimum_deficiency_depth)
        affected_area_fraction = self.Hypsographs.get_area_fraction_at_depth(water_body = water_body, depth = minimum_deficiency_depth)
        
        return affected_area_fraction
    
    ###############################################################################        
    def _mean_of_quantile(self, df = None, water_body = None, month_list = None):
        """
        Calculates mean of the 25% percentile for each posisition in the waterbody using data from the given months
        """
        if month_list:
#            df = df[df['MONTH'].isin(list(range(1,5+1)))]
            df = df[df['MONTH'].isin(month_list)]
        no_yr = len(df['YEAR'].unique())
        month_list = df['MONTH'].unique()
        if no_yr >= 1:
#            tol_BW = 5
#            maxD = self.Hypsographs.get_max_depth_of_water_body(water_body)
#            value_list = []
            q = df.loc[df['DEPH'] > self.maxD - self.tol_BW, self.indicator_parameter].quantile(0.25)
#            print('q',q)
            #print(group.loc[group['DEPH'] > maxD-tol_BW])
            #deph_list
#            value_list.append(df.loc[df[self.indicator_parameter] < q, self.indicator_parameter].mean())
#            value = df.loc[df[self.indicator_parameter] < q, self.indicator_parameter].mean()
            value = np.nanmean(q)
#            print('nanmean(q)',value)
#            position_list.append(key)
        else:
#            value_list = False
            value = False
#            print('no_yr',no_yr)
            
        return value, no_yr, month_list
    ###############################################################################     
#    def _set_water_body_indicator_df(self, water_body = None):
#        """
#        Created:        20180427     by Lena
#        Last modified:  20180427     by Lena
#        df should contain:
#            - all needed columns from get_filtered_data
#            - referencevalues
#            - maybe other info needed for indicator functions
#        skapa df utifrån:
#        self.index_handler
#        self.tolerance_settings
#        self.indicator_ref_settings
#        """
#        
#        if water_body:
#           if water_body not in self.get_filtered_data(subset = self.subset, step = 'step_2').dropna(subset = [self.indicator_parameter]).VISS_EU_CD.unique():
#               print('no data for waterbody {}'.format(water_body))
#               return False
#           water_body_list = [water_body]
#            
#        else:
#            water_body_list = self.get_filtered_data(subset = self.subset, step = 'step_2').dropna(subset = [self.indicator_parameter]).VISS_EU_CD.unique()
##        if water_body:
#        for water_body in water_body_list:
##            print(water_body)
#            df = self.get_filtered_data(subset = self.subset, step = 'step_2', water_body = water_body).copy(deep = True)
#            df = df.dropna(subset = [self.indicator_parameter])[self.column_list]
#            self.water_body_indicator_df[water_body] = df 
#            tol_BW = 5
#            maxD = self.Hypsographs.get_max_depth_of_water_body(water_body)
#            if maxD:
#                self.df_bottomwater[water_body] = df.loc[df['DEPH'] > maxD-tol_BW]
#            else:
#                self.df_bottomwater[water_body] = df
##        else:
##            print('water_body must be given to set_water_body_indicator_df')
         
    ###############################################################################    
    def _test1(self, df, water_body):
        """
        To decide if the water body suffers from oxygen deficiency or not.
        Takes bottomwater data for the whole year and checks if the mean of the 25% percentile is above or below limit
        """
        # all months jan-dec should be used for test1
        result, no_yr, month_list = self._mean_of_quantile(df = df, water_body = water_body, month_list = None)
        self.test1_result = result
        self.test1_no_yr = no_yr
        self.test1_month_list = month_list
        
#        if result == False:
#            return False, False, False
        
##        if all(r > self.deficiency_limit for r in result_array[~np.isnan(result_array)]):
#        if result > self.deficiency_limit:
#            # Status to be calculated from lowest mean concentration of the 25% lowest values, here all above limit so high status
#            #return 'no_deficiency', self.deficiency_limit, 
#            self.test1_no_yr = no_yr
##        elif any(r <= self.deficiency_limit for r in result_array[~np.isnan(result_array)]):
#        elif result <= self.deficiency_limit:
#            #return 'deficiency', self.deficiency_limit, 
#            self.test1_no_yr = no_yr
#        else:
#            #return False, None, None
    
    ###############################################################################    
    def _test2(self, df, water_body, skip_longterm = False):
        """
        To decide if the water body suffers from seasonla or longterm oxygen deficiency.
        Takes bottomwater data for jan-maj and for every position checks if the mean of the 25% percentile is above or below limit 
        """
        month_list = list(range(1,5+1))
        result, no_yr, month_list = self._mean_of_quantile(df = df, water_body = water_body, month_list = month_list)
        self.test2_result = result
        self.test2_no_yr = no_yr
        self.test2_month_list = month_list
        if self.test2_no_yr >= 3:
            self.test2_ok = True
        else:
            self.test2_ok = False
#        if len(result_array) == 1 and result_array[0] == False:
#            return False, None, None, None
        
        #status = None 
#        deficiency_type = None
#        deficiency_limit = None
#        
#        # When all values are above the deficiency limit the deficiency type is seasonal
##        if all(r > self.deficiency_limit for r in result_array[~np.isnan(result_array)]):
#        if result > self.deficiency_limit:
#            # seasonal oxygen deficiency
#            deficiency_limit = self.deficiency_limit 
#            deficiency_type = 'seasonal'
#            # If there is no deficiency in jan-maj it means the deficiency is in the autumn, so use value from test1 for status
#            # Status to be calculated from lowest mean concentration of the 25% lowest values (Method 1)
#            conc_value = self.test1_result
##            no_yr = self.test1_no_yr
#            area_fraction_value = None
#            #status, value = self._get_status_from_classboundaries(value, water_body)
#        # When any value is below the deficiency limit the deficiency type is longterm
##        elif any(r <= self.deficiency_limit for r in result_array[~np.isnan(result_array)]):
#        elif result <= self.deficiency_limit:
#            # Methods to determine longterm oxygen deficiency (perennial and permanent) (Method 2)
#            deficiency_type = 'longterm'
#            #month_list = list(range(6,12+1))
#            #df = df[df['MONTH'].isin(month_list)]
#            no_yr = len(df['YEAR'].unique())
#            affected_area_fraction = self._get_affected_area_fraction(df, water_body)
#            area_fraction_value = affected_area_fraction*100
#            conc_value = self.test1_result
#        else:
#            #status, 
#            conc_value = None
#            area_fraction_value = None
#            no_yr = None
#        
#        if skip_longterm:
#           deficiency_limit = self.deficiency_limit 
#           deficiency_type = 'longterm Method 1'
#           conc_value = self.test1_result
#           area_fraction_value = None
#        
##        return status, value, deficiency_type, limit
#        return conc_value, area_fraction_value, deficiency_type, deficiency_limit, no_yr
    
    ############################################################################### 
    def calculate_status(self, water_body):
        """
        Created     20180619    by Lena Viktorsson
        Updated     20180619    by Lena Viktorsson
        Method to calculate status for oxygen indicator
        """
        #### reset results
        self.test1_result = np.nan
        self.test1_no_yr = np.nan
        self.test2_result = np.nan
        self.test2_no_yr = np.nan
        self.test2_ok = False
        self.df_bottomwater = {}
        self.maxD = self.Hypsographs.get_max_depth_of_water_body(water_body)
        self.minimum_deficiency_depth = np.nan 
        self.tol_BW = 10
        
        # Set up result class
#        self.classification_results.add_info('parameter', self.indicator_parameter)

#        # Set dataframe to use        
#        self._set_water_body_indicator_df(water_body)
        # get data to be used for status calculation
        df = self.water_body_indicator_df[water_body].copy(deep = True)
        self.no_yr = len(df['YEAR'].unique())
        self.month_list = df['MONTH'].unique()
        
        # if no data        
        if len(df) < 1:
            return False, False, False, False
        # if more than one water body in dataframe, raise error      
        if len(df.VISS_EU_CD.unique()) > 1:
            #TODO hur ska vi hantera detta om vi tillåter val av stationer i angränsande waterbody?
            raise Exception('more than one waterbody in dataframe') 
        # Get type area and return False if there is not match for the given waterbody    
        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        if type_area == None:
            return False, False, False, False
        
        
        wb_name = self.mapping_objects['water_body'][water_body]['WATERBODY_NAME']
        by_year_pos, by_year = False, False
        by_date = df
        comment = ''
        
        ######## ------------------ CALCULATIONS ------------------########
        ######## TEST 1 checks if the waterbody suffers from oxygen deficiency or not jan-dec #######################
        #deficiency, deficiency_limit, no_yr = 
        self._test1(df, water_body)
        ######## TEST 2 checks if the waterbody suffers from oxygen deficiency or not jan-maj #######################
        self._test2(df, water_body)
        ######## AREA FRACTION WITHI LOW OXYGEN #######
        affected_area_fraction = self._get_affected_area_fraction(df, water_body)
        area_fraction_value = affected_area_fraction*100
        if self.test1_result > self.deficiency_limit:
            deficiency_type = 'no_deficiency'
            status = 'HIGH'
            global_EQR = 1
#            area_fraction_value = np.nan 
        elif self.test1_result <= self.deficiency_limit:
            ######### TEST 2 tests the type of oxygen deficiency if status was not 'High'. ######################
#            conc_value, area_fraction_value, deficiency_type, deficiency_limit, no_yr = self._test2(df, water_body)
            affected_area_fraction = self._get_affected_area_fraction(df, water_body)
            area_fraction_value = affected_area_fraction*100
            if self.test2_result > self.deficiency_limit or np.isnan(self.test2_result):
                #### METHOD 1 ####
                deficiency_type = 'seasonal'
                global_EQR, status = self._calculate_global_EQR_from_indicator_value(water_body = water_body, value = self.test1_result, max_value = 100)
            elif self.test2_result <= self.deficiency_limit:
                deficiency_type = 'longterm'
                if self.ref_settings.get_value(variable = 'VISS_EU_CD', water_body = water_body) == water_body:
                    #### METHOD 2 ####
                    global_EQR, status = self._calculate_global_EQR_from_indicator_value(water_body = water_body, value = area_fraction_value, max_value = 100)
                else:
                    #### METHOD 1 #####
                    comment = 'no classboundaries defined for longterm deficieny in this waterbody, using definition of seasonal deficiency'
                    global_EQR, status = self._calculate_global_EQR_from_indicator_value(value = self.test1_result, water_body = water_body)
        else:
            return False, False, False, False
        
#        print(wb_name)
#        print(deficiency_type, 'test1_result {}'.format(self.test1_result))

#        comment = ''
#        
#        if deficiency == 'no_deficiency':
#            conc_value = self.test1_result
#            deficiency_type = 'no_deficiency'
#            no_yr = no_yr
#            status = 'HIGH'
#            global_EQR = 1
#            area_fraction_value = np.nan
#        elif deficiency == 'deficiency':
#            ######### TEST 2 tests the type of oxygen deficiency if status was not 'High'. ######################
#            conc_value, area_fraction_value, deficiency_type, deficiency_limit, no_yr = self._test2(df, water_body)
#            print('conc value {} \t{} limit {}'.format(conc_value, deficiency_type, deficiency_limit))
#            if deficiency_type in ['longterm']:
#                if self.ref_settings.get_value(variable = 'VISS_EU_CD', water_body = water_body) == water_body: 
#                    deficiency_limit = self.ref_settings.get_ref_value(water_body = water_body)
#                    print(water_body, self.ref_settings.get_value(variable = 'VISS_EU_CD', water_body = water_body), wb_name)
#                else:
#                    deficiency_type = 'longterm (method 1)'
#                    #conc_value, area_fraction_value, deficiency_type, deficiency_limit, no_yr = self._test2(df, water_body, skip_longterm = True)
#                    comment = 'no classboundaries defined for longterm deficieny in this waterbody, using definition of seasonal deficiency'
#        else:
#            return False, False, False, False
##        else:
##            value, deficiency_type, deficiency_limit, no_yr = None, None, None, None
#        if deficiency_type == 'longterm':
#            print('###################################################')
#            global_EQR, status = self._calculate_global_EQR_from_indicator_value(value = area_fraction_value, water_body = water_body, max_value = 100)  
#        elif deficiency_type is not 'no_deficiency':
#            global_EQR, status = self._calculate_global_EQR_from_indicator_value(value = conc_value, water_body = water_body)
#        else:
#            print('deficiency type {}'.format(deficiency_type))

        
#        print(deficiency_type)
#        print('test1_result {}'.format(self.test1_result))
#        print('test2_result {}'.format(self.test2_result))
#        print('area_fraction_value {} minimum_deficiency_depth {} \t{} limit {}'.format(area_fraction_value, self.minimum_deficiency_depth, deficiency_type, self.deficiency_limit))
#        print('global EQR {} status {}'.format(global_EQR, status)      )
#       global_EQR, status = self._calculate_global_EQR_from_indicator_value(water_body = 'unspecified', value = value)
       
        by_period = pd.DataFrame({'VISS_EU_CD': [water_body], 'WATER_BODY_NAME': [wb_name],'WATER_TYPE_AREA': [type_area], 
                                  'GLOBAL_EQR': [global_EQR],  'STATUS': [status], 'O2 conc test1': [self.test1_result], 'O2 conc test2': [self.test1_result], 
                                  'Area below limit %': [area_fraction_value], 'test2_ok': [self.test2_ok], 'total_month_list': [self.month_list],  'test1_month_list': [self.test1_month_list], 'test2_month_list': [self.test2_month_list],
                                  'total_no_yr': [self.no_yr], 'test1_no_yr': [self.test1_no_yr], 'test2_no_yr': [self.test2_no_yr],
                                  'DEFICIENCY_TYPE': [deficiency_type], 'CONC_LIMIT': [self.deficiency_limit], 
                                  'COMMENT': [comment]})
        
#        by_period = by_period[['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA', 'GLOBAL_EQR', 'STATUS', 'O2 min conc test1', 'Area below limit %', 'DEFICIENCY_TYPE', 'LIMIT',	'NUMBER OF YEARS', 'COMMENT']]
        
#        self.classification_results[water_body].add_info('value', value)
#        self.classification_results[water_body].add_info('test1_resultlist', self.test1_result_list)
#        self.classification_results[water_body].add_info('test2_resultlist', self.test2_result_list)
        by_period['variance'] = np.nan
        by_period['p_ges'] = np.nan
        return by_date, by_year_pos, by_year, by_period
          
    
###############################################################################
class IndicatorPhytoplankton(IndicatorBase): 
    """
    Class with methods incommon for Phytoplankton indicators. 
    """
    
    def __init__(self, subset_uuid, parent_workspace_object, indicator):
        super().__init__(subset_uuid, parent_workspace_object, indicator) 
        self.indicator_parameter = self.parameter_list[0]
        self.salt_parameter = self.parameter_list[-1]
        # Set dataframe to use        
        self._set_water_body_indicator_df(water_body = None)
        
        
    def calculate_status(self, water_body):
        """
        Calculates indicator Ecological Ratio (ER) values, for nutrients this means reference value divided by observed value.
        Transforms ER values to numeric class values (num_class)
        """
        """
        Vid statusklassificering ska värden från ytvattnet användas (0-10 meter eller den övre vattenmassan om språngskiktet är grundare än 10 meter).
        Om mätningar vid ett tillfälle är utförda vid diskreta djup, 
        exempelvis 0, 5 och 10 meter ska EK-värde beräknas för varje mätning och ett medel–EK skapas för de tre djupen.
        """
        def set_value_above_one(x):
            #y = x.indicator_parameter/x.REFERENCE_VALUE
            if x > 1:
                return 1
            else:
                return x
                    
        # Set up result class
#        self.classification_results.add_info('parameter', self.indicator_parameter)
#        self.classification_results.add_info('salt_parameter', self.salt_parameter)
        
#        self._set_water_body_indicator_df(water_body)
        # get data to be used for status calculation, not deep copy because local_EQR values are relevant to see together with data
        if water_body not in self.water_body_indicator_df.keys():
            return False, False, False, False
        df = self.water_body_indicator_df[water_body]
        if self.name == 'chl' and len(df.dropna(subset = [self.indicator_parameter])) == 0 and len(df.dropna(subset = [self.parameter_list[1]])) > 0: 
            indicator_parameter = self.parameter_list[1]
        else:
            indicator_parameter = self.parameter_list[0]
        
        if len(df) < 1:
            return False, False, False, False
               
        if len(df.VISS_EU_CD.unique()) > 1:
                    #TODO hur ska vi hantera detta om vi tillåter val av stationer i angränsande waterbody?
            raise Exception('more than one waterbody in dataframe') 
            
        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        if type_area == None:
            return False, False, False, False
        
#        self._add_wb_name_to_df(df, water_body)
        """ Calculate local_EQR (EK-värde)
        """ 
        """ 1) Beräkna local_EQR (EK-värde) för varje enskilt prov utifrån (ekvationer för) referensvärden i tabellerna 6.2-6.7.
            Beräkna local_EQR (EK-värde) för varje mätning och sedan ett medel-EK för varje specifikt mättillfälle.
            TO BE UPDATED TO local_EQR for mean of nutrient conc and salinity 0-10 m.
        """
        
        # add dataframe to resultsclass
#        self.classification_results.add_info(water_body, df)
        
        # TODO: what about different stations in one waterbody?
        
        agg_dict1 = {indicator_parameter: 'mean', self.salt_parameter: 'mean', 
                     'REFERENCE_VALUE': 'mean', 'HG_VALUE_LIMIT': 'mean', 'GM_VALUE_LIMIT': 'mean', 'MP_VALUE_LIMIT': 'mean', 'PB_VALUE_LIMIT': 'mean', 
                      'DEPH': 'count', 'VISS_EU_CD': 'max', 'WATER_BODY_NAME': 'max', 'WATER_TYPE_AREA': 'max'}       
        if len(self.additional_parameter_list) > 0:
            agg_dict2 = {key: 'mean' for key in self.additional_parameter_list}
        else: agg_dict2 = {}        	
        
        by_date = df.groupby(['SDATE', 'YEAR', 'STATN']).agg({**agg_dict1, **agg_dict2}).reset_index()
        by_date.rename(columns={'DEPH':'DEPH_count'}, inplace=True)
        
#        by_date = self._add_reference_value_to_df(by_date, water_body)
        by_date['local_EQR'] = by_date.REFERENCE_VALUE/by_date[indicator_parameter]
        by_date['local_EQR'] = by_date['local_EQR'].apply(set_value_above_one)
        by_date['global_EQR'], by_date['STATUS'] = zip(*by_date['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
        #by_date.set_index(keys = 'VISS_EU_CD', append =True, drop = False, inplace = True)        
        
        """ 2) Medelvärdet av EK för parametern beräknas för varje år och station.
        """
        agg_dict1 = {'local_EQR': 'mean', indicator_parameter: 'mean', self.salt_parameter: 'mean', 'SDATE': 'count', 'VISS_EU_CD': 'max', 'WATER_BODY_NAME': 'max', 'WATER_TYPE_AREA': 'max'}       
        
        by_year_pos = by_date.groupby(['YEAR', 'STATN']).agg({**agg_dict1, **agg_dict2}).reset_index()
        by_year_pos.rename(columns={'SDATE':'DATE_count'}, inplace=True)
        by_year_pos['global_EQR'], by_year_pos['STATUS'] = zip(*by_year_pos ['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
        # by_year_pos .set_index(keys = 'VISS_EU_CD', append =True, drop = False, inplace = True)
        
        """
        3) Medelvärdet av EK för parametern beräknas för varje år.
        """
        agg_dict1 = {'local_EQR': 'mean', indicator_parameter: 'mean', self.salt_parameter: 'mean', 'STATN': 'count', 'VISS_EU_CD': 'max', 'WATER_BODY_NAME': 'max', 'WATER_TYPE_AREA': 'max'}       
        
        by_year = by_year_pos.groupby(['YEAR']).agg({**agg_dict1}).reset_index() #, **agg_dict2
        by_year.rename(columns={'STATN':'STATN_count'}, inplace=True)
        by_year['global_EQR'], by_year['STATUS'] = zip(*by_year ['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
        by_year['STATIONS_USED'] = ', '.join(by_year_pos.STATN.unique())
        #by_year.set_index(keys = 'VISS_EU_CD', append =True, drop = False, inplace = True)
        
                
        """
        4) Medelvärdet av EK för varje parameter och vattenförekomst (beräknas för minst
        en treårsperiod)
        """
        agg_dict1 = {'local_EQR': 'mean', indicator_parameter: 'mean', self.salt_parameter: 'mean', 'YEAR': 'count', 'YEAR': 'count', 'WATER_BODY_NAME': 'max', 'WATER_TYPE_AREA': 'max'}       
        
        by_period = by_year.groupby(['VISS_EU_CD']).agg({**agg_dict1}).reset_index() #, **agg_dict2
        by_period.rename(columns={'YEAR':'YEAR_count'}, inplace=True)
        by_period['global_EQR'], by_period['STATUS'] = zip(*by_period['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
        S = ', '.join(by_year.STATIONS_USED.unique())
        by_period['STATIONS_USED'] = ', '.join(set(S.split(', '))) 
        
        min_nr_years = self.tolerance_settings.get_min_nr_years(water_body = water_body) 
        boolean_list = by_period['YEAR_count'] >= min_nr_years
        by_period['ok'] = False
        by_period.loc[boolean_list, 'ok'] = True
        
        """
        4) Statusklassificeringen för respektive parameter görs genom att medelvärdet av
        EK jämförs med de angivna EK-klassgränserna i tabellerna 6.2-6.7. 
        """
        by_period['variance'] = np.nan
        by_period['p_ges'] = np.nan
        return by_date, by_year_pos, by_year, by_period
                
       
    
###############################################################################
class IndicatorSecchi(IndicatorBase): 
    """
    Class with methods for Secchi indicator. 
    """
    
    def __init__(self, subset_uuid, parent_workspace_object, indicator):
        super().__init__(subset_uuid, parent_workspace_object, indicator) 
        self.indicator_parameter = self.parameter_list[0]  
        self.salt_parameter = self.parameter_list[-1]
        # Set dataframe to use        
        self._set_water_body_indicator_df(water_body = None)
        
    ###############################################################################   
    def calculate_status(self, water_body):
        """
        Calculates indicator Ecological Ratio (ER) values, for nutrients this means reference value divided by observed value.
        Transforms ER values to numeric class values (num_class)
        tolerance_filters is a dict with tolerance filters for the 
        """
        """
        Vid statusklassificering ska värden från ytvattnet användas (0-10 meter eller den övre vattenmassan om språngskiktet är grundare än 10 meter).
        Om mätningar vid ett tillfälle är utförda vid diskreta djup, 
        exempelvis 0, 5 och 10 meter ska EK-värde beräknas för varje mätning och ett medel–EK skapas för de tre djupen.
        """
        
        def set_value_above_one(x):
            #y = x.indicator_parameter/x.REFERENCE_VALUE
            if x > 1:
                return 1
            else:
                return x
                    
        # Set up result class
#        self.classification_results.add_info('parameter', self.indicator_parameter)
#        self.classification_results.add_info('salt_parameter', self.salt_parameter)
        
#        self._set_water_body_indicator_df(water_body)
        # get data to be used for status calculation, not deep copy because local_EQR values are relevant to see together with data
        if water_body not in self.water_body_indicator_df.keys():
            return False, False, False, False
        df = self.water_body_indicator_df[water_body]
        if water_body == 'SE603650-174500':
            print(df.head())
        if len(df) < 1:
            return False, False, False, False
               
        if len(df.VISS_EU_CD.unique()) > 1:
                    #TODO hur ska vi hantera detta om vi tillåter val av stationer i angränsande waterbody?
            raise Exception('more than one waterbody in dataframe') 
            
        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        if type_area == None:
            return False, False, False, False
        
#        self._add_wb_name_to_df(df, water_body)
        # add dataframe to resultsclass
#        self.classification_results.add_info(water_body, df)
        
        """ 
        1) Beräkna local_EQR för varje enskilt prov.
        
        """
#        agg_dict1 = {self.indicator_parameter: 'mean', self.salt_parameter: 'mean', 'DEPH': 'count', 'VISS_EU_CD': 'max', 'WATER_BODY_NAME': 'max', 'WATER_TYPE_AREA': 'max'}       
        agg_dict1 = {self.indicator_parameter: 'mean', self.salt_parameter: 'mean', 
                     'REFERENCE_VALUE': 'mean', 'HG_VALUE_LIMIT': 'mean', 'GM_VALUE_LIMIT': 'mean', 'MP_VALUE_LIMIT': 'mean', 'PB_VALUE_LIMIT': 'mean', 
                     'DEPH': 'count', 'VISS_EU_CD': 'max', 'WATER_BODY_NAME': 'max', 'WATER_TYPE_AREA': 'max'}       
        agg_dict2 = {key: 'mean' for key in self.additional_parameter_list}       
        
        by_date = df.groupby(['SDATE', 'YEAR', 'STATN']).agg({**agg_dict1, **agg_dict2}).reset_index()
        by_date.rename(columns={'DEPH':'DEPH_count'}, inplace=True)
#        by_date = self._add_reference_value_to_df(df, water_body)
        by_date['local_EQR'] = by_date[self.indicator_parameter]/by_date.REFERENCE_VALUE
#        by_date['local_EQR'] = by_date['local_EQR'].apply(set_value_above_one)
        by_date['global_EQR'], by_date['STATUS'] = zip(*by_date['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
        if water_body == 'SE603650-174500':
            print(by_date)
#        df['local_EQR'] = df[self.indicator_parameter]/df.REFERENCE_VALUE
#        df['local_EQR'] = df['local_EQR'].apply(set_value_above_one)
#        df['global_EQR'], df['STATUS'] = zip(*df['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
#        

        by_year_pos = False
        by_year = False    
        """
        2) Medelvärdet av local_EQR för varje siktdjup och vattenförekomst (beräknas för minst
        en treårsperiod)
        """
        agg_dict1 = {'local_EQR': 'mean', self.indicator_parameter: 'mean', 'YEAR': 'count', 'WATER_BODY_NAME': 'max', 'WATER_TYPE_AREA': 'max'}       
        if len(self.additional_parameter_list) > 0:
            agg_dict2 = {key: 'mean' for key in self.additional_parameter_list}
        else: agg_dict2 = {}  

        by_period = by_date.groupby(['VISS_EU_CD']).agg({**agg_dict1}).reset_index() #, **agg_dict2
        by_period.rename(columns={'YEAR':'YEAR_count'}, inplace=True)
        by_period['global_EQR'], by_period['STATUS'] = zip(*by_period['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR, water_body = water_body))
        by_period['STATIONS_USED'] = ', '.join(by_date.STATN.unique())      	        
        
        min_nr_years = self.tolerance_settings.get_min_nr_years(water_body = water_body) 
        boolean_list = by_period['YEAR_count'] >= min_nr_years
        by_period['ok'] = False
        by_period.loc[boolean_list, 'ok'] = True
        
        by_period['variance'] = np.nan
        by_period['p_ges'] = np.nan
        return by_date, by_year_pos, by_year, by_period
    
###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "indicators.py"')
    print('-'*50)
    print('')
    
    core.ParameterList()
    
    raw_data_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/raw_data/data_BAS_2000-2009.txt'
    
    first_data_filter_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filters/first_data_filter.txt'
    first_filter = core.DataFilter('First filter', file_path=first_data_filter_file_path)
    
    winter_data_filter_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filters/winter_data_filter.txt'
    winter_filter_1 = core.DataFilter('winter_filter', file_path=winter_data_filter_file_path)
    
    tolerance_filter_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filters/tolerance_filter_template.txt'
    
    raw_data = core.DataHandler('raw')
    raw_data.add_txt_file(raw_data_file_path, data_type='column') 
    
    filtered_data = raw_data.filter_data(first_filter)
    
    print('-'*50)
    print('done')
    print('-'*50)
    
    