import cv2
from PyQt5.QtGui import QImage
import platform
from enum import Enum
import time
import os

class PlatformType(Enum):
    UNKNOWN_TYPE = 1
    WINDOWS_TYPE = 2
    LINUX_TYPE   = 3
    MACOS_TYPE   = 4
    
class CamModel:
    def __init__(self, device: str = "/dev/video11", width: int = 640, height: int = 480):
        self.device = device
        self.width = width
        self.height = height
        self.cap = None
        # RK3562 专用 GStreamer 管道（动态宽高，NV12 格式）
        self.pipeline = (
            f"v4l2src device={self.device} !  "
            f"video/x-raw,format=NV12,width={self.width},height={self.height},framerate=30/1 ! "
            "videoconvert ! video/x-raw,format=BGR ! "
            "appsink sync=false"
        )
        self.platform = self.get_current_platform()

    def get_current_platform(self) -> str:
        system = platform.system().lower()
        if system == "windows":
            return PlatformType.WINDOWS_TYPE
        if system == "linux":
            return PlatformType.LINUX_TYPE
        if system == "darwin":
            return PlatformType.MACOS_TYPE
        return PlatformType.UNKNOWN_TYPE

    def opencam(self) -> bool:
        # 打开前先释放之前的摄像头资源，防止 opencam 挂起
        self.closecam()
        time.sleep(0.1)  # 短暂等待确保资源释放完成
        try:
            if self.platform == PlatformType.LINUX_TYPE:
                cap = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)
            else:
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        except Exception:
            self.cap = None
            return False
        if not cap or not cap.isOpened():
            if cap:
                cap.release()
            self.cap = None
            return False
        self.cap = cap
        return True

    def closecam(self):
        print("[摄像头] 释放资源中...")
        # 无论何时都可以安全关闭，防止 closecam 挂起
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
        time.sleep(0.3)
        self.cap = None

    def IsCamConned(self) -> bool:
        # 只有 capture handle 存在且打开时才认定为连接
        return bool(self.cap and self.cap.isOpened())

    def GetRgbImg(self):
        try:
            # 1. 判断摄像头是否连接
            if not self.IsCamConned():
                return None
            # 2. 尝试读取一帧（非阻塞）
            try:
                grabbed, frame = self.cap.read()
            except Exception as e:
                print(f"[摄像头] 读取帧异常: {e}")
                return None
            # 3. 没读到帧
            if not grabbed or frame is None:
                return None
            # 4. 颜色空间转换（BGR → RGB）
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            except Exception as e:
                print(f"[摄像头] 格式转换异常: {e}")
                return None
            # 5. 最终返回正常帧
            return rgb_frame
        
        # 最外层捕获所有未知异常，保证函数绝不崩溃
        except Exception as e:
            print(f"[摄像头] getimg 未知异常: {e}")
            return None


    def RgbImg2QImage(self, frame):
        """
        把摄像头读取的 RGB frame 转换成 QImage
        :param frame: RGB 格式的 numpy 数组（来自 getimg()）
        :return: QImage / None
        """
        try:
            # 空帧直接返回
            if frame is None:
                return None
            # 获取图像尺寸
            h, w, ch = frame.shape
            stride = frame.strides[0]
            # 转换 RGB -> QImage
            qimg = QImage(
                frame.data,
                w,
                h,
                stride,
                QImage.Format_RGB888
            )
            
            return qimg.copy()
        except Exception as e:
            # 异常安全处理
            print(f"[帧转QImage失败] {e}")
            return None