# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:05:36 2018

@author: a001985
"""

import os
import shutil
import time
import datetime

import json
import codecs 
import re

import pandas as pd
import pickle

import logging
import importlib
# TODO: Move this!

#current_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
#current_path = os.path.dirname(os.path.realpath(__file__))
#print(current_path)
##sgdöljdf
#if current_path not in sys.path:
#    sys.path.append(current_path)

import core
import core.exceptions as exceptions
"""
Module to handle all events linked to the Django application. 
Maybe this should be in the root? Maybe not a class, only functions? Maybe __name__ == "__main__"?

MW: Started this to start logging functionality. 
""" 

#==========================================================================
def timer(func):
    """
    Created     20180719    by Magnus Wenzer
        
    """
    def f(*args, **kwargs):
        _logger = core.get_log('event_handler')
        _logger.debug('Start: "{.__name__}"'.format(func))
        from_time = time.time()
        rv = func(*args, **kwargs)
        to_time = time.time()
        _logger.debug('Stop: "{.__name__}". Time for running method was {}'.format(func, to_time-from_time))
        return rv
    return f


class EventHandler(object): 
    def __init__(self, 
                 user_id=None, 
                 workspace_directory='',
                 resource_directory='', 
                 log_directory='', 
                 test_data_directory='', 
                 temp_directory='', 
                 reload_mapping_objects=False): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180919    by Magnus Wenzer
        
        MW 20180530: Only one usr per event handler. 
        In terms of user_id this does not really matter at the moment. 
        user_id must be given in every call and the corresponding uuid_mapping 
        file is loaded in the method call if neaded. 
        """
        if not all([user_id, workspace_directory, resource_directory, log_directory]): 
            raise exceptions.MissingInputVariable('Missing directory paths when creating EventHandler instance.')
        
        t0 = time.time()
        
        self.time_get_workspace = 0
        
        self.user_id = user_id
        self.workspace_directory = workspace_directory
        self.resource_directory = resource_directory
        self.log_directory = log_directory
        self.test_data_directory = test_data_directory 
        self.temp_directory = temp_directory
        self.reload_mapping_objects = reload_mapping_objects
        
        # Create directories 
        if not os.path.exists(self.workspace_directory):
            os.mkdir(self.workspace_directory)
        
        
        self.log_id = 'event_handler'
        
        self.include_status = ['editable', 'readable']
        self.all_status = ['editable', 'readable', 'deleted', 'inactive']
         
        # Add logger
        core.add_log(log_id=self.log_id, 
                     log_directory=self.log_directory, 
                     log_level='DEBUG', 
                     on_screen=True, 
                     prefix='main')
        
        # Test main logger
        self._logger = core.get_log(self.log_id)
        self._logger.debug('Start EventHandler: {}'.format(self.log_id))
#        self._logger.debug('')
#        self._logger.info('TEST info logger')
#        self._logger.warning('TEST warning logger')
#        self._logger.error('TEST error logger')
#        self._logger.debug('TEST debug logger')
        
        self.workspaces = {}
        
        tm = time.time()
        self._load_mapping_objects()
        self._logger.debug('Time for mapping: {}'.format(time.time()-tm))             
        
        if self.test_data_directory:
            self.load_test_requests()  
            
        self._logger.debug('Time for initiating EventHandler: {}'.format(time.time()-t0))
    
    
    #==========================================================================
    @timer
    def test_timer(self):
        for _ in range(10000000):
            9+9
        print('test')
    
    
        
    #==========================================================================
    def _load_mapping_objects(self):
        """
        Updated     20180721    by Magnus Wenzer
        """
        mappings_pickle_file_path = os.path.join(self.resource_directory, 'mapping_objects.pkl') 
        if os.path.exists(mappings_pickle_file_path) and not self.reload_mapping_objects:
            self._logger.debug('Loading mapping files from pickle file.')
            with open(mappings_pickle_file_path, "rb") as fid: 
                self.mapping_objects = pickle.load(fid)
                
        else:
            self._logger.debug('Loading mapping files from original files.')
            # Mapping objects
            self.mapping_objects = {}
            self.mapping_objects['water_body'] = core.WaterBody(file_path=os.path.join(self.resource_directory, 'mappings/water_body_match.txt'))
            self.mapping_objects['quality_element'] = core.QualityElement(file_path=os.path.join(self.resource_directory, 'Quality_Elements.cfg'))
            self.mapping_objects['hypsographs'] = core.Hypsograph(file_path=os.path.join(self.resource_directory, 'mappings/hypsographs.txt'))
            
            self.mapping_objects['display_mapping'] = core.ParameterMapping()
            self.mapping_objects['display_mapping'].load_mapping_settings(file_path=os.path.join(self.resource_directory, 'mappings/display_mapping.txt'))
            
            self.mapping_objects['indicator_settings_homogeneous_parameters'] = core.IndSetHomPar(file_path=os.path.join(self.resource_directory, 'mappings/indicator_settings_homogeneous_parameters.txt'))
            self.mapping_objects['indicator_settings_matching_columns'] = core.SimpleList(file_path=os.path.join(self.resource_directory, 'mappings/indicator_settings_matching_columns.txt'))
            self.mapping_objects['indicator_settings_items_to_show_in_gui'] = core.SimpleList(file_path=os.path.join(self.resource_directory, 'mappings/indicator_settings_items_to_show_in_gui.txt'))
            self.mapping_objects['indicator_settings_items_editable_in_gui'] = core.SimpleList(file_path=os.path.join(self.resource_directory, 'mappings/indicator_settings_items_editable_in_gui.txt'))
            self.mapping_objects['datatype_list'] = core.MappingObject(file_path=os.path.join(self.resource_directory, 'mappings/datatype_list.txt'))
            self.mapping_objects['sharkweb_mapping'] = core.MappingObject(file_path=os.path.join(self.resource_directory, 'mappings/sharkweb_search_mapping.txt'))
            self.mapping_objects['sharkweb_settings'] = core.SharkwebSettings(file_path=os.path.join(self.resource_directory, 'mappings/sharkweb_settings.txt'))
            self.mapping_objects['label_mapping'] = core.MappingObject(file_path=os.path.join(self.resource_directory, 'mappings/display_mapping.txt'), 
                                                                       from_column='internal', 
                                                                       to_column='label')
            
            with open(mappings_pickle_file_path, "wb") as fid:
                pickle.dump(self.mapping_objects, fid) 
        
        
    #==========================================================================
    def _change_ok(self, alias): 
        if alias in ['default_workspace', 'default_subset']: 
            self._logger.warning('Not allowed to make changes to "{}"!'.format(alias))
            return False
        return True
    
    
    #==========================================================================
    def _check_valid_uuid(self, workspace_uuid=None, subset_uuid=None): 
        """
        Created     20180719    by Magnus Wenzer
        Updated     20180720    by Magnus Wenzer
        """
        if not workspace_uuid:
            raise exceptions.InvalidInputVariable 
        
#        print('===', workspace_uuid, subset_uuid)
        if not subset_uuid:
#            print('IF')
            uuid_mapping = self._get_uuid_mapping_object() 
            
            if workspace_uuid in uuid_mapping.get_uuid_list_for_user(status=['deleted']): 
                raise exceptions.WorkspaceIsDeleted(workspace_uuid)
            elif workspace_uuid not in uuid_mapping.get_uuid_list_for_user(): 
                raise exceptions.WorkspaceNotFound(workspace_uuid)

        else:
#            print('ELSE')
            workspace_object = self.workspaces.get(workspace_uuid, None) 
            uuid_mapping = workspace_object.uuid_mapping
            
            if subset_uuid in uuid_mapping.get_uuid_list_for_user(status=['deleted']): 
                raise exceptions.SubsetIsDeleted(subset_uuid)
            elif subset_uuid not in uuid_mapping.get_uuid_list_for_user(): 
                raise exceptions.SubsetNotFound(subset_uuid)
                
    
    #==========================================================================
    def _get_active_values_in_list_with_dicts(self, dict_list): 
        """
        Created     20180315    by Magnus Wenzer
        Updated     20180315    by Magnus Wenzer
        
        Checks a list containing dictionaries. For each dict in list, if active, 
        value is put in return list. 
        """
        return_list = []
        for item in dict_list:
            if item['value']: 
                return_list.append(item['key'])
        return return_list
        
    
    #==========================================================================
    def _get_mapping_for_name_in_dict(self, name, list_of_dicts): 
        return_mapping = {} 
        if not list_of_dicts:
            return return_mapping
        for item in list_of_dicts:
            return_mapping[item[name]] = item
        return return_mapping
        

    #==========================================================================
    def _get_selected_areas_from_subset_request(self, request):
        """
        Created     20180611    by Magnus Wenzer
        Updated 
        
        Returns a dict like: 
            selected_areas = {'water_district_list': [], 
                              'type_area_list': [], 
                              'viss_eu_cd_list': []}
            
        ...containing the selected areas in subset reques / response
        """
        selected_areas = {'water_district_list': [], 
                          'type_area_list': [], 
                          'viss_eu_cd_list': []}
        
        areas = request.get('areas', [])
        for water_district in areas:
            if water_district.get('value', False):
                selected_areas['water_district_list'].append(water_district['key']) 
                for type_area in water_district.get('children', []): 
                    if type_area.get('value', False): 
                        selected_areas['type_area_list'].append(type_area['key'])
                        for water_body in type_area.get('children', []): 
                            if water_body.get('value', False): 
                                selected_areas['viss_eu_cd_list'].append(water_body['key'])
                                
        return selected_areas
    
    
    #==========================================================================
    def _get_uuid_mapping_object(self): 
        file_path = '{}/uuid_mapping_{}.txt'.format(self.workspace_directory, self.user_id)
        if not os.path.exists(file_path):
#            print('=file_path'.upper(), file_path)
            shutil.copy('{}/templates/uuid_mapping.txt'.format(self.resource_directory), 
                        file_path)
#            print('-file_path'.upper(), file_path)
        uuid_mapping_object = core.UUIDmapping(file_path, self.user_id)
        return uuid_mapping_object
    
    
    #==========================================================================
    def _get_string_for_water_body(self, water_body): 
        """
        Created 20180721    by Magnus
        """
        name = self.mapping_objects['water_body'].get_display_name(water_body=water_body)
        return '{} ({})'.format(name, water_body)
       
        
    #==========================================================================
    def _get_string_for_type_area(self, type_area): 
        """
        Created 20180721    by Magnus
        """
        name = self.mapping_objects['water_body'].get_display_name(type_area=type_area)
        return '{} ({})'.format(name, type_area)
    
    
    #==========================================================================
    def _get_area_from_string(self, area_string): 
        """
        Created 20180721    by Magnus
        """
        return area_string.split('(')[-1].split(')')[0]
    
        
    #==========================================================================
    def apply_data_filter(self, 
                          workspace_uuid=None,
                          subset_uuid=None,
                          step='step_1'): 
        """
        Updated     20180530    by Magnus Wenzer 
        """
        w = self.get_workspace(workspace_uuid)
        w.apply_data_filter(subset=subset_uuid, step=step)
        
        
    #==========================================================================
    def apply_indicator_data_filter(self,   
                                    workspace_uuid='',
                                    subset_uuid='', 
                                    indicator='', 
                                    type_area='', 
                                    step='step_2'): 
        """
        Created     20180319    by Magnus Wenzer
        Updated     20180530    by Magnus Wenzer
        """
        w = self.get_workspace(workspace_uuid)
        all_ok = w.apply_indicator_data_filter(subset=subset_uuid, 
                                               indicator=indicator, 
                                               type_area=type_area, 
                                               step=step)
        return all_ok
        
    
    #==========================================================================
    def change_workspace_alias(self, unique_id, new_alias): 
        """
        Updated     20180530    by Magnus Wenzer 
        """
        
        uuid_mapping = self._get_uuid_mapping_object()
        if not unique_id:
            return False
        uuid_mapping.set_alias(unique_id, new_alias)
    
    
    #==========================================================================
    def copy_subset(self, 
                    workspace_uuid=None, 
                    subset_source_uuid=None, 
                    subset_target_alias=None): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180717    by Magnus Wenzer
        
        """
        workspace_object = self.workspaces.get(workspace_uuid, False)
        if not workspace_object:
            self._logger.warning('Workspace "{}" not loaded.'.format(subset_source_uuid))
            return False
#        print('!!!!!!!!!!!!', subset_source_alias) 
#        print('!!!!!!!!!!!!', subset_target_alias) 
#            print('subset_source_alias'.upper(), subset_source_alias)
        self._logger.debug('Trying to copy subset "{}"'.format(subset_source_uuid))
#        try:
        return_dict = workspace_object.copy_subset(subset_source_uuid, subset_target_alias)
#        except:
#            raise 
#        print('return_dict'.upper(), return_dict)
        return return_dict
        
    #==========================================================================
    def copy_workspace(self, source_uuid=None, target_alias=None): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180917    by Lena Viktorsson
        
        """ 
        if self.user_id == 'default':
            self._logger.warning('Can not copy workspace as default user. ')
            return 
        
        uuid_mapping = self._get_uuid_mapping_object()

        # Add UUID for workspace in uuid_mapping 
        target_uuid = uuid_mapping.add_new_uuid_for_alias(target_alias)
        if not target_uuid:
            self._logger.debug('Could not add workspace with alias "{}". Workspace already exists!'.format(target_alias)) 
            raise exceptions.WorkspaceAlreadyExists 
#            return False
        
        # Copy all directories and files in workspace 
        
        # 20180917: default workspaces has been oved to theresources directory
        default_workspace_path = os.path.join(self.resource_directory, 'default_workspaces')
        default_workspaces_list = os.listdir(default_workspace_path) 
        if source_uuid in default_workspaces_list:
#            print(type(default_workspaces_list))
#            print(type(source_uuid))
            source_workspace_path = os.path.join(default_workspace_path, source_uuid)
        else:
            source_workspace_path = '/'.join([self.workspace_directory, source_uuid])
            
        target_workspace_path = '/'.join([self.workspace_directory, target_uuid])
        
#        print('source_workspace_path:', source_workspace_path)
#        print('target_workspace_path:', target_workspace_path)
        
        
        
        self._logger.debug('Trying to copy workspace "{}". Copy has alias "{}"'.format(source_uuid, target_alias))
        
        # Copy files
        shutil.copytree(source_workspace_path, target_workspace_path)
        
        """
        No data is loaded yet 
        Now we need to change uuid for subsets. 
        Do this by creating an UUID mapping object the subset and: 
            1: rename in mapping file 
            2: rename subset folder 
        """ 
        target_subset_uuid_mapping_file = '{}/subsets/uuid_mapping.txt'.format(target_workspace_path) 
        uuid_object = core.UUIDmapping(target_subset_uuid_mapping_file, self.user_id)
        
        uuid_list = uuid_object.get_uuid_list_for_user()
        for u_id in uuid_list:
            new_uuid = uuid_object.set_new_uuid(u_id)
            current_subset_path = '{}/subsets/{}'.format(target_workspace_path, u_id)
            new_subset_path = '{}/subsets/{}'.format(target_workspace_path, new_uuid)
            os.rename(current_subset_path, new_subset_path)
        
        status = uuid_mapping.get_status(unique_id=target_uuid) # Check in case default is changed
        
        return {'alias': target_alias,
                'workspace_uuid': target_uuid,
            	  'status': status}
    
    
    #==========================================================================
    def delete_subset(self, workspace_uuid=None, subset_alias=None, subset_uuid=None, permanently=False): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180530    by Magnus Wenzer
        
        Deletes the given subset in the given workspace. 
        """ 
        if not self._change_ok(workspace_uuid):
            return False 
        if not self._change_ok(subset_alias):
            return False
        
        if not workspace_uuid:
            return False
        workspace_object = self.workspaces.get(workspace_uuid, False)
        if not workspace_object:
            return False
        
        return workspace_object.delete_subset(unique_id=subset_uuid, permanently=permanently)
        
    
    #==========================================================================
    def delete_workspace(self, unique_id=None, permanently=False): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180223    by Lena Viktorsson
        
        Deletes the given workspace. 
        """ 

        
        uuid_mapping = self._get_uuid_mapping_object()
#        print('USER_ID', user_id)
        if unique_id not in uuid_mapping.get_uuid_list_for_user():
            return False

        alias = uuid_mapping.get_alias(unique_id)
        
#        if unique_id not in self.workspaces.keys(): 
#            self._logger.warning('Workspace "{}" with alias "{}" is not loaded!'.format(unique_id, alias))
#            return False 

        if permanently:
            path_to_remove = '/'.join([self.workspace_directory, unique_id])
            if 'workspace' not in path_to_remove:
                self._logger.error('Trying to delete workspace "{}" with alias "{}" but the path to delete is not secure!'.format(unique_id, alias)) 
                return False
            if os.path.exists(path_to_remove) is False:
                self._logger.error('Trying to delete workspace "{}" with alias "{}" but cannot find workspace with this uuid!'.format(unique_id, alias)) 
                return False
            
            self._logger.warning('Permanently deleting workspace "{}" with alias "{}".'.format(unique_id, alias))
            # Delete files and folders: 
            shutil.rmtree(path_to_remove)
            
            # Remove objects and links 
            if unique_id in self.workspaces.keys():
                self.workspaces.pop(unique_id)
            
            # Remove in uuid_mapping
            uuid_mapping.permanent_delete_uuid(unique_id)
        else:
            self._logger.warning('Removing workspace "{}" with alias "{}".'.format(unique_id, alias)) 
            uuid_mapping.set_status(unique_id, 'deleted')
        
        return True 
     
        
    #==========================================================================
    def dict_data_source(self, 
                           workspace_uuid=None, 
                           file_name=None, 
                           request={}): 
        """
        Created     20180524    by Magnus Wenzer
        Updated     
        
        Return dict like: 
            {
                "filename": "chlorophyll_integrated_2015_2016_row_format.txt", 
                "status": True, 
                "loaded": True,
                "datatype": "chlorophyll"
            }
        """
        workspace_object = self.get_workspace(workspace_uuid) 
        if not workspace_object:
            return {}
        
        datatype_settings_object = workspace_object.datatype_settings
        if not datatype_settings_object.has_info:
            return {}
        
        if request: 
            print('REQUEST', request['status'], file_name)
            datatype_settings_object.set_status(file_name=file_name, status=request['status'])
            info_dict = request

        info_dict = datatype_settings_object.get_info_for_file(file_name) 
        info_dict['loaded'] = bool(info_dict['loaded'])
        info_dict['status'] = bool(info_dict['status'])
#            print('-'*50)
#            print(info_dict)
        if info_dict['filename'] == 'physicalchemical_sharkweb_data_fyskem_wb_2007-2017_20180320.txt':
            self.info_dict = info_dict
        return info_dict
        
        
    #==========================================================================
    def dict_indicator(self, 
                       workspace_uuid=None, 
                       subset_uuid=None, 
                       indicator=None, 
                       available_indicators=None, 
                       request={}, 
                       **kwargs): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180321    by Magnus Wenzer
        
        dict like: 
            {
							"label": "Biovolume - default",
							"status": "editable",
							'value': true,
							'key': "Biovolume - default", 
                        "settings": {}
						}
            
        Update 20180608 by MW: kwargs contains what to include. Currently options are: 
            inidcator_settings 

        Usage: 
            if kwargs.get('<include>'):
                "INCLUDE"
                
        """
        return_dict = {"label": "",
					   "status": "",
					   'value': False,
					   'key': "", 
                    "settings": []}
        
#        return_dict = {"label": "",
#					   "status": "",
#					   'value': False,
#					   'key': ""}
        
        workspace_object = self.get_workspace(workspace_uuid) 
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_uuid))
            return return_dict
        
        if subset_uuid == 'default_subset': 
            available_indicators = []
        else:
            self.action_apply_data_filter(workspace_uuid=workspace_uuid, subset_uuid=subset_uuid, step='step_1')
            available_indicators = workspace_object.get_available_indicators(subset=subset_uuid, step='step_1')
            
        # Check request 
        selected = True
        if request and 'value' in request.keys():
            selected = request['value']
            
        # Check if indicator is available 
        if indicator in available_indicators: 
            status = "editable"
        else:
            status = "readable"
            selected = False
            
        
#        return_dict["label"] = self.mapping_objects['display_mapping'].get_mapping(indicator, 'internal_name', 'display_en')
        return_dict["label"] = self.mapping_objects['label_mapping'].get_mapping(indicator)
        return_dict["status"] = status
        return_dict['value'] = selected
        return_dict['key'] = indicator
    
        if kwargs.get('indicator_settings') and status=='editable': 
            self.kwargs = kwargs
            request_list = []
            if request and 'settings' in request:
                request_list = request['settings']
            return_dict["settings"] = self.list_indicator_settings(workspace_uuid=workspace_uuid, 
                                                                    subset_uuid=subset_uuid, 
                                                                    indicator=indicator, 
                                                                    request=request_list, 
                                                                    **kwargs)
#            if indicator == 'din_winter':
#                dgfs
        return return_dict
    
    
    #==========================================================================
    def dict_time(self, workspace_uuid=None, subset_uuid=None, request=None, **kwargs): 
        """
        Created     20180317   by Magnus Wenzer
        Updated     20180919   by Magnus Wenzer
        """
        workspace_object = self.get_workspace(workspace_uuid) 
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_uuid))
            return {} 

        
        
        data_filter_object = subset_object.get_data_filter_object('step_1')
        if request:
            from_year = int(request['year_interval'][0]) 
            to_year = int(request['year_interval'][1])
#            print('='*50)
#            print('='*50)
#            print('='*50)
#            print(from_year, to_year)
            if from_year > to_year:
                raise exceptions.InvalidUserInput('years in wrong order', code='year_interval_invalid')
            
            # 20180916
            if 0:
                year_choices = request.get('year_choices')
                if not year_choices: 
                    raise exceptions.MissingInputVariable('choice list for year is missing', code='year_choices_missing') 
                    
                if not all([from_year in year_choices, to_year in year_choices]): 
                    raise exceptions.InvalidUserInput('years are not within range of choices', code='year_interval_invalid')
                
                
            year_list = [str(y) for y in range(from_year, to_year+1)]
            data_filter_object.set_filter(filter_type='include_list', 
                                          filter_name='MYEAR', 
                                          data=year_list)
            return request 
#            data_filter_object.set_filter(filter_type='include_list', 
#                                          filter_name='MONTH', 
#                                          data=request['month_list'])
            
        else:
            valid_years = None
            if type(kwargs.get('check_in_df', False)) != bool: 
                df = kwargs['check_in_df']
                valid_years = sorted(set(df['MYEAR']))
            else:
                valid_years = data_filter_object.get_include_list_filter('MYEAR')
                
            valid_years = sorted(map(int, valid_years)) # Cant be int64 for json to work
#            if valid_years: 
#                from_year = 
#                if 
            
#            year_choices = [int(item) for item in kwargs.get('year_choices', list(range(1980, datetime.datetime.now().year+1)))] # Cant be int64 for json to work
#            print('&'*50)
#            print(year_list[0], type(year_list[0]))
#            print(year_choices[0], type(year_choices[0]))
#            month_list = sorted(map(int, data_filter_object.get_include_list_filter('MONTH')))
            
            return {'year_interval': [valid_years[0], valid_years[-1]], 
                    'year_choices': valid_years}#, "month_list": month_list} 
    
#            return {'year_interval': [year_list[0], year_list[-1]]}#, "month_list": month_list} 
        
    
    #==========================================================================
    def dict_select_year_interval(self, **kwargs): 
        """
        Created     20180720    by Magnus Wenzer 
        Updated     20180919    by Magnus 
        
        """ 
        from_year = self.mapping_objects['sharkweb_settings'].get('from_year')
        if not from_year: 
            from_year = 1990
        to_year = self.mapping_objects['sharkweb_settings'].get('to_year')
        if not to_year: 
            to_year = datetime.datetime.now().year
        
        choices = [int(item) for item in kwargs.get('year_choices', list(range(from_year, to_year+1)))] # Cant be int64 for json to work
        
        response = {'key': 'year_interval', 
                    'label': 'Year interval', 
                    'choices': choices, 
                    'widget': 'interval:int', 
                    'value': [self.mapping_objects['sharkweb_settings'].get('default_from_year'), 
                              self.mapping_objects['sharkweb_settings'].get('default_to_year')]}
        
        return response
    
    
    #==========================================================================
    def dict_select_datatype(self, **kwargs): 
        """
        Created     20180721   by Magnus Wenzer 
        
        """ 
#        choices = sorted(self.mapping_objects['datatype_list'].get_list('codelist_name'))
        choices = [item for item in self.sharkweb_reader.get_available_datatypes() if item in self.mapping_objects['sharkweb_settings'].get('datatypes')]
        
        response = {'key': 'datatypes', 
                    'label': 'Datatypes', 
                    'choices': choices, 
                    'widget': 'multiselect:str', 
                    'value': []}
        
        return response
    
    
    #==========================================================================
    def dict_select_area(self, **kwargs):
        """
        Created     20180824   by Magnus Wenzer 
        
        """ 
        return_dict = {'key': 'areas', 
                       'label': 'Areas', 
                       'widget': 'selection_tree', 
                       'value': []}
        
        
        
        water_body_mapping = self.mapping_objects['water_body'] 
        
        
        sharkweb_water_district_list = self.sharkweb_reader.get_available_water_district()
        sharkweb_type_area_list = self.sharkweb_reader.get_available_type_area()
        sharkweb_water_body_list = ['SE'+item for item in self.sharkweb_reader.get_available_water_body()] # without SE
        
#        self.sharkweb_water_district_list = sharkweb_water_district_list
#        self.sharkweb_type_area_list = sharkweb_type_area_list
#        self.sharkweb_water_body_list = sharkweb_water_body_list                    
        
                               
        mapping_water_district_code_list = water_body_mapping.get_list('water_district')
        mapping_water_district_name_list = [water_body_mapping.get_display_name(water_district=water_district) for water_district in mapping_water_district_code_list]
#        self.mapping_water_district_name_list = mapping_water_district_name_list
        
        # method intersection get only matching items from the two lists
        
        water_district_list = []
        #----------------------------------------------------------------------
        for water_district in set(sharkweb_water_district_list).intersection(mapping_water_district_name_list): 
#            print('water_district: {}'.format(water_district))
            water_district_code = water_body_mapping.get_internal_name(water_district=water_district)
#            print('water_district: {} - {}'.format(water_district_code, water_district))
            
            mapping_type_area_code_list = water_body_mapping.get_list('type_area', water_district=water_district_code)
            # Create type_area format matching sharkweb 
            mapping_type_area_name_list_sharkweb = [self.mapping_objects['sharkweb_mapping'].get_mapping(item, 'internal', 'sharkweb') \
                                                    for item in mapping_type_area_code_list]
            
            

            
            #------------------------------------------------------------------
            type_area_list = []
#            print(mapping_type_area_name_list_sharkweb)
#            self.mapping_type_area_name_list_sharkweb = mapping_type_area_name_list_sharkweb 
#            self.sharkweb_type_area_list = set(sharkweb_type_area_list)
            for type_area in set(sharkweb_type_area_list).intersection(mapping_type_area_name_list_sharkweb): 
                type_area_code = self.mapping_objects['sharkweb_mapping'].get_mapping(type_area, 'sharkweb', 'internal')
#                print('\ttype_area: {}'.format(type_area)) 
#                self.type_area = type_area
                mapping_water_body = water_body_mapping.get_list('water_body', type_area=type_area_code) 
#                self.mapping_water_body = mapping_water_body
                #--------------------------------------------------------------
                water_body_list = []
                for water_body in set(sharkweb_water_body_list).intersection(mapping_water_body): 
#                    print('\twater_body: {}'.format(water_body))
                    label = '{} - {}'.format(water_body, water_body_mapping.get_display_name(water_body=water_body))
                    water_body_dict = {"label": label,
                                       "key": water_body,
                                       "type": "water_body",
                                       "status": "editable", 
                                       "url": water_body_mapping.get_url(water_body), 
                                       "active": False}
                    
                    water_body_list.append(water_body_dict)
                #--------------------------------------------------------------
#                key = water_body_mapping.get_internal_name(type_area=type_area_code)
                type_area_dict = {"label": type_area,
                                  "key": type_area_code,
                                  "type": "type_area",
                                  "status": "editable", 
                                  "active": False, 
                                  "children": water_body_list[:]} 
                
                type_area_list.append(type_area_dict)
                
            #------------------------------------------------------------------ 
            water_district_dict = {"label": water_district,
                                   "key": water_body_mapping.get_internal_name(water_district=water_district),
                                   "type": "water_district",
                                   "status": "editable", 
                                   "active": False, 
                                   "children": type_area_list[:]}
            
            water_district_list.append(water_district_dict)
#            return water_district_list
        return_dict['children'] = water_district_list
        return return_dict
        
        
    #==========================================================================
    def dict_indicator_settings(self, 
                              workspace_uuid=None, 
                              subset_uuid=None, 
                              indicator=None, 
                              type_area=None, 
                              viss_eu_cd=None, 
                              request={}): 
        """
        Created     20180321   by Magnus Wenzer
        Updated     20180615   by Magnus Wenzer
        
        Contains indicator settings for a specific type_area oc viss_eu_cd. 
        """
        
        
        workspace_object = self.get_workspace(workspace_uuid) 
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_uuid))
            return {}
        
#        if indicator == 'din_winter':
#            print('='*50)
#            print(workspace_uuid)
#            print(subset_uuid)
#            print(indicator)
#            print(type_area)
#            print('='*50)
#            df

        return_dict = {}
        if type_area:
            return_dict['area_type'] = 'type_area'
            return_dict['key'] = type_area 
            return_dict['label'] = self.mapping_objects['water_body'].get_display_name(type_area=type_area)
        elif viss_eu_cd:
            return_dict['area_type'] = 'viss_eu_cd'
            return_dict['key'] = viss_eu_cd 
            return_dict['label'] = self.mapping_objects['water_body'].get_display_name(water_body=viss_eu_cd) 
        
        return_dict['children'] = self.list_indicator_settings_items(workspace_uuid=workspace_uuid, 
                                                                      subset_uuid=subset_uuid, 
                                                                      indicator=indicator, 
                                                                      type_area=type_area, 
                                                                      viss_eu_cd=viss_eu_cd, 
                                                                      request=request.get('children', []))
        return return_dict


    #==========================================================================
    def list_indicator_settings_items(self, 
                              workspace_uuid=None, 
                              subset_uuid=None, 
                              indicator=None, 
                              type_area=None, 
                              viss_eu_cd=None, 
                              request={}, 
                              **kwargs): 
        """
        Created     20180615   by Magnus Wenzer
        Updated     20180716   by Magnus Wenzer
        
        Returns a list of all the items in the settings file. 
        """
        response = [] 
        
        # Load filter objects 
        settings_data_filter_object = self.get_settings_filter_object(workspace_uuid=workspace_uuid, 
                                                                           subset_uuid=subset_uuid,
                                                                           indicator=indicator, 
                                                                           filter_type='data')
        if not settings_data_filter_object:
            self._logger.debug('Could not load data filter object for indicator "{}"'.format(indicator))
            return {}
        
        
        settings_tolerance_filter_object = self.get_settings_filter_object(workspace_uuid=workspace_uuid, 
                                                                           subset_uuid=subset_uuid,
                                                                           indicator=indicator,
                                                                           filter_type='tolerance') 
        
        item_mapping = self._get_mapping_for_name_in_dict('key', request) 
        if type_area == '2' and indicator=='din_winter':
            self.item_mapping = item_mapping
            self.request = request
            
        # Loop and add filters 
        for settings_item in self.mapping_objects['indicator_settings_items_to_show_in_gui']:
#            print('settings_item'.upper(), settings_item, item_mapping.get(settings_item))
            
            # data_filter
            if settings_item in settings_data_filter_object.allowed_variables: 
#                if settings_item in self.mapping_objects['indicator_settings_items_to_show_in_gui']:
                settings_item_dict = self.dict_indicator_settings_item(settings_filter_object=settings_data_filter_object, 
                                                                       settings_item=settings_item, 
                                                                       type_area=type_area, 
                                                                       viss_eu_cd=viss_eu_cd,
                                                                       request=item_mapping.get(settings_item, {}))
                if settings_item_dict:
                    response.append(settings_item_dict)
             
                
            # tolerance_filters 
            elif settings_item in settings_tolerance_filter_object.allowed_variables: 
#                if settings_item in self.mapping_objects['indicator_settings_items_to_show_in_gui']:
                settings_item_dict = self.dict_indicator_settings_item(settings_filter_object=settings_tolerance_filter_object, 
                                                                       settings_item=settings_item, 
                                                                       type_area=type_area, 
                                                                       viss_eu_cd=viss_eu_cd,
                                                                       request=item_mapping.get(settings_item, {}))
                if settings_item_dict:
                    response.append(settings_item_dict)
                    
        return response
            
        
    #==========================================================================
    def dict_indicator_settings_item(self, 
                                     settings_filter_object=None, 
                                     settings_item=None, 
                                     type_area=None, 
                                     viss_eu_cd=None,
                                     request={}): 
        """
        Created     20180615   by Magnus Wenzer
        Updated     20180918   by Magnus Wenzer 
        
        Information for a specifick settings "item" in indicator_settings_filter object 
        While the 'key' key is the indicator settings name, "children" is the actual settings value. 
        """
        
        if not all([settings_filter_object, settings_item]): 
            return {}
#        if type_area == '2':
##            print('request'.upper(), request)
#            self.request_item = request
        
        settings_item_dict = {}
        settings_item_dict['choices'] = False

        if request and request['status'] == 'editable': 
#            if not request['status'] == 'editable':
#                return request
            
            value = request['value'] 
            
            # Convert MONTHDAY from list to string:
            if 'MONTHDAY' in settings_item:
                value = [''.join(map(lambda x: str(x).rjust(2, '0'), value[0])), 
                         ''.join(map(lambda x: str(x).rjust(2, '0'), value[-1]))]
                
#                print('&'*50)
#                print('&'*50)
#                print(value, type(value), settings_item)
            if 'LIST' in settings_item: 
                value = get_list_from_interval(value) 
            
            # Check order of month list 
            # TODO: Check months per season
#            if settings_item == 'MONTH_LIST': 
#                if value[0] > value[1]:
#                    print(value)
#                    raise exceptions.InvalidUserInput('month in wrong order', code='month_interval_invalid')
             
                
                
            # 
            # No tuples come from json. Convert first 
#            if 'MONTHDAY' in settings_item:
#                print('#'*50)
#                print('#'*50)
#                print(value, type(value), settings_item)
            if type(value) == list:
                if type(value[0]) == list:
                    value = [tuple(val) for val in value]
                else:
                    value = tuple(value)
                
            settings_filter_object.set_value(type_area=type_area, 
                                              variable=settings_item, 
                                              value=value, 
                                              viss_eu_cd=viss_eu_cd)
#            print('IFIFIFIFIFIFIFI')
            return request
        
        else: 
            # Create settings_item_dict
            settings_item_dict['key'] = settings_item
            
            unit = settings_item_dict["unit"] = self.mapping_objects['display_mapping'].get_mapping(settings_item, 'internal', 'unit')
            settings_item_dict["label"] = '{} ({})'.format(self.mapping_objects['display_mapping'].get_mapping(settings_item, 'internal', 'label'), unit)
            
            # Check status 
            if settings_item in self.mapping_objects['indicator_settings_items_editable_in_gui']:
                settings_item_dict['status'] = 'editable'
            else:
                settings_item_dict['status'] = 'readable'
            
            
            value = settings_filter_object.get_value(type_area=type_area, 
                                                     variable=settings_item, 
                                                     water_body=viss_eu_cd, 
                                                     return_series=False)
            
            # Check type of widget 
            multi = ''
            what = ''
            typ = ''
            if type(value) == list and len(value) > 1: 
                multi = 'multi'  
                
            if 'INTERVAL' in settings_item: 
                what = 'interval'   
            elif 'LIST' in settings_item: 
                what = 'interval'   
            elif type(value) == int:
                what = 'number'   
            
            if 'MONTHDAY' in settings_item:
                typ = 'monthday'
            elif type(value) == int or type(value[0]) == int:
                typ = 'int' 
   
            settings_item_dict['widget'] = '{}{}:{}'.format(multi, what, typ)
            
                                                     
            if settings_item == 'MONTHDAY_INTERVAL': 
#                print(type(value), value)
                value = [list(map(int, [value[0][:2], value[0][2:]])), 
                         list(map(int, [value[-1][:2], value[-1][2:]]))]
                
            elif 'INTERVAL' in settings_item:
                # Not allowed to edit if several intervals
                if type(value[0]) == list: 
                    settings_item_dict['status'] = 'readable'
                                  
            elif 'LIST' in settings_item:
                value = get_interval_from_list(value) 
                
            # Check choices 
            if settings_item == 'MONTH_LIST': 
                settings_item_dict['choices'] = list(range(1,13))
            elif 'MIN_NR' in settings_item: 
                settings_item_dict['choices'] = [1, 2, 3]
            
                     
            # Set value
#            print('value:', value)
            settings_item_dict['value'] = value            
                              
        return settings_item_dict


    #==========================================================================
    def dict_quality_element(self, 
                             workspace_uuid=None, 
                             subset_uuid=None, 
                             quality_element=None, 
                             request={}, 
                             **kwargs): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180608    by Magnus Wenzer
        
        dict like: 
            {
					"label": "Phytoplankton", 
					"children": []
				}
            
            
        Update 20180608 by MW: kwargs contains what to include. Currently options are: 
            inidcator_settings 

        Usage: 
            if kwargs.get('<include>'):
                "INCLUDE"
        """
        workspace_object = self.get_workspace(workspace_uuid) 
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_uuid))
            return {"label": '',
    					"children": []}
        
#        request_dict = None
#        if request: 
#            for req in request:
#                if req['label'] == quality_element:
#                    request_dict = req['children']
#                    break
        return_dict = {'label': quality_element, 
                       "children": self.list_indicators(workspace_uuid=workspace_uuid, 
                                                        subset_uuid=subset_uuid, 
                                                        quality_element=quality_element, 
                                                        request=request.get('children', []), 
                                                        **kwargs)} 
                       
#        request_dict = None
#        if request: 
#            for req in request:
#                if req['label'] == quality_element:
#                      request_dict = req['children']
#                      break
#        return_dict = {'label': quality_element, 
#                       "children": self.list_indicators(workspace_uuid=workspace_uuid, 
#                                                        subset_uuid=subset_uuid, 
#                                                        quality_element=quality_element, 
#                                                        request=request_dict, 
#                                                        include_indicator_settings=include_indicator_settings)} 
        
        return return_dict
        
        
    #==========================================================================
    def dict_subset(self, workspace_uuid=None, subset_uuid=None, request={}, **kwargs):  
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180917    by Magnus Wenzer
        
        Update 20180608 by MW: kwargs contains what to include. Currently options are: 
            inidcator_settings 
            quality_elements 
            supporting_elements 
        
        Update 20180824 by MW: 
            Handle request. The request is not a full dict_subset but only lists of selection from data filter. 
        Request is handle for: 
            area 
            time
        
        Usage: 
            if kwargs.get('<include>'):
                "INCLUDE"
        """
        workspace_object = self.get_workspace(workspace_uuid) 
        uuid_mapping = workspace_object.uuid_mapping
        
        
        subset_dict = {}
#        subset_dict = {'alias': None,
#                        'subset_uuid': None,
#                        'status': None,
#                        'value': None,
#                        'time': {}, 
#                        'areas': [], 
##                        'periods': [], # Should be removed
##                        'water_bodies': [], 
##                        'water_districts': [], 
#                        'supporting_elements': [], 
#                        'quality_elements': []}
        
#        print(request.keys()) 
#        print(request['subset_uuid'])
        if not subset_uuid: 
            subset_uuid = request.get('subset_uuid')
        if not subset_uuid: 
            subset_uuid = request.get('subset', {}).get('subset_uuid')
        
        self.request = request 
        subset_dict['alias'] = uuid_mapping.get_alias(subset_uuid, status=self.all_status) 
        subset_dict['subset_uuid'] = subset_uuid
        subset_dict['status'] = uuid_mapping.get_status(unique_id=subset_uuid) 
        subset_dict['value'] = uuid_mapping.is_active(unique_id=subset_uuid)
            
        # Check request 
        if request.get('value', False):
            if request['value']:
                workspace_object.uuid_mapping.set_active(subset_uuid)
            else:
                workspace_object.uuid_mapping.set_inactive(subset_uuid)
        
        
        # Time
        if kwargs.get('time'):                
            subset_dict['time'] = self.dict_time(workspace_uuid=workspace_uuid, 
                                                       subset_uuid=subset_uuid, 
                                                       request=request.get('time', {}), 
                                                       **kwargs)
        
        # Deprecated list for periods
#        subset_dict['periods'] = self.list_periods(workspace_uuid=workspace_uuid, 
#                                                   subset_uuid=subset_uuid, 
#                                                   request=request.get('periods', {}))
        

        # Areas (contains water_district, type_area and water_body in a tree structure (or all in one list if request)) 
        # OBS! If request is given the value for key 'area' is a list containing all levels of areas
        if kwargs.get('areas'): 
            if 'areas' in request: 
                area_list = request.get('areas')
                if len(area_list) == 0:
                    raise exceptions.NoAreasSelected   
                    
            subset_dict['areas'] = self.list_areas(workspace_uuid=workspace_uuid, 
                                                            subset_uuid=subset_uuid, 
                                                            request=request.get('areas', []), 
                                                            **kwargs)
        
        # Quality elements 
        if kwargs.get('quality_elements'): 
            subset_dict['quality_elements'] = self.list_quality_elements(workspace_uuid=workspace_uuid, 
                                                                         subset_uuid=subset_uuid, 
                                                                         request=request.get('quality_elements', []), 
                                                                         **kwargs)
        
        # Supporting elements 
        if kwargs.get('supporting_elements'):
            subset_dict['supporting_elements'] = self.list_supporting_elements(workspace_uuid=workspace_uuid, 
                                                                               subset_uuid=subset_uuid, 
                                                                               request=request.get('supporting_elements', []), 
                                                                               **kwargs)


        # Result 
        if kwargs.get('result'): 
            subset_dict['result'] = self.dict_result(workspace_uuid=workspace_uuid, 
                                                     subset_uuid=subset_uuid, 
                                                     **kwargs)

        if kwargs.get('dont_build_subset'):
            return None
        return subset_dict
                                
    
    #==========================================================================
    def dict_water_body(self, workspace_uuid=None, subset_uuid=None, water_body=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180315    by Magnus Wenzer
        
        Internally its only possible to filter water bodies.  
        """
        workspace_object = self.get_workspace(workspace_uuid) 
#        print(subset_uuid)
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_uuid))
            return {"label": "",
                      'key': "",
                      "type": "",
                      "status": "", 
                      "url": "", 
                      "active": False}
        
        if request: 
            # Return request. information about selected is taken from one step up
            return request
        else:
            active = False 
            data_filter_object = subset_object.get_data_filter_object('step_1')
            wb_active_list = data_filter_object.get_include_list_filter('VISS_EU_CD')
            water_body_mapping = self.mapping_objects['water_body']
            if water_body in wb_active_list:
                active = True
                
            # Always selectable if no request
            return {"label": water_body_mapping.get_display_name(water_body=water_body),
                      'key': water_body,
                      "type": "water_body",
                      "status": "editable", 
                      "url": water_body_mapping.get_url(water_body), 
                      "active": active}
                          
        
    #==========================================================================
    def dict_type_area(self, workspace_uuid=None, subset_uuid=None, type_area=None, request=None, **kwargs): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180919    by Magnus Wenzer
        
        "editable" is not checked at the moment....
        """
        
        workspace_object = self.get_workspace(workspace_uuid) 
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_uuid))
            return {"label": "",
                      'key': "",
                      "type": "",
                      "status": "", 
                      "active": False, 
                      "children": []}
            
        if request: 
            return request # From 20180824 this is handled in a previous stage 
            # Add active water bodies to include filter. 
            # Set the data filter for water body here instead of adding one by one in dict_water_body 
            active_water_bodies = self._get_active_values_in_list_with_dicts(request['children'])
            if active_water_bodies:
                self.request = request
                self.active_water_bodies = active_water_bodies
            subset_object.set_data_filter(step='step_1', 
                                          filter_type='include_list', 
                                          filter_name='VISS_EU_CD', 
                                          data=active_water_bodies, 
                                          append_items=True)
            return request
        else:
            active = False 
            data_filter_object = subset_object.get_data_filter_object('step_1')
            water_body_active_list = data_filter_object.get_include_list_filter('VISS_EU_CD')
            water_body_mapping = self.mapping_objects['water_body']
            
            type_area_active_list = water_body_mapping.get_list('type_area', water_body=water_body_active_list)
            
            if type_area in type_area_active_list:
                active = True
                
            return_dict = {"label": water_body_mapping.get_display_name(type_area=type_area),
                          'key': type_area,
                          "type": "type_area",
                          "status": "editable", 
                          "active": active, 
                          "children": []}
            
            children_list = []
            
            # Check in data or not
            if type(kwargs.get('check_in_df', False)) != bool: 
                df = kwargs['check_in_df']
                water_body_list = sorted(list(set(df['VISS_EU_CD'])))
            elif kwargs.get('list_viss_eu_cd'):
                water_body_list = kwargs.get('list_viss_eu_cd')
            
            water_body_list = sorted(set(water_body_list).intersection(water_body_mapping.get_list('water_body', type_area=type_area)))
#            water_body_list = water_body_mapping.get_list('water_body', type_area=type_area)
            
            
            for water_body in water_body_list:
                children_list.append(self.dict_water_body(workspace_uuid=workspace_uuid, 
                                                          subset_uuid=subset_uuid, 
                                                          water_body=water_body, 
                                                          request=request)) 
                # request not active here...
            return_dict['children'] = children_list 
        
            return return_dict
        
        
    #==========================================================================
    def dict_water_district(self, workspace_uuid=None, subset_uuid=None, water_district=None, request={}, **kwargs): 
        """
        Created     20180315    by Magnus Wenzer
        Updated     20180917    by Magnus Wenzer
        
        Internally its only possible to filter water bodies.  
        "editable" needs to be checked against water district and type. 
        """
        workspace_object = self.get_workspace(workspace_uuid) 
#        print('subset_uuid', subset_uuid)
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        water_body_mapping = self.mapping_objects['water_body']
#        print('subset_uuid'.upper(), subset_uuid)
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_uuid))
            return {"label": "",
                      'key': "",
                      "type": "",
                      "status": "", 
                      "active": False, 
                      "children": []}
            
        if request: 
            for child in request['children']: 
                type_area = child['key'] 
                # Water district is not set as a internal data filter list. Only water body is saved. 
                self.dict_type_area(workspace_uuid=workspace_uuid, 
                                    subset_uuid=subset_uuid, 
                                    type_area=type_area, 
                                    request=child)
            return request
        else:
            
            active = False 
            data_filter_object = subset_object.get_data_filter_object('step_1')
            water_body_active_list = data_filter_object.get_include_list_filter('WATER_BODY')
            
#            print('****')
#            print(water_body_active_list)
            water_district_active_list = water_body_mapping.get_list('water_district', water_body=water_body_active_list)
#            print('### water_body_active_list', water_body_active_list)
#            print('=== water_district_active_list', water_district_active_list) 
#            print('--- water_district', water_district)
            if water_district in water_district_active_list:
                active = True
            # TODO: water district is not set tto active=true is sub-baisins are active. Is this ok?  
        
                
            label = water_body_mapping.get_display_name(water_district=water_district) 
            if not label:
                label = water_district
            return_dict = {"label": label,
                          'key': water_district,
                          "type": "water_district",
                          "status": "editable", 
                          "active": active, 
                          "children": []}
            
            children_list = []
            
            # Check in data or not
            if type(kwargs.get('check_in_df', False)) != bool: 
                df = kwargs['check_in_df']
                type_area_list = sorted(self.mapping_objects['water_body'].get_list('type_area', 
                                                                            water_body=list(set(df['VISS_EU_CD']))))
            elif kwargs.get('list_viss_eu_cd'):
                type_area_list = sorted(self.mapping_objects['water_body'].get_list('type_area', 
                                             water_body=kwargs.get('list_viss_eu_cd')))
            else:
                type_area_list = water_body_mapping.get_list('type_area', water_district=water_district)
            
            for type_area in type_area_list:
                children_list.append(self.dict_type_area(workspace_uuid=workspace_uuid, 
                                                          subset_uuid=subset_uuid, 
                                                          type_area=type_area, 
                                                          request=request, 
                                                          **kwargs)) 
                # request not active here...
            return_dict['children'] = children_list 
        
            return return_dict
                
    #==========================================================================
    def dict_workspace(self, workspace_uuid=None, **kwargs): 
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180720    by Magnus Wenzer
        
        """
        
        uuid_mapping = self._get_uuid_mapping_object() 
            
        alias = uuid_mapping.get_alias(workspace_uuid, status=self.all_status) 
        status = uuid_mapping.get_status(unique_id=workspace_uuid)
        
        workspace_dict = {'alias': alias, 
                          'workspace_uuid': workspace_uuid,
                          'status': status}
        
        if kwargs.get('check_data_availability'): 
            self.action_load_workspace(workspace_uuid)
#            self._check_valid_uuid(workspace_uuid)
#            self.load_workspace(workspace_uuid) 
            workspace_object = self.get_workspace(workspace_uuid)
            
            if workspace_object.data_is_available():
                workspace_dict.update({'data_is_available': True})
            else:
                workspace_dict.update({'data_is_available': False})
                
            
#        workspace_object = self.get_workspace(workspace_uuid)
        
        return workspace_dict
    
    
    #==========================================================================
    def _get_worse_status(self, *args): 
        status_list = ['BAD', 'POOR', 'MODERATE', 'GOOD', 'HIGH', ''] 
        return status_list[min([status_list.index(item) for item in args])]
    
    
    #==========================================================================
    def _get_all_viss_eu_cd_in_result_dict(self, result_dict):
        """
        Created     20180919    by Magnus Wenzer 
        
        Returns a list with all viss_eu_cd frond in the result dict. result_dict 
        is a dict with dataframes. 
        """ 
        viss_eu_cd_list = [] 
        for key in result_dict:
            viss_eu_cd_list.extend(list(result_dict[key]['VISS_EU_CD']))
        
        return sorted(set(viss_eu_cd_list))
        
        
    #==========================================================================
    def dict_result(self, workspace_uuid=None, subset_uuid=None, **kwargs): 
        """
        Created     20180720    by Magnus Wenzer
        Updated     20180919    by Magnus
        
        """ 
        self.action_load_workspace(workspace_uuid)
        workspace_object = self.get_workspace(workspace_uuid) 
        self._check_valid_uuid(workspace_uuid, subset_uuid)
        
        # Loading saved  
        step3_object = workspace_object.get_step_object(step=3, subset=subset_uuid)
        result_data = step3_object.get_results(by='period')
        
        # Get list of viss_eu_cd from data filter step 1 
        viss_eu_cd_list = self._get_all_viss_eu_cd_in_result_dict(result_data) 
        
#        step1 = workspace_object.get_step_object(step=1, subset=subset_uuid) 
#        data_filter_object = step1.get_data_filter_object()
#        viss_eu_cd_list = data_filter_object.get_include_list_filter('VISS_EU_CD') 
        
        result_dict = {} 
        # Setup combined dict 
        result_dict['all'] = {}
        result_dict['all']['value'] = 'all'
        result_dict['all']['label'] = 'all'
        result_dict['all']['result'] = {}
        
        # Loopar viss_eu_cd
        for viss_eu_cd in viss_eu_cd_list:
            result_dict[viss_eu_cd] = {}
            result_dict[viss_eu_cd]['value'] = viss_eu_cd 
            result_dict[viss_eu_cd]['label'] = '{} ({})'.format(self.mapping_objects['water_body'].get_display_name(water_body=viss_eu_cd), 
                                                         viss_eu_cd)
            result_dict[viss_eu_cd]['worse_status'] = ''
            result_dict[viss_eu_cd]['result'] = {} 
            
            for item, data in result_data.items(): 
                key = item.split('-')[0] 
                
                # Extend combined dict 
                if key not in result_dict['all']['result'].keys():
                    result_dict['all']['result'][key] = {} 
                    result_dict['all']['result'][key]['status'] = ''
                if 'active' not in result_dict['all']['result'][key].keys():
#                    print('---', result_dict['all']['result'][key].keys())
                    result_dict['all']['result'][key]['active'] = False
#                    print('===', result_dict['all']['result'][key]['active'])  
                    
                result_dict['all']['result'][key]['value'] = key
                result_dict['all']['result'][key]['label'] = self.mapping_objects['label_mapping'].get_mapping(key) 
                
                result_dict[viss_eu_cd]['result'][key] = self.dict_result_element(workspace_uuid=workspace_uuid, 
                                                                                  subset_uuid=subset_uuid, 
                                                                                  viss_eu_cd=viss_eu_cd, 
                                                                                  element_id=key, 
                                                                                  **kwargs)
                
                
#                result_dict[viss_eu_cd]['result'][key] = {} 
#                result_dict[viss_eu_cd]['result'][key]['status'] = '' 
#                result_dict[viss_eu_cd]['result'][key]['active'] = False
#                result_dict[viss_eu_cd]['result'][key]['value'] = key
#                result_dict[viss_eu_cd]['result'][key]['label'] = self.mapping_objects['label_mapping'].get_mapping(key)         
#                
#                
#                result_dict[viss_eu_cd]['result'][key]['data'] = [{'type': 'timeseries', 
#                                                                   'datasets': [{}]
#                                                                   }]
                
                
                
                
                if viss_eu_cd in data['VISS_EU_CD'].values: 
                    status_list = data.loc[data['VISS_EU_CD']==viss_eu_cd, 'STATUS'].values
                    if len(status_list) == 1:
                        status = status_list[0].strip()
                        result_dict[viss_eu_cd]['result'][key]['status'] = status 
#                        print()
#                        print('key:', key)
#                        print('viss_eu_cd', viss_eu_cd)
                        result_dict[viss_eu_cd]['worse_status'] = self._get_worse_status(status, result_dict[viss_eu_cd]['worse_status'])
                        result_dict[viss_eu_cd]['result'][key]['active'] = True 
                        result_dict['all']['result'][key]['active'] = True
#                print(result_dict['all']['result'][key]['active'])
                                   
            result_dict[viss_eu_cd]['label'] = result_dict[viss_eu_cd]['label'] + ' ({})'.format(result_dict[viss_eu_cd]['worse_status'])
       
    
        
#        if kwargs.get('status')
        
#        labels = {}
#        for key in step3_object.result_data.keys():
#            labels[key] = self.mapping_objects['display_mapping'].get_mapping(key, 'internal_name', 'display_en')
#            
#        
#        return_dict = {'dataframes': step3_object.result_data, 
#                       'labels': labels}
        
        return result_dict 
        
    
    #==========================================================================
    def dict_result_element(self, viss_eu_cd=None, element_id=None, **kwargs):
        """
        Created     20181918    by Magnus Wenzer
        
        """
        
        result_item_dict = {}
        result_item_dict['status'] = '' 
        result_item_dict['active'] = False # changed later i think 
        result_item_dict['value'] = element_id
        result_item_dict['label'] = self.mapping_objects['label_mapping'].get_mapping(element_id) 
        
        # kwargs must be workspace_uuid and subset_uuid
        result_item_dict['data'] = [] 
        result_item_dict['data'].append(self.dict_data_timeseries(viss_eu_cd=viss_eu_cd, 
                                                                       element_id=element_id, 
                                                                       **kwargs)) 
        return result_item_dict
    
        
    #==========================================================================
    def dict_data_timeseries(self, workspace_uuid=None, subset_uuid=None, 
                             viss_eu_cd=None, element_id=None, time_as_string=False, **kwargs):
        """
        Created     20181918    by Magnus Wenzer
        Updated     20180918    by Magnus
        """
        
#        self.action_load_workspace(workspace_uuid)
        workspace_object = self.get_workspace(workspace_uuid) 
#        self._check_valid_uuid(workspace_uuid, subset_uuid)
        
        # Loading saved  
        step3_object = workspace_object.get_step_object(step=3, subset=subset_uuid)
        result_data = step3_object.get_results(by='date', match_string=element_id) 
        # Should only return result for one key...
        key = element_id + '-by_date'
        
        df = result_data[key] 
        self.df = df
        
        # Extract the given viss_eu_cd 
        df = df.loc[df['VISS_EU_CD']==viss_eu_cd].copy()
#        print('KEY', key)
        # Find primary variable 
        primary_variable = self.mapping_objects['quality_element'].get_mapping(element_id, 'indicator', 'parameters').split(',')[0].strip()
        if primary_variable not in df.columns: 
            # Primary variable not found. No data to plot. 
#            print('primary_variable'.upper(), primary_variable)
            return {}
#        print('=== primary_variable'.upper(), primary_variable)
        # Find unit for xlabel
        unit = self.mapping_objects['display_mapping'].get_mapping(primary_variable, 
                                                                     'internal', 
                                                                     'unit', 
                                                                     return_blank_if_not_found=True)
        
        # List stations 
        station_list = sorted(set(df['STATN']))
        
        #----------------------------------------------------------------------
        # Create datasets 
        datasets = []
        
        # Stations
        for station in station_list: 
            statn_df = df.loc[df['STATN']==station].copy()
            y = list(statn_df[primary_variable]) 
            if time_as_string: 
                x = ['{}T'.format(sdate) for sdate in statn_df['SDATE']]
            else: 
                # Time as datetime objects 
                x = []
                for sdate in statn_df['SDATE']:
                    ymd = [int(item) for item in sdate.split('-')]
                    x.append(datetime.datetime(*ymd))
            
            dataset_dict = {'x': x, 
                            'y': y, 
                            'label': station.capitalize(), 
                            'type': 'scatter'}
            
            datasets.append(dataset_dict)
        
        
        # Status lines/fields
        
        # Add date column and sort by date 
        df['date'] = pd.to_datetime(df['SDATE'])
        df.sort_values('date', inplace=True)
        
        # First check order 
        direction = self.mapping_objects['quality_element'].get_mapping(element_id, 'indicator', 'direction_good')
        
        status_list = ['REFERENCE_VALUE', 'HG_VALUE_LIMIT', 'GM_VALUE_LIMIT', 'MP_VALUE_LIMIT', 'PB_VALUE_LIMIT']
        label_dict = dict(zip(status_list, ['high', 'good', 'moderate', 'poor', 'bad'])) 
        
        if direction == 'negative':
            # Lower value is better  
            for status in status_list:                 
                y = list(df[status]) 
                if time_as_string: 
                    x = ['{}T'.format(sdate) for sdate in df['SDATE']]
                else: 
                    # Time as datetime objects 
                    x = df['date']
                    
                status_dict = {'x': x, 
                               'y': y, 
                               'label': label_dict[status], 
                               'type': 'fill', 
                               'extend': ''} 
                if status == 'PB_VALUE_LIMIT':
                    status_dict['extend'] = 'max'
                
                datasets.append(status_dict)
            
        
        elif direction == 'positive':
            # Higher value is better 
            status_list.reverse() 
            for status in status_list:                 
                y = list(df[status]) 
                if time_as_string: 
                    x = ['{}T'.format(sdate) for sdate in df['SDATE']]
                else: 
                    # Time as datetime objects 
                    x = df['date']
                    
                status_dict = {'x': x, 
                               'y': y, 
                               'label': label_dict[status], 
                               'type': 'fill', 
                               'extend': ''} 
                if status == 'REFERENCE_VALUE':
                    status_dict['extend'] = 'max'
                
                datasets.append(status_dict)
            
        
        # Create dict to return 
        data_dict = {'type': 'timeseries', 
                     'xlabel': 'Date', 
                     'ylabel': unit, 
                     'datasets': datasets}
        
        return data_dict
        
    
    #==========================================================================
    def print_workspaces(self): 
        """
        Created     20180601    by Magnus Wenzer
        Updated     
        
        """
        nr_signs = 100
        uuid_ljust = 40
        alias_ljust = 30
        status_ljust = 30
        print('='*nr_signs)
        print('Current workspaces for user are:')
        print('')
        print('{}{}{}'.format('uuid'.ljust(uuid_ljust), 'alias'.ljust(alias_ljust), 'status'.ljust(status_ljust)))
        print('-'*nr_signs)
        uuid_mapping = self._get_uuid_mapping_object() 
        for u in self.get_workspaces_for_user(): 
            alias = uuid_mapping.get_alias(u)
            status = uuid_mapping.get_status(u)
#            print(u)
#            print(alias)
#            print(status)
            print('{}{}{}'.format(u.ljust(uuid_ljust), alias.ljust(alias_ljust), status.ljust(status_ljust)))
            
        
        print('='*nr_signs)
        
        
    
    #==========================================================================
    def get_alias_for_unique_id(self, workspace_uuid=None, subset_uuid=None): 
        if workspace_uuid and subset_uuid: 
            workspace_object = self.workspaces.get(workspace_uuid, None)
            if not workspace_object:
                return False
            return workspace_object.get_alias_for_unique_id(subset_uuid)
        elif workspace_uuid:
            uuid_mapping = self._get_uuid_mapping_object()
            return uuid_mapping.get_alias(workspace_uuid)
        
        
    #==========================================================================
    def get_unique_id_for_alias(self, workspace_alias=None, subset_alias=None, workspace_uuid=None):
        """
        Updated     20180720    by Magnus Wenzer
        
        """
        
        uuid_mapping = self._get_uuid_mapping_object()
        
        if workspace_alias:
            workspace_uuid = uuid_mapping.get_uuid(workspace_alias)
        
        if workspace_uuid and subset_alias: 
            workspace_object = self.workspaces.get(workspace_uuid, None) 
            workspace_object = self.get_workspace(workspace_uuid)
            if not workspace_object:
                return False 
            return workspace_object.get_unique_id_for_alias(subset_alias)
        elif workspace_alias:
            return workspace_uuid
        else:
            return False
           
            
    #==========================================================================
    def get_subset_list(self, workspace_uuid=None): 
        # Load workspace if not loaded
        if workspace_uuid not in self.workspaces.keys():
            all_ok = self.load_workspace(unique_id=workspace_uuid)
            if not all_ok:
                return []
        workspace_object = self.workspaces.get(workspace_uuid, None)
        return workspace_object.get_subset_list()
    
    
    #==========================================================================
    def get_workspace(self, workspace_uuid=None): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180721    by Magnus Wenzer
        
        """
        t0 = time.time()
        workspace_object = self.workspaces.get(workspace_uuid, None)
        if not workspace_object:
            self._check_valid_uuid(workspace_uuid)
        
#        # Get UUID for workspace
#        if workspace_uuid == 'default_workspace': 
#            pass
#        else:
#            uuid_mapping = self._get_uuid_mapping_object()
#            if not uuid_mapping.is_present(workspace_uuid):
#                raise exceptions.WorkspaceNotFound(workspace_uuid)
#
##            alias = uuid_mapping.get_alias(workspace_uuid)
##            # return matching workspace 
##            self._logger.debug('Getting workspace "{}" with alias "{}"'.format(workspace_uuid, alias)) 
#        workspace_object = self.workspaces.get(workspace_uuid, None) 
#        if not workspace_object:
#            raise exceptions.WorkspaceNotFound(workspace_uuid)
        self.time_get_workspace += (time.time()-t0)
        return workspace_object
    
    
    #==========================================================================
    def get_workspaces_for_user(self, status=[]):
        uuid_mapping = self._get_uuid_mapping_object() 
        return uuid_mapping.get_uuid_list_for_user(status=status)
    
    
    
    #==========================================================================
    def set_status_for_datasource(self, workspace_uuid=None, file_name=None, status=None): 
        """
        Created     20180601    by Magnus Wenzer
        Updated 
        
        """
        assert all([workspace_uuid, file_name, status])
        
        workspace_object = self.get_workspace(workspace_uuid) 
        if not workspace_object:
            return False
        
        datatype_settings_object = workspace_object.datatype_settings
        if not datatype_settings_object.has_info:
            return False
        
        return datatype_settings_object.set_status(file_name=file_name, status=status)
    
    
    #==========================================================================
    def import_sharkweb_data(self, 
                              workspace_uuid=None, 
                              **kwargs): 
        """
        Created     20180721    by Magnus Wenzer
        
        Loads data from sharkweb. 
        """
        print('===', workspace_uuid) 
        print(kwargs)
        self.action_load_workspace(workspace_uuid)
        reader = core.SharkWebReader(debug=True)
        data_params = reader.get_data_params()
        self.data_params = data_params
        
        invalid_keys = []
        for key in kwargs:
            if key in data_params:
                data_params[key] = kwargs[key]
            else:
                invalid_keys.append(key)
                
        if invalid_keys:
            exceptions.InvalidUserInput
          
#        data_params['datatype'] = 'Harbour Porpoise'
#        data_params['sample_table_view'] = 'sample_col_harbourporpoise'
#        
#        data_params['county_list'] = ['Blekinge län', 'Kalmar län'] 
#        try:            
        # Read data 
        reader.read_data(data_params=data_params) 
        self.data = reader.data
        # Find datatype
        datatype = reader.data.split('\n')[1].split('\t')[0] 
        if not datatype: 
            raise exceptions.UnableToLoadData('No data available') 
            
        internal_datatype_name = self.mapping_objects['datatype_list'].get_mapping(datatype, 'codelist_name', 'internal_name')
#        print('datatype', datatype)
#        print('internal_datatype_name', internal_datatype_name)
        # Save file 
        parameter = kwargs.get('parameter', 'all')
        if not parameter:
            parameter = 'all'
        full_file_name = '{}_sharkweb_data_{}_{}-{}_{}.txt'.format(internal_datatype_name, 
                                                                   parameter, 
                                                                   kwargs.get('year_from'), 
                                                                   kwargs.get('year_to'), 
                                                                   datetime.datetime.now().strftime('%Y%m%d%H%M'))
        file_path = os.path.join(self.temp_directory, full_file_name) 
        reader.save_data(file_path) 
        
        # Import file in workspace 
        workspace_object = self.get_workspace(workspace_uuid) 
        workspace_object.import_file(file_path=file_path, 
                                     data_type=internal_datatype_name, 
                                     status=0, 
                                     force=True)
        
        # Remove temp file 
#            os.remove(file_path)
        print('Done')
        return full_file_name
            
#        except:
#            exceptions.SharkwebLoadError
            
        
        
    #==========================================================================
    def import_default_data(self, workspace_alias=None, force=False):
        """
        Created     20180220    by Magnus Wenzer
        Updated     20180220    by Magnus Wenzer
        
        Loads default data to the workspace with alias workspace_alias. 
        """ 
        uuid_mapping = self._get_uuid_mapping_object()
        unique_id = uuid_mapping.get_uuid(workspace_alias)
        self._logger.debug('Trying to load default data in workspace "{}" with alias "{}"'.format(unique_id, workspace_alias))
        workspace_object = self.workspaces.get(unique_id, None)
        if not workspace_object:
            return False
        workspace_object.import_default_data(force=force)
        
        
    #==========================================================================
    def list_data_sources(self, 
                        workspace_uuid=None, 
                        request=[]): 
        """
        Created     20180524    by Magnus Wenzer
        Updated     
        
        request is a list of dicts. 
        """ 
#        print(workspace_uuid)
        workspace_object = self.get_workspace(workspace_uuid) 
        if not workspace_object:
            print('NOT workspace_object') 
            print(workspace_uuid)
            return []
        
        datatype_settings_object = workspace_object.datatype_settings
        if not datatype_settings_object.has_info:
            print('NOT datatype_settings_object.has_info')
            return [] 
        
        response = [] 
        for filename in datatype_settings_object.get_file_list():
            request_dict = {}
            
            for finfo in request:
                if finfo['filename'] == filename:
                    request_dict = finfo
                    break
            
            filename_dict = self.dict_data_source(workspace_uuid=workspace_uuid, 
                                                   file_name=filename, 
                                                   request=request_dict)
            # TODO: Compare request_dict and filename_dict
            response.append(filename_dict)
            
        return response
        
    
    #==========================================================================
    def list_indicators(self, 
                        workspace_uuid=None, 
                        subset_uuid=None, 
                        quality_element=None, 
                        request=[], 
                        **kwargs): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180608    by Magnus Wenzer
        
        request is a list of dicts. 
        
        Update 20180608 by MW: kwargs contains what to include. Currently options are: 
            inidcator_settings 

        Usage: 
            if kwargs.get('<include>'):
                "INCLUDE"
        """ 
        workspace_object = self.get_workspace(workspace_uuid) 
#        subset_object = workspace_object.get_subset_object(subset_uuid)
        
        indicator_list = self.mapping_objects['quality_element'].get_indicator_list_for_quality_element(quality_element)
        
        # Check available indicators. Check this onse (here) and send list to dict_indicators to avoid multiple calls 
        if subset_uuid == 'default_subset':
            available_indicators = []
        else:
            if not len(workspace_object.data_handler.all_data): # use len, all_data is a pandas dataframe
                workspace_object.load_all_data()
            available_indicators = workspace_object.get_available_indicators(subset=subset_uuid, step='step_1')
        
        return_list = []
        for indicator in indicator_list:
            request_dict = {}
            # Need to check which element in request list belong to the indicator 
            for ind in request:
                if ind['key'] == indicator:
                    request_dict = ind
                    break
            
            indicator_dict = self.dict_indicator(workspace_uuid=workspace_uuid, 
                                                 subset_uuid=subset_uuid, 
                                                 indicator=indicator, 
                                                 available_indicators=available_indicators, 
                                                 request=request_dict, 
                                                 **kwargs)
        
            return_list.append(indicator_dict)
        
        return return_list
        
    
    #==========================================================================
    def list_indicator_settings(self, 
                                workspace_uuid=None, 
                                subset_uuid=None, 
                                indicator=None, 
                                request=[], 
                                **kwargs): 
        """
        Created     20180321    by Magnus Wenzer
        Updated     20180824    by Magnus Wenzer
        
        request is a list of dicts. 
        """ 
        
        # Get list of areas that the filters can be applied on. 
        # This is a list with all water_bodies selected by the user 
        # New 20180824: 'selected_areas' in kwargs is a list of water bodies. 
        water_body_list = kwargs.get('selected_areas', [])
        type_area_list = self.mapping_objects['water_body'].get_list('type_area', water_body=water_body_list)
        
        selected_areas = {'type_area_list': type_area_list, 
                          'viss_eu_cd_list': water_body_list} 
            
#        selected_areas_list = selected_areas['type_area_list'] + selected_areas['viss_eu_cd_list']
        
        
        workspace_object = self.get_workspace(workspace_uuid) 
#        if indicator == 'din_winter':
#            print('¤'*50)
#            print(indicator) 
#            print(request)
#            print('¤'*50)
##            df
#        print('¤'*50)
#        print(indicator) 
#        print(request)
#        print('¤'*50)
        indicator_settings_object = workspace_object.get_indicator_settings_data_filter_object(subset=subset_uuid, 
                                                                                               step='step_2', 
                                                                                               indicator=indicator)
        if not indicator_settings_object:
            # No settings for indicator 
            return []
            
#        self.selected_areas_2 = selected_areas
#        self.selected_areas_list = selected_areas_list
        
        #----------------------------------------------------------------------
        # Check type_area
        if selected_areas['type_area_list']: 
            type_area_list = selected_areas['type_area_list'][:]
        else:
            type_area_list = set(indicator_settings_object.get_type_area_list())
        
        request_dict = self._get_mapping_for_name_in_dict('key', request)
        
        self.type_area_list = type_area_list
        
        return_list = []
        for type_area in type_area_list: 
#            if selected_areas_list and type_area not in selected_areas_list:
#                continue
#            request_dict = {}
            # Need to check which element in request list belong to the indicator 
#            for ty in request:
##                    print(ty)
#                if ty and ty['key'] == type_area: # ty can be empty dict if no settings for indicator
#                    request_dict = ty
#                    break
                    
            indicator_settings_dict = self.dict_indicator_settings(workspace_uuid=workspace_uuid, 
                                                                  subset_uuid=subset_uuid, 
                                                                  indicator=indicator, 
                                                                  type_area=type_area, 
                                                                  viss_eu_cd=False, 
                                                                  request=request_dict.get(type_area, {}))
            self.indicator_settings_dict = indicator_settings_dict
            return_list.append(indicator_settings_dict)
        
        
        #----------------------------------------------------------------------
        # Check water_body (VISS_EU_CD)
        if selected_areas['viss_eu_cd_list']: 
            # Updated 20180615 by MW: Only viss_eu_cd present in the settings files should be shown. 
            # water_body_list = [item for item in selected_areas['viss_eu_cd_list'] if item in indicator_settings_object.get_viss_eu_cd_list()]
            # Correction: This does not work if viss_eu_cd is added. the check needs to be done later 
            # and only applied on calls without request. UPDATED 20180620: Implemented below.
            water_body_list = selected_areas['viss_eu_cd_list'][:]
        else:
            water_body_list = set(indicator_settings_object.get_viss_eu_cd_list())
        
#        return_list = []
        for water_body in water_body_list:
            # If nor request then only water bodies in settings file chould be returned
            if not request and water_body not in indicator_settings_object.get_viss_eu_cd_list():
                continue
            
            
#            if selected_areas_list and water_body not in selected_areas_list:
#                continue
#            request_dict = {}
            # Need to check which element in request list belong to the indicator 
#            request_dict = self._get_mapping_for_name_in_dict('key', request)
#            for ty in request:
##                    print(ty)
#                if ty and ty['key'] == water_body: # ty can be empty dict if no settings for indicator
#                    request_dict = ty
#                    break
                    
            indicator_settings_dict = self.dict_indicator_settings(workspace_uuid=workspace_uuid, 
                                                                  subset_uuid=subset_uuid, 
                                                                  indicator=indicator, 
                                                                  type_area=False, 
                                                                  viss_eu_cd=water_body, 
                                                                  request=request_dict.get(water_body, {}))
            return_list.append(indicator_settings_dict)

        return return_list

        
    #==========================================================================
    def list_periods(self, workspace_uuid=None, subset_uuid=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        Temporary method to give static periods.
        """
        workspace_object = self.get_workspace(workspace_uuid) 
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        
        # Check request
        if request:
            for per in request:
                if per['value']:
#                    print('per', per)
                    from_year, to_year = map(int, per['key'].split('-'))
                    year_list = map(str, list(range(from_year, to_year+1)))
#                    print('subset_object.alias', subset_object.alias)
                    subset_object.set_data_filter(step='step_1', filter_type='include_list', filter_name='MYEAR', data=year_list)
                    break
#            print('request'.upper(), request)
            return request

        return [{"label": "2007-2012",
    				"status": "editable",
    				'value': False,
    				'key': "2007-2012"}, 
    
                {"label": "2013-2018",
    				"status": "editable",
    				'value': True,
    				'key': "2013-2018"}]
        
    
    #==========================================================================
    def list_quality_elements(self, 
                              workspace_uuid=None, 
                              subset_uuid=None, 
                              request=[], 
                              **kwargs): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180608    by Magnus Wenzer
        
        Update 20180608 by MW: kwargs contains what to include. Currently options are: 
            inidcator_settings 

        Usage: 
            if kwargs.get('<include>'):
                "INCLUDE"
        
        """ 
#        print('list_quality_elements', request)
#        workspace_object = self.get_workspace(workspace_uuid) 
#        subset_object = workspace_object.get_subset_object(subset_uuid)
        
        quality_element_list = self.mapping_objects['quality_element'].get_quality_element_list() 
        exclude = ['secchi', 'nutrients', 'oxygen']
        quality_element_list = [item for item in quality_element_list if item not in exclude]
        
        request_for_label = self._get_mapping_for_name_in_dict('label', request)
        
        
        return_list = []
        for quality_element in quality_element_list:
            sub_request = request_for_label.get(quality_element, {})
            quality_element_dict = self.dict_quality_element(workspace_uuid=workspace_uuid, 
                                                             subset_uuid=subset_uuid, 
                                                             quality_element=quality_element, 
                                                             request=sub_request, 
                                                             **kwargs)
        
            return_list.append(quality_element_dict)
        
        return return_list
    
    
    #==========================================================================
    def list_subsets(self, workspace_uuid=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180317    by Magnus Wenzer 
        
        request is a list of subsets
        """
#        print('list_subsets_request', request)
        subset_list = []
#        subset_uuid_list = [] 
#        sub_request_list = []
        request_for_subset_uuid = self._get_mapping_for_name_in_dict('subset_uuid', request) 
#                subset_uuid_list.append(sub['uuid'])
#                sub_request_list.append(sub)
#        else: 
#            subset_uuid_list = self.get_subset_list(workspace_uuid=workspace_uuid, user_id=user_id)
#            sub_request_list = [None]*len(subset_uuid_list)
            
#        for subset_uuid, sub_request in zip(subset_uuid_list, sub_request_list): 
#        print('=====SUBSET_UUID=====')
#        print(workspace_uuid)
#        print(user_id)
#        print(self.workspaces)
#        print('=====================')
        for subset_uuid in self.get_subset_list(workspace_uuid=workspace_uuid):
#            print('=====SUBSET_UUID', '"{}"'.format(subset_uuid))
            sub_request = request_for_subset_uuid.get(subset_uuid, {})
            
            # Check uuid for subset in request (if given) 
#            if request:
#                for sub in request:
#    #                    print(sub)
#                    if sub['uuid'] == subset_uuid:
#                        break
        
            # Get subset dict
            subset_dict = self.dict_subset(workspace_uuid=workspace_uuid, 
                                           subset_uuid=subset_uuid, 
                                           request=sub_request)
            
            
            # Add subset dict to subset list
            subset_list.append(subset_dict)
               
        return subset_list
    
    
    #==========================================================================
    def list_supporting_elements(self, 
                                 workspace_uuid=None, 
                                 subset_uuid=None, 
                                 request=[], 
                                 **kwargs): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180608    by Magnus Wenzer
        
        Update 20180608 by MW: kwargs contains what to include. Currently options are: 
            inidcator_settings 

        Usage: 
            if kwargs.get('<include>'):
                "INCLUDE"
        
        """ 
#        print('list_supporting_elements', request)
#        workspace_object = self.get_workspace(workspace_uuid) 
#        subset_object = workspace_object.get_subset_object(subset_uuid)
        
        quality_element_list = ['secchi', 'nutrients', 'oxygen']
        
        request_for_label = self._get_mapping_for_name_in_dict('label', request)
        
#        print('request', request)
        return_list = []
        for quality_element in quality_element_list: 
            
            sub_request = request_for_label.get(quality_element, {})
#            # Check request 
#            qe_dict = None
#            if request:
#                for qe in request:
#                    if qe['key'] == quality_element:
#                        qe_dict = qe
#                        break
                    
            quality_element_dict = self.dict_quality_element(workspace_uuid=workspace_uuid, 
                                                             subset_uuid=subset_uuid, 
                                                             quality_element=quality_element, 
                                                             request=sub_request, 
                                                             **kwargs)
        
            return_list.append(quality_element_dict)
        
        return return_list
    
    
    #==========================================================================
    def list_workspaces(self): 
        """
        Created     20180317    by Magnus Wenzer
        Updated     20180317    by Magnus Wenzer 
        
        Only looks in uuid_mapping file. Does not require workspaces to be loaded. 
        """
        workspace_list = []
        uuid_mapping = self._get_uuid_mapping_object()
        for unique_id in uuid_mapping.get_uuid_list_for_user(status=self.all_status):
            workspace_list.append(self.dict_workspace(workspace_uuid=unique_id))
        
#        if include_default:
#            workspace_list.append(self.dict_workspace(unique_id='default_workspace')) 
        
        return workspace_list
        
        
    
    #==========================================================================
    def list_areas(self, workspace_uuid=None, subset_uuid=None, request=None, **kwargs): 
        """
        Created     20180315    by Magnus Wenzer
        Updated     20180917    by Magnus Wenzer
        
        Lists information for "areas". Areas are hierarchically structured like: 
            [
                {
                  "label": "SE5",
                  'key': "SE5",
                  "type": "district",
                  "status": "editable",
                  "active": true,
                  "children": [
                        {
                          "label": "1s - Västkustens inre kustvatten, södra",
                          'key': "1s",
                          "type": "type_area",
                          "status": "editable",
                          "active": true,
                          "children": [
                                {
                                  "label": "Balgöarkipelagen",
                                  'key': "SE570900-121060",
                                  "type": "water_body",
                                  "status": "readable",
                                  "active": false
                                }
                              ]
                          }
                      ]
                  }
               ]
        """
        # Try to load subset if not loaded 
        
         
#        if not subset_object:
#            self.load_su
        
#        print('request'.upper(), request.keys())
#        if 'water_district' not in request
        area_list = [] 
        
        if request:
            # OBS! If request is given it is a list containing all levels of areas. 
            # create a list of the water bodies from this list 
            water_body_list = self._get_water_bodies_from_area_list(request)
            
            workspace_object = self.get_workspace(workspace_uuid)
            subset_object = workspace_object.get_subset_object(subset_uuid)
            subset_object.set_data_filter(step='step_1', 
                                          filter_type='include_list', 
                                          filter_name='VISS_EU_CD', 
                                          data=water_body_list, 
                                          append_items=False) 
            
        if kwargs.get('dont_build_subset'):
            return {}
#        request_for_water_district = self._get_mapping_for_name_in_dict('key', request)
        
        if type(kwargs.get('check_in_df', False)) != bool: 
            df = kwargs['check_in_df']
            water_district_list = sorted(self.mapping_objects['water_body'].get_list('water_district', 
                                         water_body=list(set(df['VISS_EU_CD']))))
        elif kwargs.get('list_viss_eu_cd'):
            water_district_list = sorted(self.mapping_objects['water_body'].get_list('water_district', 
                                         water_body=kwargs.get('list_viss_eu_cd')))
        else:
            water_district_list = self.mapping_objects['water_body'].get_list('water_district')

        for water_district in water_district_list:
#            sub_request = request_for_water_district.get(water_district, None) 
        
            response = self.dict_water_district(workspace_uuid=workspace_uuid, 
                                                subset_uuid=subset_uuid, 
                                                water_district=water_district, 
                                                request={}, 
                                                **kwargs)
            area_list.append(response)
        
        return area_list
        
    
    #==========================================================================
    def _check_active_in_area_tree(self, area_list): 
        """
        Created     20180919    by Magnus Wenzer
        
        Check area list tree and sets active True or False. Rules are: 
            If all children are all True: Parent=True, all children=False 
            If some but not all children=True: parent=False 
        """
        
        for water_district in area_list: 
            #------------------------------------------------------------------
            type_area_active_list = []
            for type_area in water_district['children']: 
                #--------------------------------------------------------------
                water_body_active_list = []
                for water_body in type_area['children']: 
                    # Check if water body is active
                    water_body_active_list.append(water_body['active']) 
                    
                # Check if all water bodies are active 
                if all(water_body_active_list):
                    # Activate type_area 
                    type_area['active'] = True
                    # Set all water bodies to False 
#                    for water_body in type_area['children']: 
#                        water_body['active'] = False
                else:
                    type_area['active'] = False
                    print('TYPE AREA', type_area['key'])
                    
                #--------------------------------------------------------------
                # Check if type_area is active
                type_area_active_list.append(type_area['active'])
            
            # Check if all type areas are active 
            if all(type_area_active_list):
                # Activate type_area 
                water_district['active'] = True
                # Set all water bodies to False 
#                for type_area in water_district['children']: 
#                    type_area['active'] = False
            else:
                water_district['active'] = False
                
            #------------------------------------------------------------------
        
        
        
    #==========================================================================
    def _get_water_bodies_from_area_list(self, area_list): 
        """
        Created     20180824    by Magnus Wenzer
        Updated     20180913    by Magnus Wenzer
        
        Extracts water bodies from list of water districts, type areas and water bodies. 
        """
        
        water_district_list = self.mapping_objects['water_body'].get_list('water_district') 
        type_area_list = self.mapping_objects['water_body'].get_list('type_area') 
        water_body_list = self.mapping_objects['water_body'].get_list('water_body') 
        
        water_bodies = set()
        invalid_areas= []
        for area in area_list: 
            if area in water_district_list:
                water_bodies.update(self.mapping_objects['water_body'].get_list('water_body', water_district=area))
            elif area in type_area_list:
                water_bodies.update(self.mapping_objects['water_body'].get_list('water_body', type_area=area))
            elif area in water_body_list:
                water_bodies.add(area)
            else:
                invalid_areas.append(area)
            
#        print('invalid_areas', invalid_areas)
        if len(invalid_areas): 
            raise exceptions.InvalidArea(';'.join(invalid_areas))
        
        return list(water_bodies)
    

    #==========================================================================
    def list_water_bodies(self, workspace_uuid=None, subset_uuid=None, type_area=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180315    by Magnus Wenzer
        
        Lists information for water bodies.
        """
        if not all([workspace_uuid, subset_uuid, type_area]):
            return []
        
        # Check request 
        if request:
            workspace_object = self.get_workspace(workspace_uuid) 
            # Create list of type areas 
            water_body_list = [req['key'] for req in request if req['value']]
            # Set data filter 
            workspace_object.set_data_filter(step='step_1', subset=subset_uuid, filter_type='include_list', filter_name='WATER_BODY', data=water_body_list)
            
            return request
        else:
            
            return_list = []
            for water_body in self.mapping_objects['water_body'].get_list('water_body', type_area=type_area): 
                
                water_body_dict = self.dict_water_body(workspace_uuid=workspace_uuid, 
                                                       subset_uuid=subset_uuid, 
                                                       water_body=water_body, 
                                                       request=request)
                return_list.append(water_body_dict)
        
            return return_list
    
    
    #==========================================================================
    def list_water_district(self, workspace_uuid=None, subset_uuid=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        NOT DYNAMIC YET. NEEDS TO BE MAPPED! 
        
        Lists information for water district. 
        """
        # TODO: kanske kan behandlas som periods for nu?
        return_list = [{
        					"label": "Bottenhavet",
        					"status": "editable",
        					'value': True,
        					'key': "Bottenhavet"
        				},
        				{
        					"label": "Skagerakk", 
        					"status": "editable",
        					'value': False,
        					'key': "Skagerakk"
        				}] 
        
        return return_list
    
#        for water_body in self.mapping_objects['water_body'].get_water_body_list():
#            water_body_dict = self.dict_water_body(workspace_uuid=workspace_uuid, 
#                                                   subset_uuid=subset_uuid, 
#                                                   water_body=water_body)
#            return_list.append(water_body_dict)
#    
#        return return_list
    
    
    #==========================================================================
    def load_all_workspaces_for_user(self, with_status=None):
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180530    by Magnus Wenzer
        
        Loads all workspaces for the given user. Including default workspace.  
        """
        self._logger.debug('Trying to load all workspaces for user "{}"'.format(self.user_id))
        status = self.include_status[:]
        if with_status:
            if type(with_status) != list:
                with_status = [with_status]
            status = with_status
        uuid_mapping = self._get_uuid_mapping_object()
#        workspace_list = ['default_workspace'] + uuid_mapping.get_uuid_list_for_user(user_id, status=status) # Now one default_workspace for each user 
        workspace_list = uuid_mapping.get_uuid_list_for_user(status=status) 
        for unique_id in workspace_list: 
            self.load_workspace(unique_id=unique_id)
        
        
    #==========================================================================
    def load_data(self, workspace_uuid=None, force=False): 
        
        workspace_object = self.get_workspace(workspace_uuid)
        if not workspace_object:
            return False 
        
        workspace_object.load_all_data(force=force)
        return True
        
    #==========================================================================
    def load_test_requests(self): 
        self.test_requests = {} 
        directory = '{}/requests'.format(self.test_data_directory)
        for file_name in os.listdir(directory):
            if 'response' in file_name:
                continue
            file_path = os.path.join(directory, file_name)
            with codecs.open(file_path, 'r', encoding='cp1252') as fid: 
#                print(file_path)
                self.test_requests[file_name[:-4]] = json.load(fid)
        
        
    #==========================================================================
    def write_test_response(self, name, response): 
        if 0:
            file_path = '{}/requests/{}.txt'.format(self.test_data_directory, name)
            self.response = response
            with codecs.open(file_path, 'w', encoding='cp1252') as fid:
                json.dump(response, fid, indent=4) 
        else:
            if name.startswith('request_'):
                name = name[8:]
            file_path = '{}/requests/response_{}.txt'.format(self.test_data_directory, name)
            self.response = response
            with codecs.open(file_path, 'w', encoding='cp1252') as fid:
                json.dump(response, fid, indent=4)        
        
        
    #==========================================================================
    def update_workspace_uuid_in_test_requests(self, workspace_uuid, filename=None): 
        """
        Created     20180524    by Magnus Wenzer
        Updated     
        
        Changes workspace uuid in all test requests. 
        This is used for easy work in notebook.  
        """ 
        if len(workspace_uuid) != 36: 
            print('Not a valid uuid!')
            return
        directory = '{}/requests'.format(self.test_data_directory)
        for file_name in os.listdir(directory):
            if 'response' in file_name:
                continue 
            
            if filename and file_name != filename:
                continue
            
            file_path = os.path.join(directory, file_name)
            
            if 1:
                new_lines = []
                with codecs.open(file_path) as fid: 
                    for line in fid:
                        new_line = re.sub('"workspace_uuid": ".{36}"', '"workspace_uuid": "{}"'.format(workspace_uuid), line)
                        new_lines.append(new_line)
                
                with codecs.open(file_path, 'w') as fid:
                    fid.write(''.join(new_lines))
                
            else:
                with codecs.open(file_path, 'r', encoding='cp1252') as fid: 
    #                print(file_path)
                    j = json.load(fid) 
                    
                if 'workspace_uuid' in j.keys(): 
                    print('Updating workspace_uuid in file: {}'.format(file_name))
                    if j['workspace_uuid'] != 'default_workspace':
                        j['workspace_uuid'] = workspace_uuid
                        
                elif 'workspace' in j.keys():
                    if 'workspace_uuid' in j['workspace'].keys():
                        if j['workspace']['workspace_uuid'] != 'default_workspace':
                            j['workspace']['workspace_uuid'] = workspace_uuid
                elif 'subsets' in j.keys(): 
                    for sub in j['subsets']:
                        if 'workspace_uuid' in sub.keys():
                            if sub['workspace_uuid'] != 'default_workspace':
                                sub['workspace_uuid'] = workspace_uuid
                        
                with codecs.open(file_path, 'w', encoding='cp1252') as fid:
                    json.dump(j, fid, indent=4) 
                
        self.load_test_requests()
        
        
    #==========================================================================
    def update_subset_uuid_in_test_requests(self, subset_uuid=None, filename=None): 
        """
        Created     20180524    by Magnus Wenzer
        Updated     
        
        Changes workspace uuid in all test requests. 
        This is used for easy work in notebook.  
        """ 
        if len(subset_uuid) != 36: 
            print('Not a valid uuid!')
            return
        directory = '{}/requests'.format(self.test_data_directory)
        for file_name in os.listdir(directory):
            if 'response' in file_name:
                continue 
            
            if filename and file_name != filename:
                continue
            
            file_path = os.path.join(directory, file_name)
            
            if 1:
                new_lines = []
                with codecs.open(file_path) as fid: 
                    for line in fid:
                        new_line = re.sub('"subset_uuid": ".{36}"', '"subset_uuid": "{}"'.format(subset_uuid), line)
                        new_lines.append(new_line)
                
                with codecs.open(file_path, 'w') as fid:
                    fid.write(''.join(new_lines))
                
            else:
                with codecs.open(file_path, 'r', encoding='cp1252') as fid: 
    #                print(file_path)
                    j = json.load(fid) 
                if 'subset_uuid' in j.keys(): 
                    print('Updating workspace_uuid in file: {}'.format(file_name))
                    if j['subset_uuid'] != 'default_workspace':
                        j['subset_uuid'] = subset_uuid
                        
                elif 'subset' in j.keys():
                    if 'subset_uuid' in j['subset'].keys():
                        if j['subset']['subset_uuid'] != 'default_workspace':
                            j['subset']['subset_uuid'] = subset_uuid
                elif 'subsets' in j.keys(): 
                    for sub in j['subsets']:
                        if 'workspace_uuid' in sub.keys():
                            if sub['workspace_uuid'] != 'default_workspace':
                                sub['workspace_uuid'] = subset_uuid
                        
                with codecs.open(file_path, 'w', encoding='cp1252') as fid:
                    json.dump(j, fid, indent=4) 
                
        self.load_test_requests()
        
        
    #==========================================================================
    def load_workspace(self, unique_id=None, reload=False): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180605    by Magnus Wenzer
        
        Loads the given workspace. Subsets in workspace are also loaded. 
        By default workspace will not be reloaded if it already exsist. 
        """
        uuid_mapping = self._get_uuid_mapping_object()
        alias = uuid_mapping.get_alias(unique_id=unique_id)
        
#        print('¤¤¤ alias', alias)
#        print('¤¤¤ unique_id', unique_id) 
#        print('¤¤¤ user_id', user_id)

        if not all([alias, unique_id]):
            self._logger.warning('Could not load workspace "{}" with alias "{}"'.format(unique_id, alias))
            return False
        
        # Only load if workspace 
        if unique_id not in self.workspaces or reload:
            if unique_id not in self.workspaces:
                self._logger.debug('Trying to load new workspace "{}" with alias "{}"'.format(unique_id, alias))
            elif reload:
                self._logger.debug('Trying to reload workspace "{}" with alias "{}"'.format(unique_id, alias))
                
            self.workspaces[unique_id] = core.WorkSpace(alias=alias, 
                                                        unique_id=unique_id, 
                                                        parent_directory=self.workspace_directory,
                                                        resource_directory=self.resource_directory, 
                                                        mapping_objects=self.mapping_objects, 
                                                        user_id=self.user_id)
        else:
            self._logger.debug('Workspace "{}" with alias "{}" is already loaded. Set reload=True if you want to reload the workspace.'.format(unique_id, alias))
            return True
        
        if not self.workspaces[unique_id]:
            self._logger.warning('Could not load workspace "{}" with alias "{}"'.format(unique_id, alias))
            return False
        else:
            self._logger.info('Workspace "{}" with alias "{} loaded."'.format(unique_id, alias))
            return True            
           
            
    #==========================================================================
    def action_apply_data_filter(self, workspace_uuid=None, subset_uuid=None, step=None):
        """
        Created     20180608    by Magnus Wenzer
        Updated     
        
        Applies the data filter at step for the given workspace and subset. 
        If all previous steps are applied if necessary
        """ 
        self.action_load_workspace(workspace_uuid=workspace_uuid) 
        workspace_object = self.get_workspace(workspace_uuid) 
        workspace_object.apply_data_filter(step=step, subset=subset_uuid)
        
        
    #==========================================================================
    def action_apply_indicator_settings_data_filter(self, workspace_uuid=None, subset_uuid=None, step='step_2'):
        """
        Created     20180718    by Magnus Wenzer
        Updated     
        
        Applies the settings data filter at step for the given workspace and subset. 
        Filter is applied for all available indicators from step 1. 
        """ 
        self.action_load_workspace(workspace_uuid=workspace_uuid) 
        workspace_object = self.get_workspace(workspace_uuid) 
        for indicator in workspace_object.get_available_indicators(subset=subset_uuid, step=1): 
            workspace_object.apply_indicator_data_filter(subset=subset_uuid, indicator=indicator, step=step)
        
        
    #==========================================================================
    def action_calculate_status(self, workspace_uuid=None, subset_uuid=None, indicator_list=None, water_body_list=None):
        """
        Created     20180913    by Magnus Wenzer 
        Updated     20180917    by Magnus Wenzer
        
        Calculates status for the given subset. 
        """
        self.action_load_workspace(workspace_uuid=workspace_uuid) # Loaded in action_apply_data_filter

        # Apply data filters 
        self.action_apply_data_filter(workspace_uuid=workspace_uuid, 
                                      subset_uuid=subset_uuid, 
                                      step=1) 
        
        self.action_apply_indicator_settings_data_filter(workspace_uuid=workspace_uuid, 
                                                         subset_uuid=subset_uuid, 
                                                         step=2)
        
        
        workspace_object = self.get_workspace(workspace_uuid) 
        
        step_object_calculate = workspace_object.get_step_object(subset=subset_uuid, step=3) 
        
        # Setup indicators 
        step_object_calculate.indicator_setup(indicator_list=indicator_list)
        # Calculate status 
        step_object_calculate.calculate_status(indicator_list=indicator_list, 
                                               water_body_list=water_body_list) 
        
        # Calculate quaity elements  
        # TODO: Hur väljer vi quality elements
        quality_elements = ['Nutrients', 'Phytoplankton']
        for qe in quality_elements:
            step_object_calculate.calculate_quality_element(quality_element=qe)
        
        
    #==========================================================================
    def action_reset_data_filter(self, workspace_uuid=None, subset_uuid=None, step=1): 
        """
        Created     20180608    by Magnus Wenzer
        Updated     
        
        Resets all data filters for the given subset. 
        This is typically called before executing a request that sets the data filter. 
        """
        self.action_load_workspace(workspace_uuid=workspace_uuid)
        workspace_object = self.get_workspace(workspace_uuid) 
        workspace_object.reset_data_filter(subset_uuid=subset_uuid, step=step, include_filters=True, exclude_filters=True)
        
        
    #==========================================================================
    def action_load_workspace(self, workspace_uuid=None, force=False): 
        """
        Created     20180530    by Magnus Wenzer
        Updated     20180605    by Magnus 
        
        Action to load workspace. 
        """
        self._check_valid_uuid(workspace_uuid)
        all_ok = self.load_workspace(unique_id=workspace_uuid, reload=force)
        if not all_ok: 
            self._logger.warning('Could not load workspace with uuid: {}'.format(workspace_uuid))
            raise exceptions.UnableToLoadWorkspace
        return all_ok
    
    
    #==========================================================================
    def action_load_data(self, workspace_uuid, force=False): 
        """
        Created     20180605    by Magnus Wenzer
        Updated     
        
        Action to load data in the given workspace. 
        """
        
        all_ok = self.action_load_workspace(workspace_uuid)
        if not all_ok:
            return all_ok
        workspace_object = self.get_workspace(workspace_uuid) 
        if workspace_object:
            data_loaded = workspace_object.load_all_data(force=force) 
            if not data_loaded:
                raise exceptions.UnableToLoadData
            
            return True
        else:
            self._logger.warning('Could not load data for workspace: {}'.format(workspace_uuid))
            return False
        
        
    #==========================================================================
    def action_workspace_load_default_data(self, workspace_uuid=None, force=True): 
        """
        Created     20180525    by Magnus Wenzer
        Updated     
        
        Action to load default data. force is True by default. 
        Actions are: 
            load the given workspace 
            imports default data 
            load data
        """
        
        all_ok = self.action_load_workspace(workspace_uuid=workspace_uuid)
        if not all_ok:
            return all_ok
        
        workspace_object = self.get_workspace(workspace_uuid) 
        all_ok = workspace_object.import_default_data(force=force)
        
        if all_ok:
            workspace_object.load_all_data(force=force)
        return all_ok
      
        
    #==========================================================================
    @timer 
    def request_sharkweb_import(self, request):
        """
        Created     20180827    by Magnus Wenzer 
        Updated     20180919    by Magnus 
        """ 
        workspace_uuid = request.get('workspace_uuid') 
        year_interval = request.get('year_interval')
        from_year = year_interval[0]
        to_year = year_interval[1]
        datatype_list = request.get('datatypes') 
        area_list = request.get('areas')
        
        # Check area and devide into "area level" 
        water_district_list = [] 
        type_area_list = [] 
        water_body_list = [] 
        
        water_districts = self.mapping_objects['water_body'].get_list('water_district')
        type_areas = self.mapping_objects['water_body'].get_list('type_area')
        water_bodies = self.mapping_objects['water_body'].get_list('water_body')
        
#        self.water_districts = water_districts
#        self.type_areas = type_areas
#        self.water_bodies = water_bodies
        for area in area_list: 
            if area in water_districts:
                sharkweb_name = self.mapping_objects['water_body'].get_mapping(area, 'WATER_DISTRICT_CODE', 'WATER_DISTRICT_NAME')
                water_district_list.append(sharkweb_name)
            elif area in type_areas:
                sharkweb_name = self.mapping_objects['sharkweb_mapping'].get_mapping(area, 'internal', 'sharkweb')
                type_area_list.append(sharkweb_name)
            elif area in water_bodies:
                sharkweb_name = self.mapping_objects['water_body'].get_mapping(area, 'VISS_EU_CD', 'WATERBODY_NAME')
                water_body_list.append(sharkweb_name)
        
        self.selection_dicts = {}
        for datatype in datatype_list: 
            selection_dict = {'year_from': from_year, 
                              'year_to': to_year, 
                              'datatype': datatype, 
                              self.mapping_objects['sharkweb_mapping'].get_mapping('WATER_DISTRICT', 'internal', 'sharkweb'): water_district_list, 
                              self.mapping_objects['sharkweb_mapping'].get_mapping('WATER_TYPE_AREA', 'internal', 'sharkweb'): type_area_list, 
                              self.mapping_objects['sharkweb_mapping'].get_mapping('VISS_EU_CD', 'internal', 'sharkweb'): water_body_list, 
                              'encoding': 'utf8',  
#                              'encoding': "Windows-1252", 
                              'lineend': 'windows', 
                              'delimiters': 'point-tab', 
                              'sample_table_view': self.mapping_objects['sharkweb_settings'].get('{}_sample_table_view'.format(datatype)), 
                              'parameter': self.mapping_objects['sharkweb_settings'].get('{}_parameter'.format(datatype)), 
                              'headerlang': self.mapping_objects['sharkweb_settings'].get('headerlang')} 
            
#            self.selection_dict = selection_dict
#            return {} 
            self.selection_dicts[datatype] = selection_dict
#            return {}
            file_name = self.import_sharkweb_data(workspace_uuid=workspace_uuid, 
                                                  **selection_dict)
        
        return {'file_name': file_name}
#            self.import_sharkweb_data
            #TODO: Här är request enklare listor mm.
            #self.load_data_from_sharkweb(request)
    #==========================================================================
    @timer 
    def request_sharkweb_search(self, *arg, **kwargs):
        """
        Created     20180827    by Magnus Wenzer
        """ 
        pkl_file_path = os.path.join(self.resource_directory, 'pkl/request_sharkweb_search.pkl')
        if kwargs.get('force_update') or not os.path.exists(pkl_file_path): 
            # Create sharkweb reader 
            self.sharkweb_reader = core.SharkWebReader()
            response = {}
            response['options'] = [] 
            response['options'].append(self.dict_select_year_interval())
            response['options'].append(self.dict_select_datatype())
            response['options'].append(self.dict_select_area())
            # Save as pickle 
            with open(pkl_file_path, "wb") as fid:
                pickle.dump(response, fid) 
        else:
            with open(pkl_file_path, "rb") as fid: 
                response = pickle.load(fid)
        return response
        
        
        
    #==========================================================================
    @timer 
    def request_subset_add(self, request):
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180319    by Magnus Wenzer
        
        "request" must contain: 
            "workspace_uuid": "335af11c-a7d4-4edf-bc21-d90ffb762c70", 
            "subset_uuid": "default_subset",
            "alias": "mw1"
        
        Returns a dict_subset            
        """ 
        
        self._logger.debug('Start: request_subset_add')
        workspace_uuid = request['workspace_uuid']
        subset_uuid = request['subset_uuid']
        new_alias = request['alias']
        
        # Load workspace 
        self.action_load_workspace(workspace_uuid) 
        
        
        return_dict = self.copy_subset(workspace_uuid=workspace_uuid, 
                                       subset_source_uuid=subset_uuid, 
                                       subset_target_alias=new_alias)
        self.temp_return_dict = return_dict
        if return_dict:
            subset_uuid = return_dict['subset_uuid']
        else:
            uuid_mapping = self._get_uuid_mapping_object()
#            print(new_alias, user_id)
            subset_uuid = uuid_mapping.get_uuid(alias=new_alias)
        response = self.dict_subset(workspace_uuid=workspace_uuid, 
                                   subset_uuid=subset_uuid)
        
        return response
    
    #==========================================================================
    @timer
    def request_subset_calculate_status(self, request):
        """
        Created     20180913    by Magnus Wenzer
        Updated     
        
        "request" must contain: 
            workspace_uuid
            subset_uuid 
            indicators
            areas (any level)
        
        Calculates status for the given indicators and area.
            
        """
        self._logger.debug('Start: request_subset_calculate_status')
        
        workspace_uuid = request['workspace_uuid']
        subset_uuid = request['subset_uuid']
        
        # Load workspace 
        self.action_load_data(workspace_uuid) 
        
        self._check_valid_uuid(workspace_uuid, subset_uuid)
        
        workspace_object = self.get_workspace(workspace_uuid)  
        
        if not workspace_object.data_is_loaded():
            raise exceptions.NoDataSelected 
            
        # Extract water bodies from "areas" 
        water_body_list = None
#        water_body_list = self._get_water_bodies_from_area_list(request['areas']) 
        
        self.action_calculate_status(workspace_uuid=workspace_uuid, 
                                     subset_uuid=subset_uuid, 
                                     indicator_list=request.get('indicators', None), 
                                     water_body_list=water_body_list)
            
        return {'all_ok': True, 
                'message': ''}
    
    
    #==========================================================================
    @timer 
    def request_subset_set_data_filter(self, request):
        """
        Created     20180919    by Magnus Wenzer
        
        
        "request" must contain: 
            workspace_uuid
            subset_uuid 
            areas 
            year_interval
                
        Response: 
            - Only indicators that has data are active (only those need information). 
        
            
        """
        #TODO: Här är request enklare listor mm.
        self._logger.debug('Start: request_subset_get_indicator_settings')
        
        workspace_uuid = request.get('workspace_uuid')
        subset_uuid = request.get('subset_uuid')
         
        if not subset_uuid:
            subset_uuid = request.get('subset', {}).get('subset_uuid')
        
#        workspace_uuid = request.get('workspace_uuid', {}) 
#        if not workspace_uuid:
#            workspace_uuid = request['workspace']['workspace_uuid'] 
#        subset_uuid = request['subset']['subset_uuid']
        
        
        # Load workspace 
#        self.action_load_workspace(workspace_uuid) 
        
        # Load data 
        self.action_load_data(workspace_uuid) # workspace is loaded in action 
        
        self._check_valid_uuid(workspace_uuid, subset_uuid)
        
        # Reset all data filters in step 1. 
        # This has to be done as water bodies are appended to current filter when looping throughtype areas. 
        # So if data filters are removed from last request it won't automaticly be removed in the data filter files. 
        
        # Dont think we need to reset filter anymore. MW 20180824
        if 0:
            self.action_reset_data_filter(workspace_uuid=workspace_uuid, 
                                          subset_uuid=subset_uuid, 
                                          step=1)
        
        response = {} 
        
        # Add workspace info to response 
        response['workspace_uuid'] = workspace_uuid
        response['workspace'] = self.dict_workspace(workspace_uuid)
        
        # Added by Magnus 20180914 
        request['subset'] = {} 
        request['subset']['value'] = True
        request['subset']['subset_uuid'] = subset_uuid
        request['subset']['areas'] = request.get('areas') 
        request['subset']['time'] = {'year_interval': request.get('year_interval')}
        self.request_ = request
        # Set data filter and add subset information to response
        response['subset'] = self.dict_subset(workspace_uuid=workspace_uuid, 
                                              subset_uuid=subset_uuid, 
                                              request=request['subset'], 
                                              time=True, 
                                              areas=True, 
                                              list_viss_eu_cd=request.get('areas', []), 
                                              dont_build_subset=True) 
        
        return request 
    
#        # Check selected areas 
#        workspace_object = self.get_workspace(workspace_uuid) 
#        subset_object = workspace_object.get_subset_object(subset_uuid) 
#        data_filter_object = subset_object.get_data_filter_object(step=1)
#        selected_areas = data_filter_object.get_include_list_filter('VISS_EU_CD')
##        selected_areas = self._get_selected_areas_from_subset_request(request['subset'])
##        self.selected_areas = selected_areas
#        
#        
        # Apply data filter 
#        self.action_apply_data_filter(workspace_uuid=workspace_uuid, 
#                                      subset_uuid=subset_uuid, 
#                                      step=1) 
#        
#        
#        # Quality elements 
#        response['quality_elements'] = self.list_quality_elements(workspace_uuid=workspace_uuid, 
#                                                                  subset_uuid=subset_uuid, 
#                                                                  request=[], 
#                                                                  indicator_settings=True, 
#                                                                  selected_areas=selected_areas)
#        
#        # Supporting elements 
#        response['supporting_elements'] = self.list_supporting_elements(workspace_uuid=workspace_uuid, 
#                                                                        subset_uuid=subset_uuid, 
#                                                                        request=[], 
#                                                                        indicator_settings=True, 
#                                                                        selected_areas=selected_areas) 
#        
#        
#               
#        return response
        
        
    
    
    #==========================================================================
    @timer
    def request_subset_get_data_filter(self, request):
        """
        Created     20180608    by Magnus Wenzer
        Updated     20180720    by Magnus Wenzer
        
        "request" must contain: 
            workspace_uuid
            subset_uuid
        
        Returns information about current time range and list of areas.
            
        """
        self._logger.debug('Start: request_subset_get_data_filter')
        
        workspace_uuid = request['workspace_uuid']
        subset_uuid = request['subset_uuid']
        
#        self._check_valid_uuid(workspace_uuid)
        # Load workspace 
        self.action_load_data(workspace_uuid) 
        
        self._check_valid_uuid(workspace_uuid, subset_uuid)
        
        workspace_object = self.get_workspace(workspace_uuid)  
        
        if not workspace_object.data_is_loaded():
            raise exceptions.NoDataSelected
        
        df0 = workspace_object.get_filtered_data(step=0) 
#        year_choices = sorted(set(df0['MYEAR']))
#        water_distric_list = sorted(ekos.mapping_objects['water_body'].get_list('water_district', 
#                                                                        water_body=list(set(df0['VISS_EU_CD']))))
  
        response = {}
        response['workspace_uuid'] = workspace_uuid
        response['workspace'] = self.dict_workspace(workspace_uuid) 
        
#        print('===', subset_uuid)
        response['subset'] = self.dict_subset(workspace_uuid=workspace_uuid, 
                                              subset_uuid=subset_uuid, 
                                              time=True, 
                                              areas=True, 
                                              indicator_settings=False, 
                                              quality_elements=False, 
                                              supporting_elements=False, 
#                                              year_choices=year_choices, 
                                              check_in_df=df0)
       
        # Fick active=True/False in areas tree 
        self._check_active_in_area_tree(response['subset']['areas'])
        
#        print('='*50)
#        self.workspace_uuid = workspace_uuid
#        self.subset_uuid = subset_uuid 
#        self.response = response
        return response
    
    #==========================================================================
    @timer 
    def request_subset_get_indicator_settings(self, request):
        """
        Created     20180608    by Magnus Wenzer
        Updated     20180919    by Magnus Wenzer
        
        "request" must contain: 
            workspace_uuid
            subset_uuid 
                
        Response: 
            - Only indicators that has data are active (only those need information). 
        
            
        """
        #TODO: Här är request enklare listor mm.
        self._logger.debug('Start: request_subset_get_indicator_settings')
        
        workspace_uuid = request.get('workspace_uuid')
        subset_uuid = request.get('subset_uuid')
         
        if not subset_uuid:
            subset_uuid = request.get('subset', {}).get('subset_uuid')
        
#        workspace_uuid = request.get('workspace_uuid', {}) 
#        if not workspace_uuid:
#            workspace_uuid = request['workspace']['workspace_uuid'] 
#        subset_uuid = request['subset']['subset_uuid']
        
        
        # Load workspace 
#        self.action_load_workspace(workspace_uuid) 
        
        # Load data 
        self.action_load_data(workspace_uuid) # workspace is loaded in action 
        
        workspace_object = self.get_workspace(workspace_uuid)  
        
        if not workspace_object.data_is_loaded():
            raise exceptions.NoDataSelected
            
        self._check_valid_uuid(workspace_uuid, subset_uuid)
        
        df0 = workspace_object.get_filtered_data(step=0)
        # Reset all data filters in step 1. 
        # This has to be done as water bodies are appended to current filter when looping throughtype areas. 
        # So if data filters are removed from last request it won't automaticly be removed in the data filter files. 
        
        # Dont think we need to reset filter anymore. MW 20180824
        if 0:
            self.action_reset_data_filter(workspace_uuid=workspace_uuid, 
                                          subset_uuid=subset_uuid, 
                                          step=1)
        
        response = {} 
        
        # Add workspace info to response 
        response['workspace_uuid'] = workspace_uuid
        response['workspace'] = self.dict_workspace(workspace_uuid)
        
        # Set data filter and add subset information to response
        response['subset'] = self.dict_subset(workspace_uuid=workspace_uuid, 
                                              subset_uuid=subset_uuid, 
                                              request={}, 
                                              time=True, 
                                              areas=True, 
                                              list_viss_eu_cd=request.get('areas', []), 
                                              check_in_df=df0) 
        
        # Check selected areas 
        workspace_object = self.get_workspace(workspace_uuid) 
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        data_filter_object = subset_object.get_data_filter_object(step=1)
        selected_areas = data_filter_object.get_include_list_filter('VISS_EU_CD')
#        selected_areas = self._get_selected_areas_from_subset_request(request['subset'])
#        self.selected_areas = selected_areas
        
        
        # Apply data filter 
        self.action_apply_data_filter(workspace_uuid=workspace_uuid, 
                                      subset_uuid=subset_uuid, 
                                      step=1) 
        
        
        # Quality elements 
        response['quality_elements'] = self.list_quality_elements(workspace_uuid=workspace_uuid, 
                                                                  subset_uuid=subset_uuid, 
                                                                  request=[], 
                                                                  indicator_settings=True, 
                                                                  selected_areas=selected_areas)
        
        # Supporting elements 
        response['supporting_elements'] = self.list_supporting_elements(workspace_uuid=workspace_uuid, 
                                                                        subset_uuid=subset_uuid, 
                                                                        request=[], 
                                                                        indicator_settings=True, 
                                                                        selected_areas=selected_areas) 
        
        
               
        return response
        
#        self.workspace_uuid = workspace_uuid
#        self.subset_uuid = subset_uuid 
#        self.response = response
    
    #==========================================================================
    @timer 
    def old_request_subset_get_indicator_settings(self, request):
        """
        Created     20180608    by Magnus Wenzer
        Updated     20180824    by Magnus Wenzer
        
        "request" must contain: 
            workspace_uuid
            subset_uuid 
                
        Response: 
            - Only indicators that has data are active (only those need information). 
        
            
        """
        #TODO: Här är request enklare listor mm.
        self._logger.debug('Start: request_subset_get_indicator_settings')
        
        workspace_uuid = request.get('workspace_uuid')
        subset_uuid = request.get('subset_uuid')
         
        if not subset_uuid:
            subset_uuid = request.get('subset', {}).get('subset_uuid')
        
#        workspace_uuid = request.get('workspace_uuid', {}) 
#        if not workspace_uuid:
#            workspace_uuid = request['workspace']['workspace_uuid'] 
#        subset_uuid = request['subset']['subset_uuid']
        
        
        # Load workspace 
#        self.action_load_workspace(workspace_uuid) 
        
        # Load data 
        self.action_load_data(workspace_uuid) # workspace is loaded in action 
        
        self._check_valid_uuid(workspace_uuid, subset_uuid)
        
        # Reset all data filters in step 1. 
        # This has to be done as water bodies are appended to current filter when looping throughtype areas. 
        # So if data filters are removed from last request it won't automaticly be removed in the data filter files. 
        
        # Dont think we need to reset filter anymore. MW 20180824
        if 0:
            self.action_reset_data_filter(workspace_uuid=workspace_uuid, 
                                          subset_uuid=subset_uuid, 
                                          step=1)
        
        response = {} 
        
        # Add workspace info to response 
        response['workspace_uuid'] = workspace_uuid
        response['workspace'] = self.dict_workspace(workspace_uuid)
        
        # Added by Magnus 20180914 
        request['subset'] = {} 
        request['subset']['value'] = True
        request['subset']['subset_uuid'] = subset_uuid
        request['subset']['areas'] = request.get('areas') 
        request['subset']['time'] = {'year_interval': request.get('year_interval')}
        self.request_ = request
        # Set data filter and add subset information to response
        response['subset'] = self.dict_subset(workspace_uuid=workspace_uuid, 
                                              subset_uuid=subset_uuid, 
                                              request=request['subset'], 
                                              time=True, 
                                              areas=True, 
                                              list_viss_eu_cd=request.get('areas', [])) 
        
        # Check selected areas 
        workspace_object = self.get_workspace(workspace_uuid) 
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        data_filter_object = subset_object.get_data_filter_object(step=1)
        selected_areas = data_filter_object.get_include_list_filter('VISS_EU_CD')
#        selected_areas = self._get_selected_areas_from_subset_request(request['subset'])
#        self.selected_areas = selected_areas
        
        
        # Apply data filter 
        self.action_apply_data_filter(workspace_uuid=workspace_uuid, 
                                      subset_uuid=subset_uuid, 
                                      step=1) 
        
        
        # Quality elements 
        response['quality_elements'] = self.list_quality_elements(workspace_uuid=workspace_uuid, 
                                                                  subset_uuid=subset_uuid, 
                                                                  request=[], 
                                                                  indicator_settings=True, 
                                                                  selected_areas=selected_areas)
        
        # Supporting elements 
        response['supporting_elements'] = self.list_supporting_elements(workspace_uuid=workspace_uuid, 
                                                                        subset_uuid=subset_uuid, 
                                                                        request=[], 
                                                                        indicator_settings=True, 
                                                                        selected_areas=selected_areas) 
        
        
               
        return response
    
    
    #==========================================================================
    @timer
    def request_subset_set_indicator_settings(self, request):
        """
        Created     20180611    by Magnus Wenzer
        Updated     
        
        "request" is a response from "request_subset_get_indicator_settings" 
                
        Response:         
            
        """
        self._logger.debug('Start: request_subset_set_indicator_settings')
        
        workspace_uuid = request.get('workspace_uuid', {}) 
        if not workspace_uuid:
            workspace_uuid = request['workspace']['workspace_uuid'] 
        subset_uuid = request['subset']['subset_uuid']
        
        
        # Load workspace 
#        self.action_load_workspace(workspace_uuid) 
        
        # Load data 
        self.action_load_data(workspace_uuid) # workspace is loaded in action
        
        self._check_valid_uuid(workspace_uuid, subset_uuid)
                             
        # Reset all data filters in step 1. 
        # This has to be done as water bodies are appended to current filter when looping throughtype areas. 
        # So if data filters are removed from last request it wont automaticly be removed in the data filter files. 
#        self.action_reset_data_filter(workspace_uuid=workspace_uuid, 
#                                      subset_uuid=subset_uuid)
        
        response = {} 
        response['workspace_uuid'] = workspace_uuid 
        response['subset_uuid'] = subset_uuid
        
        # Set data filter 
#        response['subset'] = self.dict_subset(workspace_uuid=workspace_uuid, 
#                                     subset_uuid=subset_uuid, 
#                                     request=request['subset'], 
#                                     time=True, 
#                                     areas=True) 
        
        # Check selected areas. Updated by MW 20180913. Could be better 
        areas = request.get('subset', {}).get('areas')
        self.areas = areas
#        return response
        if type(areas) == list and len(areas) and type(areas[0]) == str:
            print('areas[0]:', areas[0])
            viss_eu_cd_list = self._get_water_bodies_from_area_list(areas)
        elif type(areas):
            selected_areas = self._get_selected_areas_from_subset_request(request['subset']) 
            viss_eu_cd_list = selected_areas['viss_eu_cd_list'] 
        else:
            viss_eu_cd_list = None
        
        
        
        
        # Quality elements 
        response['quality_elements'] = self.list_quality_elements(workspace_uuid=workspace_uuid, 
                                                                  subset_uuid=subset_uuid, 
                                                                  request=request['quality_elements'], 
                                                                  indicator_settings=True, 
                                                                  selected_areas=viss_eu_cd_list)
        
        # Supporting elements 
        response['supporting_elements'] = self.list_supporting_elements(workspace_uuid=workspace_uuid, 
                                                                        subset_uuid=subset_uuid, 
                                                                        request=request['supporting_elements'], 
                                                                        indicator_settings=True, 
                                                                        selected_areas=viss_eu_cd_list) 
        
        # Apply data filter 
        self.action_apply_data_filter(workspace_uuid=workspace_uuid, 
                                      subset_uuid=subset_uuid, 
                                      step=1) 
        
        self.action_apply_indicator_settings_data_filter(workspace_uuid=workspace_uuid, 
                                                         subset_uuid=subset_uuid, 
                                                         step=2)
               
        return response
    
    
    
    
    #==========================================================================
    @timer
    def request_subset_delete(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        "request" must contain: 
            workspace_uuid
            subset_uuid
        
        Returns a dict like:
            {
            	"alias": "New Name",
              "subset_uuid": "...",
              "status": "..."
            }
        """
        workspace_uuid = request['workspace_uuid']
        subset_uuid = request['subset_uuid']
        
        self._check_valid_uuid(workspace_uuid)
        
        self.action_load_workspace(workspace_uuid) 

        self._check_valid_uuid(workspace_uuid, subset_uuid)
        
        self.delete_subset(workspace_uuid=workspace_uuid, subset_uuid=subset_uuid) 
        
        response = self.dict_subset(workspace_uuid=workspace_uuid, subset_uuid=subset_uuid)
        
        return response
    
    
    #==========================================================================
    @timer
    def request_subset_edit(self, request):
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180719    by Magnus Wenzer
        
        "request" must contain: 
            workspace_uuid
            subset_uuid
            alias (new alias for subset)
            
            
        Returns a dict like:
            {
            	"alias": "New Name",
              "subset_uuid": "...",
              "status": "..."
            }
        """
        alias = request['alias'] 
        workspace_uuid = request['workspace_uuid']
        subset_uuid = request['subset_uuid']
        self._check_valid_uuid(workspace_uuid)
        
        self.action_load_workspace(workspace_uuid) 

        self._check_valid_uuid(workspace_uuid, subset_uuid)
        
        workspace_object = self.get_workspace(workspace_uuid)
        uuid_mapping = workspace_object.uuid_mapping 
        
        old_alias = uuid_mapping.get_alias(subset_uuid)
        if alias == old_alias:
            raise exceptions.SubsetAlreadyExists(code='subset_alias_unchanged')
            
        uuid_mapping.set_alias(subset_uuid, alias)
        
        status = request.get('status', False)
        if status: 
            uuid_mapping.set_status(subset_uuid, status)
        else:
            status = uuid_mapping.get_status(unique_id=subset_uuid)
        
        response = self.dict_subset(workspace_uuid=workspace_uuid, 
                                    subset_uuid=subset_uuid)
        
        return response
    

    #==========================================================================
    @timer
    def request_subset_info(self, request):
        """
        Created     20180321    by Magnus Wenzer
        Updated     20180605    by Magnus Wenzer
        
        Handles a single subset. 
        """
        
        workspace_uuid = request['workspace_uuid'] 
        subset_uuid = request['subset_uuid'] 
        
        all_ok = self.action_load_data(workspace_uuid, force=False)
        if not all_ok:
            return {}
#            return {'workspace_uuid': workspace_uuid}
        self._check_valid_uuid(workspace_uuid, subset_uuid)
        
        response = {}
        response['workspace_uuid'] = workspace_uuid
        response['workspace'] = self.dict_workspace(workspace_uuid)
        
        response['subset'] = self.dict_subset(workspace_uuid=workspace_uuid, 
                                    subset_uuid=subset_uuid, 
                                    include_indicator_settings=False, 
                                    time=False, 
                                    areas=False, 
                                    quality_elements=False, 
                                    supporting_elements=False)
        return response
    
    
    #==========================================================================
    @timer 
    def request_subset_list(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180317    by Magnus Wenzer
        
        "request" must contain: 
            workspace_uuid 
        
        Returns a dict like:
            {
            	"workspace": {
            		"alias": "My Workspace",
            		"uuid": "...",
            		"status": "editable"
            	},
            	"subsets": [
            		{
            			"alias": "My Subset 1",
            			"uuid": "...",
            			"active": true,
            			"periods": [
            				{
            					"label": "2006-2012",
            					"status": "editable",
            					'value': true,
            					'key': "2006-2012"
            				},
            				{
            					"label": "2012-2017",
            					"status": "editable",
            					'value': false,
            					'key': "2012-2017"
            				}
            			],
            			"areas": [
            				{
            					"label": "WB 1",
            					"status": "editable",
            					'value': true,
            					'key': "WB 1"
            				},
            				{
            					"label": "WB 2",
            					"status": "editable",
            					'value': true,
            					'key': "WB 2"
            				},
            				{
            					"label": "WB 3",
            					"status": "editable",
            					'value': false,
            					'key': "WB 3"
            				},
            				{
            					"label": "WB 4",
            					"status": "editable",
            					'value': true,
            					'key': "WB 4"
            				}
            			],
            			"water_districts": [
            				{
            					"label": "Bottenhavet",
            					"status": "editable",
            					'value': true,
            					'key': "Bottenhavet"
            				},
            				{
            					"label": "Skagerakk",
            					"status": "editable",
            					'value': false,
            					'key': "Skagerakk"
            				}
            			],
            			"supporting_elements": [
            				{
            					"label": "Secchi",
            					"children": [
            						{
            							"label": "Secchi - default",
            							"status": "editable",
            							'value': false,
            							'key': "Secchi - default"
            						}
            					]
            				}
            			],
            			"quality_elements": [
            				{
            					"label": "Phytoplankton",
            					"children": [
            						{
            							"label": "Chlorophyll - default",
            							"status": "editable",
            							'value': true,
            							'key': "Chlorophyll - default"
            						},
            						{
            							"label": "Biovolume - default",
            							"status": "editable",
            							'value': true,
            							'key': "Biovolume - default"
            						}
            					]
            				}
            			]
            		}
            	]
            }
        """
        
        workspace_uuid = request['workspace_uuid']  
        
#        if 'default' in workspace_uuid: 
#            raise exceptions.
        # Initiate structure 
        response = {'workspace': {}, 
                   'subsets': []}
#        print('1:', time.time()-t0)
        
        # Load workspace 
        self.action_load_workspace(workspace_uuid)
#        self.assure_data_is_loaded(workspace_uuid=workspace_uuid)
#        print('2:', time.time()-t0)
        # Add workspace info 
        response['workspace_uuid'] = workspace_uuid
        response['workspace'] = self.dict_workspace(workspace_uuid=workspace_uuid)
#        print('3:', time.time()-t0)      
        subset_list = self.list_subsets(workspace_uuid=workspace_uuid)
#        print('4:', time.time()-t0)
        # Add subset info   
        response['subsets'] = subset_list
               
        return response
               
    
    #==========================================================================
    @timer
    def request_workspace_result(self, request):
        """
        Created     20180720    by Magnus Wenzer
        Updated     20180828    by Magnus Wenzer
        
        "request" must contain: 
            workspace_uuid
            
        """
        
        workspace_uuid = request['workspace_uuid'] 
        
        self.action_load_workspace(workspace_uuid)
        
        
        subset_uuid = request.get('subset_uuid') 
        if subset_uuid: 
            subset_uuid_list = [subset_uuid] 
        else:
            subset_uuid_list = self.get_subset_list(workspace_uuid)
        
        
        
        response = {} 
        response['workspace_uuid'] = workspace_uuid
        response['workspace'] = self.dict_workspace(workspace_uuid) 
        response['subset'] = {}
        
        for subset_uuid in subset_uuid_list: 
            response['subset'][subset_uuid] = self.dict_subset(workspace_uuid=workspace_uuid, 
                                                                subset_uuid=subset_uuid, 
                                                                result=True, 
                                                                time_as_string=True)
        return response
        
    
    #==========================================================================
    @timer 
    def request_workspace_add(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        "request" must contain: 
            alias (for the new workspace)
            source (uuid)
        
        Returns a dict like:
            {
            	"alias": "My Workspace",
            	"uuid": "my_workspace",
            	"status": "editable"
            }
        """
        self._logger.debug('Start: request_workspace_add')
        alias = request['alias'] 
        source_uuid = request['workspace_uuid'] 
#        print('###', user_id)
#        print('###', alias)
#        print('###', source_uuid)
        
        self.copy_workspace(source_uuid=source_uuid, target_alias=alias)
        
        uuid_mapping = self._get_uuid_mapping_object()
        workspace_uuid = uuid_mapping.get_uuid(alias)
        
        response = self.dict_workspace(workspace_uuid, check_data_availability=True)
        
        return response
    
    
    #==========================================================================
    @timer
    def request_workspace_delete(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        "request" must contain: 
            uuid 
        
        Returns status like: 
            {
            "all_ok": True/False, 
            "message": ""
            }
        """
        response = {"all_ok": True, 
                    "message": ""}
        
        unique_id = request['workspace_uuid']
#        print('###', user_id)
#        print('###', alias)
#        print('###', source_uuid)
        
        uuid_mapping = self._get_uuid_mapping_object()
        if unique_id not in uuid_mapping.get_uuid_list_for_user():
            response['all_ok'] = False
            response['message'] = 'Workspace does not belong to user'
            return response
            
#        print()
        all_ok = self.delete_workspace(unique_id=unique_id, permanently=False)
        if not all_ok:
            response['all_ok'] = False
            response['message'] = 'Could not delete workspace'
        
        return response
    
    
    #==========================================================================
    @timer
    def request_workspace_edit(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180719    by Magnus Wenzer
        
        "request" must contain: 
            workspace_uuid 
            alias (new alias)
        
        Returns a dict like:
            {
            	"alias": "New Name",
            	"workspace_uuid": "...", 
              "status": "..."
            }
        """
        alias = request['alias'] 
        workspace_uuid = request['workspace_uuid'] 
        self._check_valid_uuid(workspace_uuid)
        
        uuid_mapping = self._get_uuid_mapping_object()
        
        old_alias = uuid_mapping.get_alias(workspace_uuid)
        if alias == old_alias:
            raise exceptions.WorkspaceAlreadyExists(code='workspace_alias_unchanged')
        
        uuid_mapping.set_alias(workspace_uuid, alias)
        
        status = request.get('status', False)
        if status: 
            uuid_mapping.set_status(workspace_uuid, status)
        else:
            status = uuid_mapping.get_status(unique_id=workspace_uuid)
        
        response = self.dict_workspace(workspace_uuid=workspace_uuid)
        
        return response
    
    
    #==========================================================================
    @timer
    def request_workspace_list(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        "request" must contain: 
        
        Returns a dict like:
            {
            	"workspaces": [
            		{
            			"alias": "My Workspace",
            			"uuid": "my_workspace",
            			"status": "editable"
            		}
            	]
            }
        """
        self._logger.debug('Start: request_workspace_list')
        
        response = {'workspaces': []}
        response['workspaces'] = self.list_workspaces()
        
        return response 
    
    
    #==========================================================================
    @timer
    def request_workspace_info(self, request):
        """
        Created     20180718    by Magnus Wenzer
        Updated     
        
        "request" must contain: 
            workspace_uuid
        Returns a dict like:
    		{
    			"alias": "My Workspace",
    			"workspace_uuid": "my_workspace",
    			"status": "editable"
    		}

        """
        self._logger.debug('Start: request_workspace_list')
        
        workspace_uuid = request['workspace_uuid']
        
        response = self.dict_workspace(workspace_uuid=workspace_uuid)
        
        return response
    
    
    #==========================================================================
    @timer
    def request_workspace_data_sources_edit(self, request):
        """
        Created     20180524    by Magnus Wenzer
        Updated     
        
        Request like: 
            {   
                "workspace_uuid": "55ce9a98-bda3-40b4-ada7-d8d62a65eab2",
                "data_sources": [
                    {
                        "status": false,
                        "loaded": false,
                        "filename": "chlorophyll_integrated_2015_2016_row_format.txt",
                        "datatype": "chlorophyll"
                    },...]

        
        Returns a dict like:
            {
                "workspace_uuid": "55ce9a98-bda3-40b4-ada7-d8d62a65eab2",
                "data_sources": [
                    {
                        "status": false,
                        "loaded": false,
                        "filename": "chlorophyll_integrated_2015_2016_row_format.txt",
                        "datatype": "chlorophyll"
                    },...]
        """ 
        self._logger.debug('Start: request_workspace_data_sources_list')
        workspace_uuid = request['workspace_uuid'] 
        response = {} 
        
        # Load workspace 
        self.action_load_workspace(workspace_uuid)
#        print('listar')
        response['data_sources'] = self.list_data_sources(workspace_uuid=workspace_uuid, 
                                                          request=request['data_sources']) 
        
        # Load data 
        all_ok = self.load_data(workspace_uuid=workspace_uuid) 
        if all_ok: 
            response = self.request_workspace_data_sources_list({'workspace_uuid': workspace_uuid})
        
        return response
    
    
    #==========================================================================
    @timer
    def request_workspace_data_sources_list(self, request):
        """
        Created     20180524    by Magnus Wenzer
        Updated     
        
        Request like: 
            {
              "workspace_uuid": "55ce9a98-bda3-40b4-ada7-d8d62a65eab2"
            }

        
        Returns a dict like:
            {   
                "workspace_uuid": "55ce9a98-bda3-40b4-ada7-d8d62a65eab2",
                "data_sources": [
                    {
                        "status": false,
                        "loaded": false,
                        "filename": "chlorophyll_integrated_2015_2016_row_format.txt",
                        "datatype": "chlorophyll"
                    },...]
        """ 
        self._logger.debug('Start: request_workspace_data_sources_list')
        workspace_uuid = request['workspace_uuid'] 
        response = {} 
        response['workspace_uuid'] = workspace_uuid
                
        # Load workspace 
        self.action_load_workspace(workspace_uuid)
        
        response['data_sources'] = self.list_data_sources(workspace_uuid=workspace_uuid)
        return response
        
    
    #==========================================================================
    def request_workspace_import_default_data(self, request):
        """
        Created     20180319    by Magnus Wenzer
        Updated     20180720    by Magnus Wenzer
        
        "request" must contain: 
            {
              "workspace_uuid": "335af11c-a7d4-4edf-bc21-d90ffb762c70"
            }
        
        Returns status like: 
            {
            "all_ok": True/False, 
            "message": ""
            }
        """
        self._logger.debug('Start: request_workspace_load_default_data')
        workspace_uuid = request['workspace_uuid'] 
        response = {"all_ok": False, 
                    "message": ""}
        
        self._check_valid_uuid(workspace_uuid)
        uuid_mapping_object = self._get_uuid_mapping_object()
#        print('user_id', user_id)
#        print(workspace_uuid)
#        print(uuid_mapping_object.get_uuid_list_for_user(user_id))
        if workspace_uuid not in uuid_mapping_object.get_uuid_list_for_user():
            response['all_ok'] = False 
            response['message'] = "Workspace does not belong to user"
            return response
        
        # Call action-method to load workspace and copy data
        all_ok = self.action_workspace_load_default_data(workspace_uuid=workspace_uuid)
        
        response['all_ok'] = all_ok
        if not all_ok:
            response['message'] = "Could not load default data"
            
        return response
    
#    #==========================================================================
#    def request_subset_info(self, request):
#        """
#        Created     20180220    by Magnus Wenzer
#        Updated     20180220    by Magnus Wenzer
#        
#        Returns a list with dicts with subset info for the given workspace.  
#        """
#        workspace_object = self._get_workspace_object_from_alias(workspace_alias)
#        if not workspace_object:
#            return False
#        
#        return workspace_object.json_subset_info()
    
    
#    #==========================================================================
#    def set_data_filter(self, 
#                        user_id, 
#                        workspace_alias=None, 
#                        step='', 
#                        subset='', 
#                        filter_type='', 
#                        filter_name='', 
#                        data=None, 
#                        append_items=False): 
#        """
#        Created     20180220    by Magnus Wenzer
#        Updated     20180221    by Magnus Wenzer
#        
#        Sets the data filter as described. 
#        """
#        self._logger.debug('Start: set_data_filter')
#        assert all([workspace_alias, step, subset, filter_type, filter_name, data])
#        workspace_object = self._get_workspace_object_from_alias(workspace_alias) 
#        if not workspace_object:
#            return False 
#        
#        return workspace_object.set_data_filter(step=step, 
#                                                subset=subset, 
#                                                filter_type=filter_type, 
#                                                filter_name=filter_name, 
#                                                data=data, 
#                                                append_items=append_items)
    
    #==========================================================================
    def get_settings_filter_object(self, 
                                    workspace_uuid='', 
                                    subset_uuid='',
                                    indicator='', 
                                    step='step_2', 
                                    filter_type=''): 
        """
        Created     20180321    by Magnus Wenzer
        Updated     20180321    by Magnus Wenzer
        """
        if not filter_type:
            return False
        workspace_object = self.get_workspace(workspace_uuid) 
        subset_object = workspace_object.get_subset_object(subset_uuid) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_uuid))
            return {}
        
        step_object = subset_object.get_step_object(step)
        
        if filter_type == 'data':
            return step_object.get_indicator_data_filter_settings(indicator)
        elif filter_type == 'tolerance':
            return step_object.get_indicator_tolerance_settings(indicator)
    

#==========================================================================
def get_interval_from_list(input_list):
    """
    Created     20180619    by Magnus Wenzer
    Updated     20180716    by Magnus Wenzer

    Takes a list and returns a an interval as a list. 
    Example: [3, 4, 5, 6] => [3, 6]
    """ 
    if type(input_list) not in (list, tuple): 
        return None
    elif not len(set([type(i) for i in input_list])) == 1:
        return None
    
    output_list = []
    for item in input_list:
        if type(item) == list: 
            output_list.append(get_interval_from_list(item))
        else: 
            return [input_list[0], input_list[-1]]
    return output_list 


#==========================================================================
def get_list_from_interval(input_interval):
    """
    Created     20180619   by Magnus Wenzer
    Updated     20180717   by Magnus Wenzer

    Takes an interval in a list and returns a list with the gange of the interval: 
        Example: [2, 7] => [2, 3, 4, 5, 6, 7] 
    If start value > stop value the interval in intepretated as month interval: 
        Example: [12, 3] => [12, 1, 2, 3]
    """ 
    if not input_interval:
        return None
    elif not len(set([type(i) for i in input_interval])) == 1:
        return None
    
    start_value = input_interval[0]
    stop_value = input_interval[-1]
    
    if type(start_value) != list: 
        output_list = []
        value = input_interval[0]
        while value != input_interval[-1]:
            output_list.append(value)
            value += 1
            if stop_value < start_value and value == 13:
                value = 1
        output_list.append(stop_value)
        return output_list
    else:
        output_list = []
        for item in input_interval: 
            output_list.append(get_list_from_interval(item))
        return output_list
    
        
        
        
def print_json(data): 
    json_string = json.dumps(data, indent=2, sort_keys=True)
    print(json_string)
        
   
#"""
#===============================================================================
#===============================================================================
#===============================================================================
#"""     
if __name__ == '__main__':
#    root_path = os.path.dirname(os.path.dirname(os.path.os.path.abspath(os.path.realpath(__file__))))
    root_path = os.path.dirname(os.path.os.path.abspath(os.path.realpath(__file__)))
    user_id_1 = 'user_1'
    user_id_2 = 'user_2'
    ekos = EventHandler(root_path)
    user_1_ws_1 = 'mw1'
    
    if 0:
        ekos.copy_workspace(user_id_1, source_alias='default_workspace', target_alias=user_1_ws_1)
        ekos.copy_workspace(user_id_1, source_alias='default_workspace', target_alias='mw2')
        
        ekos.copy_workspace(user_id_2, source_alias='default_workspace', target_alias='test1')
        ekos.copy_workspace(user_id_2, source_alias='default_workspace', target_alias='test2')
    
    ekos.load_test_requests()
    
    if 0:
        # Request workspace list 
        request = ekos.test_requests['request_workspace_list']
        response = ekos.request_workspace_list(request) 
        ekos.write_test_response('request_workspace_list', response)
        
        # Request subset list 
        request = ekos.test_requests['request_subset_list']
        response_subset_list = ekos.request_subset_list(request)
        ekos.write_test_response('request_subset_list', response_subset_list)
        
        # Load default data
        request = ekos.test_requests['request_workspace_load_default_data']
        ekos.request_workspace_load_default_data(request)
        
        # Add new subset 
        request = ekos.test_requests['request_subset_add']
        response_subset_add = ekos.request_subset_add(request)
        ekos.write_test_response('request_subset_add', response_subset_add)
        
        # Edit subset 
        request = ekos.test_requests['request_subset_edit']
        response_subset_edit = ekos.request_subset_edit(request)
        ekos.write_test_response('request_subset_edit', response_subset_edit)
    
    
    
    
    
    w_id = '335af11c-a7d4-4edf-bc21-d90ffb762c70'
    s_id = '1bdd7eb5-2f2a-44f6-bd7e-c26bf09ce047'
    
    ekos.apply_data_filter(user_id=user_id_1,  
                           workspace_uuid=w_id,
                           subset_uuid=s_id,
                           step='step_1')
    
    
#    w = ekos.get_workspace(user_id=user_id_1, alias='mw1')
#    
#    wb_mapping = ekos.mapping_objects['water_body']
    
    
    
    
    
##    ekos.load_all_workspaces_for_user()
#    
#    ekos.copy_workspace(user_id, source_alias='default_workspace', target_alias='mw1')
#    ekos.copy_workspace(user_id, source_alias='default_workspace', target_alias='mw2')
#    ekos.copy_workspace(user_id, source_alias='default_workspace', target_alias='mw3')
#    
#    
#    
#    ekos.copy_subset(user_id, workspace_source_alias='mw2', subset_source_alias='default_subset', subset_target_alias='test_subset_1')
#    ekos.copy_subset(user_id, workspace_source_alias='mw2', subset_source_alias='default_subset', subset_target_alias='test_subset_2')
#    ekos.copy_subset(user_id, workspace_source_alias='mw2', subset_source_alias='default_subset', subset_target_alias='test_subset_3')
#    ekos.copy_subset(user_id, workspace_source_alias='mw3', subset_source_alias='default_subset', subset_target_alias='test_subset_4')
#    
#    ekos.delete_subset(user_id, workspace_alias='mw2', subset_alias='test_subset_2')
#    # default_workspace
##    default_workspace = ekos.get_workspace('default')
    

        