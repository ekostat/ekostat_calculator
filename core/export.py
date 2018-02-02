# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 08:09:06 2018

@author: a002028
"""

import pandas as pd
#import numpy as np
import json


"""
#==============================================================================
#==============================================================================
"""
class Export(object):
    """
    Handles different exports
    - excel
    - json
    - netcdf
    - text
    """
    #==========================================================================
    def __init__(self, out_source='', data={}):
        """
        """
        pass
#        self.out_source = out_source

    #==========================================================================
    def _get_dict(self, df=None, column_order=[]):
        """
        Transform DataFrame into dictionary
        """
        return df.to_dict()
    
    
    #==========================================================================
    def export_excel(self, data_dict={}):
        """
        """
        #TODO code
        pass
    
    
    #==========================================================================
    def export_json(self, data_dict={}, out_source='', indent=4):
        """
        """
        if isinstance(data_dict, pd.DataFrame):
            data_dict = self._get_dict(df=data_dict)
                
        with open(out_source, "w") as outfile:
            json.dump(data_dict, outfile, indent=indent)
        
        
    #==========================================================================
    def export_netcdf(self, data_dict={}):
        """
        """
        #TODO code
        pass
        
        
    #==========================================================================
    def export_text(self, data_dict={}):
        """
        """
        #TODO code
        pass
        
    
    #==========================================================================
    
"""
#==============================================================================
#==============================================================================
"""    
    
    
    
