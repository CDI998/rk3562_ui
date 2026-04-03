# -*- coding: utf-8 -*-
"""
路径处理工具类（静态类版）
特点：无需实例化，直接通过类名调用方法，不存储任何实例数据
功能：兼容打包/非打包环境，生成正确的文件/文件夹绝对路径
"""
import sys
import os

class PathUtils:
    """路径处理静态工具类（无需实例化）"""

    @staticmethod
    def get_app_root_dir() -> str:
        """
        获取程序根目录（静态方法）返回绝对路径
        兼容场景：
        1. 打包为可执行文件（exe）→ 返回exe所在目录
        2. 源码运行（py文件）→ 返回当前工具文件所在目录
        :return: 程序根目录绝对路径 / 失败返回空字符串
        """
        try:
            if getattr(sys, 'frozen', False):
                # 打包环境：sys.executable 指向exe文件
                root_dir = os.path.dirname(sys.executable)
            else:
                # 源码环境：__file__ 指向当前工具文件
                root_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 路径标准化（处理跨系统分隔符、多余斜杠）
            root_dir = os.path.normpath(root_dir)
            return root_dir
        except Exception as e:
            print(f" [PathUtils] 获取程序根目录失败：{str(e)}")
            return ""

    @staticmethod
    def get_absolute_path(input_name: str) -> str:
        """
        生成目标文件/文件夹的绝对路径（静态方法）
        :param input_name（相对路径）: 输入值（支持3种格式）：
                           1. 仅文件夹名（如"pics"）
                           2. 仅文件名（如"1.png"）
                           3. 文件夹+文件名（如"pics/1.png" 或 "pics\\1.png"）
        :return: 绝对路径 / 输入无效返回空字符串
        """
        # 1. 输入校验
        if not input_name or input_name.strip() == "":
            print(" [PathUtils] 输入名称为空，无法生成路径")
            return ""
        
        # 2. 获取程序根目录
        app_root = PathUtils.get_app_root_dir()
        if not app_root:
            return ""
        
        # 3. 拼接并标准化路径
        target_path = os.path.join(app_root, input_name.strip())
        target_path = os.path.normpath(target_path)
        
        return target_path

    @staticmethod
    def get_file_path(folder_name: str, file_name: str) -> str:
        """
        便捷方法：生成指定文件夹下文件的绝对路径（静态方法）
        :param folder_name: 文件夹名称（如"pics"）
        :param file_name: 文件名（如"1.png"）
        :return: 文件绝对路径 / 输入无效返回空字符串
        """
        if not folder_name or not file_name:
            print(" [PathUtils] 文件夹名/文件名不能为空")
            return ""
        
        # 拼接文件夹和文件名，调用核心方法
        combo_name = os.path.join(folder_name, file_name)
        return PathUtils.get_absolute_path(combo_name)

    @staticmethod
    def check_path_exists(path: str) -> bool:
        """
        检查路径是否存在（静态方法）
        :param path: 待检查的路径
        :return: 存在返回True，不存在/路径为空返回False
        """
        if not path:
            return False
        return os.path.exists(path)
    
    @staticmethod
    def get_files_by_type(abs_folder_path: str, file_type: str) -> list:
        """
        静态方法：获取指定绝对路径文件夹下指定类型的所有文件名称（仅返回文件名，不含路径）
        注意：输入的文件夹路径必须是绝对路径
        :param abs_folder_path: 文件夹绝对路径（如 "D:/test/pics"、"/home/user/pics"）
        :param file_type: 文件类型（不带点，如 "png"、"jpg"、"txt"，大小写均可）
        :return: 符合条件的文件名称列表（空列表=路径无效/无对应文件/参数错误）
        """
        # 1. 基础参数校验
        if not abs_folder_path or not file_type:
            print(f" [PathUtils] 参数错误：文件夹绝对路径={abs_folder_path}，文件类型={file_type}")
            return []
        
        # 2. 校验绝对路径合法性（核心优化：直接校验输入的绝对路径）
        # 标准化路径（处理跨系统分隔符、多余斜杠）
        abs_folder_path = os.path.normpath(abs_folder_path)
        if not os.path.isabs(abs_folder_path):
            print(f" [PathUtils] 输入路径不是绝对路径：{abs_folder_path}")
            return []
        if not os.path.exists(abs_folder_path):
            print(f" [PathUtils] 绝对路径不存在：{abs_folder_path}")
            return []
        if not os.path.isdir(abs_folder_path):
            print(f" [PathUtils] 绝对路径不是文件夹：{abs_folder_path}")
            return []
        
        # 3. 遍历筛选指定类型文件（兼容大小写）
        file_type_lower = file_type.strip().lower()
        file_names = []
        try:
            for file_name in os.listdir(abs_folder_path):
                # 排除文件夹，仅处理文件
                file_full_path = os.path.join(abs_folder_path, file_name)
                if os.path.isfile(file_full_path):
                    # 获取文件后缀（不带点，转小写）
                    suffix = os.path.splitext(file_name)[-1].lstrip('.').lower()
                    if suffix == file_type_lower:
                        file_names.append(file_name)
        except PermissionError:
            print(f" [PathUtils] 无权限访问绝对路径文件夹：{abs_folder_path}")
            return []
        except Exception as e:
            print(f" [PathUtils] 遍历绝对路径文件夹失败：{str(e)}")
            return []
        
        # 4. 返回结果（空列表=无对应文件）
        print(f" [PathUtils] 绝对路径{abs_folder_path}下找到{len(file_names)}个{file_type}类型文件")
        return file_names


# ========== 测试代码（直接运行该文件时执行） ==========
if __name__ == "__main__":
    print("=" * 60)
    print("PathUtils 静态工具类测试（无需实例化）")
    print("=" * 60)
    
    # 1. 获取程序根目录（直接类名调用）
    root_dir = PathUtils.get_app_root_dir()
    print(f"\n1. 程序根目录：{root_dir}")
    
    # 2. 生成文件夹路径
    folder_path = PathUtils.get_absolute_path("pics")
    print(f"\n2. 文件夹路径：{folder_path}")
    print(f"   路径是否存在：{PathUtils.check_path_exists(folder_path)}")
    
    # 3. 生成文件路径
    file_path = PathUtils.get_absolute_path("1.png")
    print(f"\n3. 文件路径：{file_path}")
    print(f"   路径是否存在：{PathUtils.check_path_exists(file_path)}")
    
    # 4. 生成文件夹+文件路径（便捷方法）
    combo_path = PathUtils.get_file_path("pics", "2.png")
    print(f"\n4. 文件夹+文件路径：{combo_path}")
    print(f"   路径是否存在：{PathUtils.check_path_exists(combo_path)}")