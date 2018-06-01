# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:05:36 2018

@author: a001985
"""

import os
import shutil
import time

import json
import codecs


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
"""
Module to handle all events linked to the Django application. 
Maybe this should be in the root? Maybe not a class, only functions? Maybe __name__ == "__main__"?

MW: Started this to start logging functionality. 
""" 

class EventHandler(object): 
    def __init__(self, 
                 user_id=None, 
                 workspace_directory='',
                 resource_directory='', 
                 log_directory='', 
                 test_data_directory=''): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180530    by Magnus Wenzer
        
        MW 20180530: Only one usr per event handler. 
        In terms of user_id this does not really matter at the moment. 
        user_id must be given in every call and the corresponding uuid_mapping 
        file is loaded in the method call if neaded. 
        """
        assert all([user_id, workspace_directory, resource_directory, log_directory]), 'Missing directory paths when creating EventHandler instance.' 
                 
        self.user_id = user_id
        self.workspace_directory = workspace_directory
        self.resource_directory = resource_directory
        self.log_directory = log_directory
        self.test_data_directory = test_data_directory
        
        
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
        
        # Mapping objects
        self.mapping_objects = {}
        self.mapping_objects['water_body'] = core.WaterBody(file_path=os.path.join(self.resource_directory, 'mappings/water_body_match.txt'))
        self.mapping_objects['quality_element'] = core.QualityElement(file_path=os.path.join(self.resource_directory, 'Quality_Elements.cfg'))
        self.mapping_objects['hypsographs'] = core.Hypsograph(file_path=os.path.join(self.resource_directory, 'mappings/hypsographs.txt'))
        
        self.mapping_objects['display_mapping'] = core.ParameterMapping()
        self.mapping_objects['display_mapping'].load_mapping_settings(file_path=os.path.join(self.resource_directory, 'mappings/display_mapping.txt'))
        
        if self.test_data_directory:
            self.load_test_requests()
    
    #==========================================================================
    def _change_ok(self, alias): 
        if alias in ['default_workspace', 'default_subset']: 
            self._logger.warning('Not allowed to make changes to "{}"!'.format(alias))
            return False
        return True
    
    
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
            if item['active']: 
                return_list.append(item['value'])
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
    def _get_workspace_object(self, unique_id=None): 
        """
        Updated     20180530    by Magnus wenzer
        """
        # TODO: _get_workspace_object and self.get_workspace does the same thing. 
        # TODO: Maybe use self.get_workspace to handle status and check against user etc 
        return self.workspaces.get(unique_id, False)
    
    
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
    def apply_data_filter(self, 
                          workspace_uuid=None,
                          subset_uuid=None,
                          step='step_1'): 
        """
        Updated     20180530    by Magnus Wenzer 
        """
        w = self._get_workspace_object(unique_id=workspace_uuid)
        w.apply_data_filter(subset=subset_uuid,step=step)
        
        
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
        w = self._get_workspace_object(unique_id=workspace_uuid)
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
        Updated     20180601    by Magnus Wenzer
        
        """
        workspace_object = self.workspaces.get(workspace_uuid, False)
        if not workspace_object:
            self._logger.warning('Workspace "{}" not loaded.'.format(subset_source_uuid))
            return False
#        print('!!!!!!!!!!!!', subset_source_alias) 
#        print('!!!!!!!!!!!!', subset_target_alias) 
#            print('subset_source_alias'.upper(), subset_source_alias)
        self._logger.debug('Trying to copy subset "{}"'.format(subset_source_uuid))
        return_dict = workspace_object.copy_subset(subset_source_uuid, subset_target_alias)
#        print('return_dict'.upper(), return_dict)
        return return_dict
        
    #==========================================================================
    def copy_workspace(self, source_uuid=None, target_alias=None): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180530    by Lena Viktorsson
        
        """ 
        if self.user_id == 'default':
            self._logger.warning('Can not copy workspace as default user. ')
            return 
        
        uuid_mapping = self._get_uuid_mapping_object()

        # Add UUID for workspace in uuid_mapping 
        target_uuid = uuid_mapping.add_new_uuid_for_alias(target_alias)
        if not target_uuid:
            self._logger.debug('Could not add workspace with alias "{}". Workspace already exists!'.format(target_alias)) 
            return False
        
        # Copy all directories and files in workspace 
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
    def delete_subset(self, workspace_unique_id=None, subset_alias=None, subset_unique_id=None, permanently=False): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180530    by Magnus Wenzer
        
        Deletes the given subset in the given workspace. 
        """ 
        if not self._change_ok(workspace_unique_id):
            return False 
        if not self._change_ok(subset_alias):
            return False
        
        if not workspace_unique_id:
            return False
        workspace_object = self.workspaces.get(workspace_unique_id, False)
        if not workspace_object:
            return False
        
        return workspace_object.delete_subset(unique_id=subset_unique_id, permanently=permanently)
        
    
    #==========================================================================
    def delete_workspace(self, unique_id=None, permanently=False): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180223    by Lena Viktorsson
        
        Deletes the given workspace. 
        """ 

        
        uuid_mapping = self._get_uuid_mapping_object()
#        print('USER_ID', user_id)
        if unique_id not in uuid_mapping.get_uuid_list_for_user(self.user_id):
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
                           workspace_unique_id=None, 
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
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        if not workspace_object:
            return {}
        
        datatype_settings_object = workspace_object.datatype_settings
        if not datatype_settings_object.has_info:
            return {}
        
        if request:
            datatype_settings_object.set_status(file_name=file_name, status=request['status'])
            info_dict = request
        else:
            info_dict = datatype_settings_object.get_info_for_file(file_name) 
            info_dict['loaded'] = bool(info_dict['loaded'])
            info_dict['status'] = bool(info_dict['status'])
#            print('-'*50)
#            print(info_dict)
            
        return info_dict
    
    
    #==========================================================================
    def dict_indicator(self, 
                       workspace_unique_id=None, 
                       subset_unique_id=None, 
                       indicator=None, 
                       available_indicators=None, 
                       request=None, 
                       include_indicator_settings=False): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180321    by Magnus Wenzer
        
        dict like: 
            {
							"label": "Biovolume - default",
							"status": "selectable",
							"selected": true,
							"value": "Biovolume - default", 
                        "settings": {}
						}
        """
        return_dict = {"label": "",
					   "status": "",
					   "selected": False,
					   "value": "", 
                    "settings": {}}
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return return_dict
        
        if subset_unique_id == 'default_subset': 
            available_indicators = []
        else:
            available_indicators = workspace_object.get_available_indicators(subset=subset_unique_id, step='step_1')
            
        # Check request 
        selected = True
        if request and 'selected' in request.keys():
            selected = request['selected']
            
        # Check if indicator is available 
        if indicator in available_indicators: 
            status = "selectable"
        else:
            status = "not selectable"
            selected = False
            
        
        return_dict["label"] = self.mapping_objects['display_mapping'].get_mapping(indicator, 'internal_name', 'display_en')
        return_dict["status"] = status
        return_dict["selected"] = selected
        return_dict["value"] = indicator
    
        if include_indicator_settings: 
            request_list = []
            if request and 'settings' in request:
                request_list = request['settings']
            return_dict["settings"] = self.list_indicator_settings(workspace_unique_id=workspace_unique_id, 
                                                                    subset_unique_id=subset_unique_id, 
                                                                    indicator=indicator, 
                                                                    request=request_list)
#            if indicator == 'din_winter':
#                dgfs
        return return_dict
    
    #==========================================================================
    def dict_time(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
        """
        Created     20180317   by Magnus Wenzer
        Updated     20180317   by Magnus Wenzer
        """
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {}

        data_filter_object = subset_object.get_data_filter_object('step_1')
        if request:
            data_filter_object.set_filter(filter_type='include_list', 
                                          filter_name='MYEAR', 
                                          data=request['year_interval'])
#            data_filter_object.set_filter(filter_type='include_list', 
#                                          filter_name='MONTH', 
#                                          data=request['month_list'])
            
        else:
            year_list = sorted(map(int, data_filter_object.get_include_list_filter('MYEAR')))
#            month_list = sorted(map(int, data_filter_object.get_include_list_filter('MONTH')))
            
            return {"year_interval": [year_list[0], year_list[-1]]}#, "month_list": month_list}
        
    #==========================================================================
    def dict_indicator_settings(self, 
                              workspace_unique_id=None, 
                              subset_unique_id=None, 
                              indicator=None, 
                              type_area=None, 
                              request=None): 
        """
        Created     20180321   by Magnus Wenzer
        Updated     20180323   by Magnus Wenzer
        
        Takes information from settings filter in step 2. 
        """
        
        
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {}
        
#        if indicator == 'din_winter':
#            print('='*50)
#            print(workspace_unique_id)
#            print(subset_unique_id)
#            print(indicator)
#            print(type_area)
#            print('='*50)
#            df
        settings_data_filter_object = self.get_settings_filter_object(workspace_unique_id=workspace_unique_id, 
                                                                           subset_unique_id=subset_unique_id,
                                                                           indicator=indicator, 
                                                                           filter_type='data')
        if not settings_data_filter_object:
            self._logger.debug('Could not load data filter object for indicator "{}"'.format(indicator))
            return {}
        
        
        settings_tolerance_filter_object = self.get_settings_filter_object(workspace_unique_id=workspace_unique_id, 
                                                                           subset_unique_id=subset_unique_id,
                                                                           indicator=indicator,
                                                                           filter_type='tolerance')
         
        
#        type_area = self.mapping_objects['water_body'].get_list('type_area', water_body=water_body)
        if not type_area:
            return {}
#        type_area = type_area[0]
        
        if request:
            value_dict = {type_area: {}} 
            depth_interval_list = []
            month_list_list = []
            min_no_years_list = []
            for k in range(len(request['depth_interval'])):
                # Add data filter
                depth_interval = request['depth_interval'][k]
                month_interval = request['month_interval'][k]
                month_list = [] 
                month = month_interval[0]
                while month != month_interval[-1]:
                    month_list.append(month)
                    month += 1
                    if month == 13:
                        month = 1
                month_list.append(month_interval[-1])  
                
                # Add tolerance filter
                min_no_years = request['min_no_years'][k]

                depth_interval_list.append(depth_interval)
                month_list_list.append(month_list)
                min_no_years_list.append(min_no_years)
                
            value_dict[type_area]['DEPH_INTERVAL'] = depth_interval_list 
            value_dict[type_area]['MONTH_LIST'] = month_list_list
            value_dict[type_area]['MIN_NR_YEARS'] = min_no_years_list 
                      
            settings_data_filter_object.set_values(value_dict) 
            settings_tolerance_filter_object.set_values(value_dict)
            return request
            
            
        else:
            return_dict = {}
            return_dict['value'] = type_area
            return_dict['indicator'] = indicator
            
            # Depth
            return_dict['depth_interval'] = settings_data_filter_object.get_value(type_area=type_area, variable='DEPH_INTERVAL')
            
            # Month
            month_list = settings_data_filter_object.get_value(type_area=type_area, variable='MONTH_LIST') 
            # Give interval instead of list. Each item in the list chould be converted 
            month_interval = []
            for month in month_list:
                month_interval.append([month[0], month[-1]])
            return_dict['month_interval'] = month_interval
        
            # Min number of years 
            return_dict['min_no_years'] = settings_tolerance_filter_object.get_value(type_area=type_area, variable='MIN_NR_YEARS')
            
#        if indicator == 'bqi':
#            self.return_dict = return_dict
#            qq
        return return_dict
        
#    #==========================================================================
#    def dict_period(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
#        """
#        Created     20180221    by Magnus Wenzer
#        Updated     20180222    by Magnus Wenzer
#        
#        NOT USED YET! 
#        
#        Information is taken from data filter in step 1. 
#        This should be more dynamic in the future. For example not set ranges but min and max year. 
#        """ 
#            
#        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
#        subset_object = workspace_object.get_subset_object(subset_unique_id) 
#        if not subset_object:
#            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
#            return {}
#        
#        data_filter_object = subset_object.get_data_filter_object('step_1')
#        
#        year_list = data_filter_object.get_include_list_filter('MYEAR')
#
#        return {"label": "2006-2012",
#				  "status": "selectable",
#				  "selected": True,
#				  "value": "2006-2012"}
        
        
    #==========================================================================
    def dict_quality_element(self, 
                             workspace_unique_id=None, 
                             subset_unique_id=None, 
                             quality_element=None, 
                             request={}, 
                             include_indicator_settings=False): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180321    by Magnus Wenzer
        
        dict like: 
            {
					"label": "Phytoplankton", 
					"children": []
				}
        """
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {"label": '',
    					"children": []}
        
        request_dict = None
        if request: 
            for req in request:
                if req['label'] == quality_element:
                      request_dict = req['children']
                      break
        return_dict = {'label': quality_element, 
                       "children": self.list_indicators(workspace_unique_id=workspace_unique_id, 
                                                        subset_unique_id=subset_unique_id, 
                                                        quality_element=quality_element, 
                                                        request=request.get('children', []), 
                                                        include_indicator_settings=include_indicator_settings)} 
                       
#        request_dict = None
#        if request: 
#            for req in request:
#                if req['label'] == quality_element:
#                      request_dict = req['children']
#                      break
#        return_dict = {'label': quality_element, 
#                       "children": self.list_indicators(workspace_unique_id=workspace_unique_id, 
#                                                        subset_unique_id=subset_unique_id, 
#                                                        quality_element=quality_element, 
#                                                        request=request_dict, 
#                                                        include_indicator_settings=include_indicator_settings)} 
        
        return return_dict
        
        
    #==========================================================================
    def dict_subset(self, workspace_unique_id=None, subset_unique_id=None, request={}, include_indicator_settings=False):  
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180317    by Magnus Wenzer
        
        """
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id)
        
        subset_dict = {}
#        subset_dict = {'alias': None,
#                        'subset_uuid': None,
#                        'status': None,
#                        'active': None,
#                        'time': {}, 
#                        'areas': [], 
##                        'periods': [], # Should be removed
##                        'water_bodies': [], 
##                        'water_districts': [], 
#                        'supporting_elements': [], 
#                        'quality_elements': []}
        
        if not subset_unique_id and request.get('subset_uuid', False):
            subset_unique_id = request['subset_uuid']
            
        subset_dict['alias'] = workspace_object.uuid_mapping.get_alias(subset_unique_id, status=self.all_status) 
        subset_dict['subset_uuid'] = subset_unique_id
        subset_dict['status'] = workspace_object.uuid_mapping.get_status(unique_id=subset_unique_id) 
        subset_dict['active'] = workspace_object.uuid_mapping.is_active(unique_id=subset_unique_id)
            
        # Check request 
        if request.get('active', False):
            if request['active']:
                workspace_object.uuid_mapping.set_active(subset_unique_id)
            else:
                workspace_object.uuid_mapping.set_inactive(subset_unique_id)
        
        if request == None: 
            request = {}
            
        
        # Time
        subset_dict['time'] = self.dict_time(workspace_unique_id=workspace_unique_id, 
                                                   subset_unique_id=subset_unique_id, 
                                                   request=request.get('time', {}))
        
        # Deprecated list for periods
#        subset_dict['periods'] = self.list_periods(workspace_unique_id=workspace_unique_id, 
#                                                   subset_unique_id=subset_unique_id, 
#                                                   request=request.get('periods', {}))
        
        
        # Areas (contains water_district, type_area and water_body in a tree structure) 
        subset_dict['areas'] = self.list_areas(workspace_unique_id=workspace_unique_id, 
                                                        subset_unique_id=subset_unique_id, 
                                                        request=request.get('areas', []))
        
        # Quality elements 
        subset_dict['quality_elements'] = self.list_quality_elements(workspace_unique_id=workspace_unique_id, 
                                                                     subset_unique_id=subset_unique_id, 
                                                                     request=request.get('quality_elements', []), 
                                                                     include_indicator_settings=include_indicator_settings)
        
        # Quality elements 
        subset_dict['supporting_elements'] = self.list_supporting_elements(workspace_unique_id=workspace_unique_id, 
                                                                           subset_unique_id=subset_unique_id, 
                                                                           request=request.get('supporting_elements', []), 
                                                                           include_indicator_settings=include_indicator_settings)


        

        return subset_dict
                                
    
    #==========================================================================
    def dict_water_body(self, workspace_unique_id=None, subset_unique_id=None, water_body=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180315    by Magnus Wenzer
        
        Internally its only possible to filter water bodies.  
        """
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
#        print(subset_unique_id)
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {"label": "",
                      "value": "",
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
            wb_active_list = data_filter_object.get_include_list_filter('WATER_BODY')
            water_body_mapping = self.mapping_objects['water_body']
            if water_body in wb_active_list:
                active = True
                
            # Always selectable if no request
            return {"label": water_body_mapping.get_display_name(water_body=water_body),
                      "value": water_body,
                      "type": "water_body",
                      "status": "selectable", 
                      "url": water_body_mapping.get_url(water_body), 
                      "active": active}
                          
        
    #==========================================================================
    def dict_type_area(self, workspace_unique_id=None, subset_unique_id=None, type_area=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180315    by Magnus Wenzer
        
        "selectable" is not checked at the moment....
        """
        
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {"label": "",
                      "value": "",
                      "type": "",
                      "status": "", 
                      "active": False, 
                      "children": []}
            
        if request: 
            # Add active water bodies to include filter. 
            # Set the data filter for water body here instead of adding one by one in dict_water_body 
            active_water_bodies = self._get_active_values_in_list_with_dicts(request['children'])
            subset_object.set_data_filter(step='step_1', 
                                          filter_type='include_list', 
                                          filter_name='WATER_BODY', 
                                          data=active_water_bodies, 
                                          append_items=True)
            return request
        else:
            active = False 
            data_filter_object = subset_object.get_data_filter_object('step_1')
            water_body_active_list = data_filter_object.get_include_list_filter('WATER_BODY')
            water_body_mapping = self.mapping_objects['water_body']
            
            type_area_active_list = water_body_mapping.get_list('type_area', water_body=water_body_active_list)
            
            if type_area in type_area_active_list:
                active = True
                
            return_dict = {"label": water_body_mapping.get_display_name(type_area=type_area),
                          "value": type_area,
                          "type": "type_area",
                          "status": "selectable", 
                          "active": active, 
                          "children": []}
            
            children_list = []
            for water_body in water_body_mapping.get_list('water_body', type_area=type_area):
                children_list.append(self.dict_water_body(workspace_unique_id=workspace_unique_id, 
                                                          subset_unique_id=subset_unique_id, 
                                                          water_body=water_body, 
                                                          request=request)) 
                # request not active here...
            return_dict['children'] = children_list 
        
            return return_dict
        
        
    #==========================================================================
    def dict_water_district(self, workspace_unique_id=None, subset_unique_id=None, water_district=None, request=None): 
        """
        Created     20180315    by Magnus Wenzer
        Updated     20180315    by Magnus Wenzer
        
        Internally its only possible to filter water bodies.  
        "selectable" needs to be checked against water district and type. 
        """
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
#        print('subset_unique_id', subset_unique_id)
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        water_body_mapping = self.mapping_objects['water_body']
#        print('subset_unique_id'.upper(), subset_unique_id)
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {"label": "",
                      "value": "",
                      "type": "",
                      "status": "", 
                      "active": False, 
                      "children": []}
            
        if request: 
            for child in request['children']: 
                type_area = child['value'] 
                # Water district is not set as a internal data filter list. Only water body is saved. 
                self.dict_type_area(workspace_unique_id=workspace_unique_id, 
                                                          subset_unique_id=subset_unique_id, 
                                                          type_area=type_area, 
                                                          request=child)
            return request
        else:
            
            active = False 
            self.temp_subset_object =subset_object
            data_filter_object = subset_object.get_data_filter_object('step_1')
            water_body_active_list = data_filter_object.get_include_list_filter('WATER_BODY')
            
#            print('****')
#            print(water_body_active_list)
            water_district_active_list = water_body_mapping.get_list('water_district', water_body=water_body_active_list)
            
            if water_district in water_district_active_list:
                active = True
                
            return_dict = {"label": water_body_mapping.get_display_name(water_district=water_district),
                          "value": water_district,
                          "type": "water_district",
                          "status": "selectable", 
                          "active": active, 
                          "children": []}
            
            children_list = []
            for type_area in water_body_mapping.get_list('type_area', water_district=water_district):
                children_list.append(self.dict_type_area(workspace_unique_id=workspace_unique_id, 
                                                          subset_unique_id=subset_unique_id, 
                                                          type_area=type_area, 
                                                          request=request)) 
                # request not active here...
            return_dict['children'] = children_list 
        
            return return_dict
                
    #==========================================================================
    def dict_workspace(self, unique_id=None): 
        """
        Created     20180221    by Magnus Wenzer
        Updated     201805030    by Magnus Wenzer
        
        """
        uuid_mapping = self._get_uuid_mapping_object()
        alias = uuid_mapping.get_alias(unique_id, status=self.all_status) 
        status = uuid_mapping.get_status(unique_id=unique_id)
        
        return {'alias': alias, 
                'workspace_uuid': unique_id,
                'status': status}
    
    #==========================================================================
    def get_alias_for_unique_id(self, workspace_unique_id=None, subset_unique_id=None): 
        if workspace_unique_id and subset_unique_id: 
            workspace_object = self.workspaces.get(workspace_unique_id, None)
            if not workspace_object:
                return False
            return workspace_object.get_alias_for_unique_id(subset_unique_id)
        elif workspace_unique_id:
            uuid_mapping = self._get_uuid_mapping_object()
            return uuid_mapping.get_alias(workspace_unique_id)
        
        
    #==========================================================================
    def get_unique_id_for_alias(self, workspace_alias=None, subset_alias=None):
        uuid_mapping = self._get_uuid_mapping_object()
        if workspace_alias and subset_alias: 
            workspace_unique_id = uuid_mapping.get_uuid(workspace_alias)
            workspace_object = self.workspaces.get(workspace_unique_id, None) 
            workspace_object = self._get_workspace_object(unique_id=workspace_unique_id)
            if not workspace_object:
                return False 
            return workspace_object.get_unique_id_for_alias(subset_alias)
        elif workspace_alias:
            return uuid_mapping.get_uuid(workspace_alias)
        else:
            return False
           
            
    #==========================================================================
    def get_subset_list(self, workspace_unique_id=None): 
        # Load workspace if not loaded
        if workspace_unique_id not in self.workspaces.keys():
            all_ok = self.load_workspace(unique_id=workspace_unique_id)
            if not all_ok:
                return []
        workspace_object = self.workspaces.get(workspace_unique_id, None)
        return workspace_object.get_subset_list()
    
    
    #==========================================================================
    def get_workspace(self, alias=None, unique_id=None, include_deleted=False): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180219    by Magnus Wenzer
        
        """
        # Get UUID for workspace
        if alias == 'default_workspace':
            unique_id = 'default_workspace'
        else:
            uuid_mapping = self._get_uuid_mapping_object()
            status = self.include_status[:]
            if include_deleted:
                status.append('deleted')
            if not unique_id:
                unique_id = uuid_mapping.get_uuid(alias, status=status)
        if not unique_id:
            return False
        # return matching workspace 
        self._logger.debug('Getting workspace "{}" with alias "{}"'.format(unique_id, alias)) 
        
        return self.workspaces.get(unique_id, None)
    
    
    #==========================================================================
    def get_workspaces_for_user(self, status=[]):
        uuid_mapping = self._get_uuid_mapping_object() 
        return uuid_mapping.get_uuid_list_for_user(status=status)
    
    
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
                        workspace_unique_id=None, 
                        request=[]): 
        """
        Created     20180524    by Magnus Wenzer
        Updated     
        
        request is a list of dicts. 
        """ 
#        print(workspace_unique_id)
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        if not workspace_object:
            print('NOT workspace_object') 
            print(workspace_unique_id)
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
            
            filename_dict = self.dict_data_source(workspace_unique_id=workspace_unique_id, 
                                                   file_name=filename, 
                                                   request=request_dict)
            # TODO: Compare request_dict and filename_dict
            response.append(filename_dict)
            
        return response
        
    
    #==========================================================================
    def list_indicators(self, 
                        workspace_unique_id=None, 
                        subset_unique_id=None, 
                        quality_element=None, 
                        request=[], 
                        include_indicator_settings=False): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180524    by Magnus Wenzer
        
        request is a list of dicts. 
        """ 
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
#        subset_object = workspace_object.get_subset_object(subset_unique_id)
        
        indicator_list = self.mapping_objects['quality_element'].get_indicator_list_for_quality_element(quality_element)
        
        # Check available indicators. Check this onse (here) and send list to dict_indicators to avoid multiple calls 
        if subset_unique_id == 'default_subset':
            available_indicators = []
        else:
            if not len(workspace_object.data_handler.all_data): # use len, all_data is a pandas dataframe
                workspace_object.load_all_data()
            available_indicators = workspace_object.get_available_indicators(subset=subset_unique_id, step='step_1')
        
        return_list = []
        for indicator in indicator_list:
            request_dict = {}
            # Need to check which element in request list belong to the indicator 
            for ind in request:
                if ind['value'] == indicator:
                    request_dict = ind
                    break
            
            indicator_dict = self.dict_indicator(workspace_unique_id=workspace_unique_id, 
                                                 subset_unique_id=subset_unique_id, 
                                                 indicator=indicator, 
                                                 available_indicators=available_indicators, 
                                                 request=request_dict, 
                                                 include_indicator_settings=include_indicator_settings)
        
            return_list.append(indicator_dict)
        
        return return_list
        
    #==========================================================================
    def list_indicator_settings(self, 
                                workspace_unique_id=None, 
                                subset_unique_id=None, 
                                indicator=None, 
                                request=[]): 
        """
        Created     20180321    by Magnus Wenzer
        Updated     20180524    by Magnus Wenzer
        
        request is a list of dicts. 
        """ 
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
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
        indicator_settings_object = workspace_object.get_indicator_settings_data_filter_object(subset=subset_unique_id, 
                                                                                               step='step_2', 
                                                                                               indicator=indicator)
        if not indicator_settings_object:
            # No settings for indicator 
            return []
            
        type_area_list = set(indicator_settings_object.get_type_area_list())
        return_list = []
        for type_area in type_area_list:
            request_dict = {}
            # Need to check which element in request list belong to the indicator 
            for ty in request:
#                    print(ty)
                if ty and ty['value'] == type_area: # ty can be empty dict if no settiengs for indicator
                    request_dict = ty
                    break
                    
            indicator_settings_dict = self.dict_indicator_settings(workspace_unique_id=workspace_unique_id, 
                                                                  subset_unique_id=subset_unique_id, 
                                                                  indicator=indicator, 
                                                                  type_area=type_area, 
                                                                  request=request_dict)
            return_list.append(indicator_settings_dict)
        
#        if indicator == 'bqi':
#            self.type_area_list = type_area_list
#            self.return_list = return_list
#            qq
        return return_list
        
    #==========================================================================
    def list_periods(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        Temporary method to give static periods.
        """
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        
        # Check request
        if request:
            for per in request:
                if per["selected"]:
#                    print('per', per)
                    from_year, to_year = map(int, per["value"].split('-'))
                    year_list = map(str, list(range(from_year, to_year+1)))
#                    print('subset_object.alias', subset_object.alias)
                    subset_object.set_data_filter(step='step_1', filter_type='include_list', filter_name='MYEAR', data=year_list)
                    break
#            print('request'.upper(), request)
            return request

        return [{"label": "2007-2012",
    				"status": "selectable",
    				"selected": False,
    				"value": "2007-2012"}, 
    
                {"label": "2013-2018",
    				"status": "selectable",
    				"selected": True,
    				"value": "2013-2018"}]
        
    
    #==========================================================================
    def list_quality_elements(self, 
                              workspace_unique_id=None, 
                              subset_unique_id=None, 
                              request=[], 
                              include_indicator_settings=False): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180524    by Magnus Wenzer
        
        """ 
#        print('list_quality_elements', request)
#        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
#        subset_object = workspace_object.get_subset_object(subset_unique_id)
        
        quality_element_list = self.mapping_objects['quality_element'].get_quality_element_list() 
        exclude = ['secchi depth', 'nutrients', 'oxygen balance']
        quality_element_list = [item for item in quality_element_list if item not in exclude]
        
        request_for_label = self._get_mapping_for_name_in_dict('label', request)
        
        
        return_list = []
        for quality_element in quality_element_list:
            sub_request = request_for_label.get(quality_element, {})
            quality_element_dict = self.dict_quality_element(workspace_unique_id=workspace_unique_id, 
                                                             subset_unique_id=subset_unique_id, 
                                                             quality_element=quality_element, 
                                                             request=sub_request, 
                                                             include_indicator_settings=include_indicator_settings)
        
            return_list.append(quality_element_dict)
        
        return return_list
    
    
    #==========================================================================
    def list_subsets(self, workspace_unique_id=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180317    by Magnus Wenzer 
        
        request is a list of subsets
        """
#        print('list_subsets_request', request)
        subset_list = []
#        subset_uuid_list = [] 
#        sub_request_list = []
        self.temp_request = request
        request_for_subset_uuid = self._get_mapping_for_name_in_dict('subset_uuid', request)
        self.temp_request_for_subset_uuid = request_for_subset_uuid
#                subset_uuid_list.append(sub['uuid'])
#                sub_request_list.append(sub)
#        else: 
#            subset_uuid_list = self.get_subset_list(workspace_unique_id=workspace_unique_id, user_id=user_id)
#            sub_request_list = [None]*len(subset_uuid_list)
            
#        for subset_uuid, sub_request in zip(subset_uuid_list, sub_request_list): 
#        print('=====SUBSET_UUID=====')
#        print(workspace_unique_id)
#        print(user_id)
#        print(self.workspaces)
#        print('=====================')
        for subset_uuid in self.get_subset_list(workspace_unique_id=workspace_unique_id):
#            print('=====SUBSET_UUID', '"{}"'.format(subset_uuid))
            sub_request = request_for_subset_uuid.get(subset_uuid, {})
            
            # Check uuid for subset in request (if given) 
#            if request:
#                for sub in request:
#    #                    print(sub)
#                    if sub['uuid'] == subset_uuid:
#                        break
        
            # Get subset dict
            subset_dict = self.dict_subset(workspace_unique_id=workspace_unique_id, 
                                           subset_unique_id=subset_uuid, 
                                           request=sub_request)
            
            
            # Add subset dict to subset list
            subset_list.append(subset_dict)
               
        return subset_list
    
    
    #==========================================================================
    def list_supporting_elements(self, 
                                 workspace_unique_id=None, 
                                 subset_unique_id=None, 
                                 request=[], 
                                 include_indicator_settings=False): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180321    by Magnus Wenzer
        
        """ 
#        print('list_supporting_elements', request)
#        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
#        subset_object = workspace_object.get_subset_object(subset_unique_id)
        
        quality_element_list = ['secchi depth', 'nutrients', 'oxygen balance']
        
        request_for_label = self._get_mapping_for_name_in_dict('label', request)
        
#        print('request', request)
        return_list = []
        for quality_element in quality_element_list: 
            
            sub_request = request_for_label.get(quality_element, {})
#            # Check request 
#            qe_dict = None
#            if request:
#                for qe in request:
#                    if qe['value'] == quality_element:
#                        qe_dict = qe
#                        break
                    
            quality_element_dict = self.dict_quality_element(workspace_unique_id=workspace_unique_id, 
                                                             subset_unique_id=subset_unique_id, 
                                                             quality_element=quality_element, 
                                                             request=sub_request, 
                                                             include_indicator_settings=include_indicator_settings)
        
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
            workspace_list.append(self.dict_workspace(unique_id=unique_id))
        
#        if include_default:
#            workspace_list.append(self.dict_workspace(unique_id='default_workspace')) 
        
        return workspace_list
        
        
    
    #==========================================================================
    def list_areas(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
        """
        Created     20180315    by Magnus Wenzer
        Updated     20180315    by Magnus Wenzer
        
        Lists information for "areas". Areas are hierarchically structured like: 
            [
                {
                  "label": "SE5",
                  "value": "SE5",
                  "type": "district",
                  "status": "selectable",
                  "active": true,
                  "children": [
                        {
                          "label": "1s - Västkustens inre kustvatten, södra",
                          "value": "1s",
                          "type": "type_area",
                          "status": "selectable",
                          "active": true,
                          "children": [
                                {
                                  "label": "Balgöarkipelagen",
                                  "value": "SE570900-121060",
                                  "type": "water_body",
                                  "status": "disabled",
                                  "active": false
                                }
                              ]
                          }
                      ]
                  }
               ]
        """
        # Try to load subset if not loaded 
#        subset_object = workspace_object.get_subset_object(subset_unique_id) 
#        if not subset_object:
#            self.load_su
        
#        print('request'.upper(), request.keys())
#        if 'water_district' not in request
        area_list = [] 
        self.temp_request = request
        request_for_water_district = self._get_mapping_for_name_in_dict('value', request)
        

        for water_district in self.mapping_objects['water_body'].get_list('water_district'):
            sub_request = request_for_water_district.get(water_district, None)
        
            response = self.dict_water_district(workspace_unique_id=workspace_unique_id, 
                                                subset_unique_id=subset_unique_id, 
                                                water_district=water_district, 
                                                request=sub_request)
            area_list.append(response)
        
        return area_list
        
        
    #==========================================================================
    def deprecated_list_type_areas(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        Lists information for type areas. 
        """
        # Check request 
        if request:
            workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
            # Create list of type areas 
            type_area_list = [req['value'] for req in request if req['selected']]
            # Set data filter 
            workspace_object.set_data_filter(step='step_1', filter_type='include_list', filter_name='TYPE_AREA', data=type_area_list)
            
            return request
        else:
            return_list = []
            for type_area in self.mapping_objects['water_body'].get_type_area_list(): 
    
                        
                type_area_dict = self.dict_type_area(workspace_unique_id=workspace_unique_id, 
                                                       subset_unique_id=subset_unique_id, 
                                                       type_area=type_area, 
                                                       request=request)
                return_list.append(type_area_dict)
    
            return return_list
        
    
    #==========================================================================
    def list_water_bodies(self, workspace_unique_id=None, subset_unique_id=None, type_area=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180315    by Magnus Wenzer
        
        Lists information for water bodies.
        """
        if not all([workspace_unique_id, subset_unique_id, type_area]):
            return []
        
        # Check request 
        if request:
            workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
            # Create list of type areas 
            water_body_list = [req['value'] for req in request if req['selected']]
            # Set data filter 
            workspace_object.set_data_filter(step='step_1', subset=subset_unique_id, filter_type='include_list', filter_name='WATER_BODY', data=water_body_list)
            
            return request
        else:
            
            return_list = []
            for water_body in self.mapping_objects['water_body'].get_list('water_body', type_area=type_area): 
                
                water_body_dict = self.dict_water_body(workspace_unique_id=workspace_unique_id, 
                                                       subset_unique_id=subset_unique_id, 
                                                       water_body=water_body, 
                                                       request=request)
                return_list.append(water_body_dict)
        
            return return_list
    
    
    #==========================================================================
    def list_water_district(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        NOT DYNAMIC YET. NEEDS TO BE MAPPED! 
        
        Lists information for water district. 
        """
        # TODO: kanske kan behandlas som periods for nu?
        return_list = [{
        					"label": "Bottenhavet",
        					"status": "selectable",
        					"selected": True,
        					"value": "Bottenhavet"
        				},
        				{
        					"label": "Skagerakk", 
        					"status": "selectable",
        					"selected": False,
        					"value": "Skagerakk"
        				}] 
        
        return return_list
    
#        for water_body in self.mapping_objects['water_body'].get_water_body_list():
#            water_body_dict = self.dict_water_body(workspace_unique_id=workspace_unique_id, 
#                                                   subset_unique_id=subset_unique_id, 
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
    def deprecated_assure_data_is_loaded(self, user_id=None, workspace_uuid=None): 
        """
        Created     20180323    by Magnus Wenzer
        Updated     20180323    by Magnus Wenzer
        
        Assures that data is loaded in the given workspace. 
        Data is loaded if workspace.index_handler.data_handler.all_data is empty
        """
        self.assure_workspace_is_loaded(user_id=user_id, workspace_uuid=workspace_uuid)
        workspace_object = self._get_workspace_object(user_id=user_id, unique_id=workspace_uuid)
#        self.ih = workspace_object.index_handler
        if not len(workspace_object.index_handler.data_handler_object.all_data):
            workspace_object.load_all_data()
        
    #==========================================================================
    def deprecated_assure_workspace_is_loaded(self, user_id=None, workspace_uuid=None): 
        """
        Created     20180323    by Magnus Wenzer
        Updated     20180323    by Magnus Wenzer
        
        Assures that workspace is loaded. 
        Loads workspace if not loaded. 
        """
        if workspace_uuid not in self.workspaces:
            self.load_workspace(user_id=user_id, unique_id=workspace_uuid)
        
        
    #==========================================================================
    def load_data(self, unique_id=None, force=False): 
        workspace_object = self._get_workspace_object(unique_id=unique_id) 
        if not workspace_object:
            return False 
        
        workspace_object.load_all_data(force=force)
        
        
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
        if name.startswith('request_'):
            name = name[8:]
        file_path = '{}/requests/response_{}.txt'.format(self.test_data_directory, name)
        with codecs.open(file_path, 'w', encoding='cp1252') as fid:
            json.dump(response, fid, indent=4)        
        
        
    #==========================================================================
    def update_workspace_uuid_in_test_requests(self, new_uuid, filename=None): 
        """
        Created     20180524    by Magnus Wenzer
        Updated     
        
        Changes workspace uuid in all test requests. 
        This is used for easy work in notebook.  
        """ 
        if len(new_uuid) != 36: 
            print('Not a valid uuid!')
            return
        directory = '{}/requests'.format(self.test_data_directory)
        for file_name in os.listdir(directory):
            if 'response' in file_name:
                continue 
            
            if filename and file_name != filename:
                continue
            
            file_path = os.path.join(directory, file_name)
            with codecs.open(file_path, 'r', encoding='cp1252') as fid: 
#                print(file_path)
                j = json.load(fid) 
            if 'workspace_uuid' in j.keys(): 
                print('Updating workspace_uuid in file: {}'.format(file_name))
                if j['workspace_uuid'] != 'default_workspace':
                    j['workspace_uuid'] = new_uuid
                    
            elif 'workspace' in j.keys():
                if 'workspace_uuid' in j['workspace'].keys():
                    if j['workspace']['workspace_uuid'] != 'default_workspace':
                        j['workspace']['workspace_uuid'] = new_uuid
                    
            with codecs.open(file_path, 'w', encoding='cp1252') as fid:
                json.dump(j, fid, indent=4) 
                
        self.load_test_requests()
        
    #==========================================================================
    def load_workspace(self, unique_id=None, reload=False): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180531    by Magnus Wenzer
        
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
            
        
        if not self.workspaces[unique_id]:
            self._logger.warning('Could not load workspace "{}" with alias "{}"'.format(unique_id, alias))
            return False
        else:
            self._logger.info('Workspace "{}" with alias "{} loaded."'.format(unique_id, alias))
            return True            
           
            
    #==========================================================================
    def action_load_workspace(self, workspace_uuid=None, force=False): 
        """
        Created     20180530    by Magnus Wenzer
        Updated     
        
        Action to load workspace. 
        """
        all_ok = self.load_workspace(unique_id=workspace_uuid, reload=force)
        return all_ok
    
    
    #==========================================================================
    def action_load_all_data(self, workspace_uuid): 
        workspace_object = self._get_workspace_object(unique_id=workspace_uuid)  
        self.action_load_workspace()
    
    
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
        
        workspace_object = self._get_workspace_object(unique_id=workspace_uuid) 
        all_ok = workspace_object.import_default_data(force=force)
        
        if all_ok:
            workspace_object.load_all_data(force=force)
        return all_ok
        
        
    #==========================================================================
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
        t0 = time.time()
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
        response = self.dict_subset(workspace_unique_id=workspace_uuid, 
                                   subset_unique_id=subset_uuid)
        
        self._logger.debug('Time for excecuting request_subset_add: {}'.format(time.time()-t0)) 
        return response
    
    #==========================================================================
    def request_subset_delete(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        "request" must contain: 
            workspace_uuid
            subset_uuid
        
        Returns a dict like:
            {
            	"alias": "My Workspace",
            	"uuid": "..."
            }
        """
        self._logger.debug('Start: request_subset_delete')
        workspace_uuid = request['workspace_uuid']
        subset_uuid = request['subset_uuid']
#        print('###', user_id)
#        print('###', alias)
#        print('###', source_uuid)
        uuid_mapping = self._get_uuid_mapping_object()
        workspace_alias = uuid_mapping.get_alias(workspace_uuid) 
        response = self.delete_subset(workspace_alias=workspace_alias, subset_unique_id=subset_uuid)
        
        return response
    
    
    #==========================================================================
    def request_subset_edit(self, request):
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180323    by Magnus Wenzer
        
        """
        self._logger.debug('Start: request_subset_edit')
        workspace_uuid = request['workspace']['workspace_uuid'] 
        request_subset_list = request['subsets']
        if not self.get_workspace(unique_id=workspace_uuid):
            return {} 
        
        response = self.list_subsets(workspace_unique_id=workspace_uuid, request=request_subset_list)
        request['subsets'] = response
#        request_list = None
#        if 'subsets' in request.keys():
#            request_list = request['subsets']
#        response = self.list_subsets(workspace_unique_id=workspace_uuid, user_id=user_id, request=request_list)
        return request
#        return response
    

    #==========================================================================
    def request_subset_info(self, request):
        """
        Created     20180321    by Magnus Wenzer
        Updated     20180322    by Magnus Wenzer
        
        Handles a single subset. 
        """
        
        self._logger.debug('Start: request_subset_info')
        workspace_uuid = request['workspace_uuid'] 
        request_subset_dict = request['subset']
        if not self.get_workspace(unique_id=workspace_uuid):
            return {} 
        self.assure_data_is_loaded(workspace_uuid=workspace_uuid)
        response = self.dict_subset(workspace_unique_id=workspace_uuid, 
                                    request=request_subset_dict, 
                                    include_indicator_settings=True)
        request['subset'] = response

        
        return request
    
    
    #==========================================================================
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
            					"status": "selectable",
            					"selected": true,
            					"value": "2006-2012"
            				},
            				{
            					"label": "2012-2017",
            					"status": "selectable",
            					"selected": false,
            					"value": "2012-2017"
            				}
            			],
            			"areas": [
            				{
            					"label": "WB 1",
            					"status": "selectable",
            					"selected": true,
            					"value": "WB 1"
            				},
            				{
            					"label": "WB 2",
            					"status": "selectable",
            					"selected": true,
            					"value": "WB 2"
            				},
            				{
            					"label": "WB 3",
            					"status": "selectable",
            					"selected": false,
            					"value": "WB 3"
            				},
            				{
            					"label": "WB 4",
            					"status": "selectable",
            					"selected": true,
            					"value": "WB 4"
            				}
            			],
            			"water_districts": [
            				{
            					"label": "Bottenhavet",
            					"status": "selectable",
            					"selected": true,
            					"value": "Bottenhavet"
            				},
            				{
            					"label": "Skagerakk",
            					"status": "selectable",
            					"selected": false,
            					"value": "Skagerakk"
            				}
            			],
            			"supporting_elements": [
            				{
            					"label": "Secchi",
            					"children": [
            						{
            							"label": "Secchi - default",
            							"status": "selectable",
            							"selected": false,
            							"value": "Secchi - default"
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
            							"status": "selectable",
            							"selected": true,
            							"value": "Chlorophyll - default"
            						},
            						{
            							"label": "Biovolume - default",
            							"status": "selectable",
            							"selected": true,
            							"value": "Biovolume - default"
            						}
            					]
            				}
            			]
            		}
            	]
            }
        """
#        t0 = time.time()
        self._logger.debug('Start: request_subset_list')
        
        workspace_uuid = request['workspace_uuid'] 
        # Initiate structure 
        response = {'workspace': {}, 
                   'subsets': []}
#        print('1:', time.time()-t0)
        
        # Load workspace 
        self.action_load_workspace(workspace_uuid)
#        self.assure_data_is_loaded(workspace_uuid=workspace_uuid)
#        print('2:', time.time()-t0)
        # Add workspace info
        response['workspace'] = self.dict_workspace(unique_id=workspace_uuid)
#        print('3:', time.time()-t0)      
        subset_list = self.list_subsets(workspace_unique_id=workspace_uuid)
#        print('4:', time.time()-t0)
        # Add subset info   
        response['subsets'] = subset_list
               
        return response
               
    
    #==========================================================================
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
        source_uuid = request['source'] 
#        print('###', user_id)
#        print('###', alias)
#        print('###', source_uuid)
        
        response = self.copy_workspace(source_uuid=source_uuid, target_alias=alias)
        
        return response
    
    
    #==========================================================================
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
        self._logger.debug('Start: request_workspace_delete')
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
            
        print()
        all_ok = self.delete_workspace(unique_id=unique_id, permanently=False)
        if not all_ok:
            response['all_ok'] = False
            response['message'] = 'Could not delete workspace'
        
        return response
    
    
    #==========================================================================
    def request_workspace_edit(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180531    by Magnus Wenzer
        
        "request" must contain: 
            alias (new alias)
            uuid 
        
        Returns a dict like:
            {
            	"alias": "New Name",
            	"uuid": "...", 
              "status": "..."
            }
        """
        t0 = time.time() 
        self._logger.debug('Start: request_workspace_edit')
        alias = request['alias'] 
        unique_id = request['workspace_uuid'] 
        
        uuid_mapping = self._get_uuid_mapping_object()
        uuid_mapping.set_alias(unique_id, alias)
        
        status = request.get('status', False)
        if status: 
            uuid_mapping.set_status(unique_id, status)
        else:
            status = uuid_mapping.get_status(unique_id=unique_id)
        
        response = {"alias": alias, 
                    "uuid": unique_id, 
                    "status": status}
        
        self._logger.debug('Time for excecuting request_workspace_data_sources_list: {}'.format(time.time()-t0))
        return response
    
    #==========================================================================
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
        t0 = time.time()
        self._logger.debug('Start: request_workspace_list')
        
        response = {'workspaces': []}
        response['workspaces'] = self.list_workspaces()
        
        self._logger.debug('Time for excecuting request_workspace_list: {}'.format(time.time()-t0))
        return response
    
    
    #==========================================================================
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
        t0 = time.time()
        self._logger.debug('Start: request_workspace_data_sources_list')
        workspace_uuid = request['workspace_uuid'] 
        response = {} 
        
        # Load workspace 
        self.action_load_workspace()
        
        response['data_sources'] = self.list_data_sources(workspace_unique_id=workspace_uuid, 
                                                          request=request['data_sources']) 
        
        # Load data 
        self.load_data(unique_id=workspace_uuid)
        self._logger.debug('Time for excecuting request_workspace_data_sources_edit: {}'.format(time.time()-t0))
        return response
    
    
    #==========================================================================
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
        t0 = time.time()
        self._logger.debug('Start: request_workspace_data_sources_list')
        workspace_uuid = request['workspace_uuid'] 
        response = {} 
        response['workspace_uuid'] = workspace_uuid
                
        # Load workspace 
        self.action_load_workspace(workspace_uuid)
        
        response['data_sources'] = self.list_data_sources(workspace_unique_id=workspace_uuid)
        self._logger.debug('Time for excecuting request_workspace_data_sources_list: {}'.format(time.time()-t0))
        return response
        
    
    #==========================================================================
    def request_workspace_load_default_data(self, request):
        """
        Created     20180319    by Magnus Wenzer
        Updated     20180322    by Magnus Wenzer
        
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
                                    workspace_unique_id='', 
                                    subset_unique_id='',
                                    indicator='', 
                                    step='step_2', 
                                    filter_type=''): 
        """
        Created     20180321    by Magnus Wenzer
        Updated     20180321    by Magnus Wenzer
        """
        if not filter_type:
            return False
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {}
        
        step_object = subset_object.get_step_object(step)
        
        if filter_type == 'data':
            return step_object.get_indicator_data_filter_settings(indicator)
        elif filter_type == 'tolerance':
            return step_object.get_indicator_tolerance_settings(indicator)
    
    
        
        
        
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
    

        
        
        
        
        
        
        
        
        
        