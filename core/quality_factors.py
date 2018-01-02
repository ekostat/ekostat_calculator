# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 14:43:35 2017

@author: a001985
"""
import os
import core 
import numpy as np

###############################################################################
class ClassificationResult(dict):
    """
    Class to hold result from a classification. 
    Jag kopierade denna från indicators.py
    """ 
    def __init__(self):
        super().__init__() 
        
        self['qualityfactor'] = None
        self['type_area'] = None
        self['status'] = None
        self['EQR'] = None
        self['qf_EQR'] = None
        self['all_ok'] = False
        
        self._set_attributes()
        
    #========================================================================== 
    def _set_attributes(self):
        for key in self.keys():
            setattr(self, key, self[key])
            
    #========================================================================== 
    def add_info(self, key, value): 
        self[key] = value
        setattr(self, key, value)
        

###############################################################################
class QualityFactorBase(object): 
    """
    Class to hold general information about quality factors. 
    """ 
    def __init__(self):
        self.name = '' 
        
        self._load_indicators()
        self.indicator_list = []
        self.class_result = None
        
    
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
            attr.set_data_handler(data_handler = data_handler, parameter = parameter) 
            # parameter could be None here. If so, all parameters in the indicator will be assigned the data_handler. 
        elif data_handler:
            for key in self.indicator_list:
                attr = getattr(self, key.lower())
                attr.set_data_handler(data_handler = data_handler)
        return True
    
    
    #==========================================================================
    def filter_data(self, data_filter_object=None, indicator=None, parameter=None):
        """
        Filters data in Indicator objects
        data_filter_object is of type core.settings.FilterData
        If "data_filter_object" is given all indicators will be filtered using this filter. 
        If "data_filter_object_dict" is given the corresponding filter under its key will be used. 
        """
        if all([data_filter_object, indicator]):
            attr = getattr(self, indicator.lower())
            attr.filter_data(data_filter_object = data_filter_object, parameter = parameter)
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
        self.indicator_list = ['DIN_winter', 'TOTN_summer', 'TOTN_winter']
        self._load_indicators()
        
    #==========================================================================
    def _load_indicators(self): 
        """
        Make sure the attributes and items in self.indicator_list are matching.
        (not case sensitive)
        """        
        self.din_winter = core.IndicatorDIN() # winter modified by filter on months 
        self.totn_summer = core.IndicatorTOTN() # summer modified by filter on months 
        self.totn_winter = core.IndicatorTOTN() # 
    
    #==========================================================================
    def calculate_quality_factor(self, tolerance_filter):
        """
        5) EK vägs samman för ingående parametrar (tot-N, tot-P, DIN och DIP) enligt
        beskrivning nedan (6.4.2) för slutlig statusklassificering av hela kvalitetsfaktorn Näringsämnen.
        """
        """
        Ett medelvärde av de numeriska klassningarna (Nklass) beräknas för 
        DIN, DIP, tot-N, tot-P under vintern och ett medelvärde för tot-N, tot-P under sommaren. 
        Därefter beräknas medelvärdet av sommar och vinter, vilket blir den sammanvägda klassificeringen av näringsämnen. 
        Statusklassificeringen avgörs av medelvärdet för den numeriska klassningen enligt tabell 2.1, ett värde 0-4.99.
        Denna klassificering ska sedan omvandlas till skalan 0-1 med stegen 0.2 mellan statusklasserna. 
        Dessa värden kan sedan jämföras med övriga kvalitetsfaktorer och ingå i sammansvägningen.
        """
        class_result = ClassificationResult()
        class_result.add_info('qualityfactor', 'Nutrients')
        print('\t\tCalculating Indicator EK values.....')
        self.din_winter.calculate_ek_value(tolerance_filter, 'DIN_winter', 'DIN')
        self.totn_winter.calculate_ek_value(tolerance_filter, 'TOTN_winter', 'NTOT')
        self.totn_summer.calculate_ek_value(tolerance_filter, 'TOTN_summer', 'NTOT')
        print('\t\tIndicator EK values calculated')
        
        nklass_din_winter = self.din_winter.class_result['num_class'][-1]
        nklass_totn_winter = self.totn_winter.class_result['num_class'][-1]
        nklass_totn_summer = self.totn_summer.class_result['num_class'][-1]
        #qf_NP_summer = self.totn_summer.get_status(tolerance_filter)['num_class'][-1]
        
        nklass_qf_NP_winter = np.mean([nklass_totn_winter, nklass_din_winter])
        nklass_qf_NP_summer = np.mean([nklass_totn_summer])
        
        # TODO: add the rest of the indicators
        qf_nklass = np.mean([nklass_qf_NP_summer, nklass_qf_NP_winter])
        qf_EQR = {'qf_NP_winter': nklass_qf_NP_winter, 'qf_NP_summer': nklass_qf_NP_summer, 'qf_NP_EQR': qf_nklass}
        class_result.add_info('qf_EQR', qf_EQR)
        
        self.class_result = class_result
        
    #==========================================================================
    def get_EQR(self, tolerance_filter = None):
        """
        Calculates EQR from quality factor class (Nklass) according to eq. 1 in WATERS final report p 153.
        This can probabaly be moved to QualityFactorBase of the boundaries are retrieved from the RefValues object.
        """
        self.calculate_quality_factor(tolerance_filter)
        qf_EQR = getattr(self.class_result, 'qf_EQR')['qf_NP_EQR']

        if qf_EQR >= 4.99: 
            EQR = 1
            status = 'High'
        elif qf_EQR >= 4:
            EQR = 0.2*((qf_EQR-4)/(5-4)) + 0.8
            status = 'High'          
        elif qf_EQR >= 3:
            EQR = 0.2*((qf_EQR-3)/(4-3)) + 0.6
            status = 'Good'
        elif qf_EQR >= 2:
            EQR = 0.2*((qf_EQR-2)/(3-2)) + 0.4
            status = 'Moderate'
        elif qf_EQR >= 1: 
            EQR = 0.2*((qf_EQR-1)/(2-1)) + 0.2
            status = 'Poor'
        elif qf_EQR > 0:
            EQR = 0.2*((qf_EQR-0)/(1-0))
            status = 'Bad'
        elif qf_EQR == 0:
            EQR = 0
            status = 'Bad'
        else:
            raise('Error: NP Qualityfactor numeric class: {} incorrect.'.self.qf_num_class)
        
        self.class_result.add_info('EQR', EQR)
        self.class_result.add_info('status', status)
                
    #==========================================================================       
    def get_quality_factor(self, tolerance_filter):
        """
        Jag vet inte vad denna def behövs för.
        """
        #return self.totn_winter.get_status(tolerance_filter)
        pass
    
###############################################################################
if __name__ == '__main__':
    nr_marks = 60
    print('='*nr_marks)
    print('Running module "quality_factor.py"')
    print('-'*nr_marks)
    print('')
    
    
    root_directory = os.path.dirname(os.path.abspath(__file__))[:-9]
    
#    core.StationList(root_directory + '/test_data/Stations_inside_med_typ_attribute_table_med_delar_av_utsjö.txt')
    core.ParameterList()
    
    #--------------------------------------------------------------------------
    # Directories and file paths
    raw_data_file_path = root_directory + '/test_data/raw_data/data_BAS_2000-2009.txt'
    first_filter_data_directory = root_directory + '/test_data/filtered_data' 
    
    first_data_filter_file_path = root_directory + '/test_data/filters/first_data_filter.txt' 
    winter_data_filter_file_path = root_directory + '/test_data/filters/winter_data_filter.txt'
    
    tolerance_filter_file_path = root_directory + '/test_data/filters/tolerance_filter_template.txt'
    
    #--------------------------------------------------------------------------
    # Filters 
    first_filter = core.DataFilter('First filter', file_path=first_data_filter_file_path)
    winter_filter = core.DataFilter('winter_filter', file_path=winter_data_filter_file_path)
    winter_filter.save_filter_file(root_directory + '/test_data/filters/winter_data_filter_save.txt') # mothod available
    tolerance_filter = core.ToleranceFilter('test_tolerance_filter', file_path=tolerance_filter_file_path)

    #--------------------------------------------------------------------------
    # Reference values
    core.RefValues()
    core.RefValues().add_ref_parameter_from_file('DIN_winter', root_directory + '/test_data/din_vinter.txt')
    core.RefValues().add_ref_parameter_from_file('TOTN_winter', root_directory + '/test_data/totn_vinter.txt')
    
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    # Handler (raw data)
    raw_data = core.DataHandler('raw')
    raw_data.add_txt_file(raw_data_file_path, data_type='column') 
    
    # Use first filter 
    filtered_data = raw_data.filter_data(first_filter) 
    
    # Save filtered data (first filter) as a test
    filtered_data.save_data(first_filter_data_directory)
    
    
    # Load filtered data (first filter) as a test
    loaded_filtered_data = core.DataHandler('first_filtered')
    loaded_filtered_data.load_data(first_filter_data_directory)


    # Create and fill QualityFactor
    qf_NP = core.QualityFactorNP()
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
    
    
    
    
    
    
    
    
    
    