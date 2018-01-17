# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 14:57:56 2017

@author: a002028
"""
import pandas as pd
import numpy as np
import core
import os, sys

#if current_path not in sys.path: 
#    sys.path.append(os.path.dirname(os.path.realpath(__file__)))


"""
#==============================================================================
#==============================================================================
""" 
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
#            array = [v for v in array if v] # if you are using '' as nan value
#            array = array[np.logical_and(array!='', ~pd.isnull(array))] 
            if len(array)==1:
                array = array[0]
            setattr(self, key, array)

    #==========================================================================
    def add_corresponding_arrays(self, df=None, first_key=u'', 
                                 second_key=u'', match_key=u''):
        """
        Ex. Add arrays of all water bodies within a specific type area (key)
        """
        for value in df[first_key].unique():
            array = self._get_array_from_df(df=df, 
                                            key_a=match_key, 
                                            key_b=first_key, 
                                            match=value)
            setattr(self, value, sorted(array))
            
        if second_key: 
            df['temp_key'] = np.array([a+b for a,b in zip(df[first_key].values, 
                                      df[second_key].values)])
    
            for value in np.unique(df['temp_key']):
                if value not in self:
                    array = self._get_array_from_df(df=df, 
                                                    key_a=match_key, 
                                                    key_b='temp_key', 
                                                    match=value)
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
        for i, value in enumerate(df[first_key].values):
            setattr(self, value.strip(), {key: df[key][i] for key in key_list})
                    
    #==========================================================================
    def keys(self):
        return list(self.__dict__.keys())
        
    #==========================================================================
    def get(self, key):
        try:
            return getattr(self, key.lower())
        except: 
            return getattr(self, key)
    
    #==========================================================================
    def _get_array_from_df(self, df=None, key_a=u'', key_b=u'', match=None):
#        print(type(df[key_a]), type(df[key_a][0]))
#        return df[key_a].loc[df[key_b].isin([match])].values.str.strip()
        return [x.strip() for x in df[key_a].loc[df[key_b].isin([match])].values]
#        return [x.strip() for x in df[key_a].iloc[np.where(df[key_b]==match)].values]
        
    #==========================================================================
    def get_list(self, key_list):
        return list(self.get(key) for key in key_list)
        
    #==========================================================================
    def get_mapping_dict(self, key_list):
        return dict(list((key, self.get(key)) for key in key_list))
        
    #==========================================================================
    def __getitem__(self, key):
        return getattr(self, key)
    
    #==========================================================================




"""
#==============================================================================
#==============================================================================
""" 
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




"""
#==============================================================================
#==============================================================================
"""    
class WaterBody(AttributeDict):
    """
    Object to hold information on water bodies and type areas
    - get various info for each water body 
    - get list on different water bodies within a specific type area
    """
    def __init__(self, **kwargs):
        super().__init__()
        
        #TODO Add Parametermapping for water body names
        #TODO Map against .lower() letters 
        if kwargs:
            self.load_water_body_match(**kwargs)
            
    #==========================================================================
    def load_water_body_match(self, file_path=u'', sep='\t', encoding='cp1252'):
        
        water_bodies = core.Load().load_txt(file_path, sep=sep, 
                                                 encoding=encoding, 
                                                 fill_nan=u'')
        
        key_list = list(water_bodies.keys())
        key_list.remove(u'NAME')
        
        self.add_info_dict(df=water_bodies, 
                           first_key=u'NAME',
                           key_list=key_list)
        
        self.add_corresponding_arrays(df=water_bodies,
                                      first_key=u'TYPE_AREA_NUMBER', 
                                      second_key=u'TYPE_AREA_SUFFIX',
                                      match_key=u'NAME')
        
    #==========================================================================
    def get_water_bodies_in_type_area(self, type_area):
        return self.get(type_area)
    
    #==========================================================================
    def get_type_area_for_water_body(self, wb, include_suffix=False, 
                                     key_number=u'TYPE_AREA_NUMBER', 
                                     key_suffix=u'TYPE_AREA_SUFFIX'):
        if include_suffix:
            string = self.get(wb).get(key_number) + '-' + \
                     self.get(wb).get(key_suffix)
            return string.strip('-')
        else:
            return self.get(wb).get(key_number)
    
    #==========================================================================
    def get_type_area_suffix_for_water_body(self, wb, key=u'TYPE_AREA_SUFFIX'):
        return self.get(wb).get(key)
    
    #==========================================================================
    def get_eu_cd_for_water_body(self, wb, key=u'EU_CD'):
        return self.get(wb).get(key)

    #==========================================================================
    def get_basin_number_for_water_body(self, wb, key=u'BASIN_NUMBER'):
        return self.get(wb).get(key)
        
    #==========================================================================
    def get_hid_for_water_body(self, wb, key=u'HID'):
        return self.get(wb).get(key)
        
    #==========================================================================
    def get_url_viss_for_water_body(self, wb, key=u'URL_VISS'):
        return self.get(wb).get(key)
        
    #==========================================================================
    def get_center_position_for_water_body(self, wb, key_lat=u'CENTER_LAT', 
                                           key_lon=u'CENTER_LON'):
        return {'lat': self.get(wb).get(key_lat),
                'lon': self.get(wb).get(key_lon)}
        
    #==========================================================================
    
    
    
"""#========================================================================"""
if __name__ == '__main__':
    current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
    sys.path.append(current_path)
    print('='*50)
    print('Running module "mapping.py"')
    print('-'*50)
    print('')
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    source_dir = u'D:\\Utveckling\\GitHub\\ekostat_calculator\\'

    first_filter_directory = source_dir + 'resources/mappings/mapping_parameter_dynamic_extended.txt'
    fields_filter_directory = source_dir + '/resources/filters/filter_fields_zoobenthos.txt'
    water_body_match_directory = source_dir + 'resources/mappings/water_body_match.txt' 
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    # Mapping
    print('\n# Mapping')
    p_map = ParameterMapping()
    p_map.load_mapping_settings(file_path=first_filter_directory)
    print(p_map.map_parameter_list(['myear', u'ammonium nh4-n']))
    print(p_map.get_parameter_mapping(['myear', u'ammonium nh4-n']))
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    f_filter = AttributeDict()
    data = core.Load().load_txt(fields_filter_directory, fill_nan=u'')
    f_filter._add_arrays_to_entries(**data)
#    print('compulsory_fields',f_filter.compulsory_fields)
#    print('parameter_key',f_filter.parameter_key)
#    print('sort_by_fields',f_filter.sort_by_fields)
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    # Water Body Match
    print('\n# Water Body Match')
#    wb_match = WaterBody()
#    wb_match.load_water_body_match(file_path=water_body_match_directory)
##    print(wb_match.dict.get('S. Seskaröfjärden sek namn').get('TYP'))
#    print(wb_match.get_type_area_for_water_body('Vändelsöarkipelagen', include_suffix=True))
#    print('='*50)
#    print(wb_match.get_basin_number_for_water_body('Vändelsöarkipelagen'))
#    print('='*50)
#    print(wb_match.get_eu_cd_for_water_body('Vändelsöarkipelagen'))
#    print('='*50)
#    print(wb_match.get_hid_for_water_body('Vändelsöarkipelagen'))
#    print('='*50)
#    print(wb_match.get_url_viss_for_water_body('Vändelsöarkipelagen'))
#    print('='*50)
#    print(wb_match.get_center_position_for_water_body('Vändelsöarkipelagen'))
#    print('='*50)
#    print(wb_match.get_water_bodies_in_type_area('1n'))
#    print('='*50)
#    print(wb_match.get_water_bodies_in_type_area('1s'))
#    print('='*50)
#    print(wb_match.get_water_bodies_in_type_area('1'))
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    print('-'*50)
    print('done')
    print('-'*50)
#    for k in p_map.keys():
#        if k.startswith('sili'):
#            print(k, len(k), p_map.get(k))
    
