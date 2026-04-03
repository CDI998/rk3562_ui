
import sys
from PyQt5.QtWidgets import  QPushButton, QVBoxLayout, QSpacerItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QColor, QBrush
from tool.globals.font import *
from PyQt5.QtWidgets import QWidget, QSizePolicy, QGridLayout


class WinCtrlMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.systemfont = systemfont()
        self.initUI()
    
    def initUI(self):
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)  # 使用 Qt.Dialog
        self.setAttribute(Qt.WA_TranslucentBackground)  # 确保背景透明
        # self.setFixedSize(200, 150)
        self.font = QFont("微软雅黑", 15, QFont.Bold)# 设置字体大小为 20

        # 设置样式表
        # font-size: 16px;padding: 10px;padding: 10px;
        self.setStyleSheet("""
            QWidget {
                color: #e1e3e1;
              
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
               
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #003d73;
            }
        """)
        
        # 创建按钮
        self.button_minimize = QPushButton('最小化', self)
        # button_maximize = QPushButton('放大', self)
        self.button_close = QPushButton('关  闭', self)
        
        # 设置图标
        self.button_minimize.setIcon(QIcon(':/winctrl/image/winctrl/min.svg'))
        # # button_maximize.setIcon(QIcon(':/winctrl/image/winctrl/max.svg'))
        self.button_close.setIcon(QIcon(':/winctrl/image/winctrl/close.svg'))

        # 布局
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 去掉边距
        layout.setSpacing(0)                  # 去掉控件间距
        self.button_minimize.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_close.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        # layout.addWidget(self.button_minimize, 1, 1)  # 第一行第一列
        # layout.addWidget(self.button_close, 2, 1)  # 第二行第一列

        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 0, 1)  # 顶部弹簧
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 0)  # 左侧弹簧
        layout.addWidget(self.button_minimize, 1, 1)  # 第一个按钮
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 2)  # 按钮右侧弹簧
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 2, 1)  # 按钮下方弹簧
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 3, 1)  # 中间弹簧
        layout.addWidget(self.button_close, 4, 1)  # 第二个按钮
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 5, 1)  # 底部弹簧

# 设置行和列的伸缩比例
        layout.setRowStretch(0, 1)  # 顶部弹簧
        layout.setRowStretch(1, 8)  # 第一个按钮
        layout.setRowStretch(2, 1)  # 第一个按钮下的弹簧
        layout.setRowStretch(3, 1)  # 中间弹簧
        layout.setRowStretch(4, 8)  # 第二个按钮
        layout.setRowStretch(5, 1)  # 底部弹簧
        layout.setColumnStretch(0, 1)  # 左侧弹簧
        layout.setColumnStretch(1, 10)  # 按钮列
        layout.setColumnStretch(2, 1)  # 右侧弹簧
        # layout.addStretch(1) 
        # layout.addWidget(self.button_minimize,5)
        # layout.addStretch(1)
        # layout.addWidget(self.button_close,5)
        # layout.addStretch(1) 
        self.setLayout(layout)
        
        # 绑定按钮事件
        self.button_minimize.clicked.connect(self.minimizeParent)
        # button_maximize.clicked.connect(self.maximizeParent)
        self.button_close.clicked.connect(self.closeParent)
        self.installEventFilter(self)
        self.setFontSize()
        # self.systemfont.set_font_for_all_widgets(self,"微软雅黑")
    
    def minimizeParent(self):
        if self.parent is not None:
            self.parent.showMinimized()
        self.close()
    
    def maximizeParent(self):
        if self.parent is not None:
            if self.parent.isMaximized():
                self.parent.showNormal()
            else:
                self.parent.showMaximized()
        self.close()
    
    def closeParent(self):
        if self.parent is not None:
            self.parent.close()
        self.close()
    
    def eventFilter(self, source, event):
        if event.type() == 2:  # QEvent.MouseButtonPress
            self.close()
        return super().eventFilter(source, event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆角背景
        rect = self.rect()
        painter.setBrush(QBrush(QColor(255, 255, 255, 255)))  # 不透明背景色
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 3, 3)  # 绘制圆角矩形

    def setFontSize(self, size:int = 15):
        # print("设置字体大小",size)
        self.font.setPointSize(size)  # 设置字体大小为 20
        self.button_minimize.setFont(self.font)
        self.button_close.setFont(self.font)
        
import ui.rs_rc