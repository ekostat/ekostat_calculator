# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:14:50 2018

@author: a001985
"""
import os
import sys


current_path = os.path.dirname(os.path.realpath(__file__))[:-4]
if current_path not in sys.path:
    sys.path.append(current_path)
    
import core 
    
if __name__ == '__main__':
    root_path = os.path.dirname(os.path.realpath(__file__))
    ekos = core.Ekostat(root_path)