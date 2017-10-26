# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 21:47:05 2017

@author: a002087
"""

import os
import shutil
import sys
import datetime

#if current_path not in sys.path: 
#    sys.path.append(os.path.dirname(os.path.realpath(__file__)))
try:
    import core
except:
    pass

###############################################################################
class WorkSpace(object):
    """
    Class to load workspace
    Creates folder structure and necessary filter files
    """
    def __init__(self, name=None, parent_directory=None):
        if not all([name, parent_directory]): 
            return
        self.name = name 
        self.parent_directory = parent_directory 
        self.workspace_directory = '/'.join([self.parent_directory, self.name]) 
        
        self._load_attributes() 
        
        self._set_paths()
        
        print('Parent directory is: {}'.format(self.parent_directory))
        
        if not os.path.exists(self.workspace_directory): 
            print('Setting up empty workspace named: {}'.format(self.name))
            self._create_folder_structure() 
        else:
            print('Using existing workspace named: {}'.format(self.name))
            self._check_folderstructure() 
            self._create_file_paths()
            self.load_all_files()
    
    #==========================================================================
    def _load_attributes(self): 
        # Load attributes to be able to check what has been done
        self.first_filter = None
        self.raw_data = None 
        self.filtered_data = None 
        self.indicator_settings = {}
        
    #==========================================================================
    def _set_paths(self):
        self.directory_paths = {}
        #set paths
        self.directory_paths['data'] = self.workspace_directory + '/data'
        self.directory_paths['raw_data'] = self.workspace_directory + '/data/raw_data'
        self.directory_paths['filtered_data'] = self.workspace_directory + '/data/filtered_data'
        self.directory_paths['data_filters'] = self.workspace_directory + '/data_filters'
        self.directory_paths['settings'] = self.workspace_directory + '/settings'
        self.directory_paths['indicator_settings'] = self.workspace_directory + '/settings/indicator_settings'
        self.directory_paths['results'] = self.workspace_directory + '/results'
        
    #==========================================================================
    def _create_folder_structure(self):
        """
        Sets up the needed folder structure for the new workspace
        """
        for path in self.directory_paths.values():
            if not os.path.exists(path):
                os.makedirs(path)
        
    #==========================================================================
    def _create_file_paths(self): 
        
        # Indicator settings 
        self.indicator_settings_paths = {}
        for file_name in os.listdir(self.directory_paths['indicator_settings']): 
            if file_name.endswith('.set'):
                file_path = '/'.join([self.directory_paths['indicator_settings'], file_name]) 
                indicator = file_name.split('.')[0]
                self.indicator_settings_paths[indicator] = file_path
                
        # Data filters 
        self.data_filters_paths = {} 
        for file_name in os.listdir(self.directory_paths['data_filters']): 
            if file_name.endswith('.fil'):
                file_path = '/'.join([self.directory_paths['data_filters'], file_name]) 
                data_filter = file_name.split('.')[0]
                self.data_filters_paths[data_filter] = file_path 
                
        #TODO: What about data? 
        
    #==========================================================================
    def get_all_file_paths_in_worksapace(self):
        file_list = []
        for root, dirs, files in os.walk(self.workspace_directory): 
                for f in files:
                    file_list.append('/'.join([root, f]).replace('\\', '/'))
        return sorted(file_list)
    
    #==========================================================================
    def add_files_from_workspace(self, workspace_object=None, overwrite=False):
        """
        Copy files from given workspace. Opteion to overwrite or not. 
        """ 
        for from_file_path in workspace_object.get_all_file_paths_in_worksapace():
            to_file_path = from_file_path.replace(workspace_object.workspace_directory, self.workspace_directory) 
            if os.path.exists(to_file_path) and not overwrite:
                continue
            to_directory = os.path.dirname(to_file_path)
            if not os.path.exists(to_directory):
                # If directory has been added in later versions of the ekostat calculator
                os.makedirs(to_directory) 
            # Copy file
            shutil.copy(from_file_path, to_file_path)
        
        self._create_file_paths()
            
#        self.selection_filter_default =  shutil.copy(self.root_directory + '\\workspaces\\default\\filters\\selection_filters\\first_data_filter.txt', self.directory_paths['selection_filters'])       
#        self.tolerance_filter_default =  shutil.copy(self.root_directory + '\\workspaces\\default\\filters\\tolerance_filters\\tolerance_filter_template.txt', self.directory_paths['tolerance_filters'])       
#        self.first_filter = core.DataFilter('First filter', file_path = self.directory_paths['selection_filters']+'\\first_data_filter.txt')
        
    #==========================================================================
    def _check_folderstructure(self):
        #TODO: make check of workspace folder structure
        for key, item in self.directory_paths.items():
            if os.path.isdir(item):
                continue
            else:
                try:
                    # MW: Does not work for me in Spyder
                    raise('PathError')
                except:
                    pass
                print('no folder set for {}'.format(key))
        
    #==========================================================================
    def _save_ok(self):
        if self.name == 'default':
            print('Not allowed to save default workspace!')
            return False
        return True
    
    #==========================================================================
    def load_all_files(self): 
        self.load_data_filters()
        self.load_indicator_files()
        
    #==========================================================================
    def load_data_filters(self):
        # Load all settings file in the current WorkSpace filter folder... 
        self.data_filters = {} 
        for data_filter, file_path in self.data_filters_paths.items():
            self.data_filters[data_filter] = core.DataFilter(data_filter, file_path=file_path)

    #==========================================================================
    def load_indicator_files(self): 
        """
        Loads all types of settings, data and config files/objects. 
        """
        
        # All indicators in directory should be loaded automatically         
        # Load indicator setting files. Internal attr (_) since they are only used by other objects.  
        self._indicator_setting_files = {} 
        for indicator, file_path in self.indicator_settings_paths.items(): 
            self._indicator_setting_files[indicator] = core.SettingsFile(file_path)
            if self._indicator_setting_files[indicator].indicator != indicator:
                print('Missmatch in indicator name and ombejct name!')
            
        # Load Filter settings. Filter settings are using indicator_setting_files-obects as data
        self.indicator_filter_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_filter_settings[indicator] = core.SettingsFilter(obj)
            
        # Load Ref settings. Filter settings are using indicator_setting_files-obects as data
        self.indicator_ref_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_ref_settings[indicator] = core.SettingsRef(obj) 
            
        # Load Tolerance settings. Filter settings are using indicator_setting_files-obects as data
        self.indicator_tolerance_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_tolerance_settings[indicator] = core.SettingsTolerance(obj)
        
    #==========================================================================
    def get_indicator_settings_name_list(self):
        return sorted(self.indicator_settings.keys()) 
    
    #==========================================================================
    def save_indicator_settings(self, indicator): 
        if not self._save_ok(): 
            return 
        self.indicator_settings[indicator].save_file() # Overwrites existing file if no file_path is given
        return True 
    
    #==========================================================================
    def save_all_indicator_settings(self): 
        if not self._save_ok(): 
            return 
        all_ok = True
        for obj in self.indicator_settings.values():
            if not obj.save_file() :
                all_ok = False
        return all_ok
        
    #==========================================================================
    def load_data(self): 
        # Load all data in the current WorkSpace data folder...
        
        # ...for now load test data...
        raw_data_file_path = root_directory + '/test_data/raw_data/data_BAS_2000-2009.txt'
        
        
        self.raw_data = core.DataHandler('raw')
        self.raw_data.add_txt_file(raw_data_file_path, data_type='column') 
        
    #==========================================================================
    def apply_first_filter(self):
        # Use first filter 
        print('{}\nApplying first filter\n'.format('*'*nr_marks))
        
        self.filtered_data = self.raw_data.filter_data(self.first_filter) 
        
    #==========================================================================
    def update_filter_settings(self, indicator=None, filter_settings=None):
        """
        filter_settings are dicts like: 
            filter_settings[type_area][variable] = value 
        """
        if filter_settings: 
            filter_object = self.indicator_filter_settings[indicator] 
            filter_object.set_values(filter_settings) 
            
    #==========================================================================
    def show_settings(self):
        print('first_filter:')
        self.first_filter.show_filter()
    
    
    
###############################################################################
class WorkSpace_old(object):
    """
    Class to load workspace
    Creates folder structure and necessary filter files
    """
    
    def __init__(self, name = 'active workspace', root_directory=None):
        self.name = name
        if root_directory:
            self.root_directory = root_directory
        else:
#            self.root_directory = os.path.dirname(os.path.abspath(__file__))
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
                try:
                    # MW: Does not work for me in Spyder
                    raise('PathError')
                except:
                    pass
                print('no folder set for {}'.format(key))
    
    def _check_settings(self):
        #TODO: make check of workspace settings
        self.first_filter = core.DataFilter('First filter', file_path = self.paths['selection_filters']+'\\first_data_filter.txt')
        
    
    def show_settings(self):
        print('first_filter:')
        self.first_filter.show_filter()
    
    def first_filter(self):
        pass


if __name__ == '__main__':
    directory = 'D:/Utveckling/g_ekostat_calculator/ekostat_calculator_lena/workspaces/default'
    new_directory = 'D:/Utveckling/g_ekostat_calculator/ekostat_calculator_lena/workspaces/active_workspace'
    file_list = []
    new_file_list = []
    for root, dirs, files in os.walk(directory): 
#            print(root.replace('\\', '/'))
#             level = root.replace(directory, '').count(os.sep)
#             indent = ' ' * 4 * (level)
#             print('{}{}/'.format(indent, os.path.basename(root)))
#             subindent = ' ' * 4 * (level + 1)
            for f in files:
#                 file_list.append('/'.join([os.path.basename(root), f]))
                file_path = '/'.join([root, f]).replace('\\', '/')
                file_list.append(file_path) 
                new_file_path = file_path.replace(directory, new_directory)
                new_file_list.append(new_file_path)
                