import configparser
import os
import sys
import ast

class Config:
    def __init__(self):
        self.ConfigData = {}
        try:
            self.config = configparser.ConfigParser()
            self.config.optionxform = str # 禁止大小写转换
            # file_root = os.path.dirname(__file__)
            # path = os.path.join(file_root, 'appconfig.conf')
            file_path = self.get_resource_path('appconfig.conf')
            print("file_path", file_path)
            # 使用'utf-8'编码读取配置文件内容
            with open(file_path, 'r', encoding='utf-8') as configfile:
                self.config.read_string(configfile.read())
        except Exception as e:
            print(e)

    def get_executable_directory(self):
        if getattr(sys, 'frozen', False):
            # 应用程序是打包后的可执行文件
            application_path = os.path.dirname(sys.executable)
        else:
            # 应用程序是在解释器中运行的
            application_path = os.path.dirname(os.path.abspath(__file__))
        return application_path

    # 获取可执行文件同级目录下的文件路径
    def get_resource_path(self,relative_path):
        base_path = self.get_executable_directory()
        return os.path.join(base_path, relative_path)

    def getint(self, section, key):
        if self.config is None:
            return None
        if self.config.has_option(section, key):
            conf_str = self.config.get(section, key)
            conf_int = int(conf_str)
            print(section, key, conf_int)
            return conf_int
        else:
            return None
    
    def getstr(self, section, key):
        if self.config is None:
            return None
        if self.config.has_option(section, key):
            conf_str = self.config.get(section, key)
            print(section, key, conf_str)
            return conf_str
        else:
            return None
    
    def gettuple(self, section, key):
        if self.config is None:
            return None
        if self.config.has_option(section, key):
            conf_str = self.config.get(section, key)
            conf_tuple = ast.literal_eval(conf_str)
            print(section, key, conf_tuple)
            return conf_tuple
        else:
            return None
    
    def getbool(self, section, key):
        if self.config is None:
            return None
        if self.config.has_option(section, key):
            conf_bool = self.config.getboolean(section, key)
            print(section, key, conf_bool)
            return conf_bool
        else:
            return None
    
    def LoadAllItem(self)->dict:
        # 遍历所有sections
        for section in self.config.sections():
            # 遍历每个section中的所有键值对
            for key in self.config[section]:
                self.ConfigData[key] = self.config[section][key]
        # 输出字典内容
        for key, value in self.ConfigData.items():
            print(f'{key}: {value}')
        return self.ConfigData

    def GetItem(self, key:str)->str:
        if self.ConfigData.get(key) is not None:
            return self.ConfigData[key]
        else:
            print(key,'is not in the appconfig.conf')
            return None
        
    
    def SetItemInt(self, section: str, key: str, value: int):
        """设置int类型的值，如果该项不存在则添加"""
        if self.config is None:
            print("SetItemInt:config is None")
            return None
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))  # 将int转换为str存储
        self.ConfigData[key] = str(value)  # 同样更新到ConfigData字典中
        # 将修改保存到配置文件中
        file_path = self.get_resource_path('appconfig.conf')
        with open(file_path, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

if __name__ == '__main__':
    cfig = Config()
    cfig.LoadAllItem()
    cfig.SetItemInt('camera', 'id', 1)
    cfig.LoadAllItem()



