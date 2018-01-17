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
if __name__ == '__main__':
    nr_marks = 60
    print('='*nr_marks)
    print('Running module "lv_test_file.py"')
    print('-'*nr_marks)
    print('')
    
    root_directory = os.path.dirname(os.path.abspath(__file__))[:-4]
    
#    core.StationList(root_directory + '/test_data/Stations_inside_med_typ_attribute_table_med_delar_av_utsjö.txt')
    core.ParameterList()
    
    #--------------------------------------------------------------------------
    # Directories and file paths
    print('{}\nSet directories and file paths'.format('*'*nr_marks))
    raw_data_file_path = root_directory + '/test_data/raw_data/data_BAS_2000-2009.txt'
    first_filter_data_directory = root_directory + '/test_data/filtered_data' 
    
    first_data_filter_file_path = root_directory + '/test_data/filters/first_data_filter_test.txt' 
    winter_data_filter_file_path = root_directory + '/test_data/filters/winter_data_filter.txt'
    summer_data_filter_file_path = root_directory + '/test_data/filters/summer_data_filter.txt'
    
    tolerance_filter_file_path = root_directory + '/test_data/filters/tolerance_filter_template.txt'
    
    #--------------------------------------------------------------------------
    # Filters 
    print('{}\nInitiating filters'.format('*'*nr_marks))
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    