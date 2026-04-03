import copy
from enum import Enum

class HigDataBean:
    def __init__(self):
        self.SendState = False  # 发送状态

    def SetSendState(self, IsSending: bool):
        self.SendState = IsSending

    def GetSendState(self) -> bool:
        return self.SendState
    
