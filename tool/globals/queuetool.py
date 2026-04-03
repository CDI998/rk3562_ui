import queue
from enum import Enum

class MsduQueCmd(Enum):
    Invalid_E = 0   
    CheckMode_E = 1
    SyncBoard_E = 2
    CheckVersion_E = 3
    CheckCpuTemp_E = 4
    CheckProgress_E = 5 
    SendMsduMsg_E = 6
    CheckIldeCache_E = 7

class qeuetool:
    @staticmethod
    def PutMsgQueue(self, q:queue, msg = None):
        # print("PutMsgQueue")
        if not q.full():  # 检查队列是否满
            try:
                q.put(msg, block=False)  # 尝试放入队列
                # print("PutMsgQueue:Message put into queue")
            except queue.Full:
                print("PutMsgQueue failed:Net Queue is full")
        else:
            print("PutMsgQueue:Net Queue is full")
            pass