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
    
    def __init__(self, message='', code=''):
        self.message = '{}: {}'.format(self.message, message) 
        if code:
            self.code = code
    
    
    
    
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
class WorkspaceIsDeleted(EkostatUserException):
    """
    Created     20180619    by Magnus Wenzer
    Updated     
    """
    code = 'workspace_uuid_deleted'   
    message = 'The workspace you are refering to is deleted. Contact administration to recover workspace!' 
    

#==============================================================================
class WorkspaceNotFound(EkostatUserException):
    """
    Created     20180619    by Magnus Wenzer
    Updated     
    """
    code = 'workspace_uuid_missing'   
    message = 'The workspace you are refering to does not exists' 
    
    
#==============================================================================
class SubsetAlreadyExists(EkostatUserException):
    """
    Created     20180615    by Magnus Wenzer
    Updated     20180617    by Magnus Wenzer
    """
    code = 'subset_alias_exists'   
    message = 'The subset you are trying to create already exists' 
    
    
#==============================================================================
class SubsetIsDeleted(EkostatUserException):
    """
    Created     20180619    by Magnus Wenzer
    Updated     
    """
    code = 'subset_uuid_deleted'   
    message = 'The subset you are refering to is deleted. Contact administration to recover subset!' 
    

#==============================================================================
class SubsetNotFound(EkostatUserException):
    """
    Created     20180617    by Magnus Wenzer
    Updated     20180619    by Magnus Wenzer
    """
    code = 'subset_uuid_missing'   
    message = 'The subset you are refering to does not exists' 
    
    
#==============================================================================
class InvalidUserInput(EkostatUserException):
    """
    Created     20180719    by Magnus Wenzer
    """
    code = 'invalid_user_input'   
    message = 'Invalid user input'
    
    
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
    

#==============================================================================
class UnableToLoadWorkspace(EkostatInternalException):
    """
    Created     20180719    by Magnus Wenzer
    """
    code = 500   
    message = 'Unable to load workspace'
    
    
#==============================================================================
class UnableToLoadData(EkostatUserException):
    """
    Created     20180719    by Magnus Wenzer
    """
    code = 'load_data_failed'   
    message = 'Unable to load data'
    
    
#==============================================================================
class UnexpectedInputVariable(EkostatInternalException):
    """
    Created     20180718    by Magnus Wenzer
    """
    code = 500   
    message = 'Found unexpected variable' 
    

#==============================================================================
class BooleanNotFound(EkostatInternalException):
    """
    Created     20180718    by Magnus Wenzer
    """
    code = 500   
    message = 'Could not find boolean' 
    

#==============================================================================
class NoAreasSelected(EkostatUserException):
    """
    Created     20180719    by Magnus Wenzer
    """
    code = 'areas_missing'   
    message = 'No areas selected' 
    
    
    
#class InputError(Exception):
#
#    """Exception raised for errors in the input.
#
#    Attributes:
#        expression -- input expression in which the error occurred
#        message -- explanation of the error
#    """
#
#    def __init__(self, expression, message):
#        self.expression = expression
#        self.message = message   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    