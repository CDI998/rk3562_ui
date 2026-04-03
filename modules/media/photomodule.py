from tool.globals.bintool import bintool
from threading import Thread
from tool.globals.queuetool import qeuetool, MsduQueCmd
from tool.packtool.packer import MsduMode
import time
import queue
from modules.datamodule.midbean import MidDataBean, BlockSendState
from PyQt5.QtCore import pyqtSignal as Signal
from modules.globals.msdu import MsduMsgDataType
from modules.signal.DefSignal import PhotoSignals
import threading
from tool.globals.pathutils import PathUtils

class photoModule():
    def __init__(self, LocalPicPath):
        self.databean = MidDataBean()
        self.LocalPicPath = PathUtils.get_absolute_path(LocalPicPath)
        self.LoadLocalMsg()

    def LoadLocalMsg(self):
        if PathUtils.check_path_exists(self.LocalPicPath):
            print("本地图片路径有效")
            piles = PathUtils.get_files_by_type(self.LocalPicPath, "png") 
            print(f"本地图片列表: {piles}")
            self.databean.SetLocalPicNameList(piles)
        else:
            print(f"本地图片路径无效: {self.LocalPicPath}")

    def switchLocalPic(self, IsUpOption: bool = True) -> str:
        """
        切换本地图片，返回完整的图片路径
        :param IsUpOption: True=切换下一张，False=切换上一张
        :return: 完整的图片路径（str）/路径无效返回空字符串
        """
        # 1. 获取当前图片名称和目标文件名
        curr_name = self.databean.GetCurrLocalPicName()
        if IsUpOption:
            print(f"当前图片: {curr_name} → 切换到下一张图片")
            new_name = self.databean.get_next_pic_name(curr_name)
            print(f"切换到下一张图片: {new_name}")
        else:
            print(f"当前图片: {curr_name} → 切换到上一张图片")  
            new_name = self.databean.get_prev_pic_name(curr_name)
            print(f"切换到上一张图片: {new_name}")

        # 2. 校验文件名有效性
        if not new_name:  # 空字符串（列表为空）
            return ""
        new_path = PathUtils.get_absolute_path(self.LocalPicPath+'/'+new_name)
        if PathUtils.check_path_exists(new_path):
            self.databean.SetCurrLocalPicName(new_name)  # 更新当前图片名称
            return new_path
        else:
            print(f"图片路径无效: {new_path}")
            return ""







                