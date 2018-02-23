# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:05:36 2018

@author: a001985
"""

import os
import shutil
import sys
import datetime
import codecs
import pandas as pd
import uuid
import re 
import pathlib
import getpass


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
    def __init__(self, root_path): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180219    by Magnus Wenzer
        
        """
        self.root_path = root_path.replace('\\', '/') 
        self.workspace_directory = self.root_path + '/workspaces'
        self.resource_directory = self.root_path + '/resources'
        
        self.log_directory = self.root_path + '/log'
        self.log_id = 'event_handler'
        
        self.include_status = ['editable', 'readable']
        self.all_status = ['editable', 'readable', 'deleted']
         
        # Add logger
        core.add_log(log_id=self.log_id, 
                     log_directory=self.log_directory, 
                     log_level='DEBUG', 
                     on_screen=True, 
                     prefix='main')
        
        # Test main logger
        self._logger = core.get_log(self.log_id)
        self._logger.debug('Start EventHandler: {}'.format(self.log_id))
        self._logger.debug('')
        self._logger.info('TEST info logger')
        self._logger.warning('TEST warning logger')
        self._logger.error('TEST error logger')
        self._logger.debug('TEST debug logger')
        
        self.workspaces = {}
        
        # Load UUID mapping file for workspaces
        self.uuid_mapping = core.UUIDmapping('{}/uuid_mapping.txt'.format(self.workspace_directory))
        
        # Mapping objects
        self.mapping_objects = {}
        self.mapping_objects['water_body'] = core.WaterBody(file_path=self.root_path + '/resources/mappings/water_body_match.txt')
        self.mapping_objects['quality_element'] = core.QualityElement(file_path=self.root_path + '/resources/Quality_Elements.cfg')
        self.mapping_objects['display_mapping'] = core.ParameterMapping()
        self.mapping_objects['display_mapping'].load_mapping_settings(file_path=self.root_path + '/resources/mappings/display_mapping.txt')
        
    
    #==========================================================================
    def _change_ok(self, alias): 
        if alias in ['default_workspace', 'default_subset']: 
            self._logger.warning('Not allowed to make changes to "{}"!'.format(alias))
            return False
        return True
    
    
    #==========================================================================
    def _get_workspace_object(self, user_id=None, alias=None, unique_id=None): 
        if user_id and alias:
            unique_id = self.uuid_mapping.get_uuid(alias, user_id) 
        if not unique_id:
            return False
        return self.workspaces.get(unique_id, None)
    
    
    #==========================================================================
    def apply_data_filter(self, 
                          user_id=None,  
                          workspace_uuid=None): 
        pass
        
        
    #==========================================================================
    def change_workspace_alias(self, user_id, current_alias, new_alias): 
        
        unique_id = self.uuid_mapping.get_uuid(current_alias, user_id) 
        if not unique_id:
            return False
        self.uuid_mapping.set_alias(unique_id, new_alias)
    
    
    #==========================================================================
    def copy_subset(self, user_id, workspace_alias=None, workspace_uuid=None, subset_source_alias=None, subset_source_uuid=None, subset_target_alias=None): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180219    by Magnus Wenzer
        
        """
        if workspace_alias:
            workspace_uuid = self.uuid_mapping.get_uuid(workspace_alias, user_id)
        if not workspace_uuid:
            print('workspace_unique_id')
            return False
        workspace_object = self.workspaces.get(workspace_uuid)
        if not workspace_object:
            print('workspace_object')
            return False
#        print('!!!!!!!!!!!!', subset_source_alias) 
#        print('!!!!!!!!!!!!', subset_target_alias)
        if subset_source_uuid:
            print('subset_source_uuid'.upper(), subset_source_uuid)
            subset_source_alias = workspace_object.uuid_mapping.get_alias(subset_source_uuid) 
            print('subset_source_alias'.upper(), subset_source_alias)
        self._logger.debug('Trying to copy subset "{}". Copy has alias "{}"'.format(subset_source_alias, subset_target_alias))
        return_dict = workspace_object.copy_subset(subset_source_alias, subset_target_alias)
        print('return_dict'.upper(), return_dict)
        return return_dict
        
    #==========================================================================
    def copy_workspace(self, user_id, source_alias=None, source_uuid=None, target_alias=None): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180220    by Magnus Wenzer
        
        """
        if source_alias == 'default_workspace':
            source_uuid = self.uuid_mapping.get_uuid(source_alias, 'default') 
        elif source_alias:
            source_uuid = self.uuid_mapping.get_uuid(source_alias, user_id) 
            
        if not source_uuid:
            self._logger.warning('No alias named "{}"'.format(source_alias))
            return False
        
        if not source_alias:
            source_alias = self.uuid_mapping.get_alias(source_uuid)
            
        target_alias = '{} (copy of {})'.format(target_alias, source_alias)
        # Add UUID for workspace in uuid_mapping 
        target_uuid = self.uuid_mapping.add_new_uuid_for_alias(target_alias, user_id)
        if not target_uuid:
            self._logger.debug('Could not add workspace with alias "{}". Workspace already exists!'.format(target_alias)) 
            return False
        
        # Copy all directories and files in workspace 
        source_workspace_path = '/'.join([self.workspace_directory, source_uuid])
        target_workspace_path = '/'.join([self.workspace_directory, target_uuid])
        
        print('source_workspace_path:', source_workspace_path)
        print('target_workspace_path:', target_workspace_path)
        
        
        self._logger.debug('Trying to copy workspace "{}" with alias "{}". Copy has alias "{}"'.format(source_uuid, source_alias, target_alias))
        
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
        uuid_object = core.UUIDmapping(target_subset_uuid_mapping_file)
        
        uuid_list = uuid_object.get_uuid_list_for_user(user_id)
        for u_id in uuid_list:
            new_uuid = uuid_object.set_new_uuid(u_id)
            current_subset_path = '{}/subsets/{}'.format(target_workspace_path, u_id)
            new_subset_path = '{}/subsets/{}'.format(target_workspace_path, new_uuid)
            os.rename(current_subset_path, new_subset_path)
        
        status = self.uuid_mapping.get_status(unique_id=target_uuid) # Check in case default is changed
        
        return {'alias': target_alias,
                'uuid': target_uuid,
            	  'status': status}
    
    
    #==========================================================================
    def delete_subset(self, user_id=None, workspace_alias=None, subset_alias=None, subset_unique_id=None, permanently=False): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180220    by Magnus Wenzer
        
        Deletes the given subset in the given workspace. 
        """ 
        if not self._change_ok(workspace_alias):
            return False 
        if not self._change_ok(subset_alias):
            return False
            
        workspace_unique_id = self.uuid_mapping.get_uuid(workspace_alias, user_id)
        if not workspace_unique_id:
            return False
        workspace_object = self.workspaces.get(workspace_unique_id)
        if not workspace_object:
            return False
        
        return workspace_object.delete_subset(unique_id=subset_unique_id, permanently=permanently)
        
    
    #==========================================================================
    def delete_workspace(self, user_id=None, alias=None, unique_id=None, permanently=False):
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        Deletes the given workspace. 
        """ 
        if not self._change_ok(alias):
            return False  
        
        if alias:
            unique_id = self.uuid_mapping.get_uuid(alias, user_id, status=self.all_status)
        
#        if unique_id not in self.workspaces.keys(): 
#            self._logger.warning('Workspace "{}" with alias "{}" is not loaded!'.format(unique_id, alias))
#            return False 

        if permanently:
            path_to_remove = '/'.join([self.workspace_directory, unique_id])
            if 'workspace' not in path_to_remove:
                self._logger.error('Trying to delete workspace "{}" with alias "{}" but the path to delete is not secure!'.format(unique_id, alias)) 
                return False
            
            self._logger.warning('Permanently deleting workspace "{}" with alias "{}".'.format(unique_id, alias))
            # Delete files and folders: 
            shutil.rmtree(path_to_remove)
            
            # Remove objects and links 
            if unique_id in self.workspaces.keys():
                self.workspaces.pop(unique_id)
            
            # Remove in uuid_mapping
            self.uuid_mapping.permanent_delete_uuid(unique_id)
        else:
            self._logger.warning('Removing workspace "{}" with alias "{}".'.format(unique_id, alias)) 
            self.uuid_mapping.set_status(unique_id, 'deleted')
        
        return True 
     
    
    #==========================================================================
    def dict_indicator(self, workspace_unique_id=None, subset_unique_id=None, indicator=None, available_indicators=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        dict like: 
            {
							"label": "Biovolume - default",
							"status": "selectable",
							"selected": true,
							"value": "Biovolume - default"
						}
        """
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {"label": "",
					   "status": "",
					   "selected": False,
					   "value": ""}
        
        if not available_indicators:
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
            
        return_dict = {"label": self.mapping_objects['display_mapping'].get_mapping(indicator, 'internal_name', 'display_en'),
							"status": status,
							"selected": selected,
							"value": indicator}
        
        return return_dict
    
    #==========================================================================
    def dict_period(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        NOT USED YET! 
        
        Information is taken from data filter in step 1. 
        This should be more dynamic in the future. For example not set ranges but min and max year. 
        """ 
            
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {}
        
        data_filter_object = subset_object.get_data_filter_object('step_1')
        
        year_list = data_filter_object.get_include_list_filter('MYEAR')

        return {"label": "2006-2012",
				  "status": "selectable",
				  "selected": True,
				  "value": "2006-2012"}
        
        
    #==========================================================================
    def dict_quality_element(self, workspace_unique_id=None, subset_unique_id=None, quality_element=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
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
                                                        request=request_dict)} 
        
        return return_dict
        
        
    #==========================================================================
    def dict_subset(self, workspace_unique_id=None, subset_unique_id=None, request=None):  
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        """
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id)
        
        # Check request 
        if request:
            if request['active']:
                workspace_object.uuid_mapping.set_active(subset_unique_id)
            else:
                workspace_object.uuid_mapping.set_inactive(subset_unique_id)
            return request
        
        else:
            alias = workspace_object.uuid_mapping.get_alias(subset_unique_id, status=self.all_status) 
            status = workspace_object.uuid_mapping.get_status(unique_id=subset_unique_id) 
            active = workspace_object.uuid_mapping.is_active(unique_id=subset_unique_id)
    
            return {'alias': alias,
                    'uuid': subset_unique_id,
                    'status': status,
                	  'active': active,
                	  'periods': [], 
                    'water_bodies': [], 
                    'water_districts': [], 
                    'supporting_elements': [], 
                    'quality_elements': []}
                                
    
    #==========================================================================
    def dict_type_area(self, workspace_unique_id=None, subset_unique_id=None, type_area=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        type_area is "TYPE_AREA_NUMBER" at the moment. 
        "selected" needs to be checked against water district. 
        """
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {"label": '',
    					"status": '',
    					"selected": False,
    					"value": ''}
            
        if request: 
            # Return request. information about selected is taken in one step up
            return request
        else:
            selected = False 
            data_filter_object = subset_object.get_data_filter_object('step_1')
            type_area_active_list = data_filter_object.get_include_list_filter('TYPE_AREA_NUMBER')
            if type_area in type_area_active_list:
                selected = True
                
            return {"label": self.mapping_objects['display_mapping'].get_mapping(type_area, 'internal_name', 'display_en'),
    				  "status": "selectable",
    				  "selected": selected,
    				  "value": type_area}
        
    
    #==========================================================================
    def dict_water_body(self, workspace_unique_id=None, subset_unique_id=None, water_body=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        water_body is "SEA_AREA_NAME". 
        "selectable" needs to be checked against water district and type. 
        """
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
        subset_object = workspace_object.get_subset_object(subset_unique_id) 
        if not subset_object:
            self._logger.warning('Could not find subset object {}. Subset is probably not loaded.'.format(subset_unique_id))
            return {"label": '',
    					"status": '',
    					"selected": False,
    					"value": ''}
        
        if request: 
            # Return request. information about selected is taken in one step up
            return request
        else:
            selected = False 
            data_filter_object = subset_object.get_data_filter_object('step_1')
            wb_active_list = data_filter_object.get_include_list_filter('SEA_AREA_NAME')
            if water_body in wb_active_list:
                selected = True
                
            return {"label": self.mapping_objects['display_mapping'].get_mapping(water_body, 'internal_name', 'display_en'),
    				  "status": "selectable",
    				  "selected": selected,
    				  "value": water_body}
                          
                
                
    #==========================================================================
    def dict_workspace(self, unique_id=None): 
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        """
        alias = self.uuid_mapping.get_alias(unique_id, status=self.all_status) 
        status = self.uuid_mapping.get_status(unique_id=unique_id)
        
        return {'alias': alias, 
                'uuid': unique_id,
                'status': status}
    
    #==========================================================================
    def get_alias_for_unique_id(self, workspace_unique_id=None, subset_unique_id=None): 
        if workspace_unique_id and subset_unique_id: 
            workspace_object = self.workspaces.get(workspace_unique_id, None)
            if not workspace_object:
                return False
            return workspace_object.get_alias_for_unique_id(subset_unique_id)
        
        
    #==========================================================================
    def get_unique_id_for_alias(self, user_id, workspace_alias=None, subset_alias=None):
        if workspace_alias and subset_alias: 
            workspace_object = self._get_workspace_object(alias=workspace_alias, user_id=user_id)
            workspace_unique_id = self.uuid_mapping.get_uuid(workspace_alias, user_id)
            workspace_object = self.workspaces.get(workspace_unique_id, None) 
            if not workspace_object:
                return False 
            return workspace_object.get_unique_id_for_alias(subset_alias)
        elif workspace_alias:
            return self.uuid_mapping.get_uuid(workspace_alias, user_id)
        else:
            return False
           
            
    #==========================================================================
    def get_subset_list(self, workspace_unique_id): 
        workspace_object = self.workspaces.get(workspace_unique_id, None)
        return workspace_object.get_subset_list()
    
    
    #==========================================================================
    def get_workspace(self, user_id=None, alias=None, unique_id=None, include_deleted=False): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180219    by Magnus Wenzer
        
        """
        # Get UUID for workspace
        if alias == 'default_workspace':
            unique_id = 'default_workspace'
        else:
            status = self.include_status[:]
            if include_deleted:
                status.append('deleted')
            if not unique_id:
                unique_id = self.uuid_mapping.get_uuid(alias, user_id, status=status)
        if not unique_id:
            return False
        # return matching workspace 
        self._logger.debug('Getting workspace "{}" with alias "{}"'.format(unique_id, alias))
        return self.workspaces.get(unique_id, None)
    
    
    #==========================================================================
    def import_default_data(self, user_id, workspace_alias=None, force=False):
        """
        Created     20180220    by Magnus Wenzer
        Updated     20180220    by Magnus Wenzer
        
        Loads default data to the workspace with alias workspace_alias. 
        """ 
        unique_id = self.uuid_mapping.get_uuid(workspace_alias, user_id)
        self._logger.debug('Trying to load default data in workspace "{}" with alias "{}"'.format(unique_id, workspace_alias))
        workspace_object = self.workspaces.get(unique_id, None)
        if not workspace_object:
            return False
        workspace_object.import_default_data(force=force)
        
    
    #==========================================================================
    def list_indicators(self, workspace_unique_id=None, subset_unique_id=None, quality_element=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        request is a list och dicts. 
        """ 
        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
#        subset_object = workspace_object.get_subset_object(subset_unique_id)
        
        indicator_list = self.mapping_objects['quality_element'].get_indicator_list_for_quality_element(quality_element)
        
        # Check available indicators. Check this onse (here) and send list to dict_indicators to avoid multiple calls
        available_indicators = workspace_object.get_available_indicators(subset=subset_unique_id, step='step_1')
        
        return_list = []
        for indicator in indicator_list:
            request_dict = None
            if request:
                # Need to check which element in request list belong to the indicator 
                for ind in request:
                    if ind['value'] == indicator:
                        request_dict = ind
                        break
            
            indicator_dict = self.dict_indicator(workspace_unique_id=workspace_unique_id, 
                                                 subset_unique_id=subset_unique_id, 
                                                 indicator=indicator, 
                                                 available_indicators=available_indicators, 
                                                 request=request_dict)
        
            return_list.append(indicator_dict)
        
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
                    print('per', per)
                    from_year, to_year = map(int, per["value"].split('-'))
                    year_list = map(str, list(range(from_year, to_year+1)))
                    print('subset_object.alias', subset_object.alias)
                    subset_object.set_data_filter(step='step_1', filter_type='include_list', filter_name='MYEAR', data=year_list)
                    break
            print('request'.upper(), request)
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
    def list_quality_elements(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        """ 
        print('list_quality_elements', request)
#        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
#        subset_object = workspace_object.get_subset_object(subset_unique_id)
        
        quality_element_list = self.mapping_objects['quality_element'].get_quality_element_list() 
        exclude = ['secchi depth'] 
        quality_element_list = [item for item in quality_element_list if item not in exclude]
        
        
        return_list = []
        for quality_element in quality_element_list:
            quality_element_dict = self.dict_quality_element(workspace_unique_id=workspace_unique_id, 
                                                             subset_unique_id=subset_unique_id, 
                                                             quality_element=quality_element, 
                                                             request=request)
        
            return_list.append(quality_element_dict)
        
        return return_list
    
    
    #==========================================================================
    def list_subsets(self, workspace_unique_id=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer 
        
        request is a list of subsets
        """
#        print('list_subsets_request', request)
        subset_list = []
        for subset_uuid in self.get_subset_list(workspace_unique_id):
            
            # Check uuid for subset in request (if given) 
            if request:
                for sub in request:
#                    print(sub)
                    if sub['uuid'] == subset_uuid:
                        break
            
                # Get subset dict
                subset_dict = self.dict_subset(workspace_unique_id=workspace_unique_id, 
                                               subset_unique_id=subset_uuid, 
                                               request=sub)
                
                # Temporary default list for periods
                subset_dict['periods'] = self.list_periods(workspace_unique_id=workspace_unique_id, 
                                                           subset_unique_id=subset_uuid, 
                                                           request=sub['periods'])
                
                # Water bodies 
                subset_dict['water_bodies'] = self.list_water_bodies(workspace_unique_id=workspace_unique_id, 
                                                                     subset_unique_id=subset_uuid, 
                                                                     request=sub['water_bodies'])
                
                # Type area
                subset_dict['type_area'] = self.list_water_bodies(workspace_unique_id=workspace_unique_id, 
                                                                  subset_unique_id=subset_uuid, 
                                                                  request=sub['type_area'])
                
                # Type area
                subset_dict['water_districts'] = self.list_water_district(workspace_unique_id=workspace_unique_id, 
                                                                          subset_unique_id=subset_uuid, 
                                                                          request=sub['water_districts'])
                
                # Quality elements 
                subset_dict['quality_elements'] = self.list_quality_elements(workspace_unique_id=workspace_unique_id, 
                                                                             subset_unique_id=subset_uuid, 
                                                                             request=sub['quality_elements'])
                
                # Quality elements 
                subset_dict['supporting_elements'] = self.list_supporting_elements(workspace_unique_id=workspace_unique_id, 
                                                                                   subset_unique_id=subset_uuid, 
                                                                                   request=sub['supporting_elements'])
            else:
                # Get subset dict
                subset_dict = self.dict_subset(workspace_unique_id=workspace_unique_id, 
                                               subset_unique_id=subset_uuid, 
                                               request=None)
                
                # Temporary default list for periods
                subset_dict['periods'] = self.list_periods(workspace_unique_id=workspace_unique_id, 
                                                           subset_unique_id=subset_uuid, 
                                                           request=None)
                
                # Water bodies 
                subset_dict['water_bodies'] = self.list_water_bodies(workspace_unique_id=workspace_unique_id, 
                                                                     subset_unique_id=subset_uuid, 
                                                                     request=None)
                
                # Type area
                subset_dict['type_area'] = self.list_water_bodies(workspace_unique_id=workspace_unique_id, 
                                                                  subset_unique_id=subset_uuid, 
                                                                  request=None)
                
                # Type area
                subset_dict['water_districts'] = self.list_water_district(workspace_unique_id=workspace_unique_id, 
                                                                          subset_unique_id=subset_uuid, 
                                                                          request=None)
                
                # Quality elements 
                subset_dict['quality_elements'] = self.list_quality_elements(workspace_unique_id=workspace_unique_id, 
                                                                             subset_unique_id=subset_uuid, 
                                                                             request=None)
                
                # Quality elements 
                subset_dict['supporting_elements'] = self.list_supporting_elements(workspace_unique_id=workspace_unique_id, 
                                                                                   subset_unique_id=subset_uuid, 
                                                                                   request=None)
            
            # Add subset dict to subset list
            subset_list.append(subset_dict)
               
        return subset_list
    
    
    #==========================================================================
    def list_supporting_elements(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        """ 
        print('list_supporting_elements', request)
#        workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
#        subset_object = workspace_object.get_subset_object(subset_unique_id)
        
        quality_element_list = ['secchi depth']
        print('request', request)
        return_list = []
        for quality_element in quality_element_list: 
            
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
                                                             request=request)
        
            return_list.append(quality_element_dict)
        
        return return_list
    
    
        
    #==========================================================================
    def list_type_areas(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
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
    def list_water_bodies(self, workspace_unique_id=None, subset_unique_id=None, request=None): 
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        Lists information for water bodies.
        """
        # Check request 
        if request:
            workspace_object = self._get_workspace_object(unique_id=workspace_unique_id) 
            # Create list of type areas 
            water_body_list = [req['value'] for req in request if req['selected']]
            # Set data filter 
            workspace_object.set_data_filter(step='step_1', subset=subset_unique_id, filter_type='include_list', filter_name='WATER_BODY_NAME', data=water_body_list)
            
            return request
        else:
            
            return_list = []
            for water_body in self.mapping_objects['water_body'].get_water_body_list(): 
                
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
    def load_all_workspaces_for_user(self, user_id, with_status=None):
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180219    by Magnus Wenzer
        
        Loads all workspaces for the given user. Including default workspace.  
        """
        self._logger.debug('Trying to load all workspaces for user "{}"'.format(user_id))
        status = self.include_status[:]
        if with_status:
            if type(with_status) != list:
                with_status = [with_status]
            status = with_status
        workspace_list = ['default_workspace'] + self.uuid_mapping.get_uuid_list_for_user(user_id, status=status) 
        for unique_id in workspace_list: 
            self.load_workspace(unique_id=unique_id)
        
    
    #==========================================================================
    def load_data(self, user_id, workspace_alias): 
        workspace_object = self._get_workspace_object(user_id=user_id, alias=workspace_alias) 
        if not workspace_object:
            return False 
        
        workspace_object.load_all_data()
        
    #==========================================================================
    def load_workspace(self, user_id, alias=None, unique_id=None): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180219    by Magnus Wenzer
        
        Loads the given workspace. Subsets in workspace are also loaded. 
        """
        if alias == 'default_workspace':
            unique_id = 'default_workspace'
        elif unique_id == 'default_workspace':
            alias = 'default_workspace'
        elif alias:
            unique_id = self.uuid_mapping.get_uuid(alias, user_id) 
        elif unique_id:
            alias = self.uuid_mapping.get_alias(unique_id, user_id)
        
        print('¤¤¤ alias', alias)
        print('¤¤¤ unique_id', unique_id) 
        print('¤¤¤ user_id', user_id)

        if not all([alias, unique_id]):
            self._logger.warning('Could not load workspace "{}" with alias "{}"'.format(unique_id, alias))
            return False
        
        self._logger.debug('Trying to load workspace "{}" with alias "{}"'.format(unique_id, alias))
        self.workspaces[unique_id] = core.WorkSpace(alias=alias, 
                                                    unique_id=unique_id, 
                                                    parent_directory=self.workspace_directory,
                                                    resource_directory=self.resource_directory, 
                                                    user_id=user_id)
    
    
    #==========================================================================
    def remove_test_user_workspaces(self):
        user_id = 'test_user'
        status = ['editable', 'readable', 'deleted']
        alias_id_list = self.uuid_mapping.get_alias_list_for_user(user_id, status=status)
        for alias in alias_id_list:
            print('DELETING:', alias)
            self.delete_workspace(user_id=user_id, alias=alias, permanently=True)
           
    
    #==========================================================================
    def request_subset_create(self, request):
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        "request" must contain: 
            user_id 
            workspace_uuid
            subset_uuid
            alias (for new subset)
        
        Returns a dict like:
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
            	"water_bodies": [
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

        """
        user_id = request['user_id']
        workspace_uuid = request['workspace_uuid']
        subset_uuid = request['subset_uuid']
        new_alias = request['alias']
        
        return_dict = self.copy_subset(user_id, 
                                       workspace_uuid=workspace_uuid, 
                                       subset_source_uuid=subset_uuid, 
                                       subset_target_alias=new_alias)
        if return_dict:
            subset_uuid = return_dict['uuid']
        else:
            subset_uuid = self.uuid_mapping.get_uuid(alias=new_alias, user_id=user_id)
        response = self.dict_subset(workspace_unique_id=workspace_uuid, 
                                   subset_unique_id=subset_uuid)
        
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
        workspace_uuid = request['workspace_uuid']
        subset_uuid = request['subset_uuid']
#        print('###', user_id)
#        print('###', alias)
#        print('###', source_uuid)
        
        workspace_alias = self.uuid_mapping.get_alias(workspace_uuid) 
        response = self.delete_subset(workspace_alias=workspace_alias, subset_unique_id=subset_uuid)
        
        return response
    
    #==========================================================================
    def request_subset_edit(self, request):
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        "request" and "response" is the output from a request_subset_list
        """
        workspace_uuid = request['workspace']['uuid']
        request_list = None
        if 'subsets' in request.keys():
            request_list = request['subsets']
        response = self.list_subsets(workspace_unique_id=workspace_uuid, request=request_list)
        
        return response
            
    #==========================================================================
    def request_subset_list(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
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
            			"water_bodies": [
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
        workspace_uuid = request['workspace_uuid'] 
        
        # Initiate structure 
        response = {'workspace': {}, 
                   'subsets': []}
        
        # Add workspace info
        workspace_dict = self.dict_workspace(unique_id=workspace_uuid)
                    
        response['workspace'] = workspace_dict
               
        subset_list = self.list_subsets(workspace_unique_id=workspace_uuid)
        
        # Add subset info   
        response['subsets'] = subset_list
               
        return response
               
    
    #==========================================================================
    def request_workspace_add(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        "request" must contain: 
            user_id (need this for copy of default_workspace)
            alias (for the new workspace)
            source (uuid)
        
        Returns a dict like:
            {
            	"alias": "My Workspace",
            	"uuid": "my_workspace",
            	"status": "editable"
            }
        """
        user_id = request['user_id']
        alias = request['alias'] 
        source_uuid = request['source'] 
#        print('###', user_id)
#        print('###', alias)
#        print('###', source_uuid)
        
        response = self.copy_workspace(user_id, source_uuid=source_uuid, target_alias=alias)
        
        return response
    
    
    #==========================================================================
    def request_workspace_delete(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        "request" must contain: 
            uuid 
        
        Returns a dict like:
            {
            	"alias": "My Workspace",
            	"uuid": "..."
            }
        """
        unique_id = request['uuid']
#        print('###', user_id)
#        print('###', alias)
#        print('###', source_uuid)
        
        alias = self.uuid_mapping.get_alias(unique_id)
        self.delete_workspace(unique_id=unique_id)
        
        response = {'alias': alias, 
                   'uuid': unique_id}
        
        return response
    
    
    #==========================================================================
    def request_workspace_edit(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        "request" must contain: 
            alias (new alias)
            uuid 
        
        Returns a dict like:
            {
            	"alias": "New Name",
            	"uuid": "..."
            }
        """
        alias = request['alias'] 
        unique_id = request['uuid'] 
        
        self.uuid_mapping.set_alias(unique_id, alias)
        alias = self.uuid_mapping.get_alias(unique_id, status=['editable', 'readable']) 
        
        response = {'alias': alias, 
                   'uuid': unique_id}
        
        return response
    
    #==========================================================================
    def request_workspace_list(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        "request" must contain: 
            user_id 
        
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
        
        user_id = request['user_id'] 
        
        response = {'workspaces': []}
        for unique_id in self.uuid_mapping.get_uuid_list_for_user(user_id, status=self.all_status):
            response['workspaces'].append(self.dict_workspace(unique_id=unique_id))
              
        response['workspaces'].append(self.dict_workspace(unique_id='default_workspace'))
        
#        response['workspaces'].append({'alias': 'default_workspace', 
#                                      'uuid': 'default_workspace',
#                                      'status': 'readable'})
                    
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
    
    
    #==========================================================================
    def set_data_filter(self, 
                        user_id, 
                        workspace_alias=None, 
                        step='', 
                        subset='', 
                        filter_type='', 
                        filter_name='', 
                        data=None): 
        """
        Created     20180220    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        Sets the data filter as described. 
        """
        assert all([workspace_alias, step, subset, filter_type, filter_name, data])
        workspace_object = self._get_workspace_object_from_alias(workspace_alias) 
        if not workspace_object:
            return False 
        
        return workspace_object.set_data_filter(step=step, 
                                                subset=subset, 
                                                filter_type=filter_type, 
                                                filter_name=filter_name, 
                                                data=data)
        
        
        
#"""
#===============================================================================
#===============================================================================
#===============================================================================
#"""     
#if __name__ == '__main__':
##    root_path = os.path.dirname(os.path.dirname(os.path.os.path.abspath(os.path.realpath(__file__))))
#    root_path = os.path.dirname(os.path.os.path.abspath(os.path.realpath(__file__)))
#    user_id = getpass.getuser()
#    ekos = EventHandler(root_path)
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
    

        
        
        
        
        
        
        
        
        
        