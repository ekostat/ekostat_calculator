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
    
    def __init__(self, name = 'active workspace'):
        self.name = name
#        self.root_directory = os.path.dirname(os.path.abspath(__file__))
        self.root_directory = os.path.join( os.path.dirname( __file__ ), '..' )
        self._set_paths()
        print(self.root_directory)
        if self.name not in os.listdir(self.root_directory + '\\workspaces'):
            print('Workspace directory: {}'.format(self.root_directory + '\\workspaces'))
            print('Setting up new workspace named: {}'.format(name))
            self._create_folder_structure()
            self._default_settings()
        else:
            print('Using existing workspace named: {}'.format(name))
            self._check_folderstructure()
            self._check_settings()
     
    def _set_paths(self):
        self.paths = {}
        self.paths['current_workspace'] = self.root_directory + '\\workspaces\\' + self.name
        #set paths
        self.paths['filtered_data'] = self.paths['current_workspace'] + '\\data\\filtered_data'
        self.paths['raw_data'] = self.paths['current_workspace'] + '\\data\\raw_data'
        self.paths['selection_filters'] = self.paths['current_workspace'] + '\\filters\\selection_filters'
        self.paths['tolerance_filters'] = self.paths['current_workspace'] + '\\filters\\tolerance_filters'
        self.paths['results'] = self.paths['current_workspace'] + '\\results'
        
    def _create_folder_structure(self):
        """
        Sets up the needed folder structure for the new workspace
        """

        #create directories
        os.makedirs(self.paths['filtered_data'])
        os.makedirs(self.paths['raw_data'])
        os.makedirs(self.paths['selection_filters'])
        os.makedirs(self.paths['tolerance_filters'])
        os.makedirs(self.paths['results'])
        
        
    def _default_settings(self):
        """
        Gets default filter files (some with default filters defined some with only the structure of the file)
        """
        self.selection_filter_default =  shutil.copy(self.root_directory + '\\workspaces\\default\\filters\\selection_filters\\first_data_filter.txt', self.paths['selection_filters'])       
        self.tolerance_filter_default =  shutil.copy(self.root_directory + '\\workspaces\\default\\filters\\tolerance_filters\\tolerance_filter_template.txt', self.paths['tolerance_filters'])       
        self.first_filter = core.DataFilter('First filter', file_path = self.paths['selection_filters']+'\\first_data_filter.txt')
        
    def _check_folderstructure(self):
        #TODO: make check of workspace folder structure
        for key, item in self.paths.items():
            if os.path.isdir(item):
                continue
            else:
                raise('PathError')
                print('no folder set for {}'.format(key))
    
    def _check_settings(self):
        #TODO: make check of workspace settings
        self.first_filter = core.DataFilter('First filter', file_path = self.paths['selection_filters']+'\\first_data_filter.txt')
        
    
    def show_settings(self):
        print('first_filter:')
        self.first_filter.show_filter()
    
    def first_filter(self):
        pass
    