import pandas as pd
import folder_path
import json
import re,os,csv

category_mappping = {
    'Family' : 'Code Name', 
    'Series' : 'Series', 
    'Form Factor' : 'Form Factor',
    'Processor Technology for CPU Cores' : 'Achitecture',
    'Name' : 'Name',
    '# of CPU Cores' : 'Total Cores', 
    '# of Threads' : 'Total Threads', 
    'Max. Boost Clock' : 'Max Boost Clock', 
    'Base Clock' : 'Base Clock', 
    'Total Cache' : 'Total Cache',
    'L1 Cache' : 'Cache', 
    'L2 Cache' : 'L2 Cache',
    'L3 Cache' : 'L3 Cache', 
    'Default TDP' : 'Base Power', 
    'AMD Configurable TDP (cTDP)' : 'Max Power', 
    'Launch Date' : 'Launch Date', 
    'System Memory Type' : 'Memory Type', 
    # 'Max Memory Size (dependent on memory type)' : 'Max Memory Size', #
    'Memory Channels' : 'Memory Channels', 
    # 'Max Memory Bandwidth' : 'Max Memory Bandwidth', #
    'Graphics Model' : 'IGPU Name', 
    'Graphics Frequency' : 'IGPU Frequency', 

    'Link' : 'Link', 
}

raw_df = pd.read_csv(folder_path.amd.cpu_result)
cols = category_mappping.values()
cols = set(cols)
cols = list(cols)
cols.sort()
preprocessed_df = pd.DataFrame(columns=cols)
old_cols = raw_df.columns
for i in range(len(raw_df)):
    new_row = {}
    for old_col in old_cols:
        if (old_col in category_mappping):
            new_row[category_mappping[old_col]] = raw_df.iloc[i][old_col]
    new_row['Link'] = 'https://www.amd.com/en/products/specifications/processors.html'
    preprocessed_df.loc[i] = new_row
    
preprocessed_df.to_csv(folder_path.output.pre_amd_data,index=False)


    