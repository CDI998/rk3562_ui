import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

class CameraTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RK3562 摄像头测试")
        self.setFixedSize(640, 480)

        # 界面
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # 摄像头
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # 打开摄像头
        self.open_camera()
        self.timer.start(30)

    def open_camera(self):
        """ ✅ RK3562 唯一能稳定出图的方式：V4L2 + 手动设置 NV12 格式 """
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()

        # 核心：必须用 V4L2
        self.cap = cv2.VideoCapture("/dev/video11", cv2.CAP_V4L2)

        # RK3562 摄像头强制格式：NV12
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'NV12'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        print("摄像头打开成功:", self.cap.isOpened())

    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # NV12 转 RGB（RK3562 必须这样转）
        rgb = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_NV12)

        # 转 Qt 图像（用 stride 保证不花屏、不空白）
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, rgb.strides[0], QImage.Format_RGB888)

        self.label.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        print("关闭摄像头")
        if self.cap:
            self.cap.release()
        self.timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CameraTestWindow()
    win.show()
    sys.exit(app.exec_())