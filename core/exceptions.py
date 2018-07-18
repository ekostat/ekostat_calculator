# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 15:43:19 2018

@author: a001985
"""

#==============================================================================
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
    
    
#==============================================================================
class EkostatUserException(EkostatException):
    """
    Created     20180716    by Magnus Wenzer
    """
    code = ''   
    message = ''

    
#==============================================================================
class EkostatInternalException(EkostatException):
    """
    Created     20180716    by Magnus Wenzer
    """
    code = ''   
    message = ''
    
"""
===============================================================================
===============================================================================
"""

#==============================================================================
class WorkspaceAlreadyExists(EkostatUserException):
    """
    Created     20180617    by Magnus Wenzer
    Updated     
    """
    code = 'workspace_alias_exists'   
    message = 'The workspace you are trying to create already exists' 
    
    
#==============================================================================
class SubsetAlreadyExists(EkostatUserException):
    """
    Created     20180615    by Magnus Wenzer
    Updated     20180617    by Magnus Wenzer
    """
    code = 'subset_alias_exists'   
    message = 'The subset you are trying to create already exists' 
    

#==============================================================================
class SubsetUUIDNotFound(EkostatInternalException):
    """
    Created     20180617    by Magnus Wenzer
    Updated     
    """
    code = 'workspace_uuid_missing'   
    message = 'The workspace you are trying to create already exists' 
    
    
#==============================================================================
class InvalidInputVariable(EkostatInternalException):
    """
    Created     20180716    by Magnus Wenzer
    """
    code = 500   
    message = 'Input variable not valid'
    
    
#==============================================================================
class MissingInputVariable(EkostatInternalException):
    """
    Created     20180718    by Magnus Wenzer
    """
    code = 500   
    message = 'Input variable is missing'
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    