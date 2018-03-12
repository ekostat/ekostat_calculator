# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:14:50 2018

@author: a001985
"""
import os
import sys
import importlib
import logging

try:
    logging.shutdown()
    importlib.reload(logging)
except:
    pass

current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
if current_path not in sys.path:
    sys.path.append(current_path)
    
import core 
    
if __name__ == '__main__':
    root_path = os.path.dirname(os.path.realpath(__file__))
    ekos = core.EventHandler(root_path)
    
    mww = ekos.get_workspace('mw')
    if not mww:
        ekos.create_copy_of_workspace('default', 'mw')
        mww = ekos.get_workspace('mw')
       
    mww.import_default_data()

    print('='*50)
    for item in sorted(logging.Logger.manager.loggerDict.keys()): 
        print('- {}\t{}'.format(item, logging.Logger.manager.loggerDict[item]))