import pandas as pd
import folder_path
import json
import re,os,csv

category_mappping = {
    'Code Name' : 'Code Name',
    'Product Collection' : 'Series',
    'Vertical Segment' : 'Form Factor',
    'Lithography' : 'Achitecture',
    'Processor Number' : 'Name',
    'Total Cores' : 'Total Cores',
    'Total Threads' : 'Total Threads',
    'Max Turbo Frequency' : 'Max Boost Clock',
    'Performance-core Max Turbo Frequency' : 'Max Boost Clock',
    'Efficient-core Base Frequency' : 'Base Clock',
    'Processor Base Frequency' : 'Base Clock',
    'Configurable TDP-down Base Frequency' : 'Base Clock',
    'Cache' : 'Total Cache',
    'Total L2 Cache' : 'L2 Cache',
    'Total L3 Cache' : 'L3 Cache',
    'Processor Base Power' : 'Base Power',
    'Configurable TDP-down' : 'Base Power',
    'TDP' : 'Max Power',
    'Configurable TDP-up' : 'Max Power',
    'Maximum Turbo Power' : 'Max Power',
    'Launch Date' : 'Launch Date',
    'Memory Types' : 'Memory Type',
    # 'Max Memory Size (dependent on memory type)' : 'Max Memory Size',
    'Memory Channels' : 'Memory Channels',
    # 'Max Memory Bandwidth' : 'Max Memory Bandwidth',
    'GPU Name‡' : 'IGPU Name',
    # 'Graphics Base Frequency' : 'IGPU Base Frequency',
    'Graphics Max Dynamic Frequency' : 'IGPU Frequency',
    'Link' : 'Link'
}

def read_folder(folder):
    paths = folder_path.util.get_tree(folder)
    result = []
    for filename in paths:
        # print(filename,paths[filename])
        if (os.path.basename(filename) not in ['links.json','exception.json']):
            new_data = []
            with open(paths[filename],'r',newline='',encoding='utf-8') as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    new_data.append(row)
            result.append(new_data)
    return result
raw_datas = read_folder(folder_path.intel.path)

def column_selection(input_list : list[list]):
    result = {}
    for row in input_list:
        if (len(row) == 2):
            if (row[0] in category_mappping):
                result[category_mappping[row[0]]] = row[1]
    for key in category_mappping:
        if (category_mappping[key] not in result):
            result[category_mappping[key]] = None
    return result

preprocessed_datas = []

for raw_data in raw_datas:
    preprocessed_datas.append(column_selection(raw_data))
# for i in range(len(preprocessed_datas)):
#     print(raw_datas[i])
#     print(preprocessed_datas[i])
#     print()
#     raise Exception

cols = category_mappping.values()
cols = set(cols)
cols = list(cols)
cols.append('Gen')
cols.sort()
df = pd.DataFrame(columns=cols)
def extract_gen(input_str : str):
    if ('intel-core-ultra-' in input_str):
        input_str = input_str.split('intel-core-ultra-')[-1][0]
        return int(input_str)
    elif ('intel-core-i' in input_str):
        input_str = input_str.split('intel-core-i')[-1][0]
        return int(input_str)
    else:
        input_str = input_str.split('intel-core-')[-1][0]
        return int(input_str)
for i in range(len(preprocessed_datas)):
    preprocessed_datas[i]['Gen'] =  extract_gen(preprocessed_datas[i]['Link'])
    df.loc[i] = preprocessed_datas[i]


df.to_csv(folder_path.output.pre_intel_data,index=False)