# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 14:43:35 2017

@author: a001985
"""

import est_core 

###############################################################################
class QualityFactorBase(object): 
    """
    Class to hold general inforamtion about quality factors. 
    """ 
    def __init__(self):
        self.name = '' 
        
        self._load_indicators()
        self.indicator_list = []
        
    
    #==========================================================================
    def _load_indicators(self):
        """
        Load indicator objects that are included in the quality factor. 
        """
        pass
    
    #==========================================================================
    def _calculate_quality_factor(self):
        pass
    
    #========================================================================== 
    def set_data_handler(self, data_handler=None, indicator=None, parameter=None): 
        """
        Assigns data_handler-object(s) to the indicator objects belonging to self. 
        If "data_handler" is given all indicators will be assigned that data_handler. 
        If "data_handler_dict" is given the corresponding data_handler under its key will be assigend. 
        """ 
        if all([data_handler, indicator]):
            attr = getattr(self, indicator.lower())
            attr.set_data_handler(data_handler=data_handler, parameter=parameter) 
            # parameter could be None here. If so, all parameters in the indicator will be assigned the data_handler. 
        elif data_handler:
            for key in self.indicator_list:
                attr = getattr(self, key.lower())
                attr.set_data_handler(data_handler=data_handler)
        return True
    
    
    #==========================================================================
    def filter_data(self, filter_data_object=None, indicator=None, parameter=None):
        """
        Filters data in Indicator objects
        filter_data_object is of type est_core.settings.FilterData
        If "filter_data_object" is given all indicators will be filtered using this filter. 
        If "filter_data_object_dict" is given the corresponding filter under its key will be used. 
        """
        if all([filter_data_object, indicator]):
            attr = getattr(self, indicator.lower())
            attr.filter_data(filter_data_object=filter_data_object, parameter=parameter)
        elif filter_data_object:
            for key in self.parameter_list:
                attr = getattr(self, key.lower())
                attr.filter_data(filter_data_object)
#        elif filter_data_object_dict:
#            for key in filter_data_object_dict.keys():
#                if key in self.parameter_list: 
#                    attr = getattr(self, key.lower())
#                    attr.filter_data(filter_data_object_dict[key]) 
        return True
        
        
###############################################################################
class QualityFactorNP(QualityFactorBase): 
    """
    Class to hold information and calculate the quality factor for Nutrients. 
    """
    def __init__(self):
        super().__init__() 
        self.name = 'NP'
        self.indicator_list = ['DIN_winter', 'DIN_summer']
        self._load_indicators()
        
    #==========================================================================
    def _load_indicators(self): 
        """
        Make sure the attributes and items in self.indicator_list are matching.
        (not case sensitive)
        """        
        self.din_winter = est_core.IndicatorDINwinter() 
        self.din_summer = est_core.IndicatorDINwinter() # Temp, should not be winter!
        
    #==========================================================================
    def get_quality_factor(self):
        pass
        
        
        
        
        
        
        
        
        
        
        
    #==========================================================================
    def _calculate_quality_factor(self):
        pass