import os
import subprocess
import shutil
import re

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

def convert_ui_to_py(ui_file_path, output_dir="."):
    # 获取 .ui 文件的基名，并添加 .py 扩展名作为输出文件名
    base_name = os.path.splitext(os.path.basename(ui_file_path))[0]
    output_file_path = os.path.join(output_dir, f"{base_name}.py")

    # 调用 pyuic5 将 .ui 文件转换为 .py 文件
    try:
        subprocess.run(["pyuic5", "-o", output_file_path, ui_file_path], check=True)
        # subprocess.run(["python", "-m", "PyQt5.uic.pyuic", "-o", output_file_path, ui_file_path], check=True)
        print(f"Converted {ui_file_path} to {output_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {ui_file_path}: {e}")

def convert_qrc_to_py(qrc_file_path, output_dir="."):
    # 获取 .qrc 文件的基名，并添加 _rc.py 扩展名作为输出文件名
    base_name = os.path.splitext(os.path.basename(qrc_file_path))[0]
    output_file_path = os.path.join(output_dir, f"{base_name}_rc.py")

    # 调用 pyrcc5 将 .qrc 文件转换为 .py 文件
    try:
        subprocess.run(["pyrcc5", "-o", output_file_path, qrc_file_path], check=True)
        print(f"Converted {qrc_file_path} to {output_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {qrc_file_path}: {e}")

def replace_last_line_with_string(file_path, new_string):
    # 读取文件的所有行
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 如果文件为空（没有行），则直接写入新字符串并返回
    if not lines:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_string)
        return

    # 替换最后一行为新字符串
    lines[-1] = new_string + '\n'  # 确保新字符串后有一个换行符，除非它已经是文件的最后一行且不需要额外的换行符

    # 将修改后的行写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def update_margin_in_py_file(file_path):
    # 读取原始文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # 使用正则表达式替换所有 margin-top:0px 为 margin-top:12px
    updated_content = re.sub(r'margin-top:\s*0px;', 'margin-top:12px;', content)
    # 将修改后的内容写回到文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    print(f"文件 '{file_path}' 中的 margin-top 已更新为 12px")

def update_html_in_file(file_path):
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # 定义要替换的 CSS 规则
    old_style = r'SimSun'
    new_style = r'Microsoft YaHei'
    # 替换旧的 CSS 规则
    updated_content = re.sub(old_style, new_style, content)
    # 将更新后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
ui_file_path = "./ui/home.ui"  # 替换为你的 .ui 文件路径
output_ui_file_path = "./ui"
qrc_file_path = "./resources/rs.qrc"  # 替换为你的 .qrc 文件路径
outputqrc_file_path = "./ui"

ui_py_file_path = output_ui_file_path + '/home.py'  # 替换为你的文件路径
ui_py_file_import = 'import ui.rs_rc'  # 替换为你想要的新字符串

convert_ui_to_py(ui_file_path, output_ui_file_path)
convert_qrc_to_py(qrc_file_path, outputqrc_file_path)
replace_last_line_with_string(ui_py_file_path, ui_py_file_import)
# 调用函数并传入文件路径
# update_margin_in_py_file(ui_py_file_path)
update_html_in_file(ui_py_file_path)

print("Done!")