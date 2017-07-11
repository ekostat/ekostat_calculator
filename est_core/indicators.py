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
    def set_data_handlers(self, data_handler=None, data_handler_dict=None):
        """
        Assigns data_handler-object(s) to the parameter objects beloniging to self. 
        If "data_handler" is given all parameters will be assigned that data_handler. 
        If "data_handler_dict" is given the coresponding data_handler under its key will be assigend. 
        """
        if data_handler:
            for key in self.parameters.keys():
                attr = getattr(self, key.lower())
                attr.set_data_handler(data_handler)
        elif data_handler_dict:
            for key in data_handler_dict.keys():
                if key in self.parameters.keys(): 
                    attr = getattr(self, key.lower())
                    attr.set_data_handler(data_handler_dict[key])
        
        
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
        
        self._initiate_data_objects()
        
    
    #==========================================================================
    def _initiate_data_objects(self):
        """
        Initiates data to work with. Typically parameter class objects. 
        """
        self.ntra = est_core.ParameterNTRA()
        
    #==========================================================================
    def filter_data(self, filter_data_objects):
        """
        Filters data in Parameter objects
        filter_data_object is of type est_core.settings.FilterData
        """
        pass

            
###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "indicators.py"')
    print('-'*50)
    print('')
    
    
    
    
    