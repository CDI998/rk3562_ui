from enum import Enum

class StepLowMode(Enum):
    InputingStep = 1
    SendingStep = 2
    ResultsStep = 3
    InvalStep = 4

class UserActionManage():
    def __init__(self):
        self._mode_step = StepLowMode.InvalStep
    
    @property
    def mode_step(self)->StepLowMode:
        return self._mode_step
    
    @mode_step.setter
    def mode_step(self, newstep:StepLowMode)->bool:
        if not isinstance(newstep, StepLowMode):
            print(f"步骤必须是 StepLowMode 枚举类型！当前传入：{type(new_step)}（值：{new_step}）")
            return False
        self._mode_step = newstep
        return True
