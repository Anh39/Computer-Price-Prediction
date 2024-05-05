import pandas as pd
import folder_path
import json
import re,os

result_category = ['CPU','RAM','Main','Storage','GPU','Case','Cooler']

def read_folder(folder):
    paths = folder_path.util.get_tree(folder)
    result = []
    for filename in paths:
        # print(filename,paths[filename])
        if (os.path.basename(filename) not in ['links.json','exception.json']):
            with open(paths[filename],'r') as file:
                result.append(json.loads(file.read()))
    return result
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
    if (type(raw_data_infos[0]) == str):
        warranty = extract_number(warranty)
        for i in range(len(raw_data_infos)):
            raw_data_info = raw_data_infos[i]
            new_data_info = [None,None,None]
            new_data_info[0] = raw_data_info
            new_data_info[1] = 1
            new_data_info[2] = warranty
            raw_data_infos[i] = new_data_info
        return raw_data_infos
    elif max_len(raw_data_infos) > 3:
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

def normalize(input_str : str) -> str:
    output_str = input_str.strip()
    output_str = output_str.lower()
    return output_str
def simple_search(input_str : str,matches : list[str]):
    normalized_input_str = normalize(input_str)
    for match in matches:
        if (normalize(match) in normalized_input_str):
            return True
    return False
def info_format(raw_data_infos):
    mapping = {
        'CPU' : ['CPU', 'bộ vi xử lý','Bộ xử lý','Bộ VXL', 'Intel Core','Intel® Core™','Chíp xử lý','INTEL PENTIUM'],
        'RAM' : ['RAM',' DDR','PCIe','NVMe'],
        'Main' : ['Mainboard','Bo mạch chủ','Main'],
        'Storage' : ['SSD','HDD','Ổ cứng'],
        'GPU' : ['GPU','Card màn hình','RTX','Card'],
        'PSU' : ['PSU','Nguồn'],
        'Case' : ['Case'],
        'Cooler' : ['Fan','Tản nhiệt']
    }
    result = {}
    for category in result_category:
        flag = True
        for raw_data_info in raw_data_infos:
            if simple_search(raw_data_info[0],mapping[category]):
                result[category+' Name'] = raw_data_info[0]
                result[category+' Amount'] = raw_data_info[1]
                result[category+' Warranty'] = raw_data_info[2]
                flag = False
                break
        if (flag == True):
            result[category+' Name'] = ''
            result[category+' Amount'] = 0
            result[category+' Warranty'] = 0
    return result
def process(raw_data):
    result = info_format(three_colum_format(raw_data['Info'],raw_data['Warrent']))
    result['Price'] = raw_data['Price']
    result['Link'] = raw_data['Link']
    return result
raw_data = raw_datas[0]
cols = []
for category in result_category:
    cols.append(category+ ' Name')
    cols.append(category+ ' Amount')
    cols.append(category+ ' Warranty')
cols.append('Price')
cols.append('Link')
processed_datas = pd.DataFrame(columns=cols)
it = 0
for raw_data in raw_datas:
    try:
        print(raw_data['Link'])
        processed_data = process(raw_data)
        for key in processed_data:
            if (type(processed_data[key]) == str):
                processed_data[key] = processed_data[key].strip()
        processed_datas.loc[it] = processed_data
        it+=1
    except Exception as e:
        print(e)
  
processed_datas.to_csv(folder_path.output.processed_data,index=False)

# for raw_data in raw_datas:
#     print(raw_data)
#     print()