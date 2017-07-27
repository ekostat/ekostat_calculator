# -*- coding: utf-8 -*-

"""
Created on Mon Jul 10 15:27:01 2017

@author: a001985
"""
import os
import sys
import datetime
import est_core

    
    
    
###############################################################################
if __name__ == '__main__':
    nr_marks = 60
    print('='*nr_marks)
    print('Running module "mw_test_file.py"')
    print('-'*nr_marks)
    print('')
    
    est_core.StationList('D:/Utveckling/g_EKOSTAT_tool/test_data/Stations_inside_med_typ_attribute_table_med_delar_av_utsjö.txt')
    est_core.ParameterList()
    
    #--------------------------------------------------------------------------
    # Directories an file paths
#    raw_data_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/raw_data/data.txt'
    raw_data_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/raw_data/data_BAS_2000-2009.txt'
    first_filter_directory = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filtered_data' 
    
    indicator_save_directory = 'D:/Utveckling/g_EKOSTAT_tool/test_data/indicator_saves' 
    indicator_save_directory_calc = indicator_save_directory + '/calculations'
    indicator_save_directory_data = indicator_save_directory + '/data'
    
    
    #--------------------------------------------------------------------------
    # Filters 
    first_data_filter_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filters/first_data_filter.txt'
    first_filter = est_core.DataFilter('First filter', file_path=first_data_filter_file_path)
    
    winter_data_filter_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filters/winter_data_filter.txt'
    winter_filter_1 = est_core.DataFilter('winter_filter', file_path=winter_data_filter_file_path)
    winter_filter_1.save_filter_file('D:/Utveckling/g_EKOSTAT_tool/test_data/filters/winter_data_filter_save.txt')
    
    tolerance_filter_file_path = 'D:/Utveckling/g_EKOSTAT_tool/test_data/filters/tolerance_filter_template.txt'
    tolerance_filter = est_core.ToleranceFilter('test_tolerance_filter', file_path=tolerance_filter_file_path)

    est_core.RefValues()
    est_core.RefValues().add_ref_parameter_from_file('DIN_winter', 'D:/Utveckling/g_EKOSTAT_tool/test_data/din_vinter.txt')
    est_core.RefValues().add_ref_parameter_from_file('TN_winter', 'D:/Utveckling/g_EKOSTAT_tool/test_data/totn_vinter.txt')
    
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
    qf_NP.filter_data(data_filter_object=first_filter, indicator='DIN_summer') 
    qf_NP.filter_data(data_filter_object=winter_filter_1, indicator='DIN_winter') 
    qf_NP.filter_data(data_filter_object=winter_filter_1, indicator='TN_winter') 
    
    
    
    tolerance_filters = {'SALT': tolerance_filter}
    
    qf_NP.tn_winter.get_ek_value(tolerance_filters)
    
    
    date = datetime.datetime(2000, 1, 17, 17, 20)
    
    prof = qf_NP.din_winter.ntra.get_closest_profile_in_time(datetime_object=date, 
                                                             tolerance_filter=tolerance_filter)
    
    
    
    # Parameter
    print('-'*nr_marks)
    print('done')
    print('-'*nr_marks)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    