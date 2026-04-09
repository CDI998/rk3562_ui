from tool.globals.queuetool import *
from modules.globals.systemmanage import SystemState
from tool.packtool.packer import *
from threading import Thread
from modules.network.network import NetWorkMode
# from PyQt5.QtCore import pyqtSignal as Signal
import time
from tool.packtool.packer import MsduType, MsduMode, MsduCmd, MLME_Def
from tool.packtool.packer import MCPS_Def, MLME_Head_Def, MCPS_Head_Def
from tool.globals.mediatool import MediaTool

class MsduMsgDataType(Enum):
    InvalMdataType_E = 0  # 非法类型
    BytesMdataType_E = 1  # 字节流类型
    StrMdataType_E   = 2  # 字符串类型

class MsduModule(packer):
    def __init__(self, MsduRxQueue:queue, MsduTxQueue:queue):
        super().__init__()
        self.MsduQueueRx = MsduRxQueue # (MediaType.Type_VDO, packet_id, len(chunk), chunk)
        self.MsduQueueTx = MsduTxQueue
       
        self.MsduTxRuning = True
        self.MsduTxThread = Thread(target=self.MsudTxTh, args=())
        self.MsduTxThread.daemon = True

        self.MsduRxRuning = True
        self.MsduRxThread = Thread(target=self.MsduRxTh, args=())
        self.MsduRxThread.daemon = True
   
    def MsudTxTh(self):
        while self.MsduTxRuning:
            msg = QueueTool.GetMsgQueueBlock(self.MsduQueueTx)
            # 没拿到任务
            if msg is None:
                continue
            # 解析消息
            try:
                # 你的包格式：(类型, id, 长度, 数据)
                media_type = msg[0]
                packet_id   = msg[1]
                data_len    = msg[2]
                data        = msg[3]
                try:
                    print(f"[MsudTxTh] 准备发送数据包 - 类型: {media_type}, ID: {packet_id}, 长度: {data_len}")
                except Exception as e:
                    print(f"[MsudTxTh] 单包写入失败: {e}")

            except Exception as e:
                print(f"[MsudTxTh] 消息解析异常: {e}")
            
    def MsduRxTh(self):
        while self.MsduRxRuning:
            time.sleep(5)

    def Start(self):
        self.MsduRxRuning = True
        self.MsduRxThread.start()
        self.MsduTxRuning = True
        self.MsduTxThread.start()

    def Stop(self):
        self.MsduRxRuning = False
        self.MsduTxRuning = False

    def McpsAnaly(self, MsduMsg:bytes)->bool:
        return True 

    def MlmeAnaly(self, MlmeData:MLME_Def):
        pass
