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
    def __init__(self, MsduQueueRx:queue, MdeiaQueRx:queue, 
                 MyIp = "", BoardIp="192.168.1.1", 
                 DefUdpDestIp="255.255.255.255", port=1234):
        super().__init__()
        self.MsduQueueRx = MsduQueueRx # (MsduQueCmd, param)
        self.MdeiaQueRx = MdeiaQueRx
        self.NetQueueTx = queue.Queue(maxsize=50)
        self.NetQueueRx = queue.Queue(maxsize=50)
        self.McpsByteHead = (0xaa, 0x0c)
        self.McpsBitHead = (0xaa, 0x12)
        self.RuningTx = True
        self.RuningRx = True
        self.threadTx = Thread(target=self.MsudTxThread, args=())
        self.threadTx.daemon = True
        self.threadRx = Thread(target=self.MsduRxThread, args=())
        self.threadRx.daemon = True
        self.NetWork = NetWorkMode(NetQueueTx = self.NetQueueTx,  # 接收网络包时触发信号，传递数据和IP
                                    NetQueueRx = self.NetQueueRx,  # 发送网络包时间，往队列中写入数据
                                    MyIp = MyIp,
                                    BoardIp = BoardIp, 
                                    DefUdpDestIp = DefUdpDestIp,
                                    port = port)
        self.destaddr = (DefUdpDestIp, port)
        self.qeuetool = qeuetool()
        self.mediatool = MediaTool()
   
    def MsudTxThread(self):
        while self.RuningTx:
            quecmd = self.MsduQueueRx.get() # (cmd val)
            if quecmd is None or type(quecmd) != tuple or quecmd[0] is None:
                print("MsudTxThread: None or invalid param")
                self.MsduQueueRx.task_done()
                continue
            # 获取命令
            if quecmd[0] == MsduQueCmd.SyncBoard_E:
                self.SyncBoard(quecmd[1])
            elif quecmd[0] == MsduQueCmd.CheckMode_E:
                self.CheckBoardMode()
            elif quecmd[0] == MsduQueCmd.CheckVersion_E:
                self.CheckBoardVersion()
            elif quecmd[0] == MsduQueCmd.CheckCpuTemp_E:
                self.CheckBoardCpuTemp()
            elif quecmd[0] == MsduQueCmd.CheckProgress_E: # 检测进度
                self.CheckProgress()
            elif quecmd[0] == MsduQueCmd.SendMsduMsg_E: # 发送消息
                if len(quecmd) == 5: # cmd mode data datalen
                    mode = quecmd[1]
                    data = quecmd[2]
                    datatype = quecmd[3]
                    datalen = quecmd[4]
                    # print("MsudTxThread: SendMsduMsg",mode,datalen,datatype)
                    if datatype == MsduMsgDataType.BytesMdataType_E:
                        self.SendMsduMsgBytes(mode, data, datalen)
                    elif datatype == MsduMsgDataType.StrMdataType_E:
                        self.SendMsduMsgStr(mode, data, datalen)
                    else:
                        print("MsudTxThread: SendMsduMsg_E invalid DataType")
                else:
                    print("MsudTxThread: SendMsduMsg_E invalid param")
            elif quecmd[0] == MsduQueCmd.CheckIldeCache_E: # 检测空闲个数
                self.CheckIldeCache()
            self.MsduQueueRx.task_done()  # 通知队列该任务已处理完成
            
    def MsduRxThread(self):
        while self.RuningRx:
            netpack = self.NetQueueRx.get()
            if netpack is None or type(netpack) != tuple:
                print("MsduRxThread: None or invalid param")
                self.NetQueueRx.task_done()
                continue
            # 获取数据
            data = netpack[0] #bytes
            addr = netpack[1] #(ip, port)
            self.NetRecv(data, addr)
            self.NetQueueRx.task_done()  # 通知队列该任务已处理完成

    def MsduThreadRun(self):
        self.NetWork.NetRun()
        self.RuningRx = True
        self.threadRx.start()
        self.RuningTx = True
        self.threadTx.start()

    def MsduThreadStop(self):
        self.RuningRx = False
        self.RuningTx = False
        self.NetWork.NetStop()

    def CheckBoardMode(self):
        MlmeUdpMsg_check = self.PackMlme(MsduCmd.E_ReqWorkMode, "", 0)
        self.qeuetool.PutMsgQueue(self.NetQueueTx, (MlmeUdpMsg_check, self.destaddr))

    def CheckBoardVersion(self):
        MlmeGetVersion = self.PackMlme(MsduCmd.E_ReqVersion, "", 0)
        self.qeuetool.PutMsgQueue(self.NetQueueTx, (MlmeGetVersion, self.destaddr))
        
    def CheckBoardCpuTemp(self):
        MlmeGetCPUTemp = self.PackMlme(MsduCmd.E_ReqCPUTemp, "", 0)
        self.qeuetool.PutMsgQueue(self.NetQueueTx, (MlmeGetCPUTemp, self.destaddr))

    def CheckProgress(self):
        MlmeGetProgress = self.PackMlme(MsduCmd.E_ReqProgress, "", 0)
        self.qeuetool.PutMsgQueue(self.NetQueueTx, (MlmeGetProgress, self.destaddr))

    def SendMsduMsgBytes(self, mode:MsduMode, data:bytes, datalen:int):
        MlcpsSendMsg = self.PackMcps_Bytes(False, mode, data, datalen)
        self.qeuetool.PutMsgQueue(self.NetQueueTx, (MlcpsSendMsg, self.destaddr))

    def SendMsduMsgStr(self, mode:MsduMode, data:str, datalen:int):
        MlcpsSendMsg = self.PackMcps_Str(False, mode, data, datalen)
        self.qeuetool.PutMsgQueue(self.NetQueueTx, (MlcpsSendMsg, self.destaddr))

    def CheckIldeCache(self):
        MlmeGetProgress = self.PackMlme(MsduCmd.E_ReqIdleCache, "", 0)
        self.qeuetool.PutMsgQueue(self.NetQueueTx, (MlmeGetProgress, self.destaddr))

    def SyncBoard(self, SyncMode:SystemState):
        msg = ''
        if SyncMode == SystemState.TXT_MODE:
            msg = 'L'
        elif SyncMode == SystemState.PIC_MODE:
            msg = 'M'
        elif SyncMode == SystemState.VDO_MODE:
            msg = 'H'
        else:
            msg = 'E'
        MlmeUdpMsg_swmode = self.PackMlme(MsduCmd.E_SwitWorkMode, msg, 1)
        # 发送参数
        self.qeuetool.PutMsgQueue(self.NetQueueTx, (MlmeUdpMsg_swmode, self.destaddr))
        MlmeUdpMsg_check = self.PackMlme(MsduCmd.E_ReqWorkMode, "", 0)
        self.qeuetool.PutMsgQueue(self.NetQueueTx, (MlmeUdpMsg_check, self.destaddr))

    def NetRecv(self, MsduMsg:bytes, addr:tuple):
        TimeStamp = time.time() #int(time.time() * 1000)
        # print("NetRecv",TimeStamp)
       
        MsduMsgType = self.GetMsduType(MsduMsg)
        if MsduMsgType == MsduType.McpsType:
            print("McpsType", len(MsduMsg))
            self.McpsAnaly(MsduMsg)
        elif MsduMsgType == MsduType.MlmeType:
            # print("MlmeType")
            Mlme = self.UnPackMlme(MsduMsg)
            self.MlmeAnaly(Mlme)
        else:
            pass

    def McpsAnaly(self, MsduMsg:bytes)->bool:
        Mcps = self.UnPackMcps(MsduMsg)
        if Mcps == None:
            print("McpsAnaly error UnPackMcps")
            return False
        McpsData = list(Mcps.data) # int
        print("McpsAnaly:",Mcps.mode)
        if Mcps.mode == MsduMode.LowMode.value:
            pass
        elif Mcps.mode == MsduMode.MidMode.value:
            if Mcps.amount == 3:
                ImgId = McpsData[0]
                ImgBlockId = McpsData[1]
                BlockRecvRes = McpsData[2]
                mediapg = (MsduType.McpsType, Mcps.mode, ImgId, ImgBlockId, BlockRecvRes)
                self.qeuetool.PutMsgQueue(self.MdeiaQueRx, mediapg)
            else:
                print("McpsAnaly error amount != 3(MidMode)", Mcps.amount)
        elif Mcps.mode == MsduMode.HigMode.value:
            pass
        else:
            pass
        return True 

    def MlmeAnaly(self, MlmeData:MLME_Def):
        print("mlme_cmd:",MlmeData.cmd)
        if MlmeData.cmd == MsduCmd.E_RespWorkMode.value:
          if(MlmeData.amount > 0):
              cmdparam = list(MlmeData.data) # int
              mode = cmdparam[0]
              
        elif MlmeData.cmd == MsduCmd.E_RespProgress.value:
            currid = self.GetMcpsPacketId()
            if(MlmeData.amount == 5):
                cmdparam = list(MlmeData.data) # int
                res = cmdparam[0]
                PacketId = cmdparam[1]
                ByteIndex = cmdparam[3]
                BitIndex = cmdparam[4]
                if(PacketId == currid and res == ord('R')):
                    # 发送信号刷新界面
                    mediapg = (MsduType.MlmeType, MlmeData.cmd, PacketId, ByteIndex, BitIndex, res)
                    self.qeuetool.PutMsgQueue(self.MdeiaQueRx, mediapg)
                else:
                    print("MlmeAnaly error res != R or PacketId != currid",PacketId,currid,PacketId,res)
        elif MlmeData.cmd == MsduCmd.E_RespIdleCache.value:
            print("mlme_cmd:",MlmeData.cmd)
            if MlmeData.amount == 1:
                cmdparam = list(MlmeData.data)  
                IdleNum = cmdparam[0]  # int
                if IdleNum != ord('E'):
                    mediapg = (MsduType.MlmeType, MlmeData.cmd, IdleNum)
                    self.qeuetool.PutMsgQueue(self.MdeiaQueRx, mediapg)
        elif MlmeData.cmd == MsduCmd.E_RespCPUTemp.value: # 获取温度
            print("mlme_cmd:",MlmeData.cmd)
            cmdparam = list(MlmeData.data)  # int
            Temp = ""
            if MlmeData.amount > PACKET_MLME_DATA_VOLUME or MlmeData.amount > len(cmdparam):
                print("mlme_cmd: data len error[cmd, datalen, maxlen]",MlmeData.cmd, MlmeData.amount, PACKET_MLME_DATA_VOLUME)
            else:
                for i in range(MlmeData.amount):
                    Temp += chr(cmdparam[i]) 
                print("mlme_cmd resh board tempe",Temp)
               
        elif MlmeData.cmd == MsduCmd.E_RespVersion.value: # 获取板卡版本
                print("mlme_cmd:",MlmeData.cmd)
                cmdparam = list(MlmeData.data)  # int
                Temp = ""
                if MlmeData.amount > PACKET_MLME_DATA_VOLUME:
                    print("mlme_cmd: data len error[cmd, datalen, maxlen]",MlmeData.cmd, MlmeData.amount, PACKET_MLME_DATA_VOLUME)
                else:
                    for i in range(MlmeData.amount):
                        Temp += chr(cmdparam[i]) 
                   
        else:
            pass
