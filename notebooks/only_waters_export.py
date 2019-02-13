import os
import sys
path = "../"
path = "C:/github/w_vattenstatus/ekostat_calculator"
sys.path.append(path)
#os.path.abspath("../")
print(os.path.abspath(path))


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
########################################################################################################################
# ### Load directories
root_directory = 'C:/github/w_vattenstatus/ekostat_calculator'#"../" #os.getcwd()
workspace_directory = root_directory + '/workspaces'
resource_directory = root_directory + '/resources'

user_id = 'test_user' #kanske ska vara off_line user?
# ## Initiate EventHandler
print(root_directory)
paths = {'user_id': user_id,
         'workspace_directory': root_directory + '/workspaces',
         'resource_directory': root_directory + '/resources',
         'log_directory': 'C:/github' + '/log',
         'test_data_directory': 'C:/github' + '/test_data',
         'cache_directory': 'C:/github/w_vattenstatus/cache'}

t0 = time.time()
ekos = EventHandler(**paths)
print('-'*50)
print('Time for request: {}'.format(time.time()-t0))
########################################################################################################################
# ### See existing workspaces and choose workspace name to load
ekos.print_workspaces()
workspace_alias = 'waters_export_test2'#'kustzon_selection'
workspace_uuid = ekos.get_unique_id_for_alias(workspace_alias = workspace_alias) #'kuszonsmodellen' lena_indicator
print(workspace_uuid)
workspace_alias = ekos.get_alias_for_unique_id(workspace_uuid = workspace_uuid)
########################################################################################################################
# ### Load existing workspace
ekos.load_workspace(unique_id=workspace_uuid)
########################################################################################################################
# ### Choose subset name to load
subset_alias = 'waters_bugsearch'#'SE1_selection'#'satellite_results'#'waters_export'#'test_subset'
subset_uuid = ekos.get_unique_id_for_alias(workspace_alias = workspace_alias, subset_alias = subset_alias)
print('subset_alias', subset_alias, 'subset_uuid', subset_uuid)
########################################################################################################################
ekos.get_workspace(workspace_uuid = workspace_uuid).get_data_for_waterstool(step=3, subset=subset_uuid)

print(10 * '*' + 'FINISHED' + 10 * '*')