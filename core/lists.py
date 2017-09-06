# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 12:43:26 2017

@author: a001985
"""
import os 

import utils 



###############################################################################
@utils.singleton
class StationList(object): 
    """
    Singleton to hold station information. 
    """
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            return
        self.file_path = file_path 
        self.file_object = utils.TextColumnFile('r')
        self.file_object.read(file_path)
        self.data = self.file_object.data
        
        self.data['STATION'] = [item.replace('  ', ' ') for item in self.data['STATION']]
        
        self._create_dicts()
        
    def _create_dicts(self): 
        self.statn_in_type_area = {}
        for statn, type_egen in zip(self.data['STATION'], self.data['TYP_EGEN']):
            if type_egen not in self.statn_in_type_area.keys():
                self.statn_in_type_area[type_egen] = []
            self.statn_in_type_area[type_egen].append(statn)
    
    

###############################################################################
@utils.singleton
class ParameterList(object): 
    """
    Singleton to hold parameter information. 
    """
    def __init__(self):
        self.metadata_list = ['MYEAR', 'SDATE', 'STIME', 'MONTH', 'STATN', 'LATIT', 'LONGI', 'DEPH']
    
    
    
###############################################################################
@utils.singleton
class AreaList(object): 
    """
    Singleton to hold area information. 
    """
    def __init__(self):
        pass
    
###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "lists.py"')
    print('-'*50)
    print('')
    
    root_directory = os.path.dirname(os.path.abspath(__file__))
    StationList(root_directory + '/test_data/Stations_inside_med_typ_attribute_table_med_delar_av_utsjö.txt')
    
    
    
    