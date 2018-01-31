# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:05:36 2018

@author: a001985
"""

import os
import shutil
import sys
import datetime
import codecs
import pandas as pd
import uuid
import re 
import pathlib


import logging
import importlib
try:
    logging.shutdown()
    importlib.reload(logging)
except:
    pass
# TODO: Move this!

current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
if current_path not in sys.path:
    sys.path.append(current_path)

import core
"""
Module to handle all events linked to the Django application. 

MW: Started this to start logging functionality. 
""" 

class Ekostat(object): 
    def __init__(self, root_path): 
        self.root_path = root_path.replace('\\', '/') 
        self.log_directory = self.root_path + '/log'
        self.setup_log()
        
        # Test main logger
        self._logger = logging.getLogger('Ekostat')
        self._logger.info('TEST info logger')
        self._logger.warning('TEST warning logger')
        self._logger.error('TEST error logger')
        self._logger.debug('TEST debug logger')
        
        
    
    #==========================================================================
    def setup_log(self):
        """
        Usage:
            self._logger = logging.getLogger('......')
            self._logger.info('Info message.')
            self._logger.warning('Warning message.')
            self._logger.error('Error message.')
            self._logger.debug('Debug message.')
            try: ...
            except Exception as e:
                self._logger.error('Exception: ' + str(e))
        """
        print('setup_log')
        log = logging.getLogger('Ekostat')
#        log.setLevel(logging.INFO)
        log.setLevel(logging.DEBUG)


        self._internal_dir_path = pathlib.Path(self.log_directory)
        self._internal_log_path = pathlib.Path(self._internal_dir_path, 'ekostat_log.txt')
        
        # Log directories.
        if not self._internal_dir_path.exists():
            self._internal_dir_path.mkdir(parents=True)
        
        # Define rotation log files for internal log files.
        try:
            log_handler = logging.handlers.RotatingFileHandler(str(self._internal_log_path),
                                                       maxBytes = 128*1024,
                                                       backupCount = 10)
            log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-10s : %(message)s '))
            log_handler.setLevel(logging.DEBUG)
            log.addHandler(log_handler)
        except Exception as e:
            print('EKOSTAT logging: Failed to set up logging: ' + str(e))
        
