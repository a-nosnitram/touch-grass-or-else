import sys
import os

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QLabel, QWidget
import cv2
import mediapipe as mp

# Add parent directory to path to import vision modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import vision.grass_detection as grass_detection
import vision.body_tracker as body_tracker

# MediaPipe
mp_holistic = mp.solutions.holistic

class CameraWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        uic.loadUi('data/camera_alert.ui', self)
        self.setWindowIcon(QIcon('data/grass.png'))
        self.setWindowTitle("GRASS ALERT")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.grabMouse()

        self.main_window = main_window

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

        self.cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

        # MediaPipe holistic model
        self.holistic = mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Track contact time for progress
        self.contact_frames = 0
        self.required_contact_frames = 10  # 10 frames = 0.33 seconds
        self.last_contact = False  # Track contact state change

        # ctypes.windll is Windows-only, removed for macOS compatibility
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 33fps for smooth video

    def reset(self):
        self.value = 0
        self.contact_frames = 0
        self.last_contact = False
        self.timer.start()

    def update_frame(self):
        ret, frame_orig = self.cap.read()
        if not ret:
            return

        # flip mirror
        frame = cv2.flip(frame_orig, 1)

        # detect grass
        _, grass_mask = grass_detection.detect_grass(frame)

        # track body and detect contact
        body_result, contact_status = body_tracker.body_tracker(
            frame, grass_mask, self.holistic
        )

        # blend grass overlay
        overlay = body_result.copy()
        overlay[grass_mask > 0] = [0, 255, 0]
        final_frame = cv2.addWeighted(body_result, 0.85, overlay, 0.15, 0)

        # draw contact status text
        y_offset = 30
        contact_count = 0  # Count how many body parts are touching
        for part_name, in_contact in contact_status.items():
            if in_contact:
                contact_count += 1
            status_text = f"{part_name}: {'CONTACT' if in_contact else 'no contact'}"
            color = (0, 255, 0) if in_contact else (150, 150, 150)
            cv2.putText(final_frame, status_text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_offset += 25

        # draw contact percentage
        total_parts = max(len(contact_status), 1)
        contacting_parts = sum(
            1 for contact in contact_status.values() if contact)
        contact_percentage = (contacting_parts / total_parts) * 100
        percentage_text = f"Contact Percentage: {contact_percentage:.1f}%"
        cv2.putText(final_frame, percentage_text, (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)


        # Track contact duration
        if contact_count > 0:
            self.contact_frames += 1
        else:
            self.contact_frames = 0

        # Update progress bar based on contact (smooth incremental progress)
        if self.contact_frames >= self.required_contact_frames:
            # Sustained contact - increment based on number of contact points
            # Base speed: 2 points per frame
            # Bonus: +1.5 per additional contact point
            progress_increment = 2 + (contact_count - 1) * 1.5
            self.value += progress_increment
            self.progressBar.setValue(int(self.value))

            if self.value >= 100:
                self.timer.stop()
                self.hide()
                self.releaseMouse()
                # Force exit fullscreen and return to normal window size
                self.main_window.setWindowState(Qt.WindowNoState)
                self.main_window.showNormal()
                self.main_window.activateWindow()
                self.main_window.raise_()
                self.main_window.reset()

        # Convert to Qt format and display
        frame_rgb = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_image)
        pixmap = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding)
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        # clean up MediaPipe when closing
        self.holistic.close()
        self.cap.release()
        super().closeEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('data/health_bar.ui', self)
        self.setWindowTitle("Touch Grass")
        self.setWindowIcon(QIcon("data/grass.png"))

        self.progress = self.findChild(QProgressBar, "progressBar")
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(100)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.value = 100
        self.timer.start(100) # TIMER INTERVAL

        self.camera_widget = CameraWidget(self)

    def reset(self):
        self.value = 100
        self.progress.setValue(self.value)
        # Explicitly ensure window is not fullscreen
        self.setWindowState(Qt.WindowNoState)
        # Set fixed size from the updated UI file dimensions (600x220)
        self.resize(600, 220)
        self.timer.start(100) # TIMER INTERVAL

    def update_progress(self):
        self.value -= 1
        self.progress.setValue(self.value)

        if self.value <= 0:
            self.timer.stop()
            self.hide()
            self.camera_widget.reset()
            self.camera_widget.showFullScreen()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())