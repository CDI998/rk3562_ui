from PIL import Image, ImageDraw
import numpy as np
import copy

class ImgBean:
    def __init__(self):
        # USB摄像头获取的RGB像素点数据存储
        self.CamFrameRGB = None
        # 像素点处理后RGB图像数据存储
        self.QtImgRGB = None
        self.NetImgRGB = None

    def SetCamFrameRGB(self, Frame:np.ndarray)->bool:
        self.CameraFrameRGB = Frame.copy()
        return True
    
    def GetCamFrameRGB(self)->np.ndarray:
        return self.CameraFrameRGB.copy()
    
    def SetQtImgRGB(self, ImgRgb:Image)->bool:
        self.QtImgRGB = ImgRgb.copy()
        return True
    
    def GetQtImgRGB(self)->Image:
        return copy.deepcopy(self.QtImgRGB)
    
    def SetNetImgRGB(self, ImgRgb:Image)->bool:
        self.NetImgRGB = ImgRgb.copy()
        return True
    
    def GetNetImgRGB(self)->Image:
        return self.NetImgRGB.copy()
   