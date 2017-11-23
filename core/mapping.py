# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 14:57:56 2017

@author: a002028
"""
import pandas as pd
import numpy as np
import core

"""#========================================================================"""
class AttributeDict(dict):
    """    
    Base class for attribute dictionary. 
    """
    def __init__(self): 
        super().__init__() 
                    
    #==========================================================================
    def _add_arrays_to_entries(self, **entries): 
        """
        """
        for key, array in entries.items():
            if len(array)==1:
                array = array[0]
            setattr(self, key, array)

    #==========================================================================
    def add_corresponding_arrays(self, df=None, first_key=u'', second_key=u'', match_key=u''):
        """
        """
        for value in df[first_key].unique():
            array = [wb.strip() for wb in \
                     df[match_key].iloc[np.where(df[first_key]==value)].values]
            setattr(self, value, sorted(array))

        merged = df.get(df[first_key]).astype(str).str.cat(df.get(second_key).astype(str), sep=u'')
        
        for value in merged.unique():
            if value not in self:
                array = [wb.strip() for wb in \
                         df[match_key].iloc[np.where(df[first_key]==value)].values]
                setattr(self, value, sorted(array))
        
    #==========================================================================
    def add_entries(self, **entries):
        """
        Turns elements in arrays into attributes with a corresponding official 
        field name 
        """
        for key, array in entries.items():
            setattr(self, key, key)
            setattr(self, key.lower(), key)
            for value in array.values:
                if not pd.isnull(value):
                    setattr(self, value.lower(), key)
                                      
    #==========================================================================
    def add_info_dict(self, df=None, first_key=u'', key_list=[]):
        """
        Adds values from "first_key"-array to attribute with a corresponding 
        dictionary of values from key_list-arrays
        
        """
        # As dictionary
        self.dict = dict()
        for i, value in enumerate(df[first_key].values):
            self.dict[value.strip()] = {key: df[key][i] for key in key_list}
            
        # As attributes.. 
#        for i, value in enumerate(df[first_key].values):  
#            setattr(self, value.replace.strip(),
#                    {key.lower(): df[key][i] for key in key_list})
                    
    #==========================================================================
    def keys(self):
        return list(self.__dict__.keys())
        
    #==========================================================================
    def get(self, key):
        return getattr(self, key.lower())
        
    #==========================================================================
    def get_list(self, key_list):
        return list(self.get(key) for key in key_list)
        
    #==========================================================================
    def get_mapping_dict(self, key_list):
        return dict(list((key, self.get(key)) for key in key_list))
        
    #==========================================================================
    def __getitem__(self, key):
        return getattr(self, key)
        

"""#========================================================================"""
class ParameterMapping(AttributeDict):
    """
    Load file to map data fields and parameters to a standard setting format
    """
    def __init__(self):
        super().__init__()
        
    #==========================================================================
    def load_mapping_settings(self, file_path=u'',sep='\t',encoding='cp1252'):
        """ Reading csv/txt files """
        self.mapping_file = core.Load().load_txt(file_path, sep=sep, 
                                                 encoding=encoding, 
                                                 fill_nan=u'')
        self.add_entries(**self.mapping_file)
        
    #==========================================================================
    def map_parameter_list(self, para_list, ext_list=False):
        return self.get_list(para_list)
        
    #==========================================================================
    def get_parameter_mapping(self, para_list, ext_list=False):
        return self.get_mapping_dict(para_list)
        
    #==========================================================================

"""#========================================================================"""    
class WaterBody(AttributeDict):
    """
    Object to hold information on water bodies and type areas
    - get various info for each water body 
    - get list on different water bodies within a specific type area
    """
    def __init__(self):
        super().__init__()
        
        #TODO Add Parametermapping for water body names ???
        
    #==========================================================================
    def load_water_body_match(self, file_path=u'', sep='\t', encoding='cp1252'):
        self.water_bodies = core.Load().load_txt(file_path, sep=sep, 
                                                 encoding=encoding, 
                                                 fill_nan=u'')
        
        key_list = list(self.water_bodies.keys())
        key_list.remove(u'NAME')
        
        self.add_info_dict(df=self.water_bodies, 
                           first_key=u'NAME',
                           key_list=key_list)
        
        self.add_corresponding_arrays(df=self.water_bodies,
                                      first_key=u'TYPE_AREA_NUMBER', 
                                      second_key=u'TYPE_AREA_SUFFIX',
                                      match_key=u'NAME')
        
    #==========================================================================
    def get_water_bodies_in_type_area(self, type_area):
        return self.get(type_area)
    
    #==========================================================================
    def get_type_area_for_water_body(self, wb):
        return self.dict.get(wb).get(u'TYP')
    
    #==========================================================================
    def get_eu_cd_for_water_body(self, wb):
        return self.dict.get(wb).get(u'EU_CD')

    #==========================================================================
    def get_bassin_number_for_water_body(self, wb):
        return self.dict.get(wb).get(u'Bassängsnummer')
        
    #==========================================================================
    def get_hid_for_water_body(self, wb):
        return self.dict.get(wb).get(u'HID')
        
    #==========================================================================
    def get_url_viss_for_water_body(self, wb):
        return self.dict.get(wb).get(u'URL_VISS')
        
    #==========================================================================
    def get_center_pos_for_water_body(self, wb):
        return {'lat': self.dict.get(wb).get(u'Mittpunkt lat WGS84 g/m/s'),
                'lon': self.dict.get(wb).get(u'Mittpunkt long WGS84 g/m/s')}
        
    #==========================================================================
    
"""#========================================================================"""
if __name__ == '__main__':
    print('='*50)
    print('Running module "mapping.py"')
    print('-'*50)
    print('')
    
    first_filter_directory = 'D:/Utveckling/GitHub/ekostat_calculator/resources/mappings/mapping_parameter_dynamic_extended.txt' 
    water_body_match_directory = 'D:/Utveckling/GitHub/ekostat_calculator/resources/mappings/water_body_match.txt' 
    
    # Mapping
    p_map = ParameterMapping()
    p_map.load_mapping_settings(file_path=first_filter_directory)
    print(p_map.map_parameter_list(['myear', u'ammonium nh4-n']))
    print(p_map.get_parameter_mapping(['myear', u'ammonium nh4-n']))
    
    # Water Body Match
    wb_match = WaterBody()
    wb_match.load_water_body_match(file_path=water_body_match_directory)
    print(wb_match.dict.get('S. Seskaröfjärden sek namn').get('TYP'))
    print(wb_match.get('24'))
    
    print('-'*50)
    print('done')
    print('-'*50)
#    for k in p_map.keys():
#        if k.startswith('sili'):
#            print(k, len(k), p_map.get(k))
    
