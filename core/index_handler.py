# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 14:02:13 2017

@author: a002028
"""

import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
sys.path.append(current_path)

import pandas as pd
import numpy as np
import time

import utils
import core
"""
#==============================================================================
#==============================================================================
"""
class IndexHandler(object):
    """
    - Ska kunna ta emot filterobject
    - Summera index arrayer
    - Utgår från föregående index.array för det specifika subsetet.. Indicator.index 
    - Pratar med DataHandler och dess DataFrame för att plocka fram index 
    """
    def __init__(self):
        pass