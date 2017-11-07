
# coding: utf-8

# In[1]:

import os 
import core
import importlib
importlib.reload(core)


# In[2]:

root_directory = os.getcwd()
workspace_directory = root_directory + '/workspaces' 
resource_directory = root_directory + '/resources'


# In[3]:

default_workspace = core.WorkSpace(name='default', 
                                   parent_directory=workspace_directory, 
                                   resource_directory=resource_directory) 


# In[4]:

default_workspace.get_all_file_paths_in_workspace()


# In[5]:

# Add new workspace 
mw_workspace = core.WorkSpace(name='mw', 
                              parent_directory=workspace_directory, 
                              resource_directory=resource_directory) 


# In[6]:

# Copy files from default workspace 
mw_workspace.add_files_from_workspace(default_workspace, overwrite=True)


# In[7]:

mw_workspace.load_all_data()


# In[9]:

mw_workspace.data_handler.physical_chemical.para_list


# In[11]:

sorted(mw_workspace.data_handler.physical_chemical.df.columns)


# In[ ]:




# In[ ]:




# In[ ]:




# In[12]:

# Add a new subset
mw_workspace.add_subset('B')


# In[13]:

sub = mw_workspace.get_subset_object('A')
sub.get_all_file_paths_in_subset()


# In[9]:

sub.subset_directory
[item for item in os.listdir(sub.subset_directory) if '.' not in item]


# In[10]:

# Copy (clone) subset 
subsetA = mw_workspace.get_subset_object('A') 
subsetB = mw_workspace.get_subset_object('B') 
subsetB.add_files_from_subset(subsetA, overwrite=True)


# In[11]:

subsetA.steps


# In[ ]:




# In[14]:

# Add new Subset 
mw_workspace.add_subset()


# In[15]:

step0 = mw_workspace.get_step_object('step_0') 


# In[16]:

step0.get_all_file_paths_in_workstep()


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



