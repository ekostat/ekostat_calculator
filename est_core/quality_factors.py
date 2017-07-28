# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 14:43:35 2017

@author: a001985
"""
import os
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
        Overwritten by subclasses. 
        """
        pass
    
    #==========================================================================
    def _calculate_quality_factor(self):
        """
        Overwritten by subclasses. 
        """
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
    def filter_data(self, data_filter_object=None, indicator=None, parameter=None):
        """
        Filters data in Indicator objects
        data_filter_object is of type est_core.settings.FilterData
        If "data_filter_object" is given all indicators will be filtered using this filter. 
        If "data_filter_object_dict" is given the corresponding filter under its key will be used. 
        """
        if all([data_filter_object, indicator]):
            attr = getattr(self, indicator.lower())
            attr.filter_data(data_filter_object=data_filter_object, parameter=parameter)
        elif data_filter_object:
            for key in self.indicator_list:
                attr = getattr(self, key.lower())
                attr.filter_data(data_filter_object)
        return True
        
        
###############################################################################
class QualityFactorNP(QualityFactorBase): 
    """
    Class to hold information and calculate the quality factor for Nutrients. 
    """
    def __init__(self):
        super().__init__() 
        self.name = 'NP'
        self.indicator_list = ['DIN_winter', 'DIN_summer', 'TOTN_winter']
        self._load_indicators()
        
    #==========================================================================
    def _load_indicators(self): 
        """
        Make sure the attributes and items in self.indicator_list are matching.
        (not case sensitive)
        """        
        self.din_winter = est_core.IndicatorDIN() # winter modified by filter on months 
        self.din_summer = est_core.IndicatorDIN() # summer modified by filter on months 
        self.totn_winter = est_core.IndicatorTOTN() # 
        
    #==========================================================================
    def get_quality_factor(self, tolerance_filter):
        return self.totn_winter.get_status(tolerance_filter)
    
    
###############################################################################
if __name__ == '__main__':
    nr_marks = 60
    print('='*nr_marks)
    print('Running module "quality_factor.py"')
    print('-'*nr_marks)
    print('')
    
    
    root_directory = os.path.dirname(os.path.abspath(__file__))[:-9]
    
#    est_core.StationList(root_directory + '/test_data/Stations_inside_med_typ_attribute_table_med_delar_av_utsjö.txt')
    est_core.ParameterList()
    
    #--------------------------------------------------------------------------
    # Directories and file paths
    raw_data_file_path = root_directory + '/test_data/raw_data/data_BAS_2000-2009.txt'
    first_filter_data_directory = root_directory + '/test_data/filtered_data' 
    
    first_data_filter_file_path = root_directory + '/test_data/filters/first_data_filter.txt' 
    winter_data_filter_file_path = root_directory + '/test_data/filters/winter_data_filter.txt'
    
    tolerance_filter_file_path = root_directory + '/test_data/filters/tolerance_filter_template.txt'
    
    #--------------------------------------------------------------------------
    # Filters 
    first_filter = est_core.DataFilter('First filter', file_path=first_data_filter_file_path)
    winter_filter = est_core.DataFilter('winter_filter', file_path=winter_data_filter_file_path)
    winter_filter.save_filter_file(root_directory + '/test_data/filters/winter_data_filter_save.txt') # mothod available
    tolerance_filter = est_core.ToleranceFilter('test_tolerance_filter', file_path=tolerance_filter_file_path)

    #--------------------------------------------------------------------------
    # Reference values
    est_core.RefValues()
    est_core.RefValues().add_ref_parameter_from_file('DIN_winter', root_directory + '/test_data/din_vinter.txt')
    est_core.RefValues().add_ref_parameter_from_file('TOTN_winter', root_directory + '/test_data/totn_vinter.txt')
    
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    # Handler (raw data)
    raw_data = est_core.DataHandler('raw')
    raw_data.add_txt_file(raw_data_file_path, data_type='column') 
    
    # Use first filter 
    filtered_data = raw_data.filter_data(first_filter) 
    
    # Save filtered data (first filter) as a test
    filtered_data.save_data(first_filter_data_directory)
    
    
    # Load filtered data (first filter) as a test
    loaded_filtered_data = est_core.DataHandler('first_filtered')
    loaded_filtered_data.load_data(first_filter_data_directory)


    # Create and fill QualityFactor
    qf_NP = est_core.QualityFactorNP()
    qf_NP.set_data_handler(data_handler=loaded_filtered_data)
    
    # Filter parameters in QualityFactorNP 
    # First general filter 
    qf_NP.filter_data(data_filter_object=first_filter) 
    # winter filter
    qf_NP.filter_data(data_filter_object=winter_filter, indicator='TOTN_winter') 
    
    q_factor = qf_NP.get_quality_factor(tolerance_filter)
    
    
    # Parameter
    print('-'*nr_marks)
    print('done')
    print('-'*nr_marks)
    
    
    
    
    
    
    
    
    
    