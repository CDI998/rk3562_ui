from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup, QRect, Qt, QTimer
from enum import Enum


class WarnType(Enum):
    InvalWarnType_E = 0
    ErrorWarnType_E = 1
    DefWarnType_E = 2
    NormalWarnType_E = 3


class WarnLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)

        self.txtsize = 25
        self.max_pending = 3
        self.pending_msgs = []
        self.is_showing = False

        self.ErrorStyle = """
            background-color: red;
            color: white;
            border-radius: 15px;
        """
        self.DefStyle = """
            background-color: #ff9900;
            color: white;
            border-radius: 15px;
        """
        self.NormalStyle = """
            background-color: green;
            color: white;
            border-radius: 15px;
        """

        self.warn_timer = QTimer(self)
        self.warn_timer.setSingleShot(True)
        self.warn_timer.timeout.connect(self.finishCurrentWarn)

        self.setFontSize(20)
        self.setStyleSheet(self.DefStyle)

        self.animation_group = QSequentialAnimationGroup()
        self.WarnShakInit()
        self.hide()

    def WarnMsg(self, warntype: WarnType, warntxt: str):
        if warntype is None or not isinstance(warntxt, str):
            print("WarnMsg: invalid param")
            return False

        if len(self.pending_msgs) >= self.max_pending:
            print("WarnMsg: queue full, drop new message")
            return False

        self.pending_msgs.append((warntype, warntxt))

        if not self.is_showing:
            self.showNextWarn()

        return True

    def showNextWarn(self):
        if not self.pending_msgs:
            self.is_showing = False
            self.hide()
            return

        self.is_showing = True
        warntype, warntxt = self.pending_msgs.pop(0)

        if warntype == WarnType.ErrorWarnType_E:
            self.setStyleSheet(self.ErrorStyle)
        elif warntype == WarnType.DefWarnType_E:
            self.setStyleSheet(self.DefStyle)
        elif warntype == WarnType.NormalWarnType_E:
            self.setStyleSheet(self.NormalStyle)
        else:
            self.is_showing = False
            self.showNextWarn()
            return

        self.setText(warntxt)
        self.setFontSize(self.txtsize)
        self.show()
        self.animation_group.start()
        self.warn_timer.start(1800)

    def finishCurrentWarn(self):
        self.hide()
        self.is_showing = False
        self.showNextWarn()

    def setGeometry(self, x, y, width, height):
        super().setGeometry(x, y, width, height)
        self.WarnShakUpdate()

    def WarnShakInit(self):
        self.WarnShakUpdate()
        self.animation_group.finished.connect(self.WarnShakFinish)

    def WarnShakUpdate(self):
        start_pos = self.geometry()
        shake_distance = 10

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

        shake_keep = QPropertyAnimation(self, b"geometry")
        shake_keep.setDuration(1600)
        shake_keep.setStartValue(start_pos)
        shake_keep.setEndValue(start_pos)

        self.animation_group.clear()
        self.animation_group.addAnimation(shake_left)
        self.animation_group.addAnimation(shake_right)
        self.animation_group.addAnimation(shake_center)
        self.animation_group.addAnimation(shake_keep)

    def WarnShakFinish(self):
        pass

    def setFontSize(self, size):
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)
        self.txtsize = size
