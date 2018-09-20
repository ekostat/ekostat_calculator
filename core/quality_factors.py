# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 14:43:35 2017

@author: a001985
"""
import os
import core 
import numpy as np
import re

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
        # TODO update resultfilenames and here!
        for indicator in self.indicator_list:
            if not os.path.exists(self.sld.directory + indicator + '-by_period.pkl') or not os.path.exists(self.sld.directory +indicator + '-by_period.txt'):
#                 raise core.exceptions.NoResultsForIndicator()
                pass #self.indicator_dict[indicator] = False
            else:
                self.indicator_dict[indicator] = self.sld.load_df(file_name = indicator + '-by_period')         
                
#                 print('No status results for {}. Cannot calculate status without it'.format(indicator))
              
    #==========================================================================
    def _set_directories(self):
        #set paths
        self.paths = {}
        self.paths['output'] = self.step_object.paths['directory_paths']['output'] 
        self.paths['results'] = self.step_object.paths['directory_paths']['results']
    #==========================================================================
    def calculate_quality_factor(self):

        """
        Updated 20180920    by Magnus
        
        Calculates quality element based on included indicators
        
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
                
        ###### Results #####
        # how keyword:
            # - outer: use union of keys from both frames, similar to a SQL full outer join; sort keys lexicographically
            # - inner: use intersection of keys from both frames, similar to a SQL inner join; preserve the order of the left keys
        # TODO: replace merge by join? 
        merge_on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA']
        def mean_of_indicators(indicator_name):
            parameters = self.mapping_objects['quality_element'].indicator_config.loc[indicator_name]['parameters'].split(', ') 
            if 'indicator_' not in parameters[0]: 
#                 if 'qe_' not in parameters[0]:
                    return False
            if not all([par in self.indicator_dict.keys() for par in parameters]):
                return False
            if len(parameters) == 2:
                mean_of_indicators = self.indicator_dict[parameters[0]].merge(self.indicator_dict[parameters[1]], on = merge_on, how = 'inner', copy=True, suffixes = ['_' + par for par in parameters])
                mean_of_indicators['ok_'+indicator_name] = mean_of_indicators['ok_' + parameters[0]] | mean_of_indicators['ok_' + parameters[1]]
                mean_of_indicators['global_EQR_'+indicator_name] = mean_of_indicators[['global_EQR' + '_' + parameters[0],'global_EQR' +'_' + parameters[1]]].mean(axis = 1, skipna = False)
                mean_of_indicators['STATUS_'+indicator_name] = mean_of_indicators['global_EQR_'+indicator_name].apply(lambda x: self.get_status_from_global_EQR(x))
                self.indicator_dict[indicator_name] = mean_of_indicators
            elif len(parameters) == 1:
                col_list = list(self.indicator_dict[parameters[0]].columns)
                [col_list.remove(r) for r in merge_on]
                {k: k+'_'+parameters[0] for k in col_list}
                self.indicator_dict[indicator_name] = self.indicator_dict[parameters[0]].rename(columns = {k: k+'_'+indicator_name for k in col_list})
            return True
                
        def cut_results(df, indicator_name):
            #pick out columns for only this indicator
            these_cols = [col for col in df.columns if re.search(indicator_name + r'$', col)]
#            return df[these_cols + merge_on].rename(columns = {col: col.strip(indicator_name) for col in these_cols})
            return df[these_cols + merge_on].rename(columns = {col: col.replace('_'+indicator_name,'') for col in these_cols})
    
        for indicator in self.mapping_objects['quality_element'].indicator_config.index:
            if self.mapping_objects['quality_element'].indicator_config.loc[indicator]['quality element'] == self.name:
                # calculate mean for the included sub-indicators
                if mean_of_indicators(indicator):
                    df = cut_results(self.indicator_dict[indicator], indicator)
                    self.sld.save_df(df, indicator + '-by_period')
        if 'qe_'+self.name in self.indicator_dict.keys():
            self.sld.save_df(self.indicator_dict['qe_'+self.name], self.name+'_all_results')
    
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
            
        ###### Results #####
        # how keyword:
            # - outer: use union of keys from both frames, similar to a SQL full outer join; sort keys lexicographically
            # - inner: use intersection of keys from both frames, similar to a SQL inner join; preserve the order of the left keys
        # TODO: replace merge by join? 
        merge_on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA']
#         for indicator in self.indicator_list:
#             col_list = list(self.indicator_dict[indicator].columns)
#             [col_list.remove(r) for r in merge_on]
#             {k: k+'_'+indicator for k in col_list}
#             self.indicator_dict[indicator].rename(columns = {k: k+'_'+indicator for k in col_list}, inplace = True)
#       
        def mean_of_indicators(indicator_name):
#             print(self.mapping_objects['quality_element'].indicator_config.loc[indicator_name]['parameters'])
            parameters = self.mapping_objects['quality_element'].indicator_config.loc[indicator_name]['parameters'].split(', ') 
            if 'indicator_' not in parameters[0]: 
                if 'qe_' not in parameters[0]:
                    return False
#             print(indicator_name, parameters)
            if not all([par in self.indicator_dict.keys() for par in parameters]):
                return False
            if len(parameters) == 2:
#                 print(self.indicator_dict[parameters[0]].columns) 
                   
                mean_of_indicators = self.indicator_dict[parameters[0]].merge(self.indicator_dict[parameters[1]], on = merge_on, how = 'inner', copy=True, suffixes = ['_' + par for par in parameters])
#                 print('columns 1 merge', mean_of_indicators.columns)
                mean_of_indicators['global_EQR_'+indicator_name] = mean_of_indicators[['global_EQR' + '_' + parameters[0],'global_EQR' +'_' + parameters[1]]].mean(axis = 1, skipna = False)
                mean_of_indicators['STATUS_'+indicator_name] = mean_of_indicators['global_EQR_'+indicator_name].apply(lambda x: self.get_status_from_global_EQR(x))
#                 print(mean_of_indicators.loc[mean_of_indicators['VISS_EU_CD'] == 'SE622500-172430'][['global_EQR_'+indicator_name, 'STATUS_'+indicator_name, 'global_EQR_indicator_dip_winter', 'global_EQR_indicator_ptot_winter']])
#                 print('columns 2', mean_of_indicators.columns)
                self.indicator_dict[indicator_name] = mean_of_indicators
#                 self.sld.save_df(mean_of_indicators, indicator_name)
            elif len(parameters) == 1:
                col_list = list(self.indicator_dict[parameters[0]].columns)
                [col_list.remove(r) for r in merge_on]
                {k: k+'_'+parameters[0] for k in col_list}
                self.indicator_dict[indicator_name] = self.indicator_dict[parameters[0]].rename(columns = {k: k+'_'+indicator_name for k in col_list})
#                 self.sld.save_df(self.indicator_dict[indicator_name], indicator_name)
            return True
                
        def cut_results(df, indicator_name):
            #pick out columns for only this indicator
            these_cols = [col for col in df.columns if re.search(indicator_name + r'$', col)]
#             df[these_cols + merge_on].rename(columns = {col: col.strip(indicator_name) for col in these_cols})
            return df[these_cols + merge_on].rename(columns = {col: col.strip(indicator_name) for col in these_cols})
    
        for indicator in self.mapping_objects['quality_element'].indicator_config.index:
            if self.mapping_objects['quality_element'].indicator_config.loc[indicator]['quality element'] == self.name:#'nutrients':
                # calculate mean for the included sub-indicators
                if mean_of_indicators(indicator):
                    df = cut_results(self.indicator_dict[indicator], indicator)
                    self.sld.save_df(df, indicator)
        if 'qe_'+self.name in self.indicator_dict.keys():
            self.sld.save_df(self.indicator_dict['qe_'+self.name], self.name+'_all_results')
#         mean_of_indicators('indicator_p_winter')
#         mean_of_indicators('indicator_p_summer')
#         mean_of_indicators('indicator_p')
#         mean_of_indicators('indicator_n_winter')
#         mean_of_indicators('indicator_n_summer')
#         mean_of_indicators('indicator_n')
#         mean_of_indicators('qe_nutrients')

    #==========================================================================
    def old_calculate_quality_factor(self):
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
            if self.indicator_dict[indicator] is None:
                continue
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
        P_winter['EQR_P_winter_mean'] = P_winter[['global_EQR_indicator_dip_winter','global_EQR_indicator_ptot_winter']].mean(axis = 1, skipna = False)
        P_winter['STATUS_P_winter'] = P_winter['EQR_P_winter_mean'].apply(lambda x: self.get_status_from_global_EQR(x))
        #print('P_winter columns 2', P_winter.columns)
        N_winter = self.indicator_dict['indicator_din_winter'].merge(self.indicator_dict['indicator_ntot_winter'], on = merge_on, how = 'inner', copy=True)
        N_winter['EQR_N_winter_mean'] = N_winter[['global_EQR_indicator_din_winter','global_EQR_indicator_ntot_winter']].mean(axis = 1, skipna = False)
        N_winter['STATUS_N_winter'] = N_winter['EQR_N_winter_mean'].apply(lambda x: self.get_status_from_global_EQR(x))
        
        ###### QualityElement results #####
        P_results = P_winter.merge(self.indicator_dict['indicator_ptot_summer'], on = merge_on, how = 'inner', copy=True)
        #print('P_summer columns', self.indicator_dict['ptot_summer'].columns)
        #print('P merged columns 1', P_results.columns)
        P_results['MEAN_P_EQR'] = P_results[['EQR_P_winter_mean','global_EQR_indicator_ptot_summer']].mean(axis = 1, skipna = False)
        P_results['STATUS_P'] = P_results['MEAN_P_EQR'].apply(lambda x: self.get_status_from_global_EQR(x))
        #print('P merged columns 2', P_results.columns)
        N_results = N_winter.merge(self.indicator_dict['indicator_ntot_summer'], on = merge_on, how = 'inner', copy=True)
        N_results['MEAN_N_EQR'] = N_results[['EQR_N_winter_mean','global_EQR_indicator_ntot_summer']].mean(axis = 1, skipna = False)
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
        print(self.name)
        merge_on = ['VISS_EU_CD', 'WATER_BODY_NAME', 'WATER_TYPE_AREA']
        
        def mean_of_indicators(indicator_name):
#             print(self.mapping_objects['quality_element'].indicator_config.loc[indicator_name]['parameters'])
            parameters = self.mapping_objects['quality_element'].indicator_config.loc[indicator_name]['parameters'].split(', ') 
            if 'indicator_' not in parameters[0]: 
                if 'qe_' not in parameters[0]:
                    return False
#             print(indicator_name, parameters)
            if len(parameters) == 2:
#                 print(self.indicator_dict[parameters[0]].columns)    
                mean_of_indicators = self.indicator_dict[parameters[0]].merge(self.indicator_dict[parameters[1]], on = merge_on, how = 'inner', copy=True, suffixes = ['_' + par for par in parameters])
#                 print('columns 1 merge', mean_of_indicators.columns)
                mean_of_indicators['global_EQR_'+indicator_name] = mean_of_indicators[['global_EQR' + '_' + parameters[0],'global_EQR' +'_' + parameters[1]]].mean(axis = 1, skipna = False)
                mean_of_indicators['STATUS_'+indicator_name] = mean_of_indicators['global_EQR_'+indicator_name].apply(lambda x: self.get_status_from_global_EQR(x))
#                 print('columns 2', mean_of_indicators.columns)
                self.indicator_dict[indicator_name] = mean_of_indicators
                self.sld.save_df(mean_of_indicators, indicator_name)
            elif len(parameters) == 1:
                col_list = list(self.indicator_dict[parameters[0]].columns)
                [col_list.remove(r) for r in merge_on]
                {k: k+'_'+parameters[0] for k in col_list}
                self.indicator_dict[indicator_name] = self.indicator_dict[parameters[0]].rename(columns = {k: k+'_'+indicator_name for k in col_list})
                self.sld.save_df(self.indicator_dict[indicator_name], indicator_name)
    
        for indicator in self.mapping_objects['quality_element'].indicator_config.index:
            if self.mapping_objects['quality_element'].indicator_config.loc[indicator]['quality element'] == self.name:
                mean_of_indicators(indicator)
    
###############################################################################
if __name__ == '__main__':
    nr_marks = 60
    print('='*nr_marks)
    print('Running module "quality_factor.py"')
    print('-'*nr_marks)
    print('')
    
    