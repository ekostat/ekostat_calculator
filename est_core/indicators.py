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
        self.name = ''
        self.parameter_list = []
    
    #========================================================================== 
    def set_data_handler(self, data_handler=None, parameter=None): 
        """
        Assigns data_handler-object(s) to the parameter objects belonging to self. 
        if data_handler and parameter is given that parameter is given the data handler. 
        If "data_handler" is given all parameters will be assigned that data_handler. 
        If "data_handler_dict" is given the corresponding data_handler under its key will be assigend. 
        """ 
        if data_handler and parameter:
            if not parameter in self.parameter_list:
                return False
            attr = getattr(self, parameter.lower())
            all_ok = attr.set_data_handler(data_handler)
            return all_ok
        elif data_handler:
            for key in self.parameter_list:
                try:
                    attr = getattr(self, key.lower())
                    attr.set_data_handler(data_handler)
                except AttributeError as e:
                    print(e)
        return True
    
    
    #==========================================================================
    def filter_data(self, filter_data_object=None, parameter=None):
        """
        Filters data in Parameter objects
        filter_data_object is of type est_core.settings.FilterData
        If "filter_data_object" is given all parameters will be filtered using this filter. 
        If "filter_data_object_dict" is given the corresponding filter under its key will be used. 
        """
        print('parameter', parameter)
        if filter_data_object and parameter:
            print('parameter', parameter)
            if not parameter in self.parameter_list:
                return False
            if not hasattr(self, parameter.lower()):
                return False
            attr = getattr(self, parameter.lower())
            all_ok = attr.filter_data(filter_data_object)
            return all_ok
        if filter_data_object:
            for key in self.parameter_list:
                print('key', key)
                if hasattr(self, key.lower()):
                    attr = getattr(self, key.lower())
                    attr.filter_data(filter_data_object)
        return True
        
        
###############################################################################
class IndicatorNtotSummer(IndicatorBase): 
    """
    Class to calculate status for a NP. 
    """
    
    def __init__(self):
        super().__init__() 
        self.name = 'NtotSummer'
        
        # Parameter list contains all parameters that is used by the indicator class
        self.parameter_list = []
        
        self._load_data_objects()
        
    
    #==========================================================================
    def _load_data_objects(self):
        """
        Initiates data to work with. Typically parameter class objects. 
        """
        pass
        
    
###############################################################################
class IndicatorDINwinter(IndicatorBase): 
    """
    Class to calculate status for a NP. 
    """
    
    def __init__(self):
        super().__init__() 
        self.name = 'DIN'
        
        # Parameter list contains all parameters that is used by the indicator class
        self.parameter_list = ['NTRA', 'NTRI', 'AMON', 'DIN']
        
        self._load_data_objects()
        
    
    #==========================================================================
    def _load_data_objects(self):
        """
        Initiates data to work with. Typically parameter class objects. 
        """
        
        self.salt = est_core.ParameterSALT
        
        self.ntra = est_core.ParameterNTRA()
        self.ntri = est_core.ParameterNTRI()
        self.amon = est_core.ParameterAMON()
        self.din = None
        
    #==========================================================================
    def filter_data(self, filter_data_object=None, parameter=None):
        """
        Override from Parent class IndicatorBase. 
        After filtering of parameterrs the calculated din-parameter is created. 
        """
        print('parameter', parameter)
        if filter_data_object and parameter:
            print('parameter', parameter)
            if not parameter in self.parameter_list:
                return False
            if not hasattr(self, parameter.lower()):
                return False
            attr = getattr(self, parameter.lower())
            all_ok = attr.filter_data(filter_data_object)
            return all_ok
        if filter_data_object:
            for key in self.parameter_list:
                try:
                    attr = getattr(self, key.lower())
                    attr.filter_data(filter_data_object)
                except AttributeError as e:
                    print(e)
        
        # Load CalculatedParameterDIN if possible
        # TODO: Option to load pre-calculated DIN (DIN in dataset). This 
        if all([self.ntra.data, self.ntri.data, self.amon.data]):
            self.din = est_core.CalculatedParameterDIN(ntra=self.ntra.data, 
                                                       ntri=self.ntri.data, 
                                                       amon=self.amon.data)
        return True

    #==========================================================================
    def get_ek_value(self):
        pass
    
    
    
            
###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "indicators.py"')
    print('-'*50)
    print('')
    
    
    
    
    