# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 17:41:38 2018

@author: a002028
"""

import os
import numpy as np
import pandas as pd

"""
Convert format of model-output to a readable format..
"""

w_dir = u'D:\\Temp\\ekostat_data\\TOOLBOX_försök2\\'
out_dir =  u'D:\\Temp\\ekostat_data\\model_data_new_format\\'
wb_match = pd.read_csv(open('D:\\github\\ekostat_calculator\\resources\\mappings\\water_body_match.txt'), sep = '\t')

original_header = u'EUCD            YYYY-MM-DD      Djup(m) Salt (psu o/oo)   O2 (ml/l)   PO4 (µmol/l)   TotP (µmol/l)   NO3 (µmol/l)    NH4 (µmol/l)   TotN (µmol/l)     Chla (ug/l)   Siktdjup (m)\n'
new_header = u'EUCD\tYYYY-MM-DD\tDjup(m)\tSalt (psu o/oo)\tO2 (ml/l)\tPO4 (µmol/l)\tTotP (µmol/l)\tNO3 (µmol/l)\tNH4 (µmol/l)\tTotN (µmol/l)\tChla (ug/l)\tSiktdjup (m)'.split(u'\t')
# new_header = '...'.split(u'\t')

file_list = os.listdir(w_dir)
for i, fid in enumerate(file_list):
    print(i, '/', len(file_list))
    
    with open(w_dir+fid) as f:
        lines = f.readlines()
    
    if lines[0] != original_header:
        print('File header != new_header')
        break
    
    # creating a 2d array using the 2nd line. Skipping header line (original_header)..
    data_array = np.array( [ lines[1].replace(u' ',u'').replace(u'\n',u'').split(u'\t') ] )
    
    for row in lines[2:]:
        add_row = [ row.replace(u' ',u'').replace(u'\n',u'').split(u'\t') ]
        data_array = np.concatenate( (data_array, add_row), axis=0 )

    df = pd.DataFrame(data_array, columns = new_header)
    df.loc[:,'SEA_AREA_NAME'] = df.apply(lambda row: wb_match[wb_match['EU_CD'] == row.EUCD]['NAME'].values[0], axis = 1)
    
    df.to_csv(out_dir + fid, sep='\t', encoding='cp1252', index=False)
