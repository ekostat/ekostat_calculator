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
        # from SettingsFile
        self.tolerance_settings = self.parent_workspace_object.get_step_object(step = 2, subset = self.subset).get_indicator_tolerance_settings(self.name)
        # To be read from config-file
        indicator_list = list(self.parent_workspace_object.mapping_objects['quality_element'].keys())
        self._load_indicator_results()
        # perform checks before continuing
        self._check()
        self._set_directories()
        #paths and saving
        self.result_directory = self.step_object.paths['step_directory']+'/output/results/'
        self.sld = core.SaveLoadDelete(self.result_directory)
        
        self._load_indicators()
        self.indicator_list = []
        self.class_result = None
    
    #==========================================================================    
    def _check(self):
        pass
    #==========================================================================  
    def _load_indicator_results(self):
        
        self.indicator_list = {}
        for indicator in self.indicator_list:
            try:
                self.indicator_dict[indicator] = self.step_object.indicator_objects[indicator].sld.load_df(file_name = indicator + '_by_period')
            except FileNotFoundError:
                print('No status results for {}. Cannot calculate status without it'.format(indicator))
              
    #==========================================================================
    def _set_directories(self):
        #set paths
        self.paths = {}
        self.paths['output'] = self.step_object.paths['directory_paths']['output'] 
        self.paths['results'] = self.step_object.paths['directory_paths']['results']
        
        
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
        def mean_EQR(df, winter_values, summer_values) :
            df['winter_EQR'] = df[winter_values].mean(axis = 1, skipna = False)
            df['summer_EQR'] = df[summer_values].mean(axis = 1, skipna = False)
            df['mean_EQR'] = df[['winter_EQR','summer_EQR']].mean(axis = 1, skipna = False)
        
            
        ###### Results #####
        # how keyword:
            # - outer: use union of keys from both frames, similar to a SQL full outer join; sort keys lexicographically
            # - inner: use intersection of keys from both frames, similar to a SQL inner join; preserve the order of the left keys
        # TODO: replace merge by join? 
        P_results = self.indicator_list['dip_winter'].merge(self.indicator_list['ptot_winter'], on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA'], how = 'inner', suffixes = ['dip', 'ptot'], copy=True)
        P_results.merge(self.indicator_list['ptot_summer'], on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA'], how = 'inner', suffixes = ['winter', 'summer'], copy=True)
        mean_EQR(P_results)
        N_results = self.indicator_list['din_winter'].merge(self.indicator_list['ntot_winter'], on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA'], how = 'inner', suffixes = ['din', 'ntot'], copy=True)
        N_results.merge(self.indicator_list['ntot_summer'], on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA'], how = 'inner', suffixes = ['winter', 'summer'], copy=True)
        mean_EQR(N_results)
        
#        P_winter = self.indicator_list['dip_winter'].merge(self.indicator_list['ptot_winter'], on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA'], how = 'inner', suffixes = ['dip', 'ptot'], copy=True)
#        P_winter['mean'] = np.mean(P_winter['dip_winter'], P_winter['ptot_winter'])
#        N_winter = self.indicator_list['din_winter'].merge(self.indicator_list['ntot_winter'], on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA'], how = 'inner', suffixes = ['dip', 'ptot'], copy=True)
#        N_winter['mean'] = np.mean(P_winter['din_winter'], P_winter['ntot_winter'])
#        
#        ###### QualityElement results #####
#        P_results = P_winter.merge(self.indicator_list['ptot_summer'], on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA'], how = 'inner', suffixes = ['winter', 'summer'], copy=True)
#        P_results = 
        
        results = P_results.merge(N_results, on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA'], how = 'inner', suffixes = ['P', 'N'], copy=True)
        results['mean_EQR'] = results[['mean_EQR_P','mean_EQR_N']].mean(axis = 1, skipna = False)
        
        self.class_result = results
        
    
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
    
    
    
    
    
    
    
    
    
    