
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
from modules.media.mediamodule import MediaModule, MediaWorkState
from modules.datamodule.midbean import MidDataBean, BlockSendState
from modules.network.network import NetWorkMode
from modules.signal.DefSignal import *
from modules.globals.msdu import MsduModule, MsduQueCmd
from modules.signal.DefSignal import DefSignals
from modules.globals.UserActionManage import *

from tool.packtool.packer import *
from tool.conftool.config import *
from tool.globals.log import log
from tool.globals.queuetool import *
from tool.globals.font import *
from tool.globals.pathutils import PathUtils

from PIL import Image
import numpy as np

def handle_exception(exc_type, exc_value, exc_traceback):
    # 全局异常处理程序，将异常写入日志文件
    print("Unhandled exception:", file=sys.stderr)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

class step(Enum):
    Step1 = 1
    Step2 = 2
    Step3 = 3
    Step4 = 4
    InvalStep = 5

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, WinIconFilePath:str, WinTitle:str):
        super().__init__()
        self.setupUi(self)
        self.WinIconFilePath = WinIconFilePath
        self.WinTitle = WinTitle
        self.Version = "v2.1.3(Tx_A)"
        self.NoteHtml=""
        self.modebtns = {}
        self.DefQItem = {}
        self.lowbtns = {}
        self.lowtxts = {}
        self.midbtns = {}
        self.midtxts = {}
        self.higbtns = {}
        self.higtxts = {}
        self.syspage = {}
        self.timers = {}

         # ========== 滑动切换本地资源配置 ==========
        self.slide_threshold = 30  # 滑动触发阈值
        self.slide_start_y = 0     # 通用滑动起点Y轴
        self.current_widget = None # 记录当前滑动的组件

        self.WarnLabel = None
        self.conf = Config()
        self.mylog = log(audiocleanlog = self.conf.getbool("Log", "AutoClean"), 
                         logmax = self.conf.getint("Log", "LogFileMax"))
        self.VdoTranMaxTime = self.conf.getint("video", "VdoTranMaxTime")
        self.LowModeInputMaxLen = self.conf.getint("text", "InputMaxLen")
        self.LocalPicPath = self.conf.getstr("picture", "LocalPath")
        self.LocalVdoPath = self.conf.getstr("video", "LocalPath")
        self.mylog.LogRun()
        self.UserAction   = UserActionManage()
        self.DefSgnals    = DefSignals()
        self.MsduRxQueue  = queue.Queue(maxsize=10)
        self.MediaRxQueue = queue.Queue(maxsize=10)
        self.MediaSignals = MediaSignals()
        
        self.SysManage = SystemManager(SystemState.TXT_MODE)
        self.media     = MediaModule(localpicpath=self.LocalPicPath,  # 初始化本地图片路径
                                     localvdopath=self.LocalVdoPath   # 初始化本地视频路径
                                     )

        self.uiinit()
        self.modeinit()
        systemfont.set_font_for_all_widgets(self,"微软雅黑")   
        self.remove_all_frame_borders()
        # self.showFullScreen()   

    def remove_all_frame_borders(self):
        """移除所有QFrame组件的边框，使界面更简洁。RK芯片必须步骤"""
        for frame in self.findChildren(QFrame):
            frame.setFrameShape(QFrame.NoFrame)
            frame.setFrameShadow(QFrame.Plain)
        
    def uiinit(self):
        """
        初始化UI组件，包括按钮、文本框、页面、定时器等的绑定和界面属性设置。
        主要负责界面元素的组织和初始状态设定。
        """

        self.modebtns['close_btn_test'] = self.closebtn
        self.modebtns['low'] = self.lowbtn
        self.modebtns['hig'] = self.higbtn
        self.modebtns['mid'] = self.midbtn
        self.DefQItem['warnframe'] = self.warnframe 

        self.lowtxts['step1intxt'] = self.low1inputedit
        self.lowtxts['low1set']    = self.low1set
        
        keyboard_low = {
            '数字': ['1','2','3','4','5','6','7','8'],
            '字母': [chr(c) for c in range(ord('A'), ord('Z')+1)],  # A-Z自动生成
            '功能键': ['DEL', 'ENTER']
        }
        for group, keys in keyboard_low.items():
            for key in keys:
                btn_key = f'KB_{key}'       # 如 KB_1、KB_A、KB_DEL
                attr_name = f'kb_{key.lower()}'  # 如 kb_1、kb_a、kb_del
                # 通过对象属性名获取按键对象（核心：利用反射简化代码）
                self.lowbtns[btn_key] = getattr(self, attr_name)

        self.midtxts['step1camframe'] = self.mid1camframe # 容纳step1cam的窗口
        self.midtxts['step1cam'] = self.mid1cam
        self.midtxts['step1pic'] = self.mid1pic
        self.midbtns['tookphoto'] = self.tookphoto

        self.higtxts['step1camframe'] = self.hig1camframe # 容纳step1cam的窗口
        self.higtxts['step1cam'] = self.hig1cam # 容纳hig2vdo的窗口
        self.higtxts['step1vdo'] = self.hig1vdo
        self.higbtns['record'] = self.record
        

        self.syspage['homepage'] = self.modepage
        self.syspage['lowpage'] = self.lowpage_2
        self.syspage['midpage'] = self.midpage_2
        self.syspage['higpage'] = self.higpage_2
       
        self.disable_slider_manual_control(self.lowtxts['low1set']) # 禁止用户手动控制滑块位置，滑块位置只能通过代码控制（步骤）

        self.WarnLabel = WarnLabel("Initial Text", self.DefQItem['warnframe'])
        self.WarnLabel.setObjectName("WarnLabel")  # 设置 QLabel 的名字
        self.timers['MidAck'] = QTimer(self)
        self.timers['HigMaxWorkTime'] = QTimer(self)
        self.SwitHomePage(SystemState.TXT_MODE)
        self.setWindowIcon(QIcon(self.WinIconFilePath))
        self.setWindowTitle(self.WinTitle)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 设置为无边框

           
    def modeinit(self):
            self.modebtns['close_btn_test'].clicked.connect(self.close) 
        # 初始化模式
            self.modebtns['low'].clicked.connect(self.triglowmode) 
            self.modebtns['mid'].clicked.connect(self.trigmidmode) 
            self.modebtns['hig'].clicked.connect(self.trighigmode) 

            # 2. 低速按键
            for btn_key, btn in self.lowbtns.items():
                key_text = btn_key.replace('KB_', '')
                if key_text == 'DEL':
                    btn.clicked.connect(self.on_keyboard_click_del)
                elif key_text == 'ENTER':
                    btn.clicked.connect(self.on_keyboard_click_enter)
                else:
                    btn.clicked.connect(lambda checked, txt=key_text: self.on_keyboard_click_data(txt))

            # step1pic绑定
            self.midtxts['step1pic'].mousePressEvent = lambda e: self.on_widget_press(e, 'step1pic')
            self.midtxts['step1pic'].mouseReleaseEvent = self.on_widget_release
            
            # step1vdo绑定
            self.higtxts['step1vdo'].mousePressEvent = lambda e: self.on_widget_press(e, 'step1vdo')
            self.higtxts['step1vdo'].mouseReleaseEvent = self.on_widget_release

    
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
        time.sleep(0.4)
        self.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def eventFilter(self, obj, event):
        # print(f"Event type: {event.type()}")  # 打印事件类型值
        # if obj == self.lowtxts['step1intxt']:
        #     # print(f"Event type: {event.type()}")  # 打印事件类型值
        #     if event.type() == QEvent.Enter:
        #         print("Mouse entered the label area.")
        #         self.DefSgnals.UserInputAreaEnter.emit()
        #     elif event.type() == QEvent.Leave:
        #         print("Mouse left the label area.")
        #         self.DefSgnals.UserInputAreaLeave.emit()
        #     return False  # Allow the event to continue to be processed by QTextEdit
        # return super().eventFilter(obj, event)
        pass
    
    # ========== 禁用QSlider鼠标/键盘手动控制 ==========
    def disable_slider_manual_control(self, slider: QSlider):
        """
        禁止用户手动控制QSlider（鼠标点击/拖动、键盘操作均无效）
        :param slider: 目标QSlider对象
        """
        # 禁用键盘焦点（阻止方向键/回车控制）
        slider.setFocusPolicy(Qt.NoFocus)
        # 鼠标穿透（核心：点击/拖动滑块无任何反应）
        slider.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        # 可选：禁用鼠标跟踪（避免hover样式干扰）
        slider.setMouseTracking(False)

    # ==========设置滑块位置（0-99） ==========
    def set_slider_value(self, slider: QSlider, value: int):
        """
        代码控制QSlider位置，值范围限制在0-99
        :param slider: 目标QSlider对象
        :param value: 要设置的滑块值（自动裁剪到0-99范围）
        """
        # 校验并裁剪值到0-99范围，避免越界
        clamped_value = max(0, min(99, value))
        # 设置滑块位置
        slider.setValue(clamped_value)
        
#############################################################################################
################################## 1. 通用核心功能函数实现 end #############################
#############################################################################################

#############################################################################################
################################## 2. 低速模式核心功能函数实现 start #############################
#############################################################################################
    def triglowmode(self)->bool:
        print("low mode")
        # 已处于低模式
        if self.SysManage.sys_state == SystemState.TXT_MODE:
            print("low mode already")
            return True

        self.lowtxts['step1intxt'].clear()
        self.SwitHomePage(SystemState.TXT_MODE)
        self.SetLowActionStep(StepLowMode.InputingStep) # 默认低速第一步（用户输入）
        return True
    
    # 核心功能函数（保持不变）
    def on_keyboard_click_data(self, key_text):
        """数字/字母按键：先校验长度→再校验字符→根据光标插入 + 实时提示"""
        key_text = key_text[:1]  
        if not key_text:  
            return
        # 1. 获取输入框控件、光标对象和当前内容
        current_text = self.lowtxts['step1intxt'].text()
        cursor_pos = self.lowtxts['step1intxt'].cursorPosition()  # 光标当前位置（字符索引）

        # ========== 第一步：校验长度（核心逻辑调整） ==========
        # 预判插入后总长度：当前长度 + 1个新字符
        if len(current_text) + 1 > self.LowModeInputMaxLen:
            self.lowtxts['step1intxt'].setFocus()
            return  
        # ========== 第二步：校验要插入的字符合法性 ==========
        if not (key_text.isdigit() or (key_text.isupper() and key_text.isalpha())):
            self.lowtxts['step1intxt'].setFocus()
            return  # 非法字符直接返回

        # ========== 第三步：根据光标位置插入合法字符 ==========
        # 更新输入框内容
        new_text = current_text[:cursor_pos] + key_text + current_text[cursor_pos:]
        self.lowtxts['step1intxt'].setText(new_text)
        self.lowtxts['step1intxt'].setCursorPosition(cursor_pos + 1)  # 光标移到新字符右侧
        self.lowtxts['step1intxt'].setFocus()
        print(f'新内容: {new_text}')  # 调试输出

    def on_keyboard_click_del(self):
        """删除键：根据光标位置删除左侧字符（适配QLineEdit单行输入框）"""
        # 获取当前文本和光标位置（QLineEdit专用方法）
        current_text = self.lowtxts['step1intxt'].text()
        cursor_pos = self.lowtxts['step1intxt'].cursorPosition()  # 单行输入框光标位置
        
        # 边界判断：无字符可删时直接返回
        if cursor_pos <= 0 or len(current_text) == 0:
            self.lowtxts['step1intxt'].setFocus()
            return

        # 根据光标位置删除左侧字符（退格键逻辑）
        new_text = current_text[:cursor_pos - 1] + current_text[cursor_pos:]
        self.lowtxts['step1intxt'].setText(new_text)
        self.lowtxts['step1intxt'].setCursorPosition(cursor_pos - 1)
        self.lowtxts['step1intxt'].setFocus() # 保持输入框焦点
        print(f'删除后内容：{new_text}')  # 调试输出
        
    def on_keyboard_click_enter(self):
        """回车键：自定义处理逻辑"""
        print("Enter键被点击，执行自定义逻辑")

    def LowModeStep1Send(self):
        print("low step1 send")
        # 获取txt内容
        text = self.lowtxts['step1intxt'].toPlainText()
        print(text)
        # 转换为物理层进制流
        if len(text) == 0:
            self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.DefWarnType_E, "请输入内容")  # 发射信号，传递数据
            print("low step1 input is empty")
            return False
        self.media.SetTxtInput(text)
        if self.media.TxtCanSend():
            self.SwitStepPage(step.Step2)
            self.SetLowActionStep(StepLowMode.SendingStep)
            html = self.media.GetTxtBinMsg()
            self.lowtxts['step1tip'].setHtml(html)
            self.lowtxts['step2bin'].setHtml(html)
            txthtml = self.media.GetTxtMsg()
            self.lowtxts['step2txt'].setHtml(txthtml)
            # 创建udp包，并发送
            self.media.SendTxt()
        else:
            self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.DefWarnType_E, "忙碌中，稍后重试")  # 发射信号，传递数据
            print("LowModeStep1Send_busy")

#############################################################################################
################################## 2. 低速模式核心功能函数实现 end #############################
#############################################################################################

#############################################################################################
################################## 中速模式核心功能函数实现 start #############################
#############################################################################################
    def trigmidmode(self):
        print("mid mode")
        # 已处于中模式
        if self.SysManage.sys_state == SystemState.PIC_MODE:
            print("mid mode already")
            return True
        # 开启摄像头
        
        self.SwitHomePage(SystemState.PIC_MODE)

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
                self.display_image_to_label(picpath, self.lowtxts['step1pic'])
            else:
                print(f" {widget_name} 图片切换失败")
        
        elif widget_name == "step1vdo":
            if slide_dir == "up":
                print(f" {widget_name} 上滑 → 执行视频上滑逻辑（如音量+）")
            else:
                print(f" {widget_name} 下滑 → 执行视频下滑逻辑（如音量-）")
                # self.higtxts[widget_name].setText(f"{widget_name}\n下滑触发！")

    # 假设该函数写在你的主窗口类/业务类中
    
#############################################################################################
#################################### 3. 中速模式核心功能函数实现 end #############################
#############################################################################################

#############################################################################################
################################### 4. 高速模式核心功能函数实现 start ############################
#############################################################################################
    def trighigmode(self):
        print("hig mode")
        # 已处于高模式
        if self.SysManage.sys_state == SystemState.VDO_MODE:
            print("hig mode already")
            return True
        # 关闭业务
        # if self.media.IsTraning():
        #     self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.ErrorWarnType_E, "发送中，模式切换失败")  
        #     return False
        
        self.SwitHomePage(SystemState.VDO_MODE)

#############################################################################################
################################### 4. 高速模式核心功能函数实现 end ############################
#############################################################################################

#############################################################################################
################################### 5. 工具类核心功能函数实现 start ############################
#############################################################################################

    def display_image_to_label(self, image_path: str, label: QLabel):
        print(f" [显示图片] 开始显示图片，路径：{image_path}, QLabel对象：{label.objectName()}")    
            # """
            # 将指定路径的图片显示到传入的 QLabel 控件中
            # 支持：绝对路径/PNG/JPG等常见格式，自动适配控件大小
            # :param image_path: 图片绝对路径（必填）
            # :param label: 要显示图片的 QLabel 控件（必填）
            # :return: 显示成功返回True，失败返回False
            # """
            # print(f" [显示图片] 开始显示图片，路径：{image_path}, QLabel对象：{label.objectName()}")
            # # 1. 基础参数校验
            # if not image_path or not isinstance(image_path, str):
            #     print(" [显示图片] 图片路径无效（不能为空且必须为字符串）")
            #     return False
            
            # if not label or not isinstance(label, QLabel):
            #     print(" [显示图片] Label控件无效（不能为空且必须是QLabel类型）")
            #     return False
            
            # # 2. 校验图片路径存在性
            # if not PathUtils.check_path_exists(image_path):
            #     print(f" [显示图片] 图片路径不存在：{image_path}")
            #     return False
            # print(f" [显示图片] 图片路径验证通过：{image_path}")    
            # # 3. 加载并显示图片（核心逻辑）
            # try:
            #     # 方式1：优先用QPixmap加载本地图片（效率更高）
            #     pixmap = QPixmap(image_path)
            #     print(f" [显示图片] QPixmap加载结果：{'成功' if not pixmap.isNull() else '失败'}")
            #     if pixmap.isNull():
            #         # 方式2：PIL兜底加载（兼容特殊格式/损坏图片）
            #         img = Image.open(image_path).convert("RGB")
            #         img_np = np.array(img)
            #         h, w, ch = img_np.shape
            #         bytes_per_line = ch * w
            #         q_image = QImage(img_np.data, w, h, bytes_per_line, QImage.Format_RGB888)
            #         pixmap = QPixmap.fromImage(q_image)
                
            #     # 适配控件大小（保持宽高比，平滑缩放）
            #     scaled_pixmap = pixmap.scaled(
            #         label.size(), 
            #         aspectRatioMode=Qt.KeepAspectRatio,    # 保持图片宽高比
            #         transformMode=Qt.SmoothTransformation  # 平滑缩放，避免锯齿
            #     )
                
            #     # 设置图片到传入的Label控件
            #     label.setPixmap(scaled_pixmap)
            #     label.setAlignment(Qt.AlignCenter)  # 图片居中显示
            #     print(f" [显示图片] 成功加载图片到Label控件：{image_path}")
            #     return True
            
            # except Exception as e:
            #     print(f" [显示图片] 加载失败：{str(e)}")
            #     return False
            
#############################################################################################
################################### 5. 工具类核心功能函数实现 end ############################
#############################################################################################
        ############

    def MidModeStep1TakPto(self)->bool:
        mediastste = self.media.MediaState()
        if self.media.CamIsConned() == False:
            self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.DefWarnType_E, "正在连接摄像头")  # 发射信号，传递数据
            print("media not Runnig")
            return False
        if self.media.TakePhoto() == False:
            print("MidModeStep1TakPto 拍照失败")
            # 拍照失败
            self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.ErrorWarnType_E, "未连接摄像头")  # 发射信号，传递数据
        return True

    def MidModeStep1ReTakPto(self)->bool:
        print("MidModeStep1ReTakPto")
        mediastste = self.media.MediaState()
        if mediastste != MediaWorkState.IdleState:
            print("media not Idle")
            return False
        self.media.CameraPreview()
        return True

    def MidModeStep1Send(self)->bool:
        print("MidModeStep1Next mid step1 turn to step2")
        mediastste = self.media.MediaState()
        if mediastste != MediaWorkState.IdleState:
            self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.ErrorWarnType_E, "未拍摄照片")  # 发射信号，传递数据
            print("MidModeStep1Next media not Idle")
            return False
        # 判断是否拍照成功
        if self.media.TakePhotoRes() == True:
            if self.media.IsTraning():
                self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.DefWarnType_E, "忙碌中，稍后重试")  # 发射信号，传递数据
                print("MidModeStep2Send Is Sending")
                return False
            print("发送图片")
            self.SwitStepPage(step.Step2)
            qimage = self.media.MidModeImgAddBox(0)
            # 设置QPixmap
            pixmap = QPixmap.fromImage(qimage)
            # 创建带有圆角的QPixmap
            rounded_pixmap = self.createRoundedPixmap(pixmap, radius=20.0)
            # 显示图像
            self.midtxts['step3image'].setScaledContents(True)
            self.midtxts['step3image'].setPixmap(rounded_pixmap.scaled(self.midtxts['step3imageframe'].size(), Qt.IgnoreAspectRatio))
            self.midtxts['step2image'].setScaledContents(True)
            self.midtxts['step2image'].setPixmap(rounded_pixmap.scaled(self.midtxts['step2imageframe'].size(), Qt.IgnoreAspectRatio))
            self.media.SendImg()
            return True
        else:
            return False

    def MidModeStep3back(self):
        if self.media.IsTraning():
            self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.DefWarnType_E, "忙碌中，稍后重试")  # 发射信号，传递数据
            print("MidModeStep3back Is Sending")
            return False
        self.SwitStepPage(step.Step1)
        self.MidModeStep1ReTakPto()

    def MidModeStep3Resend(self):
        print("MidModeStep3Resend")
        if self.media.IsTraning():
            self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.DefWarnType_E, "忙碌中，稍后重试")  # 发射信号，传递数据
            print("MidModeStep3Resend Is Sending")
            return False
        print("重传图片")
        self.SwitStepPage(step.Step2)
        qimage = self.media.MidModeImgAddBox(0)
        # 设置QPixmap
        pixmap = QPixmap.fromImage(qimage)
        # 创建带有圆角的QPixmap
        rounded_pixmap = self.createRoundedPixmap(pixmap, radius=20.0)
        # 显示图像
        self.midtxts['step3image'].setScaledContents(True)
        self.midtxts['step3image'].setPixmap(rounded_pixmap.scaled(self.midtxts['step2imageframe'].size(), Qt.IgnoreAspectRatio))
        self.midtxts['step2image'].setScaledContents(True)
        self.midtxts['step2image'].setPixmap(rounded_pixmap.scaled(self.midtxts['step2imageframe'].size(), Qt.IgnoreAspectRatio))
        self.media.SendImg()

    def MidModeStep2Canl(self):
        # 停止中速发送
        self.media.ForceStopCurrImgTran()

    def HidModeStep2Send(self):
        if self.media.CamIsConned() == False:
            self.DefSgnals.ShowWarnMsgSignal.emit(WarnType.ErrorWarnType_E, "未连接摄像头")  # 发射信号，传递数据
            print("HidModeStep2Send 未连接摄像头")
            return False
        print("发送视频")
        # 切换界面
        self.SwitStepPage(step.Step2)
        # 传输数据
        self.media.MediaVdoStreamCTRL(True)
        if self.VdoTranMaxTime != 0:
            self.TimeCtrl('HigMaxWorkTime', True, self.VdoTranMaxTime)
        
    def HidModeStep3Stop(self):
        print("停止视频")
        # 切换界面
        self.SwitStepPage(step.Step1)
        # 停止发送
        self.media.MediaVdoStreamCTRL(False)
        
    def MidModeAckReshTimer(self):
        # 中速图片块超时无响应
        # print("MidModeAckReshTimer")
        # 获取图片块的时间戳
        self.media.UpdatePhotoSendState()

    def HigModeWorkTimeOut(self):
        # 高速依旧在发送，则停止
        if self.media.IsVdoTraning() == True:
            self.HidModeStep3Stop()
        print("HigModeWorkTimeOut,视频播放过久自动停止")
        self.TimeCtrl('HigMaxWorkTime',False,0)
  
    def CameRefrsh(self, qimage:QImage)->bool:
        # 刷新图片显示，qimage，图片内容，Res图片刷新是否成功
        # 当Res为True时，刷新成功，qimage有效。
        # print("came refresh")
        if qimage == None:
            print("no image")
            return False
        # 获取当前的模式

        if self.SysManage.sys_state == SystemState.TXT_MODE:
            pass
        elif self.SysManage.sys_state == SystemState.PIC_MODE:
            # if Res:
                # 设置 QPixmap
                pixmap = QPixmap.fromImage(qimage)
                # 创建带有圆角的QPixmap
                rounded_pixmap = self.createRoundedPixmap(pixmap, radius=20.0)
                # 显示图像
                self.midtxts['step1cam'].setScaledContents(True)
                self.midtxts['step1cam'].setPixmap(rounded_pixmap.scaled(self.midtxts['step1camframe'].size(), Qt.IgnoreAspectRatio))
        elif self.SysManage.sys_state == SystemState.VDO_MODE:
            # pageidx = self.syspage['higpage'].currentIndex()
            # if pageidx == 1 or pageidx == 2:
                # 设置 QPixmap
                pixmap = QPixmap.fromImage(qimage)
                # 创建带有圆角的QPixmap
                rounded_pixmap = self.createRoundedPixmap(pixmap, radius=20.0)
                # 显示图像
                self.higtxts['step1vdo'].setScaledContents(True)
                self.higtxts['step1vdo'].setPixmap(rounded_pixmap.scaled(self.higtxts['step1vdoframe'].size(), Qt.IgnoreAspectRatio))
                # 创建带有圆角的QPixmap
                rounded_pixmap = self.createRoundedPixmap(pixmap, radius=20.0)
                # 显示图像
                self.higtxts['step2vdo'].setScaledContents(True)
                self.higtxts['step2vdo'].setPixmap(rounded_pixmap.scaled(self.higtxts['step2vdoframe'].size(), Qt.IgnoreAspectRatio))
            # else:
            #     print("pageidx error", pageidx)
            
    def ImgBinfrsh(self, ImgBinHtml:str):
        pass
        # self.midtxts['step2bintxt'].setHtml(ImgBinHtml)

    def MidSendImgRefrsh(self, Id:int, done:bool)->bool:
        if done == False:
            # 刷新图片显示
            print("MidSendImgRefrsh")
            # 设置提示框
            qimage = self.media.MidGetSendQImgWithBox(Id)
            # 设置 QPixmap
            pixmap = QPixmap.fromImage(qimage)
            # 创建带有圆角的QPixmap
            rounded_pixmap = self.createRoundedPixmap(pixmap, radius=20.0)
            # 显示图像
            self.midtxts['step3image'].setScaledContents(True)
            self.midtxts['step3image'].setPixmap(rounded_pixmap.scaled(self.midtxts['step3imageframe'].size(), Qt.IgnoreAspectRatio))
            self.midtxts['step2image'].setScaledContents(True)
            self.midtxts['step2image'].setPixmap(rounded_pixmap.scaled(self.midtxts['step2imageframe'].size(), Qt.IgnoreAspectRatio))
        else: 
            # 设置提示框
            qimage = self.media.MidGetQImgWithAllErrBox()
            # 设置 QPixmap
            pixmap = QPixmap.fromImage(qimage)
            # 创建带有圆角的QPixmap
            rounded_pixmap = self.createRoundedPixmap(pixmap, radius=20.0)
            # 显示图像
            self.midtxts['step3image'].setScaledContents(True)
            self.midtxts['step3image'].setPixmap(rounded_pixmap.scaled(self.midtxts['step3imageframe'].size(), Qt.IgnoreAspectRatio))
            self.midtxts['step2image'].setScaledContents(True)
            self.midtxts['step2image'].setPixmap(rounded_pixmap.scaled(self.midtxts['step2imageframe'].size(), Qt.IgnoreAspectRatio))

    def TimeCtrl(self, TimeName:str, Open:bool, Time:int):
        if TimeName in self.timers:
            if Open:
                self.timers[TimeName].start(Time)
            else:
                self.timers[TimeName].stop()

    def ResetTimer(self, TimeName:str, Time:int)->bool:
        if TimeName in self.timers:
            self.timers[TimeName].stop()
            self.timers[TimeName].start(Time)
            return True
        else:
            return False

    def SetImgSendState(self, IsSending:bool):
        # True - 图片传输开始
        # False - 图片传输结束
        if IsSending:
            # 刷新界面
            pass
        else:
            # 刷新界面
            self.SwitStepPage(step.Step3)
            # 显示发送情况
            # 设置提示框
            qimage = self.media.MidGetQImgWithAllStateBox()
            # 设置 QPixmap
            pixmap = QPixmap.fromImage(qimage)
            # 创建带有圆角的QPixmap
            rounded_pixmap = self.createRoundedPixmap(pixmap, radius=20.0)
            # 显示图像
            self.midtxts['step3image'].setScaledContents(True)
            self.midtxts['step3image'].setPixmap(rounded_pixmap.scaled(self.midtxts['step3imageframe'].size(), Qt.IgnoreAspectRatio))
            # 修改提示
            if self.media.IsAllBlockSendSucc_Mid(): # 全部块都发送成功
                self.SetMidTransResIcon(self.midtxts['step3tip'], 'zhong_p_c_ok.svg')
            else :
                HasErrorBlock = self.media.HasErrorBlockState_Mid()
                HasUnSendBlock = self.media.HasUnSendBlockState_Mid()
                if HasErrorBlock and HasUnSendBlock: # 有错误的块、未发送的块
                    self.SetMidTransResIcon(self.midtxts['step3tip'], 'zhong_p_c_EU.svg')
                elif HasErrorBlock: # 有错误的块
                    self.SetMidTransResIcon(self.midtxts['step3tip'], 'zhong_p_c_Error.svg')
                elif HasUnSendBlock: # 有未发送的块
                    self.SetMidTransResIcon(self.midtxts['step3tip'], 'zhong_p_c_UnUse.svg')
                else: # 没有块
                    print("设置图片发送结果异常")
            
    def ShowWarnMsg(self, Type:WarnType, msg:str)->bool:
        if self.WarnLabel is None:
            print("ShowWarnMsg warnlabel is none")
            return False
        else:
            self.WarnLabel.WarnMsg(Type, msg)

    # new start
    def ReshLowProgress(self, Txthtml:str,Binhtml:str):
        self.lowtxts['step2bin'].setHtml(Binhtml)
        self.lowtxts['step2txt'].setHtml(Txthtml)

    def SetTxtSendState(self, IsSending:bool):
        # True - 文本传输开始
        # False - 文本传输结束
        if IsSending:
            # 刷新界面
            pass
        else:
            # pass
            self.SwitStepPage(step.Step1)
            self.SetLowActionStep(StepLowMode.ResultsStep)


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
                self.syspage['homepage'].setCurrentIndex(0)
                self.syspage['lowpage'].setCurrentIndex(0)
        elif page == SystemState.PIC_MODE:
            if mystste == SystemState.PIC_MODE:
               print("alread in mid mode")
            else:
                self.SysManage.sys_state = SystemState.PIC_MODE
                self.syspage['homepage'].setCurrentIndex(1)
                self.syspage['midpage'].setCurrentIndex(0)
        elif page == SystemState.VDO_MODE:
            if mystste == SystemState.VDO_MODE:
                print("alread in hig mode")
            else:
                self.SysManage.sys_state = SystemState.VDO_MODE
                self.syspage['homepage'].setCurrentIndex(2)
                self.syspage['higpage'].setCurrentIndex(0)
        else:   
            print("error inval param")
            pass    

    def ShowModeChooseIcon(self, page:SystemState):
        if page == SystemState.TXT_MODE:
            self.toggleImg(self.modebtns['low'], 'lowbtnUnEnable.svg', 'lowbtnEnable.svg')
            self.toggleImg(self.modebtns['mid'], 'midbtnEnable.svg', 'midbtnUnEnable.svg')
            self.toggleImg(self.modebtns['hig'], 'higbtnEnable.svg', 'higbtnUnEnable.svg')
        elif page == SystemState.PIC_MODE:
            self.toggleImg(self.modebtns['low'], 'lowbtnEnable.svg', 'lowbtnUnEnable.svg')
            self.toggleImg(self.modebtns['mid'], 'midbtnUnEnable.svg', 'midbtnEnable.svg')
            self.toggleImg(self.modebtns['hig'], 'higbtnEnable.svg', 'higbtnUnEnable.svg')
        elif page == SystemState.VDO_MODE:
            self.toggleImg(self.modebtns['low'], 'lowbtnEnable.svg', 'lowbtnUnEnable.svg')
            self.toggleImg(self.modebtns['mid'], 'midbtnEnable.svg', 'midbtnUnEnable.svg')
            self.toggleImg(self.modebtns['hig'], 'higbtnUnEnable.svg', 'higbtnEnable.svg')
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
       
    def SwitStepPage(self, NewStep:step):
        """
        根据系统状态和新的步骤更新功能页面。
        Args:
            NewStep (step): 新的步骤对象，用于指示需要更新的功能页面。
        Returns:
            bool: 如果成功更新功能页面，则返回True；否则返回False。
        """
        # 获取主页面
        mystste = self.SysManage.sys_state
        if mystste == SystemState.TXT_MODE:
            steppage = self.syspage['lowpage']
        elif mystste == SystemState.PIC_MODE:
            steppage = self.syspage['midpage']
        elif mystste == SystemState.VDO_MODE:
            steppage = self.syspage['higpage']
        else:
            print("error SwitStepPage system state inval")
            return False
        # 更新功能页面
        if NewStep == step.Step1:
            steppage.setCurrentIndex(0)
        elif NewStep == step.Step2:
            steppage.setCurrentIndex(1)
        elif NewStep == step.Step3:
            steppage.setCurrentIndex(2)
        elif NewStep == step.Step4:
            steppage.setCurrentIndex(3)
        else:   
            print("error inval param")  
            return False
        return True
    
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

    def SetLowActionStep(self, newstep:StepLowMode)->bool:
        if newstep == StepLowMode.InvalStep:
            print("param inval")
            return False
        if self.UserAction.mode_step == newstep:
            pass
        else:
            if newstep == StepLowMode.InputingStep:
                # 显示操作提示、按键名称发送、可编辑
                self.UserAction.mode_step = newstep
                self.lowtxts['step1intxt'].setReadOnly(False) # 左侧刷新
            elif newstep == StepLowMode.SendingStep:
                pass
            elif newstep == StepLowMode.ResultsStep:
                # 显示传输进度、按键名称重发、可编辑
                self.UserAction.mode_step = newstep
                self.lowtxts['step1intxt'].setReadOnly(False)# 左侧刷新
        return True
    
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
