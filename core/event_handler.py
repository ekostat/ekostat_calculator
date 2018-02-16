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

current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
if current_path not in sys.path:
    sys.path.append(current_path)

import core
"""
Module to handle all events linked to the Django application. 
Maybe this should be in the root? Maybe not a class, only functions? Maybe __name__ == "__main__"?

MW: Started this to start logging functionality. 
""" 

class EventHandler(object): 
    def __init__(self, root_path): 
        self.user_id = getpass.getuser()
        self.root_path = root_path.replace('\\', '/') 
        self.workspace_directory = self.root_path + '/workspaces'
        self.resource_directory = self.root_path + '/resources'
        
        self.log_directory = self.root_path + '/log'
        self.log_id = 'event_handler'
        
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
        
        
        for unique_id in os.listdir(self.workspace_directory):
            if '.' not in unique_id:
                self.load_workspace(unique_id, self.user_id)
        
    #==========================================================================
    def load_workspace(self, alias=None, unique_id=None, user_id=None): 
        """
        Copies the default workspace and sets ist to the given workspace_alias. 
        """
        if alias == 'default':
            unique_id = 'default'
        elif alias:
            unique_id = self.uuid_mapping.get_uuid(alias, self.user_id) 
        elif unique_id:
            alias = self.uuid_mapping.get_alias(unique_id, self.user_id)
            
        if not all([alias, unique_id]):
            self._logger.warning('Could not load workspace "{}" with alias "{}"'.format(unique_id, alias))
            return False
#        # Add UUID for workspace in uuid_mapping 
#        unique_id = self.uuid_mapping.add_new_uuid_for_alias(unique_id, user_id)
#        if not unique_id:
#            self._logger.debug('Could not add workspace with alias "{}". Workspace already exists!') 
#            return False
        
        # Create copy of default workspace
#        self.workspaces['default'].
        
        self.workspaces[unique_id] = core.WorkSpace(alias=alias, 
                                                    unique_id=unique_id, 
                                                    parent_directory=self.workspace_directory,
                                                    resource_directory=self.resource_directory)
    
    #==========================================================================
    def copy_workspace(self, source_alias=None, target_alias=None): 
        
        if source_alias == 'default':
            source_uuid = self.uuid_mapping.get_uuid(source_alias, 'default') 
        else:
            source_uuid = self.uuid_mapping.get_uuid(source_alias, self.user_id) 
            
        if not source_uuid:
            self._logger.warning('No alias named "{}"'.format(source_alias))
            return False
        
        # Add UUID for workspace in uuid_mapping 
        target_uuid = self.uuid_mapping.add_new_uuid_for_alias(target_alias, self.user_id)
        if not target_uuid:
            self._logger.debug('Could not add workspace with alias "{}". Workspace already exists!'.format(target_alias)) 
            return False
        
        # Copy all directories an files in workspace 
        source_workspace_path = '/'.join([self.workspace_directory, source_uuid])
        target_workspace_path = '/'.join([self.workspace_directory, target_uuid])
        
        print('source_workspace_path:', source_workspace_path)
        print('target_workspace_path:', target_workspace_path)
        
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
        
        uuid_list = uuid_object.get_uuid_list_for_user(self.user_id)
        for u_id in uuid_list:
            new_uuid = uuid_object.set_new_uuid(u_id)
            current_subset_path = '{}/subsets/{}'.format(target_workspace_path, u_id)
            new_subset_path = '{}/subsets/{}'.format(target_workspace_path, new_uuid)
            os.rename(current_subset_path, new_subset_path)
            
        # Add workspace
        self.workspaces[target_uuid] = core.WorkSpace(alias=target_alias, 
                                                      unique_id=target_uuid, 
                                                      parent_directory=self.workspace_directory,
                                                      resource_directory=self.resource_directory)
                        
        
    #==========================================================================
    def get_workspace(self, alias, user_id=None): 
        if not user_id:
            user_id = self.user_id
        # Get UUID for workspace 
        unique_id = self.uuid_mapping.get_uuid(alias, user_id)
        if not unique_id:
            return False
        # return matching workspace 
        return self.workspaces.get(unique_id, None)
    
    #==========================================================================
    def create_copy_of_workspace(self, from_workspace_name, to_workspace_name, overwrite=True): 
        
        if from_workspace_name not in self.workspaces.keys(): 
            self._logger.error('Trying to make copy of workspace "{}" workspace. This workspace is not loaded or non excisting!'.format(from_workspace_name))
            return False
        
        if to_workspace_name in self.workspaces.keys(): 
            self._logger.debug('Workspace "{}" already excists.'.format(to_workspace_name))
            return False
        
        self.workspaces[to_workspace_name] = self.workspaces[from_workspace_name].make_copy_of_workspace(to_workspace_name, overwrite=overwrite)
        self._logger.debug('create_copy_of_workspace from "{}" to "{}"'.format(from_workspace_name, to_workspace_name))
        
            
        
        
        
        
if __name__ == '__main__':
    root_path = os.path.dirname(os.path.dirname(os.path.os.path.abspath(os.path.realpath(__file__))))
    ekos = core.EventHandler(root_path)
    
    ekos.copy_workspace('default', 'mw')
    # default_workspace
#    default_workspace = ekos.get_workspace('default')
    

        
        
        
        
        
        
        
        
        
        