import copy
from enum import Enum

class BlockSendState(Enum):
    UnUsedtate    = 1  # 未使用
    SendedState   = 2  # 该块已发送
    SuccAckState  = 3  # 接收到成功响应
    ErrAckState   = 4  # 接收到错误响应
    NoAckState    = 5  # 超时无响应

class MidDataBean:
    def __init__(self):
        self.SendState = False  # 发送状态
        self.ImgBlockSendState = {} # 记录每一个图片块的发送情况
        self.ImgId = 0 # 记录每一个图片块的发送情况

        self.CurrLocalPicName = ""
        self.LocalPicNameList = []

    def SetSendState(self, IsSending: bool):
        self.SendState = IsSending

    def GetSendState(self) -> bool:
        return self.SendState
    
    def SetImgBlockMsg(self, Id: int, State:BlockSendState, Time:int):
        self.ImgBlockSendState[Id] = (State, Time)

    def SetImgBlockState(self, Id: int, State:BlockSendState):
        if Id in self.ImgBlockSendState:
            self.ImgBlockSendState[Id] = (State, self.ImgBlockSendState[Id][1])

    def SetImgBlockTime(self, Id: int, Time:int):
        if Id in self.ImgBlockSendState:
            self.ImgBlockSendState[Id] = (self.ImgBlockSendState[Id][0], Time)

    def ReSetImgBlockState(self, idlist:list):
        self.ImgBlockSendState = {}
        for id in idlist:
            self.ImgBlockSendState[id] = (BlockSendState.UnUsedtate, 0)

    def GetImgBlockState(self) -> dict:
        return copy.deepcopy(self.ImgBlockSendState)
    
    def GetImgBlockSendFailId(self) -> list:
        FailIdList = []
        for k, v in self.ImgBlockSendState.items():
            if v[0] == BlockSendState.ErrAckState or v[0] == BlockSendState.NoAckState:
                FailIdList.append(k)
        return FailIdList
    
    def SetImgId(self,Imgid:int):
        self.ImgId = Imgid
    
    def GetImgId(self) -> int:
        return self.ImgId


    
    def SetLocalPicNameList(self, pic_list: list) -> bool:
        """
        设置图片名称列表（深拷贝，保证数据隔离）
        :param pic_list: 图片名称列表（如["1.png", "2.png"]）
        :return: 设置成功返回True，失败返回False
        """
        # 1. 类型校验：必须是列表
        if not isinstance(pic_list, list):
            return False
        
        # 3. 深拷贝赋值（避免外部修改影响内部）
        self.LocalPicNameList = copy.deepcopy(pic_list)
        print(f" SetLocalPicNameList成功：共{len(self.LocalPicNameList)}个图片名称")
        return True
    
    def GetLocalPicNameList(self) -> list:
        """
        获取图片名称列表（深拷贝返回，避免外部修改内部数据）
        :return: 图片名称列表（深拷贝）
        """
        return copy.deepcopy(self.LocalPicNameList)
    
    def SetCurrLocalPicName(self, pic_name: str) -> bool:
        """
        设置当前图片名称（核心逻辑：不在列表则设为最后一个元素）
        :param pic_name: 要设置的图片名称（如"2.png"）
        :return: 设置成功返回True，失败返回False
        """
        # 1. 前置校验：LocalPicNameList为空
        if not self.LocalPicNameList:
            self.CurrLocalPicName = ""
            return False
        
        # 2. 类型校验：必须是字符串
        if not isinstance(pic_name, str):
            return False
        
        # 3. 核心逻辑：判断是否在列表中
        if pic_name in self.LocalPicNameList:
            self.CurrLocalPicName = pic_name
        else:
            # 不在列表中 → 设为列表最后一个元素（上一个）
            last_name = self.LocalPicNameList[-1]
            self.CurrLocalPicName = last_name
        return True 
    
    def GetCurrLocalPicName(self) -> str:
        """
        获取当前图片名称
        :return: 当前图片名称（字符串，空列表时返回空字符串）
        """
        return self.CurrLocalPicName

    def get_next_pic_name(self, input_name: str) -> str :
        """
        独立版：输入文件名和图片列表，返回后一个名称
        :param input_name: 输入的文件名称
        :return: 后一个名称/列表为空返回None
        """
        print(f" [ImgBean] 获取下一张图片名称，输入名称: {input_name}")
        if not self.LocalPicNameList or input_name is None:
            print(" [ImgBean] 图片列表为空，无法获取下一张图片名称")
            return ""
        if input_name not in self.LocalPicNameList:
            print(f" [ImgBean] 输入图片名称: {input_name} 不在列表中")
            return self.LocalPicNameList[0]
        print(f" [ImgBean] 输入图片名称: {input_name} 在列表中，获取下一张图片名称")
        curr_idx = self.LocalPicNameList.index(input_name)
        next_idx = 0 if curr_idx == len(self.LocalPicNameList) - 1 else curr_idx + 1
        return self.LocalPicNameList[next_idx]

    def get_prev_pic_name(self, input_name: str) -> str:
        """
        输入文件名，返回LocalPicNameList中该名称的前一个名称
        规则：
        1. LocalPicNameList为空 → 返回空字符串
        2. 输入名称不存在于LocalPicNameList → 返回第一个名称
        3. 输入名称是第一个 → 返回最后一个名称
        4. 输入名称存在且非第一个 → 返回前一个名称
        :param input_name: 输入的文件名称
        :return: 符合规则的名称（str）/列表为空返回空字符串
        """
        # 1. 列表为空 → 返回空字符串
        if not self.LocalPicNameList or input_name is None:
            return ""
        
        # 2. 输入名称不存在 → 返回第一个名称
        if input_name not in self.LocalPicNameList:
            return self.LocalPicNameList[0]
        
        # 3. 找到当前索引，计算前一个索引
        curr_idx = self.LocalPicNameList.index(input_name)
        list_len = len(self.LocalPicNameList)
        
        # 4. 核心逻辑：第一个→返回最后一个；否则返回前一个
        prev_idx = list_len - 1 if curr_idx == 0 else curr_idx - 1
        return self.LocalPicNameList[prev_idx]
    
