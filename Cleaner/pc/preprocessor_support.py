import pandas as pd
import folder_path
import json
import re,os
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
def read_folder(folder):
    paths = folder_path.util.get_tree(folder)
    result = []
    for filename in paths:
        # print(filename,paths[filename])
        if (os.path.basename(filename) not in ['links.json','exception.json']):
            with open(paths[filename],'r') as file:
                data = json.loads(file.read())
                data['Filename'] = filename
                result.append(data)
    return result
def get_cpu_info():
    df1 = pd.read_csv(folder_path.output.intel_data)
    df2 = pd.read_csv(folder_path.output.amd_data)
    result_df = pd.concat([df1,df2],ignore_index=True)
    return result_df
def get_gpu_info():
    df1 = pd.read_csv(folder_path.output.amd_gpu_data)
    df2 = pd.read_csv(folder_path.output.nvidia_gpu_data)
    result_df = pd.concat([df1,df2],ignore_index=True)
    return result_df
cpu_infos = get_cpu_info()
gpu_infos = get_gpu_info()
cpu_names = cpu_infos['Name'].to_list()
gpu_names = gpu_infos['Name'].to_list()
def cpu_process_function(detail_data_infos,data_infos,filename):
    this_cpu_name = None
    for cpu_name in cpu_names:
        if cpu_name != 'B75' and cpu_name.replace(' ','-') in filename.replace(' ','-'):
            this_cpu_name = cpu_name
            break 
    for data_info in data_infos:
        if (this_cpu_name == None):
            for cpu_name in cpu_names:
                if cpu_name != 'B75' and cpu_name.replace(' ','-') in data_info.replace(' ','-'):
                    this_cpu_name = cpu_name
                    break
    if (detail_data_infos != None):
        for detail_data_info in detail_data_infos:
            if (this_cpu_name == None):
                for cpu_name in cpu_names:
                    if cpu_name != 'B75' and cpu_name.replace(' ','-') in detail_data_info[0].replace(' ','-'):
                        this_cpu_name = cpu_name
                        break
    if (this_cpu_name == None):
        return None
    else:
        index = cpu_names.index(this_cpu_name)
        result = {
            'CPU Achitecture' : cpu_infos.iloc[index]['Achitecture'],
            'CPU Name' : cpu_infos.iloc[index]['Name'],
            'CPU Core' : cpu_infos.iloc[index]['Total Cores'],
            'CPU Thread' : cpu_infos.iloc[index]['Total Threads'],
            'CPU Cache' : cpu_infos.iloc[index]['Total Cache'],
            'Max DDR Support' : cpu_infos.iloc[index]['Memory Type'],
            'Base Clock' : cpu_infos.iloc[index]['Base Clock'],
            'Max Clock' : cpu_infos.iloc[index]['Max Boost Clock'],
            'IGPU Clock' : cpu_infos.iloc[index]['IGPU Frequency'] 
        }
        return result
def gpu_process_function(detail_data_infos,data_infos,filename):
    this_gpu_name = None
    for gpu_name in gpu_names:
        if gpu_name.replace(' ','-') in filename.replace(' ','-'):
            this_gpu_name = gpu_name
            break 
    for data_info in data_infos:
        if (this_gpu_name == None):
            for gpu_name in gpu_names:
                if gpu_name.replace(' ','-') in data_info.replace(' ','-'):
                    this_gpu_name = gpu_name
                    break
    if (detail_data_infos != None):
        for detail_data_info in detail_data_infos:
            if (this_gpu_name == None):
                for gpu_name in gpu_names:
                    if gpu_name.replace(' ','-') in detail_data_info[0].replace(' ','-'):
                        this_gpu_name = gpu_name
                        break
    if (this_gpu_name == None):
        return None
    else:
        index = gpu_names.index(this_gpu_name)
        result = {
            'GPU VRAM' : gpu_infos.iloc[index]['VRAM'],
            'GPU Name' : gpu_infos.iloc[index]['Name']
        }
        return result
def psu_process_function(detail_data_infos,data_infos,filename):
    def extract_psu(input_str : str):
        input_str = input_str.upper()
        psu_match = re.search(r'\b\d+\s*W\b',input_str)
        if psu_match:
            ram_result = psu_match.group()
            return ram_result
        else:
            return None
    search_str = '' # filename
    for data_info in data_infos:
        search_str += ' ' + data_info
    if (detail_data_infos != None):
        for detail_data_info in detail_data_infos:
            search_str += ' '+ detail_data_info[0]

    psu = extract_psu(search_str)
    return {
        'PSU' : psu
    }
def ram_process_function(detail_data_infos,data_infos,filename):
    blacklist = [
        '1050','1060','1070','1080','1090',
        '2050','2060','2070','2080','2090',
        '3050','3060','3070','3080','3090',
        '4050','4060','4070','4080','4090'
    ]
    def extract_ram(input_str : str):
        input_str = input_str.upper()
        possible = [
            '4','8','12','16','20','24','32','48','64','128'
        ]
        for i in range(len(possible)-1,-1,-1):
            num = possible[i]
            ram_match = re.search(r'\b{}\s*GB\b'.format(num),input_str,re.IGNORECASE)
            if ram_match:
                ram_result = ram_match.group()
                if ('Tối đa lên tới {}'.format(ram_result).upper() not in input_str
                    and 'Up to {}'.format(ram_result).upper() not in input_str):
                    return ram_result
            else:
                continue
        return None
    def extract_ddr(input_str : str):
        input_str = input_str.upper()
        possible = [
            '2','3','4','5','6'
        ]
        for i in range(len(possible)-1,-1,-1):
            num = possible[i]
            ram_match = re.search(r'\bDDR{}\b'.format(num),input_str,re.IGNORECASE)
            if ram_match:
                ram_result = ram_match.group()
                return ram_result
            else:
                continue
        return None
    search_target = ['DDR','RAM']
    ram_amount_filename = extract_ram(filename)
    search_str = ''
    for data_info in data_infos:
        if simple_search(data_info,search_target) and not simple_search(data_info,blacklist):
            search_str += ' ' + data_info
    if (detail_data_infos != None):
        for detail_data_info in detail_data_infos:
            if simple_search(detail_data_info[0],search_target) and not simple_search(detail_data_info[0],blacklist):
                search_str += ' '+ detail_data_info[0]
    ram_amount = extract_ram(search_str)
    ddr_type = extract_ddr(search_str)
    if (ram_amount == None and ram_amount_filename != None):
        ram_amount = ram_amount_filename
    elif (ram_amount != None and ram_amount_filename != None):
        # if (extract_number(ram_amount) > extract_number(ram_amount_filename)):
            ram_amount = ram_amount_filename

    return {
        'RAM' : ram_amount,
        'Memory Type' : ddr_type
    }
def storage_process_function(detail_data_infos,data_infos,filename):
    def extract_storage(input_str : str):
        input_str = input_str.upper()
        possible_g = [
            '120','128','250','256','500','512','1000','1024','2000','2048','3000','3096','4000','4096'
        ]
        for i in range(len(possible_g)-1,-1,-1):
            num = possible_g[i]
            storage_match = re.search(r'\b{}\s*GB\b'.format(num),input_str,re.IGNORECASE)
            if storage_match:
                ram_result = storage_match.group()
                return ram_result
            else:
                continue
        possible_t = [
            '1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20'
        ]
        for i in range(len(possible_t)-1,-1,-1):
            num = possible_t[i]
            storage_match = re.search(r'\b{}\s*TB\b'.format(num),input_str,re.IGNORECASE)
            if storage_match:
                ram_result = storage_match.group()
                return ram_result
            else:
                continue
        return None
    def extract_type(input_str : str):
        input_str = input_str.upper()
        possible = [
            'SSD','HDD'
        ]
        for i in range(len(possible)-1,-1,-1):
            num = possible[i]
            if (num.upper() in input_str):
                return num
        return None
    ram_amount_filename = extract_storage(filename)
    search_str = ''
    for data_info in data_infos:
        search_str += ' ' + data_info
    if (detail_data_infos != None):
        for detail_data_info in detail_data_infos:
            search_str += ' '+ detail_data_info[0]
    storage_amount = extract_storage(search_str)
    storage_type = extract_type(search_str)
    if (storage_amount == None and ram_amount_filename != None):
        storage_amount = ram_amount_filename
    elif (storage_amount != None and ram_amount_filename != None):
        # if (extract_number(ram_amount) > extract_number(ram_amount_filename)):
            storage_amount = ram_amount_filename

    return {
        'Storage' : storage_amount,
        'Storage Type' : storage_type
    }
def cooler_process_function(detail_data_infos,data_infos,filename):
    def extract_type(input_str : str):
        input_str = input_str.upper()
        possible = list(mapping.keys())
        for i in range(len(possible)-1,0,-1):
            num = possible[i]
            if (num.upper() in input_str):
                return num
        return None
    mapping = {
        None : 'Fan',
        'Liquid' : 'Liquid',
        'Fan' : 'Fan',
        'Nước' : 'Liquid',
        'Khí' : 'Fan'
    }
    search_str = ''
    for data_info in data_infos:
        search_str += ' ' + data_info
    if (detail_data_infos != None):
        for detail_data_info in detail_data_infos:
            search_str += ' '+ detail_data_info[0]
    cooler_type = extract_type(search_str)

    return {
        'Cooler' : mapping[cooler_type]
    }
def os_process_function(detail_data_infos,data_infos,filename):
    def extract_type(input_str : str):
        input_str = input_str.upper()
        possible =list(mapping.keys())
        for i in range(len(possible)-1,0,-1):
            num = possible[i]
            if (num.upper() in input_str):
                return num
        return None
    mapping = {
        None : 0,
        'Windows 11' : 11,
        'Windows 10' : 10
    }
    search_str = ''
    for data_info in data_infos:
        search_str += ' ' + data_info
    if (detail_data_infos != None):
        for detail_data_info in detail_data_infos:
            search_str += ' '+ detail_data_info[0]
    os_type = extract_type(search_str)
    return {
        'OS' : mapping[os_type]
    }
    
def pass_function(detail_info,info):
    return detail_info + ' ' + info
def info_format(raw_detail_data_infos,raw_data_infos,result_category):
    mapping = {
        # 'RAM' : {
        #     'Search' : [' DDR','PCIe','NVMe','RAM'],
        #     'Function' : pass_function
        # },
        'Main' : {
            'Search' : ['Mainboard','Bo mạch chủ','Main'],
            'Function' : pass_function
        },
        'Storage' : {
            'Search' : ['SSD','HDD','Ổ cứng'],
            'Function' : pass_function
        },
        'GPU' : {
            'Search' : ['GPU','Card màn hình','RTX','Card','VGA'],
            'Function' : pass_function
        },
        'PSU' : {
            'Search' : ['PSU','Nguồn'],
            'Function' : pass_function
        },
        'Case' : {
            'Search' : ['Case'],
            'Function' : pass_function
        },
        'Cooler' : {
            'Search' : ['Fan','Tản nhiệt'],
            'Function' : pass_function
        }
    }
    result = {}
    for category in result_category:
        have_detail_info_flag = False
        for raw_data_info in raw_data_infos:
            if simple_search(raw_data_info,mapping[category]['Search']):
                found_raw_detail_data_info = ['',0,0]
                if raw_detail_data_infos != None:
                    for raw_detail_data_info in raw_detail_data_infos:
                        if simple_search(raw_detail_data_info[0],mapping[category]['Search']):
                            found_raw_detail_data_info = raw_data_info
                            break
                process_function = mapping[category]['Function']
                if (category+' Name' not in result):
                    result[category+' Name'] = process_function(raw_data_info,found_raw_detail_data_info[0])
                    # try:
                    #     result[category+' Amount'] = int(found_raw_detail_data_info[1]) if found_raw_detail_data_info != None and found_raw_detail_data_info[1] != None else 0
                    #     result[category+' Warranty'] = int(found_raw_detail_data_info[2]) if found_raw_detail_data_info != None and found_raw_detail_data_info[2] != None else 0
                    # except:
                    #     pass
                else:
                    result[category+' Name'] += process_function(raw_data_info,found_raw_detail_data_info[0])
                    # result[category+' Amount'] += min(int(found_raw_detail_data_info[1]),result[category+' Amount'])
                    # result[category+' Warranty'] += min(int(found_raw_detail_data_info[2]),result[category+' Warranty'])
                have_detail_info_flag = True
                
        if (have_detail_info_flag == False):
            result[category+' Name'] = ''
            result[category+' Amount'] = 0
            result[category+' Warranty'] = 0
    return result