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
    'Link'
]
df = pd.read_csv(folder_path.output.pre_intel_data)

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
    remove_list = ['™']
    for remove_ele in remove_list:
        input_str = input_str.replace(remove_ele,'')
    return input_str.strip()

df['Achitecture'] = df['Achitecture'].apply(extract_number)
df['Base Clock'] = df['Base Clock'].apply(extract_float)
df['Max Boost Clock'] = df['Max Boost Clock'].apply(extract_float)
df['IGPU Frequency'] = df['IGPU Frequency'].apply(extract_number)
# df['L2 Cache'] = df['L2 Cache'].apply(extract_number)
# df['L3 Cache'] = df['L3 Cache'].apply(extract_number)
df['Total Cache'] = df['Total Cache'].apply(extract_number)
df['Memory Type'] = df['Memory Type'].apply(extract_number)
df['Name'] = df['Name'].apply(format_name)
for index,row in df.iterrows():
    if pd.notna(row['Max Power']) and pd.notna(row['Base Power']):
        row['Base Power'] = extract_number(row['Base Power'])
        row['Max Power'] = extract_number(row['Max Power'])
    elif pd.isna(row['Max Power']):
        row['Base Power'] = extract_number(row['Max Power'])
        row['Max Power'] = extract_number(row['Max Power'])
    else:
        row['Base Power'] = extract_number(row['Base Power'])
        row['Max Power'] = extract_number(row['Base Power'])
    if pd.isna(row['Base Clock']) or row['Base Clock'] == 0:
        row['Base Clock'] = row['Max Boost Clock']
    elif pd.isna(row['Max Boost Clock']) or row['Max Boost Clock'] == 0:
        row['Max Boost Clock'] = row['Base Clock']
    if (row['Base Clock'] > 100):
        row['Base Clock'] /= 1000
    if (row['Max Boost Clock'] > 100):
        row['Max Boost Clock'] /= 1000
    if (row['IGPU Frequency'] < 100):
        row['IGPU Frequency'] *= 1000
    df.iloc[index] = row
        

drop_cols = []
for col in df.columns:
    if col not in final_cols:
        drop_cols.append(col)
df = df.drop(columns=drop_cols)

df.to_csv(folder_path.output.intel_data,index=False)
