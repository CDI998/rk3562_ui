from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QImage
from ui.warn import WarnType
from enum import Enum

class MediaType(Enum):
    Type_TXT = 1  # 媒体类型：文本
    Type_PIC = 2  # 媒体类型：图片
    Type_VDO = 3  # 媒体类型：视频

# 自定义信号源对象类型，一定要继承自 QObject
class DefSignals(QObject):  
    ShowWarnMsgSignal = Signal(WarnType, str)  # 告警类型、警告信息
    UserSwitchMedia   = Signal(QLabel, bool)

class MediaSignals(QObject):
    TransProgress      = Signal(MediaType, float, str)   # 传输进度信号, 传输类型，进度百分比（-1为异常），附加信息(异常信息等)
    CameRefrshSignal   = Signal(QImage) # 新图片
    LoadLocalPicSignal = Signal(QImage) # 新图片
    