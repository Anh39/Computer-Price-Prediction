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
df = pd.read_csv(folder_path.output.preprocessed_data)

def get_cpu_info():
    df1 = pd.read_csv(folder_path.output.intel_data)
    df2 = pd.read_csv(folder_path.output.amd_data)
    result_df = pd.concat([df1,df2],ignore_index=True)
    return result_df

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

def extract_name(input_str : str) -> str:
    if (pd.notna(input_str)):
        cpu_name = input_str.split('Core')[-1]
        return cpu_name

df['CPU Spec'] = df['CPU Name'].apply(extract_name)

# drop_cols = []
# for col in df.columns:
#     if col not in final_cols:
#         drop_cols.append(col)
# df = df.drop(columns=drop_cols)

df.to_csv(folder_path.output.processed_data,index=False)
