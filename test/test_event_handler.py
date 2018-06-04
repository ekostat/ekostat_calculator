# -*- coding: utf-8 -*-
"""
Created on Tue May 22 13:48:04 2018

@author: a001985
"""
import unittest 
import os 
import sys 
import time
import pandas as pd 
from pandas.util.testing import assert_frame_equal # <-- for testing dataframes
import pickle
#import core

#TEST_DIRECTORY = 'D:\\Utveckling\\git\\ekostat_calculator\\test'
TEST_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) 
TESTDATA_DIRECTORY = TEST_DIRECTORY + '/testdata'
BASE_DIRECTORY = os.path.dirname(TEST_DIRECTORY)
if BASE_DIRECTORY not in sys.path:
    sys.path.append(BASE_DIRECTORY)
    
#==============================================================================

import event_handler

#==============================================================================

#print(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
class TestEventHandler(unittest.TestCase): 
    """
    Created:        20180601     by Magnus
    Last modified:  
    """ 
    #==========================================================================
    @classmethod
    def setUpClass(self): 
        print('='*50)
        print('setUpClass in TestEventHandler')
        print('-'*50)
        self.paths = {'user_id': 'test_user', 
                      'workspace_directory': BASE_DIRECTORY + '/workspaces', 
                      'resource_directory': BASE_DIRECTORY + '/resources', 
                      'log_directory': BASE_DIRECTORY + '/log', 
                      'test_data_directory': BASE_DIRECTORY + '/test_data'}
        
        self.ekos = event_handler.EventHandler(**self.paths) 
        
        self.workspace_alias = 'test_workspace'
        self.ekos.copy_workspace(source_uuid='default_workspace', target_alias=self.workspace_alias)  
        
        
        self.workspace_uuid = self.ekos.get_unique_id_for_alias(self.workspace_alias)
        self.ekos.action_load_workspace(self.workspace_uuid)
        
        
        if LOAD_DEFAULT_DATA:
            self.ekos.action_workspace_load_default_data(self.workspace_uuid)
        
        file_names = ['physicalchemical_sharkweb_data_fyskem_wb_2007-2017_20180320.txt']
        for file_name in file_names: 
            self.ekos.set_status_for_datasource(workspace_unique_id=self.workspace_uuid, file_name=file_name, status=True)        
        
        
        self.ekos.load_data(unique_id=self.workspace_alias)
        
        print('-'*50)
        print(self.ekos.workspaces)
        print('-'*50)
    
    #==========================================================================
    @classmethod
    def tearDownClass(self):
        print('Using unique_id: {}'.format(self.workspace_uuid))
        
    #==========================================================================
    def setUp(self):
        self.ekos = event_handler.EventHandler(**self.paths) 
        print(self.ekos.user_id)
    
    #==========================================================================
    def tearDown(self):
        pass
    
    
    #==========================================================================
    def test_compare_all_data(self):
        self.ekos.action_load_workspace(self.workspace_uuid)
        print('='*50)
        print(self.ekos.workspaces)
        print('='*50)
        all_data = self.ekos.workspaces[self.workspace_uuid].data_handler.all_data
        
        directory = 'D:/Utveckling/git/ekostat_calculator/workspaces/{}/input_data/exports'.format(self.workspace_uuid)
        with open(directory + "/all_data.pkl", "rb") as fid:
            all_data_pkl = pickle.load(fid)
        all_data_txt = pd.read_csv(directory + "/all_data.txt", sep='\t', encoding='cp1252')
        
        assert_frame_equal(all_data, all_data_txt)
        assert_frame_equal(all_data, all_data_pkl)
       
        
        
class EKOS(): 
    """
    Created:        20180601     by Magnus
    Last modified:  
    """ 
    #==========================================================================
#    @classmethod
    def setUpClass(self): 
        print('='*50)
        print('setUpClass in TestEventHandler')
        print('-'*50)
        self.paths = {'user_id': 'test_user', 
                      'workspace_directory': BASE_DIRECTORY + '/workspaces', 
                      'resource_directory': BASE_DIRECTORY + '/resources', 
                      'log_directory': BASE_DIRECTORY + '/log', 
                      'test_data_directory': BASE_DIRECTORY + '/test_data'}
        
        self.ekos = event_handler.EventHandler(**self.paths) 
        
        self.workspace_alias = 'test_workspace'
        self.ekos.copy_workspace(source_uuid='default_workspace', target_alias=self.workspace_alias)  
        
        
        self.workspace_uuid = self.ekos.get_unique_id_for_alias(self.workspace_alias)
#        
        self.ekos.action_workspace_load_default_data(self.workspace_uuid)
#        
        file_names = ['physicalchemical_sharkweb_data_fyskem_wb_2007-2017_20180320.txt']
        for file_name in file_names: 
            print('AAAAAAAAAAAAAA', file_name)
            self.ekos.set_status_for_datasource(workspace_unique_id=self.workspace_uuid, file_name=file_name, status=True)        
            
        
        self.ekos.load_data(unique_id=self.workspace_uuid)
        
    def compare(self): 
        
        self.all_data = self.ekos.workspaces[self.workspace_uuid].data_handler.all_data
        
        self.directory = 'D:/Utveckling/git/ekostat_calculator/workspaces/{}/input_data/exports'.format(self.workspace_uuid)
        self.all_data_pkl = pickle.load(open(self.directory + "/all_data.pkl", "rb"))
        self.all_data_txt = pd.read_csv(self.directory + "/all_data.txt", sep='\t', encoding='cp1252')
        
#==============================================================================
#==============================================================================
#==============================================================================      
if __name__ == "__main__":
#    e = EKOS()
#    e.setUpClass()
    
    LOAD_DEFAULT_DATA = False
    
    unittest.main() 
    
    
    
"""   
#==============================================================================
Nice tutorial here:
https://www.youtube.com/watch?v=6tNS--WetLI 


# Context manager for testing exceptions
with self.assertRaises(ValueError):
    <func>(arg_1, arg_2)

#==============================================================================
"""