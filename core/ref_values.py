# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 15:13:24 2017

@author: a001985
"""
import codecs
import numpy as np

import utils


###############################################################################
class RefTypeArea(dict):
    """
    Hold reference values for a specific "type area" and parameter. 
    """
    
    def __init__(self, info_dict): 
        for key in info_dict.keys():
            value = info_dict[key]
            if key == 'Month': 
                value = sorted([int(item) for item in value.strip('"').split(';')])
            elif key == 'Type Area':
                pass
            else:
                try:
                    value = float(value)
                except:
                    pass
            self[key] = value
            
        self.type_area = self['Type Area']
        self.ekv_ref = self['EKV Ref']
        
    #==========================================================================
    def is_matching_month_list(self, month_list):
        if sorted(month_list) == self['Month']:
            return True
        return False
    
    #==========================================================================
    def get_max_salinity(self, s=None):

        if s != None:
            if np.isnan(s):
                return s
            else:
                return np.min([s, self['Salinity max']])
        else:
            return self['Salinity max']
    
    #==========================================================================
    def get_ref_value(self, s):
        """
        Returns the reference value acording to "EKV Ref". 
        For now value is calculated via the eval statement. 
        """
        return eval(self.ekv_ref)
    
    #==========================================================================
    def get_num_class(self, ek_calc):
        """
        Calculates indicator class (Nklass) according to eq 2.1 in HVMFS 2013:19.
        Returns a tuple with four values, low, ek_low, ek_heigh and the resulting Nklass.
        This is specific for the nutrient indicators.
        There needs to be:
            - one def to get nutrient num_class for nutrient indicators (this one as is)
            - one def to get indicator class and value with the indicator specific EQR and the EQR transformed to the common scale
            (for nutrients that is num_class on scale 0-4.99 for most others some values on a 0-1 scale)
        """
        if ek_calc > self['EK H/G']: 
            n_low = 4 
            ek_high = 1
            ek_low = self['EK H/G']
            
        elif ek_calc > self['EK G/M']:
            n_low = 3 
            ek_high = self['EK H/G']
            ek_low = self['EK G/M']

        elif ek_calc > self['EK M/O']:
            n_low = 2 
            ek_high = self['EK G/M']
            ek_low = self['EK M/O']
            
        elif ek_calc > self['EK O/D']:
            n_low = 1 
            ek_high = self['EK M/O']
            ek_low = self['EK O/D']
            
        else:
            n_low = 0 
            ek_high = self['EK O/D']
            ek_low = 0
        
        return n_low, ek_low, ek_high, n_low + (ek_calc - ek_low)/(ek_high-ek_low)

###############################################################################     
class ParameterRefTypeAreas(dict):
    """
    Class to hold all type areas for a parameter. 
    """
    def __init__(self, parameter=None, file_path=None): 
        self.parameter = parameter
        if file_path:
            self.load_txt_file(file_path)
            
    #==========================================================================
    def load_data_dict(self, data_dict): 
        pass
    
    #==========================================================================
    def load_txt_file(self, file_path): 
        fid = codecs.open(file_path, 'r', encoding='cp1252')
        for k, line in enumerate(fid):
            split_line = [item.strip() for item in line.split('\t')]
            if k == 0:
                header = split_line
            else:
                line_dict = dict(zip(header, split_line))
                self[line_dict['Type Area']] = RefTypeArea(line_dict)
        fid.close()
    
###############################################################################    
@utils.singleton 
class RefValues(object):

    def __init__(self): 
        pass
    
    #==========================================================================
    def add_ref_parameter_from_file(self, par, file_path): 
        setattr(self, par.lower(), ParameterRefTypeAreas(parameter=par, 
                                                         file_path=file_path))
        
###############################################################################    
#@utils.singleton
#class DINRefTypeAreas(ParameterRefTypeAreas): 
#    """
#    Holds information about reference values for DIN per type area. 
#    """
#    def __init__(self): 
#        super().__init__(parameter='DIN') 
#        
################################################################################     
#@utils.singleton
#class TNRefTypeAreas(ParameterRefTypeAreas): 
#    """
#    Holds information about reference values for DIN per type area. 
#    """
#    def __init__(self): 
#        super().__init__(parameter='TN') 
    
    
###############################################################################     
def create_type_area_object():
    """
    Creates parameter type area singletons for 
    """  
    RefValues()
    RefValues().add_ref_parameter_from_file('DIN_winter', 'D:/Utveckling/g_EKOSTAT_tool/test_data/din_vinter.txt')
    RefValues().add_ref_parameter_from_file('TOTN_winter', 'D:/Utveckling/g_EKOSTAT_tool/test_data/totn_vinter.txt')
    
#    DINRefTypeAreas()
#    DINRefTypeAreas().load_txt_file('D:/Utveckling/g_EKOSTAT_tool/test_data/din_vinter.txt')
#    
#    TNRefTypeAreas()
#    TNRefTypeAreas().load_txt_file('D:/Utveckling/g_EKOSTAT_tool/test_data/totn_vinter.txt.txt')
    
###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "ref_values.py"')
    print('-'*50)
    print('')
    
    create_type_area_object()
    
    ta = '22'
    s = 19
    print('-'*50)
    print('Type area', ta)
    print('-'*50)
    for key in RefValues().totn_winter['20'].keys():
        if key == 'Type Area':
            continue
        print(key.ljust(30), RefValues().totn_winter['20'][key])
    print('Ref value for salinity %s psu:' %s, RefValues().totn_winter['20'].get_ref_value(s))
        
    print('-'*50)
    
    