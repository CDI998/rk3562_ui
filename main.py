
import os
import sys
import time
import queue
import re
from enum import Enum

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

from PyQt5 import QtGui
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtGui import QPainter, QPainterPath
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QCursor

from PyQt5 import QtCore 
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QRectF

from ui.home import Ui_MainWindow
from ui.winctrl import WinCtrlMenu 
from ui.setwind import SettingDialog
from ui.warn import *

from modules.globals.systemmanage import SystemManager, SystemState
from modules.media.mediamodule import MediaModule
from modules.signal.DefSignal import *
from modules.globals.msdu import MsduModule
from modules.globals.UserActionManage import *

from tool.packtool.packer import *
from tool.conftool.config import *
from tool.globals.log import log
from tool.globals.queuetool import *
from tool.globals.font import *
from tool.globals.pathutils import PathUtils

from PIL import Image
import numpy as np

from ui.progress import Progress
from modules.signal.DefSignal import MediaType

# def handle_exception(exc_type, exc_value, exc_traceback):
#     # 全局异常处理程序，将异常写入日志文件
#     print("Unhandled exception:", file=sys.stderr)
#     sys.__excepthook__(exc_type, exc_value, exc_traceback)

import sys
import threading
import traceback
import faulthandler

# 捕获底层崩溃（如扩展库、段错误等）
faulthandler.enable()

# 捕获主线程未处理异常
def handle_exception(exc_type, exc_value, exc_traceback):
    print("程序发生未捕获异常：")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

# 捕获子线程未处理异常
def thread_exception_handler(args):
    print(f"线程 {args.thread.name} 发生未捕获异常：")
    traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)

sys.excepthook = handle_exception
threading.excepthook = thread_exception_handler


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, WinIconFilePath:str, WinTitle:str):
        super().__init__()
        self.setupUi(self)
        self.WinIconFilePath = WinIconFilePath
        self.WinTitle = WinTitle
        self.Version = "v2.1.3(Tx_A)"
        
        self.Items_Def = {} # 系统通用组件集合，key为组件名，value为组件对象
        self.Pages_Def = {} # 系统页面组件集合，key为页面名，value为页面组件对象
        self.Items_txtmode = {} # 低速文本模式组件集合，key为组件名，value为组件对象
        self.Items_picmode = {} # 中速图片模式组件集合，key为组件名，value为组件对象
        self.Items_vdomode = {} # 高速视频模式组件集合，key为组件名，value为组件对象
        
        self.slide_threshold = 30  # 滑动切换的最小像素距离
        self.slide_start_y = 0     # 记录滑动起点的Y坐标
        self.current_widget = None # 记录当前滑动的组件名（如step1pic/step1vdo）
        
        self.keyboards = {
            '数字': ['1','2','3','4','5','6','7','8'],
            '字母': [chr(c) for c in range(ord('A'), ord('Z')+1)],  # A-Z自动生成
            '功能键': ['DEL', 'SEND']
        }

        # 获取本地配置
        self.conf = Config()
        self.TxtInputMaxLen = self.conf.getint("text", "InputMaxLen")
        self.LocalPicPath   = self.conf.getstr("picture", "LocalPath")
        self.LocalVdoPath   = self.conf.getstr("video", "LocalPath")

        # 日志模块初始化
        self.mylog = log(audiocleanlog = self.conf.getbool("Log", "AutoClean"), 
                         logmax = self.conf.getint("Log", "LogFileMax"))
        self.mylog.LogRun()
        
        self.UserAction   = UserActionManage()

        self.DefSgnals    = DefSignals()
        self.MediaSignals = MediaSignals()
        self.MsduRxQueue  = queue.Queue(maxsize=10)
        self.MsduTxQueue  = queue.Queue(maxsize=10)
        
        self.SysManage = SystemManager(SystemState.TXT_MODE)
        self.media     = MediaModule(
                                     localpicpath=self.LocalPicPath,  # 初始化本地图片路径
                                     localvdopath=self.LocalVdoPath,  # 初始化本地视频路径
                                     MediaSignals=self.MediaSignals,  # 传入信号对象，main与media通信信号
                                     MsduRxQueue=self.MsduRxQueue,    # 传入接收队列，media接收msdu的数据
                                     MsduTxQueue=self.MsduTxQueue     # 传入发送队列，media发送数据给msdu
                                     )
        self.msdu = MsduModule(MsduRxQueue=self.MsduRxQueue, MsduTxQueue=self.MsduTxQueue)

        self.uiinit()
        self.modeinit()
        systemfont.set_font_for_all_widgets(self,"微软雅黑")   
        self.remove_all_frame_borders()
        # self.showFullScreen() 
        self.media.Start()
        self.msdu.Start()
  
        
    def uiinit(self):
        """
        初始化UI组件，包括按钮、文本框、页面、定时器等的绑定和界面属性设置。
        主要负责界面元素的组织和初始状态设定。
        """
        # 1.0 通用按键和显示组件
        self.Items_Def['close_btn_test'] = self.closebtn
        self.Items_Def['warnframe'] = self.warnframe 
        self.Items_Def['txtmode']   = self.txtmodebtn
        self.Items_Def['vdomode']   = self.vdomodebtn
        self.Items_Def['picmode']   = self.picmodebtn

        # 2.0 文本传输模式的按键和显示组件
        self.Items_txtmode['progress']    = self.txtprogress
        self.Items_txtmode['progresstip'] = self.txtprogresstip
        self.Items_txtmode['inputedit']   = self.inputedit
        for group, keys in self.keyboards.items():
            for key in keys:   
                btn_key = f'KB_{key}'       # 如 KB_1、KB_A、KB_DEL
                attr_name = f'kb_{key.lower()}'  # 如 kb_1、kb_a、kb_del
                # 通过对象属性名获取按键对象（核心：利用反射简化代码）
                self.Items_txtmode[btn_key] = getattr(self, attr_name)

        # 3.0 图片传输模式的按键和显示组件
        self.Items_picmode['progress']    = self.picprogress # 图片传输进度条
        self.Items_picmode['progresstip'] = self.picprogresstip # 进度条数值显示标签
        self.Items_picmode['localpic']    = self.localpic # 本地图片显示区域qlabel
        self.Items_picmode['camframe']    = self.piccamframe # 容纳cam的窗口
        self.Items_picmode['cam']         = self.piccam      # 显示cam的qlabel
        self.Items_picmode['tookphoto']   = self.tookphoto # 拍照按钮
        self.Items_picmode['sendpic']     = self.sendpic  # 发送按钮
        
        # 4.0 视频传输模式的按键和显示组件
        self.Items_vdomode['progress']    = self.vdoprogress # 视频传输进度条
        self.Items_vdomode['progresstip'] = self.vdoprogresstip # 进度条数值显示标签
        self.Items_vdomode['localvdo']    = self.localvdo # 本地视频显示区域qlabel
        self.Items_vdomode['camframe']    = self.vdocamframe # 容纳cam的窗口
        self.Items_vdomode['cam']         = self.vdocam # 显示cam的qlabel
        self.Items_vdomode['record']      = self.record # 录像按钮
        self.Items_vdomode['sendvdo']     = self.sendvdo # 发送按钮

        # 5.0 系统页面组件
        self.Pages_Def['homepage'] = self.modepage
        self.Pages_Def['txtpage']  = self.txtpage
        self.Pages_Def['picpage']  = self.picpage
        self.Pages_Def['vdopage']  = self.vdopage
       
        # 6.0 组件初始化
         # 初始化进度条和提示标签
        Progress.init(self.Items_txtmode['progress'], self.Items_txtmode['progresstip'])
        Progress.init(self.Items_picmode['progress'], self.Items_picmode['progresstip']) 
        Progress.init(self.Items_vdomode['progress'], self.Items_vdomode['progresstip']) 
         # 初始化信息警告标签
        self.Items_Def['WarnLabel'] = WarnLabel("Initial Text", self.Items_Def['warnframe'])
        self.Items_Def['WarnLabel'].setObjectName("WarnLabel")  # 设置 QLabel 的名字
        self.Items_Def['WarnLabel'].setGeometry(11, 6, 186, 50)  # 设置 QLabel 的位置和大小
        self.Items_Def['WarnLabel'].setFontSize(15)
        
        self.SwitHomePage(SystemState.TXT_MODE)
        self.setWindowIcon(QIcon(self.WinIconFilePath))
        self.setWindowTitle(self.WinTitle)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 设置为无边框
           
    def modeinit(self):
        self.Items_Def['close_btn_test'].clicked.connect(self.close) # 关闭按钮,测试用
        # 初始化模式
        self.Items_Def['txtmode'].clicked.connect(self.trigtxtmode) 
        self.Items_Def['picmode'].clicked.connect(self.trigpicmode) 
        self.Items_Def['vdomode'].clicked.connect(self.trigvdomode) 

        self.Items_picmode['tookphoto'].clicked.connect(self.TookPhoto) 
        self.Items_picmode['sendpic'].clicked.connect(self.SendPhoto) 

        # 2. 低速按键
        for group, keys in self.keyboards.items():
            for key in keys:   
                btn_key = f'KB_{key}'       # 如 KB_1、KB_A、KB_DEL
                # 通过对象属性名获取按键对象（核心：利用反射简化代码）
                if key == 'DEL':
                    self.Items_txtmode[btn_key].clicked.connect(self.on_keyboard_click_del)
                elif key == 'SEND':
                    self.Items_txtmode[btn_key].clicked.connect(self.on_keyboard_click_send)
                else:
                    self.Items_txtmode[btn_key].clicked.connect(lambda checked, txt=key: self.on_keyboard_click_data(txt))

        # 上下滑动预览本地图片
        self.Items_picmode['localpic'].mousePressEvent = lambda e: self.on_widget_press(e, 'localpic')
        self.Items_picmode['localpic'].mouseReleaseEvent = self.on_widget_release
        
        # 上下滑动预览本地视频
        self.Items_vdomode['localvdo'].mousePressEvent = lambda e: self.on_widget_press(e, 'localvdo')
        self.Items_vdomode['localvdo'].mouseReleaseEvent = self.on_widget_release

        self.MediaSignals.TransProgress.connect(self.on_media_trans_progress)
        self.MediaSignals.CameRefrshSignal.connect(self.CameRefrsh)
        self.DefSgnals.ShowWarnMsgSignal.connect(self.ShowWarnMsg)


    def remove_all_frame_borders(self):
        """移除所有QFrame组件的边框，使界面更简洁。RK芯片必须步骤"""
        for frame in self.findChildren(QFrame):
            frame.setFrameShape(QFrame.NoFrame)
            frame.setFrameShadow(QFrame.Plain)
    '''
        ##########################################################
        ##########################################################
        槽函数实现区域
        start
        ##########################################################
        ##########################################################
    '''
#############################################################################################
################################## 1. 通用核心功能函数实现 start #############################
#############################################################################################
    def closeEvent(self, event):
        print("close_window")
        self.media.Stop()
        self.msdu.Stop()
        time.sleep(0.4)
        self.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)
    
    # ========== 通用滑动按下事件（记录组件和起点） ==========
    def on_widget_press(self, event, widget_name):
        if event.button() == Qt.LeftButton:
            self.current_widget = widget_name  # 记录当前滑动的组件名
            self.slide_start_y = event.y()     # 记录Y轴起点

    # ========== 通用滑动释放事件（判断方向，调用共用槽函数） ==========
    def on_widget_release(self, event):
        if event.button() == Qt.LeftButton and self.current_widget:
            y_offset = event.y() - self.slide_start_y
            # 判断滑动方向并调用共用槽函数
            if abs(y_offset) > self.slide_threshold:
                slide_dir = "up" if y_offset < 0 else "down"
                self.on_slide_common(self.current_widget, slide_dir)
            # 重置当前组件
            self.current_widget = None

    # ========== 所有组件共用的滑动槽函数（核心逻辑） ==========
    def on_slide_common(self, widget_name, slide_dir):
        """
        共用槽函数
        :param widget_name: 滑动的组件名（step1pic/step1vdo）
        :param slide_dir: 滑动方向（up/down）
        """
        if widget_name == "step1pic":
            if slide_dir == "up":
                picpath = self.media.switchLocalPic(IsUpOption=True)  # 切换到上一张图片
            else:
                picpath = self.media.switchLocalPic(IsUpOption=False)  # 切换到下一张图片
            if picpath:
                print(f"切换到图片: {picpath}")
                self.display_image_to_label(picpath, self.Items_txtmode['step1pic'])
            else:
                print(f" {widget_name} 图片切换失败")
        
        elif widget_name == "step1vdo":
            if slide_dir == "up":
                print(f" {widget_name} 上滑 → 执行视频上滑逻辑（如音量+）")
            else:
                print(f" {widget_name} 下滑 → 执行视频下滑逻辑（如音量-）")
                # self.Items_vdomode[widget_name].setText(f"{widget_name}\n下滑触发！")

    def on_media_trans_progress(self, media_type, progress, tip):
        if media_type == MediaType.Type_TXT:
            print(f"文本传输进度: {progress:.1f}%" + f" {tip}")
        elif media_type == MediaType.Type_PIC:
            print(f"图片传输进度: {progress:.1f}%" + f" {tip}")
        elif media_type == MediaType.Type_VDO:
            print(f"视频传输进度: {progress:.1f}%" + f" {tip}")
        else:
            print(f"未知的媒体类型: {media_type}" + f" {tip}")

    def CameRefrsh(self, qimage:QImage):
        if qimage is None:
            print("[CameRefrsh] qimage is None")
            return False

        if qimage.isNull():
            print("[CameRefrsh] qimage is null")
            return False

        try:
            pixmap = QPixmap.fromImage(qimage)
            if pixmap.isNull():
                print("[CameRefrsh] pixmap is null")
                return False
            rounded_pixmap = self.createRoundedPixmap(pixmap, radius=20.0)
            if rounded_pixmap.isNull():
                print("[CameRefrsh] rounded_pixmap is null")
                return False

            if self.SysManage.sys_state == SystemState.PIC_MODE:
                    # 显示图像
                    self.Items_picmode['cam'].setScaledContents(True)
                    self.Items_picmode['cam'].setPixmap(
                        rounded_pixmap.scaled(
                            self.Items_picmode['camframe'].size(), 
                            Qt.IgnoreAspectRatio
                        )
                    )
            elif self.SysManage.sys_state == SystemState.VDO_MODE:
                    # 显示图像
                    self.Items_vdomode['cam'].setScaledContents(True)
                    self.Items_vdomode['cam'].setPixmap(
                        rounded_pixmap.scaled(
                            self.Items_vdomode['camframe'].size(), 
                            Qt.IgnoreAspectRatio
                        )
                    )
            return True
        except Exception as e:
            print(f"[CameRefrsh] exception: {e}")
            return False
        
    def ShowWarnMsg(self, Type:WarnType, msg:str)->bool:
        if self.Items_Def['WarnLabel'] is None:
            print("ShowWarnMsg warnlabel is none")
            return False
        else:
            return self.Items_Def['WarnLabel'].WarnMsg(Type, msg)

#############################################################################################
################################## 1. 通用核心功能函数实现 end #############################
#############################################################################################

#############################################################################################
################################## 2. 文本传输核心功能函数实现 start #############################
#############################################################################################
    def trigtxtmode(self)->bool:
        print("low mode")
        # 已处于低模式
        if self.SysManage.sys_state == SystemState.TXT_MODE:
            print("low mode already")
            return True

        self.media.CloseCamStream()
        self.SwitHomePage(SystemState.TXT_MODE)
        return True
    
    # 核心功能函数（保持不变）
    def on_keyboard_click_data(self, key_text):
        """数字/字母按键：先校验长度→再校验字符→根据光标插入 + 实时提示"""
        key_text = key_text[:1]  
        if not key_text:  
            return
        # 1. 获取输入框控件、光标对象和当前内容
        current_text = self.Items_txtmode['inputedit'].text()
        cursor_pos = self.Items_txtmode['inputedit'].cursorPosition()  # 光标当前位置（字符索引）

        # ========== 第一步：校验长度（核心逻辑调整） ==========
        # 预判插入后总长度：当前长度 + 1个新字符
        if len(current_text) + 1 > self.TxtInputMaxLen:
            self.Items_txtmode['inputedit'].setFocus()
            return  
        # ========== 第二步：校验要插入的字符合法性 ==========
        if not (key_text.isdigit() or (key_text.isupper() and key_text.isalpha())):
            self.Items_txtmode['inputedit'].setFocus()
            return  # 非法字符直接返回

        # ========== 第三步：根据光标位置插入合法字符 ==========
        # 更新输入框内容
        new_text = current_text[:cursor_pos] + key_text + current_text[cursor_pos:]
        self.Items_txtmode['inputedit'].setText(new_text)
        self.Items_txtmode['inputedit'].setCursorPosition(cursor_pos + 1)  # 光标移到新字符右侧
        self.Items_txtmode['inputedit'].setFocus()
        print(f'新内容: {new_text}')  # 调试输出

    def on_keyboard_click_del(self):
        """删除键：根据光标位置删除左侧字符（适配QLineEdit单行输入框）"""
        # 获取当前文本和光标位置（QLineEdit专用方法）
        current_text = self.Items_txtmode['inputedit'].text()
        cursor_pos = self.Items_txtmode['inputedit'].cursorPosition()  # 单行输入框光标位置
        
        # 边界判断：无字符可删时直接返回
        if cursor_pos <= 0 or len(current_text) == 0:
            self.Items_txtmode['inputedit'].setFocus()
            return

        # 根据光标位置删除左侧字符（退格键逻辑）
        new_text = current_text[:cursor_pos - 1] + current_text[cursor_pos:]
        self.Items_txtmode['inputedit'].setText(new_text)
        self.Items_txtmode['inputedit'].setCursorPosition(cursor_pos - 1)
        self.Items_txtmode['inputedit'].setFocus() # 保持输入框焦点
        print(f'删除后内容：{new_text}')  # 调试输出
        
    def on_keyboard_click_send(self):
        """发送键：自定义处理逻辑"""
        print("Send键被点击，执行自定义逻辑")
        # 获取txt内容
        current_text = self.Items_txtmode['inputedit'].text()
        print(current_text)
        # 校验长度
        if len(current_text) == 0:
            self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.DefWarnType_E, "请输入内容")  # 发射信号，传递数据
            print("low step1 input is empty")
            return False
        # 可以发送
        if self.media.IsSending():
            # 设置数据
            self.media.SaveMediaData(MediaType.Type_TXT, current_text)
            # 开始发送
            self.media.Send(MediaType.Type_TXT)
        else:
            self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.DefWarnType_E, "忙碌中，稍后重试")  # 发射信号，传递数据
            print("LowModeStep1Send_busy")

#############################################################################################
################################## 2. 低速模式核心功能函数实现 end #############################
#############################################################################################

#############################################################################################
################################## 中速模式核心功能函数实现 start #############################
#############################################################################################
    def trigpicmode(self):
        print("pic mode")
        # 已处于中模式
        if self.SysManage.sys_state == SystemState.PIC_MODE:
            print("pic mode already")
            return True
        self.media.OpenCamStream()
        self.SwitHomePage(SystemState.PIC_MODE)

    def TookPhoto(self)->bool:
        # MidModeStep1TakPto
        cur_text = self.Items_picmode['tookphoto'].text()
        if cur_text == "拍照":
            res = self.media.TookPhoto()
            if res == False:
                self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.DefWarnType_E, "正在连接摄像头")  # 发射信号，传递数据
                return False
            self.Items_picmode['tookphoto'].setText("重拍")
        else:
            self.media.OpenCamStream()
            self.Items_picmode['tookphoto'].setText("拍照")
        return True
    
    def SendPhoto(self)->bool:
        print("SendPic mid step1 send photo")
        return True
    
#############################################################################################
#################################### 3. 中速模式核心功能函数实现 end ###########################
#############################################################################################

#############################################################################################
################################### 4. 高速模式核心功能函数实现 start ##########################
#############################################################################################
    def trigvdomode(self):
        print("hig mode")
        # 已处于高模式
        if self.SysManage.sys_state == SystemState.VDO_MODE:
            print("hig mode already")
            return True
       
        self.media.OpenCamStream()
         # 关闭业务
        self.SwitHomePage(SystemState.VDO_MODE)

#############################################################################################
################################### 4. 高速模式核心功能函数实现 end ############################
#############################################################################################

#############################################################################################
################################### 5. 工具类核心功能函数实现 start ############################
#############################################################################################
    
            
#############################################################################################
################################### 5. 工具类核心功能函数实现 end #############################
#############################################################################################
    def PicTranCtrl(self)->bool:
        print("SendPic mid step1 turn to step2")
        if self.SysManage.sys_state == SystemState.PIC_MODE:
            return False
        mediastste = self.media.IsSending()
        if mediastste != True:
            # 取消按钮
            print("SendPic media cancled")
            return False
        else:
            # 开始发送
            print("SendPic media start sending")
            return False


    '''
        ##########################################################
        ##########################################################
        槽函数实现区域
        stop
        ##########################################################
        ##########################################################
    '''

    '''
        ##########################################################
        ##########################################################
        功能函数实现区域
        start
        ##########################################################
        ##########################################################
    '''
       
    def SwitHomePage(self, page:SystemState):
        print("switchpage")
        mystste = self.SysManage.sys_state
        self.ShowModeChooseIcon(page)
        if page == SystemState.TXT_MODE:
            if mystste == SystemState.TXT_MODE:
                print("alread in low mode")
            else:
                self.SysManage.sys_state = SystemState.TXT_MODE
                self.Pages_Def['homepage'].setCurrentIndex(0)
                self.Pages_Def['txtpage'].setCurrentIndex(0)
        elif page == SystemState.PIC_MODE:
            if mystste == SystemState.PIC_MODE:
               print("alread in mid mode")
            else:
                self.SysManage.sys_state = SystemState.PIC_MODE
                self.Pages_Def['homepage'].setCurrentIndex(1)
                self.Pages_Def['picpage'].setCurrentIndex(0)
        elif page == SystemState.VDO_MODE:
            if mystste == SystemState.VDO_MODE:
                print("alread in hig mode")
            else:
                self.SysManage.sys_state = SystemState.VDO_MODE
                self.Pages_Def['homepage'].setCurrentIndex(2)
                self.Pages_Def['vdopage'].setCurrentIndex(0)
        else:   
            print("error inval param")
            pass    

    def ShowModeChooseIcon(self, page:SystemState):
        if page == SystemState.TXT_MODE:
            self.toggleImg(self.Items_Def['txtmode'], 'lowbtnUnEnable.svg', 'lowbtnEnable.svg')
            self.toggleImg(self.Items_Def['picmode'], 'midbtnEnable.svg', 'midbtnUnEnable.svg')
            self.toggleImg(self.Items_Def['vdomode'], 'higbtnEnable.svg', 'higbtnUnEnable.svg')
        elif page == SystemState.PIC_MODE:
            self.toggleImg(self.Items_Def['txtmode'], 'lowbtnEnable.svg', 'lowbtnUnEnable.svg')
            self.toggleImg(self.Items_Def['picmode'], 'midbtnUnEnable.svg', 'midbtnEnable.svg')
            self.toggleImg(self.Items_Def['vdomode'], 'higbtnEnable.svg', 'higbtnUnEnable.svg')
        elif page == SystemState.VDO_MODE:
            self.toggleImg(self.Items_Def['txtmode'], 'lowbtnEnable.svg', 'lowbtnUnEnable.svg')
            self.toggleImg(self.Items_Def['picmode'], 'midbtnEnable.svg', 'midbtnUnEnable.svg')
            self.toggleImg(self.Items_Def['vdomode'], 'higbtnUnEnable.svg', 'higbtnEnable.svg')
        else:   
            print("error inval param")
            pass    

    def SetMidTransResIcon(self, Qtobject, newimgurl:str):
        TipImgs = ['zhong_p_c_Error.svg','zhong_p_c_UnUse.svg','zhong_p_c_EU.svg','zhong_p_c_ok.svg']
        if Qtobject == None and newimgurl in TipImgs:
            print("SetMidTransResIcon error: Qtobject is None or newimgurl error")
            return False
        current_stylesheet = Qtobject.styleSheet()
        for imgurl in TipImgs:
            if imgurl in current_stylesheet:
                new_stylesheet = current_stylesheet.replace(imgurl, newimgurl)
                Qtobject.setStyleSheet(new_stylesheet)
                break
        return True
        
    def toggleImg(self, Qtobject, imgurl:str, newimgurl:str)->bool:
        if Qtobject == None:
            print("error: Qtobject is None")
            return False
        current_stylesheet = Qtobject.styleSheet()
        if imgurl in current_stylesheet:
            new_stylesheet = current_stylesheet.replace(imgurl, newimgurl)
            Qtobject.setStyleSheet(new_stylesheet)
            return True
        return False
        # else:
        #     print("error: The current style does not have this img")

    def toggleIcon(self, Qtobject:QPushButton, IconUrl:str):
        # 切换按钮图标
        if Qtobject.icon().isNull():
            return
        else:
            Qtobject.setIcon(QIcon(IconUrl)) # ':/btn/image/btn/ico_startG.svg'
        # else:
        #     print("error: The current style does not have this img")

    def SwitchToolImg(self, Qtobject:QPushButton, ImgName:str):
        names = ['ico_startG.svg', 'ico_startR.svg', 'ico_startY.svg']
        # 切换按钮图标
        if Qtobject == None:
            print("error: Qtobject is None")
            return False
        else:
            for name in names:
                if self.toggleImg(Qtobject, name, ImgName) == True:
                    return True
        return False
       
   
    
    def createRoundedPixmap(self, pixmap, radius):
        size = pixmap.size()
        rounded_pixmap = QPixmap(size)
        rounded_pixmap.fill(Qt.transparent)  # 填充透明背景

        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, size.width(), size.height()), radius, radius)
        
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return rounded_pixmap


    
    def InitNoteHtml(self, Browser:QTextBrowser,new_margin_top: int = 12)->None:
        # 获取当前的 HTML 内容
        html_content = Browser.toHtml()
        # 使用正则表达式匹配所有的 margin-top 样式，并将其值替换为指定的新值
        updated_html_content = re.sub(r'margin-top:\d+px;', f'margin-top:{new_margin_top}px;', html_content)
        # print("InitNoteHtml", updated_html_content)
        # 将修改后的 HTML 内容设置回 QTextBrowser
        Browser.setHtml(updated_html_content)
        
        '''
        ##########################################################
        ##########################################################
        功能函数实现区域
        stop
        ##########################################################
        ##########################################################
    '''

if __name__ == "__main__":
    # os.environ["QT_OPENGL"] = "software"
    # os.environ["QT_X11_NO_MITSHM"] = "1"
    # os.environ["QT_LOGGING_RULES"] = "qt.glx=false" 

    WinIconFilePath = ":/applogo/image/applogo_send.svg"
    WinTitle = '光通信教具(发送端)'
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QGuiApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow( WinIconFilePath, WinTitle)
    window.show()
    # window.showFullScreen() # 设置全屏显示
    # app.setOverrideCursor(QCursor(Qt.BlankCursor))
    sys.exit(app.exec_())
