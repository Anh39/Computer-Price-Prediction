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
def read_folders(folders : list):
    paths = {}
    result = []
    for folder in folders:
        paths.update(folder_path.util.get_tree(folder))
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
    df1['CPU Type'] = 'Intel'
    df2 = pd.read_csv(folder_path.output.amd_data)
    df2['CPU Type'] = 'AMD'
    result_df = pd.concat([df1,df2],ignore_index=True)
    return result_df
def get_gpu_info():
    df1 = pd.read_csv(folder_path.output.amd_gpu_data)
    df1['GPU Type'] = 'AMD'
    df2 = pd.read_csv(folder_path.output.nvidia_gpu_data)
    df2['GPU Type'] = 'NVIDIA'
    result_df = pd.concat([df1,df2],ignore_index=True)
    return result_df
cpu_infos = get_cpu_info()
gpu_infos = get_gpu_info()
cpu_names = cpu_infos['Name'].to_list()
gpu_names = gpu_infos['Name'].to_list()
def get_search_str(detail_data_infos,data_infos,filename : str = '',blacklist : list = []):
    search_str = filename
    for data_info in data_infos:
        if (not simple_search(data_info,blacklist)):
            search_str += ' ' + data_info
    if (detail_data_infos != None):
        for detail_data_info in detail_data_infos:
            if (not simple_search(detail_data_info[0],blacklist)):
                search_str += ' '+ detail_data_info[0]
    return search_str
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
        return {
            'CPU Lithography' :None,
            'CPU Name' : None,
            'CPU Series' : None,
            'CPU Core' : None,
            'CPU Thread' : None,
            'CPU Cache' : None,
            'Max DDR Support' : None,
            'CPU Base Clock' : None,
            'CPU Max Clock' : None,
            'IGPU Clock' : None ,
            'CPU Cache' : None,
            'Base Power' : None,
            'Max Power' : None,
            'CPU Intel' : None
        }
    else:
        index = cpu_names.index(this_cpu_name)
        result = {
            'CPU Lithography' : cpu_infos.iloc[index]['Achitecture'],
            'CPU Name' : cpu_infos.iloc[index]['Name'],
            'CPU Series' : cpu_infos.iloc[index]['Gen'],
            'CPU Core' : cpu_infos.iloc[index]['Total Cores'],
            'CPU Thread' : cpu_infos.iloc[index]['Total Threads'],
            'CPU Cache' : cpu_infos.iloc[index]['Total Cache'],
            'Max DDR Support' : cpu_infos.iloc[index]['Memory Type'],
            'CPU Base Clock' : cpu_infos.iloc[index]['Base Clock'],
            'CPU Max Clock' : cpu_infos.iloc[index]['Max Boost Clock'],
            'IGPU Clock' : cpu_infos.iloc[index]['IGPU Frequency'] ,
            'CPU Cache' :cpu_infos.iloc[index]['Total Cache'] ,
            'Base Power' : cpu_infos.iloc[index]['Base Power'] ,
            'Max Power' : cpu_infos.iloc[index]['Max Power'],
            'CPU Intel' : int(cpu_infos.iloc[index]['CPU Type'] == 'Intel')
        }
        return result
def gpu_process_function(detail_data_infos,data_infos,filename):
    this_gpu_name = None
    blacklist = ['620','520','530']
    for gpu_name in gpu_names:
        if gpu_name.replace(' ','-') in filename.replace(' ','-') and gpu_name.replace(' ','-') not in blacklist:
            this_gpu_name = gpu_name
            break 
    for data_info in data_infos:
        if (this_gpu_name == None):
            for gpu_name in gpu_names:
                if gpu_name.replace(' ','-') in data_info.replace(' ','-') and gpu_name.replace(' ','-') not in blacklist:
                    this_gpu_name = gpu_name
                    break
    if (detail_data_infos != None):
        for detail_data_info in detail_data_infos:
            if (this_gpu_name == None):
                for gpu_name in gpu_names:
                    if gpu_name.replace(' ','-') in detail_data_info[0].replace(' ','-') and gpu_name.replace(' ','-') not in blacklist:
                        this_gpu_name = gpu_name
                        break
    if (this_gpu_name == None):
        return {
            'GPU VRAM' : None,
            'GPU Name' : None,
            'GPU Onboard' : 1,
            'GPU AMD' : 0,
            'GPU NVIDIA' : 0 
        }
    else:
        index = gpu_names.index(this_gpu_name)
        result = {
            'GPU VRAM' : gpu_infos.iloc[index]['VRAM'],
            'GPU Name' : gpu_infos.iloc[index]['Name'],
            'GPU Onboard' : 0,
            'GPU AMD' : int(gpu_infos.iloc[index]['GPU Type'] == 'AMD'),
            'GPU NVIDIA' : int(gpu_infos.iloc[index]['GPU Type'] == 'NVIDIA')
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
    search_str = get_search_str(detail_data_infos,data_infos)

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
            ram_match = re.search(r'\s{}\s*GB'.format(num),input_str,re.IGNORECASE)
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
            ram_match = re.search(r'\sDDR{}'.format(num),input_str,re.IGNORECASE)
            if ram_match:
                ram_result = ram_match.group()
                return ram_result
            else:
                continue
        for i in range(len(possible)-1,-1,-1):
            num = possible[i]
            ram_match = re.search(r'\sLPDDR{}'.format(num),input_str,re.IGNORECASE)
            if ram_match:
                ram_result = ram_match.group()
                return ram_result
            else:
                continue
        return None
    search_target = ['DDR','RAM']
    ram_amount_filename = extract_ram(filename)
    search_str = get_search_str(detail_data_infos,data_infos,blacklist=blacklist)
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
        for i in range(len(possible)):
            num = possible[i]
            if (num.upper() in input_str):
                return num
        return None
    ram_amount_filename = extract_storage(filename)
    search_str = get_search_str(detail_data_infos,data_infos,filename)
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
def display_process_function(detail_data_infos,data_infos,filename):
    search_str = get_search_str(detail_data_infos,data_infos,filename)
    def extract_type(input_str : str):
        input_str = input_str.upper()
        possible = [
            'IPS','LCD','OLED','LED'
        ]
        for i in range(len(possible)):
            num = possible[i]
            if (num.upper() in input_str):
                return num
        return None
    def extract_size(input_str : str):
        input_str = input_str.upper()
        possible = [
            'inch(?!e)','"'
        ]
        for i in range(len(possible)):
            scale = possible[i]
            storage_match = re.search(r'\b\d\d[.]?\d?[\s-]?{}'.format(scale),input_str,re.IGNORECASE)
            if storage_match:
                ram_result = storage_match.group()
                return ram_result
            else:
                continue
        storage_match = re.search(r'\b\d\d[.]\d',input_str,re.IGNORECASE)
        if storage_match:
            ram_result = storage_match.group()
            return ram_result
        return None
    def extract_resolution(input_str : str):
        input_str = input_str.upper()
        storage_match = re.search(r'\b\d\d\d\d\s?[xX]\s?\d\d\d\d',input_str,re.IGNORECASE)
        if storage_match:
            ram_result = storage_match.group()
            return ram_result
        
        possible = [
            'WQXGA',
            'QHD',
            'FHD'
        ]
        mapping = {
            'WQXGA' : '2560x1600',
            'QHD' : '2560x1440',
            'FHD' : '1920x1080'
        }
        for i in range(len(possible)):
            if possible[i].upper() in search_str:
                return mapping[possible[i]]
        return None
    def extract_frequency(input_str : str):
        input_str = input_str.upper()
        storage_match = re.search(r'\b\d\d\d?[Hh][Zz]',input_str,re.IGNORECASE)
        if storage_match:
            ram_result = storage_match.group()
            return ram_result
    def extract_color(input_str : str):
        input_str = input_str.upper()
        possible = [
            'DCI-P3','RGB','sRGB','SRGB','NTSC'
        ]
        for i in range(len(possible)):
            scale = possible[i]
            storage_match = re.search(r'[\s,]\d\d\d?%[\s:-]?{}'.format(scale),input_str,re.IGNORECASE)
            if storage_match:
                ram_result = storage_match.group()
                return ram_result
            else:
                continue
        possible = [
            'sRGB','DCI-P3'
        ]
        for i in range(len(possible)):
            scale = possible[i]
            storage_match = re.search(r'[\s,]{}[\s:-]?\d\d\d?%'.format(scale),input_str,re.IGNORECASE)
            if storage_match:
                ram_result = storage_match.group()
                return ram_result
            else:
                continue
    display_type = extract_type(search_str)
    display_size = extract_size(search_str)
    display_resolution = extract_resolution(search_str)
    display_frequency = extract_frequency(search_str)
    display_color = extract_color(search_str)
    return {
        'Display Type' : display_type,
        'Display Size' : display_size,
        'Display Resolution' : display_resolution,
        'Display Frequency' : display_frequency,
        'Display Color' : display_color
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
    search_str = get_search_str(detail_data_infos,data_infos)
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