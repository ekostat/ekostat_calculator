# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 14:57:56 2017

@author: a002028
"""
import pandas as pd
import numpy as np
import core
import os, sys
import uuid

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
    def get_mapping(self, item=None, from_column=None, to_column=None):
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
            
        """ 
        result = self.mapping_file.loc[self.mapping_file[from_column]==item, to_column]
        if len(result):
            return result.values[0]
        return item



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
        """
        Created     ????????    by Johannes Johansson
        Updated     20180222    by Magnus Wenzer
        """
        
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
    def get_water_body_list(self):
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        Returns a list with all water bodies. 
        """
        return sorted(set(self.water_bodies['NAME']))
    
    #==========================================================================
    def get_type_area_list(self):
        """
        Created     20180222    by Magnus Wenzer
        Updated     20180222    by Magnus Wenzer
        
        Returns a list with all type areas. 
        """
        return sorted(set(self.water_bodies['TYPE_AREA_NUMBER']))
    
        
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
        
        
"""
#==============================================================================
#==============================================================================
""" 
class QualityElement(object): 
    """
    Created     20180222    by Magnus Wenzer
    Updated     20180222    by Magnus Wenzer
    
    """ 
    
    def __init__(self, file_path): 
        self.file_path = file_path
        self.cf_df = pd.read_csv(self.file_path, sep='\t', dtype='str', encoding='cp1252')
        assert all(['quality element' in self.cf_df.keys(), 'indicator' in self.cf_df.keys(), 'parameters' in self.cf_df.keys()]), 'configuration file must contain quality element, indicator and parameters information'
        self.cfg = {}
        self.cfg['quality elements'] = self.cf_df.groupby('quality element')['indicator'].unique()
        self.cfg['indicators'] = self.cf_df.groupby('indicator')['parameters'].unique() 
    
    
    #==========================================================================
    def get_quality_element_list(self):
        return sorted(self.cfg['quality elements'].keys())
    
    
    #==========================================================================
    def get_indicator_list_for_quality_element(self, quality_element):
        return sorted(self.cfg['quality elements'][quality_element])
    
    
"""
#==============================================================================
#==============================================================================
""" 
class RawDataFiles(object): 
    """
    Class to hold information in dtype_settings.txt based on the file 
    content in the rad_data-directory of the workspace. 
    Also keeps and handles information about active files. 
    """
    def __init__(self, raw_data_directory): 
        self.raw_data_directory = raw_data_directory.replace('\\', '/') 
        self.info_file_name ='dtype_settings.txt'
        self.info_file_path = '/'.join([self.raw_data_directory, self.info_file_name])
        
        self.has_info = False
        self.load_and_sync_dtype_settings() 
        
        
        
    #==========================================================================
    def load_and_sync_dtype_settings(self): 
        """
        Loads the infofile and check if all links and info is present. 
        Returns True if all is ok, else False. 
        """
        if not os.path.exists(self.info_file_path): 
            print('No dtype_setting file found in raw_data directory')
            return False
        
        # Load info file
        self.df = pd.read_csv(self.info_file_path, sep='\t', dtype={'status': int, 
                                                                    'filename': str, 
                                                                    'data_type': str}) 
        self.has_info = True
        
        # List all files
        all_file_names = sorted([item for item in os.listdir(self.raw_data_directory) if item != os.path.basename(self.info_file_path)])
        
        # Check that all files are in info file
        if sorted(self.df['filename']) != all_file_names:
            print('='*50)
            print('\n'.join(sorted(self.df['filename'])))
            print('.'*50)
            print('\n'.join(all_file_names))
            print('-'*50)
            print('All files not in dtype_settings file!') 
            return False
        
        # Check that all data_types are present 
        if not all(self.df['data_type']):
            print('dtype not specified for all files!') 
            return False 
        
        return True
        
    #==========================================================================
    def get_active_paths(self): 
        if not self.has_info:
            return False
        return sorted(['/'.join([self.raw_data_directory, item]) for item in self.df.loc[self.df['status']==1, 'filename']])
   
    #==========================================================================
    def get_active_paths_with_data_type(self):
        if not self.has_info:
            return False
        file_paths = self.get_active_paths() 
        output_list = []
        for file_path in file_paths:
            dt = self.df.loc[self.df['filename']==os.path.basename(file_path), 'data_type'].values[0]
            output_list.append((file_path, dt))
        return output_list
        
    
    #==========================================================================
    def activate(self, file_list): 
        """
        Activates the given filenames and deactivate the rest. Returns True if all ok. 
        Returns False if filename is missing. 
        file_list is a list with strings. 
        """
        file_list = [os.path.basename(item) for item in file_list] 
        for file_name in file_list: 
            print(file_name)
            if file_name not in self.df['filename'].values: 
                return False
            
        for file_name in self.df['filename']:
            if file_name in file_list:
                self.df.loc[self.df['filename']==file_name, 'status'] = 1
            else:
                self.df.loc[self.df['filename']==file_name, 'status'] = 0 
                           
        # Save file 
        self._save_file()
        return True
        
        
    #==========================================================================
    def add_file(self, file_name=None, data_type=None): 
        """
        Takes tha basname of the file_name (Could be path) and adds it to the file. 
        """
        assert all([file_name, data_type]), 'Not enough input arguments' 
        
        file_name = os.path.basename(file_name)
        if file_name in self.df['filename'].values: 
            print('File already added')
            return False
        next_index = len(self.df) 
        self.df.iloc[next_index] = [1, file_name, data_type]
        return True
        
    #==========================================================================
    def _save_file(self):
        self.df.to_csv(self.info_file_path, index=False, sep='\t')
        
#==========================================================================
#==========================================================================
class UUIDmapping():
    """
    Holds the mapping file fro uuid. 
    """
    def __init__(self, file_path=None): 
        self.file_path = file_path
        self.all_status = ['editable', 'readable', 'deleted']
        self._load_file()
        
        
    #==========================================================================
    def _load_file(self): 
        print('FILE_PATH:', self.file_path)
        self.df = pd.read_csv(self.file_path, sep='\t')
        
        
    #==========================================================================
    def _save_file(self): 
        self.df.to_csv(self.file_path, sep='\t', index=False)
        
        
    #==========================================================================
    def _get_status_list(self): 
        return sorted(set(self.df['status']))
        
    
    #==========================================================================
    def add_new_uuid_for_alias(self, alias=None, user_id=None): 
        """
        Adds a new uuid to the mapping file and returns its value. 
        """
        print('¤', alias)
        print('¤', user_id)
        status = self.all_status
        if self.get_uuid(alias, user_id, status=status): 
            return False 
        
        unique_id = str(uuid.uuid4())
#        print('&&&&&')
#        print(unique_id)
#        print(alias)
#        print(user_id)
        add_df = pd.DataFrame([[unique_id, alias, user_id, 'editable', 'True']], columns=['uuid', 'alias', 'user_id', 'status', 'active'])
        self.df = self.df.append(add_df)
        self.df = self.df.reset_index(drop=True)
        self._save_file()
        return unique_id
    
    
    #==========================================================================
    def get_alias(self, unique_id, status=None): 
        if not status:
            status = self.all_status
            
#        print('status', status)
        result = self.df.loc[(self.df['uuid']==unique_id) & \
                             (self.df['status'].isin(status)), 'alias']
        if len(result):
            return result.values[0]
        return False
        
    
    #==========================================================================
    def get_status(self, alias=None, user_id=None, unique_id=None): 
        if unique_id:
            result = self.df.loc[self.df['uuid']==unique_id, 'status']
        else:
            result = self.df.loc[(self.df['alias']==alias) & \
                                 (self.df['user_id']==user_id), 'status']
        if len(result):
            return result.values[0]
        return False
    
    #==========================================================================
    def get_user_id(self, unique_id, status=None): 
        if not status:
            status = self.all_status 
        result = self.df.loc[(self.df['uuid']==unique_id) & \
                             (self.df['status'].isin(status)), 'user_id']
        if len(result):
            return result.values[0]
        return False
                 
    #==========================================================================
    def get_uuid(self, alias=None, user_id=None, status=None): 
        if not status:
            status = self.all_status
        result = self.df.loc[(self.df['alias']==alias) & \
                             (self.df['user_id']==user_id) & \
                             (self.df['status'].isin(status)), 'uuid']
        if len(result):
            return result.values[0]
        return False
        
    
    #==========================================================================
    def get_alias_list_for_user(self, user_id, status=None): 
        if not status:
            status = self.all_status
        return list(self.df.loc[(self.df['user_id']==user_id) & \
                                (self.df['status'].isin(status)), 'alias'])
    
    
    #==========================================================================
    def get_uuid_list_for_user(self, user_id, status=None): 
        if not status:
            status = self.all_status 
        return list(self.df.loc[(self.df['user_id']==user_id) & \
                                (self.df['status'].isin(status)), 'uuid'])
        
    
    #==========================================================================
    def is_active(self, unique_id):
        result = self.df.loc[self.df['uuid']==unique_id, 'active']
        if len(result):
            result = str(result.values[0]).lower()
            if result == 'true':
                return True
            elif result == 'false':
                return False 
        return None
    
    
    #==========================================================================
    def permanent_delete_uuid(self, unique_id):
        self.df = self.df.drop(self.df.index[self.df['uuid']==unique_id])
        self._save_file()
        
        
    #==========================================================================
    def set_active(self, unique_id): 
        self.df.loc[self.df['uuid']==unique_id, 'active'] = 'True'
        
    
    #==========================================================================
    def set_inactive(self, unique_id): 
        self.df.loc[self.df['uuid']==unique_id, 'active'] = 'False'
        
        
    #==========================================================================
    def set_alias(self, unique_id, new_alias): 
        user_id = self.get_user_id(unique_id)
        if new_alias in self.get_alias_list_for_user(user_id):
            return False
        self.df.loc[self.df['uuid']==unique_id, 'alias'] = new_alias
        self._save_file()
        return True
        
    
    #==========================================================================
    def set_new_uuid(self, current_uuid):
        new_uuid = str(uuid.uuid4())
        self.df.loc[self.df['uuid']==current_uuid, 'uuid'] = new_uuid
        self._save_file()      
        return new_uuid
    
    
    #==========================================================================
    def set_status(self, unique_id, status): 
        self.df.loc[self.df['uuid']==unique_id, 'status'] = status
        self._save_file() 
        return status
    
    
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
    

