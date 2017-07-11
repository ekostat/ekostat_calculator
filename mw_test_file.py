# -*- coding: utf-8 -*-

"""
Created on Mon Jul 10 15:27:01 2017

@author: a001985
"""
import os
import sys
import est_core
#input('first')
#
###############################################################################
if __name__ == '__main__':
    print('='*50)
    print('Running module "mw_test_file.py"')
    print('-'*50)
    print('')
    
    # Raw data saved in DataHandler object
#    raw_data_handler = est_core.DataHandler('raw')
    raw_data_handler = est_core.DataHandler('raw')
    raw_data_handler.add_txt_file('D:/Utveckling/g_EKOSTAT_tool/test_data/data.txt') 
    
    # Indicator
    indicator_NP = est_core.IndicatorNP()
    indicator_NP.set_data_handler(raw_data_handler)
    
    # Parameter
    print('done')