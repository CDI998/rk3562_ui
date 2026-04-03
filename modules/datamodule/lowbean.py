import copy

class LowDataBean:
    def __init__(self):
        self.input_data = ""  # 用户输入的数据
        self.bin_data = []    # 用户数据转换为的二进制数据
        self.bin_html_data = ""  # bin转换为的html数据
        self.send_html_data = ""  # 正在发送的html数据
        self.SendState = False  # 发送状态

    def SetInputData(self, data: str):
        """Set the input data, requires a string."""
        self.input_data = copy.deepcopy(data)

    def GetInputData(self) -> str:
        """Get the input data."""
        return copy.deepcopy(self.input_data)

    def SetBinData(self, data: list):
        """Set the binary data, requires a list."""
        self.bin_data = copy.deepcopy(data)

    def GetBinData(self) -> list:
        """Get the binary data."""
        return copy.deepcopy(self.bin_data)

    def SetBinHtmlData(self, data: str):
        """Set the binary HTML data, requires a string."""
        self.bin_html_data = copy.deepcopy(data)

    def GetBinHtmlData(self) -> str:
        """Get the binary HTML data."""
        return copy.deepcopy(self.bin_html_data)

    def SetSendHtmlData(self, data: str):
        """Set the sending HTML data, requires a string."""
        self.send_html_data = copy.deepcopy(data)

    def GetSendHtmlData(self) -> str:
        """Get the sending HTML data."""
        return copy.deepcopy(self.send_html_data)
    
    def SetSendState(self, IsSending: bool):
        self.SendState = IsSending

    def GetSendState(self) -> bool:
        return self.SendState
    
