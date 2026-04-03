import cv2


class CamModel:
    def __init__(self, device: str = "/dev/video11", width: int = 640, height: int = 480):
        self.device = device
        self.width = width
        self.height = height
        self.cap = None
        # RK3562 专用 GStreamer 管道（动态宽高，NV12 格式）
        self.pipeline = (
            f"v4l2src device={self.device} ! "
            f"video/x-raw,format=NV12,width={self.width},height={self.height},framerate=30/1 ! "
            "videoconvert ! "
            "appsink"
        )

    def opencam(self) -> bool:
        # 打开前先释放之前的摄像头资源，防止 opencam 挂起
        self.closecam()
        try:
            cap = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)
        except Exception:
            self.cap = None
            return False
        if not cap or not cap.isOpened():
            if cap:
                cap.release()
            self.cap = None
            return False
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap = cap
        return True

    def closecam(self):
        # 无论何时都可以安全关闭，防止 closecam 挂起
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
        self.cap = None

    def IsCamConned(self) -> bool:
        # 只有 capture handle 存在且打开时才认定为连接
        return bool(self.cap and self.cap.isOpened())

    def getimg(self):
        if not self.IsCamConned():
            return None
        # 只尝试一次读取最新帧，避免阻塞
        grabbed, frame = self.cap.read()
        if grabbed and frame is not None:
            return frame
        return None
