# -*- coding: utf-8 -*-

"""
Created on Mon Jul 10 15:27:01 2017

@author: a001985
"""
import os
import sys
import datetime
import core
import importlib
importlib.reload(core)

###############################################################################
class MWWorkSpace(core.WorkSpace):
    def __init__(self, **kwargs): 
        # Merge later on. Inherit for now to keep things separate.  
        core.WorkSpace.__init__(self, **kwargs) 
        
        self._load_attributes()
        self.load_settings_files()
        
    #==========================================================================
    def _load_attributes(self): 
        # Load attributes to be able to check what has been done
        self.first_filter = None
        self.filtered_data = None 
        self.raw_data = None 
        self.filtered_data = None 
        self.indicator_settings = {}
        
    #==========================================================================
    def load_settings_files(self): 
        # Load all settings file in the current WorkSpace filter folder... 
        
        # ...for now load test filters... 
        first_data_filter_file_path = root_directory + '/resources/indicator_settings/first_data_filter.txt' 
        self.first_filter = core.DataFilter('First filter', file_path=first_data_filter_file_path) 
        
        
        inidicator_settings_list = [root_directory + '/resources/indicator_settings/din_winter_settings.txt'] 
        # All indicators in directory should be loaded automatically 
        
        
        
        # Load indicator setting files. Internal attr since they are only used by other objects.  
        self._indicator_setting_files = {} 
        for file_path in inidicator_settings_list: 
            s = core.SettingsFile(file_path) 
            self._indicator_setting_files[s.indicator] = s
            
        # Load Filter settings. Filter settings are using indicator_setting_files-obects as data
        self.indicator_filter_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_filter_settings[indicator] = core.SettingsFilter(obj)
            
        # Load Ref settings. Filter settings are using indicator_setting_files-obects as data
        self.indicator_ref_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_ref_settings[indicator] = core.SettingsRef(obj) 
            
        # Load Tolerance settings. Filter settings are using indicator_setting_files-obects as data
        self.indicator_tolerance_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_tolerance_settings[indicator] = core.SettingsTolerance(obj)
        
    #==========================================================================
    def get_indicator_settings_name_list(self):
        return sorted(self.indicator_settings.keys()) 
    
    #==========================================================================
    def save_indicator_settings(self, indicator):
        self.indicator_settings[indicator].save_file() # Overwrites existing file if no file_path is given
        
    #==========================================================================
    def load_data(self): 
        # Load all data in the current WorkSpace data folder...
        
        # ...for now load test data...
        raw_data_file_path = root_directory + '/test_data/raw_data/data_BAS_2000-2009.txt'
        
        
        self.raw_data = core.DataHandler('raw')
        self.raw_data.add_txt_file(raw_data_file_path, data_type='column') 
        
    #==========================================================================
    def apply_first_filter(self):
        # Use first filter 
        print('{}\nApplying first filter\n'.format('*'*nr_marks))
        
        self.filtered_data = self.raw_data.filter_data(self.first_filter) 
        
    #==========================================================================
    def update_filter_settings(self, indicator=None, filter_settings=None):
        """
        filter_settings are dicts like: 
            filter_settings[type_area][variable] = value 
        """
        if filter_settings: 
            filter_object = self.indicator_filter_settings[indicator] 
            filter_object.set_values(filter_settings)
            

###############################################################################
class EventHandler(): 
    
    def __init__(self):
        self.root_directory = os.path.dirname( __file__ )
        self.load_workspaces() # Default
    
    #==========================================================================
    def load_workspaces(self):  
        self.workspace_directory = self.root_directory + '/workspaces'
        # Laod all workspaces in WorkSpaces 
        self.workspaces = {}
        # for workspace in "workspace-directory" 
        ws_default = 'default'
        ws_name_1 = 'mw_test_workspace_1'
        self.workspaces[ws_default] = core.WorkSpace(name=ws_default, parent_directory=self.workspace_directory) 
        self.workspaces[ws_name_1] = core.WorkSpace(name=ws_name_1, parent_directory=self.workspace_directory) 
        
        self.workspaces[ws_name_1].add_files_from_workspace(workspace_object=self.workspaces[ws_default], 
                                                           overwrite=False)
        
    #==========================================================================
    def get_workspace(self, work_space_name): 
        return self.workspaces[work_space_name]
        
    
###############################################################################
if __name__ == '__main__':
    nr_marks = 60
    print('='*nr_marks)
    print('Running module "mw_test_file.py"')
    print('-'*nr_marks)
    print('')
    
    root_directory = os.path.dirname(os.path.abspath(__file__))
    workspace_name = 'mw_test_workspace_1' 
    indicator_name = 'din_winter'
    
    e = EventHandler()
    ws = e.get_workspace(workspace_name)

    set_value_dict = {'1n': {'DEPTH_INTERVAL': [0, 20], 
                             'MONTH_LIST': [3,4,5]}, 
                      '3': {'MIN_NR_VALUES': 10}}
#    ws.update_filter_settings(indicator=indicator_name, filter_settings=set_value_dict)
    
#    month = s.get_value('2', 'MONTH_LIST')
#    s.set_value('2', 'MONTH_LIST', [1,2,3])
#    
    
#    s.set_values(set_value_dict)
#    s.save_settings(output_file_path)
#
#    
#    sf = SettingsFilter(s)

    
#    root_directory = os.path.dirname(os.path.abspath(__file__))
#    
##    core.StationList(root_directory + '/test_data/Stations_inside_med_typ_attribute_table_med_delar_av_utsjö.txt')
#    core.ParameterList()
#    
#    #--------------------------------------------------------------------------
#    # Directories and file paths
#    print('{}\nSet directories and file paths'.format('*'*nr_marks))
#    raw_data_file_path = root_directory + '/test_data/raw_data/data_BAS_2000-2009.txt'
#    first_filter_data_directory = root_directory + '/test_data/filtered_data' 
#    
#    first_data_filter_file_path = root_directory + '/test_data/filters/first_data_filter_test.txt' 
#    winter_data_filter_file_path = root_directory + '/test_data/filters/winter_data_filter.txt'
#    summer_data_filter_file_path = root_directory + '/test_data/filters/summer_data_filter.txt'
#    
#    tolerance_filter_file_path = root_directory + '/test_data/filters/tolerance_filter_template.txt'
#    
#    #--------------------------------------------------------------------------
#    # Filters 
#    print('{}\nInitiating filters'.format('*'*nr_marks))
#    first_filter = core.DataFilter('First filter', file_path = first_data_filter_file_path)
#    
#    winter_filter = core.DataFilter('winter_filter', file_path = winter_data_filter_file_path)
#    winter_filter.save_filter_file(root_directory + '/test_data/filters/winter_data_filter_save.txt') # mothod available
#    summer_filter = core.DataFilter('summer_filter', file_path = summer_data_filter_file_path)
#    summer_filter.save_filter_file(root_directory + '/test_data/filters/summer_data_filter_save.txt') # mothod available
#    tolerance_filter = core.ToleranceFilter('test_tolerance_filter', file_path = tolerance_filter_file_path)
#
#    #--------------------------------------------------------------------------
#    # Reference values
#    print('{}\nLoading reference values'.format('*'*nr_marks))
#    core.RefValues()
#    core.RefValues().add_ref_parameter_from_file('DIN_winter', root_directory + '/test_data/din_vinter.txt')
#    core.RefValues().add_ref_parameter_from_file('TOTN_winter', root_directory + '/test_data/totn_vinter.txt')
#    core.RefValues().add_ref_parameter_from_file('TOTN_summer', root_directory + '/test_data/totn_summer.txt')
#    
#    #--------------------------------------------------------------------------
#    #--------------------------------------------------------------------------
#    # Handler (raw data)
#    print('{}\nInitiate raw data handler\n'.format('*'*nr_marks))
#    raw_data = core.DataHandler('raw')
#    raw_data.add_txt_file(raw_data_file_path, data_type='column') 
#    
#    # Use first filter 
#    print('{}\nApply data filters\n'.format('*'*nr_marks))
#    filtered_data = raw_data.filter_data(first_filter) 
#    
#    # Save filtered data (first filter) as a test
#    filtered_data.save_data(first_filter_data_directory)
#    
#    # Load filtered data (first filter) as a test
#    loaded_filtered_data = core.DataHandler('first_filtered')
#    loaded_filtered_data.load_data(first_filter_data_directory)
#
#
#    # Create and fill QualityFactor
#    print('{}\nCreate QualityFactor and set data_handler\n'.format('*'*nr_marks))
#    qf_NP = core.QualityFactorNP()
#    
#    qf_NP.set_data_handler(data_handler = loaded_filtered_data)
#    #Class IndicatorBase:
#    #No attribute for parameter DIN  'NoneType' object has no attribute 'set_data_handler'
#    
#    # Filter parameters in QualityFactorNP
#    print('{}\nApply season filters to parameters in QualityFactor\n'.format('*'*nr_marks))
#    # First general filter 
#    qf_NP.filter_data(data_filter_object = first_filter) 
#    # winter filter
#    qf_NP.filter_data(data_filter_object = winter_filter, indicator = 'TOTN_winter') 
#    qf_NP.filter_data(data_filter_object = winter_filter, indicator = 'DIN_winter')
#    # summer filter
#    qf_NP.filter_data(data_filter_object = summer_filter, indicator = 'TOTN_summer')
#    
#    print('{}\nApply tolerance filters to all indicators in QualityFactor and get result\n'.format('*'*nr_marks))
##    qf_NP.calculate_quality_factor(tolerance_filter)
#    qf_NP.get_EQR(tolerance_filter)    
#    
#    # Parameter
#    print('-'*nr_marks)
#    print('done')
#    print('-'*nr_marks)
#    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    