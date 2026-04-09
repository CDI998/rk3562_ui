from enum import Enum

class UserActionStep(Enum):
    InputingStep = 1 # 输入步骤，用户正在输入数据
    SendingStep  = 2 # 发送步骤，用户正在发送数据，等待响应
    InvalStep    = 3 # 无效步骤，未定义或错误的步骤

class UserActionManage():
    def __init__(self):
        self._mode_step = UserActionStep.InvalStep
    
    @property
    def mode_step(self)->UserActionStep:
        return self._mode_step
    
    @mode_step.setter
    def mode_step(self, newstep:UserActionStep)->bool:
        if not isinstance(newstep, UserActionStep):
            print(f"步骤必须是 UserActionStep 枚举类型！当前传入：{type(new_step)}（值：{new_step}）")
            return False
        self._mode_step = newstep
        return True
