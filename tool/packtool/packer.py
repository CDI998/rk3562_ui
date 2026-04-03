from ctypes import Structure, c_ubyte, c_uint16
from ctypes import sizeof
from enum import Enum

PACKET_MLME_DATA_VOLUME = 20  # 替换为实际的值
PACKET_MCPS_DATA_VOLUME = 1128  # 替换为实际的值

# 使用PACKET_MLME_DATA_VOLUME定义一个c_ubyte数组类型
DataArrayType_MLME = c_ubyte * PACKET_MLME_DATA_VOLUME
DataArrayType_MCPS = c_ubyte * PACKET_MCPS_DATA_VOLUME

class MsduType(Enum):
    InvalMsduType = 0
    MlmeType   = 1
    McpsType   = 2

class MsduMode(Enum):
    InvalMode = 0
    LowMode   = 1
    MidMode   = 2
    HigMode   = 3

class MsduCmd(Enum):
    E_Invalid = 0          # /* 非法 */
    E_ReqProgress = 1      # /* 申请获取发送进度 */
    E_RespProgress = 2     # /* 响应发送进度 */
    E_SwitWorkMode = 3     # /* 切换工作模式 */
    E_ReqWorkMode = 4      # /* 申请获取工作模式 */
    E_RespWorkMode = 5     # /* 响应工作模式 */
    E_ReqVersion = 6        # /* 查询版本号 */
    E_RespVersion = 7       # /* 响应版本号 */
    E_ReqDeliveryTime = 8   # /* 查询出厂时间 */
    E_RespDeliveryTime = 9  # /* 响应出厂时间 */
    E_ReqCPUTemp = 10       # /* 查询CPU温度 */
    E_RespCPUTemp = 11      # /* 响应CPU温度 */
    E_ReqCPUId = 12         # /* 查询CPU编号 */
    E_RespCPUId = 13        # /* 响应CPU编号 */
    E_ReqIdleCache = 14     # /* 查询空闲缓存（光路fifo中可用的成员个数）*/
    E_RespIdleCache = 15    # /* 响应空闲缓存（光路fifo中可用的成员个数） */


# 定义管理服务结构体
class MLME_Def(Structure):
    _pack_ = 1  # 确保没有内存对齐
    _fields_ = [
        ('head', c_ubyte * 2),  # 区分管理和服务
        ('cmd', c_ubyte),       # 指令
        ('amount', c_ubyte),    # 指令内容长度
        ('data', DataArrayType_MLME)  # 指令内容，使用先前定义的数组类型10
    ]

# 定义数据服务结构体
class MCPS_Def(Structure):
    _pack_ = 1  # 确保没有内存对齐
    _fields_ = [
        ('head', c_ubyte * 2),  # 区分管理和服务
        ('mode', c_ubyte),      # 模式
        ('id', c_ubyte),        # 数据包编号
        ('amount', c_uint16),    # 数据内容长度
        ('data', DataArrayType_MCPS)  # 指令内容，使用先前定义的数组类型10
    ]

class MLME_Head_Def(Structure):
    _pack_ = 1  # 确保没有内存对齐
    _fields_ = [
        ('head', c_ubyte * 2),  # 区分管理和服务
        ('cmd', c_ubyte),       # 指令
        ('amount', c_ubyte),    # 指令内容长度
    ]

class MCPS_Head_Def(Structure):
    _pack_ = 1  # 确保没有内存对齐
    _fields_ = [
        ('head', c_ubyte * 2),  # 区分管理和服务
        ('mode', c_ubyte),      # 模式
        ('id', c_ubyte),        # 数据包编号
        ('amount', c_uint16),    # 数据内容长度
    ]


class packer:
    def __init__(self, McpsHead=(0x0a, 0x55), MlmeHead=(0x0a, 0x59)):
        self.McpsHead = McpsHead
        self.MlmeHead = MlmeHead
        self.mlme_instance = MLME_Def()
        self.mcps_instance = MCPS_Def()
        self.DataArrayType_MLME = PACKET_MLME_DATA_VOLUME
        self.DataArrayType_MCPS = PACKET_MCPS_DATA_VOLUME
        self.mlmePackId = 0
        self.mcpsPackId = 0
        self.McpsStructSize = sizeof(MCPS_Def)
        self.MlmeStructSize = sizeof(MLME_Def)


    def PackMlme(self, cmd:MsduCmd, param:str, paramlen:int)->bytes:
        # mlme
        packcmd = (cmd.value & 0xFF) 
        self.mlme_instance.head = self.MlmeHead
        self.mlme_instance.cmd = packcmd
        self.mlme_instance.amount = paramlen
        if paramlen > self.DataArrayType_MLME:
            self.mcps_instance.amount = self.DataArrayType_MLME
        else:
            self.mcps_instance.amount = paramlen
            
        for i, char in enumerate(param):
            if(i < self.DataArrayType_MLME):
                self.mlme_instance.data[i] = ord(char);  
            else:
                break
        # 打印结构体内容
        # print("mlme_head:",list(self.mlme_instance.head))
        # print("mlme_cmd:",self.mlme_instance.cmd)
        # print("mlme_amount:",self.mlme_instance.amount)
        # print("mlme_data:",list(self.mlme_instance.data))  # 转换为列表以打印所有元素
        # 将结构体实例转换为字节串以便发送
        data_to_send_MLME = bytes(self.mlme_instance)
        # print("udpmsg:",data_to_send_MLME)  # 转换为列表以打印所有元素
        return data_to_send_MLME
    
    
    def PackMcps_Str(self, autofill:bool, Mode:MsduMode, data:str, datalen:int)->bytes:
        mcps_head = MCPS_Head_Def()
        packmode = (Mode.value & 0xFF) 
        self.mcpsPackId = (self.mcpsPackId + 1) % 0xfa
        # 填充信息
        mcps_head.head = self.McpsHead
        mcps_head.mode = packmode
        mcps_head.id = self.mcpsPackId
        # 最大长度判断
        # 最大长度判断
        if len(data) < datalen:
            datalen = len(data)
        if datalen > self.DataArrayType_MCPS:
            datalen = self.DataArrayType_MCPS
        mcps_head.amount = datalen
        # datacut=b''
        # for i, char in enumerate(data):
        #     if(i < datalen):
        #         datacut += ord(char);  
        #     else:
        #         break
        strdatacut = data[:datalen]
        datacut = strdatacut.encode()
        # 自动填充,使其满足4的倍数
        AddNum = datalen % 4
        if autofill and AddNum != 0:
            for j in range(AddNum):
                if(datalen < self.DataArrayType_MCPS): 
                    datacut = datacut + bytes([0x00])
                    datalen += 1
                else:
                    break
        # print("mcps_head:",list(self.mcps_instance.head))
        # print("mcps_mode:",self.mcps_instance.mode)
        # print("mcps_id:",self.mcps_instance.id)
        # print("mcp_amount:",self.mcps_instance.amount)
        # print("mcps_data:",list(self.mcps_instance.data))  # 转换为列表以打印所有元素
        data_to_send_MCPS = bytes(mcps_head)
        data_to_send_MCPS = data_to_send_MCPS + datacut
        # print("udpmsg:",data_to_send_MCPS)  # 转换为列表以打印所有元素
        return data_to_send_MCPS
        
    def PackMcps_Bytes(self, autofill:bool, Mode:MsduMode, data:bytes, datalen:int)->bytes:
        mcps_head = MCPS_Head_Def()
        packmode = (Mode.value & 0xFF) 
        self.mcpsPackId = (self.mcpsPackId + 1) % 0xfa
        # 填充信息
        mcps_head.head = self.McpsHead
        mcps_head.mode = packmode
        mcps_head.id = self.mcpsPackId
        # 最大长度判断
        if len(data) < datalen:
            datalen = len(data)
        if datalen > self.DataArrayType_MCPS:
            mcps_head.amount = self.DataArrayType_MCPS
        else:
            mcps_head.amount = datalen
        datacut = data[:datalen]
        # 自动填充,使其满足4的倍数
        AddNum = datalen % 4
        if autofill and AddNum != 0:
            for j in range(AddNum):
                if(datalen+j < self.DataArrayType_MCPS): 
                    datacut = datacut + bytes([0x00])
                else:
                    break
        # print("mcps_head:",list(mcps_head.head))
        # print("mcps_mode:",mcps_head.mode)
        # print("mcps_id:",mcps_head.id)
        # print("mcp_amount:",mcps_head.amount)
        # print("mcps_data:",list(self.mcps_instance.data))  # 转换为列表以打印所有元素
        data_to_send_MCPS = bytes(mcps_head)
        data_to_send_MCPS = data_to_send_MCPS + datacut
        return data_to_send_MCPS
    
    def GetMcpsPacketId(self)->int:
        return  self.mcpsPackId
    
    def UnPackMlme(self, MlmeMsg:bytes)->MLME_Def:
        if(len(MlmeMsg) != self.MlmeStructSize):
            return None
        else:
            # 手动构建结构体实例
            head = (c_ubyte * 2)(*MlmeMsg[:2])  # 取前两个字节构建head
            cmd = MlmeMsg[2]  # 第三个字节是cmd
            amount = MlmeMsg[3]  # 第四个字节是amount
            data = (c_ubyte * PACKET_MLME_DATA_VOLUME)(*MlmeMsg[4:])  # 剩下的字节构建data
             # 创建结构体实例并返回
            return MLME_Def(head=head, cmd=cmd, amount=amount, data=data)


    def UnPackMcps(self, McpsMsg:bytes)->MCPS_Def:
        print("UnPackMcps:",len(McpsMsg),sizeof(MCPS_Head_Def))
        if len(McpsMsg) <= sizeof(MCPS_Head_Def)+1:
            return None
        else:
            # 手动构建结构体实例
            head = (c_ubyte * 2)(*McpsMsg[:2])  # 取前两个字节构建head
            mode = McpsMsg[2]  # 第三个字节是 模式
            id = McpsMsg[3]  # 第四个字节是 id
            amount = (McpsMsg[5]<<8)|McpsMsg[4] # 第五六个字节是amount
            data = (c_ubyte * PACKET_MCPS_DATA_VOLUME)()
            mcpsdata = McpsMsg[6:]
            for i in range(len(mcpsdata)):
                data[i] = mcpsdata[i]  # 剩下的字节构建data
             # 创建结构体实例并返回
            return MCPS_Def(head=head, mode=mode, id = id, amount=amount, data=data)

    def GetMsduType(self, MsduMsg:bytes)->MsduType:
        res = MsduType.InvalMsduType
        Msdulen = len(MsduMsg)
        if Msdulen < 3:
            print("UnPackMsdu net data len < 3")
            return res
        # 解析数据
        if  self.McpsHead[0] == MsduMsg[0] and self.McpsHead[1] == MsduMsg[1]:
            if Msdulen < sizeof(MCPS_Head_Def):
                print("UnPackMlme net data len < MCPS_Head_Def")
            else:
                res = MsduType.McpsType
        elif self.MlmeHead[0] == MsduMsg[0] and self.MlmeHead[1] == MsduMsg[1]:
            if Msdulen < sizeof(MLME_Head_Def):
                print("UnPackMlme net data len < MLME_Head_Def")
            else:
                res = MsduType.MlmeType
        return res