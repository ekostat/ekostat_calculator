# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 21:47:05 2017

@author: a002087
"""

import os
import shutil
import sys
import datetime
import codecs
import pandas as pd
import uuid
import re

current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
sys.path.append(current_path)

import core
"""
Module contains classes related to the structure of a workspace-directory. 
WorkSpace is the top class and contains one WorkStep-object representing step_0 
and one or several Subset-objects. Each Subset contains several WorkStep-objects 
for step_1, step_2....etc. 

All calls from outside this module should be made to the WorkSpace instance. 
If information in subsets or steps is needed the WorkSpace-class should be 
updated to retrieve this information (data should be passt on hierarchically in 
the data structure) 

Be aware that classes in this module are dependent on the directory and file 
structure of a Workspace. Altering the structure of the workspace directory  
tree 
"""

###############################################################################
class WorkStep(object):
    """
    A WorkStep holds information about the file structure in a step-directory 
    and contains all methodes operating on a specific workstep. 
    """
    def __init__(self, 
                 name=None, 
                 parent_directory=None, 
                 mapping_objects={}, 
                 parent_workspace_object=None, 
                 parent_subset_object=None):
        if not all([name, parent_directory]): 
            return 
        name = get_step_name(name)
        self.paths = {}
        self.name = name 
        self.paths['parent_directory'] = parent_directory 
        self.paths['step_directory'] = '/'.join([self.paths['parent_directory'], self.name]) 
        self.parent_workspace_object = parent_workspace_object
        self.parent_subset_object = parent_subset_object
        print('Initiating WorkStep: {}'.format(self.paths['step_directory']))
        
        """ 
        Input argument mapping_objects is a dictionary since there might be several mapping objects in the future. 
        We do not want to (?) load mapping objects individually in each sub-object to save memory. 
        """
        self.mapping_objects = mapping_objects 
        
        self._initiate_attributes()
        
        self._set_directories()
        
        self._create_folder_structure()
        self.load_all_files()
        self._check_folder_structure()        
        
    #==========================================================================
    def _create_folder_structure(self):
        """
        Sets up the needed folder structure for the workstep. 
        Folders are added if they dont exist. 
        """
        if not os.path.exists(self.paths['step_directory']): 
            os.makedirs(self.paths['step_directory'])
            
        for path in self.paths['directory_paths'].values():
            if not os.path.exists(path):
                os.makedirs(path)
        
    #==========================================================================
    def _create_file_paths(self): 
        """
        Builds file paths for: 
            indicator_settings
        """
        self.paths['indicator_settings_paths'] = {}
        for file_name in os.listdir(self.paths['directory_paths']['indicator_settings']): 
            if file_name.endswith('.set'):
                file_path = '/'.join([self.paths['directory_paths']['indicator_settings'], file_name])
                indicator = file_name.split('.')[0]
                self.paths['indicator_settings_paths'][indicator] = file_path
        
    #==========================================================================
    def _check_folder_structure(self):
        #TODO: make check of workspace folder structure
        all_ok = True
        for key, item in self.paths['directory_paths'].items():
            if os.path.isdir(item):
                continue
            else:
                all_ok = False
                try:
                    # MW: Does not work for me in Spyder
                    raise('PathError')
                except:
                    pass
                print('no folder set for: {}'.format(item))
                
        return all_ok
        
    #==========================================================================
    def _initiate_attributes(self): 
        """
        Load attributes 
        """
        self.data_filter = None
        self.indicator_settings = {} 
        
        self.allowed_data_filter_steps = ['step_0', 'step_1']
        self.allowed_indicator_settings_steps = ['step_2'] 
        
        
    #==========================================================================
    def _change_ok(self): 
        """
        Check to make sure that the default 
        """
        if self.parent_subset_object and self.parent_workspace_object.name == 'default':
            print('Not allowed to change default workspace!')
            return False
        elif self.parent_subset_object and self.parent_subset_object.name == 'default_subset':
            print('Not allowed to change default subset!')
            return False
        return True
    
    #==========================================================================
    def _set_directories(self):
        #set paths
        self.paths['directory_paths'] = {}
        self.paths['directory_paths']['data_filters'] = self.paths['step_directory'] + '/data_filters'
        self.paths['directory_paths']['settings'] = self.paths['step_directory'] + '/settings'
        self.paths['directory_paths']['indicator_settings'] = self.paths['step_directory'] + '/settings/indicator_settings'
        self.paths['directory_paths']['output'] = self.paths['step_directory'] + '/output'
        self.paths['directory_paths']['results'] = self.paths['step_directory'] + '/output/results'
    
    #==========================================================================
    def add_files_from_workstep(self, step_object=None, overwrite=False):
        """
        Copy files from given workstep. Option to overwrite or not. 
        This method shold generaly be used when copying step_0 or a whole subset. 
        DONT USE FOR COPYING SINGLE STEPS NUMBERED 1 and up. 
        """ 
        for from_file_path in step_object.get_all_file_paths_in_workstep():
            to_file_path = from_file_path.replace(step_object.paths['step_directory'], self.paths['step_directory']) 
            if os.path.exists(to_file_path) and not overwrite:
                continue
            to_directory = os.path.dirname(to_file_path)
            if not os.path.exists(to_directory):
                # If directory has been added in later versions of the ekostat calculator
                os.makedirs(to_directory) 
            # Copy file
            shutil.copy(from_file_path, to_file_path)
        
        self.load_all_files()    
            
        
    #==========================================================================
    def get_all_file_paths_in_workstep(self): 
        """
        Returns a sorted list of all file paths in the workstep tree. 
        Generally this method is used when copying the workstep. 
        """
        file_list = []
        for root, dirs, files in os.walk(self.paths['step_directory']): 
                for f in files:
                    file_list.append('/'.join([root, f]).replace('\\', '/'))
        return sorted(file_list)
    
    #==========================================================================
    def get_data_filter_object(self): 
        if self.name not in self.allowed_data_filter_steps:
            return False
        return self.data_filter
    
    #==========================================================================
    def get_data_filter_info(self): 
        """
        Returns a dict with data filter names as keys. 
        Every key contains a list of the active filters. 
        """
        self.data_filter.get_filter_info()
        
    #==========================================================================
    def get_indicator_data_filter_settings(self, indicator): 
        """
        Returns the data filter settings for the given indicator. 
        """
        if self.name not in self.allowed_indicator_settings_steps:
            return False
        return self.indicator_data_filter_settings.get(indicator, False)
    
    #==========================================================================
    def get_indicator_tolerance_settings(self, indicator): 
        """
        Returns the tolerance settings for the given indicator. 
        """
        if self.name not in self.allowed_indicator_settings_steps:
            return False
        return self.indicator_tolerance_settings.get(indicator, False)
    
    #==========================================================================
    def get_indicator_ref_settings(self, indicator): 
        """
        Returns the reference settings for the given indicator. 
        """
        if self.name not in self.allowed_indicator_settings_steps:
            return False
        return self.indicator_ref_settings.get(indicator, False)
    
    #==========================================================================
    def get_indicator_settings_name_list(self):
        return sorted(self.indicator_settings.keys())
    
    #==========================================================================
    def load_all_files(self): 
        self._create_file_paths()
        self.load_data_filter()
        self.load_indicator_settings_filters()
        
    #==========================================================================
    def load_data_filter(self):
        """
        Load all settings files in the current WorkSpace filter folder... 
        """
        self.data_filter = core.DataFilter(self.paths['directory_paths']['data_filters'], 
                                           mapping_objects=self.mapping_objects) 
        

    #==========================================================================
    def load_indicator_settings_filters(self): 
        """
        Loads all types of settings, data and config files/objects. 
        """
        
        # All indicators in directory should be loaded automatically         
        # Load indicator setting files. Internal attr (_) since they are only used by other objects.  
        self._indicator_setting_files = {} 
        for indicator, file_path in self.paths['indicator_settings_paths'].items(): 
            self._indicator_setting_files[indicator] = core.SettingsFile(file_path, mapping_objects=self.mapping_objects)
            if self._indicator_setting_files[indicator].indicator != indicator:
                print('Missmatch in indicator name and object name! {}:{}'.format(self._indicator_setting_files[indicator].indicator, indicator))
            
        # Load Filter settings. Filter settings are using indicator_setting_files-objects as data
        self.indicator_data_filter_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_data_filter_settings[indicator] = core.SettingsDataFilter(obj)
            
        # Load Ref settings. Filter settings are using indicator_setting_files-objects as data
        self.indicator_ref_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_ref_settings[indicator] = core.SettingsRef(obj) 
            
        # Load Tolerance settings. Filter settings are using indicator_setting_files-objects as data
        self.indicator_tolerance_settings = {} 
        for indicator, obj in self._indicator_setting_files.items():
            self.indicator_tolerance_settings[indicator] = core.SettingsTolerance(obj)
            
    #==========================================================================
    def set_indicator_settings_data_filter(self, indicator=None, filter_settings=None):
        """
        filter_settings are dicts like: 
            filter_settings[type_area][variable] = value 
        """
        if not self._change_ok(): 
            return 
        if filter_settings: 
            filter_object = self.indicator_data_filter_settings[indicator] 
            filter_object.set_values(filter_settings) 
        
    #==========================================================================
    def deprecated_save_indicator_settings(self, indicator): 
        if not self._change_ok(): 
            return 
        self.indicator_settings[indicator].save_file() # Overwrites existing file if no file_path is given
        return True 
    
    #==========================================================================
    def deprecated_save_all_indicator_settings(self): 
        if not self._change_ok(): 
            return 
        all_ok = True
        for obj in self.indicator_settings.values():
            if not obj.save_file() :
                all_ok = False
        return all_ok
        
    #==========================================================================
    def rename_paths(self, from_name, to_name, pre_directory=''): 
        """
        Replaces string in all file paths. 
        """
        for name in self.paths.keys(): 
            if type(self.paths[name]) == dict:
                for sub_name in self.paths[name].keys():
                    self.paths[name][sub_name] = get_new_path(from_name, to_name, self.paths[name][sub_name], pre_directory)
            else:
                self.paths[name] = get_new_path(from_name, to_name, self.paths[name], pre_directory) 
            
    #==========================================================================
    def print_all_paths(self): 
        """
        Prints all path in the step.
        """
        sep_length = 100
        print('='*sep_length)
        print('='*sep_length)
        print('{} paths'.format(self.name))
        print('-'*sep_length)
        for item in sorted(self.paths.keys()):
            if type(self.paths[item]) == dict:
                for path in sorted(self.paths[item].keys()):
                    if type(self.paths[item][path]) == dict:
                        for p in sorted(self.paths[item][path].keys()):
                            print('-', self.paths[item][path][p])
                    else:
                        print(self.paths[item][path])
            else:
                print(self.paths[item])
                
        print('')
                
    #==========================================================================
    def set_data_filter(self, filter_type='', filter_name='', data=None, save_filter=True): 
        """
        Sets the data_filter. See core.filters.data_filter.set_filter for more information. 
        """ 
        if not self._change_ok(): 
            return 
        data_filter = self.get_data_filter_object() 
        data_filter.set_filter(filter_type=filter_type, 
                               filter_name=filter_name, 
                               data=data, 
                               save_filter=save_filter)    
        return True
            
    #==========================================================================
    def show_settings(self):
        print('first_filter:')
        self.data_filter.show_filter()
        
        
###############################################################################
class Subset(object):
    """
    Class to hold subset paths and objects. 
    """
    def __init__(self, 
                 name=None, 
                 parent_directory=None, 
                 mapping_objects={}, 
                 parent_workspace_object=None): 
        assert all([name, parent_directory])
        self.name = name 
        self.paths = {}
        self.paths['parent_directory'] = parent_directory.replace('\\', '/')
        self.paths['subset_directory'] = '/'.join([self.paths['parent_directory'], self.name]) 
        self.parent_workspace_object = parent_workspace_object
        print('-'*100)
        print('Initiating Subset: {}'.format(self.paths['subset_directory'])) 
        
        self.mapping_objects = mapping_objects
        
        self._initiate_attributes()
        self._load_steps() 
        
        self._load_subset_config()
        
        
    #==========================================================================
    def _initiate_attributes(self): 
        self.nr_steps = 5
        self.steps = {}
            
    #==========================================================================
    def _change_ok(self): 
        """
        Check to make sure that the default 
        """
        if self.parent_subset_object and self.parent_workspace_object.name == 'default':
            print('Not allowed to change default workspace!')
            return False
        elif self.name == 'default_subset':
            print('Not allowed to change default subset!')
            return False
        return True
    
    #==========================================================================
    def _load_subset_config(self): 
        self.config = Config(self.paths['subset_directory'] + '/subset.cfg')
        
    #==========================================================================
    def _load_steps(self): 
        if not os.path.exists(self.paths['subset_directory']): 
            os.makedirs(self.paths['subset_directory'])
        step_list = [item for item in os.listdir(self.paths['subset_directory']) if '.' not in item]
        print('step_list', step_list)
        for step in step_list:
            self._load_workstep(step)
        
    #==========================================================================
    def _add_files_from_subset(self, subset_object=None, overwrite=False):
        """
        Copy files from given subset. Option to overwrite or not. 
        This method is used to copy (branching) an entire subset. 
        """ 
        for step in subset_object.get_step_list(): 
            print('step:', step)
            self._load_workstep(step)
            step_object = subset_object.get_step_object(step)
            self.steps[step].add_files_from_workstep(step_object=step_object, 
                                                     overwrite=overwrite)
            
        # Copy config file
        # This is done in Workspace since new uuid needs to be given
#        if os.path.exists(subset_object.config_file_path):
#            if os.path.exists(self.config_file_path) and not overwrite: 
#                return False 
#            
#            shutil.copy(subset_object.config_file_path, self.config_file_path)
#            self._load_config()
        return True
            
            
    #==========================================================================
    def _load_workstep(self, step=None): 
        step = get_step_name(step)
        if not step:
            return False
        
        self.steps[step] = WorkStep(name=str(step), 
                                    parent_directory=self.paths['subset_directory'], 
                                    mapping_objects=self.mapping_objects, 
                                    parent_workspace_object=self.parent_workspace_object, 
                                    parent_subset_object=self)
        return True
        
    #==========================================================================
    def deprecated_delete_workstep(self, step=None): 
        """
        step is like 'step_1', 'step_2' and so on. 
        """
        if step in self.subset_dict.keys(): 
            # TODO: Delete files and directories. How to make this safe? 
            self.steps.pop(step)
    
    #==========================================================================
    def deprecated_get_alias(self): 
        alias = self.config.get_config('alias') 
        if not alias:
            return '' 
        
    #==========================================================================
    def _set_unique_id(self): 
        """
        Sets a unique id (UUID) to the subset. Will not overwrite an existing one. 
        """
        self.unique_id = self.config.set_unique_id()  
        
    #==========================================================================
    def get_unique_id(self): 
        return self.unique_id 
        
    #==========================================================================
    def get_all_file_paths_in_subset(self): 
        """
        Returns a sorted list of all file paths in the subset tree. 
        """
        file_list = []
        for root, dirs, files in os.walk(self.paths['subset_directory']): 
                for f in files:
                    file_list.append('/'.join([root, f]).replace('\\', '/'))
        return sorted(file_list)

    #==========================================================================
    def get_data_filter_info(self, step): 
        """
        Returns a dict with information about the active filters. 
        """
        data_filter = self.get_data_filter_object(step)
        if not data_filter:
            return False
        return data_filter.get_data_filter_info()
    
    #==========================================================================
    def get_data_filter_object(self, step): 
        """
        Returns the data filter for the given step. 
        """
        step = get_step_name(step)
        if step not in self.get_step_list():
            return False 
        return self.steps[step].data_filter 
    
    #==========================================================================
    def get_step_list(self): 
        return sorted(self.steps.keys())
    
    #==========================================================================
    def get_step_object(self, step): 
        step = get_step_name(step)
        return self.steps.get(step, False)
        
    #==========================================================================
    def get_step_1_object(self): 
        return self.get_step_object('step_1')
    
    #==========================================================================
    def get_step_2_object(self): 
        return self.get_step_object('step_2')
    
    #==========================================================================
    def load_data(self, step): 
        if step not in self.steps.keys():
            print('Invalid step "{}" given to load data in subset "{}"!'.format(step, self.name))
            return False 
            
        self.steps[step].load_data()
    
    #==========================================================================
    def deprecated_set_alias(self, alias):
        print('New alias for subset "{}" => "{}"'.format(self.config.get_config('alias'), alias))
        self.config.set_config('alias', alias)
        
    #==========================================================================
    def rename_paths(self, from_name, to_name, pre_directory=''): 
        
        for name in self.paths.keys(): 
            if type(self.paths[name]) == dict:
                for sub_name in self.paths[name].keys():
                    self.paths[name][sub_name] = get_new_path(from_name, to_name, self.paths[name][sub_name], pre_directory)
            else:
                self.paths[name] = get_new_path(from_name, to_name, self.paths[name], pre_directory)


    #==========================================================================
    def rename_subset(self, new_name): 
        if new_name.lower() in ['subset', 'default_subset']: 
            print('Invalid name "{}" for subset!'.format(new_name))
            return False 
        
        current_directory = self.paths['subset_directory']
        new_directory = '{}/{}'.format(self.paths['parent_directory'], new_name)
        
        # Rename all paths in subset 
        self.rename_paths(self.name, new_name, pre_directory='subsets')
        
        # Rename paths in steps 
        for step in self.steps.keys(): 
            self.steps[step].rename_paths(self.name, new_name, pre_directory='subsets') 
        
        # Rename directoy
        os.rename(current_directory, new_directory) 
        
        # Set path in config file 
        self.config.set_path(self.name, new_name, pre_directory='subsets')
        
        self.name = new_name
        
        return True 
    
    #==========================================================================
    def rename_workspace(self, from_name, to_name): 
        
        # Rename all paths in subset 
        self.rename_paths(from_name, to_name, pre_directory='workspaces')
        
        # Rename paths in steps 
        for step in self.steps.keys(): 
            self.steps[step].rename_paths(from_name, to_name, pre_directory='workspaces')  
            
        # Set path in config file 
        self.config.set_path(from_name, to_name, pre_directory='workspaces')
        
        return True
            
    #==========================================================================
    def print_all_paths(self): 
        """
        Prints all path in the subset.
        """
        sep_length = 100
        print('='*sep_length)
        print('='*sep_length) 
        print('Subset {} paths'.format(self.name))
        print('-'*sep_length)
        for item in sorted(self.paths.keys()):
            if type(self.paths[item]) == dict:
                for path in sorted(self.paths[item].keys()):
                    if type(self.paths[item][path]) == dict:
                        for p in sorted(self.paths[item][path].keys()):
                            print('-', self.paths[item][path][p])
                    else:
                        print(self.paths[item][path])
            else:
                print(self.paths[item])
            
        for step in sorted(self.steps.keys()):
            self.steps[step].print_all_paths() 
        
        print('')
                
    #==========================================================================
    def set_data_filter(self, step='', filter_type='', filter_name='', data=None, save_filter=True):  
        step_object = self.get_step_object(step)
        if not step_object:
            return False 
        return step_object.set_data_filter(filter_type=filter_type, filter_name=filter_name, data=data, save_filter=save_filter)
    
    
    
            

###############################################################################
class WorkSpace(object):
    """
    Class to hold and alter a workspace. 
    Holds step_0 and subsets. 
    """
    def __init__(self, 
                 name=None, 
                 parent_directory=None, 
                 resource_directory=None,
                 nr_subsets_allowed=4): 
        
        assert all([name, parent_directory])
        assert nr_subsets_allowed
        
        # Initiate paths 
        self.paths = {}
        self.name = name 
        self.paths['parent_directory'] = parent_directory.replace('\\', '/')
        self.paths['resource_directory'] = resource_directory.replace('\\', '/')
        self.nr_subsets_allowed = nr_subsets_allowed
         
        self._initiate_attributes()
        
        self._setup_workspace()
        self._load_config_files()
            
    #==========================================================================
    def _initiate_attributes(self): 
        # Setup default paths 
        self.paths['mapping_directory'] = '/'.join([self.paths['resource_directory'], 'mappings'])
        self.paths['workspace_directory'] = '/'.join([self.paths['parent_directory'], self.name]) 
        print('')
        print('='*100)
        print('Initiating WorkSpace: {}'.format(self.paths['workspace_directory'])) 
        print('Parent directory is: {}'.format(self.paths['parent_directory']))
        print('Resource directory is: {}'.format(self.paths['resource_directory']))
        
        self.paths['directory_path_subsets'] = {}
        self.paths['directory_path_input_data'] = self.paths['workspace_directory'] + '/input_data'
        self.paths['directory_path_raw_data'] = self.paths['directory_path_input_data'] + '/raw_data'
        self.paths['directory_path_subset'] = self.paths['workspace_directory'] + '/subsets'
        
        # Step
        self.step_0 = None 
        
        # Subset
        self.subset_dict = {} 
        
        # Mapping objects 
        self.mapping_objects = {}
        self.mapping_objects['water_body'] = core.WaterBody(file_path=self.paths['mapping_directory'] + '/water_body_match.txt')
        
    #==========================================================================
    def _change_ok(self): 
        """
        Check to make sure that default workspace is not changed. 
        """
        if self.name == 'default':
            print('Not allowed to change default workspace!')
            return False
        return True
        
    #==========================================================================
    def _setup_workspace(self):
        """
        Adds paths and objects for the workspace. 
        """        
        # Create input data folder if non existing
        if not os.path.exists(self.paths['directory_path_raw_data']):
            os.makedirs(self.paths['directory_path_raw_data'])
            
        # Create raw data folder if non existing
        if not os.path.exists(self.paths['directory_path_input_data']):
            os.makedirs(self.paths['directory_path_input_data'])
        
        # Initiate one subset as default 
        if not os.path.exists(self.paths['directory_path_subset']):
            os.makedirs(self.paths['directory_path_subset'])
            
        subsets = os.listdir(self.paths['directory_path_subset'])
#        print('subsets', subsets)
        if subsets:
            for s in subsets:
                self._add_subset(s)
        else:
            self._add_subset('default_subset')
            
        # Load config file 
        self._load_workspace_config()
            
        # Step 0
        self.step_0 = WorkStep(name='step_0', 
                               parent_directory=self.paths['workspace_directory'], 
                               mapping_objects=self.mapping_objects, 
                               parent_workspace_object=self)
        
        # Set data and index handler
        self.data_handler = core.DataHandler(input_data_directory=self.paths['directory_path_input_data'], 
                                             resource_directory=self.paths['resource_directory'])
        
        self.index_handler = core.IndexHandler(workspace_object=self, 
                                               data_handler_object=self.data_handler)
        
    #==========================================================================
    def _load_config_files(self):       
        
        self.cf_df = pd.read_csv(self.paths['resource_directory'] + '/Quality_Elements.cfg', sep='\t', dtype='str', encoding='cp1252')
        assert all(['quality element' in self.cf_df.keys(), 'indicator' in self.cf_df.keys(), 'parameters' in self.cf_df.keys()]), 'configuration file must contain quality element, indicator and parameters information'
        self.cfg = {}
        self.cfg['quality elements'] = self.cf_df.groupby('quality element')['indicator'].unique()
        self.cfg['indicators'] = self.cf_df.groupby('indicator')['parameters'].unique()
#        for QE in self.cfg['quality elements']:
#            self.cfg[QE] = self.cf_df.groupby(QE)['indicator'].unique()
#        for indicator in self.cfg['indicators']:
#            self.cfg[indicator] = self.cf_df.groupby(QE)['parameters'].split(',')     

    #==========================================================================
    def _load_workspace_config(self): 
        self.config = Config(self.paths['workspace_directory'] + '/workspace.cfg')   

    #==========================================================================
    def import_file(self, file_path=None, data_type=None):
        """
        Imports a data file to the raw_data directory in the workspace. 
        Also adds information to the dtype_settings-object. 
        """ 
        assert all([file_path, data_type]), 'Not enough input arguments to import file' 
                  
        if not os.path.exists(file_path):
            return False 
        
        # Copy file
        target_file_path = '/'.join([self.paths['directory_path_raw_data'], os.path.basename(file_path)])
        shutil.copyfile(file_path, target_file_path)
        
        # Add file to dtype_settings file
        self.dtype_settings.add_file(file_path=file_path, data_type=data_type)

    #==========================================================================
    def import_default_data(self, force=False):
        """
        Imports default data from the resources directory to input raw_data directory in workspace.
        """
        # Not able to load data into default workspace
        if not self._change_ok():
            return False
        
        if os.listdir(self.paths['directory_path_raw_data']): 
            if not force:
                print('raw_data directory is not empty. Will not copy default files from resource directory!')
                return False
        
        source_directory = self.paths['resource_directory'] + '/default_data'  
        
        
        file_name_list = os.listdir(source_directory)
        
        # copy files
        for file_name in file_name_list: 
            src = '/'.join([source_directory, file_name])
            tar = '/'.join([self.paths['directory_path_raw_data'], file_name])
            shutil.copyfile(src, tar)
            
        # Load data 
        self.load_all_data() 
        
        # Update dtype_settings object
        all_ok = self.dtype_settings.load_and_sync_dtype_settings()
        
        if not all_ok:
            print('Default data not loaded correctly!')
            return False
        return True
        
    #==========================================================================
    def make_copy_of_workspace(self, workspace_name='', overwrite=False): 
        """
        Makes a copy of the workspace and loads all data and settings files. 
        
        Input: 
            workspace_name - name of the new workspace 
            overwrite - Tue/False
        Return: 
            workspace object for the new workspace
            Returns False if something went wrong 
        """ 
        
        # Initiating workspace
        new_workspace_path = '/'.join([self.paths['parent_directory'], workspace_name])
        if os.path.exists(new_workspace_path): 
            print('New workspace already excists!')
            return False
        new_workspace_object = core.WorkSpace(name=workspace_name, 
                                              parent_directory=self.paths['parent_directory'],
                                              resource_directory=self.paths['resource_directory']) 
        
        # Copy files to new workspace
        new_workspace_object._add_files_from_workspace(self, overwrite=overwrite)
        
        # Load data in workspace 
        data_loaded = new_workspace_object.load_all_data()
        
        if data_loaded:
            print('Data loaded!')
        else:
            print('No data to load! Consider loading default data by calling <workspace_objetc>.load_default_data()')
            
        # Load config files. One for workspace and one for each subset. 
        # The config file are copies of the existing ones but with new uuid 
        # Workspace config 
        des_path = new_workspace_object.config.file_path 
        new_workspace_object.config = self.config.make_copy_of_config(des_path)
        print(self.name)
        print(new_workspace_object.name)
        # Subset configs
        for subset in new_workspace_object.subset_dict.keys(): 
            des_path = new_workspace_object.subset_dict[subset].config.file_path
            new_workspace_object.subset_dict[subset].config = self.subset_dict[subset].config.make_copy_of_config(des_path)
        
        return new_workspace_object
        
        
    #==========================================================================
    def _add_files_from_workspace(self, workspace_object=None, overwrite=False):
        """
        Copy files from given workspace. Option to overwrite or not. 
        This method is used when copy an entire workspace. 
        """ 
        # Step 0
        if workspace_object.step_0: 
            self.step_0 = WorkStep(name='step_0', 
                          parent_directory=self.paths['workspace_directory'], 
                          mapping_objects=self.mapping_objects, 
                          parent_workspace_object=self) 
            self.step_0.add_files_from_workstep(step_object=workspace_object.step_0, 
                                                overwrite=overwrite)
                
        # Subsets
        for subset in workspace_object.get_subset_list():
            self._add_subset(subset)
            self.subset_dict[subset]._add_files_from_subset(subset_object=workspace_object.subset_dict[subset], 
                                                           overwrite=overwrite)
            
        # Data         
        for from_file_path in workspace_object.get_all_file_paths_in_input_data():
            to_file_path = from_file_path.replace(workspace_object.paths['workspace_directory'], self.paths['workspace_directory'])
            if os.path.exists(to_file_path) and not overwrite:
                continue
            to_directory = os.path.dirname(to_file_path)
            if not os.path.exists(to_directory):
                # If directory has been added in later versions of the ekostat calculator
                os.makedirs(to_directory)
            # Copy file
            shutil.copy(from_file_path, to_file_path)
        
    #==========================================================================
    def _add_subset(self, sub=None): 
        assert sub, 'No subset name given!'
        if sub in self.subset_dict.keys():
            print('Given subset is already present!')
            return False
        
#        print('== {}'.format(sub))
        self.paths['directory_path_subsets'][sub] = self.paths['directory_path_subset'] + '/{}'.format(sub)
        self.subset_dict[sub] = Subset(name=sub, 
                                       parent_directory=self.paths['directory_path_subset'],
                                       mapping_objects=self.mapping_objects, 
                                       parent_workspace_object=self)
        return sub 
    
    #==========================================================================
    def _load_workstep(self, subset=None, step=None): 
        subset_object = self.get_subset_object(subset) 
        if not subset_object:
            return False 
        return subset_object._load_workstep(step)
        
    #==========================================================================
    def deprecated_apply_data_filter_step_0(self): 
        """
        Applies the first filter to the index_handler. 
        """
        all_ok = self.index_handler.add_filter(filter_object=self.step_0.data_filter, step='step_0')
        return all_ok
        
    #==========================================================================
    def deprecated_apply_subset_data_filter(self, subset):
        """
        Applies the data filter for the given subset. 
        This is not fully handled by the index_handler. 
        Filter is applyed in step 1.
        """
        if subset not in self.get_subset_list():
            return False
        sub_object = self.get_step_1_object(subset)
        all_ok = self.index_handler.add_filter(filter_object=sub_object.data_filter, filter_step=1, subset=subset)
        return all_ok
    
    #==========================================================================
    def apply_data_filter(self, step=None, subset=None):
        """
        Applies data filter to the index handler. 
        
        Input: 
            step:           step that the data filter should be applied on. 
                            data_filter can be applied on step 0, 1 and 2
                            
            subset:         subset to apply filter on. Must be provided if step is > 0 
        
        Output: 
            True:           If all is ok
            False:          If something faild
        """
        
        step = get_step_name(step)
        if step == 'step_0':
            filter_object = self.step_0.data_filter
            
        elif int(step[-1]) > 2: 
            print('No data filter in {}'.format(step))
            return False
        
        elif subset not in self.get_subset_list(): 
            print('Provides subset "{}" not in subset list'.format(subset))
            return False
        else:
            subset_object = self.get_subset_object(subset) 
            step_object = subset_object.get_step_object(step)
            filter_object = step_object.get_data_filter_object() 
            
        all_ok = self.index_handler.add_filter(filter_object=filter_object, step=step, subset=subset)
        return all_ok
        
    #==========================================================================
    def apply_indicator_dator_filter(self, subset=None, indicator=None, step=2):
        """
        Applies indicator data filter to the index handler. Step. 
        
        Input:                
            subset:         subset to apply filter on. 
            
            indicator:      name of indicator to apply, ex. "din_winter"
            
            step:           step_2 is default
        
        Output: 
            True:           If all is ok
            False:          If something faild
        """
        
        if subset not in self.get_subset_list(): 
            print('Provides subset "{}" not in subset list'.format(subset))
            return False
        else:
            subset_object = self.get_subset_object(subset) 
            # Indicator_settings are linked to step 2 by default
            step_object = subset_object.get_step_object(step) 
            filter_object = step_object.get_indicator_data_filter_settings(indicator) 
            
        all_ok = self.index_handler.add_filter(filter_object=filter_object, step=step, subset=subset, indicator=indicator)
        return all_ok
        
    #==========================================================================
    def copy_subset(self, source_subset_name=None, target_subset_name=None): 
        assert all([source_subset_name, target_subset_name])
        if not self._add_subset(sub=target_subset_name):
            return False
        all_ok = self.subset_dict[target_subset_name]._add_files_from_subset(self.subset_dict[source_subset_name], overwrite=True) 
        if not all_ok:
            return all_ok
        
        # Copy subset.cfg. This will give the new subset a new uuid 
        des_path = self.subset_dict[target_subset_name].config.file_path
        self.subset_dict[target_subset_name].config = self.subset_dict[source_subset_name].config.make_copy_of_config(des_path) 
        
        return True
    
    #==========================================================================
    def rename_paths(self, from_name, to_name, pre_directory=''): 
        
        for name in self.paths.keys(): 
            if type(self.paths[name]) == dict:
                for sub_name in self.paths[name].keys():
                    self.paths[name][sub_name] = get_new_path(from_name, to_name, self.paths[name][sub_name], pre_directory)
            else:
                self.paths[name] = get_new_path(from_name, to_name, self.paths[name], pre_directory)
            
                
    #==========================================================================
    def rename_subset(self, from_name=None, to_name=None): 
        """
        Renames the subset and changes all the paths. 
        """ 
        assert all([from_name, to_name]) 
        
        if to_name.lower() in ['subset', 'default_subset']: 
            print('Invalid name "{}" for subset!'.format(to_name)) 
            return False 
        
        if to_name in self.subset_dict.keys():
            print('Invalid name "{}" for subset! subset already excists!'.format(to_name)) 
            return False 
            
        subset_object = self.get_subset_object(from_name)
        
        subset_object.rename_subset(to_name)
        
        # Rename paths in Workspace 
        self.rename_paths(from_name, to_name, pre_directory='subsets')
        
        # Rename paths in step_0 
        self.step_0.rename_paths(from_name, to_name, pre_directory='subsets')
        
        # Rename key in dict 
        self.subset_dict[to_name] = self.subset_dict[from_name]
        self.subset_dict.pop(from_name)
        
    
    #==========================================================================
    def rename_workspace(self, to_name=None): 
        """
        Renames the workspace and changes all the paths. 
        """  
        
        if not self._change_ok(): 
            print('Not allowed to rename workspace!') 
            return False  
            
        current_directory = self.paths['workspace_directory']
        new_directory = '{}/{}'.format(self.paths['parent_directory'], to_name) 
        
        if os.path.exists(new_directory):
            print('Workspace "{}" already excists. Can not rename workspace!'.format(to_name))
            return False
        
        # Rename paths in Workspace 
        self.rename_paths(self.name, to_name, pre_directory='workspaces')
        
        # Rename paths in step_0 
        self.step_0.rename_paths(self.name, to_name, pre_directory='workspaces') 
        
        # Rename subsets 
        for subset in self.subset_dict.keys():
            self.subset_dict[subset].rename_workspace(self.name, to_name)
        
        # Set path in config file 
        self.config.set_path(self.name, to_name, pre_directory='workspaces') 
        
        # Rename directory 
#        print(from_path)
#        print(to_path)
        os.rename(current_directory, new_directory)
        
        self.name = to_name 
        
    #==========================================================================
    def print_all_paths(self): 
        """
        Prints all path in the workspace.
        """
        sep_length = 100
        print('='*sep_length)
        print('='*sep_length)
        print('Workspace root paths')
        print('-'*sep_length)
        for item in sorted(self.paths.keys()):
            if type(self.paths[item]) == dict:
                for path in sorted(self.paths[item].keys()):
                    if type(self.paths[item][path]) == dict:
                        for p in sorted(self.paths[item][path].keys()):
                            print('-', self.paths[item][path][p])
                    else:
                        print(self.paths[item][path])
            else:
                print(self.paths[item])
                
        self.step_0.print_all_paths()
        
        for subset in sorted(self.subset_dict.keys()):
            self.subset_dict[subset].print_all_paths()
        
        print('')
        
        
    #==========================================================================
    def delete_subset(self, subset_name=None): 
        """
        subset_name is like 'A', 'B' and so on. Consider to use alias as option. 
        """
        if subset_name in self.subset_dict.keys(): 
            # TODO: Delete files and directories. How to make this safe? 
            self.subset_dict.pop(subset_name)
            self.paths['directory_path_subsets'].pop(subset_name)
            return True
        return False
            
    #==========================================================================
    def get_all_file_paths_in_workspace(self): 
        """
        Returns a sorted list of all file paths in the workspace tree. 
        """
        file_list = []
        for root, dirs, files in os.walk(self.paths['workspace_directory']): 
                for f in files:
                    file_list.append('/'.join([root, f]).replace('\\', '/'))
        return sorted(file_list)
    
    #==========================================================================
    def get_all_file_paths_in_input_data(self):
        file_list = []
        for root, dirs, files in os.walk(self.paths['directory_path_input_data']): 
                for f in files:
                    file_list.append('/'.join([root, f]).replace('\\', '/'))
        return sorted(file_list)
    
    #==========================================================================
    def get_data_filter_object(self, step=None, subset=None): 
        step_object = self.get_step_object(step=step, subset=subset)
        if not step_object:
            return False
        return step_object.get_data_filter_object()
        
    #==========================================================================
    def get_data_filter_info(self, step=None, subset=None): 
        data_filter = self.get_data_filter_object(step=step, subset=subset)
        if not data_filter:
            return False
        return data_filter.get_filter_info()
    
    #==========================================================================
    def get_filtered_data(self, step=None, subset=None, water_body=None, indicator=None): 
        """
        Returns filtered data using the given filter level. 
        """
        step = get_step_name(step)
        if step == None:
            return False
        print('STEP', step)
        return self.index_handler.get_filtered_data(subset=subset, step=step, water_body=water_body, indicator=indicator)
    
    #==========================================================================
    def get_available_indicators(self):
        
        self.available_indicators = []
        for indicator, parameters in self.cfg['indicators'].items():
            for param in parameters:
                if len(param.split('/')) > 1:
                    for param2 in param.split('/'):
                        if param2 == 'SALT':
                            continue
                        if param2 in self.get_filtered_data(level=0).columns and self.get_filtered_data(level=0)[param2].dropna().count() > 0:
                            self.available_indicators.append(indicator) 
                else:
                    if param in self.get_filtered_data(level=0).columns and self.get_filtered_data(level=0)[param].dropna().count() > 0:
                        self.available_indicators.append(indicator) 
            
        return sorted(self.available_indicators)
    
    #==========================================================================
    def get_indicator_settings_data_filter_object(self, subset=None, step=2, indicator=None): 
        step_object = self.get_step_object(subset=subset, step=step)
        return step_object.get_indicator_data_filter_settings(indicator)
    
    #==========================================================================
    def get_indicator_settings_name_list(self, subset=None, step=2):
        step_object = self.get_step_object(subset=subset, step=step)
        return sorted(step_object.indicator_settings.keys())
    
    #==========================================================================
    def get_subset_list(self):
        return sorted(self.subset_dict.keys())
    
    #==========================================================================
    def get_subset_object(self, subset): 
        return self.subset_dict.get(subset, False)
    
    #==========================================================================
    def get_step_object(self, step=None, subset=None): 
        step = get_step_name(step)
        if step == 'step_0':
            return self.step_0
        
        assert all([subset, step])
        
        sub = self.get_subset_object(subset)
        if not sub:
            return False
        return sub.get_step_object(step)
    
    #==========================================================================
    def get_step_0_object(self): 
        return self.step_0 
    
    #==========================================================================
    def get_step_1_object(self, subset): 
        return self.subset_dict[subset].get_step_1_object()
    
    #==========================================================================
    def get_step_2_object(self, subset): 
        return self.subset_dict[subset].get_step_2_object()
    
    #==========================================================================
    def initiate_quality_factors(self, ):
        self.quality_factor_NP = core.QualityFactorNP()
        
    #==========================================================================
    def load_all_data(self): 
        """ 
        Loads all data from the input_data/raw_data-directory belonging to the workspace. 
        """
        # TODO: Make this part dynamic 
        output_directory = self.paths['directory_path_input_data'] + '/exports/' 
        """
        # The input_data directory is given to DataHandler during initation. 
        # If no directory is given use the default directory! 
        # This has to be done in physical_chemical, zoobenthos etc. 
        """
#        # read settings to match filename and datatype, return pd df
#        dtype_settings = core.Load().load_txt(file_path=raw_data_file_path + 'dtype_settings.txt', sep='\t')
#        # TODO:  User should maybe choose which files to load?
#        #loop filenames in dtype_settings to read with correct datahandler
#        for index, row in dtype_settings.iterrows():
#            
#            if row.filename.startswith('#'):
#                print('\nSkipping', row.filename+'\n')
#                continue
#            
#            print(row.keys())
#            if row['data_type'] == 'phyche':
#                self.data_handler.physical_chemical.load_source(file_path=raw_data_file_path + row.filename,

        self.dtype_settings = core.RawDataFiles(self.paths['directory_path_raw_data'])
        if not self.dtype_settings.has_info:
            print('No info found')
            return False
        data_loaded = False
        for file_path, data_type in self.dtype_settings.get_active_paths_with_data_type(): 
            
            if data_type == 'phyche':
                self.data_handler.physical_chemical.load_source(file_path=file_path, raw_data_copy=True)
                data_loaded = True
                self.data_handler.physical_chemical.save_data_as_txt(directory=output_directory, prefix=u'Column_format') 
                
#            elif row['data_type'] == 'phyche_model':
#                self.data_handler.physical_chemical.load_source(file_path=raw_data_file_path + row.filename,
#                                                                raw_data_copy=True)
#                self.data_handler.physical_chemical.save_data_as_txt(directory=output_directory, prefix=u'Column_format')                
#                
#            elif row['data_type']== 'zooben':
#                self.data_handler.zoobenthos.load_source(file_path=raw_data_file_path + row.filename,

            elif data_type== 'zooben':
                self.data_handler.zoobenthos.load_source(file_path=file_path,
                                                         raw_data_copy=True)
                data_loaded = True
                self.data_handler.zoobenthos.save_data_as_txt(directory=output_directory, prefix=u'Column_format')
            elif data_type == 'pp':
                self.data_handler.phytoplankton.load_source(file_path=file_path,
                                                         raw_data_copy=True)
                data_loaded = True
                self.data_handler.phytoplankton.save_data_as_txt(directory=output_directory, prefix=u'Column_format')
            elif data_type == 'hose':
                self.data_handler.chlorophyll.load_source(file_path=file_path,
                                                         raw_data_copy=True)
                data_loaded = True
                self.data_handler.chlorophyll.save_data_as_txt(directory=output_directory, prefix=u'Column_format')   
            else:
                print('could not read {} from raw_data directory. Check data type'.format(os.path.basename(file_path)))

        
        self.data_handler.merge_all_data(save_to_txt=True)
        
        return data_loaded
#        # read settings to match filename and datatype, return pd df
#        dtype_settings = core.Load().load_txt(file_path=raw_data_file_path + 'dtype_settings.txt', sep='\t')
#        # TODO:  User should maybe choose which files to load?
#        #loop filenames in dtype_settings to read with correct datahandler 
#        
#        for index, row in dtype_settings.iterrows(): 
#            if row.filename.startswith('#'):
#                print('\nSkipping', row.filename+'\n')
#                continue
#            
#            print(row.keys())
#            if row['data_type'] == 'phyche':
#                self.data_handler.physical_chemical.load_source(file_path=raw_data_file_path + row.filename,
#                                                                raw_data_copy=True)
#                self.data_handler.physical_chemical.save_data_as_txt(directory=output_directory, prefix=u'Column_format')
#            elif row['data_type']== 'zooben':
#                self.data_handler.zoobenthos.load_source(file_path=raw_data_file_path + row.filename,
#                                                         raw_data_copy=True)
#                self.data_handler.zoobenthos.save_data_as_txt(directory=output_directory, prefix=u'Column_format')
#            elif row['data_type'] == 'pp':
#                self.data_handler.phytoplankton.load_source(file_path=raw_data_file_path + row.filename,
#                                                         raw_data_copy=True)
#                self.data_handler.phytoplankton.save_data_as_txt(directory=output_directory, prefix=u'Column_format')
#            elif row['data_type'] == 'hose':
#                self.data_handler.chlorophyll.load_source(file_path=raw_data_file_path + row.filename,
#                                                         raw_data_copy=True)
#                self.data_handler.chlorophyll.save_data_as_txt(directory=output_directory, prefix=u'Column_format')   
#            else:
#                print('could not read {} from raw_data directory. Check data type'.format(row.filename))
#
#        
#        self.data_handler.merge_all_data(save_to_txt=True)
        
        # Row data
        # TODO: retrieve from workspace. User should maybe choose which files to load?
#        fid_zooben = u'zoobenthos_2016_row_format_2.txt'
#        fid_phyche = u'BOS_HAL_2015-2016_row_format_2.txt'
#        fid_phyche_col = u'BOS_BAS_2016-2017_column_format.txt' 
#        
#        self.data_handler.physical_chemical.load_source(file_path=raw_data_file_path + fid_phyche,
#                                                        raw_data_copy=True)
#        self.data_handler.physical_chemical.load_source(file_path=raw_data_file_path + fid_phyche_col,
#                                                        raw_data_copy=True)
#        self.data_handler.physical_chemical.save_data_as_txt(directory=output_directory, prefix=u'Column_format')
#        
#        
#        self.data_handler.zoobenthos.load_source(file_path=raw_data_file_path + fid_zooben,
#                                                 raw_data_copy=True)
#        self.data_handler.zoobenthos.save_data_as_txt(directory=output_directory, prefix=u'Column_format')
#        
#        self.data_handler.merge_all_data(save_to_txt=True)
        
    #==========================================================================
    def deprecated_save_indicator_settings(self, indicator=None, subset=None): 
        """
        Saving indicator settings is only possible in step 2. 
        """
        # TODO: Chould later steps be removed if indicator settings are saved (saving only possible at level 2)?
        if not self._change_ok(): 
            return 
        step_object = self.get_step_2_object(subset)
        step_object.indicator_settings[indicator].save_file() # Overwrites existing file if no file_path is given
        return True 
    
    #==========================================================================
    def deprecated_save_all_indicator_settings_in_subset(self, subset): 
        if not self._change_ok(): 
            return 
        all_ok = True
        step_object = self.get_step_2_object(subset)
        for obj in step_object.indicator_settings.values():
            if not obj.save_file():
                all_ok = False
        return all_ok 
    
    #==========================================================================
    def set_data_filter(self, step='', subset='', filter_type='', filter_name='', data=None, save_filter=True): 
        """
        Sets/changes the data_filter of the given filter_name. 
        
        Input: 
            step:           Specify in what step you want to change the data filter. 
                            data_filter can be applied on step 0, 1 and 2
                            
            subset:         Subset that the step belog to. Must be provided if step is > 0 
            
            filter_type:    Can be "include_list" or "exclude_list"
            
            filter_name:    Name of filter that you want to change. 
                            Name follows the CodeList
            
            data:           value that you want to change to
            
            save filter:    option to save text file. default is true
        """
        assert filter_type in ['include_list','exclude_list'], 'filter_type must be include_list or exclude_list'
        if not self._change_ok():
            return False
        
        step = get_step_name(step)
        step_object = self.get_step_object(step=step, subset=subset)
        if not step_object:
            return False
        if int(step[-1]) > 2:
            print('Data filter can only be applied on step_2 or lower!')
            return False
        return step_object.set_data_filter(filter_type=filter_type, 
                                            filter_name=filter_name, 
                                            data=data, 
                                            save_filter=save_filter)
        
    #==========================================================================
    def set_indicator_settings_data_filter(self, indicator=None, filter_settings=None, subset=None, step=2): 
        """
        Sets/changes the indicator_settings_data_filter of the given indicator. 
        filter_settings is a dict like: 
            filter_settings[type_area][variable] = value
        
        Input: 
            indicator:          Indicator that you want to change settings for. 
                            
            filter_settings:    values in a dict like: filter_settings[type_area][variable]
                                If variable is 
            
            subset:             Subset that you want to change the indicator settings for. 
            
            step:               Default is 2
            
        """
        step_object = self.get_step_object(step=step, subset=subset)
        if not step_object:
            return False
        return step_object.set_indicator_settings_data_filter(indicator=indicator, 
                                                              filter_settings=filter_settings)

        
    
#==========================================================================
#==========================================================================
class Config(dict): 
    def __init__(self, file_path): 
        self.file_path = file_path
        if not os.path.exists(file_path):
            with codecs.open(file_path, 'w', encoding='cp1252') as fid: 
                fid.write('')
        else:
            with codecs.open(file_path, encoding='cp1252') as fid:
                for line in fid: 
                    line = line.strip()
                    if not line:
                        continue
                    split_line = [item.strip() for item in line.split(';')]
                    item, value = split_line
                    self[item] = value
    
    #==========================================================================
    def get_config(self, item):
        return self.get(item)
    
    #==========================================================================
    def set_config(self, item, value):
        self[item] = value
        self.save_file()
    
    #==========================================================================
    def set_unique_id(self): 
        if not self.get('unique_id'):
            self['unique_id'] = str(uuid.uuid4())
            self.save_file()
        return self['unique_id']
    
    #==========================================================================
    def save_file(self):
        with codecs.open(self.file_path, 'w', encoding='cp1252') as fid:
            for item, value in sorted(self.items()):
                line = ';'.join([item, value])
                fid.write('{}\n'.format(line)) 
                
    #==========================================================================
    def make_copy_of_config(self, file_path): 
        """
        Returns a copy of the config file. The copy will have a new unique_id. 
        """
        shutil.copyfile(self.file_path, file_path) 
        c = Config(file_path) 
        # Force new uuid
        c.set_config('unique_id', str(uuid.uuid4()))
        c.save_file()
        return c
    
    #==========================================================================
    def set_path(self, from_name, to_name, pre_directory): 
        self.file_path = get_new_path(from_name, to_name, self.file_path, pre_directory)
        
"""
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
"""


#==============================================================================
#==============================================================================
def get_step_name(step): 
#    print('STEP', step)
    if step == None:
        return step
    step = str(step)
    if not step.startswith('step_'):
        step = 'step_' + step
    return step


#==============================================================================
#==============================================================================
def get_new_path(from_name, to_name, old_path, pre_directory=''): 
    # include /p/ here to be safer when using replace for string. 
    from_string = '/{}/{}'.format(pre_directory, from_name)
    to_string = '/{}/{}'.format(pre_directory, to_name) 
    if old_path.endswith(from_name):
        from_string = from_string + '$'
    else:
        from_string = from_string + '/'
        to_string = to_string + '/' 
    
    return re.sub(from_string, to_string, old_path, 1)


#==============================================================================
#==============================================================================
#==============================================================================
if __name__ == '__main__':
    if 0:
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
                    
    if 1:
        workspace_path = 'D:/Utveckling/g_ekostat_calculator/ekostat_calculator_lena/workspaces'
        w = WorkSpace(name='default', parent_directory=workspace_path)
                    
                    
                    
                    
                    
                    
                    
                    
                