'''
 编码转换工具
 字符串转进制流
'''

class bintool():
    def __init__(self):
        self.StartBit = 1
        self.DataBit = 8
        self.CheckBit = 1
        self.StopBit = 1

    def DataToPhyBinList(self, data:str, dataLen:int)->list:
        """
        将字符串数据转换为物理层二进制字符串列表。
        Args:
            data (str): 待转换的字符串数据。
            dataLen (int): 数据长度，即字符串data中字符的个数。
        Returns:
            list: 包含转换后的物理层二进制字符串的列表，每个字符串格式为"0[8位二进制数据][奇偶校验位]1"。
        """
        BinList = []
        BinStr = ""
        ParityStr = ""
        for i in range(dataLen):
           BinStr = self.ByteStrToBinStr(data[i])
           ParityStr = self.genChecksum(data[i])
           BinList.append("0" + BinStr + ParityStr + "1")
        return BinList
    
    def BinListToHtmlStr(self, lines:list, linenum:int, listnum:int)->str:
        """
        将给定的文本行列表转换为带有颜色标记的HTML字符串。
        Args:
            lines (list): 包含文本行的列表。
            linenum (int): 文本行的编号（此参数在函数内部未使用，可忽略）。
            listnum (int): 文本列表的编号（此参数在函数内部未使用，可忽略）。
        Returns:
            str: 包含颜色标记的HTML字符串，其中前ByteNum个字节（包含）以绿色显示，
                 ByteNum个字节之后（如果有的话）以灰色显示，其余行（如果有的话）也以灰色显示。
                 行与行之间用<br>标签代替\n来换行。
        Raises:
            无。
        Note:
            此函数未使用linenum和listnum参数，这两个参数可能是用于其他目的或遗留代码。
        """
        colored_lines = []
        i = 0
        for line in lines:
            if not line.strip(): # 只有空白字符，不做操作
                colored_lines.append(line)
                continue
            if(i < linenum):
                colored_line = f'<span style="color: green;">{line}</span>'
            elif(i == linenum):
                # 如果还有剩余的字符，将它们添加为灰色
                colored_line = f'<span style="color: #00ff00;">{line[:listnum]}</span>'
                colored_line += f'<span style="color: gray;">{line[listnum:]}</span>'
            else:
                colored_line = f'<span style="color: gray;">{line}</span>'
            colored_lines.append(colored_line)    
            i = i + 1
        # 使用<br>标签代替\n来换行
        return '<br>'.join(colored_lines)
    
    def TxtStrToHtmlStr(self, TxtStr:str, GreenIdx:int, ClorEnableFlag:bool= True)->str:
        HtmlStr = ""
        if ClorEnableFlag == False:
            HtmlStr += f'<span style="color: gray;">{TxtStr}</span>'
        else:
            for index, char in enumerate(TxtStr):
                if index < GreenIdx:
                    HtmlStr += f'<span style="color: green;">{char}</span>'
                elif index == GreenIdx:
                    HtmlStr += f'<span style="color: #00ff00;">{char}</span>'
                else:
                    HtmlStr += f'<span style="color: gray;">{char}</span>'
        return HtmlStr

    def genChecksum(self, Strbyte)->str:
        """
        计算并返回给定字节的偶校验位。
        Args:
            Strbyte (str): 要计算偶校验位的单个字符字节，必须是单字节长度的字符串。
        Returns:
            str: 奇偶校验位的结果，为'0'或'1'的字符串形式。
        Raises:
            无特定异常抛出，但如果输入的Strbyte不是单字节长度的字符串，则结果可能不准确。
        """
        byte = ord(Strbyte)
        parity = 0
        while byte:
            parity ^= byte & 1
            byte >>= 1
        return str(parity)

    def ByteStrToBinStr(self, bytestr)->str:
        """
        将字节转换为二进制字符串。
        Args:
            byte (bytes): 一个字节的输入值。
        Returns:
            str: 转换后的8位二进制字符串。
        """
        int_value = ord(bytestr)
        binstr = format(int_value, '08b')
        return binstr
    
    def BytesToBinStr(self, byte_data:bytes)->str:
        return ''.join(format(byte, '08b') for byte in byte_data)

    def HtmlTxtCenter(self, HtmlTxt: str):
        return f'<div style="text-align: center; line-height: 0.82;">{HtmlTxt}</div>'
# if __name__ == '__main__':
#     mybintool = bintool()
#     # 示例
#     byte_data = b'\x01\x0f\xff'
#     binary_string = mybintool.BytesToBinStr(byte_data)
#     print(binary_string)  
            

