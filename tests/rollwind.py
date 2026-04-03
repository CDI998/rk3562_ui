import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, 
                             QVBoxLayout, QTextEdit, QFrame)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import (QPixmap, QFont, QPalette, QColor)

class TouchSlideTestWindow(QWidget):
    # 定义滑动信号
    slideUp = pyqtSignal()
    slideDown = pyqtSignal()

    def __init__(self):
        super().__init__()
        # 初始化所有属性（避免属性未定义）
        self.log_edit = None
        self.img_label = None
        self.current_img_idx = 0
        self.slide_start_pos = QPoint()
        self.slide_threshold = 30

        # 基础窗口配置
        self.setWindowTitle("触屏滑动测试界面")
        self.setFixedSize(480, 600)
        self.setStyleSheet("background-color: #f0f0f0;")

        # 图片路径配置（替换为你的绝对路径）
        self.img_base_path = "./"
        self.img_paths = [
            os.path.join(self.img_base_path, "img1_close.png"),
            os.path.join(self.img_base_path, "img2_max.png"),
            os.path.join(self.img_base_path, "img3_min.png")
        ]

        # 严格按顺序初始化：UI → 信号绑定 → 加载图片
        self._init_ui()          # 第一步：初始化所有UI组件
        self._bind_signals()     # 第二步：绑定信号槽
        self._load_current_image()  # 第三步：加载图片（此时log_edit已存在）

    def _init_ui(self):
        """初始化所有UI组件（确保log_edit先被创建）"""
        # 1. 标题标签
        title_label = QLabel("触屏上下滑动测试")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(50)

        # 2. 图片显示Label（核心滑动区域）
        self.img_label = QLabel()
        self.img_label.setFixedSize(400, 400)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.img_label.setStyleSheet("border-width: 2px; border-color: #cccccc;")

        # 3. 日志显示框（先初始化，避免后续调用报错）
        self.log_edit = QTextEdit()
        self.log_edit.setFixedHeight(100)
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("Consolas", 10))
        palette = self.log_edit.palette()
        palette.setColor(QPalette.Base, QColor(245, 245, 245))
        palette.setColor(QPalette.Text, QColor(50, 50, 50))
        self.log_edit.setPalette(palette)
        self.log_edit.append("测试提示：在图片区域上下滑动（触屏/鼠标拖拽）")

        # 4. 整体布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.img_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.log_edit)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

    def _bind_signals(self):
        """绑定滑动信号到槽函数"""
        self.slideUp.connect(self._on_slide_up)
        self.slideDown.connect(self._on_slide_down)

    def _load_current_image(self):
        """加载当前索引的图片（此时log_edit已初始化）"""
        img_path = self.img_paths[self.current_img_idx]
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.img_label.width(), self.img_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.img_label.setPixmap(scaled_pixmap)
            self.log_edit.append(f"✅ 加载图片：{os.path.basename(img_path)}")
        else:
            self.img_label.setText(f"图片加载失败\n{os.path.basename(img_path)}")
            self.log_edit.append(f"❌ 加载失败：{os.path.basename(img_path)}")

    # ========== 滑动事件处理（兼容触屏/鼠标） ==========
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.slide_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            end_pos = event.pos()
            y_offset = end_pos.y() - self.slide_start_pos.y()
            
            if abs(y_offset) > self.slide_threshold:
                if y_offset < 0:
                    self.slideUp.emit()
                else:
                    self.slideDown.emit()
        super().mouseReleaseEvent(event)

    # ========== 滑动槽函数 ==========
    def _on_slide_up(self):
        self.current_img_idx = (self.current_img_idx - 1) % len(self.img_paths)
        self.log_edit.append(f"🔼 上滑 → 切换到第{self.current_img_idx+1}张图")
        self._load_current_image()

    def _on_slide_down(self):
        self.current_img_idx = (self.current_img_idx + 1) % len(self.img_paths)
        self.log_edit.append(f"🔽 下滑 → 切换到第{self.current_img_idx+1}张图")
        self._load_current_image()

if __name__ == "__main__":
    # 启用高DPI适配
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    test_win = TouchSlideTestWindow()
    test_win.show()
    sys.exit(app.exec_())