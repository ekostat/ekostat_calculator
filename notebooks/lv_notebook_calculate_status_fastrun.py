
# coding: utf-8

# In[1]:


# Reload when code changed:
get_ipython().magic('load_ext autoreload')
get_ipython().magic('autoreload 2')
get_ipython().magic('pwd')
import os 
import sys
path = "../"
path = "D:/github/ekostat_calculator"
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


root_directory = 'D:/github/ekostat_calculator'#"../" #os.getcwd()
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
#request = ekos.test_requests['request_workspace_list']
#response = ekos.request_workspace_list(request) 
#ekos.write_test_response('request_workspace_list', response)
print('-'*50)
print('Time for request: {}'.format(time.time()-t0))
# OLD: ekos = EventHandler(root_directory)


# ### Load existing workspace

# In[6]:


#ekos.copy_workspace(source_uuid='default_workspace', target_alias='lena_1')


# In[7]:


ekos.print_workspaces()


# In[8]:


workspace_uuid = ekos.get_unique_id_for_alias(workspace_alias = 'lena_indicator')
print(workspace_uuid)


# In[9]:

# ÄNDRAT
workspace_alias = ekos.get_alias_for_unique_id(workspace_uuid = workspace_uuid)


# In[10]:


ekos.load_workspace(unique_id = workspace_uuid)


# In[11]:


#ekos.import_default_data(workspace_alias = workspace_alias)


# ### Load all data in workspace

# In[12]:


#ekos.get_workspace(unique_id = workspace_uuid, alias = workspace_alias).delete_alldata_export()


# In[13]:


#%%timeit
# ÄNDRAT
ekos.load_data(workspace_uuid = workspace_uuid, force = True)


# In[14]:

# ÄNDRAT
w = ekos.get_workspace(workspace_uuid = workspace_uuid)
len(w.data_handler.get_all_column_data_df())


# In[15]:


print('subsetlist', w.get_subset_list())


# # Step 0 

# In[16]:


w.data_handler.all_data.columns


# ### Apply first data filter 

# In[17]:


w.apply_data_filter(step = 0) # This sets the first level of data filter in the IndexHandler 


# # Step 1 
# ### Set subset filter

# In[18]:


#w.copy_subset(source_uuid='default_subset', target_alias='period_2007-2012_refvalues_2013')


# In[19]:


subset_alias = 'period_2007-2012_refvalues_2013'
subset_uuid = ekos.get_unique_id_for_alias(workspace_alias = workspace_alias, subset_alias = subset_alias)
#w.set_data_filter(subset = subset_uuid, step=1, 
#                         filter_type='include_list', 
#                         filter_name='MYEAR', 
#                         data=['2007', '2008', '2009', '2010', '2011', '2012']) 


#f1 = w.get_data_filter_object(subset = subset_uuid, step=1) 
#print(f1.include_list_filter)


# In[20]:


print('subset_alias:', subset_alias, '\nsubset uuid:', subset_uuid)


# In[21]:


f1 = w.get_data_filter_object(subset = subset_uuid, step=1) 
print(f1.include_list_filter)


# ### Apply step 1 datafilter to subset

# In[22]:


w.apply_data_filter(subset = subset_uuid, step = 1)


# # Step 2
# ### Load indicator settings filter

# In[23]:

w.get_step_object(step = 2, subset = subset_uuid).load_indicator_settings_filters()


# ### set available indicators

# In[24]:


w.get_available_indicators(subset= subset_uuid, step=2)


# ### Apply indicator data filter

# In[25]:


#list(zip(typeA_list, df_step1.WATER_TYPE_AREA.unique()))
#indicator_list = w.get_available_indicators(subset= subset_uuid, step=2)
#indicator_list = ['oxygen','din_winter','ntot_summer', 'ntot_winter', 'dip_winter', 'ptot_summer', 'ptot_winter','bqi', 'biov', 'chl', 'secchi']
indicator_list = ['din_winter','ntot_summer', 'ntot_winter', 'dip_winter', 'ptot_summer', 'ptot_winter']
#indicator_list = ['biov', 'chl']
#indicator_list = ['bqi', 'secchi']
#indicator_list = ['bqi', 'secchi'] + ['biov', 'chl'] + ['din_winter']
#indicator_list = ['din_winter']

# In[ ]:
print('apply indicator data filter')

for indicator in indicator_list:
    w.apply_indicator_data_filter(step = 2, 
                          subset = subset_uuid, 
                          indicator = indicator)#,
                         # water_body_list = test_wb)
    #print(w.mapping_objects['water_body'][wb])
    #print('*************************************')


# # Step 3 
# ### Set up indicator objects

# In[ ]:
print('indicator set up')
w.get_step_object(step = 3, subset = subset_uuid).indicator_setup(subset_unique_id = subset_uuid, indicator_list = indicator_list) 


# ### CALCULATE STATUS

# In[ ]:
print('CALCULATE STATUS')
w.get_step_object(step = 3, subset = subset_uuid).calculate_status(indicator_list = indicator_list)
#'din_winter','ntot_summer', 'ntot_winter', 'dip_winter', 'ptot_summer', 'ptot_winter'


# ### CALCULATE QUALITY ELEMENTS

# In[ ]:


w.get_step_object(step = 3, subset = subset_uuid).calculate_quality_element(subset_unique_id = subset_uuid, quality_element = 'Nutrients', class_name = 'QualityElementNutrients')


# In[ ]:

columns = ['VISS_EU_CD','WATER_BODY_NAME','WATER_TYPE_AREA','STATUS_NUTRIENTS','mean_EQR','MEAN_N_EQR','EQR_N_winter_mean','global_EQR_ntot_winter','global_EQR_din_winter','global_EQR_ntot_summer','MEAN_P_EQR','EQR_P_winter_mean','global_EQR_ptot_winter','global_EQR_dip_winter','global_EQR_ptot_summer']
#w.get_step_object(step = 3, subset = subset_uuid).quality_element['Nutrients'].results.columns
w.get_step_object(step = 3, subset = subset_uuid).quality_element['Nutrients'].results[columns].to_csv('D:/Nutrients'+subset_alias+'.txt', float_format='%.3f', header = True, index = None, sep = '\t')


# In[ ]:


def get_QF_results(subset_alias):
    subset_uuid = ekos.get_unique_id_for_alias(workspace_alias = workspace_alias, subset_alias = subset_alias)
    w.get_step_object(step = 3, subset = subset_uuid).calculate_quality_element(subset_unique_id = subset_uuid, quality_element = 'Nutrients', class_name = 'QualityElementNutrients')
    columns = ['VISS_EU_CD','WATER_BODY_NAME','WATER_TYPE_AREA','STATUS_NUTRIENTS','mean_EQR','MEAN_N_EQR','EQR_N_winter_mean','global_EQR_ntot_winter','global_EQR_din_winter','global_EQR_ntot_summer','MEAN_P_EQR','EQR_P_winter_mean','global_EQR_ptot_winter','global_EQR_dip_winter','global_EQR_ptot_summer']
    return w.get_step_object(step = 3, subset = subset_uuid).quality_element['Nutrients'].results[columns]
    
QF_2017 = get_QF_results('period_2007-2012_refvalues_2017')   

# ## Plotting results

# In[ ]:


#%matplotlib inline
#import seaborn as sns
#for name, group in ind_obj.classification_results['status_by_date'].groupby('VISS_EU_CD'):
    #group['date'] = pd.to_datetime(group.SDATE)
    #group.dropna(subset = ['date', 'DIN'])
    #sns.tsplot(data = group.to_dict(), time = 'SDATE', value = 'DIN', condition = 'STATUS', legend = True)
#    group.plot('SDATE', ['DIN', 'REFERENCE_VALUE'], title = name + group.WATER_TYPE_AREA.values[0], marker ='*')


# In[ ]:


#name + group.WATER_TYPE_AREA.values[0]

