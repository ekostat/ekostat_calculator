# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 21:47:05 2017

@author: a002087
"""

import os
import shutil
import sys
import datetime
import core

class WorkSpace(object):
    """
    Class to load workspace
    Creates folder structure and necessary filter files
    """
    
    def __init__(self, name):
        self.name = name
        self.root_directory = os.path.dirname(os.path.abspath(__file__)).rstrip('\\core')
        if self.name not in os.listdir(self.root_directory + '\\workspaces'):
            print('Setting up new workspace named: {}'.format(name))
            self._folder_structure()
            self._default_settings()
        else:
            print('Using existing workspace named: {}'.format(name))
            self._check_folderstructure()
            self._check_settings()
        
    def _folder_structure(self):
        """
        Sets up the needed folder structure for the new workspace
        """
        self.paths = {}
        self.paths['current_workspace'] = self.root_directory + '\\workspaces\\' + self.name
        self.paths['filtered_data'] = os.makedirs(self.paths['current_workspace'] + '\\data\\filtered_data')
        self.paths['raw_data'] = os.makedirs(self.paths['current_workspace'] + '\\data\\raw_data')
        self.paths['selection_filters'] = os.makedirs(self.paths['current_workspace'] + '\\filters\\selection_filters')
        self.paths['tolerance_filters'] = os.makedirs(self.paths['current_workspace'] + '\\filters\\tolerance_filters')
        self.paths['results'] = os.makedirs(self.paths['current_workspace'] + '\\results')
        
    def _default_settings(self):
        """
        Gets default filter files (some with default filters defined some with only the structure of the file)
        """
        self.selection_filter_template =  shutil.copy(self.root_directory + '\\workspaces\\default\\filters\\selection_filters\\data_filter_template.txt', self.paths['selection_filters'])       
        self.tolerance_filter_template =  shutil.copy(self.root_directory + '\\workspaces\\default\\filters\\tolerance_filters\\tolerance_filter_template.txt', self.paths['tolerance_filters'])       
        
        
    def _check_folderstructure(self):
        #TODO: make check of workspace folder structure
        pass
    
    def _check_settings(self):
        #TODO: make checka of workspace settings
        pass
    
    