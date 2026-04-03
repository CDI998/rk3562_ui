import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QPoint

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("所有组件上下滑动共用一个槽函数")
        self.setFixedSize(800, 500)

        # ========== 1. 初始化你的组件（和你现有结构一致） ==========
        self.midtxts = {}
        self.higtxts = {}
        
        # 组件1：step1pic
        self.mid1pic = QLabel("step1pic 组件\n（上下滑动我）")
        self.mid1pic.setFixedSize(350, 400)
        self.mid1pic.setStyleSheet("border:2px solid green; background:#e8f5e9;")
        self.mid1pic.setAlignment(Qt.AlignCenter)
        self.midtxts['step1pic'] = self.mid1pic
        
        # 组件2：step1vdo
        self.hig1vdo = QLabel("step1vdo 组件\n（上下滑动我）")
        self.hig1vdo.setFixedSize(350, 400)
        self.hig1vdo.setStyleSheet("border:2px solid blue; background:#e3f2fd;")
        self.hig1vdo.setAlignment(Qt.AlignCenter)
        self.higtxts['step1vdo'] = self.hig1vdo

        # ========== 2. 滑动配置 ==========
        self.slide_threshold = 30  # 滑动触发阈值
        self.slide_start_y = 0     # 通用滑动起点Y轴
        self.current_widget = None # 记录当前滑动的组件

        # ========== 3. 绑定所有组件的滑动事件到通用处理函数 ==========
        # step1pic绑定
        self.midtxts['step1pic'].mousePressEvent = lambda e: self.on_widget_press(e, 'step1pic')
        self.midtxts['step1pic'].mouseReleaseEvent = self.on_widget_release
        
        # step1vdo绑定
        self.higtxts['step1vdo'].mousePressEvent = lambda e: self.on_widget_press(e, 'step1vdo')
        self.higtxts['step1vdo'].mouseReleaseEvent = self.on_widget_release

        # ========== 4. 布局 ==========
        layout = QHBoxLayout()
        layout.addWidget(self.mid1pic)
        layout.addWidget(self.hig1vdo)
        layout.setSpacing(50)
        self.setLayout(layout)

    # ========== 通用滑动按下事件（记录组件和起点） ==========
    def on_widget_press(self, event, widget_name):
        if event.button() == Qt.LeftButton:
            self.current_widget = widget_name  # 记录当前滑动的组件名
            self.slide_start_y = event.y()     # 记录Y轴起点

    # ========== 通用滑动释放事件（判断方向，调用共用槽函数） ==========
    def on_widget_release(self, event):
        if event.button() == Qt.LeftButton and self.current_widget:
            y_offset = event.y() - self.slide_start_y
            # 判断滑动方向并调用共用槽函数
            if abs(y_offset) > self.slide_threshold:
                slide_dir = "up" if y_offset < 0 else "down"
                self.on_slide_common(self.current_widget, slide_dir)
            # 重置当前组件
            self.current_widget = None

    # ========== 所有组件共用的滑动槽函数（核心逻辑） ==========
    def on_slide_common(self, widget_name, slide_dir):
        """
        共用槽函数
        :param widget_name: 滑动的组件名（step1pic/step1vdo）
        :param slide_dir: 滑动方向（up/down）
        """
        # ========== 你只需要在这里写业务逻辑 ==========
        if widget_name == "step1pic":
            if slide_dir == "up":
                print(f"✅ {widget_name} 上滑 → 执行图片上滑逻辑（如切换图片）")
                self.midtxts[widget_name].setText(f"{widget_name}\n上滑触发！")
            else:
                print(f"✅ {widget_name} 下滑 → 执行图片下滑逻辑（如缩小图片）")
                self.midtxts[widget_name].setText(f"{widget_name}\n下滑触发！")
        
        elif widget_name == "step1vdo":
            if slide_dir == "up":
                print(f"✅ {widget_name} 上滑 → 执行视频上滑逻辑（如音量+）")
                self.higtxts[widget_name].setText(f"{widget_name}\n上滑触发！")
            else:
                print(f"✅ {widget_name} 下滑 → 执行视频下滑逻辑（如音量-）")
                self.higtxts[widget_name].setText(f"{widget_name}\n下滑触发！")

# 运行程序
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())