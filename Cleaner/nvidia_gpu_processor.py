import pandas as pd
import folder_path
import json
import re,os,csv



final_cols = [    
    'Name',
    'VRAM'
]
df = pd.read_csv(folder_path.nvidia.gpu_result)

def format_name(input_str : str) -> str:
    # remove_list = ['AMD','Athlon','™','Radeon','Ryzen']
    remove_list = ['™','GeForce', 'RTX','GTX']
    for remove_ele in remove_list:
        input_str = input_str.replace(remove_ele,'')
    return input_str.strip()
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
df['Name'] = df['Name'].apply(format_name)
df['VRAM'] = df['Standard Memory Config'].apply(extract_number)
        

drop_cols = []
for col in df.columns:
    if col not in final_cols:
        drop_cols.append(col)
df = df.drop(columns=drop_cols)

df.to_csv(folder_path.output.nvidia_gpu_data,index=False)
