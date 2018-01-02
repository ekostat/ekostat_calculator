
# coding: utf-8

# In[1]:

# Reload when code changed:
get_ipython().magic('load_ext autoreload')
get_ipython().magic('autoreload 2')
get_ipython().magic('pwd')


# In[2]:

import os 
import core
import importlib
importlib.reload(core) 
import pandas as pd
pd.__version__


# ### Load directories

# In[3]:

root_directory = os.getcwd()
workspace_directory = root_directory + '/workspaces' 
resource_directory = root_directory + '/resources'


# # LOAD WORKSPACES

# ### Load default workspace

# In[4]:



default_workspace = core.WorkSpace(name='default', 
                                   parent_directory=workspace_directory, 
                                   resource_directory=resource_directory) 


# ### Add new workspace

# In[5]:

lv_workspace = core.WorkSpace(name='lv', 
                              parent_directory=workspace_directory, 
                              resource_directory=resource_directory) 


# ### Copy files from default workspace to make a clone

# In[6]:

lv_workspace.add_files_from_workspace(default_workspace, overwrite=True)


# ### Load all data in lv_workspace

# In[7]:

lv_workspace.load_all_data()


# # Set first filter and load filtered data

# ### Set first data filter 

# In[8]:

# show available waterbodies
workspace_data = lv_workspace.data_handler.get_all_column_data_df()
lst = workspace_data.WATER_TYPE_AREA.unique()
print('Type Areas in dataset:\n{}'.format('\n'.join(lst)))


# In[9]:

lst = workspace_data.SEA_AREA_NAME.unique()
print('Waterbodies in dataset:\n{}'.format('\n'.join(lst)))


# In[10]:

include_WB = ['Gullmarn centralbassäng', 'Rivö fjord', 'Byfjorden', 'Havstensfjorden']
include_stations = [] 
exclude_stations = []
include_years = ['2015', '2017'] 

lv_workspace.set_data_filter(step=0, filter_type='include_list', filter_name='SEA_AREA_NAME', data=include_WB)
lv_workspace.set_data_filter(step=0, filter_type='include_list', filter_name='STATN', data=include_stations) 
lv_workspace.set_data_filter(step=0, filter_type='exclude_list', filter_name='STATN', data=exclude_stations) 
lv_workspace.set_data_filter(step=0, filter_type='include_list', filter_name='MYEAR', data=include_years) 


# ### Apply first data filter 

# In[11]:

lv_workspace.apply_first_filter() # This sets the first level of data filter in the IndexHandler 


# ### Extract filtered data 

# In[12]:

data_after_first_filter = lv_workspace.get_filtered_data(level=0) # level=0 means first filter 
print('{} rows mathing the filter criteria'.format(len(data_after_first_filter)))
data_after_first_filter.head()
data_after_first_filter.shape

# # Set subset filter and load subset data 

# ### Set subset filter 

# In[13]:

include_WB = ['Gullmarn centralbassäng', 'Rivö fjord']
include_stations = ['BJÖRKHOLMEN']
# Lägg till något som kan plocka in stationer öven ifrån närliggande WB?
exclude_stations = ['SLÄGGÖ'] # Example that both include and exclude are possible 
include_years = ['2016', '2017']

lv_workspace.set_data_filter(step=1, subset='A', filter_type='include_list', filter_name='SEA_AREA_NAME', data=include_WB)
lv_workspace.set_data_filter(step=1, subset='A', filter_type='include_list', filter_name='STATN', data=include_stations)
lv_workspace.set_data_filter(step=1, subset='A', filter_type='exclude_list', filter_name='STATN', data=exclude_stations)
lv_workspace.set_data_filter(step=1, subset='A', filter_type='include_list', filter_name='MYEAR', data=include_years)

# In[ ]:




# ### Apply subset filter 

# In[14]:

lv_workspace.apply_subset_filter(subset='A') # Not handled properly by the IndexHandler

lv_workspace.initiate_quality_factors()

#tolerance_filter_file_path = u'D:/Utveckling/GitHub/ekostat_calculator/resources/filters/tolerance_filter_template.txt'
#tolerance_filter = core.ToleranceFilter('test_tolerance_filter', file_path=tolerance_filter_file_path)
#
#lv_workspace.quality_factor_NP.calculate_quality_factor(tolerance_filter)
# ### Extract filtered data 

data_after_subset_filter = lv_workspace.get_filtered_data(level=1, subset='A') # level=0 means first filter 
print('{} rows mathing the filter criteria'.format(len(data_after_subset_filter)))
data_after_subset_filter.head()
data_after_subset_filter.shape

import numpy as np
np.where(lv_workspace.index_handler.subset_filter)

f = lv_workspace.get_data_filter_object(step=1, subset='A')

f.all_filters

f.exclude_list_filter

f.include_list_filter







#s = lv_workspace.get_step_1_object('A')
#
#s.data_filter.all_filters
#
#
#f0 = lv_workspace.get_data_filter_object(step=0)
#
#
#f0.exclude_list_filter
#
#f0.include_list_filter
