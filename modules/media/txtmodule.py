from tool.globals.bintool import bintool
from modules.datamodule.lowbean import LowDataBean
from threading import Thread
from tool.globals.queuetool import qeuetool, MsduQueCmd
from tool.packtool.packer import MsduMode
import time
import queue
from modules.globals.msdu import MsduMsgDataType
from modules.signal.DefSignal import MediaSignals

class txtModule():
    def __init__(self, MsduTxQueue:queue, TxtSignals:MediaSignals):
        self.TxtMsduTxQueue = MsduTxQueue
        self.TxtSignals = TxtSignals
        self.bintool = bintool()
        self.lowdata = LowDataBean()
        self.TXTthread = Thread(target = self.TxtSendThread) # , args=()
        self.TXTthread.daemon = True
        self.TxtRuning = True
        self.qeuetool = qeuetool()
        self.TxtQueue = queue.Queue(maxsize=10)

    def SetTxtInput(self, text:str)->bool:
        if 0 == len(text):
            return False
        # 转换为物理层进制流
        BitList = self.bintool.DataToPhyBinList(text, len(text))
        htmlstr = self.bintool.BinListToHtmlStr(BitList, 0, 0)
        self.lowdata.SetInputData(text) 
        self.lowdata.SetBinData(BitList) 
        self.lowdata.SetBinHtmlData(htmlstr) 
        return True
    
    def GetTxtBinMsg(self)->str:
        htmlstr = self.lowdata.GetBinHtmlData() 
        htmlcen = self.bintool.HtmlTxtCenter(htmlstr)
        return htmlcen
    
    def GetTxtMsg(self)->str:
        UserData = self.lowdata.GetInputData() 
        htmlstr = self.bintool.TxtStrToHtmlStr(UserData, 0, False) 
        return htmlstr
    
    def TxtCanSend(self)->bool:
        if self.lowdata.GetSendState() == False:
            return True
        else:
            return False
        
    def IsTxtTraning(self)->bool:
        return self.lowdata.GetSendState()
        
    def TxtSendThread(self):
        while self.TxtRuning:
            quecmd = self.TxtQueue.get() # (cmd val)
            if quecmd is None or quecmd[0] is None:
                print("MsudTxThread: None or invalid param")
                self.TxtQueue.task_done()
                continue
            UserText = quecmd[0]
            self.lowdata.SetSendState(True)
            self.TxtSignals.TxtSendStateSignal.emit(True)  # 开始发送
            # 发送网络包_数据
            time.sleep(0.8)
            msdumsg = (MsduQueCmd.SendMsduMsg_E, MsduMode.LowMode, UserText, MsduMsgDataType.StrMdataType_E, len(UserText))
            self.qeuetool.PutMsgQueue(q = self.TxtMsduTxQueue, msg = msdumsg)
            ReqTimes = len(UserText) * 18 * 4
            time.sleep(0.09)
            # 发送查询包
            for i in range(ReqTimes):
                time.sleep(0.041)
                self.qeuetool.PutMsgQueue(q = self.TxtMsduTxQueue, msg = (MsduQueCmd.CheckProgress_E, None))
            time.sleep(0.1)
            self.TxtSignals.TxtSendStateSignal.emit(False)  # 停止发送
            self.lowdata.SetSendState(False)
            self.TxtQueue.task_done()
            
    def TxtThreadRun(self):
        self.TxtRuning = True
        self.TXTthread.start()

    def TxtThreadStop(self):
        self.TxtRuning = False

    def SendTxt(self)->bool:
        TxtMsg = self.lowdata.GetInputData() 
        if len(TxtMsg) == 0 or self.TxtCanSend() == False:
            return False
        self.qeuetool.PutMsgQueue(q = self.TxtQueue, msg = (TxtMsg, None))
        return True


