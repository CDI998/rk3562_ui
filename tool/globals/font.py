from PyQt5.QtWidgets import  QWidget
from PyQt5.QtGui import QFont

class systemfont():
    @staticmethod
    def set_font_for_all_widgets(parent: QWidget, desired_font_family: str) -> None:
        """
        遍历 parent 及其所有子组件，设置具有 font 方法的组件的字体家族。
        
        :param parent: 父组件，用于遍历所有子组件
        :param desired_font_family: 目标字体家族名称，字符串类型
        """
        # 遍历 parent 下的所有子组件
        for widget in parent.findChildren(QWidget):
            # 检查 widget 是否有 font 方法
            if hasattr(widget, 'font'):
                # 获取当前字体
                current_font = widget.font()
                # 检查当前字体家族
                if current_font.family() != desired_font_family:
                    # 创建新的字体对象并设置
                    new_font = QFont(desired_font_family, current_font.pointSize())
                    widget.setFont(new_font)
    @staticmethod
    def check_and_set_font(widget: QWidget, desired_font_family: str) -> None:
        # 检查 widget 是否有 font 方法
        if hasattr(widget, 'font'):
            # 获取当前字体
            current_font = widget.font()
            # 检查当前字体家族
            if current_font.family() != desired_font_family:
                # 创建新的字体对象并设置
                new_font = QFont(desired_font_family, current_font.pointSize())
                widget.setFont(new_font)
        else:
            print(f"{widget.__class__.__name__} does not support font method")