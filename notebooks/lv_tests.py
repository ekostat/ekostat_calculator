'''
Created on 22 nov. 2018

@author: a002087
'''
# coding: utf-8

# In[1]:


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
###############################################################################################################################
# ### Load directories
root_directory = 'D:/github/w_vattenstatus/ekostat_calculator'#"../" #os.getcwd()
workspace_directory = root_directory + '/workspaces' 
resource_directory = root_directory + '/resources'

user_id = 'test_user' #kanske ska vara off_line user?
# ## Initiate EventHandler
print(root_directory)
paths = {'user_id': user_id, 
         'workspace_directory': root_directory + '/workspaces', 
         'resource_directory': root_directory + '/resources', 
         'log_directory': 'D:/github' + '/log', 
         'test_data_directory': 'D:/github' + '/test_data',
         'cache_directory': 'D:/github/w_vattenstatus/cache'}

t0 = time.time()
ekos = EventHandler(**paths)
#request = ekos.test_requests['request_workspace_list']
#response = ekos.request_workspace_list(request) 
#ekos.write_test_response('request_workspace_list', response)
print('-'*50)
print('Time for request: {}'.format(time.time()-t0))
###############################################################################################################################
# ### Make a new workspace
# ekos.copy_workspace(source_uuid='default_workspace', target_alias='satellit')
# ### set alias etc.
#alias = 'lena'
workspace_alias = 'waters_export'
ekos.print_workspaces()
workspace_uuid = ekos.get_unique_id_for_alias(workspace_alias = workspace_alias) #'kuszonsmodellen' lena_indicator 
print(workspace_uuid)

workspace_alias = ekos.get_alias_for_unique_id(workspace_uuid = workspace_uuid)
###############################################################################################################################
# ### Load existing workspace
ekos.load_workspace(unique_id = workspace_uuid)
###############################################################################################################################
# #### to just load existing data in workspace
ekos.load_data(workspace_uuid = workspace_uuid)
############################################################################################################################### 
# ### check workspace data length
w = ekos.get_workspace(workspace_uuid = workspace_uuid)
len(w.data_handler.get_all_column_data_df())
###############################################################################################################################
# ### Choose subset name to load
# subset_alias = 'test_kustzon'
# subset_alias = 'period_2007-2012_refvalues_2013'
subset_alias = 'waters_export'#'test_with_sharkdata_only'#'test_subset'
subset_uuid = ekos.get_unique_id_for_alias(workspace_alias = workspace_alias, subset_alias = subset_alias)
print('subset_alias', subset_alias, 'subset_uuid', subset_uuid)
############################################################################################################################### 
### set available indicators  
w.get_available_indicators(subset= subset_uuid, step=2)
 
###############################################################################################################################
# ### choose indicators
#list(zip(typeA_list, df_step1.WATER_TYPE_AREA.unique()))
# indicator_list = ['oxygen','din_winter','ntot_summer', 'ntot_winter', 'dip_winter', 'ptot_summer', 'ptot_winter','bqi', 'biov', 'chl', 'secchi']
# indicator_list = ['din_winter','ntot_summer', 'ntot_winter', 'dip_winter', 'ptot_summer', 'ptot_winter']
# indicator_list = ['chl','biov']
indicator_list = ['chl']
#indicator_list = ['bqi', 'secchi'] + ['biov', 'chl'] + ['din_winter']
# indicator_list = ['din_winter','ntot_summer']
indicator_list = ['indicator_' + indicator for indicator in indicator_list]
indicator_list = w.available_indicators
############################################################################################################################### 
# ### compile data for waters
w.get_data_for_waterstool(step = 3, subset = subset_uuid, indicator_list = indicator_list) 
 
print(10*'*'+'FINISHED'+10*'*')













