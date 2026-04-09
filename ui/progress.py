from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSlider


class Progress:
    @staticmethod
    def init(slider: QSlider, label: QLabel):
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(0)
        label.setText("当前进度0.0%")
        slider.setFocusPolicy(Qt.NoFocus)
        slider.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        slider.setMouseTracking(False)

    @staticmethod
    def set(slider: QSlider, label: QLabel, value: float):
        progress = max(0.0, min(100.0, float(value)))
        slider.setValue(int(round(progress)))
        label.setText(f"当前进度{progress:.1f}%")

    @staticmethod
    def get(slider: QSlider) -> float:
        return float(slider.value())


# from ui.progress import Progress

# Progress.init(self.low1set, self.xxxLabel)
# Progress.set(self.low1set, self.xxxLabel, 36.5)
# value = Progress.get(self.low1set)
