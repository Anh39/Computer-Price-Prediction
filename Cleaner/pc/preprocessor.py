import pandas as pd
import folder_path
import json
import re,os
from Cleaner.pc.preprocessor_support import *

result_category = []

raw_datas = read_folder(folder_path.hacom.path)

def extract_number(input_str):
    if (type(input_str) == int):
        return input_str
    numbers = re.findall(r'\d+', input_str)
    if (numbers) :
        return int(numbers[0])
    else:
        return None
def max_len(input_list : list):
    max_len = 0
    for ele in input_list:
        max_len = max(max_len,len(ele))
    return max_len
def three_colum_format(raw_data_infos,warranty):
    # if (type(raw_data_infos[0]) == str):
    #     warranty = extract_number(warranty)
    #     for i in range(len(raw_data_infos)):
    #         raw_data_info = raw_data_infos[i]
    #         new_data_info = [None,None,None]
    #         new_data_info[0] = raw_data_info
    #         new_data_info[1] = 1
    #         new_data_info[2] = warranty
    #         raw_data_infos[i] = new_data_info
    #     return raw_data_infos
    if (raw_data_infos == None):
        return
    if max_len(raw_data_infos) > 3:
        for raw_data in raw_data_infos:
            if (len(raw_data) > 3):
                raw_data_infos.remove(raw_data)
    if max_len(raw_data_infos) == 3:
        new_raw_data_infos = []
        while(len(raw_data_infos[0]) != 3):
            raw_data_infos.pop(0)
        for raw_data_info in raw_data_infos:
            if(len(raw_data_info) == 3):
                new_raw_data_infos.append(raw_data_info)
        raw_data_infos = new_raw_data_infos
        
        for raw_data_info in raw_data_infos:
            raw_data_info[1] = extract_number(raw_data_info[1])
            raw_data_info[2] = extract_number(raw_data_info[2])
    elif max_len(raw_data_infos) == 2:
        new_raw_data_infos = []
        while(len(raw_data_infos[0]) != 2):
            raw_data_infos.pop(0)
        for raw_data_info in raw_data_infos:
            if(len(raw_data_info) == 2):
                new_raw_data_infos.append(raw_data_info)
            elif(len(raw_data_info) == 1):
                new_raw_data_infos[-1][1] += ' ' + str(raw_data_info)
        raw_data_infos = new_raw_data_infos
        
        warranty = extract_number(warranty)
        for i in range(len(raw_data_infos)):
            raw_data_info = raw_data_infos[i]
            new_data_info = [None,None,None]
            new_data_info[0] = raw_data_info[0] + ' ' + raw_data_info[1]
            new_data_info[1] = 1
            new_data_info[2] = warranty
            raw_data_infos[i] = new_data_info
    if (len(raw_data_infos[0]) != 3):
        print(max_len(raw_data_infos))
        raise Exception
    return raw_data_infos

            

def process(raw_data):
    raw_data['Detail Info'] = three_colum_format(raw_data['Detail Info'],raw_data['Warrent'])
    cpu_result = cpu_process_function(raw_data['Detail Info'],raw_data['Info'],raw_data['Filename'])
    gpu_result = gpu_process_function(raw_data['Detail Info'],raw_data['Info'],raw_data['Filename'])
    ram_result = ram_process_function(raw_data['Detail Info'],raw_data['Info'],raw_data['Filename'])
    psu_result = psu_process_function(raw_data['Detail Info'],raw_data['Info'],raw_data['Filename'])
    cooler_result = cooler_process_function(raw_data['Detail Info'],raw_data['Info'],raw_data['Filename'])
    storage_result = storage_process_function(raw_data['Detail Info'],raw_data['Info'],raw_data['Filename'])
    os_result = os_process_function(raw_data['Detail Info'],raw_data['Info'],raw_data['Filename'])
    if (cpu_result != None):
        result = info_format(raw_data['Detail Info'],raw_data['Info'],result_category)
        result['Price'] = raw_data['Price']
        result['Link'] = raw_data['Link']
        result.update(cpu_result)
        if (gpu_result != None):
            result.update(gpu_result)
        result.update(psu_result)
        result.update(ram_result)
        result.update(storage_result)
        result.update(cooler_result)
        result.update(os_result)
        return result
    # else:
    #     result = info_format(raw_data['Detail Info'],raw_data['Info'])
    #     result['Price'] = raw_data['Price']
    #     result['Link'] = raw_data['Link']
    #     return result
raw_data = raw_datas[0]
cols = []
for category in result_category:
    cols.append(category+ ' Name')
    cols.append(category+ ' Amount')
    cols.append(category+ ' Warranty')
cols.append('Price')
cols.append('Link')
cols.append('CPU Name')
cols.append('RAM')
cols.append('Memory Type')
cols.append('Storage')
cols.append('Storage Type')
cols.append('GPU Name')
cols.append('GPU VRAM')
cols.append('PSU')
cols.append('Cooler')
cols.append('OS')
cols.append('CPU Achitecture')
cols.append('CPU Core')
cols.append('CPU Thread')
cols.append('CPU Cache')
cols.append('Max DDR Support')
cols.append('Base Clock')
cols.append('Max Clock')
cols.append('IGPU Clock')
processed_datas = pd.DataFrame(columns=cols)
it = 0
for raw_data in raw_datas:
    try:
        print(raw_data['Link'])
        if (raw_data['Link'] != 'https://hacom.vn/pc-hp-pro-280-g9-tower-i5-12500-8gb-ram-512gb-ssd-wl-bt-k-m-win11-72g57pa'):
            pass
        processed_data = process(raw_data)
        if (processed_data == None):
            continue
        for key in processed_data:
            if (type(processed_data[key]) == str):
                processed_data[key] = processed_data[key].strip()
        processed_datas.loc[it] = processed_data
        it+=1
    except Exception as e:
        print(e)
  
processed_datas.to_csv(folder_path.output.preprocessed_data,index=False)

# for raw_data in raw_datas:
#     print(raw_data)
#     print()