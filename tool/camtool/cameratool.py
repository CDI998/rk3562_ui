
import cv2
import time
from PyQt5.QtGui import QImage
import numpy as np

class CameraTool:
    def __init__(self, camera_id=0, ReConnectInterval=1, MaxRetries = 2, cameraSize=(640, 480)):
        self.camera_id = camera_id
        self.cameraSize =cameraSize
        self.cap = None
        self.MaxRetries = MaxRetries # 最大重试次数
        self.ReConnectInterval = ReConnectInterval  # 重新连接的间隔时间（秒）
        self.EnCamera = True
        self.cameras = []

    def list_cameras(self,max_tested=3)->list:
        """
        List all available camera devices.
        max_tested: the maximum number of devices to test.
        return [0, 1] 两个摄像头
        调用前先关闭摄像头
        """
        available_cameras = []
        try:
            for i in range(max_tested):
                # 判断是否与当前已打开的摄像头一致
                if i == self.camera_id:
                    if self.isUsable():
                        available_cameras.append(i)
                else:
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            available_cameras.append(i)
                        cap.release()
            return available_cameras.copy()
        except Exception as e:
            print(f"list_cameras ERRPR: {e}")
            return None
    
    def resetcamid(self, camera_id: int)->bool:
        if self.camera_id == camera_id:
            return True
        else:
            self.EnCamera = False
            self.camera_id = camera_id
            # 重新连接摄像头
            self.reconnect()
            self.EnCamera = True
            return True

    def close(self) -> None:
        if self.cap != None:
            self.cap.release()

    def is_connected(self)->bool:
        """
        判断摄像头是否已连接。
        Args:
            无。
        Returns:
            bool: 如果摄像头已连接，则返回True；否则返回False。
        """
        if self.cap is not None and self.cap.isOpened():
            # print("检测——已连接")
            return True
        # print("检测-未连接")
        return False
    
    def isUsable(self)->bool:
        if self.is_connected():
            ret, frame = self.cap.read()
            if not ret:
                return False
            else:
                return True
        else:
            return False

    def connectToFirstOne(self)->bool:
        self.cameras = self.list_cameras()
        print(self.cameras)
        if len(self.cameras) == 0:
            print("没有检测到摄像头")
            return False
        else:
            print("识别到摄像头，自动打开新摄像头:camid",self.cameras[0])
            self.camera_id = self.cameras[0]
            res = self.connect()
            return res

    def connect(self)->bool:
        """
        尝试连接到指定ID的摄像头并返回一个布尔值表示连接是否成功。
        Args:
            无参数。
        Returns:
            bool: 连接成功返回True，否则返回False
        Raises:
            无特定异常抛出，但内部使用了try-except块捕获了可能发生的异常，并打印了错误信息。
        """
        try:
            if not self.is_connected():
                self.cap = cv2.VideoCapture(self.camera_id)
            if self.isUsable():
                return True
            self.disconnect()
            # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cameraSize[0])
            # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cameraSize[1])
            # if not self.cap.isOpened():
            raise Exception("无法打开摄像头")
            # return True
        except Exception as e:
            print(f"摄像头连接失败: {e}")
            return False

    def disconnect(self)->bool:
        """
        断开摄像头连接。
        Args:
            无参数。
        Returns:
            bool: 连接断开操作成功返回True，否则返回False。
        """
        if self.cap is not None:  
            try:
                self.cap.release()
                # print("摄像头已断开连接")
                return True
            except Exception as e:  # 捕获所有异常
                print(f"在断开摄像头连接时发生错误: {e}")
                return False
        else:
            # print("摄像头未连接")
            return True

    def reconnect(self)->bool:
        """
        尝试重新连接摄像头。
        Args:
            无
        Returns:
            bool: 连接成功返回True，否则返回False。
        """
        self.disconnect()
        retries = 0
        while not self.connect() and retries < self.MaxRetries:
            # print(f"尝试重新连接摄像头（{self.ReConnectInterval}秒后重试）...")
            time.sleep(self.ReConnectInterval)
            retries += 1
        if retries == self.MaxRetries:
            # print("无法重新连接摄像头，已达到最大重试次数。")
            return False
        return True
    
    def ReconnectAutoSelect(self)->bool:
        self.disconnect()
        retries = 0
        if not self.connect():
          print("ReconnectAutoSelect 连接失败, 开始自动选择")
          if not self.connectToFirstOne():
            print("自动选择失败")
            return False
        return True
    
    def take_photo(self, photoname='myphoto'):
        """
        从连接的摄像头捕获一张图片并保存到本地。
        Args:
            photoname (str, optional): 图片保存的文件名，默认为 'myphoto'。
        Returns:
            numpy.ndarray: 捕获到的图像帧，类型为numpy数组。
        Raises:
            Exception: 如果摄像头未连接或无法重新连接，将引发异常。
            Exception: 如果无法从摄像头读取帧，将引发异常。
        """
        if self.EnCamera == False:
            return None
        connedflag = True # 记录初始连接状态
        if not self.is_connected():
            connedflag = False # 连接断开
            self.reconnect()
            if not self.is_connected():
                raise Exception("摄像头未连接或无法重新连接")
        ret, frame = self.cap.read()
        if not ret:
            if not connedflag and self.is_connected(): # 还原连接状态
                self.disconnect()
            raise Exception("无法从摄像头读取帧")
        flipped_frame = cv2.flip(frame, 1)
        resized_frame = cv2.resize(flipped_frame, self.cameraSize)
        cv2.imwrite(photoname+'.jpg', resized_frame)
        if not connedflag: # 还原连接状态
            self.disconnect()
        return frame
    
    def get_frame_RGB888(self)-> np.ndarray:
        # print("get_frame_RGB888")
        if self.EnCamera == False:
            return None
        connedflag = True # 记录初始连接状态
        if not self.isUsable():
            connedflag = False # 连接断开
            self.ReconnectAutoSelect()
            if not self.isUsable():
                raise Exception("摄像头未连接或无法重新连接")
        ret, frame = self.cap.read()
        if not ret:
            # if not connedflag and self.is_connected(): # 还原连接状态
            #     self.disconnect()
            self.disconnect()
            raise Exception("无法从摄像头读取帧,可能被占用")
        # 对图像进行水平翻转（即左右翻转）
        flipped_frame = cv2.flip(frame, 1)
        resized_frame = cv2.resize(flipped_frame, self.cameraSize)
        rgbImage = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        # if not connedflag: # 还原连接状态
        #     self.disconnect()
        #     pass
        return rgbImage

    def getcamera_id(self)->int:
        return self.camera_id
# camera_tool = CameraTool(camera_id=0)
# try:
#     frame = camera_tool.take_photo()
# except Exception as e:
#     print(f"拍照或显示失败: {e}")

# while True:
#     try:
#         frame = camera_tool.take_photo()
#         # 在这里处理frame，例如显示
#         cv2.imshow('Camera Preview', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     except Exception as e:
#         print(f"拍照或显示失败: {e}")

# 在退出循环后，销毁所有OpenCV窗口
# cv2.destroyAllWindows()