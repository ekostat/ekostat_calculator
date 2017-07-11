# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 16:07:18 2017

@author: a001985

Python3
"""         
        
###############################################################################
class ParameterGetInformation(object):
    """
    Holds various information about get-methodes in the Parameter objects. 
    Information can be different for differnet parameter types. 
    Permanent information is:
        information_source
        status = None
    """
    def __init__(self, information_source): 
        self.information_source = information_source
        self.status = None
    
    

###############################################################################
class ParameterBase(object):
    """
    Base-class to describe and hold base information about Parameters. 
    """
    def __init__(self):
        self._initiate_attributes()
    
    #==========================================================================
    def _initiate_attributes(self): 
        self.data_holder = None # Dedicated for a DataHolder obejct. This is the source data. 
        
        self.data = None        # Dedicated for a pandas dataframe. Hold data to work with. 
        
        self.area = None        # Dedicated for a est_core.Area object 
        self.time = None        # Dedicated for a ext_core.Time object
        
        self.info = None        # Dedicated for a ParameterGetInformation object
        
        self.internal_name = ''
        self.display_name = ''
        self.unit = ''
        
    #==========================================================================
    def set_data_handler(self, data_handler): 
        """
        Set pandas dataframe to work with. 
        Not sure how this should be handled. 
        Data might look different depending on the source. 
        """
        self.data_handler = data_handler 
        self.data_handler_source = data_handler.source 
        
    #==========================================================================
    def drop_data_handler(self): 
        self.data_handler = None 
        self.data_handler_source = None 
        
    #==========================================================================
    def get_data(self, **kwargs): 
        """
        Loads data from DataHandler object and stores result in self.data. 
        This method is overwritten in subclasses. 
        """
        if not self.data: 
            return 
        
    #==========================================================================
    def get_station_list(self):
        """
        Returns a list of all stations that has data of the current parameter (self.internal_name). 
        """
        if not self.internal_name or not self.data:
            return False
        
        return sorted(set(self.data.loc[self.data.index[~self.data[self.internal_name].isnull()], 'STATN']))
            
    
###############################################################################
class ParameterBasePhysicalChemical(ParameterBase):
    """
    Base-class to describe and hold base information about PhysicalChemical Parameters. 
    """
    def __init__(self):
        super().__init__() 
        
    
    def get_data(self, depth_interval):
        pass
        
        
    
###############################################################################
class ParameterNTRA(ParameterBasePhysicalChemical):
    """
    Class to describe and handle Nitrate. 
    """
    def __init__(self):
        super().__init__()
        
        self.internal_name = 'NTRA'
        self.external_name = 'Nitrate' 
        self.unit = 'umol/l'


###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "parameters.py"')
    print('-'*50)
    print('')
    
    
    
    
    
    
    