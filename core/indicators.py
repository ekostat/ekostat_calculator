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
        self['type_area'] = None
        self['all_data'] = None
        self['mean_by_occasion'] = None
        self['mean_by_year'] = None 
        self['nr_years'] = None
        self['mean_total'] = None
        self['all_ok'] = False
        self['num_class'] = None
        
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
    def __init__(self, index_handler, data_filter_settings, tolerance_settings, ref_settings):
        self.name = ''
        self.parameter_list = []
        self.class_result = None
        self.subset = None
        self.step = None
        self.index_handler = index_handler
        self.tolerance_settings = tolerance_settings
        self.ref_settings = ref_settings

    def get_filtered_data(self, subset=None, step=None, water_body=None, indicator=None):
        """
        Filter for water_body and indicator means filters from indicator_settings are applied.
        But the filters are only applied if they first are added to the index_handler so need to check if water_body and indicator have filters added
        """

        return self.index_handler.get_filtered_data(subset, step, water_body, indicator)

    def get_indicator_df(self):
        """
        Created:        20180215     by Lena
        Last modified:  20180215     by Lena
        df should contain:
            - all needed columns from get_filtered_data
            - referencevalues
            - maybe other info needed for indicator functions
        skapa df utifrån:
        self.index_handler
        self.tolerance_settings
        self.indicator_ref_settings
        """
        pass
    
    #==========================================================================
    def get_ref_value_for_par_with_salt_ref(self, par=None, salt_par='SALT_CTD', indicator_name=None, tolerance_filter=None):
        """
        tolerance_filters is a dict with tolerance filters for the specific (sub) parameter. 
        """
        """
        Vid statusklassificering
        ska värden från ytvattnet användas (0-10 meter eller den övre vattenmassan
        om språngskiktet är grundare än 10 meter).
        
        Om mätningar vid ett tillfälle är utförda vid diskreta djup, exempelvis 0, 5 och 10
        meter ska EK-värde beräknas för varje mätning och ett medel–EK skapas för de tre
        djupen.
        """
#        class_result = ClassificationResult()
#        class_result.add_info('parameter', par)
#        class_result.add_info('salt_parameter', salt_par)
#        class_result.add_info('type_area', self.data_filter_object.TYPE_AREA.value)
        
        """
        För kvalitetsfaktorn Näringsämnen: 
        1) Beräkna EK för varje enskilt prov utifrån referensvärden i tabellerna 6.2-6.7.
        Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vid
        varje enskilt prov. Om mätningar är utförda vid diskreta djup, beräkna EKvärde
        för varje mätning och sedan ett medel-EK för varje specifikt mättillfälle.
        """
        
        ref_object = getattr(core.RefValues(), indicator_name.lower())[self.data_filter_object.TYPE_AREA.value]
#        self.ref_object = ref_object
        par_object = getattr(self, par.lower())
        salt_object = getattr(self, salt_par.lower())
        self.par_object = par_object
        self.salt_object = salt_object
        
        par_df = par_object.data.column_data.copy(deep=True)
        salt_df = salt_object.data.column_data
        
        par_df['salt_value_ori'] = np.nan 
        par_df['salt_value'] = np.nan 
        par_df['salt_index'] = np.nan 
        par_df['ref_value'] = np.nan 
        #par_df['ek_value_calc'] = np.nan 
        par_df['par_value'] = np.nan 
        for i in par_df.index:
#            self.i = i
            df_row = par_df.loc[i, :]
            par_value = df_row[par]
            if np.isnan(par_value):
                ref_value = np.nan
            else:
                try:
                    salt_df.loc[1, salt_par]
                    first_salt = 1 
                except KeyError:
                    # TODO: Why was default set to 1?
                    first_salt = salt_df.index[0]
                if i in salt_df.index and not np.isnan(salt_df.loc[first_salt, salt_par]): 
                    salt_value_ori = salt_df.loc[first_salt, salt_par]  # ska inte det vara: salt_df.loc[i, salt_par]?
                    salt_index = i
                else:
                    # TODO: If not allowed to continue
                    matching_salt_data = salt_object.get_closest_matching_data(df_row=df_row, 
                                                                             tolerance_filter=tolerance_filter)
                    if matching_salt_data.empty:
                        salt_value_ori = np.nan
                        salt_index = np.nan
                        self.missing = df_row
                    else:
                        self.matching_salt_data = matching_salt_data
                        salt_value_ori = matching_salt_data[salt_par]
                        salt_index = matching_salt_data.name
                        
                # Check salt for maximum value
                salt_value = ref_object.get_max_salinity(salt_value_ori)
                
                # Get ref value
                ref_value = ref_object.get_ref_value(salt_value)
                
                # Get EK-value
                
                # TODO: This differs between indicators, some are ref/obs other obs/ref
                # So this should not be in IndicatorBase, output from this def should be salt_val, ref_val och par_val
#                ek_value_calc = ref_value/par_value
                
#                self.salt_value = salt_value
#                self.ek_value_calc = ek_value_calc
#                self.ref_value = ref_value
#                self.par_value = par_value
#            print('ref_value', ref_value, '=', value)
#            self.df_row = df_row
#            self.salt_value = salt_value
            par_df.set_value(i, 'salt_value_ori', salt_value_ori) 
            par_df.set_value(i, 'salt_value', salt_value) 
            par_df.set_value(i, 'salt_index', salt_index)
            par_df.set_value(i, 'ref_value', ref_value)
            par_df.set_value(i, 'par_value', par_value)
            
            # Check ek_value_calc
#            ek_value = ek_value_calc
#            if ek_value > 1:
#                ek_value = 1
#            par_df.set_value(i, 'ek_value', ek_value)
        return par_df        
###############################################################################
class IndicatorNutrients(IndicatorBase): 
    """
    Class with methods incommon for all nutrient indicators (TOTN, DIN, TOTP and DIP). 
    """
    
    def __init__(self):
        super().__init__()  
    
    def calculate_ek_value(self, tolerance_filter, indicator_name, par, salt_par = 'SALT_CTD'):
        """
        Calculates indicator ER values, for nutrients this is means reference value divided by observed value.
        Transforms ER values to numeric class values (num_class)
        tolerance_filters is a dict with tolerance filters for the 
        """
        """
        Vid statusklassificering
        ska värden från ytvattnet användas (0-10 meter eller den övre vattenmassan
        om språngskiktet är grundare än 10 meter).
        
        Om mätningar vid ett tillfälle är utförda vid diskreta djup, exempelvis 0, 5 och 10
        meter ska EK-värde beräknas för varje mätning och ett medel–EK skapas för de tre
        djupen.
        """
        """
        Calculate EK-value
        """
        ref_object = getattr(core.RefValues(), indicator_name.lower())[self.data_filter_object.TYPE_AREA.value]
        
        class_result = ClassificationResult()
        class_result.add_info('parameter', par)
        class_result.add_info('salt_parameter', salt_par)
        class_result.add_info('type_area', self.data_filter_object.TYPE_AREA.value)
        
        """
        För kvalitetsfaktorn Näringsämnen: 
        1) Beräkna EK för varje enskilt prov utifrån referensvärden i tabellerna 6.2-6.7.
        Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vid
        varje enskilt prov. Om mätningar är utförda vid diskreta djup, beräkna EK-värde
        för varje mätning och sedan ett medel-EK för varje specifikt mättillfälle.
        """
        print('\t\t\tget_ref_value_for_par_with_salt_ref for indicator {}...'.format(indicator_name))
        par_df = self.get_ref_value_for_par_with_salt_ref(par = par, 
                                                 salt_par = salt_par, 
                                                 indicator_name = indicator_name, tolerance_filter = tolerance_filter)
        par_df['ek_value_calc'] = np.nan
        print('\t\t\tCalculate {} Ek value...'.format(indicator_name))
        for i in par_df.index:
            df_row = par_df.loc[i, :]
            par_value = df_row[par]
            ref_value = df_row['ref_value']
            if np.isnan(par_value):
                ek_value_calc = np.nan
            else:
                # Get ER-value (EK på svenska)
                ek_value_calc = ref_value/par_value
                par_df['ek_value_calc'] = ek_value_calc
                      
            # Check ek_value_calc
            ek_value = ek_value_calc
            if ek_value > 1:
                ek_value = 1
            par_df.set_value(i, 'ek_value', ek_value)
                      
        par_df['salt_index'] = par_df['salt_index'].apply(lambda x: '' if np.isnan(x) else int(x))
        
        # calculate mean, max, min and count for EK values per measurement occasion. .reset_index keeps all df column headers
        by_occasion = par_df.groupby(['profile_key', 'MYEAR'],).ek_value.agg(['count', 'min', 'max', 'mean']).reset_index()
#        by_occasion.to_csv('d:/Ny mapp/pandas/by_occation.txt', sep='\t')
        by_occasion.rename(columns={'mean':'mean_ek_value'}, inplace=True) # Cant use "mean" below
        
        # Remove occations with not enough samples
        by_occasion = by_occasion.loc[by_occasion['count'] >= tolerance_filter.MIN_NR_VALUES.value, :]
        
        """
        2) Medelvärdet av EK för varje parameter beräknas för varje år.
        """
        by_year = by_occasion.groupby('MYEAR').mean_ek_value.agg(['count', 'min', 'max', 'mean'])
#        by_year.to_csv('d:/Ny mapp/pandas/by_year.txt', sep='\t')
        print('\t\t\t{} Ek value Calculated'.format(indicator_name))
        class_result.add_info('all_data', par_df)
        class_result.add_info('mean_by_occasion', by_occasion)
        class_result.add_info('mean_by_year', by_year)
        class_result.add_info('nr_years', len(by_year))

        
        """
        3) Medelvärdet av EK för varje parameter och vattenförekomst beräknas för minst
        en treårsperiod.
        """
        if len(by_year) >= tolerance_filter.MIN_NR_YEARS.value:
            class_result.add_info('mean_total', np.mean(by_year['mean']))
            class_result.add_info('all_ok', True)
        else:
            return class_result
        
        """
        4) Statusklassificeringen för respektive parameter görs genom att medelvärdet av
        EK jämförs med de angivna EK-klassgränserna i tabellerna 6.2-6.7. 
        """
        class_result.add_info('num_class', ref_object.get_num_class(class_result['mean_total']))
        
        self.class_result = class_result  
                
        """
        5) EK vägs samman för ingående parametrar (tot-N, tot-P, DIN och DIP) enligt
        beskrivning nedan (6.4.2) för slutlig statusklassificering av hela kvalitetsfaktorn.
        Görs i quality_factors, def calculate_quality_factor()
        """
        
###############################################################################
class IndicatorDIN(IndicatorNutrients): 
    """
    Class to calculate indicator DIN. 
    """
    
    def __init__(self):
        super().__init__()
        self.name = 'DIN'
        
        # Parameter list contains all parameters that is used by the indicator class
        self.parameter_list = ['NTRA', 'NTRI', 'AMON', 'DIN', 'SALT_CTD']
       
    #==========================================================================
    def _set_refvalues(self):
        pass

    #==========================================================================
    def filter_data(self, data_filter_object=None, parameter=None):
        """
        If filtering on indicator-level the filter has to be saved for this indicator specifically.
        """
        pass
        
    #==========================================================================
    def get_status(self):

        return self.class_result
    
###############################################################################
class IndicatorTOTN(IndicatorNutrients): 
    """
    Class to calculate indicator TOTN. 
    """
    
    def __init__(self):
        super().__init__() 
        self.name = 'TOTN'
        
        # Parameter list contains all parameters that is used by the indicator class
        self.parameter_list = ['SALT_CTD', 'NTOT']
        
    #==========================================================================
    def _set_refvalues(self):
        pass

    #==========================================================================
    def filter_data(self, data_filter_object=None, parameter=None):
        """
        If filtering on indicator-level the filter has to be saved for this indicator specifically.
        """
        pass
        
    #==========================================================================
    def get_status(self):

        return self.class_result
            
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
    
    
    ind_TOTN = IndicatorTOTN()
    ind_TOTN.set_data_handler(filtered_data)
    ind_TOTN.filter_data(winter_filter_1)
    
    core.RefValues()
    core.RefValues().add_ref_parameter_from_file('TOTN_winter', 'D:/Utveckling/g_EKOSTAT_tool/test_data/totn_vinter.txt')
    
    
    nclass = ind_TOTN.get_status(tolerance_filter)
    
    print('-'*50)
    print('done')
    print('-'*50)
    
    