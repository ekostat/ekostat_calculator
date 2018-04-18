# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:24:34 2017

@author: a001985
"""
import numpy as np

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
        self['water_body'] = None
        self['all_data'] = None
        self['all_ok'] = False
        self['water_body_status'] = None
        
        self._set_attributes()
        
    #========================================================================== 
    def _set_attributes(self):
        for key in self.keys():
            setattr(self, key, self[key])
            
    #========================================================================== 
    def add_info(self, key, value): 
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
        self.name = indicator
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
        # attributes that will be calculated
        self.water_body_indicator_df = {}
        self.classification_results = {}
         
    #==========================================================================
    def _set_directories(self):
        #set paths
        self.paths = {}
        self.paths['output'] = self.step_object.paths['directory_paths']['output'] 
        self.paths['results'] = self.step_objectf.paths['directory_paths']['results']
    
    #==========================================================================
    def _add_reference_value_to_df(self, df, type_area):    
        """
        Created:        20180328     by Lena
        Last modified:  
        add reference value to dataframe
        Nutrient reference values: Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vidvarje enskilt prov.
        Chl, Biov, Secchi in type 8, 12, 13, 24: Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vidvarje enskilt prov.
        """
        
        if self.get_ref_value_type(type_area) == 'str':
            df['REFERENCE_VALUE'] = np.nan
            for ix in df.index:
                salinity = df['SALT_CTD'][ix]
                df['REFERENCE_VALUE'].loc[ix] = self.get_ref_value(type_area, salinity)
        else:
            df['REFERENCE_VALUE'] = self.get_ref_value(type_area)
                                    
        return df
    
    #==========================================================================
    def get_filtered_data(self, subset=None, step=None, type_area=None, indicator=None):
        """
        Filter for water_body and indicator means filters from indicator_settings are applied.
        But the filters are only applied if they first are added to the index_handler so need to check if water_body and indicator have filters added
        """

        return self.index_handler.get_filtered_data(subset, step, type_area, indicator)
   
    #==========================================================================
    def get_numerical_class(self, ek, type_area):
        """
        Calculates indicator class (Nklass) according to eq 2.1 in HVMFS 2013:19.
        Returns a tuple with four values, low, ek_low, ek_heigh and the resulting Nklass.
        This is specific for the nutrient and phytoplankton indicators.
        There needs to be:
            - one def to get nutrient num_class for nutrient indicators (this one as is)
            - one def to get indicator class and value with the indicator specific EQR and the EQR transformed to the common scale
            (for nutrients that is num_class on scale 0-4.99 for most others some values on a 0-1 scale)
        """
        # Get EQR-class limits for the type area to be able to calculate the weighted numerical class
        HG_EQR_LIMIT = self.ref_settings.get_value(variable = 'HG_EQR_LIMIT', type_area = type_area)
        GM_EQR_LIMIT = self.ref_settings.get_value(variable = 'GM_EQR_LIMIT', type_area = type_area)
        MP_EQR_LIMIT = self.ref_settings.get_value(variable = 'MP_EQR_LIMIT', type_area = type_area)
        PB_EQR_LIMIT = self.ref_settings.get_value(variable = 'PB_EQR_LIMIT', type_area = type_area)
        
        if self.name == 'BQI' or self.name.lower() == 'secchi' or self.name.lower() == 'oxygen':
            return False
        else:
            if ek > HG_EQR_LIMIT: 
                status = 'HIGH'
                n_low = 4 
                ek_high = 1
                ek_low = HG_EQR_LIMIT
                
            elif ek > GM_EQR_LIMIT:
                status = 'GOOD'
                n_low = 3 
                ek_high = HG_EQR_LIMIT
                ek_low = GM_EQR_LIMIT
    
            elif ek > MP_EQR_LIMIT:
                status = 'MODERATE'
                n_low = 2 
                ek_high = GM_EQR_LIMIT
                ek_low = MP_EQR_LIMIT
                
            elif ek > PB_EQR_LIMIT:
                status = 'POOR'
                n_low = 1 
                ek_high = MP_EQR_LIMIT
                ek_low = PB_EQR_LIMIT
                
            else:
                status = 'BAD'
                n_low = 0 
                ek_high = PB_EQR_LIMIT
                ek_low = 0
            
            # Weighted numerical class
            n_class = n_low + (ek - ek_low)/(ek_high-ek_low)
            
            return n_low, ek_low, ek_high, status, n_class
    
    #==========================================================================
    def get_water_body_indicator_df(self, water_body = None, level = None):
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
        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        df = self.get_filtered_data(subset = self.subset, step = 'step_2', type_area = type_area, indicator = self.name)
        df = df[self.column_list]
        try:
            df =  df[df['VISS_EU_CD'] == water_body]
        except NameError:
            raise NameError('Must give water_body to get indicator_df')
        
        df = self._add_reference_value_to_df(df, type_area)
        self.water_body_indicator_df[water_body] = df
    
    #==========================================================================        
    def get_ref_value_type(self, type_area = None, get_type = True):
        """
        Created:        20180328     by Lena
        Last modified:  
        Get referencevalue either from equation or directly from settings
        To get reference value from equation you need to supply both type_area and salinity
        """
        return self.ref_settings.get_ref_value_type(type_area)
    
    #==========================================================================        
    def get_ref_value(self, type_area = None, salinity = None):
        """
        Created:        20180328     by Lena
        Last modified:  
        Get referencevalue either from equation or directly from settings
        To get reference value from equation you need to supply both type_area and salinity
        
        """
        return self.ref_settings.get_ref_value(type_area, salinity)
    
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
    Class with methods incommon for BQI indicator. 
    """
    
    def __init__(self, subset, parent_workspace_object, indicator):
        super().__init__(subset, parent_workspace_object, indicator)  
        
###############################################################################
class IndicatorNutrients(IndicatorBase): 
    """
    Class with methods common for all nutrient indicators (TOTN, DIN, TOTP and DIP). 
    """
    
    def __init__(self, subset, parent_workspace_object, indicator):
        super().__init__(subset, parent_workspace_object, indicator)  
        self.indicator_parameter = self.parameter_list[0]
        self.salt_parameter = self.parameter_list[1]
        
    def calculate_ek_value(self, water_body):
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
        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        
        """ 
        1) Beräkna EK för varje enskilt prov utifrån (ekvationer för) referensvärden i tabellerna 6.2-6.7.
        Beräkna EK-värde för varje mätning och sedan ett medel-EK för varje specifikt mättillfälle.
        
        """
        
        df['ek_value'] = df[self.indicator_parameter]/df.REFERENCE_VALUE
        df['ek_value'] = df['ek_value'].apply(set_value_above_one)
        
        # add datafram to resultsclass
        self.classification_results[water_body].add_info('all_data', df)
        
        #par_df['REFERENCE_VALUE']/par_df[self.indicator_parameter]
        #par_df['ek_value_calc'] = par_df['ek_value_calc'].apply(set_value_above_one)
        
        # calculate mean, max, min and count for EK values per measurement occasion. Here measurements on one day count as one occasion
        # .reset_index keeps all df column headers
        # TODO: what about different stations in one waterbody?
        by_date = df.groupby(['SDATE', 'YEAR'],).ek_value.agg(['count', 'min', 'max', 'mean']).reset_index()
        # by_occasion.to_csv(self.paths['results'] +'/' + self.name + water_body +'by_occation.txt', sep='\t')
        by_date.rename(columns={'mean':'mean_ek_value', 'count': 'number_of_values'}, inplace=True) # Cant use "mean" below
        
        # Remove occations with not enough samples
        # Or use count as a flag for what to display for the user?
            
        """
        2) Medelvärdet av EK för varje parameter beräknas för varje år.
        """
        by_year = by_date.groupby('YEAR').mean_ek_value.agg(['count', 'min', 'max', 'mean'])
        by_year.rename(columns={'mean':'mean_ek_value', 'count': 'number_of_dates'}, inplace=True)
        # by_year.to_csv(self.paths['results'] +'/' + self.name + water_body + 'by_year.txt', sep='\t')
        #by_year['all_ok'] = True
        #ix = by_year.loc[by_year['number_of_dates'] < self.tolerance_settings.get_min_nr_values(type_area), 'all_ok'].index
        #by_year.set_value(ix, 'all_ok', False)
        
        """
        3) Medelvärdet av EK för varje parameter och vattenförekomst (beräknas för minst
        en treårsperiod)
        """
        by_period = by_year[['mean_ek_value']].describe()
        by_period = by_period.transpose()
        limit = self.tolerance_settings.get_value(variable = 'MIN_NR_YEARS', type_area = type_area)
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
        num_class = self.get_numerical_class(by_period['mean'].get_value('mean_ek_value'), type_area = type_area)
        
        # Add waterbody status to result class
        self.classification_results[water_body].add_info('mean_EQR_by_date', by_date)
        self.classification_results[water_body].add_info('mean_EQR_by_year', by_year)
        self.classification_results[water_body].add_info('mean_EQR_by_period', by_period['mean'].get_value('mean_ek_value'))
        self.classification_results[water_body].add_info('number_of_years', by_period['count'].get_value('mean_ek_value'))
        self.classification_results[water_body].add_info('all_ok', all_ok)
        self.classification_results[water_body].add_info('numerical_class', num_class[-1])
        self.classification_results[water_body].add_info('status', num_class[-2])
                
        """
        5) EK vägs samman för ingående parametrar (tot-N, tot-P, DIN och DIP) enligt
        beskrivning nedan (6.4.2) för slutlig statusklassificering av hela kvalitetsfaktorn.
        Görs i quality_factors, def calculate_quality_factor()
        """
        

###############################################################################
class IndicatorOxygen(IndicatorBase): 
    """
    Class with methods incommon for BQI indicator. 
    """
    
    def __init__(self, subset, parent_workspace_object, indicator):
        super().__init__(subset, parent_workspace_object, indicator)  
    
###############################################################################
class IndicatorPhytoplankton(IndicatorBase): 
    """
    Class with methods incommon for BQI indicator. 
    """
    
    def __init__(self, subset, parent_workspace_object, indicator):
        super().__init__(subset, parent_workspace_object, indicator) 
        self.indicator_parameter = self.parameter_list[0]
        self.salt_parameter = self.parameter_list[1]
        
    def calculate_ek_value(self, water_body):
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
        type_area = self.mapping_objects['water_body'].get_type_area_for_water_body(water_body, include_suffix=True)
        
        """ 
        1) Beräkna EK för varje enskilt prov utifrån (ekvationer eller givna värden för) referensvärden.
        Beräkna EK-värde för varje enskilt prov och sedan ett medel-EK för varje år och station.
        
        """
        
        df['ek_value'] = df[self.indicator_parameter]/df.REFERENCE_VALUE
        df['ek_value'] = df['ek_value'].apply(set_value_above_one)
        
        # add datafram to resultsclass
        self.classification_results[water_body].add_info('all_data', df)
            
        """
        2) Medelvärdet av EK för parametern beräknas för varje år och station.
        """
        by_year_pos = df.groupby(['YEAR', 'POSITION']).mean_ek_value.agg(['count', 'min', 'max', 'mean'])
        by_year_pos.rename(columns={'mean':'mean_ek_value', 'count': 'number_of_dates'}, inplace=True)
        
        """
        3) Medelvärdet av EK för parametern beräknas för varje år.
        """
        by_year = by_year_pos.groupby('YEAR').mean_ek_value.agg(['count', 'min', 'max', 'mean'])
        by_year.rename(columns={'mean':'mean_ek_value', 'count': 'number_of_dates'}, inplace=True)
  
        """
        4) Medelvärdet av EK för varje parameter och vattenförekomst (beräknas för minst
        en treårsperiod)
        """
        by_period = by_year[['mean_ek_value']].describe()
        by_period = by_period.transpose()
        limit = self.tolerance_settings.get_value(variable = 'MIN_NR_YEARS', type_area = type_area)
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
        num_class = self.get_numerical_class(by_period['mean'].get_value('mean_ek_value'), type_area = type_area)
        
        # Add waterbody status to result class
        self.classification_results[water_body].add_info('mean_EQR_by_year_pos', by_year_pos)
        self.classification_results[water_body].add_info('mean_EQR_by_year', by_year)
        self.classification_results[water_body].add_info('mean_EQR_by_period', by_period['mean'].get_value('mean_ek_value'))
        self.classification_results[water_body].add_info('number_of_years', by_period['count'].get_value('mean_ek_value'))
        self.classification_results[water_body].add_info('all_ok', all_ok)
        self.classification_results[water_body].add_info('numerical_class', num_class[-1])
        self.classification_results[water_body].add_info('status', num_class[-2])
                
    
###############################################################################
class IndicatorSecchi(IndicatorBase): 
    """
    Class with methods incommon for BQI indicator. 
    """
    
    def __init__(self, subset, parent_workspace_object, indicator):
        super().__init__(subset, parent_workspace_object, indicator)  
        
            
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
    
    