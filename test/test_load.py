# -*- coding: utf-8 -*-
"""
Created on Tue May 22 13:48:04 2018

@author: a001985
"""
import unittest 
import os 
import sys 
import time
import pandas as pd
import pickle
import core

TEST_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) 
TESTDATA_DIRECTORY = TEST_DIRECTORY + '/testdata'
BASE_DIRECTORY = os.path.dirname(TEST_DIRECTORY)
if BASE_DIRECTORY not in sys.path:
    sys.path.append(BASE_DIRECTORY)
    
#==============================================================================

from core import load

#==============================================================================

#print(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
class TestSaveAndLoad(unittest.TestCase): 
    """
    Created:        20180522     by Magnus
    Last modified:  20180523     by Magnus 
    """ 
    #==========================================================================
    @classmethod
    def setUpClass(self): 
        print('='*50)
        print('setUpClass in TestSaveAndLoad')
        print('-'*50)
#        self.df = pd.DataFrame([['a', 'b'], [1, 2]], columns=['col1', 'col2'])
        self.df = pd.read_csv(TESTDATA_DIRECTORY + '/test_column_data.txt', sep='\t', encoding='cp1252') 
        
    #==========================================================================
    def setUp(self):
        self.save_and_load_object = load.SaveAndLoad(TESTDATA_DIRECTORY) 
        
    
    #==========================================================================
    def tearDown(self):
        pass
    
    
    #==========================================================================
    def test_pickel_file_name(self):
        self.assertEqual(self.save_and_load_object._pikle_file_name('test_name.txt'), 'test_name.pkl')
        self.assertEqual(self.save_and_load_object._pikle_file_name('test_name'), 'test_name.pkl')
        
        
    #==========================================================================
    def test_txt_file_name(self):
        self.assertEqual(self.save_and_load_object._txt_file_name('test_name.txt'), 'test_name.txt')
        self.assertEqual(self.save_and_load_object._txt_file_name('test_name'), 'test_name.txt')
        
        
    #==========================================================================
    def test_save_df(self): 
        file_name = 'df_data' 
        txt_file_path = TESTDATA_DIRECTORY + '/{}.txt'.format(file_name)
        pickle_file_path = TESTDATA_DIRECTORY + '/{}.pkl'.format(file_name)
        
        #----------------------------------------------------------------------
        # Remove both files 
        try: 
            os.remove(txt_file_path)
        except:
            pass
        
        try: 
            os.remove(pickle_file_path)
        except:
            pass
        
        # Files should not exsist
        self.assertFalse(os.path.exists(txt_file_path))
        self.assertFalse(os.path.exists(pickle_file_path))
        
        # Save files
        self.save_and_load_object.save_df(self.df, file_name=file_name, save_txt=False)
        
        # Both files should exsist 
        self.assertTrue(os.path.exists(txt_file_path))
        self.assertTrue(os.path.exists(pickle_file_path))
        
        #----------------------------------------------------------------------
        # Check that txt-file is not updated and pickle-file is updated 
        t0_txt = os.path.getmtime(txt_file_path)
        t0_pickle = os.path.getmtime(pickle_file_path)
        time.sleep(0.1) 
        self.save_and_load_object.save_df(self.df, file_name=file_name, save_txt=False)
        t1_txt = os.path.getmtime(txt_file_path)
        t1_pickle = os.path.getmtime(pickle_file_path)
        
        self.assertEqual(t0_txt, t1_txt)
        self.assertNotEqual(t0_pickle, t1_pickle)
        
        #----------------------------------------------------------------------
        # Check that both txt and and pickle is updated
        t0_txt = os.path.getmtime(txt_file_path)
        t0_pickle = os.path.getmtime(pickle_file_path)
        time.sleep(0.1) 
        self.save_and_load_object.save_df(self.df, file_name=file_name, save_txt=True)
        t1_txt = os.path.getmtime(txt_file_path)
        t1_pickle = os.path.getmtime(pickle_file_path)
        
        self.assertNotEqual(t0_txt, t1_txt)
        self.assertNotEqual(t0_pickle, t1_pickle)
        
        
    #==========================================================================
    def test_load_df(self): 
        #----------------------------------------------------------------------
        # Preparations 
        file_name = 'df_data' 
        txt_file_path = TESTDATA_DIRECTORY + '/{}.txt'.format(file_name)
        pickle_file_path = TESTDATA_DIRECTORY + '/{}.pickle'.format(file_name)
        
        # Save files 
        # TODO: Maybe this should be created in another way (copied) since its part of the test 
#        self.df.to_pickle(pickle_file_path) # Does not add index_column
#        core.save_data_file(df=self.df, directory=TESTDATA_DIRECTORY, file_name=file_name+'.txt')
        self.save_and_load_object.save_df(self.df, file_name=file_name, save_txt=False)
        #----------------------------------------------------------------------
        
        df = self.save_and_load_object.load_df(file_name=file_name, load_txt=False)
        
        if os.path.exists(pickle_file_path): 
            df_pkl = pd.read_pickle(pickle_file_path)
            self.assertTrue(all(df == df_pkl))
        
        if os.path.exists(txt_file_path): 
            df_txt = core.load_data_file(file_path=txt_file_path, sep='\t', encoding='cp1252',  fill_nan=u'')
#            print('='*50)
#            print(df)
#            print('-'*50)
#            print(df_txt)
#            print('='*50)
            self.assertTrue(all(df == df_txt))
        
        
    #==========================================================================
    def test_save_load_boolean_dict(self): 
        test_dict_1 = {'a': [True, False], 
                       'b': [False, False]}
        test_dict_2 = {'a': [True, False], 
                       'b': [False, True]} 
        
        file_name_1 = 'boolean_dict_1'
        file_name_2 = 'boolean_dict_2'
        
        pickle_file_path_1 = TESTDATA_DIRECTORY + '/{}.pkl'.format(file_name_1)
        pickle_file_path_2 = TESTDATA_DIRECTORY + '/{}.pkl'.format(file_name_2)
        
        # Expect save of pickle files
        self.save_and_load_object.save_boolean_dict(test_dict_1, file_name=file_name_1) 
        self.save_and_load_object.save_boolean_dict(test_dict_2, file_name=file_name_2)
        
        # Assert files has been created
        self.assertTrue(os.path.exists(pickle_file_path_1))
        self.assertTrue(os.path.exists(pickle_file_path_2)) 
        
        # Load dict 
        loaded_dict = pickle.load(open(pickle_file_path_1, "rb"))
        self.assertEqual(loaded_dict, test_dict_1)
        
        
        
#==============================================================================
#==============================================================================
#==============================================================================      
if __name__ == "__main__":
    unittest.main() 
    
    
    
"""   
#==============================================================================
Nice tutorial here:
https://www.youtube.com/watch?v=6tNS--WetLI 


# Context manager for testing exceptions
with self.assertRaises(ValueError):
    <func>(arg_1, arg_2)

#==============================================================================
"""