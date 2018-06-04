# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:24:34 2017

@author: a001985
"""
import numpy as np
import pandas as pd

import core 

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
        self['status_by_date'] = pd.DataFrame(columns = ['VISS_EU_CD', 'WATER_TYPE_AREA',
                                'DATE', 'STATUS	VALUE', 'REF VALUE', 'local_EQR','	global_EQR'])
        self['status_by_year'] = pd.DataFrame(columns = ['VISS_EU_CD', 'WATER_TYPE_AREA',
                                'YEAR', 'STATUS	VALUE', 'REF VALUE', 'local_EQR','	global_EQR','Number of DATES', 'MONTHS INCLUDED'])
        self['status_by_period'] = pd.DataFrame(columns = ['VISS_EU_CD', 'WATER_TYPE_AREA',
                                'PERIOD', 'STATUS','global_EQR','	Number of YEARS', 'YEARS INCLUDED'])
        
        self._set_attributes()
        
    #========================================================================== 
    def _set_attributes(self):
        for key in self.keys():
            setattr(self, key, self[key])
            
    #========================================================================== 
    def add_info(self, key, value): 
        try:
            existing_value = getattr(self, key)
            if getattr(self, key) != value:
                raise('Error: Trying to set new value to existing attribute. new value {} does not match old value {} for attribute {}'.format(value, existing_value, key))
        except AttributeError:
            #Varför både nyckel och attribut?
            self[key] = value
            setattr(self, key, value)
        

###############################################################################
class IndicatorBase(object): 
    """
    Class to calculate status for a specific indicator. 
    """ 
    def __init__(self, subset, parent_workspace_object, indicator):
        """
        setup indicator class attributes based on subset, parent workspace object and indicator name
        """
        self.name = indicator.lower()
        print('********')
        print(self.name)
        self.class_result = None
        self.subset = subset
        self.step = 'step_3'
        # from workspace
        self.parent_workspace_object = parent_workspace_object
        self.mapping_objects = self.parent_workspace_object.mapping_objects
        self.index_handler = self.parent_workspace_object.index_handler
        self.step_object = self.parent_workspace_object.get_step_object(step = 3, subset = self.subset)
        # from SettingsFile
        self.tolerance_settings = self.parent_workspace_object.get_step_object(step = 2, subset = subset).get_indicator_tolerance_settings(self.name)
        self.ref_settings = self.parent_workspace_object.get_step_object(step = 2, subset = subset).get_indicator_ref_settings(self.name)
        # To be read from config-file
        self.meta_columns = ['SDATE', 'YEAR', 'MONTH', 'POSITION', 'VISS_EU_CD', 'WATER_TYPE_AREA', 'DEPH']
        self.parameter_list =  [item.strip() for item in self.mapping_objects['quality_element'].indicator_config.loc[self.name]['parameters'].split(', ')] #[item.strip() for item in self.parent_workspace_object.cfg['indicators'].loc[self.name][0].split(', ')]
        self.column_list = self.meta_columns + self.parameter_list
        self.indicator_parameter = self.parameter_list[0]
        # attributes that will be calculated
        self.water_body_indicator_df = {}
        self.classification_results = ClassificationResult()
        # perform checks before continuing
        self._check()
        self._set_directories()
        
        
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
    def _add_reference_value_to_df(self, df, water_body):    
        """
        Created:        20180426     by Lena
        Last modified:  
        add reference value to dataframe
        Nutrient reference values: Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vidvarje enskilt prov.
        Chl, Biov, Secchi in type 8, 12, 13, 24: Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vidvarje enskilt prov.
        """
        print(water_body,len(self.ref_settings.settings.refvalue_column))
        if len(self.ref_settings.settings.refvalue_column) == 0:
            return df
        
        print(self.get_ref_value_type(water_body = water_body))
        if self.get_ref_value_type(water_body = water_body) == 'str':
            print('ref_value is str')
            df['REFERENCE_VALUE'] = np.nan
            for ix in df.index:
                salinity = df['SALT'][ix]
                print(repr(salinity))
                df['REFERENCE_VALUE'].loc[ix] = self.get_ref_value(water_body = water_body, salinity = salinity)
        else:
            df['REFERENCE_VALUE'] = self.get_ref_value(water_body)
                                    
        return df

    #==========================================================================
    def _calculate_global_EQR_from_indicator_value(self, water_body = None, value = None):
        """
        Calculates EQR from local_EQR values according to eq. 1 in WATERS final report p 153.
        Boundaries for all classes are read from RefSettings object
        boundarie_variable is used to retrieve class boundaries from settings file and must match the type of value
        This is only valid for values with increasing quality (higher value = higher EQR)
        """
        
        if not value:
            value = getattr(self.classification_results[water_body], 'value')
        if value < 0:
            raise('Error: _calculate_global_EQR_from_indicator_value: {} value below 0.'.format(value))
        # Get EQR-class limits for the type area to be able to calculate the weighted numerical class
        REF_VALUE = self.ref_settings.get_ref_value(water_body = water_body)
        HG_VALUE_LIMIT = self.ref_settings.get_value(variable = 'HG_VALUE_LIMIT', water_body = water_body)
        GM_VALUE_LIMIT = self.ref_settings.get_value(variable = 'GM_VALUE_LIMIT', water_body = water_body)
        MP_VALUE_LIMIT = self.ref_settings.get_value(variable = 'MP_VALUE_LIMIT', water_body = water_body)
        PB_VALUE_LIMIT = self.ref_settings.get_value(variable = 'PB_VALUE_LIMIT', water_body = water_body)

#        if self.name == 'BQI'  or self.name.lower() == 'oxygen':
        if HG_VALUE_LIMIT - GM_VALUE_LIMIT > 0:
            if value > HG_VALUE_LIMIT: 
                status = 'HIGH'
                global_low = 0.8 
                high_value = REF_VALUE #This should be the highest value possible
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
             # When higher value means lower status (decreasing)
            if value > PB_VALUE_LIMIT:
                status = 'BAD'
                global_low = 0.2
                high_value = 1
                # om värde ist för ek ska ek_high vara ref_värdet eller Bmax värde
                low_value = PB_VALUE_LIMIT
                if value > REF_VALUE:
                    value = 1
                
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
                if value < Bmin:
                    value = 0
                
                    
        print('******',REF_VALUE,'******')
        print('-------***-------')
        print(type(global_low), type(value), type(low_value), type(high_value))
        # Weighted numerical class
        global_EQR = global_low + (value - low_value)/(high_value-low_value)*0.2
        
        self.classification_results[water_body].add_info('global_EQR', global_EQR)
        self.classification_results[water_body].add_info('status', status)
    
    
    
    #==========================================================================
    def _calculate_global_EQR_from_local_EQR(self, water_body, local_EQR):
        """
        Calculates EQR from local_EQR values according to eq. 1 in WATERS final report p 153.
        Boundaries for all classes are read from RefSettings object
        boundarie_variable is used to retrieve class boundaries from settings file and must match the type of local_EQR_variable
        """
        if not local_EQR:
            local_EQR = getattr(self.classification_results[water_body], 'local_EQR')
        else:
            self.classification_results[water_body].add_info('local_EQR', local_EQR)
        
        if local_EQR < 0:
            raise('Error: _calculate_global_EQR_from_indicator_value: {} local_EQR value below 0.'.format(local_EQR))
        
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
            print(water_body)
            df = self.get_filtered_data(subset = self.subset, step = 'step_2', water_body = water_body, indicator = self.name).copy(deep = True)
            df = df[self.column_list]
            df = df.dropna(subset = [self.indicator_parameter])
            print(df.dtypes)
            df = self._add_reference_value_to_df(df, water_body)
            self.water_body_indicator_df[water_body] = df 
        else:
            print('water_body must be given to set_water_body_indicator_df')
            
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
    def get_ref_value(self, type_area = None, water_body = None, salinity = None):
        """
        Created:        20180328     by Lena
        Last modified:  
        Get referencevalue either from equation or directly from settings
        To get reference value from equation you need to supply both type_area and salinity
        
        """
        return self.ref_settings.get_ref_value(type_area = type_area, water_body = water_body, salinity = salinity)
    
    #==========================================================================
    def get_water_body_indicator_df(self, water_body = None):
        """
        Created:        20180215     by Lena
        Last modified:  20180328     by Lena
        df should contains:
            - all needed columns from get_filtered_data
            - referencevalues
        TODO: add other info needed for indicator functions
        """
        
        return self.water_body_indicator_df[water_body]


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
    
    def __init__(self, subset, parent_workspace_object, indicator):
        super().__init__(subset, parent_workspace_object, indicator) 
        self.indicator_parameter = self.parameter_list[0]
        self.column_list.remove('DEPH')
        self.column_list = self.column_list + ['MNDEP', 'MXDEP']
        
    def calculate_status(self, water_body):
        """
        Calculates indicatotr EQR for BQI values using bootstrap method described in HVMFS 2013:19
        """
        # get data to be used for status calculation
        df = self.water_body_indicator_df[water_body]
        #type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
       
        by_year_pos = df.groupby(['YEAR', 'POSITION'])[self.indicator_parameter].agg(['count', 'min', 'max', 'mean']).reset_index()
        by_year_pos.rename(columns={'mean':'position_mean', 'count': 'position_count', 'min': 'position_min', 'max': 'station_max'}, inplace=True)

        by_year = by_year_pos.groupby(['YEAR']).position_mean.agg(['count', 'min', 'max', 'mean']).reset_index()

        # Random selection with replacement of as many values as there are station means (frac = 1)
        # TODO: spead-up! Is it possible more efficient way to get the list from the map object?
        def bootstrap(df):
            return df.sample(frac = 1, replace = True).mean()
        
        n = 9999
        BQIsim_year = []
        for ix, year in by_year.YEAR.items():
            print('number of stations in year ({}): {}'.format(year,len(by_year_pos['position_mean'])))
            print(by_year_pos.loc[by_year_pos.YEAR == year]['position_mean'])
            df_list = [by_year_pos.loc[by_year_pos.YEAR == year]['position_mean'].dropna()]*n
            print(water_body)
            BQIsim = [*map(bootstrap, df_list)]
#            BQIsim = []
#            for x in range(n):
#                BQIsim.append(by_year_pos.loc[by_year_pos.YEAR == year]['position_mean'].sample(frac = 1, replace = True).mean())
            percentile = np.percentile(BQIsim, 0.2) 
            print(percentile)            
            BQIsim_year.append(percentile)
        print(BQIsim_year)
        periodmean = np.mean(BQIsim_year)
        
        # TODO: Add BQImax to settingsfile (from handbok or ask Mats L). Call _calculate_global_EQR and add results to resul class
        return periodmean
        
###############################################################################
class IndicatorNutrients(IndicatorBase): 
    """
    Class with methods common for all nutrient indicators (TOTN, DIN, TOTP and DIP). 
    """
    
    def __init__(self, subset, parent_workspace_object, indicator):
        super().__init__(subset, parent_workspace_object, indicator)  
        self.indicator_parameter = self.parameter_list[0]
        self.salt_parameter = self.parameter_list[1]
        
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
        self.classification_results.add_info('parameter', self.indicator_parameter)
        self.classification_results.add_info('salt_parameter', self.salt_parameter)
        #self.classification_results.add_info('water_body', water_body)
        
        self._set_water_body_indicator_df(water_body)
        # get data to be used for status calculation, not deep copy because local_EQR values are relevant to see together with data
        df = self.water_body_indicator_df[water_body]
        
        """
        Calculate local_EQR (EK-värde)
        """        
        
        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        
        """ 
        1) Beräkna local_EQR (EK-värde) för varje enskilt prov utifrån (ekvationer för) referensvärden i tabellerna 6.2-6.7.
        Beräkna local_EQR (EK-värde) för varje mätning och sedan ett medel-EK för varje specifikt mättillfälle.
        TO BE UPDATED TO local_EQR for mean of nutrient conc and salinity 0-10 m.
        
        """
        
        df['local_EQR'] = df.REFERENCE_VALUE/df[self.indicator_parameter]
        df['local_EQR'] = df['local_EQR'].apply(set_value_above_one) 
        # TODO: should the set to one be done before or after all the means below?
        df['global_EQR'] = df['local_EQR'].apply(self._calculate_global_EQR_from_local_EQR) 
        
        # add dataframe to resultsclass
        self.classification_results.add_info(water_body, df)
        #self.classification_results[water_body].add_info('all_data', df)
        
        # calculate mean, max, min and count for local_EQR per measurement occasion. Here measurements on one day count as one occasion
        # .reset_index keeps all df column headers
        # TODO: what about different stations in one waterbody?
        by_date = df.groupby(['SDATE', 'YEAR'],).local_EQR.agg(['count', 'min', 'max', 'mean']).reset_index()
        # by_occasion.to_csv(self.paths['results'] +'/' + self.name + water_body +'by_occation.txt', sep='\t')
        by_date.rename(columns={'mean':'mean_local_EQR', 'count': 'number_of_values'}, inplace=True) # Cant use "mean" below
        by_date['WATER_TYPE_AREA'] = type_area
        by_date['VISS_EU_CD'] = water_body
        self['status_by_date'] = by_date 
            #pd.DataFrame(columns = ['VISS_EU_CD', 'WATER_TYPE_AREA', 'DATE', 'STATUS	VALUE', 'REF VALUE', 'local_EQR','	global_EQR'])
        # Remove occations with not enough samples
        # Or use count as a flag for what to display for the user?
            
        """
        2) Medelvärdet av EK för varje parameter beräknas för varje år.
        """
        by_year = by_date.groupby('YEAR').mean_local_EQR.agg(['count', 'min', 'max', 'mean'])
        by_year.rename(columns={'mean':'mean_local_EQR', 'count': 'number_of_dates'}, inplace=True)
        by_year['WATER_TYPE_AREA'] = type_area
        by_year['VISS_EU_CD'] = water_body      
        
        self['status_by_year'] = by_year 
        # by_year.to_csv(self.paths['results'] +'/' + self.name + water_body + 'by_year.txt', sep='\t')
        #by_year['all_ok'] = True
        #ix = by_year.loc[by_year['number_of_dates'] < self.tolerance_settings.get_min_nr_values(type_area), 'all_ok'].index
        #by_year.set_value(ix, 'all_ok', False)
        
        """
        3) Medelvärdet av EK för varje parameter och vattenförekomst (beräknas för minst
        en treårsperiod)
        """
        by_period = by_year[['mean_local_EQR']].describe()
        by_period = by_period.transpose()
        limit = self.tolerance_settings.get_value(variable = 'MIN_NR_YEARS', water_body = water_body)
        #limit = self.tolerance_settings.get_min_nr_years(type_area = type_area)
        if by_period['count'].get_value('mean_local_EQR') >= limit:
            by_period['all_ok'] = False
        else:
            by_period['all_ok']  = True
                     
        all_ok = by_period['all_ok']    
        print('\t\t\t{} local_EQR Calculated'.format(self.name)) 
        print(by_period)
         
        """
        4) Statusklassificeringen för respektive parameter görs genom att medelvärdet av
        EK jämförs med de angivna EK-klassgränserna i tabellerna 6.2-6.7. 
        """
        global_EQR, status = self._calculate_global_EQR_from_local_EQR(water_body = water_body, local_EQR = by_period['mean'].get_value('mean_local_EQR')) 
        columns = ['VISS_EU_CD', 'WATER_TYPE_AREA',
                                'PERIOD', 'STATUS','global_EQR','	Number of YEARS', 'YEARS INCLUDED']
        values = [water_body, type_area, 'x', status, global_EQR, by_period['count'].get_value('mean_local_EQR'), 'x']
        self['status_by_year'].append(pd.DataFrame(values, columns=columns))

        # Add waterbody status to result class
#        self.classification_results[water_body].add_info('local_EQR_by_date', by_date)
#        self.classification_results[water_body].add_info('local_EQR_by_year', by_year)
#        self.classification_results[water_body].add_info('local_EQR_by_period', by_period['mean'].get_value('mean_local_EQR'))
#        self.classification_results[water_body].add_info('number_of_years', by_period['count'].get_value('mean_local_EQR'))
#        self.classification_results[water_body].add_info('all_ok', all_ok)
#                
        """
        5) EK vägs samman för ingående parametrar (tot-N, tot-P, DIN och DIP) enligt
        beskrivning nedan (6.4.2) för slutlig statusklassificering av hela kvalitetsfaktorn.
        Görs i quality_factors, def calculate_quality_factor()
        """
        
###############################################################################
class IndicatorOxygen(IndicatorBase): 
    """
    Class with methods for Oxygen indicator. 
    """
    
    def __init__(self, subset, parent_workspace_object, indicator):
        super().__init__(subset, parent_workspace_object, indicator)  
        self.indicator_parameter = self.parameter_list[0]
        self.Hypsographs = self.mapping_objects['hypsographs']
        self.column_list = self.column_list + ['source_DOXY']
        self.deficiency_limit = 3.5
        self.test1_result_list = []
        self.test2_result_list = []
        self.df_bottomwater = {}
        
    ############################################################################### 
    def _get_status_from_classboundaries(self, value, water_body):
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
        
        return status, value     
    
    ###############################################################################        
    def _get_affected_area_fraction(self, df, water_body):
       
        # df = df[df['MONTH'].isin(list(range(1,5+1)))]
        maxD = self.Hypsographs.get_max_depth_of_water_body(water_body)
        minimum_deficiency_depth = df[df[self.indicator_parameter] <= self.deficiency_limit, 'DEPH'].min()
        print(minimum_deficiency_depth)
        if minimum_deficiency_depth > maxD:
            minimum_deficiency_depth = maxD
        affected_area_fraction = self.Hypsographs.get_area_fraction_at_depth(self, water_body=water_body, depth=minimum_deficiency_depth)
        
        return affected_area_fraction
    
    ###############################################################################        
    def _mean_of_quantile(self, df = None, water_body = None, month_list = None):
        """
        Calculates mean of the 25% percentile for each posisition in the waterbody using data from the given months
        """
        if month_list:
            df = df[df['MONTH'].isin(list(range(1,5+1)))]
        if len(df['YEAR'].unique()) >= 3:
            tol_BW = 5
            maxD = self.Hypsographs.get_max_depth_of_water_body(water_body)
            value_list = []
            deph_list = []
            for key, group in df.groupby(['POSITION']):
                group.reset_index()
                q = group.loc[group['DEPH'] > maxD-tol_BW,self.indicator_parameter].quantile(0.25)
                print(group.loc[group['DEPH'] > maxD-tol_BW])
                #deph_list
                value_list.append(group.loc[group[self.indicator_parameter] < q, self.indicator_parameter].mean())
        else:
            value_list = None
            
        return value_list

    ###############################################################################    
    def _test1(self, df, water_body):
        """
        To decide if the water body suffers from oxygen deficiency or not.
        Takes bottomwater data for the whole year and checks if the mean of the 25% percentile is above or below limit
        """
        result_list = self._mean_of_quantile(df = df, water_body = water_body, month_list = None)
        self.test1_result_list = result_list
        
        if all(r > self.deficiency_limit for r in result_list):
            return 'High'
        elif any(r <= self.deficiency_limit for r in result_list):
            return True
        else:
            return None
    
    ###############################################################################    
    def _test2(self, df, water_body):
        """
        To decide if the water body suffers from seasonla or longterm oxygen deficiency.
        Takes bottomwater data for jan-maj and for every position checks if the mean of the 25% percentile is above or below limit 
        """
        month_list = list(range(6,5+1))
        result = self._mean_of_quantile(df = df, water_body = water_body, month_list = month_list)
        self.test2_result_list = result
        
        status = None 
        deficiency_type = None
        
        if all(r > self.deficiency_limit for r in self.test2_result_list):
            # seasonal oxygen deficiency
            deficiency_type = 'seasonal'
            value = min(self.test2_result_list)
            status, value = self._get_status_from_classboundaries(value, water_body)
        elif any(r <= self.deficiency_limit for r in self.test2_result_list):
            # Methods to determine longterm oxygen deficiency (perennial and permanent)
            deficiency_type = 'longterm'
            month_list = list(range(6,12+1))
            df = df[df['MONTH'].isin(month_list)]
            if len(df['YEAR'].unique()) >= 3:
                affected_area_fraction = self._get_affected_area_fraction(df, water_body)
                status, value = self._get_status_from_classboundaries(affected_area_fraction*100, water_body)
            else:
                status, value = None, None
            
        else:
            status = None
        
        return status, value, deficiency_type
    
    ############################################################################### 
    def calculate_status(self, water_body):
        """
        Created     20180426    by Lena Viktorsson
        Updated     20180426    by Lena Viktorsson
        Method to calculate status for oxygen indicator
        """
        # set or get waterbody df
        if water_body not in self.water_body_indicator_df.keys():
            self.set_water_body_indicator_df()
            
        df = self.get_water_body_indicator_df(water_body = water_body) #self.get_filtered_data(subset = self.subset, step = 'step_2', water_body = water_body)
        
        # Set up result class 
        if water_body not in self.classification_results.keys():
            self.classification_results[water_body] = ClassificationResult()
        self.classification_results[water_body].add_info('parameter', self.indicator_parameter)
        self.classification_results[water_body].add_info('water_body', water_body)
        self.classification_results[water_body].add_info('data_used', df)
        
        
        # Test1 checks of the waterbody suffers from oxygen deficiency or not
        status = self._test1(df, water_body)
        deficiency_type = None
        
        if status:
            if status == 'High':
                value = min(self.test1_result_list)
                deficiency_type = 'no deficiency'
            else:
                # Test2 tests the type of oxygen deficiency if status was not 'High'.
                status, value, deficiency_type = self._test2(df, water_body)
        else:
            value = None
        
        # has only written global EQR calculation for increasing status indicator
        if deficiency_type in ['seasonal', 'no deficiency']:
            # Saves status and global_EQR to classification_results[water_body]
            self._calculate_global_EQR_from_indicator_value(water_body, value)
        # Calculated oxygen reference values from GM value limit and is using this to get a local_EQR value to transform to global_EQR
        if deficiency_type in ['longterm']:
            REF_VALUE_LIMIT = self.ref_settings.get_value(variable = 'REF_VALUE_LIMIT', water_body = water_body)
            local_EQR = REF_VALUE_LIMIT/value
            # Saves status and global_EQR to classification_results[water_body]
            self._calculate_global_EQR_from_local_EQR(water_body, local_EQR)
        
        self.classification_results[water_body].add_info('value', value)
        self.classification_results[water_body].add_info('test1_resultlist', self.test1_result_list)
        self.classification_results[water_body].add_info('test2_resultlist', self.test2_result_list)

    ###############################################################################     
    def set_water_body_indicator_df(self, water_body = None):
        """
        Created:        20180427     by Lena
        Last modified:  20180427     by Lena
        df should contain:
            - all needed columns from get_filtered_data
            - referencevalues
            - maybe other info needed for indicator functions
        skapa df utifrån:
        self.index_handler
        self.tolerance_settings
        self.indicator_ref_settings
        """
        
        if water_body:
            print(water_body)
            df = self.get_filtered_data(subset = self.subset, step = 'step_2', water_body = water_body).copy(deep = True)
            df = df.dropna(subset = [self.indicator_parameter])[self.column_list]
            self.water_body_indicator_df[water_body] = df 
            tol_BW = 5
            maxD = self.Hypsographs.get_max_depth_of_water_body(water_body)
            self.df_bottomwater[water_body] = df.loc[df['DEPH'] > maxD-tol_BW]
        else:
            print('water_body must be given to set_water_body_indicator_df')
          
    
###############################################################################
class IndicatorPhytoplankton(IndicatorBase): 
    """
    Class with methods incommon for Phytoplankton indicators. 
    """
    
    def __init__(self, subset, parent_workspace_object, indicator):
        super().__init__(subset, parent_workspace_object, indicator) 
        self.indicator_parameter = self.parameter_list[0]
        self.salt_parameter = self.parameter_list[1]
        
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
        # Set up result class 
        self.classification_results[water_body] = ClassificationResult()
        self.classification_results[water_body].add_info('parameter', self.indicator_parameter)
        self.classification_results[water_body].add_info('salt_parameter', self.salt_parameter)
        self.classification_results[water_body].add_info('water_body', water_body)
    
        """
        Calculate EK-value
        """
        def set_value_above_one(x):
            #y = x.indicator_parameter/x.REFERENCE_VALUE
            if x > 1:
                return 1
            else:
                return x
        
        # get data to be used for status calculation
        df = self.water_body_indicator_df[water_body]
        #type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        
        """ 
        1) Beräkna EK för varje enskilt prov utifrån (ekvationer eller givna värden för) referensvärden.
        Beräkna EK-värde för varje enskilt prov och sedan ett medel-EK för varje år och station.
        
        """
        
        df['local_EQR'] = df.REFERENCE_VALUE/df[self.indicator_parameter]
        df['local_EQR'] = df['local_EQR'].apply(set_value_above_one)
        
        # add datafram to resultsclass
        self.classification_results[water_body].add_info('all_data', df)
            
        """
        2) Medelvärdet av EK för parametern beräknas för varje år och station.
        """
        by_year_pos = df.groupby(['YEAR', 'POSITION']).local_EQR.agg(['count', 'min', 'max', 'mean']).reset_index()
        by_year_pos.rename(columns={'mean':'mean_local_EQR', 'count': 'number_of_dates'}, inplace=True)
        
        """
        3) Medelvärdet av local_EQR för parametern beräknas för varje år.
        """
        by_year = by_year_pos.groupby('YEAR').mean_local_EQR.agg(['count', 'min', 'max', 'mean'])
        by_year.rename(columns={'mean':'mean_local_EQR', 'count': 'number_of_positions'}, inplace=True)
  
        """
        4) Medelvärdet av EK för varje parameter och vattenförekomst (beräknas för minst
        en treårsperiod)
        """
        by_period = by_year[['mean_local_EQR']].describe()
        by_period = by_period.transpose()
        limit = self.tolerance_settings.get_value(variable = 'MIN_NR_YEARS', water_body = water_body)
        #limit = self.tolerance_settings.get_min_nr_years(type_area = type_area)
        if by_period['count'].get_value('mean_ek_value') >= limit:
            by_period['all_ok'] = False
        else:
            by_period['all_ok']  = True
                     
        all_ok = by_period['all_ok']    
        print('\t\t\t{} Ek value Calculated'.format(self.name)) 
        print(by_period)
         
        """
        4) Statusklassificeringen för respektive parameter görs genom att medelvärdet av
        EK jämförs med de angivna EK-klassgränserna i tabellerna 6.2-6.7. 
        """
        self._calculate_global_EQR_from_local_EQR(water_body = water_body, local_EQR = by_period['mean'].get_value('mean_local_EQR'))
        
        # Add waterbody status to result class
        self.classification_results[water_body].add_info('local_EQR_by_year_pos', by_year_pos)
        self.classification_results[water_body].add_info('local_EQR_by_year', by_year)
        self.classification_results[water_body].add_info('local_EQR_by_period', by_period['mean'].get_value('mean_local_EQR'))
        self.classification_results[water_body].add_info('number_of_years', by_period['count'].get_value('mean_local_EQR'))
        self.classification_results[water_body].add_info('all_ok', all_ok)
       
    
###############################################################################
class IndicatorSecchi(IndicatorBase): 
    """
    Class with methods  for Seccho indicator. 
    """
    
    def __init__(self, subset, parent_workspace_object, indicator):
        super().__init__(subset, parent_workspace_object, indicator) 
        self.indicator_parameter = self.parameter_list[0]  
        self.salt_parameter = self.parameter_list[1]
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
        # Set up result class 
        self.classification_results[water_body] = ClassificationResult()
        self.classification_results[water_body].add_info('parameter', self.indicator_parameter)
        self.classification_results[water_body].add_info('salt_parameter', self.salt_parameter)
        self.classification_results[water_body].add_info('water_body', water_body)
    
        """
        Calculate local_EQR
        """
        def set_value_above_one(x):
            #y = x.indicator_parameter/x.REFERENCE_VALUE
            if x > 1:
                return 1
            else:
                return x
        
        # get data to be used for status calculation
        df = self.water_body_indicator_df[water_body]
        #type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        
        """ 
        1) Beräkna EK för varje enskilt prov utifrån (ekvationer eller givna värden för) referensvärden.
        Beräkna EK-värde för varje enskilt prov och sedan ett medel-EK för varje år och station.
        
        """
        
        df['local_EQR'] = df[self.indicator_parameter]/df.REFERENCE_VALUE
        df['local_EQR'] = df['local_EQR'].apply(set_value_above_one)
        
        # add datafram to resultsclass
        self.classification_results[water_body].add_info('all_data', df)
            
        """
        2) Medelvärdet av local_EQR för varje siktdjup och vattenförekomst (beräknas för minst
        en treårsperiod)
        """
        by_period = df[['local_EQR']].describe()
        by_period = by_period.transpose()
        limit = self.tolerance_settings.get_value(variable = 'MIN_NR_YEARS', water_body = water_body)
        #limit = self.tolerance_settings.get_min_nr_years(type_area = type_area)
        if len(df['YEAR'].unique()) >= limit:
            by_period['all_ok'] = False
        else:
            by_period['all_ok']  = True
                     
        all_ok = by_period['all_ok']    
        print('\t\t\t{} Ek value Calculated'.format(self.name)) 
        print(by_period)
         
        """
        4) Statusklassificeringen för respektive parameter görs genom att medelvärdet av
        EK jämförs med de angivna EK-klassgränserna i tabellerna 6.2-6.7. 
        """
        self._calculate_global_EQR_from_local_EQR(water_body = water_body, local_EQR = by_period['mean'].get_value('local_EQR'))
        
        # Add waterbody status to result class
        self.classification_results[water_body].add_info('local_EQR_by_period', by_period['mean'].get_value('local_EQR'))
        self.classification_results[water_body].add_info('number_of_value', by_period['count'].get_value('local_EQR'))
        self.classification_results[water_body].add_info('all_ok', all_ok)    
            
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
    tolerance_filter = core.ToleranceFilter('test_tolerance_filter', file_path=tolerance_filter_file_path)
    
    raw_data = core.DataHandler('raw')
    raw_data.add_txt_file(raw_data_file_path, data_type='column') 
    
    filtered_data = raw_data.filter_data(first_filter)
    
    print('-'*50)
    print('done')
    print('-'*50)
    
    