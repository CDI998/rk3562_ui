
class TxtDataBean:
    def __init__(self):
        self.input_data = "" # 用户输入的文本数据

    # ---------------------
    # 文本 接口
    # ---------------------
    def set_text(self, text):
        self.input_data = text

    def get_text(self):
        return self.input_data
