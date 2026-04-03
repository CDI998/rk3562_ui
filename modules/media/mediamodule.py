import os
import time
from pathlib import Path

import cv2
from modules.media.cammodule import CamModel
import threading
from threading import Thread
from enum import Enum
from modules.signal.DefSignal import MediaSignals
from ui.warn import WarnType
from PyQt5.QtCore import pyqtSignal as Signal

class CamState(Enum):
    State_Idle      = 1  # 空闲状态
    State_Preview   = 2  # 预览状态，给主线程界面传输摄像头预览信息
    State_Recording = 3  # 录像状态

class MediaModule():
    def __init__(self, localpicpath: str, localvdopath: str,
                 ):
        self.localpicpath = localpicpath
        self.localvdopath = localvdopath

        self.cam = CamModel()
        self.media_signals = MediaSignals()

        self.mediathread = None
        self.MediaRunning = False
       
        self._camworkstate = CamState.State_Idle


    ################################ 图片相关核心功能函数实现 start #############################
    
        
    ################################ 图片相关核心功能函数实现 end #############################
    
    def MediaThread(self):
        # 摄像头采集线程，持续读取最新帧用于预览和录像
        while self.MediaRunning:
            if not self.cam.IsCamConned():
                opened = self.cam.opencam()
                if not opened:
                    time.sleep(0.1)
                    continue
            frame = self.cam.getimg()
            if frame is None:
                time.sleep(0.02)
                continue
            if self._camworkstate == CamState.State_Preview:
                pass
            elif self._camworkstate == CamState.State_Preview:
                pass
            time.sleep(0.01)

    def StartMediaThread(self):
        # 启动视频流线程，确保摄像头处于运行状态
        if self.MediaRunning:
            return True
        self.MediaRunning = True
        self.mediathread = Thread(target=self.MediaThread, daemon=True)
        self.mediathread.start()
        return True

    def StopMediaStream(self):
       pass

    def TookPhoto(self):
        pass

    def StartRecordVdo(self):
        pass

    def StopRecordVdo(self):
        pass
