# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:18:45 2017

@author: a002028
"""


#import numpy as np
import pandas as pd
import json
import codecs
#import netcdf
"""
#==============================================================================
#==============================================================================
"""
class Load(object):
    """
    class to hold various methods for loading different types of files
    Can be settings files, data files, info files.. 
    """
    def __init__(self):
        pass
    
    
    #==========================================================================
    def load_excel(self, file_path=u'', sheetname=u'', header_row=0, fill_nan=u''):
        xl = pd.ExcelFile(file_path)
        ncols = xl.book.sheet_by_name(sheetname).ncols
        xl.close()

        return pd.read_excel(file_path, sheetname=sheetname, header=header_row, 
                             converters={i:str for i in range(ncols)}).fillna(fill_nan)
        
        
    #==========================================================================
    def load_netcdf(self, file_path=u''):
        pass
    
    
    #==========================================================================
    def load_txt(self, file_path=u'', sep='\t', encoding='cp1252', fill_nan=u''):
        with codecs.open(file_path, 'r', encoding=encoding) as f:
            header = f.readline().strip('\n').strip('\r').split(sep) # is .strip('\r') necessary?

        return pd.read_csv(file_path, sep='\t', encoding='cp1252',
                           dtype={key:str for key in header}).fillna(fill_nan)

    
    #==========================================================================
    def load_json(self, file_path=u''):
        """
        array will be either a list of dictionaries or one single dictionary 
        depending on what the json file includes
        """
        with open(file_path, 'r') as f:
            array = json.load(f)
        
        return array
    
    
    #==========================================================================
        
        
        
"""
#==============================================================================
#==============================================================================
"""    
    
    
    
    
    
    
    
