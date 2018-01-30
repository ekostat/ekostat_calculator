# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 12:02:17 2018

@author: a002028
"""

import json
#import core


"""
#==============================================================================
#==============================================================================
"""
class Export(object):
    """
    Handles different exports
    - excel
    - json
    - netcdf
    - text
    """
    #==========================================================================
    def __init__(self, out_source='', data={}):
        """
        """        
        self.out_source = out_source
    
    #==========================================================================
    def export_json(self, data_dict={}, indent=4):
        """
        """
        with open(self.out_source, "w") as outfile:
            json.dump(data_dict, outfile, indent=indent)
    
    #==========================================================================
    def get_dict(self, df=None, column_order=[]):
        """
        Transform DataFrame into dictionary
        """
        return df.to_dict()
    
    #==========================================================================
"""
#==============================================================================
#==============================================================================
"""    
class jsonHandler(object):
    """
    Import json
    Export to json
    Find dictionary within json file based on a specific key 
    
    The idea is to have one unique key for each dictionary within a json file
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
    def append_dict(self, dictionary=None):
        """
        Append dict to out_file (list)
        """
        
        if not hasattr(self, 'out_file'):
            self.initiate_outfile()
            
        self.out_file.append(dictionary)
        
        
    #==========================================================================
    def initiate_outfile(self):
        """
        """
        
        self.out_file = []

        
    #==========================================================================
    def export(self, out_source='', out_file=None):
        """
        """
        
        if out_file:
            Export(out_source=out_source).export_json(data_dict=out_file)
            
        elif hasattr(self, 'out_file'):
            Export(out_source=out_source).export_json(data_dict=self.out_file)
        
        else:
            raise UserWarning('No out file specified for export to .json')
        

    #==========================================================================
    def get_dict(self, key_in_dict=None):
        """
        Find a dict based on a specific key within the target dict
        """
        
        if isinstance(self.json_file, list):
            # Each element of array is a dictionary
            for element in self.json_file:
                if key_in_dict in element:
                    return element
                
            UserWarning('KEY: '+ key_in_dict + ' not in json file')
            
        elif isinstance(self.json_file, dict):
            if key_in_dict in self.json_file:
                return self.json_file
            else:
                UserWarning('KEY: '+ key_in_dict + ' not in json file')
                
        else:
            raise UserWarning('The intended use of a json file has an unrecognizable format', type(self.json_file))


    #==========================================================================
    def load(self, file_path=u''):
        """
        """
        
#        json_file = core.Load().load_json(file_path=file_path)
        with open(file_path, 'r') as f:
            self.json_file = json.load(f)
    
       
    #==========================================================================


"""
#==============================================================================
#==============================================================================
"""      
class DictionaryStructure(object):
    """
    Set up a default nested dictionary structure based on a json file
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
def get_dict_structure():
    
    return {
            'signature_key':True,
            '':[],
            }
"""
#==============================================================================
#==============================================================================
"""   
if __name__ == '__main__':
    print('='*50)
    print('Running...')
    print('-'*50)
    
    data = {
            'KEY_A':'test',
            'KEY_F':{},
            'KEY_C':[],
            'KEY_B':'',
            'KEY_D':None,
            'KEY_E':True,            
            'KEY_AA':[2,35,78,58,454444],
            'KEY_R':{'key_2':[3,4,54,65],
                     'key_1':44}
            }
    data_2 = {'K':[1,2,3,4,5,6,7,0],
              'J':{'test':'TRUE'}}
    
    array = [data, data_2]
    
    fid = 'json_outfile'
    
    exports = Export(out_source='D:/Temp/'+fid)
    exports.export_json(data_dict = array )

    json_object = jsonHandler()
    json_object.load(file_path='D:/Temp/'+fid)#+'.json')

#    dd = json_object.get_dict(json_object.json_file, key_in_dict='KEY_A')
    dd = json_object.get_dict(key_in_dict='KEY_A')

    print('-'*50)
    print('done')
    print('-'*50)
  

