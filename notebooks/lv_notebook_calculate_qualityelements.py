
# coding: utf-8

# In[17]:

import os 
import sys
path = "../"
sys.path.append(path)
#os.path.abspath("../")
print(os.path.abspath(path))


# In[18]:


import pandas as pd
import numpy as np
import json
import timeit
import time
import core
import importlib
import re
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

# In[19]:


root_directory = 'D:/github/w_vattenstatus/ekostat_calculator'#"../" #os.getcwd()
workspace_directory = root_directory + '/workspaces' 
resource_directory = root_directory + '/resources'

user_id = 'test_user'


# ## Initiate EventHandler

# In[20]:


print(root_directory)
paths = {'user_id': user_id, 
         'workspace_directory': root_directory + '/workspaces', 
         'resource_directory': root_directory + '/resources', 
         'log_directory': 'D:/github' + '/log', 
         'test_data_directory': 'D:/github' + '/test_data',
         'cache_directory': 'D:/github/w_vattenstatus/cache'}


# In[21]:


t0 = time.time()
ekos = EventHandler(**paths)
print('-'*50)
print('Time for request: {}'.format(time.time()-t0))


# ### Load existing workspace

# In[22]:


workspace_alias = 'kustzon_SE1'
ekos.print_workspaces()


# In[23]:


workspace_uuid = ekos.get_unique_id_for_alias(workspace_alias = workspace_alias)
print(workspace_uuid)


# In[24]:


workspace_alias = ekos.get_alias_for_unique_id(workspace_uuid = workspace_uuid)


# In[25]:


ekos.load_workspace(unique_id = workspace_uuid)


# # QUALITY ELEMENTS

# In[26]:


w = ekos.get_workspace(workspace_uuid = workspace_uuid)
len(w.data_handler.get_all_column_data_df())


# In[27]:


subset_alias = 'SE1_alldata'
subset_uuid = ekos.get_unique_id_for_alias(workspace_alias = workspace_alias, subset_alias = subset_alias)


# In[28]:


###############################################################################################################################  
# ### CALCULATE QUALITY ELEMENTS
w.get_step_object(step = 3, subset = subset_uuid).calculate_quality_element(quality_element = 'nutrients_sw')
w.get_step_object(step = 3, subset = subset_uuid).calculate_quality_element(quality_element = 'phytoplankton')
# w.get_step_object(step = 3, subset = subset_uuid).calculate_quality_element(quality_element = 'bottomfauna')
w.get_step_object(step = 3, subset = subset_uuid).calculate_quality_element(quality_element = 'oxygen')
w.get_step_object(step = 3, subset = subset_uuid).calculate_quality_element(quality_element = 'secchi')
 

# In[29]:


# w.get_step_object(step = 3, subset = subset_uuid).quality_element['nutrients_sw'].results.head()

print(10*'*'+'FINISHED'+10*'*')
