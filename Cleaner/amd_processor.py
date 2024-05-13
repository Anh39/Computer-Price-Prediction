import pandas as pd
import folder_path
import json
import re,os,csv



final_cols = [    
    # 'Code Name', 
    'Series', 
    # 'Form Factor',
    'Achitecture',
    'Name',
    'Total Cores', 
    'Total Threads', 
    'Max Boost Clock', 
    'Base Clock', 
    'Total Cache',
    'Base Power', 
    'Max Power', 
    'Launch Date', 
    'Memory Type', 
    'Memory Channels', 
    # 'IGPU Name', 
    'IGPU Frequency', 
    # 'Link'
]
df = pd.read_csv(folder_path.output.pre_amd_data)

def extract_number(input_str):
    if (pd.isna(input_str)):
        return 0
    if (type(input_str) == int):
        return input_str
    numbers = re.findall(r'\d+', input_str)
    if (numbers) :
        return int(numbers[0])
    else:
        return None
def extract_float(input_str):
    if (pd.isna(input_str)):
        return 0
    if (type(input_str) == int):
        return input_str
    numbers = re.findall(r'\b\d+\.\d+\b', input_str)
    if (numbers) :
        return float(numbers[0])
    else:
        return float(extract_number(input_str))
def extract_numbers(input_str):
    if (pd.isna(input_str)):
        return (0,0)
    if (type(input_str) == int):
        return input_str
    numbers = re.findall(r'\d+', input_str)
    if (numbers) :
        return (int(numbers[0]),int(numbers[1]))
    else:
        return None
def format_name(input_str : str) -> str:
    # remove_list = ['AMD','Athlon','™','Radeon','Ryzen']
    remove_list = ['AMD','™']
    for remove_ele in remove_list:
        input_str = input_str.replace(remove_ele,'')
    return input_str.strip()

df['Achitecture'] = df['Achitecture'].apply(extract_number)
df['Base Clock'] = df['Base Clock'].apply(extract_float)

df['Max Boost Clock'] = df['Max Boost Clock'].apply(extract_float)
for index,row in df.iterrows():
    if pd.notna(row['Max Power']):
        min_tdp,max_tdp = extract_numbers(row['Max Power'])
        row['Base Power'] = min_tdp
        row['Max Power'] = max_tdp
    else:
        row['Base Power'] = extract_number(row['Base Power'])
        row['Max Power'] = row['Base Power']
    df.iloc[index] = row
        
df['IGPU Frequency'] = df['IGPU Frequency'].apply(extract_number)
df['L2 Cache'] = df['L2 Cache'].apply(extract_number)
df['L3 Cache'] = df['L3 Cache'].apply(extract_number)
df['Total Cache'] = df['L2 Cache'] + df['L3 Cache']
df['Memory Type'] = df['Memory Type'].apply(extract_number)
df['Name'] = df['Name'].apply(format_name)
drop_cols = []
for col in df.columns:
    if col not in final_cols:
        drop_cols.append(col)
df = df.drop(columns=drop_cols)

df.to_csv(folder_path.output.amd_data,index=False)
