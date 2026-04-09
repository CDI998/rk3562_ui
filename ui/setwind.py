from PyQt5.QtWidgets import QPushButton, QDialog, QVBoxLayout, QLabel, QComboBox, QFormLayout, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush, QMouseEvent
import re
from tool.globals.font import *

class SettingDialog(QDialog):
    # 定义信号
    refresh_signal = pyqtSignal()
    close_signal = pyqtSignal()
    confirm_signal = pyqtSignal(int)
    
    def __init__(self, parent=None, version:str = "0.0.0"):
        super().__init__(parent)
        self.version = version
        self.systemfont = systemfont()
        # Create the flags and set them
        flags = Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 210)
        self.setWindowTitle("设置")
        # Track mouse position for dragging
        self._drag_start_position = None
        # Main layout
        main_layout = QVBoxLayout(self)

        # Title bar
        title_bar = QWidget(self)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        title_bar.setStyleSheet("background-color: white;")

        # Title
        title_label = QLabel("设置", self)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_bar_layout.addWidget(title_label)

        # Spacer to push buttons to the right
        title_bar_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Close button
        self.close_button = QPushButton("X", self)
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: red; color: white;  padding: 0; font-size: 12px; border-radius: 5px
            }
            QPushButton:hover {
                background-color: darkred;
            }
            QPushButton:pressed {
                background-color: maroon;
            }
        """)
        self.close_button.clicked.connect(self.CloseSettingWind)
        title_bar_layout.addWidget(self.close_button)

        main_layout.addWidget(title_bar)
        # 创建 QFont 对象并设置字体大小
        font = QFont()
        font.setPointSize(10)  # 设置字体大小为 20
        font.setBold(True)     # 设置加粗
        # Settings content
        self.settings_layout = QFormLayout()
        self.settings_layout.setLabelAlignment(Qt.AlignRight)
        self.temp_label = QLabel("0°C")
        temp_tip_label = QLabel("温度:")
        temp_tip_label.setStyleSheet("font-weight: bold")
        self.temp_label.setFont(font)
        temp_tip_label.setFont(font)
        self.settings_layout.addRow(temp_tip_label, self.temp_label)

        self.version_label = QLabel(self.version)
        version_tip_label = QLabel("应用软件版本:")
        version_tip_label.setStyleSheet("font-weight: bold")
        self.version_label.setFont(font)
        version_tip_label.setFont(font)
        self.settings_layout.addRow(version_tip_label, self.version_label)

        self.bdversion_label = QLabel("v0.0.0")
        bdversion_tip_label = QLabel("板卡软件版本:")
        bdversion_tip_label.setStyleSheet("font-weight: bold")
        self.bdversion_label.setFont(font)
        bdversion_tip_label.setFont(font)
        self.settings_layout.addRow(bdversion_tip_label, self.bdversion_label)

        self.camera_combo = QComboBox()
        camera_tip_combo = QLabel("选择摄像头:")
        camera_tip_combo.setStyleSheet("font-weight: bold")
        self.camera_combo.addItems(["正在扫描"])
        self.camera_combo.setFont(font)
        camera_tip_combo.setFont(font)
        self.settings_layout.addRow(camera_tip_combo, self.camera_combo)

        main_layout.addLayout(self.settings_layout)
        
        # Spacer to push buttons to the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)

        # Refresh button
        self.refresh_button = QPushButton("刷新", self)
        self.refresh_button.setFont(font)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: green; color: white; border: none; padding: 5px; border-radius: 5px;
            }
            QPushButton:hover {
                background-color: darkgreen;
            }
            QPushButton:pressed {
                background-color: lime;
            }
        """)

        # Confirm button
        self.confirm_button = QPushButton("确认", self)
        self.confirm_button.setFont(font)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #0000ff; color: white; border: none; padding: 5px; border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0000cc;
            }
            QPushButton:pressed {
                background-color: #0033ff;
            }
        """)
        self.confirm_button.clicked.connect(self.send_confirm_signal)
        self.refresh_button.clicked.connect(self.send_refresh_signal)

        button_layout.addStretch(1)              # 左侧弹性占 10%
        button_layout.addWidget(self.refresh_button,3)
        button_layout.addStretch(2) 
        button_layout.addWidget(self.confirm_button,3)
        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)
        self.systemfont.set_font_for_all_widgets(self,"微软雅黑")

    def send_refresh_signal(self):
        self.refresh_signal.emit()

    def CloseSettingWind(self):
        self.close_signal.emit()
        self.accept()  # Close the dialog with accepted result

    def send_confirm_signal(self):
        txt = self.camera_combo.currentText()
        # 未扫描完
        if len(txt) >= 4 and txt[:3] == "摄像头":
            try:
                CameraId = int(txt[4:])
                self.confirm_signal.emit(CameraId)
                self.accept()
            except ValueError as e:
                print("转换失败:", e)
                self.accept()
        else:
            self.accept()

    def format_number(self, tempera:str):
        # 使用正则表达式检查输入是否符合 "xxx.XX" 的格式
        pattern = r'^\d*\.\d+$'
        if not re.match(pattern, tempera):
            # 如果输入不符合预期格式，原样返回
            return tempera
        # 分离整数部分和小数部分
        integer_part, decimal_part = tempera.split('.')
        # 去除整数部分的前导零
        integer_part = integer_part.lstrip('0')
        # 处理整数部分为空的情况
        if not integer_part:
            integer_part = '0'
        # 拼接处理后的整数部分和小数部分
        return f"{integer_part}.{decimal_part}"

    def update_temperature(self, temperature: str):
        # print("update_temperature",temperature)
        tempRes = self.format_number(temperature)
        self.temp_label.setText(f"{tempRes}°C")

    def update_boardversion(self, bdversion:str = ""):
        self.bdversion_label.setText(bdversion)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRoundedRect(self.rect(), 10, 10)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Save the start position for dragging
            self._drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_start_position is not None:
            # Calculate new position
            new_position = event.globalPos() - self._drag_start_position
            # Move the dialog
            self.move(new_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        # Reset drag start position
        self._drag_start_position = None
        event.accept()

    def update_camera_options(self, CamIdList: list, CurrCamId: int):
        """
        更新摄像头选项并设置默认选择项
        :param CamIdList: 摄像头 ID 的列表
        :param CurrCamId: 当前使用的摄像头 ID
        """
        # 清空之前的选项
        self.camera_combo.clear()
        # 添加新的摄像头选项
        for cam_id in CamIdList:
            self.camera_combo.addItem(f"摄像头 {cam_id}")
        # 查找当前摄像头 ID 的索引
        if CurrCamId in CamIdList:
            idx = CamIdList.index(CurrCamId)
        else:
            if len(CamIdList) == 0:
                idx = 0
                self.camera_combo.addItem("无摄像头")
            else:
                # 如果 CurrCamId 不在 CamIdList 中，则添加该 ID 到列表中
                idx = len(CamIdList)
                self.camera_combo.addItem(f"摄像头 {CurrCamId}")
        # 设置默认选择项
        self.camera_combo.setCurrentIndex(idx)

    def ScanCameraOptions(self):
        """
        更新摄像头选项并设置默认选择项
        :param CamIdList: 摄像头 ID 的列表
        :param CurrCamId: 当前使用的摄像头 ID
        """
        # 清空之前的选项
        self.camera_combo.clear()
        self.camera_combo.addItem("正在扫描")
        # 设置默认选择项
        self.camera_combo.setCurrentIndex(0)

