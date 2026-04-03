import cv2
import numpy as np
import queue
import threading
import time
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal, QObject

# -------------------------------
# 帧队列
frame_queue = queue.Queue(maxsize=20)

# 信号类，用于线程安全更新 Qt
class FrameSignal(QObject):
    update = pyqtSignal(np.ndarray)

class VideoWindow(QMainWindow):
    def __init__(self, title="视频窗口"):
        super().__init__()
        self.setWindowTitle(title)
        self.label = QLabel(self)
        self.setCentralWidget(self.label)
        self.resize(640, 480)
        self.signal = FrameSignal()
        self.signal.update.connect(self.on_update_frame)

    def on_update_frame(self, frame):
        h, w, ch = frame.shape
        qt_img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_img))

    def update_frame(self, frame):
        self.signal.update.emit(frame)

# -------------------------------
# 摄像头线程（5 fps）
def camera_thread():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if not frame_queue.full():
            frame_queue.put(rgb_frame)
        time.sleep(0.2)  # 5 fps

# -------------------------------
# 插帧函数
def interpolate_frames(frame1, frame2, num_intermediate=5):
    """使用光流线性插值生成中间帧"""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)

    flow = cv2.calcOpticalFlowFarneback(
        gray1, gray2, None,
        pyr_scale=0.5, levels=3, winsize=15,
        iterations=3, poly_n=5, poly_sigma=1.2, flags=0
    )

    interpolated_frames = []
    for i in range(1, num_intermediate+1):
        alpha = i / (num_intermediate+1)
        h, w = flow.shape[:2]
        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
        map_x = (map_x + alpha * flow[..., 0]).astype(np.float32)
        map_y = (map_y + alpha * flow[..., 1]).astype(np.float32)
        intermediate = cv2.remap(frame1, map_x, map_y, interpolation=cv2.INTER_LINEAR)
        interpolated_frames.append(intermediate)
    return interpolated_frames

# -------------------------------
# 插帧处理线程
def process_thread(window):
    last_frame = None
    while True:
        if frame_queue.qsize() < 2:
            time.sleep(0.01)
            continue

        frame1 = frame_queue.get()
        frame2 = frame_queue.get()

        # 原始帧显示
        window.update_frame(frame1)

        # 插帧
        interpolated = interpolate_frames(frame1, frame2, num_intermediate=5)
        for f in interpolated:
            window.update_frame(f)
            time.sleep(1/30)  # 模拟 30 fps 播放

        # 更新最后一帧为 frame2
        window.update_frame(frame2)

# -------------------------------
# 主函数
def main():
    app = QApplication([])

    window = VideoWindow("OpenCV 插帧演示")
    window.show()

    t1 = threading.Thread(target=camera_thread, daemon=True)
    t2 = threading.Thread(target=process_thread, args=(window,), daemon=True)
    t1.start()
    t2.start()

    app.exec_()

if __name__ == "__main__":
    main()