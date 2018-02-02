# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 12:02:17 2018

@author: a002028
"""

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
sys.path.append(current_path)

import json
import core



"""
#==============================================================================
#==============================================================================
"""    
class jsonHandler(object):
    """
    - Import json
    - Export to json
    - Find dictionary within json file based on a specific key 
    - Add elements to dictionary
    - Fill up json/dictionary structure with relevant/desired information
    """
    def __init__(self):
        pass
#        self._initiate_attributes()
#        self.json_file_path()


    #==========================================================================
    def _initiate_attributes(self):
        """
        """
        pass
        
        
    #==========================================================================
    def _initiate_outfile(self):
        """
        json files can save multiple dictionaries stored in a list
        """
        
        self.out_file = []
                        
    #==========================================================================
    def _check_key(self, key):
        """
        """
        list(self.find_key(key, self.json_file))
        return 
        
        
    #==========================================================================
    def add_element(self, main_key='', label='', value=''):
        """
        """
        self._check_key(main_key)
        list(self.find_key(main_key, self.json_file))
        
        
        
        self.json_file[main_key]

    #==========================================================================
    def update_element(self, main_key='', label='', value=''):
        """
        """
        
        
    #==========================================================================
    def append_dict_to_outfile(self, dictionary=None):
        """
        Append dict to out_file (list)
        Not necessary if we only want to save 
        """
        
        if not hasattr(self, 'out_file'):
            self._initiate_outfile()
            
        self.out_file.append(dictionary)
        
        
    #==========================================================================
    def export(self, out_source='', out_file=None):
        """
        """
        
        if out_file:
            core.Export().export_json(out_source=out_source, 
                                      data_dict=out_file)
            
        elif hasattr(self, 'out_file'):
            core.Export().export_json(out_source=out_source, 
                                      data_dict=self.out_file)

        elif hasattr(self, 'json_file'):
            core.Export().export_json(out_source=out_source, 
                                      data_dict=self.json_file)
            
        else:
            raise UserWarning('No out file specified for export to .json')
        
        
    #==========================================================================
    def find_key(self, key, dictionary):
        """
        Generator to find an element of a specific key.
        Note that a key can occur multiple times in a nested dictionary.
        """
        
        if isinstance(dictionary, list):
            for d in dictionary:
                for result in self.find_key(key, d):
                    yield result
                    
        else:            
            for k, v in dictionary.items():
                if k == key:
                    yield v
                elif isinstance(v, dict):
                    for result in self.find_key(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in self.find_key(key, d):
                            yield result
                        
                        
    #==========================================================================
    def get_dict(self, key=None):
        """
        Find a dictionary based on a specific key within the target dictionary
        """
        
        if isinstance(self.json_file, list):
            for element in self.json_file:
                if key in element:
                    return element
                
            UserWarning('KEY: '+ key + ' not in json file')
            
        elif isinstance(self.json_file, dict):
            if key in self.json_file:
                return self.json_file.get(key)
            else:
                UserWarning('KEY: '+ key + ' not in json file')
                
        else:
            raise UserWarning('The intended use of a json file has an unrecognizable format', 
                              type(self.json_file))


    #==========================================================================
    def load(self, file_path=u''):
        """
        """
        
        self.json_file = core.Load().load_json(file_path=file_path)
    
       
    #==========================================================================


"""
#==============================================================================
#==============================================================================
"""      
class DictionaryStructure(object):
    """
    Set up a default nested dictionary structure based on a json file
    Not used..
    """
    def __init__(self):
        self._initiate_attributes()
        
    
    #==========================================================================
    def _initiate_attributes(self):
        """
        """
        pass
#        self.dict = {}
    
    
    #==========================================================================
    def load_structure(self, file_path=u''):
        """
        """
        
#        self.dict = core.Load().load_json(file_path=file_path)
        with open(file_path, 'r') as f:
            self.dict = json.load(f)
    
    
    #==========================================================================

"""
#==============================================================================
#==============================================================================
"""   
if __name__ == '__main__':
    print('='*50)
    print('Running...')
    print('-'*50)
    
    
    
    root_directory = os.path.dirname(os.path.abspath(__file__))[:-4]
    
    print(root_directory)
    
    report_json_path = root_directory + 'resources\\default_json\\report.json'
    sample_json_path = root_directory + 'resources\\default_json\\sample.json'

    json_handler = jsonHandler()
    
#    json_handler.load(file_path=report_json_path)
    json_handler.load(file_path=sample_json_path)

#    pprint(list(json_handler.find_key('available_water_bodies', json_handler.json_file.get('available_water_bodies')))) # use pprint instead of print, bra grejer :)
    
    list(json_handler.find_key('selected_period', json_handler.json_file))
#    json_handler.get_dict(key='available_supporting_elements')
#    json_handler.export(out_source='sample_sample.json', out_file=d)
    


#    list(json_handler.find_key('available_water_bodies', json_handler.json_file))[0]

#    data = {
#            'KEY_A':'test',
#            'KEY_F':{},
#            'KEY_C':[],
#            'KEY_B':'',
#            'KEY_D':None,
#            'KEY_E':True,            
#            'KEY_AA':[2,35,78,58,454444],
#            'KEY_R':{'key_2':[3,4,54,65],
#                     'key_1':44}
#            }
#    data_2 = {'K':[1,2,3,4,5,6,7,0],
#              'J':{'test':'TRUE'}}
#    
#    array = [data, data_2]
#    
#    fid = 'json_outfile'
#    
#    exports = core.Export().export_json(data_dict=array, out_source='D:/Temp/'+fid)
##    exports.export_json(data_dict = array, out_source='D:/Temp/'+fid)
#
#    json_object = jsonHandler()
#    json_object.load(file_path='D:/Temp/'+fid)#+'.json')
#
##    dd = json_object.get_dict(json_object.json_file, key_in_dict='KEY_A')
#    dd = json_object.get_dict(key_in_dict='KEY_A')

    print('-'*50)
    print('done')
    print('-'*50)
  