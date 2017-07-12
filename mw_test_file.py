# -*- coding: utf-8 -*-

"""
Created on Mon Jul 10 15:27:01 2017

@author: a001985
"""
import os
import sys
import est_core

    
    
    
###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "mw_test_file.py"')
    print('-'*50)
    print('')
    
    #--------------------------------------------------------------------------
    # Directories an file paths
    raw_data_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/raw_data/data.txt'
    first_filter_directory = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filtered_data' 
    
    indicator_save_directory = 'D:/Utveckling/g_EKOSTAT_tool/test_data/indicator_saves' 
    indicator_save_directory_calc = indicator_save_directory + '/calculations'
    indicator_save_directory_data = indicator_save_directory + '/data'
    
    
    #--------------------------------------------------------------------------
    # Filters 
    first_filter = est_core.DataFilter('First filter')
    winter_filter = est_core.DataFilter('winter_filter')
    winter_filter.set_filter('MONTHS', [12, 1, 2])
    
    
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    # Handler
    raw_data = est_core.DataHandler('raw')
    raw_data.add_txt_file(raw_data_file_path, data_type='column') 
    
    
    filtered_data = raw_data.filter_data(first_filter)
    
    # Save filtered data (first filter)
    filtered_data.save_data(first_filter_directory)
    
    
    # Load filtered data (first filter)
    loaded_filtered_data = est_core.DataHandler('first_filtered')
    loaded_filtered_data.load_data(first_filter_directory)


    # Create and fill QualityFactor
    qf_NP = est_core.QualityFactorNP()
    qf_NP.set_data_handler(data_handler=loaded_filtered_data)
    
    # Filter parameters in QualityFactorNP 
    qf_NP.filter_data(filter_data_object=first_filter, indicator='DIN_summer')
    qf_NP.filter_data(filter_data_object=winter_filter, indicator='DIN_winter')
    
    
    # Parameter
    print('done')
    