# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:49:03 2017

@author: a001985
"""

import pandas as pd

###############################################################################
class DataHandler(object): 
    """
    Temporary class to hold data. 
    This class will work as a substitute for the est_core.DataHandler class 
    during development of the parameter module. 
    """
    def __init__(self, source):
        self.source = source
        self.data_phys_chem = pd.DataFrame()
    
    #==========================================================================
    def add_txt_file(self, file_path): 
        data = pd.read_csv(file_path, sep='\t', encoding='cp1252')
        self._add_data(data)
    
    #==========================================================================
    def _add_data(self, pd_df):
        """
        Adds data to the internal data structure. 
        """
        self.data_phys_chem = self.data_phys_chem.append(pd_df)
#        print(self.data_phys_chem.head())