# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 17:32:56 2017

@author: a002028
"""

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
import datetime
import core

import pandas as pd 
import numpy as np
import time


# Directories 
export_directory = u'D:\\Utveckling\\GitHub\\ekostat_calculator\\test_data\\test_exports\\'
filter_parameters_directory = 'D:/Utveckling/GitHub/ekostat_calculator/test_data/filters/' 
first_filter_directory = 'D:/Utveckling/GitHub/ekostat_calculator/test_data/filtered_data' 
raw_data_file_path = 'D:/Utveckling/GitHub/ekostat_calculator/test_data/raw_data/'
mapping_directory = 'D:/Utveckling/GitHub/ekostat_calculator/test_data/mappings/mapping_parameter_dynamic_extended.txt' 

filter_parameters_file_zooben = u'filter_fields_zoobenthos.txt'
filter_parameters_file_fysche = u'filter_fields_physical_chemical.txt'

# Row data
fid_zooben = u'zoobenthos_2016_row_format_2.txt'
fid_fysche = u'BOS_HAL_2015-2016_row_format_2.txt'

# Parameter mapping
parameter_mapping = core.ParameterMapping()
parameter_mapping.load_mapping_settings(file_path=mapping_directory)

#fp = core.data_handlers.DataFrameHandler()#.read_filter_file(filter_parameters_directory + filter_parameters_file, get_as_dict=True)
#fp.read_filter_file(filter_parameters_directory + filter_parameters_file)#, get_as_dict=True)
#fp.filter_parameters
#fpp = core.AttributeDict()#._add_array_to_attributes(**fp.filter_parameters)
#fpp._add_array_to_attributes(**fp.filter_parameters)
#print(fp.filter_parameters.use_parameters)
# Handle
#raw_data = core.DataHandler('raw')
#raw_data.add_txt_file(raw_data_file_path + fid, data_type='row', map_object=parameter_mapping)
#
## Row data handling
#raw_data._filter_row_data(fp=filter_parameters, map_object=parameter_mapping)
#raw_data.get_column_data_format(raw_data.row_data, filter_parameters)
#raw_data.save_data(export_directory)


## Row data handling new version
raw_data = core.DataHandler()
raw_data.physical_chemical.load_source(file_path=raw_data_file_path + fid_fysche,
                                       raw_data_copy=True)
raw_data.physical_chemical.save_data_as_txt(directory=u'', prefix=u'Column_format')

#raw_data.physical_chemical.raw_data_format
#raw_data.physical_chemical.row_data.keys()
#raw_data.physical_chemical.filter_parameters.use_parameters

raw_data.zoobenthos.load_source(file_path=raw_data_file_path + fid_zooben,
                                raw_data_copy=True)
raw_data.zoobenthos.save_data_as_txt(directory=u'', prefix=u'Column_format')

"""
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
"""
#wd = u'D:/Utveckling/GitHub/ekostat_calculator/test_data/johannes/'
#fid = u'BOS_HAL_2015-2016_row_format.txt'
##fid = u'zoobenthos_2016_row_format.txt'
#
#fid_filter_para = u'filter_fields_physical_chemical.txt'
##fid_filter_para = u'filter_fields_zoobenthos.txt'
##fid = u'test_data_format_converter.txt'
#para_mapping = u'mapping_parameter_dynamic_extended.txt'


    