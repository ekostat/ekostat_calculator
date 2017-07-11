# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:24:34 2017

@author: a001985
"""
import est_core

###############################################################################
class IndicatorBase(object): 
    """
    Class to calculate status for a specific indicator. 
    """
    
    def __init__(self):
        self.indicator = None
        
        
    #==========================================================================
    def set_data_handler(self, data_handler):
        self.data_handler = data_handler 
        
        
###############################################################################
class IndicatorNP(IndicatorBase): 
    """
    Class to calculate status for a NP. 
    """
    
    def __init__(self):
        super().__init__() 
        self.indicator = 'NP'
        
        # Parameter list contains all parameters that is used by the indicator class
        self.parameter_list = ['NTRA']
        
        self._initiate_data()
        
    
    #==========================================================================
    def _initiate_data(self):
        """
        Initiates data to work with. Typically parameter class objects. 
        """
        self.ntra = est_core.ParameterNTRA()
        
        
    #==========================================================================
    def set_data_handler(self, data_handler):
        for par in self.parameter_list:
            attr = getattr(self, par.lower())
            attr.set_data_handler(data_handler) 
            
            
###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "indicators.py"')
    print('-'*50)
    print('')
    
    
    
    
    