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
        self.uuid_mapping = core.mapping.UUIDmapping('{}/uuid_mapping.txt'.format(self.workspace_directory))
        
    
    #==========================================================================
    def _change_ok(self, alias): 
        if alias in ['default_workspace', 'default_subset']: 
            self._logger.warning('Not allowed to make changes to "{}"!'.format(alias))
            return False
        return True
    
    
    #==========================================================================
    def _get_workspace_object_from_alias(self, alias): 
        unique_id = self.uuid_mapping.get_uuid(alias, user_id) 
        if not unique_id:
            return False
        return self.workspaces.get(unique_id, None)
    
    #==========================================================================
    def change_workspace_alias(self, user_id, current_alias, new_alias): 
        
        unique_id = self.uuid_mapping.get_uuid(current_alias, user_id) 
        if not unique_id:
            return False
        self.uuid_mapping.set_alias(unique_id, new_alias)
    
    
    #==========================================================================
    def copy_subset(self, user_id, workspace_alias=None, subset_source_alias=None, subset_source_uuid=None, subset_target_alias=None): 
        """
        Created     20180219    by Magnus Wenzer
        Updated     20180219    by Magnus Wenzer
        
        """
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
            subset_source_alias = self.uuid_mapping.get_alias(subset_source_uuid, user_id) 
            
        self._logger.debug('Trying to copy subset "{}". Copy has alias "{}"'.format(subset_source_alias, subset_target_alias))
        workspace_object.copy_subset(subset_source_alias, subset_target_alias)
        
        
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
        uuid_object = core.mapping.UUIDmapping(target_subset_uuid_mapping_file)
        
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
    def delete_subset(self, user_id, workspace_alias=None, subset_alias=None, permanently=False): 
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
        
        workspace_object.delete_subset(alias=subset_alias, permanently=permanently)
    
    
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
    def get_unique_id_for_alias(self, user_id, workspace_alias=None, subset_alias=None):
        if workspace_alias and subset_alias: 
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
    def get_workspace(self, user_id, alias=None, include_deleted=False): 
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
        workspace_object = self._get_workspace_object_from_alias(workspace_alias) 
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
            	"uid": "my_workspace",
            	"status": "editable"
            }
        """
        user_id = request['user_id']
        alias = request['alias'] 
        source_uuid = request['source'] 
#        print('###', user_id)
#        print('###', alias)
#        print('###', source_uuid)
        
        respons = self.copy_workspace(user_id, source_uuid=source_uuid, target_alias=alias)
        
        return respons
    
    
    #==========================================================================
    def request_workspace_delete(self, request):
        """
        Created     20180221    by Magnus Wenzer
        Updated     20180221    by Magnus Wenzer
        
        "request" must contain: 
            uid 
        
        Returns a dict like:
            {
            	"alias": "My Workspace",
            	"uid": "..."
            }
        """
        unique_id = request['uuid']
#        print('###', user_id)
#        print('###', alias)
#        print('###', source_uuid)
        
        alias = self.uuid_mapping.get_alias(unique_id)
        self.delete_workspace(unique_id=unique_id)
        
        respons = {'alias': alias, 
                   'uuid': unique_id}
        
        return respons
    
    
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
        
        respons = {'alias': alias, 
                   'uuid': unique_id}
        
        return respons
    
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
            			"uid": "my_workspace",
            			"status": "editable"
            		}
            	]
            }
        """
        user_id = request['user_id'] 
        
        respons = {'workspaces': []}
        for alias in self.uuid_mapping.get_alias_list_for_user(user_id, status=self.all_status):
            respons['workspaces'].append({'alias': alias, 
                                          'uuid': self.uuid_mapping.get_uuid(alias, user_id, self.all_status),
                                          'status': self.uuid_mapping.get_status(alias, user_id)})
                    
        respons['workspaces'].append({'alias': 'default_workspace', 
                                      'uuid': 'default_workspace',
                                      'status': 'readable'})
                    
        return respons
    
    
    
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
                        step='', subset='', 
                        filter_type='', 
                        filter_name='', 
                        data=None):
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
    

        
        
        
        
        
        
        
        
        
        