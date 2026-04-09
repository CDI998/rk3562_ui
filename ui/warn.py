from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup, QRect, Qt
from threading import Thread
import threading
import queue
from enum import Enum
from tool.globals.queuetool import QueueTool
from PyQt5.QtCore import pyqtSignal as Signal

class WarnType(Enum):
    InvalWarnType_E = 0   # 非法类型
    ErrorWarnType_E = 1   # 错误告警（红色）
    DefWarnType_E = 2     # 默认告警（黄色）
    NormalWarnType_E = 3  # 类型（绿色）

class WarnLabel(QLabel):
    WarnStartSignal = Signal()
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.WarnFinishSemaphore = threading.Semaphore(0)
        # 启动抖动动画的线程
        self.WarnThread = Thread(target=self.WarnThreadFunc, args=())
        self.WarnThread.daemon = True
        self.WarnThreadRuning = False
        self.WarnQueue = queue.Queue(maxsize=2)
        self.txtsize = 25 
        # padding: 10px;
        self.ErrorStyle = """background-color: red;
            color: white;
            border-radius: 15px;
            """
        self.DefStyle = """background-color: #ff9900;
            color: white;
            border-radius: 15px;
            """
        self.NormalStyle = """background-color: green;
            color: white;
            border-radius: 15px;
            """
        self.setFontSize(20)  # 设置初始字体大小
        # font-size: 25px;
        # 设置标签为圆角矩形
        self.setStyleSheet(self.DefStyle)
        self.animation_group = QSequentialAnimationGroup()
        self.WarnShakInit()
        self.hide()
        self.WarnThreadRun()

    def WarnThreadRun(self):
        self.WarnThreadRuning = True
        self.WarnThread.start()
        self.WarnFinishSemaphore.release()  # 释放信号量，开始播放下一个动画

    def WarnThreadStop(self):
        self.WarnThreadRuning = False

    def WarnThreadFunc(self):
        while self.WarnThreadRuning:
            self.WarnFinishSemaphore.acquire()  # 阻塞，直到动画播放完成
            quecmd = self.WarnQueue.get() # (cmd val)
            if quecmd is None or type(quecmd) != tuple or len(quecmd) != 2 or quecmd[0] is None:
                print("WarnThreadFunc: None or invalid param")
                self.WarnQueue.task_done()
                continue
            warntype = quecmd[0]
            warntxt = quecmd[1]
            print("WarnThreadFunc: warntype, warntxt", warntype, warntxt)
            if warntype == WarnType.ErrorWarnType_E:
                self.setStyleSheet(self.ErrorStyle)
            elif warntype == WarnType.DefWarnType_E:
                self.setStyleSheet(self.DefStyle)
            elif warntype == WarnType.NormalWarnType_E:
                self.setStyleSheet(self.NormalStyle)
            else:
                return False
            self.setText(warntxt)
            self.setFontSize(self.txtsize)
            self.WarnStartSignal.emit()
            self.WarnQueue.task_done()
    
    def setGeometry(self, x, y, width, height):
        # 调用父类的方法
        print("setGeometry: x, y, width, height", x, y, width, height)
        super().setGeometry(x, y, width, height)
        self.WarnShakUpdate()

    def WarnShakInit(self):
        self.WarnShakUpdate()
        # 启动动画并执行线程事件循环
        self.WarnStartSignal.connect(self.WarnShakStart)
        self.animation_group.finished.connect(self.WarnShakFinish)
        print("WarnShak")

    def WarnShakUpdate(self):
        # 创建抖动动画
        start_pos = self.geometry()
        shake_distance = 10
        # 定义左、右移动动画
        shake_left = QPropertyAnimation(self, b"geometry")
        shake_left.setDuration(100)
        shake_left.setStartValue(start_pos)
        shake_left.setEndValue(QRect(start_pos.x() - shake_distance, start_pos.y(), start_pos.width(), start_pos.height()))
        shake_right = QPropertyAnimation(self, b"geometry")
        shake_right.setDuration(100)
        shake_right.setStartValue(QRect(start_pos.x() - shake_distance, start_pos.y(), start_pos.width(), start_pos.height()))
        shake_right.setEndValue(QRect(start_pos.x() + shake_distance, start_pos.y(), start_pos.width(), start_pos.height()))
        shake_center = QPropertyAnimation(self, b"geometry")
        shake_center.setDuration(100)
        shake_center.setStartValue(QRect(start_pos.x() + shake_distance, start_pos.y(), start_pos.width(), start_pos.height()))
        shake_center.setEndValue(start_pos)
        # 定义保持动画
        shake_Keep = QPropertyAnimation(self, b"geometry")
        shake_Keep.setDuration(1600)
        shake_Keep.setStartValue(start_pos)
        shake_Keep.setEndValue(start_pos)
        # 将动画组合成一个序列
        self.animation_group.clear()
        self.animation_group.addAnimation(shake_left)
        self.animation_group.addAnimation(shake_right)
        self.animation_group.addAnimation(shake_center)
        self.animation_group.addAnimation(shake_Keep)

    def WarnShakStart(self):
        self.show()
        self.animation_group.start()

    def WarnShakFinish(self):
        print("WarnShakFinish")
        self.WarnFinishSemaphore.release()  # 释放信号量，开始播放下一个动画
        self.hide()

    def WarnMsg(self, warntype:WarnType, warntxt:str):
        if self.WarnThreadRuning == False:
            print("WarnMsg: WarnThreadRuning is False")
            return False
        QueueTool.PutMsgQueue(q = self.WarnQueue, msg = (warntype, warntxt))
    
    def setFontSize(self, size):
        """设置字体大小"""
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)
        self.txtsize = size
