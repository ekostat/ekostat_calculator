# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 15:30:22 2018

@author: a002087
"""

#!/usr/bin/python3
# -*- coding:utf-8 -*-

import rpy2.robjects as robjects

class RCalcWrapper():
    """ Creates wrappers for R functions. 
        R code is called from Python and results are stored in files by wrappers.
    """
    
    def __init__(self):
        """ """
        self._load_r_files()
        self._create_wrappers()
    
    def calc_r_test(self, file_path, x):
        """ """
        cmd_str = 'r_test_wrapper('
        cmd_str += '\'' + file_path + '\'' + ', '
        cmd_str += str(x) + ') '
        
        print(cmd_str)
        
        robjects.r(cmd_str)
        
        return file_path
    
    def CalculateIndicatorSupport(self):
        """ """
        
    
    def _load_r_files(self):
        """ """
        r_source = robjects.r['source']
        r_source('r_test.r')
    
    def _create_wrappers(self):
        """ """
        
        robjects.r(''' 
            r_test_wrapper <- function(r_result_path, x) {
                
                y = r_test(x)
                
                # Save result.
                save(y, file = r_result_path)
            }
        ''')
    


if __name__ == "__main__":
    RCalcWrapper().calc_r_test('data.RData', 5)
