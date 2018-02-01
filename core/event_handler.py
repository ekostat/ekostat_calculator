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
        
        for item in os.listdir(self.workspace_directory):
            self.add_workspace(item)
        
    #==========================================================================
    def add_workspace(self, workspace_name):
        self.workspaces[workspace_name] = core.WorkSpace(name=workspace_name, 
                                                       parent_directory=self.workspace_directory,
                                                       resource_directory=self.resource_directory)
    
    #==========================================================================
    def get_workspace(self, workspace_name): 
        return self.workspaces.get(workspace_name, None)
    
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
        
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        