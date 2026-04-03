import os
import shutil
from PyInstaller.__main__ import run

'''
注意：打包后时，pc会

'''

def copyfile(srcfile, dstpath, replace=False):
    """复制文件到指定文件夹
    @param srcfile: 原文件绝对路径
    @param dstpath: 目标文件夹
    @param replace: 如果目标文件夹已存在同名文件，是否覆盖
    """
    try:
        # 判断源文件是否存在
        assert os.path.isfile(srcfile), "源文件不存在"
        basename = os.path.basename(srcfile)
        fname = os.path.splitext(basename)[0]  # 不带后缀的文件名
        suffix = os.path.splitext(srcfile)[-1]
        # 判断目标文件夹是否存在
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建文件夹，可递归创建文件夹，可能创建失败
        # 判断目标文件夹是否存在
        assert os.path.exists(dstpath), "目标文件夹不存在"
        # 开始尝试复制文件到目标文件夹
        i = 0
        while True:
            i += 1
            add = '(%s)' % str(i) if i != 1 else ''
            dstfile = os.path.join(dstpath, fname + add + suffix)
            opened_dstfile = os.path.join(dstpath, '~$' + fname + add + suffix)  # 已打开文件
            # 判断目标文件夹是否存在该文件
            if not os.path.exists(dstfile):
                shutil.copy(srcfile, dstfile)  # 不存在则复制文件
                break
            # 存在该文件，则判断已存在文件是否打开
            if os.path.exists(opened_dstfile):
                # 已打开则创建下一个新文件
                continue
            # 已存在文件没有打开的情况
            if replace:
                shutil.copy(srcfile, dstfile)  # 复制文件
                break
            # 不覆盖已存在文件，则创建下一个新文件
        return dstfile
    except AssertionError as e:
        print('文件复制失败', e, srcfile)
    except Exception as e:
        print('文件复制失败', e, srcfile)
 
def copy_folder(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copy_folder(s, d)
        else:
            shutil.copy2(s, d)
 
def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
 

def create_directory(path):
    try:
        # 创建目录，如果目录已存在则不会抛出异常
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{path}' is ready.")
    except Exception as e:
        print(f"An error occurred: {e}")


# 使用函数清空文件夹
if __name__ == "__main__":
    Dest_folder = './AppPacket'
    # 指定素材库文件夹的路径
    SrcImgFolder = './resources'
    DestImgFolder = './AppPacket/resources'
    # 指定样式文件夹的路径
    SrcQssFolder = './styles/QSS'
    DestQssFolder = './AppPacket/styles/QSS'
    # 指定ui文件夹的路径
    SrcUiFile = './ui'
    DestUiDir = './AppPacket/ui'
    # 指定配置文件路劲
    SrcConfFolder = './tool/conftool/appconfig.conf'
    DestConfFolder = './AppPacket/'
    #指定日志文件夹
    DestLogFolder = './AppPacket/log'

    # 指定main.py的路径
    main_py_path = './main.py'
    #指定图标文件的路径
    icon_path = './resources/image/applogo_send.png'
    # # 指定QSS文件夹的路径，并添加为额外数据
    qss_folder = ('./styles/QSS', 'QSS')  # 第一个参数是源文件夹，第二个参数是目标文件夹（在打包后的程序中）
    output_folder = './AppPacket'  # 第一个参数是源文件夹，第二个参数是目标文件夹（在打包后的程序中）
    opts = [
        main_py_path,
        '--onefile',
        '--windowed',
        # '--icon={}'.format(icon_path),
        # '--add-data={};{}'.format(*qss_folder),  # 使用unpack_dir参数来指定目标文件夹
        '--name=VLC_Edu_App(Tx)',
        '--distpath={}'.format(output_folder),
        # 其他选项...
    ]

    print(os.getcwd())
    clear_folder(Dest_folder)
    copyfile(SrcConfFolder, DestConfFolder,True) # 更新配置文件
    create_directory(DestLogFolder)# 创建日志文件夹
    # copy_folder(SrcImgFolder, DestImgFolder) # 更新素材库
    # copy_folder(SrcQssFolder, DestQssFolder) # 更新qss库
    # copy_folder(SrcUiFile, DestUiDir) # 更新ui库
    print("文件更新操作完成，开始进行程序打包。")
    run(opts)





