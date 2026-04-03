import sys
import cv2
import time
import threading
import queue
import subprocess
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal, QObject

# 队列用于线程间传输帧
frame_queue = queue.Queue(maxsize=10)

# 信号类，用于线程安全更新 GUI
class FrameSignal(QObject):
    update = pyqtSignal(np.ndarray)

# PyQt5 窗口类
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

# 摄像头线程
def camera_thread(cam_window):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("Camera thread started.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # 显示原始摄像头帧
        cam_window.update_frame(frame)

        # 每秒生成两帧送入队列
        for _ in range(2):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if not frame_queue.full():
                frame_queue.put(rgb_frame)
            time.sleep(0.5)

    cap.release()

# FFmpeg 处理线程
def process_thread(pre_window, processed_window):
    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", "640x480",
        "-r", "2",  # 输入帧率
        "-i", "pipe:0",
        "-vf", "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
        "-pix_fmt", "rgb24",
        "-f", "rawvideo",
        "-fflags", "nobuffer",
        "pipe:1"
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
    out_frame_size = 640 * 480 * 3
    buffer = []

    while True:
        if frame_queue.empty():
            time.sleep(0.01)
            continue

        frame = frame_queue.get()
        pre_window.update_frame(frame)
        buffer.append(frame)

        # 一次至少写入两帧，保证 minterpolate 有足够帧输出
        if len(buffer) >= 5:
            try:
                for f in buffer:
                    proc.stdin.write(f.tobytes())
                    print("Wrote frame to FFmpeg")
                buffer.clear()
            except BrokenPipeError:
                print("FFmpeg process terminated")
                break
            print("Wrote frames to FFmpeg222")
            # 尝试读取输出帧
            out_bytes = proc.stdout.read(out_frame_size)
            if len(out_bytes) == out_frame_size:
                out_frame = np.frombuffer(out_bytes, np.uint8).reshape((480, 640, 3))
                processed_window.update_frame(out_frame)

def main():
    app = QApplication(sys.argv)

    cam_window = VideoWindow("摄像头原始")
    cam_window.show()
    pre_window = VideoWindow("队列帧")
    pre_window.show()
    proc_window = VideoWindow("补帧后")
    proc_window.show()

    t1 = threading.Thread(target=camera_thread, args=(cam_window,), daemon=True)
    t2 = threading.Thread(target=process_thread, args=(pre_window, proc_window), daemon=True)

    t1.start()
    t2.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()