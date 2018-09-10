# coding: utf-8
'''
Created on 3 sep. 2018

@author: a002087
'''
import os 
import sys
path = "../"
path = "D:/github/w_vattenstatus/ekostat_calculator"
sys.path.append(path)
#os.path.abspath("../")
print(os.path.abspath(path))


# In[2]:


import pandas as pd
import numpy as np
import json
import timeit
import time
import core
import importlib
importlib.reload(core)
import logging
importlib.reload(core) 
try:
    logging.shutdown()
    importlib.reload(logging)
except:
    pass
from event_handler import EventHandler
print(core.__file__)
pd.__version__


# ### Load directories

# In[3]:


root_directory = 'D:/github/w_vattenstatus/ekostat_calculator'#"../" #os.getcwd()
workspace_directory = root_directory + '/workspaces' 
resource_directory = root_directory + '/resources'
#alias = 'lena'
user_id = 'test_user' #kanske ska vara off_line user?
workspace_alias = 'lena_indicator'


# ## Initiate EventHandler

# In[4]:


print(root_directory)
paths = {'user_id': user_id, 
         'workspace_directory': root_directory + '/workspaces', 
         'resource_directory': root_directory + '/resources', 
         'log_directory': 'D:/github' + '/log', 
         'test_data_directory': 'D:/github' + '/test_data'}


# In[5]:


t0 = time.time()
ekos = EventHandler(**paths)
print('-'*50)
print('Time for request: {}'.format(time.time()-t0))

ekos.print_workspaces()


# In[8]:


workspace_uuid = ekos.get_unique_id_for_alias(workspace_alias = 'lena_indicator')
print(workspace_uuid)


# In[9]:

# �NDRAT
workspace_alias = ekos.get_alias_for_unique_id(workspace_uuid = workspace_uuid)


# In[10]:


ekos.load_workspace(unique_id = workspace_uuid)

w = ekos.get_workspace(workspace_uuid = workspace_uuid)
len(w.data_handler.get_all_column_data_df())

subset_alias = 'period_2007-2012_refvalues_2017'
subset_uuid = ekos.get_unique_id_for_alias(workspace_alias = workspace_alias, subset_alias = subset_alias)


w.get_step_object(step = 3, subset = subset_uuid).calculate_quality_element(subset_unique_id = subset_uuid, quality_element = 'Nutrients', class_name = 'QualityElementNutrients')



















