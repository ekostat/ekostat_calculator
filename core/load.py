# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:18:45 2017

@author: a002028
"""


#import numpy as np
import os 
import pandas as pd
import json
import codecs
import pickle 
#import netcdf
"""
#==============================================================================
#==============================================================================
"""
class Load(object):
    """
    class to hold various methods for loading different types of files
    Can be settings files, data files, info files.. 
    """
    def __init__(self):
        pass
    
    
    #==========================================================================
    def load_excel(self, file_path=u'', sheetname=u'', header_row=0, fill_nan=u''):
        xl = pd.ExcelFile(file_path)
        ncols = xl.book.sheet_by_name(sheetname).ncols
        xl.close()

        return pd.read_excel(file_path, sheetname=sheetname, header=header_row, 
                             converters={i:str for i in range(ncols)}).fillna(fill_nan)
        
        
    #==========================================================================
    def load_netcdf(self, file_path=u''):
        pass
    
    
    #==========================================================================
    def load_txt(self, file_path=u'', sep='\t', encoding='cp1252', fill_nan=u''):
        with codecs.open(file_path, 'r', encoding=encoding) as f:
            header = f.readline().strip('\n').strip('\r').split(sep) # is .strip('\r') necessary?

        return pd.read_csv(file_path, sep='\t', encoding='cp1252',
                           dtype={key:str for key in header}).fillna(fill_nan)

    
    #==========================================================================
    def load_json(self, file_path=u''):
        """
        array will be either a list of dictionaries or one single dictionary 
        depending on what the json file includes
        """
        with open(file_path, 'r') as f:
            array = json.load(f)
        
        return array
    
    
    #==========================================================================
        
     
class SaveLoadDelete(object):
    """
    Created:        20180522     by Magnus
    Last modified:  20180525     by Magnus 
    
    class to save and load different structures (attributes). Generally saves/loads 
    from txt (if possible) and pickle. 
    Method should be added for the specific assignment. 
    The following structures are handled: 
        
    """
    
    def __init__(self, directory): 
        self.directory = directory 
        
    
    #==========================================================================
    def _strip_name(self, file_name):
        return file_name.split('.')[0] 
    
    
    #==========================================================================
    def _pikle_file_name(self, file_name): 
        return self._strip_name(file_name) + '.pkl'
        
    
    #==========================================================================
    def _txt_file_name(self, file_name): 
        return self._strip_name(file_name) + '.txt'
        
    
    #==========================================================================
    def old_load_df(self, file_name='df_data', load_txt=False): 
        """
        Created:        20180523     by Magnus
        Last modified:  20180523     by Magnus 
        
        Loads a pandas dataframe structure from pickle- and/or txt-file. 
        By default the pickle file is loaded if it exists. 
        If the corresponding pickle-file does not exists the txt file is loaded
        If load_txt=True the txt-file is loaded even if the pickle excists exists. 
        """ 
        pickle_file_path = os.path.join(self.directory, self._pikle_file_name(file_name))
        txt_file_path = os.path.join(self.directory, self._txt_file_name(file_name))
        
        if load_txt:
            df = load_data_file(file_path=txt_file_path, sep='\t', encoding='cp1252',  fill_nan=u'')
        if os.path.exists(pickle_file_path):
            with open(pickle_file_path, "rb") as fid: 
                df = pickle.load(fid)
#            df = pd.read_pickle(pickle_file_path)
        elif os.path.exists(txt_file_path):
            df = load_data_file(file_path=txt_file_path, sep='\t', encoding='cp1252',  fill_nan=u'')
        return df
    
    
    #==========================================================================
    def load_df(self, file_name='df_data', load_txt=False): 
        """
        Created:        20180523     by Magnus
        Last modified:  20180720     by Magnus 
        
        Loads a pandas dataframe structure from pickle- and/or txt-file. 
        By default the pickle file is loaded if it exists. 
        If the corresponding pickle-file does not exists the txt file is loaded
        If load_txt=True the txt-file is loaded even if the pickle excists exists. 
        """ 
        pickle_file_path = os.path.join(self.directory, self._pikle_file_name(file_name))
        txt_file_path = os.path.join(self.directory, self._txt_file_name(file_name))
        
        if load_txt or not os.path.exists(pickle_file_path): 
            if os.path.exists(txt_file_path):
                df = load_data_file(file_path=txt_file_path, sep='\t', encoding='cp1252',  fill_nan=u'')

        elif os.path.exists(pickle_file_path):
            with open(pickle_file_path, "rb") as fid: 
                df = pickle.load(fid)
#            df = pd.read_pickle(pickle_file_path)
        
        return df
        
    
    #==========================================================================
    def save_df(self, df, file_name='df_data', force_save_txt=False, only_pkl=False): 
        """
        Created:        20180522     by Magnus
        Last modified:  20180525     by Magnus 
        
        Saves a pandas dataframe structure. 
        By default a pickle file is created. 
        If the corresponding txt-file does not exists a txt file is created
        If save_txt=True a txt-file is created even if the pickle file exists. 
        If only_pkl=True and force_save_txt=True no txt file is saved. 
        
        """
        pickle_file_path = os.path.join(self.directory, self._pikle_file_name(file_name))
        txt_file_path = os.path.join(self.directory, self._txt_file_name(file_name))
        
        # Save txt-file 
        if only_pkl:
            pass
        elif force_save_txt or not os.path.exists(txt_file_path): 
            save_data_file(df=df, 
                           directory=self.directory, 
                           file_name=self._txt_file_name(file_name))
            
        
        # Save pickle file 
        with open(pickle_file_path, "wb") as fid:
            pickle.dump(df, fid) 
#        df.to_pickle(pickle_file_path)
        
        
    #==========================================================================
    def delete_files(self, file_name='df_data'): 
        """
        Created:        20180525     by Magnus
        Last modified:  20180525     by Magnus 
        
        Deletes txt and pkl files matching the file_name. 
        """ 
        pickle_file_path = os.path.join(self.directory, self._pikle_file_name(file_name))
        txt_file_path = os.path.join(self.directory, self._txt_file_name(file_name)) 
        print('¤'*50)
        print(pickle_file_path)
        print(txt_file_path)
        
        if os.path.exists(pickle_file_path):
            os.remove(pickle_file_path)
            
        if os.path.exists(txt_file_path):
            os.remove(txt_file_path)
        
        
    #==========================================================================
    def load_boolean_dict(self, boolean_dict, file_name='boolean_dict'):
        """
        Created:        20180523     by Magnus
        Last modified:  20180523     by Magnus 
        
        Loads a boolean dict from pickle. 
        Returns empty dict if non exsisting. 
        """
        pickle_file_path = os.path.join(self.directory, self._pikle_file_name(file_name)) 
        
        if os.path.exists(pickle_file_path): 
            return pickle.load(open(pickle_file_path, "rb"))
        else:
            return {}
        
        
    #==========================================================================
    def save_boolean_dict(self, boolean_dict, file_name='boolean_dict'):
        """
        Created:        20180523     by Magnus
        Last modified:  20180523     by Magnus 
        
        Saves a boolean dict to pickle
        """
        pickle_file_path = os.path.join(self.directory, self._pikle_file_name(file_name)) 
        
        pickle.dump(boolean_dict, open(pickle_file_path, "wb")) 
        
        
#==========================================================================
def save_data_file(df=None, directory=u'', file_name=u''):
    """
    Last modified:  20180525    by Magnus Wenzer
    
    20180525 by Magnus: moved to load module from data_handlers module
    """
#            directory = os.path.dirname(os.path.realpath(__file__))[:-4] + 'test_data\\test_exports\\'
        
    if not directory.endswith(('/','\\')):
        directory = directory + '/'
    
    file_path = directory + file_name
    
    print(u'Saving data to:',file_path)
    
    # MW: Name index
    df['index_column']=df.index
#    df = df.reset_index(drop=True)
    
    # MW: Index is set when loading via funktion load_data_file
    df.to_csv(file_path, sep='\t', encoding='cp1252', index=False) 
#        df.to_csv(file_path, sep='\t', encoding='cp1252', index=True)


    
#        column_file_path = directory + '/column_data.txt'
#        self.column_data.to_csv(column_file_path, sep='\t', encoding='cp1252', index=False)
#        
#        row_file_path = directory + '/row_data.txt'
#        self.row_data.to_csv(row_file_path, sep='\t', encoding='cp1252', index=False)

#==========================================================================

#==========================================================================
def load_data_file(file_path=None, sep='\t', encoding='cp1252',  fill_nan=u''):
    """
    Created:        20180420    by Magnus Wenzer
    Last modified:  20180525    by Magnus Wenzer
    
    1: Loads the given file using the core.Load().load_txt method. 
    2: Fix index 
    3: Returns the DataFrame  
    
    20180525 by Magnus: moved to load module from data_handlers module
    """
    df = Load().load_txt(file_path, sep=sep, encoding=encoding, fill_nan=fill_nan) 
    df['index_column'] = df['index_column'].astype(int)
    df = df.set_index('index_column')
    return df
        
"""
#==============================================================================
#==============================================================================
"""    
    
    
    
    
    
    
    
