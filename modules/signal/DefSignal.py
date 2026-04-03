from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QImage
from ui.warn import WarnType

# 自定义信号源对象类型，一定要继承自 QObject
class DefSignals(QObject):  
    ShowWarnMsgSignal = Signal(WarnType, str)  # 告警类型、警告信息
    UserSwitchMedia = Signal(QLabel, bool)


class PhotoSignals(QObject):  
    ReshImgBinSgnals = Signal(str) # binhtml 图片转为bin的html(中速)

class MediaSignals(PhotoSignals):  
    CameRefrshSignal = Signal(QImage) # 新图片
    ReshLowProgressSignal = Signal(str, str) # 
    TxtSendStateSignal = Signal(bool)   # 发送开始、发送结束(中速)
    