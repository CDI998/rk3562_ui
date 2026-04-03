from enum import Enum
from threading import Thread
import queue
from tool.globals.mediatool import *
from tool.packtool.packer import *
import threading
import time
from PIL import Image
from modules.datamodule.higbean import HigDataBean
from tool.globals.queuetool import qeuetool, MsduQueCmd
from modules.globals.msdu import MsduMsgDataType

class VideoModule:
    def __init__(self, MsduRxQueue:queue, CheckCacheAckEvent:threading.Event,
                 VdoCutBlockSize = (80, 120), VdoBlockZipSize = 1118, DestAddr=("255.255.255.255", 1234)):
        """
        类的初始化方法
            VdoQueue (queue): 输入视频流队列，img为图片对象
            NetQueue (queue): 输出发送队列，发送数据到网络中
            DestAddr (tuple, optional): 目的地址和端口，默认为("255.255.255.255", 1234)。

            DestAddr (tuple): 目的地址和端口
            mediatool (MediaTool): 媒体工具实例，用于处理视频流
            packtool (packer): 打包工具实例，用于将数据打包成适合网络传输的格式
            thread (Thread): 线程实例，用于执行视频处理线程
        """
        self.VdoQueue = queue.Queue(maxsize=10)   # 线程队列
        self.VdoMsduQueue = MsduRxQueue  # 线程队列
        # self.CheckIdleEvHandle = CheckIdleEvHandle
        self.DestAddr = DestAddr  # 目的地址
        self.running = False  # 线程运行状态
        self.ForceStop = False  # 强制停止图片传输
        self.mediatool = MediaTool()
        self.packtool = packer()
        self.thread = Thread(target=self.VideoThread, args=())
        self.thread.daemon = True
        # 视频流参数
        self.VdoCutBlockSize = VdoCutBlockSize
        self.VdoBlockZipSize = VdoBlockZipSize
        self.higdata = HigDataBean()
        self.qeuetool = qeuetool()
        self.CheckCacheAckEvent = CheckCacheAckEvent
            
    def CheckIldeCache(self)->bool:
        res = False
        # 查询是否是否有缓存， 最大超时次数为100
        TimeoutCoun = 1
        while TimeoutCoun > 0:
            TimeoutCoun -= 1
            self.qeuetool.PutMsgQueue(q = self.VdoMsduQueue, msg = (MsduQueCmd.CheckIldeCache_E, None))
            self.CheckCacheAckEvent.clear()  
            # 等待线程B的响应，超时时间设为5秒
            if not self.CheckCacheAckEvent.wait(timeout=0.006):
                print("Sending pictures with No cache response", TimeoutCoun)
                pass
            else:
                # print("Sending pictures with Received cache response")
                res = True
                break
        return res

    def VideoThread(self):
        VideoFrameId = 0
        # MlmeUdpMsg = self.packtool.PackMlme(MsduCmd.E_ReqIdleCache, "", 0)
        while self.running:
            Img = self.VdoQueue.get()
            if type(Img) != Image.Image:
                print("VideoThread type(Img) != Image", type(Img))
                self.VdoQueue.task_done()  # 通知队列该任务已处理完成
                continue
            # 图片转字典：int，bytes
            ImgBlock = self.mediatool.PacketImgBlock(Img, self.VdoCutBlockSize, self.VdoBlockZipSize)
            VideoFrameId = (VideoFrameId+1)&0xff
            for ImgId,val in ImgBlock.items():
                if self.ForceStop:
                    break
                if ImgId > 255:
                    continue
                # 构建MCPS包
                blockbytes =  VideoFrameId.to_bytes(1, 'big')
                blockbytes =  blockbytes + ImgId.to_bytes(1, 'big') + val
                msdumsg = (MsduQueCmd.SendMsduMsg_E, MsduMode.HigMode, blockbytes, MsduMsgDataType.BytesMdataType_E, len(blockbytes))
                # 查询是否是否有缓存， 最大超时次数为5
                # self.checkIldeCache(MlmeUdpMsg, self.DestAddr)
                self.qeuetool.PutMsgQueue(q = self.VdoMsduQueue, msg = msdumsg)
                time.sleep(0.008)
            # 打印帧间间隔
            time.sleep(0.01)
            
            self.VdoQueue.task_done()  # 通知队列该任务已处理完成
        return
    
    def VdoThreadRun(self):
        self.running = True
        self.ForceStop = False
        self.thread.start()
        self.StopTran()

    def VdoThreadStop(self):
        self.running = False
        self.StopTran()

    def TranVideoFlow(self, Img:Image)->bool:
        self.StartTran()
        # 传输图片
        if not self.VdoQueue.full():  # 检查队列是否满
            try:
                self.VdoQueue.put(Img, block=False)  # 尝试放入队列
                # print("SendVdo:Message put into queue")
                return True
            except queue.Full:
                print("SendVdo failed:Video Queue is full")
                return False
        else:
            print("SendVdo:Video Queue is full")
            return False

    def StopTran(self):
        # 停止本次图片剩余的传输
        self.ForceStop = True
        self.higdata.SetSendState(False)
        
    def StartTran(self):
        # 开始本次图片剩余的传输
        self.higdata.SetSendState(True)
        self.ForceStop = False

    def IsVdoTraning(self):
        if self.higdata.GetSendState():
            return True
        else:
            return False
                