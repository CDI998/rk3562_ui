import sys
from enum import Enum

# 1. 枚举优化：命名规范 + 语义修正
class SystemState(Enum):
    """系统状态枚举类（替代原 State）"""
    TXT_MODE = 1       # 文本
    PIC_MODE = 2       # 图片
    VDO_MODE = 3       # 视频
    INVALID_MODE = 4   # 非法

class SystemManager:
    """系统状态管理类"""

    def __init__(self, sys_state: SystemState = SystemState.INVALID_MODE):
        """
        初始化系统管理器实例

        Args:
            sys_state: 系统状态，默认为 INVALID_MODE（无效状态）
        """
        if not isinstance(sys_state, SystemState):
            print(f"错误：系统状态必须是 SystemState 枚举类型，当前传入：{type(sys_state)}（值：{sys_state}）")
        else:
            self._sys_state = SystemState.INVALID_MODE   

    def sys_state(self) -> SystemState:
        """获取当前系统状态"""
        return self._sys_state


    def sys_state(self, new_state: SystemState) -> None:
        """设置系统状态"""
        # 关键优化：校验传入的状态是否合法（必须是 SystemState 枚举成员）
        if not isinstance(new_state, SystemState):
            print(f"错误：系统状态必须是 SystemState 枚举类型，当前传入：{type(new_state)}（值：{new_state}）")
        else:
            self._sys_state = new_state

