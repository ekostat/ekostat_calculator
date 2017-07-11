#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import sys, traceback
import time

"""
========================================================================
========================================================================
========================================================================
"""
def singleton(myClass):
    """
    Decorator to create singelton class instances. 
    Enable by adding @singleton on the line above the class definition. 
     
    In reality: myClass = singleton(myClass)
    """
    instances = {}
    def getInstance(*args, **kwargs):
        if myClass not in instances:
            instances[myClass] = myClass(*args, **kwargs)
        return instances[myClass]
    return getInstance

"""
========================================================================
========================================================================
========================================================================
"""
def time_it(wrapped):
    """
    Decorator to use to get the time it takes to run a function. 
    """
    def inner(*args, **kwargs):
        t = time.time()
        ret = wrapped(*args, **kwargs)
        func_string = str(wrapped).split()[1]
        print('Execution time for function "%s": %s s' % (func_string,  time.time() - t))
        return ret
    return inner
     
        
"""
========================================================================
========================================================================
========================================================================
"""
def error_handler(handler, info=u''):
    """
    Decorator to handle exceptions
    http://stackoverflow.com/questions/129144/generic-exception-handling-in-python-the-right-way
    Can not be used (as is) when the function has a return
    """
    def decorate(func):
        def call_function(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except:
                func_name = str(func).split()[1]
                tb_string = traceback.format_exc()
                handler(func_name, tb_string, info)
        return call_function
    return decorate

# def error_handler(handler):
#     """
#     http://stackoverflow.com/questions/129144/generic-exception-handling-in-python-the-right-way
#     """
#     def decorate(func):
#         def call_function(*args, **kwargs):
#             try:
#                 func(*args, **kwargs)
#             except Exception, e:
#                 handler(e)
#         return call_function
#     return decorate


"""
========================================================================
========================================================================
========================================================================
========================================================================
=============================== TEST ===================================
========================================================================
========================================================================
========================================================================
========================================================================
"""
def target1(text):
    print( 'HEJ')
    
def target2(text):
    print ('*'*80)
    print ('*'*80)
    print (text)
    print ('*'*80)

#========================================================================== 
# @time_it
@singleton
class ERROR():
    def __init__(self):
        self.target_list = []
        
    def add_target(self, target):
        """ """
        self.target_list.append(target)
        
    def write_to_targets(self, text):
        if not self.target_list:
            print ('-'*80)
            print ('PRINT ON SCREEN')
            print (text)
            print ('-'*80)
        else:
            for target in self.target_list:
                target(text)

def error(func_name, text, info):
    return ERROR().write_to_targets(text)

#========================================================================== 
"""
error_function = error_handler(show_error)(error_function)
                [------------------------] = returned decorator
"""

@error_handler(error)
def error_function():
    return 2 + '1'


#========================================================================== 
def main():
    ERROR().add_target(target1)
    ERROR().add_target(target2)
    error_function()

if __name__ == '__main__':
    main()



