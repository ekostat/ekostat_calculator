# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 18:24:19 2018

@author: a001985
"""
import requests
import pathlib
import urllib 

class SharkWebReader():
    """ """
    def __init__(self, 
                 sharkweb_url='https://sharkweb.smhi.se',
                 debug=False):
        """ """
        self.sharkweb_url = sharkweb_url
        self.debug = debug
        self.clear()
    
    def clear(self):
        """ """
        self.options = {}
        self.location_options = {}
        self.view_options = {}
        self.data_params = {
            # Time.
            'year_from': '', 
            'year_to': '', 
            'month_list': [], 
            
            # Position.
            'bounds': '', 
            'county_list': [], # Example: ['Blekinge län', 'Kalmar län']
            'municipality_list': [], 
            'water_district_list': [], 
            'svar_sea_area_list': [], 
            'water_category': [], 
            'type_area_list': [], 
            'sea_basin': [], 
            'helcom_ospar': [], 
            'economic_zone': [], 
            
            # Standard search. 
            'datatype': '', 
            'parameter': '', 
            'station_name': '', 
            'station_name_option': '', 
            'taxon_name': '', 
            'taxon_name_option': '', 
            
            # Advanced search.
            'adv_datatype_list': '', 
            'adv_parameter_list': '', 
            'adv_deliverer_list': '', 
            'adv_orderer_list': '', 
            'adv_project_list': '', 
            'adv_dataset_name': '', 
            'adv_dataset_name_option': '', 
            'adv_check_status': '', 
            'adv_checked_by_list': '', 
            'adv_quality_flag_list': '', 
            'adv_min_depth': '', 
            'adv_max_depth': '', 
            'adv_red_list_category': '', 
            
            # Selected columns.
            'sample_table_view': 'sample_col_std', 
            
            # Not used for data download.
            # 'limit"': '', 
            # 'db_read_offset': '', 
            
            # File format.
            'delimiters': 'point-tab', 
            'lineend': 'unix', 
            'encoding': 'utf-8', 
            'headerlang': 'internal', 
        }
        self.data = None
    
    def set_data_params(self, data_params):
        """ """
        self.data_params = data_params
        
    def get_data_params(self):
        """ """
        return self.data_params
    
    def get_options(self):
        """ """
        return self.options
    
    def get_view_options(self):
        """ """
        return self.view_options
    
    def get_location_options(self):
        """ """
        return self.location_options
    
    def read_options(self):
        """ """
        url = self.sharkweb_url + '/shark_php.php?action=get_options'
        r = requests.get(url)
        self.options = r.json()
        
        if self.debug:
            print('DEBUG: Status: ', r.status_code)
            print('DEBUG: Header: ', r.headers['content-type'])
            print('DEBUG: Encoding: ', r.encoding)

    def read_view_options(self):
        """ """
        url = self.sharkweb_url + '/shark_php.php?action=get_shark_settings&settings_key=sample_view_list_json'
        r = requests.get(url)
        self.view_options = r.text
        
        if self.debug:
            print('DEBUG: Status: ', r.status_code)
            print('DEBUG: Header: ', r.headers['content-type'])
            print('DEBUG: Encoding: ', r.encoding)

    def read_location_options(self):
        """ """
        url = self.sharkweb_url + '/shark_php.php?action=get_location_options'
        r = requests.get(url)
        self.location_options = r.json()
        
        if self.debug:
            print('DEBUG: Status: ', r.status_code)
            print('DEBUG: Header: ', r.headers['content-type'])
            print('DEBUG: Encoding: ', r.encoding)
        
    def read_data(self, data_params=None):
        """ """
        url = self.sharkweb_url + '/shark_save.php?action=download_sample'
        #
        params = data_params
        if params is None:
            params = self.data_params
            
        # 
        self.encodeURIComponent(params, 'month_list')
        self.encodeURIComponent(params, 'adv_datatype_list')
        self.encodeURIComponent(params, 'adv_parameter_list')
        self.encodeURIComponent(params, 'adv_deliverer_list')
        self.encodeURIComponent(params, 'adv_orderer_list')
        self.encodeURIComponent(params, 'adv_project_list')
        self.encodeURIComponent(params, 'county_list')
        self.encodeURIComponent(params, 'municipality_list')
        self.encodeURIComponent(params, 'water_district_list')
        self.encodeURIComponent(params, 'svar_sea_area_list')
        self.encodeURIComponent(params, 'water_category')
        self.encodeURIComponent(params, 'type_area_list')
        self.encodeURIComponent(params, 'sea_basin')
        self.encodeURIComponent(params, 'helcom_ospar')
        self.encodeURIComponent(params, 'economic_zone')
        # print(params)
        
        #
        r = requests.get(url, params)
        self.data = r.text
        
        if self.debug:
            print('DEBUG: Status: ', r.status_code)
            print('DEBUG: Header: ', r.headers['content-type'])
            print('DEBUG: Encoding: ', r.encoding)
    
    def save_data(self, file_name='sharkweb_data.txt'):
        """ """
        if self.data is None:
            if self.debug:
                print('DEBUG: No data available.')
            return
        #
        file_path = pathlib.Path(file_name)
        with file_path.open('w') as f:
            f.write(self.data)
    
    def encodeURIComponent(self, params, key):
        """ """
        string = '[or]'.join(params[key])
        string = urllib.parse.quote(string, safe='~()*!.\'\\')
        params[key] = string