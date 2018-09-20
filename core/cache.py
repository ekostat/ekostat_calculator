# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 15:57:32 2018

@author: Magnus
""" 
import os
import pickle

import core.exceptions as exceptions 


class Cache():
    """
    Created 20180919    by Magnus Wenzer 
    
    Class to handle cache of data
    """
    def __init__(self, directory, mandatory_uuid=False, min_nr_arguments=3): 
        if not os.path.exists(directory): 
            raise exceptions.MissingDirectory
            
        self.directory = directory 
        self.mandatory_uuid = mandatory_uuid
        self.min_nr_arguments = min_nr_arguments 
        
      
    #==========================================================================
    def _list_files(self): 
        return os.listdir(self.directory)
        
    
    #==========================================================================
    def _save_file(self, data, file_path): 
        # Save as pickle
#        print('saving file:', file_path)
        with open(file_path, "wb") as fid:
            pickle.dump(data, fid) 
    
    
    #==========================================================================
    def _load_file(self, file_path): 
         # Load pickle 
        with open(file_path, "rb") as fid: 
            response = pickle.load(fid)
        return response
    
    
    #==========================================================================
    def save(self, data, *args): 
        """
        Items in args are used to build name of the data that is to be saved. 
        workspace_uuid, subset_uuid and at least one args is manadatory. 
        
        Minimum 3 arguments has to be given in args. At least oe needs to be a uuid. 
        """ 
        if len(args) < self.min_nr_arguments: 
            raise exceptions.MissingInputVariable('Need {} arguments, {} given'.format(self.min_nr_arguments, len(args)))
        if self.mandatory_uuid and not any([len(arg)==36 for arg in args]): 
            raise exceptions.MissingInputVariable('uuid needed')
            
        # Check uuid. Mandatory is 
            
        # Build file path 
        file_path = '{}/{}.pkl'.format(self.directory, 
                                             '_'.join(sorted(args, key=len)[::-1])) 
        
        self._save_file(data, file_path)
        print('Cache file saved: {}'.format(file_path))
        

    #==========================================================================
    def load(self, *args, **kwargs): 
        """
        If all matches in args result in one file. This file is loaded. 
        """
        all_files = self._list_files() 
        matching_files = [] 
        for file_name in all_files: 
            if all([item in file_name for item in args]): 
                matching_files.append(file_name)
        
        if len(matching_files) == 1: 
            file_path = os.path.join(self.directory, matching_files[0])
            print('Cache file loaded: {}'.format(file_path))
            return self._load_file(file_path)
        else:
            return False
        
#        elif len(matching_files) == 0:
#            raise exceptions.MatchError('No match found')
#        else:
#            raise exceptions.MatchError('{} matches found'.format(len(matching_files)))
        
        
    #==========================================================================
    def delete(self, *args): 
        """
        Deletes all files matching all arguments in args. 
        """
        if not len(args): 
            raise exceptions.MissingInputVariable 
            
        all_files = self._list_files()
        for file_name in all_files: 
            if all([item in file_name for item in args]):
                file_path = os.path.join(self.directory, file_name)
                os.remove(file_path)
                print('Cache file deleted: {}'.format(file_path))
            else:
                print('===', file_name)
        
        
        
        
        
        
        
        
        
        
        
        
