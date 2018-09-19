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
    def __init__(self, directory): 
        if not os.path.exists(directory): 
            raise exceptions.MissingDirectory
            
        self.directory = directory
       
        
    #==========================================================================
    def _save_file(self, data, file_path): 
        # Save as pickle
        with open(file_path, "wb") as fid:
            pickle.dump(data, fid) 
    
    
    #==========================================================================
    def _load_file(self, file_path): 
         # Load pickle 
        with open(file_path, "rb") as fid: 
            response = pickle.load(fid)
        return response
    
    
    #==========================================================================
    def save_result(self, data, *args, **kwargs): 
        """
        Items in args are used to build name of the data that is to be saved. 
        """ 
        # Build file path 
        file_path = '{}/result_{}.pkl'.format(self.directory, '_'.join(*args)) 
        
        self._save_file(data, file_path)
        
    
    
    #==========================================================================
    def load(self, **kwargs): 
        pass 
    
    
    #==========================================================================
    def delete(self, **kwargs): 
        pass
