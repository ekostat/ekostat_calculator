# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:24:34 2017

@author: a001985
"""
import numpy as np

import est_core 

###############################################################################
class ClassificationResult(dict):
    """
    Class to hold result from a clasification. 
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
    def __init__(self):
        self.name = ''
        self.parameter_list = []
    
    #========================================================================== 
    def set_data_handler(self, data_handler=None, parameter=None): 
        """
        Assigns data_handler-object(s) to the parameter objects belonging to self. 
        if data_handler and parameter is given that parameter is given the data handler. 
        If "data_handler" is given all parameters will be assigned that data_handler. 
        If "data_handler_dict" is given the corresponding data_handler under its key will be assigend. 
        """ 
        if data_handler and parameter:
            if not parameter in self.parameter_list:
                return False
            attr = getattr(self, parameter.lower())
            all_ok = attr.set_data_handler(data_handler)
            return all_ok
        elif data_handler:
            for key in self.parameter_list:
                try:
                    attr = getattr(self, key.lower())
                    attr.set_data_handler(data_handler)
                except AttributeError as e:
                    print(e)
        return True
    
    
    #==========================================================================
    def filter_data(self, data_filter_object=None, parameter=None):
        """
        Filters data in Parameter objects
        data_filter_object is of type est_core.settings.FilterData
        If "data_filter_object" is given all parameters will be filtered using this filter. 
        If "data_filter_object_dict" is given the corresponding filter under its key will be used. 
        """
        self.data_filter_object = data_filter_object
#        print('parameter', parameter)
        if data_filter_object and parameter:
#            print('parameter', parameter)
            if not parameter in self.parameter_list:
                return False
            if not hasattr(self, parameter.lower()):
                return False
            attr = getattr(self, parameter.lower())
            all_ok = attr.filter_data(data_filter_object)
            return all_ok
        if data_filter_object:
            for key in self.parameter_list:
#                print('key', key)
                if hasattr(self, key.lower()):
                    attr = getattr(self, key.lower())
                    attr.filter_data(data_filter_object)
        return True
    
    #==========================================================================
    def get_ek_value_for_par_with_salt_ref(self, par=None, salt_par='SALT_CTD', indicator=None, tolerance_filter=None):
        """
        tollerance_filters is a dict with tolerance filters for the specific (sub) parameter. 
        """
        """
        Vid statusklassificering
        ska värden från ytvattnet användas (0-10 meter eller den övre vattenmassan
        om språngskiktet är grundare än 10 meter).
        
        Om mätningar vid ett tillfälle är utförda vid diskreta djup, exempelvis 0, 5 och 10
        meter ska EK-värde beräknas för varje mätning och ett medel–EK skapas för de tre
        djupen.
        """
        class_result = ClassificationResult()
        class_result.add_info('paramter', par)
        class_result.add_info('salt_parameter', salt_par)
        class_result.add_info('type_area', self.data_filter_object.TYPE_AREA.value)
        
        """
        1) Beräkna EK för varje enskilt prov utifrån referensvärden i tabellerna 6.2-6.7.
        Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vid
        varje enskilt prov. Om mätningar är utförda vid diskreta djup, beräkna EKvärde
        för varje mätning och sedan ett medel-EK för varje specifikt mättillfälle.
        """
        
        ref_object = getattr(est_core.RefValues(), indicator.lower())[self.data_filter_object.TYPE_AREA.value]
#        self.ref_object = ref_object
        par_object = getattr(self, par.lower())
        salt_object = getattr(self, salt_par.lower())
        self.par_object = par_object
        self.salt_object = salt_object
        
        df = par_object.data.column_data.copy(deep=True)
        salt_df = salt_object.data.column_data
        
        df['salt_value_ori'] = np.nan 
        df['salt_value'] = np.nan 
        df['salt_index'] = np.nan 
        df['ref_value'] = np.nan 
        df['ek_value_calc'] = np.nan 
        df['ek_value'] = np.nan 
        
        for i in df.index:
#            self.i = i
            df_row = df.loc[i, :]
            par_value = df_row[par]
            if np.isnan(par_value):
                ref_value = np.nan
                ek_value_calc = np.nan
            else:
                if i in salt_df.index and not np.isnan(salt_df.loc[1, salt_par]): 
                    salt_value_ori = salt_df.loc[1, salt_par]
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
                ek_value_calc = ref_value/par_value
                
#                self.salt_value = salt_value
#                self.ek_value_calc = ek_value_calc
#                self.ref_value = ref_value
#                self.par_value = par_value
#            print('ref_value', ref_value, '=', value)
#            self.df_row = df_row
#            self.salt_value = salt_value
            df.set_value(i, 'salt_value_ori', salt_value_ori) 
            df.set_value(i, 'salt_value', salt_value) 
            df.set_value(i, 'salt_index', salt_index)
            df.set_value(i, 'ref_value', ref_value)
            df.set_value(i, 'ek_value_calc', ek_value_calc)
            
            # Check ek_value_calc
            ek_value = ek_value_calc
            if ek_value > 1:
                ek_value = 1
            df.set_value(i, 'ek_value', ek_value)
            
        df['salt_index'] = df['salt_index'].apply(lambda x: '' if np.isnan(x) else int(x))
        
        by_occasion = df.groupby(['profile_key', 'MYEAR']).ek_value.agg(['count', 'min', 'max', 'mean'])
#        by_occasion.to_csv('d:/Ny mapp/pandas/by_occation.txt', sep='\t')
        by_occasion.rename(columns={'mean':'mean_ek_value'}, inplace=True) # Cant use "mean" below
        
        # Remove occations with not enough samples
        by_occasion = by_occasion.loc[by_occasion['count'] >= tolerance_filter.MIN_NR_VALUES.value, :]
        
        """
        2) Medelvärdet av EK för varje parameter beräknas för varje år.
        """
        by_year = by_occasion.groupby('MYEAR').mean_ek_value.agg(['count', 'min', 'max', 'mean'])
#        by_year.to_csv('d:/Ny mapp/pandas/by_year.txt', sep='\t')
    
        class_result.add_info('all_data', df)
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
        return class_result
        
        
###############################################################################
class IndicatorNtotSummer(IndicatorBase): 
    """
    Class to calculate status for a NP. 
    """
    
    def __init__(self):
        super().__init__() 
        self.name = 'NtotSummer'
        
        # Parameter list contains all parameters that is used by the indicator class
        self.parameter_list = []
        
        self._load_data_objects()
        
    
    #==========================================================================
    def _load_data_objects(self):
        """
        Initiates data to work with. Typically parameter class objects. 
        """
        pass
        
    
###############################################################################
class IndicatorDINwinter(IndicatorBase): 
    """
    Class to calculate indicator DINwinter. 
    """
    
    def __init__(self):
        super().__init__() 
        self.name = 'DINwinter'
        
        # Parameter list contains all parameters that is used by the indicator class
        self.parameter_list = ['NTRA', 'NTRI', 'AMON', 'DIN', 'SALT_CTD']
        
        self._load_data_objects()
        
    
    #==========================================================================
    def _load_data_objects(self):
        """
        Initiates data to work with. Typically parameter class objects. 
        """
        
        self.salt_ctd = est_core.ParameterSALT_CTD()
        
        self.ntra = est_core.ParameterNTRA()
        self.ntri = est_core.ParameterNTRI()
        self.amon = est_core.ParameterAMON()
        self.din = None
        
    #==========================================================================
    def filter_data(self, data_filter_object=None, parameter=None):
        """
        Override from Parent class IndicatorBase. 
        After filtering of parameterrs the calculated din-parameter is created. 
        """
        self.data_filter_object = data_filter_object
#        print('parameter', parameter)
        if data_filter_object and parameter:
#            print('parameter', parameter)
            if not parameter in self.parameter_list:
                return False
            if not hasattr(self, parameter.lower()):
                return False
            attr = getattr(self, parameter.lower())
            all_ok = attr.filter_data(data_filter_object)
            return all_ok
        if data_filter_object:
            for key in self.parameter_list:
#                print(key)
#                attr = getattr(self, key.lower())
#                attr.filter_data(data_filter_object)
                try:
                    attr = getattr(self, key.lower())
                    attr.filter_data(data_filter_object)
                except AttributeError as e:
                    print('No attribute for parameter %s ' % key, e)
        
        # Load CalculatedParameterDIN if possible
        # TODO: Option to load pre-calculated DIN (DIN in dataset). This 
        if all([self.ntra.data, self.ntri.data, self.amon.data]):
            self.din = est_core.CalculatedParameterDIN(ntra=self.ntra.data, 
                                                       ntri=self.ntri.data, 
                                                       amon=self.amon.data)
        return True

    #==========================================================================
    def get_status(self, tolerance_filter):
        """
        tollerance_filters is a dict with tolerance filters for the 
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
        1) Beräkna EK för varje enskilt prov utifrån referensvärden i tabellerna 6.2-6.7.
        Det aktuella referensvärdet erhålls utifrån den salthalt som är observerad vid
        varje enskilt prov. Om mätningar är utförda vid diskreta djup, beräkna EKvärde
        för varje mätning och sedan ett medel-EK för varje specifikt mättillfälle.
        """
        
        """
        2) Medelvärdet av EK för varje parameter beräknas för varje år.
        """
        
        """
        3) Medelvärdet av EK för varje parameter och vattenförekomst beräknas för minst
        en treårsperiod.
        """
        
        """
        4) Statusklassificeringen för respektive parameter görs genom att medelvärdet av
        EK jämförs med de angivna EK-klassgränserna i tabellerna 6.2-6.7. 
        """
        
        """
        5) EK vägs samman för ingående parametrar (tot-N, tot-P, DIN och DIP) enligt
        beskrivning nedan (6.4.2) för slutlig statusklassificering av hela kvalitetsfaktorn.
        """
        pass
    
###############################################################################
class IndicatorTN(IndicatorBase): 
    """
    Class to calculate indicator TN. 
    """
    
    def __init__(self):
        super().__init__() 
        self.name = 'TN'
        
        # Parameter list contains all parameters that is used by the indicator class
        self.parameter_list = ['SALT_CTD', 'NTOT']
        
        self._load_data_objects()
        
    
    #==========================================================================
    def _load_data_objects(self):
        """
        Initiates data to work with. Typically parameter class objects. 
        """
        self.salt_ctd = est_core.ParameterSALT_CTD()
        
        self.ntot = est_core.ParameterTN()
        

    #==========================================================================
    def get_status(self, tolerance_filter):
        return self.get_ek_value_for_par_with_salt_ref(par='NTOT', 
                                                       indicator='TN_winter', tolerance_filter=tolerance_filter)
        
        """
        5) EK vägs samman för ingående parametrar (tot-N, tot-P, DIN och DIP) enligt
        beskrivning nedan (6.4.2) för slutlig statusklassificering av hela kvalitetsfaktorn.
        """
    
            
###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "indicators.py"')
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
    
    
    ind_TN = IndicatorTN()
    ind_TN.set_data_handler(filtered_data)
    ind_TN.filter_data(winter_filter_1)
    
    est_core.RefValues()
#    est_core.RefValues().add_ref_parameter_from_file('DIN_winter', 'D:/Utveckling/g_EKOSTAT_tool/test_data/din_vinter.txt')
    est_core.RefValues().add_ref_parameter_from_file('TN_winter', 'D:/Utveckling/g_EKOSTAT_tool/test_data/totn_vinter.txt')
    
    
    nclass = ind_TN.get_status(tolerance_filter)
    
#    df = ind_TN.df
#    df.to_csv('d:/Ny mapp/pandas/df.txt', sep='\t')
##    df.groupby('profile_key').ref_value.agg(['count', 'min', 'max', 'mean'])
#    by_occasion = df.groupby(['profile_key', 'MYEAR']).ek_value.agg(['count', 'min', 'max', 'mean'])
##    by_occasion = by_occasion.loc[by_occasion['count'] >= tolerance_filter.MIN_NR_VALUES.value, :]
#    by_occasion.to_csv('d:/Ny mapp/pandas/by_occation.txt', sep='\t')
#    
#    by_occasion.rename(columns={'mean':'mean_ek_value'}, inplace=True)
#    by_year = by_occasion.groupby('MYEAR').mean_ek_value.agg(['count', 'min', 'max', 'mean'])
#    by_year.to_csv('d:/Ny mapp/pandas/by_year.txt', sep='\t')
    
    
#    ind_TN.df.loc[[7795, 7870, 11647, 11728], :] # 4055
    
    