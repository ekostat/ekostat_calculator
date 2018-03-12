# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 09:03:59 2018

@author: a001985
"""
import logging
import pathlib

        
#==========================================================================
def add_log(log_id=None, log_directory=None, log_level='DEBUG', on_screen=True, prefix='log_ekostat'):
    """
    log_id:         Id of the logger. Typically a UUID 
    
    log_directory:  Directory to put the log files in. If not given no files are created. 
    
    log_level:      Specify the log level. 
    
    on_screen:      Set to True if you want to print to screen as well. Default is True. 
    
    prefix:         Prefix to be added to the files. 
    
    --------------------------------------------------------------
    Usage:
        self._logger = logging.getLogger('......')
        self._logger.debug('Debug message.')
        self._logger.info('Info message.')
        self._logger.warning('Warning message.')
        self._logger.error('Error message.')
        try: ...
        except Exception as e:
            self._logger.error('Exception: ' + str(e))
    """
#    logging_format = '%(asctime)s\t%(filename)s\t%(funcName)s\t%(levelname)-10s : %(message)s'
    logging_format = '%(asctime)s\t%(filename)s\t%(lineno)d\t%(funcName)s\t%(levelname)s\t%(message)s'
    
    log_id_ext = '{}_{}'.format(prefix, log_id)
    log = logging.getLogger(log_id_ext)
    
    # Dont add an excisting logger
    if len(log.handlers):
        return False
    print('='*100)
    print(log_id)
    print(log_directory)
    print(prefix)
    print('-'*100)
    # Set debug log_level 
    level_mapping = {'DEBUG': logging.DEBUG, 
                     'INFO': logging.INFO,
                     'WARNING': logging.WARNING,
                     'ERROR': logging.ERROR}
    
    log_level = level_mapping.get(log_level.upper(), 'ERROR')
    log.setLevel(log_level)

    if log_directory:
        dir_path = pathlib.Path(log_directory)
        log_path = pathlib.Path(dir_path, '{}_{}.log'.format(prefix, log_id))
        
        # Log directories.
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
        
        # Define rotation log files for internal log files.
        try:
            log_handler = logging.handlers.RotatingFileHandler(str(log_path),
                                                       maxBytes = 128*1024,
                                                       backupCount = 10)
            log_handler.setFormatter(logging.Formatter(logging_format))
            log_handler.setLevel(log_level)
            log.addHandler(log_handler)
        except Exception as e:
            print('EKOSTAT logging: Failed to set up file logging: ' + str(e)) 
            
    if on_screen:
        try:
            log_handler_screen = logging.StreamHandler()
            log_handler_screen.setFormatter(logging.Formatter(logging_format))
            log_handler_screen.setLevel(log_level)
            log.addHandler(log_handler_screen)
        except Exception as e:
            print('EKOSTAT logging: Failed to set up screen logging: ' + str(e))
    log.debug('')
    log.debug('='*120)
    log.debug('### Log added for log_id "{}" at locaton: {}'.format(log_id, str(log_path)))
    log.debug('-'*120)  
    return True
        
#==========================================================================
def get_log(log_id):
    """
    Return a logging object set to the given id. 
    """
    print('¤'*100)
    print('¤'*100)
    print('¤'*100)
    print(logging.Logger.manager.loggerDict.keys())
    print('¤'*100)
    for item in logging.Logger.manager.loggerDict.keys():
        print('{} _ {}'.format(log_id, item))
        if log_id in item:
            log_id = item
            break
    return logging.getLogger(log_id)
    