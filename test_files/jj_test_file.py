# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 17:32:56 2017

@author: a002028
"""

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))[:-10]
sys.path.append(current_path)
import datetime
import core
import importlib

import pandas as pd 
import numpy as np
import time


# Directories 
source_dir = u'D:\\Utveckling\\GitHub\\ekostat_calculator\\'

#export_directory = source_dir+u'test_data\\test_exports\\'
filter_parameters_directory = source_dir+'test_data/filters/' 
first_filter_directory = source_dir+'test_data/filtered_data' 
raw_data_file_path = source_dir+'test_data/raw_data/'
mapping_directory = source_dir+'test_data/mappings/mapping_parameter_dynamic_extended.txt' 
input_data_directory = source_dir+'workspaces\\default\\input_data\\'
export_directory = input_data_directory+u'exports\\'
resource_directory = source_dir+'resources\\'

filter_parameters_file_chl_integ = u'filter_fields_chlorophyll_integrated.txt'
filter_parameters_file_fysche = u'filter_fields_physical_chemical.txt'
filter_parameters_file_zooben = u'filter_fields_zoobenthos.txt'

# Row data
fid_chl_integ = u'raw_data\\chlorophyll_integrated_2015_2016_row_format.txt'
fid_phyche = u'raw_data\\BOS_HAL_2015-2016_row_format_2.txt'
fid_phyche_col = u'raw_data\\BOS_BAS_2016-2017_column_format.txt'
fid_phyche_col_big = u'raw_data\\phyche_2008_2017_column_format.txt'
fid_phyto = u'raw_data\\phytoplankton_2016_row_format.txt'
fid_zooben = u'raw_data\\zoobenthos_2016_row_format_2.txt'

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

#------------------------------------------------------------------------------
## Row data handling new version
#raw_data = core.DataHandler(input_data_directory=input_data_directory, 
#                            resource_directory=resource_directory)

#------------------------------------------------------------------------------
#raw_data.chlorophyll.load_source(file_path=input_data_directory + fid_chl_integ,
#                                 raw_data_copy=True)
#raw_data.chlorophyll.save_data_as_txt(directory=u'', prefix=u'Column_format')

#------------------------------------------------------------------------------
#raw_data.physical_chemical.load_source(file_path=input_data_directory + fid_phyche,
#                                       raw_data_copy=True)
##------------------------------------------------------------------------------
#raw_data.physical_chemical.load_source(file_path=input_data_directory + fid_phyche_col,
#                                       raw_data_copy=True)
#------------------------------------------------------------------------------
#raw_data.physical_chemical.load_source(file_path=input_data_directory + fid_phyche_col_big,
#                                       raw_data_copy=True)
#------------------------------------------------------------------------------
#raw_data.physical_chemical.save_data_as_txt(directory=u'', prefix=u'Column_format')
#------------------------------------------------------------------------------
#raw_data.physical_chemical.raw_data_format
#raw_data.physical_chemical.row_data.keys()
#raw_data.physical_chemical.filter_parameters.use_parameters

#------------------------------------------------------------------------------
#raw_data.phytoplankton.load_source(file_path=input_data_directory + fid_phyto,
#                                   raw_data_copy=True)
#raw_data.phytoplankton.save_data_as_txt(directory=export_directory, prefix=u'Column_format')

#------------------------------------------------------------------------------
#raw_data.zoobenthos.load_source(file_path=input_data_directory + fid_zooben,
#                                raw_data_copy=True)
#raw_data.zoobenthos.save_data_as_txt(directory=u'', prefix=u'Column_format')

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


#raw_data.merge_all_data(save_to_txt=True)


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
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


root_directory = "../" #os.getcwd()
workspace_directory = source_dir + '/workspaces' 
resource_directory = source_dir + '/resources'

default_workspace = core.WorkSpace(name='default', 
                                   parent_directory=workspace_directory, 
                                   resource_directory=resource_directory)
jj_workspace = default_workspace.make_copy_of_workspace('JJ', overwrite=True)
#default_workspace.load_all_data()


include_stations = ['BROFJORDEN', 'BYFJORDEN']
exclude_stations = ['BROFJORDEN'] # Example that both include and exclude are possible 
include_years = ['2015', '2017']


jj_workspace.set_data_filter(step=0, filter_type='include_list', filter_name='STATN', data=include_stations)
jj_workspace.set_data_filter(step=0, filter_type='exclude_list', filter_name='STATN', data=exclude_stations)
jj_workspace.set_data_filter(step=0, filter_type='include_list', filter_name='MYEAR', data=include_years)



#jj_workspace.apply_first_filter()
jj_workspace.apply_data_filter_step_0()

#jj_workspace.index_handler.booleans

wbo = jj_workspace.mapping_objects['water_body']

df_default_1 = jj_workspace.get_data_filter_object(subset='default_subset', step=1)


sdf_default_2 = jj_workspace.get_indicator_settings_data_filter_object(subset='default_subset', step=2, indicator='din_winter')

df_default_1.include_list_filter


jj_workspace.set_data_filter(step=1, subset='default_subset', filter_type='include_list')#, filter_name='water_body_name', data=['N m Bottenvikens kustvatten', 'Bulleröfjärden', 'Norrfjärden'])


df_default_2 = jj_workspace.get_data_filter_object(subset='default_subset', step=2) # This should not be possible


jj_workspace.index_handler.add_filter(filter_object=df_default_1, subset='default_subset', step='step_1')



#jj_workspace.index_handler.booleans







