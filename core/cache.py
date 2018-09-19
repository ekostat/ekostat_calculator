# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 15:57:32 2018

@author: Magnus
""" 
import pickle


class Cache():
    """
    Created 20180919    by Magnus Wenzer 
    
    Class to handle cache of data
    """
    def __init__(self, directory): 
        self.directory = directory
       
    #==========================================================================
    def _save_file(self, data, file_path): 
        with open(file_path, "wb") as fid:
            pickle.dump(data, fid) 
    
    #==========================================================================
    def save_result(self, data, *args, **kwargs): 
        """
        Items in args are used to build name of the data tha is to be saved. 
        """ 
        # Save as pickle 
        with open(pkl_file_path, "rb") as fid: 
            response = pickle.load(fid)
    
    
    #==========================================================================
    def load(self, **kwargs): 
        pass 
    
    
    #==========================================================================
    def delete(self, **kwargs): 
        pass
