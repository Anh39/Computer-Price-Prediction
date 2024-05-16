import pandas as pd
import numpy as np
import folder_path
import json
import re,os,csv



type_config = {}

with open(folder_path.config.lap_type,'r') as file:
    type_config = json.loads(file.read())

final_cols = [    
    'Price', 
    'CPU Name',
    'CPU Gen',
    'CPU Achitecture',
    'CPU Core',
    'CPU Thread', 
    'CPU Base Clock',
    'CPU Max Clock',
    'CPU Cache',
    'CPU Intel',
    'Base Power',
    'Max Power',
    'RAM',
    'Memory Type',
    'Max DDR Support',
    'Storage',
    'Storage Type',
    'GPU Name',
    'GPU VRAM',
    'GPU Onboard',
    'GPU AMD',
    'GPU NVIDIA',
    'Display Type',
    'Display Size',
    'Display Width',
    'Display Height',
    'Display Frequency',
    'OS',
    'Warrant'
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
        return 0
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
        return [0]
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

def extract_storage(input_str : str) -> int:
    if ('TB' in input_str):
        return 1024*int(extract_number(input_str))
    return int(extract_number(input_str))
def map_storage(input_str : str) -> int:
    if (pd.isna(input_str)):
        return 1
    return type_config['Storage Type'][input_str]
def map_display(input_str : str) -> int:
    if (input_str != 'IPS'):
        return type_config['Display Type']['Other']
    else:
        return type_config['Display Type']['IPS']
def display_width(input_str : str) -> int:
    return extract_numbers(input_str)[0]
def display_height(input_str : str) -> int:
    return extract_numbers(input_str)[1]
def format_price(input_str : str) -> int:
    return (extract_number(str(input_str).replace('.','').replace(',','')))
def format_display_size(input_str : str) -> int:
    if (int(input_str) == 0):
        return 15.6
    else:
        return int(input_str)

df['Price'] = df['Price'].apply(format_price)
df['CPU Achitecture'] = df['CPU Achitecture'].replace(0,7)
df['Base Power'] = df['Base Power'].replace(0,9)
df['Max Power'] = df['Max Power'].replace(0,15)
df['RAM'] = df['RAM'].apply(extract_number)
df['RAM'] = df['RAM'].replace(0,8)
df['Memory Type'] = df['Memory Type'].apply(extract_number)
# df['Max DDR Support'] = df['Max DDR Support'].apply(extract_number)
df['Storage'] = df['Storage'].apply(extract_storage)
df['Storage Type'] = df['Storage Type'].apply(map_storage)
df['GPU VRAM'] = df['GPU VRAM'].fillna(0)
df['Display Type'] = df['Display Type'].apply(map_display)
df['Display Size'] = df['Display Size'].apply(extract_float)
df['Display Size'] = df['Display Size'].apply(format_display_size)
df['Display Resolution'] = df['Display Resolution'].fillna('1920x1080')
df['Display Width'] = df['Display Resolution'].apply(display_width)
df['Display Height'] = df['Display Resolution'].apply(display_height)
df['Display Frequency'] = df['Display Frequency'].apply(extract_number)
df['Display Frequency'] = df['Display Frequency'].replace(0,60)
df['OS'] = df['OS'].replace(0,10)
df['Warrant'] = df['Warrant'].fillna(12)



for index,row in df.iterrows():
    if row['Memory Type'] == 0:
        df.at[index,'Memory Type'] = row['Max DDR Support']
        

drop_cols = []
for col in df.columns:
    if col not in final_cols:
        drop_cols.append(col)
df = df.drop(columns=drop_cols)
df = df[df['Price'] != 0]
df.to_csv(folder_path.output.processed_data,index=False)

print(len(df))