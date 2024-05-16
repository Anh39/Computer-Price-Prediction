import pandas as pd
import folder_path
import json
import re,os
from Cleaner.preprocessor_support import *

result_category = []

raw_datas = read_folders([
    folder_path.hacom.lap_common,
    folder_path.hacom.lap_game,
    folder_path.anphat.lap_common,
    folder_path.anphat.lap_game,
    folder_path.fpt.lap
])

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
    if (raw_data_infos != [] and len(raw_data_infos[0]) != 3):
        if (len(raw_data_infos[0]) == 1):
            for i in range(len(raw_data_infos)):
                raw_data_infos[i].append(1)
                raw_data_infos[i].append(warranty)
        else:
            raise Exception
    return raw_data_infos

            

def process(raw_data):
    raw_data['Detail Info'] = three_colum_format(raw_data['Detail Info'],raw_data['Warrant'])
    process_functions = [
        gpu_process_function,
        ram_process_function,
        display_process_function,
        storage_process_function,
        psu_process_function,
        os_process_function
    ]
    cpu_result = cpu_process_function(raw_data['Detail Info'],raw_data['Info'],raw_data['Filename'])
    additional_info = {}
    for process_function in process_functions:
        additional_info.update(process_function(raw_data['Detail Info'],raw_data['Info'],raw_data['Filename']))
    if (cpu_result['CPU Name'] != None):
        result = info_format(raw_data['Detail Info'],raw_data['Info'],result_category)
        result['Price'] = raw_data['Price']
        result['Link'] = raw_data['Link']
        result['Warrant'] = extract_number(raw_data['Warrant'])
        result.update(cpu_result)
        result.update(additional_info)
        return result
    # else:
    #     result = info_format(raw_data['Detail Info'],raw_data['Info'])
    #     result['Price'] = raw_data['Price']
    #     result['Link'] = raw_data['Link']
    #     return result
raw_data = raw_datas[0]
cols = ['Price','Link',
        'CPU Name','CPU Lithography','CPU Core','CPU Thread','CPU Cache','CPU Base Clock','CPU Max Clock',
        'CPU Intel','CPU Cache','Base Power','Max Power','CPU Series',
        'RAM','Memory Type','Max DDR Support',
        'Storage','Storage Type',
        'GPU Name','GPU VRAM','IGPU Cloock','GPU Onboard','GPU AMD','GPU NVIDIA',
        'Display Type','Display Size','Display Resolution','Display Frequency','Display Color',
        'OS',
        'Warrant']
processed_datas = pd.DataFrame(columns=cols)
it = 0
black_list_links = [
    'https://www.anphatpc.com.vn/dien-thoai-di-dong-asus-rog-6-ai2201-1d006ww.html',
    'https://www.anphatpc.com.vn/dien-thoai-di-dong-asus-rog-6-ai2201-1a005ww.html',
    'https://www.anphatpc.com.vn/may-choi-game-cam-tay-msi-claw-a1m.html'
]
for raw_data in raw_datas:
    try:
        if (raw_data['Link'] in black_list_links):
            continue
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