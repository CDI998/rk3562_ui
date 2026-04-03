import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import QSize, Qt

class SimpleImageListView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 窗口基础设置
        self.setWindowTitle('极简版 图片ListView')
        self.setGeometry(100, 100, 400, 300)

        # 中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 1. 创建ListView
        self.list_view = QListView()
        self.list_view.setIconSize(QSize(40, 40))  # 图片大小

        # 2. 创建数据模型
        self.model = QStandardItemModel()

        # 3. 配置图片路径（重点：Windows路径处理）
        # 方式1：使用原始字符串（推荐，避免转义问题）
        img_path = r"D:\CDI\KF\ElectronicBlocks\LinuxUi\UI_Tx\tests\applogo_send.png"
        # 方式2：用双反斜杠（等价写法）
        # img_path = "D:\\CDI\\KF\\ElectronicBlocks\\LinuxUi\\UI_Tx\\tests\\applogo_send.png"

        # 打印校验信息（方便排查）
        print(f"图片路径：{img_path}")
        print(f"路径是否存在：{os.path.exists(img_path)}")
        print(f"当前工作目录：{os.getcwd()}")

        # 测试数据
        test_data = [
            ("苹果", img_path),
            ("香蕉", img_path),
            ("橙子", img_path)
        ]

        # 4. 添加带图片的列表项
        for text, img_path in test_data:
            item = QStandardItem()
            item.setText(text)          
            # 校验图片是否存在，不存在则用占位图标
            if os.path.exists(img_path):
                item.setIcon(QIcon(img_path))
            else:
                item.setIcon(QIcon.fromTheme("image"))  # 占位图标
                print(f"警告：图片文件不存在 → {img_path}")
            self.model.appendRow(item)  

        # 5. 绑定模型到ListView
        self.list_view.setModel(self.model)

        # 6. 添加到布局
        layout.addWidget(self.list_view)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleImageListView()
    window.show()
    sys.exit(app.exec_())