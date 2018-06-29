# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 15:43:19 2018

@author: a001985
"""

class EkostatException(Exception): 
    """
    Created     20180615    by Magnus Wenzer
    Updated   
    
    Blueprint for error message. 
    code is for external mapping of exceptions. For example if the GUI wants to 
    handle the error text for different languages. 
    """
    code = None 
    message = ''
    
    
    
class SubsetAlreadyExist(EkostatException):
    """
    Created     20180615    by Magnus Wenzer
    Updated     20180616    by Magnus Wenzer
    """
    code = 1   
    message = 'The subset you are trying to create already exists'