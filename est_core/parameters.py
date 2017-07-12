# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 16:07:18 2017

@author: a001985

Python3
"""            

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
        Set data_handler to work with. 
        This is not the data that will be looked in by the get-methodes. 
        To create this data 
        Data might look different depending on the source. 
        """
        self.data_handler = data_handler 
        self.data_handler_source = data_handler.source 
        return True
        
    #==========================================================================
    def drop_data_handler(self): 
        self.data_handler = None 
        self.data_handler_source = None 
        
    #==========================================================================
    def drop_data(self): 
        self.data = None
        
    #==========================================================================
    def reset_all_data(self): 
        self.drop_data()
        self.drop_data_handler()
        
    #==========================================================================
    def filter_data(self, data_filter_object):
        print('filter_data')
        self.data = self.data_handler.filter_data(data_filter_object)
        # TODO: Check if all is ok
        return True
        
    #==========================================================================
    def get_data(self, **kwargs): 
        """
        Loads data from DataHandler object self.data and returns result. 
        This method is overwritten in subclasses. 
        """
        if not self.data: 
            return             
    
###############################################################################
class ParameterBasePhysicalChemical(ParameterBase):
    """
    Base-class to describe and hold base information about PhysicalChemical Parameters. 
    """
    def __init__(self):
        super().__init__() 
        

        
    
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
    
    
    
    
    
    
    