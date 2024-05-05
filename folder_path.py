import os

join = os.path.join
_project_path = os.getcwd()

class output:
    path = join(_project_path,'Output')
    processed_data = join(path,'processed_data.csv')

class intel:
    path = join(_project_path,'Intel_spec')
    i9 = join(path,'i9')
    i7 = join(path,'i7')
    i5 = join(path,'i5')
    i3 = join(path,'i3')
    series1 = join(path,'series1')
        
class hacom:
    path = join(_project_path,'Hacom_spec')
    pc_game = join(path,'pc_game')
    pc_graphic = join(path,'pc_graphic')
    pc_office = join(path,'pc_office')
        
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