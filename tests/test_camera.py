import sys
import threading
import time

import cv2
from PyQt5 import QtWidgets, QtCore, QtGui


class CameraThread(QtCore.QThread):
    frameReady = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, device: str = "/dev/video11", width: int = 640, height: int = 480):
        super().__init__()
        self.device = device
        self.cap = None
        self.running = False
        self.width = width
        self.height = height

    def run(self):
        self.running = True
        # self.cap = cv2.VideoCapture(self.device)
        # pipeline = (
        #     "v4l2src device=/dev/video11 ! "
        #     "video/x-raw,format=NV12,width=480,height=640,framerate=30/1 ! "
        #     "videoflip method=horizontal-flip ! "
        #     "videoconvert ! "
        #     "video/x-raw,format=RGB ! "
        #     "appsink"
        # )
        pipeline = (
            "v4l2src device=/dev/video11 ! "
            "video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1 ! "
            "videoconvert ! "
            "appsink"
        )
        
        self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.frameReady.emit(qimg.copy())
            time.sleep(0.03)

        if self.cap:
            self.cap.release()

    def stop(self):
        self.running = False
        self.wait()


class CameraPreviewWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RK3562 Camera Preview")
        self.resize(800, 600)
        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.setCentralWidget(self.label)

        # self.thread = CameraThread(device=0)
        self.thread = CameraThread(device="/dev/video11")
        self.thread.frameReady.connect(self.on_frame_ready)
        self.thread.start()

    def on_frame_ready(self, qimg: QtGui.QImage):
        pixmap = QtGui.QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap.scaled(
            self.label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.thread.stop()
        super().closeEvent(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = CameraPreviewWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
