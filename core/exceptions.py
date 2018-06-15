# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 15:43:19 2018

@author: a001985
"""

class EkostatException(Exception):
    code = None 
    message = ''
    
    
    
class SubsetAlreadyExist(EkostatException):
    code = 1   
    message = 'The subset you are trying to create dsfds'