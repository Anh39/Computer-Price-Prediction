import os

join = os.path.join
_project_path = os.getcwd()
crawler_data_path = join(_project_path,'Crawler_Data')

class config:
    lap_type = join(_project_path,'Cleaner','lap','type_config.json')

class output:
    path = join(_project_path,'Output')
    preprocessed_data = join(path,'preprocessed_data.csv')
    processed_data = join(path,'processed_data.csv')
    pre_intel_data = join(path,'pre_intel.csv')
    pre_amd_data = join(path,'pre_amd.csv')
    intel_data = join(path,'intel.csv')
    amd_data = join(path,'amd.csv')
    nvidia_gpu_data = join(path,'nvidia_gpu.csv')
    amd_gpu_data = join(path,'amd_gpu.csv')
class intel:
    path = join(crawler_data_path,'Intel_spec')
    i9 = join(path,'i9')
    i7 = join(path,'i7')
    i5 = join(path,'i5')
    i3 = join(path,'i3')
    series1 = join(path,'series1')
    ultra = join(path,'ultra')

class nvidia:
    path = join(crawler_data_path,'Nvidia')
    gpu = join(path,'gpu')
    gpu_result = join(gpu,'result.csv')

class amd:
    path = join(crawler_data_path,'Amd_spec')
    cpu = join(path,'cpu')
    cpu_result = join(cpu,'Processor Specifications.csv')
    gpu = join(path,'gpu')
    gpu_result = join(gpu,'Graphics Specifications.csv')

class hacom:
    path = join(crawler_data_path,'Hacom_spec')
    lap_common = join(path,'lap_common')
    lap_game = join(path,'lap_game')

class anphat:
    path = join(crawler_data_path,'Anphat_spec')
    lap_common = join(path,'lap_common')
    lap_game = join(path,'lap_game')
    
class fpt:
    path = join(crawler_data_path,'FPT_spec')
    lap = join(path,'lap')

class util:
    @classmethod
    def get_tree(self,folder_path : str):
        temp_result = set()
        self._recurse_get_file(temp_result,folder_path)
        result = {}
        for key in temp_result:
            result[os.path.normpath(self.to_relative(key,folder_path))] = key
        return result
    @classmethod
    def to_relative(self,path : str,relto : str):
        relpath = os.path.relpath(path,relto)
        return relpath
    @classmethod
    def _recurse_get_file(self,result : set,input_path : str):
        for file_name in os.listdir(input_path):
            file_path = join(input_path,file_name)
            if (os.path.isdir(file_path)):
                self._recurse_get_file(result,file_path)
            else:
                result.add(file_path)