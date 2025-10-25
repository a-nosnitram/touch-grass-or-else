import sys

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QLabel, QWidget
import cv2
from pynput.mouse import Button, Controller
import ctypes

class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('data/camera_alert.ui', self)
        self.setWindowTitle("GRASS ALERT")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.grabMouse()

        self.video_label = self.findChild(QLabel, "cameraLabel")
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        self.video_label.setGeometry(0, 0, screen_width, screen_height)

        self.progressBar = self.findChild(QProgressBar, "progressBar")
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.value = 0
        self.progressBar.setValue(self.value)
        self.progressBar.setGeometry(50, screen_height - 100, screen_width - 100, 30)


        self.cap = cv2.VideoCapture(0)

        ctypes.windll.user32.BlockInput(True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.timeout.connect(self.update_progress_bar)
        self.timer.start(500)


    def update_progress_bar(self):
        self.value += 1
        self.progressBar.setValue(self.value)

        if self.value >= 100:
            self.timer.stop()
            self.hide()
            ctypes.windll.user32.BlockInput(False)
            self.MainWindow.showFullScreen()
            self.releaseMouse()


    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(qt_image)
            pixmap = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding)
            self.video_label.setPixmap(pixmap)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Touch Grass")
        self.setWindowIcon(QIcon("grass.png"))
        uic.loadUi('data/health_bar.ui', self)

        self.progress = self.findChild(QProgressBar, "progressBar")
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(100)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.value = 100
        self.timer.start(10)

        self.camera_widget = CameraWidget()

    def update_progress(self):
        self.value -= 1
        self.progress.setValue(self.value)

        if self.value <= 0:
            self.timer.stop()
            self.hide()
            self.camera_widget.showFullScreen()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())