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
import queue
from modules.globals.systemmanage import SystemState
from tool.globals.queuetool import QueueTool
from modules.datamodule.txtdatabean import TxtDataBean
from modules.datamodule.picdatabean import PicDataBean
from modules.datamodule.vdodatabean import VdoDataBean
from modules.media.picmodule import PicModule
from modules.signal.DefSignal import MediaType

class CamState(Enum):
    State_Idle      = 1  # 空闲状态
    State_Preview   = 2  # 预览状态，给主线程界面传输摄像头预览信息
    State_Recording = 3  # 录像状态

class ErrorType(Enum):
    ERROR_DEF = -1

class MediaModule(PicModule):
    def __init__(self, localpicpath: str, localvdopath: str, 
                 MediaSignals:MediaSignals,
                 MsduRxQueue: queue.Queue,
                 MsduTxQueue: queue.Queue
                 ):
        PicModule.__init__(self, LocalPicPath = localpicpath)  # 调用父类的构造函数
        self.localpicpath = localpicpath
        self.localvdopath = localvdopath

        self.cam = CamModel(device=1, width=640, height=480)
        self.TxtDataBean = TxtDataBean()
        self.PicDataBean = PicDataBean()
        self.VdoDataBean = VdoDataBean()

        self.MediaThread = None
        self.MediaRunning = False
        self.MediaTxThread = None
        self.MediaTxRunning = False
        self.MediaSending = False
       
        self.CamWorkState = CamState.State_Idle
        self.MediaSignals = MediaSignals
        self.MsduRxQueue = MsduRxQueue
        self.MsduTxQueue = MsduTxQueue

        # 任务队列
        self.MediaTxQueue = queue.Queue(maxsize=2)
        self.currMediaTxTask = None  # 空 = 空闲 | 有值 = 正在处理
    ################################ 图片相关核心功能函数实现 start #############################
    
        
    ################################ 图片相关核心功能函数实现 end #############################
    def MediaWorkTh(self):
        # 摄像头采集线程，持续读取最新帧用于预览和录像
        while self.MediaRunning:
            time.sleep(0.01)
            if not self.cam.IsCamConned():
                opened = self.cam.opencam()
                if not opened:
                    print("[MediaWorkTh] 摄像头打开失败，10秒后重试...")
                    time.sleep(5)
                    continue
            if self.CamWorkState == CamState.State_Preview or \
               self.CamWorkState == CamState.State_Recording:
                frame = self.cam.GetRgbImg()
                if frame is None:
                    continue
                qimg = self.cam.RgbImg2QImage(frame)
                if qimg is None:
                    continue
                # 发送qimg流
                self.MediaSignals.CameRefrshSignal.emit(qimg)  # 发射信号，传递数据
            
    def MediaTxTh(self):
        # 发送媒体数据线程，持续监测发送队列并处理发送任务
        while self.MediaTxRunning:
            # 发送本地
            task = QueueTool.GetMsgQueueBlock(self.MediaTxQueue,timeout=1)
            # 没拿到任务
            if task is None:
                continue
            print(f"[MediaTxTh] 获取到发送任务: {task}")
            self.currentSendTask = task
            # 解析数据
            try:
                media_type = task.get("type")
                media_path = task.get("path")
                # 解析文本发送任务
                if media_type == MediaType.Type_TXT:
                    # 文本从缓存中读取
                    userdata = self.TxtDataBean.get_text()
                    id = 0 # 文本ID固定为0，图片和视频ID从0开始递增
                    usermsg = (MediaType.Type_TXT, id, len(userdata), userdata)
                    while self.MediaSending:
                        res = QueueTool.PutMsgQueue(q = self.MsduTxQueue, msg = usermsg)
                        if res: # 成功放入发送队列，继续发送下一块
                            self.MediaSignals.TransProgress.emit(MediaType.Type_TXT, 100.00, "")
                            break
                        else:
                            time.sleep(0.05)

                # 解析图片发送任务
                elif media_type == MediaType.Type_PIC:
                    # 加载图片资源
                    if media_path == None:
                        # 从缓存中读取图片
                        blocks = self.CutRgbImg2JpgBlocks(self.PicDataBean.get_image_rgb(), x_blocks=2, y_blocks=2)
                    else:
                        # 从本地路径读取图片
                        BasePicDir = self.PicDataBean.get_image_path()
                        full_path = os.path.join(BasePicDir, media_path)
                        blocks = self.CutJpgImg2JpgBlocks(full_path, x_blocks=2, y_blocks=2)

                    total_blocks = len(blocks)
                    if total_blocks == 0:
                        self.MediaSignals.TransProgress.emit(MediaType.Type_PIC, ErrorType.ERROR_DEF, "图片异常，发送失败")
                    else:
                        for block in blocks:
                            id = block.get("id")
                            data = block.get("data")
                            usermsg = (MediaType.Type_PIC, id, len(data), data)
                            CurrNum = 0
                            while self.MediaSending:
                                res = QueueTool.PutMsgQueue(q = self.MsduTxQueue, msg = usermsg)
                                if res: # 成功放入发送队列，继续发送下一块
                                    CurrNum += 1
                                    progress = round((CurrNum / total_blocks) * 100.0, 2)
                                    self.MediaSignals.TransProgress.emit(MediaType.Type_PIC, progress, "")
                                else:
                                    time.sleep(0.05)
                                if CurrNum == total_blocks:
                                        break
                # 解析视频发送任务
                elif media_type == MediaType.Type_VDO:
                    if media_path == None:
                        # 缓存中无视频，只能从本地路径读取视频
                        self.MediaSignals.TransProgress.emit(MediaType.Type_VDO, ErrorType.ERROR_DEF, "加载视频异常，发送失败")
                    else:
                        base_vdo_dir = self.VdoDataBean.get_video_path()
                        full_vdo_path = os.path.join(base_vdo_dir, media_path)
                        if not os.path.exists(full_vdo_path):
                            self.MediaSignals.TransProgress.emit(MediaType.Type_VDO, ErrorType.ERROR_DEF, "视频文件不存在")
                        else:
                            total_size = os.path.getsize(full_vdo_path)
                            sent_size = 0
                            packet_size = 4096  # 每次发送 4KB 小包（进度非常平滑）
                            try:
                                with open(full_vdo_path, "rb") as f:
                                    packet_id = 0
                                    while self.MediaSending:
                                        # 读一小片
                                        chunk = f.read(packet_size)
                                        if not chunk:
                                            break  # 发送完成
                                        # 构造消息
                                        usermsg = (MediaType.Type_VDO, packet_id, len(chunk), chunk)
                                        # 发送
                                        while self.MediaSending:
                                            res = QueueTool.PutMsgQueue(q=self.MsduTxQueue, msg=usermsg)
                                            if res:
                                                break
                                            time.sleep(0.05)
                                        sent_size += len(chunk)
                                        packet_id = (packet_id + 1)%250
                                        progress = round((sent_size / total_size) * 100.0, 2)
                                        self.MediaSignals.TransProgress.emit(MediaType.Type_VDO, progress, "")
                                # 发送完成
                                if sent_size == total_size:
                                    self.MediaSignals.TransProgress.emit(MediaType.Type_VDO, 100.0, "视频发送完成")
                            except Exception as e:
                                self.MediaSignals.TransProgress.emit(MediaType.Type_VDO, ErrorType.ERROR_DEF, f"视频发送异常，请重试")
            except Exception as e:
                print("[TX] 发送异常:", e)

            # 被中断，停止发送
            if self.MediaSending == False:
                QueueTool.ClearMsgQueue(self.MediaTxQueue)
            # 发送完清空
            self.currentSendTask = None
            self.MediaSending    = False

    def StartMediaWorkTh(self):
        # 启动视频流线程，确保摄像头处于运行状态
        if self.MediaRunning:
            return True
        self.MediaRunning = True
        self.MediaThread = Thread(target=self.MediaWorkTh, daemon=True)
        self.MediaThread.start()
        return True
    
    def StopMediaWorkTh(self):
        # 停止视频流线程
        if not self.MediaRunning:
            return
        # 1. 先标记停止，让线程循环退出
        self.MediaRunning = False
        # 2. 等待线程真正结束（安全关闭）
        if self.MediaThread is not None:
            self.MediaThread.join()
    
    def StartMediaTxTh(self):
        # 启动媒体发送线程
        if self.MediaTxRunning:
            return True
        self.MediaTxRunning = True
        self.mediatxthread = Thread(target=self.MediaTxTh, daemon=True)
        self.mediatxthread.start()
        return True
    
    def StopMediaTxTh(self):
        # 停止媒体发送线程
        if not self.MediaTxRunning:
            return
        # 1. 先标记停止，让线程循环退出
        self.MediaTxRunning = False
        # 2. 等待线程真正结束（安全关闭）
        if self.mediatxthread is not None:
            self.mediatxthread.join()

    def Start(self):
        # 启动媒体模块，开启摄像头预览线程和发送线程
        self.StartMediaWorkTh()
        self.StartMediaTxTh()

    def Stop(self):
        # 停止媒体模块，关闭摄像头预览线程和发送线程
        self.StopMediaWorkTh()
        self.StopMediaTxTh()

    def OpenCamStream(self):
       self.CamWorkState = CamState.State_Preview

    def CloseCamStream(self):
       self.CamWorkState = CamState.State_Idle

    def TookPhoto(self):
        self.CamWorkState = CamState.State_Idle

    def StartRecordVdo(self):
        self.CamWorkState = CamState.State_Recording

    def StopRecordVdo(self):
        self.CamWorkState = CamState.State_Idle

    def IsSending(self)->bool:
        return self.MediaSending
    
    def SaveMediaData(self, mediaType:MediaType, data=None) -> bool:
        if mediaType == MediaType.Type_TXT:
            self.TxtDataBean.set_text(data)
        elif mediaType == MediaType.Type_PIC:
            self.PicDataBean.set_image_mem(data)
        elif mediaType == MediaType.Type_VDO:
            self.VdoDataBean.set_video_path(data)
        else:
            return False
        return True
    
    def Send(self, mediaType:MediaType, mediaPath=None) -> bool:
        # 无路径为默认当前用户输入（文本、拍照、录像）的内容
        task = {
            "type": mediaType, # text / image / video
            "path": mediaPath, # mem / local
        }
        res = QueueTool.PutMsgQueue(self.MediaTxQueue, task)
        if  res:
            self.MediaSending = True
            return True
        return False
    
    def CancelSending(self) -> bool:
        # 取消发送，停止当前正在发送的内容（文本、拍照、录像）
        self.MediaSending = False
        return True
    
