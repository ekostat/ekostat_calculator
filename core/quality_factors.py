# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 14:43:35 2017

@author: a001985
"""
import os
import core 
import numpy as np

###############################################################################
class ClassificationResult(dict):
    """
    Class to hold result from a classification. 
    Jag kopierade denna från indicators.py
    """ 
    def __init__(self):
        super().__init__() 
        
        self['qualityfactor'] = None
        self['type_area'] = None
        self['status'] = None
        self['EQR'] = None
        self['qf_EQR'] = None
        self['all_ok'] = False
        
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
class QualityElementBase(object): 
    """
    Class to hold general information about quality factors. 
    """ 
    def __init__(self, subset_uuid, parent_workspace_object, quality_element):
        self.name = '' 
        
        self.name = quality_element.lower()
        print('********')
        print(self.name)
        self.class_result = None
        self.subset = subset_uuid
        self.step = 'step_3'
        # from workspace
        self.parent_workspace_object = parent_workspace_object
        self.mapping_objects = self.parent_workspace_object.mapping_objects
        self.index_handler = self.parent_workspace_object.index_handler
        self.step_object = self.parent_workspace_object.get_step_object(step = 3, subset = self.subset)
        #paths and saving
        self.result_directory = self.step_object.paths['step_directory']+'/output/results/'
        self.sld = core.SaveLoadDelete(self.result_directory)
        # from SettingsFile
        self.tolerance_settings = self.parent_workspace_object.get_step_object(step = 2, subset = self.subset).get_indicator_tolerance_settings(self.name)
        # To be read from config-file
        self.indicator_list = list(self.parent_workspace_object.mapping_objects['quality_element'].get_indicator_list_for_quality_element(self.name))
        self._load_indicator_results()
        # perform checks before continuing
        self._check()
        self._set_directories()
        
        #self._load_indicators()
        #self.indicator_list = []
        self.class_result = None
    
    #==========================================================================    
    def _check(self):
        pass
    #==========================================================================  
    def _load_indicator_results(self):
        
        self.indicator_dict = {}
        for indicator in self.indicator_list:
            try:
                self.indicator_dict[indicator] = self.sld.load_df(file_name = indicator + '_by_period')         
#                self.indicator_dict[indicator] = self.step_object.indicator_objects[indicator].sld.load_df(file_name = indicator + '_by_period')
            except FileNotFoundError:
                print('No status results for {}. Cannot calculate status without it'.format(indicator))
              
    #==========================================================================
    def _set_directories(self):
        #set paths
        self.paths = {}
        self.paths['output'] = self.step_object.paths['directory_paths']['output'] 
        self.paths['results'] = self.step_object.paths['directory_paths']['results']
    
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
        
###############################################################################
class QualityElementNutrients(QualityElementBase): 
    """
    Class calculate the quality factor for Nutrients. 
    """
    def __init__(self, subset_uuid, parent_workspace_object, quality_element):
        super().__init__(subset_uuid, parent_workspace_object, quality_element) 
    
    #==========================================================================
    def calculate_quality_factor(self):
        """
        5) EK vägs samman för ingående parametrar (tot-N, tot-P, DIN och DIP) för slutlig statusklassificering av 
        hela kvalitetsfaktorn Näringsämnen.
        """
        """
        GAMLA FÖRESKRIFTEN
        Ett medelvärde av de numeriska klassningarna (Nklass) beräknas för 
        DIN, DIP, tot-N, tot-P under vintern och ett medelvärde för tot-N, tot-P under sommaren. 
        Därefter beräknas medelvärdet av sommar och vinter, vilket blir den sammanvägda klassificeringen av näringsämnen. 
        
        NYA FÖRESKRIFTEN
        Ett medelvärde av de numeriska klasserna (global_EQR) beräknas separat för N och P. Först ett medelvärde för vintern 
        (N_vinter = medel(din_vinter, ntot_vinter) reps P_vinter = medel(dip_vinter, ptot_vinter)). 
        Sedan beräknas medelvärde för N_vinter och ntot_summer respektive P_vinter och ptot_summer och efter det medelvärde av N och P, 
        vilket blir den sammanvägda klassificeringen av näringsämnen. 
        
        Statusklassificeringen avgörs av medelvärdet för den numeriska klassningen enligt tabell 2.1, ett värde 0-1.
        Dessa värden kan sedan jämföras med övriga kvalitetsfaktorer och ingå i sammansvägningen.
        """
#        #==========================================================================
#        def get_status_from_global_EQR(global_EQR):
#            
#            if global_EQR >= 0.8:
#                return 'HIGH'
#            elif global_EQR >= 0.6:
#                return 'GOOD'
#            elif global_EQR >= 0.4:
#                return 'MODERATE'
#            elif global_EQR >= 0.2:
#                return 'POOR'
#            elif global_EQR >= 0:
#                return 'BAD'
#            else:
#                return ''
        def mean_EQR(df, winter_values, summer_values) :
            df['winter_EQR'] = df[winter_values].mean(axis = 1, skipna = False)
            df['summer_EQR'] = df[summer_values].mean(axis = 1, skipna = False)
            df['mean_EQR'] = df[['winter_EQR','summer_EQR']].mean(axis = 1, skipna = False)
        
            
        ###### Results #####
        # how keyword:
            # - outer: use union of keys from both frames, similar to a SQL full outer join; sort keys lexicographically
            # - inner: use intersection of keys from both frames, similar to a SQL inner join; preserve the order of the left keys
        # TODO: replace merge by join? 
        merge_on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA']
        for indicator in self.indicator_list:
            col_list = list(self.indicator_dict[indicator].columns)
            [col_list.remove(r) for r in merge_on]
            {k: k+'_'+indicator for k in col_list}
            self.indicator_dict[indicator].rename(columns = {k: k+'_'+indicator for k in col_list}, inplace = True)
            #print(list(self.indicator_dict[indicator].columns))
#        print(self.indicator_dict['dip_winter'].columns)
#        print(self.indicator_dict['ptot_winter'].columns)
#        P_results = self.indicator_dict['dip_winter'].merge(self.indicator_dict['ptot_winter'], on = merge_on, how = 'outer', suffixes = ['_dip', '_ptot'], copy=True)
#        print(P_results.columns)
#        print(self.indicator_dict['ptot_summer'].columns, len(self.indicator_dict['ptot_summer']))
#        P_results.merge(self.indicator_dict['ptot_summer'], on = merge_on, how = 'outer', suffixes = ['_winter', '_ptot_summer'], copy=True)
#        print(P_results.columns)
#        mean_EQR(P_results, ['dip_winter','ptot_winter'], ['ptot_summer'])
#        N_results = self.indicator_dict['din_winter'].merge(self.indicator_dict['ntot_winter'], on = merge_on, how = 'inner', suffixes = ['din', 'ntot'], copy=True)
#        N_results.merge(self.indicator_dict['ntot_summer'], on = merge_on, how = 'inner', suffixes = ['winter', 'summer'], copy=True)
#        mean_EQR(N_results, ['din_winter','ntot_winter'], ['ntot_summer'])
        
        P_winter = self.indicator_dict['indicator_dip_winter'].merge(self.indicator_dict['indicator_ptot_winter'], on = merge_on, how = 'inner', copy=True)
        #print('P_winter columns 1', P_winter.columns)
        P_winter['EQR_P_winter_mean'] = P_winter[['global_EQR_dip_winter','global_EQR_ptot_winter']].mean(axis = 1, skipna = False)
        P_winter['STATUS_P_winter'] = P_winter['EQR_P_winter_mean'].apply(lambda x: self.get_status_from_global_EQR(x))
        #print('P_winter columns 2', P_winter.columns)
        N_winter = self.indicator_dict['indicator_din_winter'].merge(self.indicator_dict['indicator_ntot_winter'], on = merge_on, how = 'inner', copy=True)
        N_winter['EQR_N_winter_mean'] = N_winter[['global_EQR_din_winter','global_EQR_ntot_winter']].mean(axis = 1, skipna = False)
        N_winter['STATUS_N_winter'] = N_winter['EQR_N_winter_mean'].apply(lambda x: self.get_status_from_global_EQR(x))
        
        ###### QualityElement results #####
        P_results = P_winter.merge(self.indicator_dict['indicator_ptot_summer'], on = merge_on, how = 'inner', copy=True)
        #print('P_summer columns', self.indicator_dict['ptot_summer'].columns)
        #print('P merged columns 1', P_results.columns)
        P_results['MEAN_P_EQR'] = P_results[['EQR_P_winter_mean','global_EQR_ptot_summer']].mean(axis = 1, skipna = False)
        P_results['STATUS_P'] = P_results['MEAN_P_EQR'].apply(lambda x: self.get_status_from_global_EQR(x))
        #print('P merged columns 2', P_results.columns)
        N_results = N_winter.merge(self.indicator_dict['indicator_ntot_summer'], on = merge_on, how = 'inner', copy=True)
        N_results['MEAN_N_EQR'] = N_results[['EQR_N_winter_mean','global_EQR_ntot_summer']].mean(axis = 1, skipna = False)
        #print(N_results.columns)
        N_results['STATUS_N'] = N_results['MEAN_N_EQR'].apply(lambda x: self.get_status_from_global_EQR(x))
        
        results = P_results.merge(N_results, on = merge_on, how = 'inner', suffixes = ['P', 'N'], copy=True)
        results['mean_EQR'] = results[['MEAN_P_EQR','MEAN_N_EQR']].mean(axis = 1, skipna = False)
        results['STATUS_NUTRIENTS'] = results['mean_EQR'].apply(lambda x: self.get_status_from_global_EQR(x))
        
        self.results = results
        
###############################################################################
class QualityElementPhytoplankton(QualityElementBase): 
    """
    Class calculate the quality element for Phytoplankton. 
    """
    def __init__(self, subset_uuid, parent_workspace_object, quality_element):
        super().__init__(subset_uuid, parent_workspace_object, quality_element)  
        
    def calculate_quality_factor(self):
        
        merge_on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA']
        for indicator in self.indicator_list:
            col_list = list(self.indicator_dict[indicator].columns)
            #print(col_list)
            [col_list.remove(r) for r in merge_on]
            {k: k+'_'+indicator for k in col_list}
            self.indicator_dict[indicator].rename(columns = {k: k+'_'+indicator for k in col_list}, inplace = True)
            
        results = self.indicator_dict[self.indicator_list[0]].merge(self.indicator_dict[self.indicator_list[2]], on = merge_on, how = 'inner', copy=True)
        results['mean_EQR'] = results[['global_EQR'+'_'+self.indicator_list[0],'global_EQR'+'_'+self.indicator_list[1]]].mean(axis = 1, skipna = False)
        results['STATUS_PHYTOPLANKTON'] = results['mean_EQR'].apply(lambda x: self.get_status_from_global_EQR(x))
        
        self.results = results
    
###############################################################################
if __name__ == '__main__':
    nr_marks = 60
    print('='*nr_marks)
    print('Running module "quality_factor.py"')
    print('-'*nr_marks)
    print('')
    
    
    root_directory = os.path.dirname(os.path.abspath(__file__))[:-9]
    
#    core.StationList(root_directory + '/test_data/Stations_inside_med_typ_attribute_table_med_delar_av_utsjö.txt')
    core.ParameterList()
    
    #--------------------------------------------------------------------------
    # Directories and file paths
    raw_data_file_path = root_directory + '/test_data/raw_data/data_BAS_2000-2009.txt'
    first_filter_data_directory = root_directory + '/test_data/filtered_data' 
    
    first_data_filter_file_path = root_directory + '/test_data/filters/first_data_filter.txt' 
    winter_data_filter_file_path = root_directory + '/test_data/filters/winter_data_filter.txt'
    
    tolerance_filter_file_path = root_directory + '/test_data/filters/tolerance_filter_template.txt'
    
    #--------------------------------------------------------------------------
    # Filters 
    first_filter = core.DataFilter('First filter', file_path=first_data_filter_file_path)
    winter_filter = core.DataFilter('winter_filter', file_path=winter_data_filter_file_path)
    winter_filter.save_filter_file(root_directory + '/test_data/filters/winter_data_filter_save.txt') # mothod available
    tolerance_filter = core.ToleranceFilter('test_tolerance_filter', file_path=tolerance_filter_file_path)

    #--------------------------------------------------------------------------
    # Reference values
    core.RefValues()
    core.RefValues().add_ref_parameter_from_file('DIN_winter', root_directory + '/test_data/din_vinter.txt')
    core.RefValues().add_ref_parameter_from_file('TOTN_winter', root_directory + '/test_data/totn_vinter.txt')
    
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    # Handler (raw data)
    raw_data = core.DataHandler('raw')
    raw_data.add_txt_file(raw_data_file_path, data_type='column') 
    
    # Use first filter 
    filtered_data = raw_data.filter_data(first_filter) 
    
    # Save filtered data (first filter) as a test
    filtered_data.save_data(first_filter_data_directory)
    
    
    # Load filtered data (first filter) as a test
    loaded_filtered_data = core.DataHandler('first_filtered')
    loaded_filtered_data.load_data(first_filter_data_directory)


    # Create and fill QualityFactor
    qf_NP = core.QualityFactorNP()
    qf_NP.set_data_handler(data_handler=loaded_filtered_data)
    
    # Filter parameters in QualityFactorNP 
    # First general filter 
    qf_NP.filter_data(data_filter_object=first_filter) 
    # winter filter
    qf_NP.filter_data(data_filter_object=winter_filter, indicator='TOTN_winter') 
    
    q_factor = qf_NP.get_quality_factor(tolerance_filter)
    
    
    # Parameter
    print('-'*nr_marks)
    print('done')
    print('-'*nr_marks)
    
    
    
    
    
    
    
    
    
    