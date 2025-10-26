import sys
import os

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QLabel, QWidget, QGraphicsBlurEffect
import cv2
import numpy as np
import mediapipe as mp

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

        # Load cursed meme images
        self.meme_images = []
        meme_paths = ['assets/grass-meme1.jpg', 'assets/grass-meme2.jpg',
                      'assets/grass-meme3.jpg', 'assets/leaf.jpg',
                      'assets/warning-text.jpg']
        for path in meme_paths:
            img = cv2.imread(path)
            if img is not None:
                # Resize to reasonable size (300x300)
                img = cv2.resize(img, (300, 300))
                self.meme_images.append(img)
            else:
                print(f"Warning: Could not load {path}")

        print(f"Loaded {len(self.meme_images)} meme images")

        # Animation state for cursed effects
        self.frame_count = 0
        self.meme_positions = []
        self.meme_rotations = []
        self.meme_scales = []
        self.meme_opacities = []

        # Initialize random properties for each meme
        import random
        for i in range(len(self.meme_images)):
            self.meme_positions.append([
                random.randint(100, screen_width - 400),
                random.randint(100, screen_height - 400)
            ])
            self.meme_rotations.append(random.uniform(0, 360))
            self.meme_scales.append(random.uniform(0.5, 1.5))
            self.meme_opacities.append(1.0)

        # ctypes.windll is Windows-only, removed for macOS compatibility
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 33fps for smooth video

    def reset(self):
        self.value = 0
        self.contact_frames = 0
        self.last_contact = False
        self.frame_count = 0
        # Reset meme animations
        import random
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        for i in range(len(self.meme_images)):
            self.meme_positions[i] = [
                random.randint(100, screen_width - 400),
                random.randint(100, screen_height - 400)
            ]
            self.meme_rotations[i] = random.uniform(0, 360)
            self.meme_scales[i] = random.uniform(0.5, 1.5)
            self.meme_opacities[i] = 1.0
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

        # cursed animated memes if progress bar is below 5%
        import random
        import math
        if self.value < 5:
            self.frame_count += 1
            for i, meme_img in enumerate(self.meme_images):
                # cursed movement patterns
                time = self.frame_count * 0.05

                # aggressive spinning
                self.meme_rotations[i] += random.uniform(-15, 15)

                # chaotic movement - blast around the screen!
                self.meme_positions[i][0] += math.sin(time + i) * random.uniform(10, 30)
                self.meme_positions[i][1] += math.cos(time * 1.3 + i) * random.uniform(10, 30)

                # random teleportation occasionally
                if random.random() < 0.02:
                    h, w = final_frame.shape[:2]
                    self.meme_positions[i][0] = random.randint(0, max(1, w - 300))
                    self.meme_positions[i][1] = random.randint(0, max(1, h - 300))

                # keep in bounds (with wraparound)
                h, w = final_frame.shape[:2]
                self.meme_positions[i][0] = self.meme_positions[i][0] % max(1, w - 300)
                self.meme_positions[i][1] = self.meme_positions[i][1] % max(1, h - 300)

                # pulsing scale - more extreme
                self.meme_scales[i] = 0.5 + 0.8 * abs(math.sin(time * 3 + i))

                # aggressive blinking
                if random.random() < 0.1:  # More frequent blinks
                    self.meme_opacities[i] = random.uniform(0.2, 1.0)
                else:
                    self.meme_opacities[i] = min(1.0, self.meme_opacities[i] + 0.1)

                # create a larger canvas that can fit the rotated image
                canvas_size = 450  # Larger than 300 to accommodate rotation
                canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

                # get the region from video frame to use as background
                x, y = int(self.meme_positions[i][0]), int(self.meme_positions[i][1])
                x = max(0, min(final_frame.shape[1] - canvas_size, x))
                y = max(0, min(final_frame.shape[0] - canvas_size, y))

                # extract background from video frame
                bg_roi = final_frame[y:y+canvas_size, x:x+canvas_size].copy()
                if bg_roi.shape[:2] == (canvas_size, canvas_size):
                    canvas = bg_roi

                # place meme image in center of canvas
                offset = (canvas_size - 300) // 2
                canvas[offset:offset+300, offset:offset+300] = meme_img

                # rotate the canvas
                M = cv2.getRotationMatrix2D((canvas_size/2, canvas_size/2), self.meme_rotations[i], self.meme_scales[i])
                rotated_canvas = cv2.warpAffine(canvas, M, (canvas_size, canvas_size))

                # create mask for non-background pixels (detect the meme vs background)
                # convert to grayscale and threshold to find the meme
                gray_meme = cv2.cvtColor(meme_img, cv2.COLOR_BGR2GRAY)
                _, mask_original = cv2.threshold(gray_meme, 10, 255, cv2.THRESH_BINARY)

                # place mask in center and rotate it
                mask_canvas = np.zeros((canvas_size, canvas_size), dtype=np.uint8)
                mask_canvas[offset:offset+300, offset:offset+300] = mask_original
                rotated_mask = cv2.warpAffine(mask_canvas, M, (canvas_size, canvas_size))

                # overlay with opacity using mask
                alpha = self.meme_opacities[i] * 0.8

                # blend rotated meme onto frame using the mask
                try:
                    y_end = min(y + canvas_size, final_frame.shape[0])
                    x_end = min(x + canvas_size, final_frame.shape[1])
                    canvas_h = y_end - y
                    canvas_w = x_end - x

                    if canvas_h > 0 and canvas_w > 0:
                        roi = final_frame[y:y_end, x:x_end]
                        canvas_crop = rotated_canvas[:canvas_h, :canvas_w]
                        mask_crop = rotated_mask[:canvas_h, :canvas_w]

                        if roi.shape == canvas_crop.shape:
                            # Only blend where mask is active
                            mask_3ch = cv2.cvtColor(mask_crop, cv2.COLOR_GRAY2BGR) / 255.0
                            blended = roi * (1 - mask_3ch * alpha) + canvas_crop * (mask_3ch * alpha)
                            final_frame[y:y_end, x:x_end] = blended.astype(np.uint8)
                except Exception as e:
                    pass

        # draw contact status text (positioned on the right side, lower on screen)
        x_offset = 1200
        y_offset = 700
        contact_count = 0
        for part_name, in_contact in contact_status.items():
            if in_contact:
                contact_count += 1
            status_text = f"{part_name}: {'CONTACT' if in_contact else 'no contact'}"
            color = (0, 255, 0) if in_contact else (150, 150, 150)
            cv2.putText(final_frame, status_text, (x_offset, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 30

        # draw contact percentage
        total_parts = max(len(contact_status), 1)
        contacting_parts = sum(
            1 for contact in contact_status.values() if contact)
        contact_percentage = (contacting_parts / total_parts) * 100
        percentage_text = f"Contact: {contact_percentage:.0f}%"
        cv2.putText(final_frame, percentage_text, (x_offset, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)


        # track contact duration
        if contact_count > 0:
            self.contact_frames += 1
        else:
            self.contact_frames = 0

        # update progress bar based on contact (smooth incremental progress)
        if self.contact_frames >= self.required_contact_frames:
            progress_increment = 0.3 + (contact_count - 1) * 1.1
            self.value += progress_increment
            self.progressBar.setValue(int(self.value))

            if self.value >= 100:
                self.timer.stop()
                self.hide()
                self.releaseMouse()
                self.main_window.setWindowState(Qt.WindowNoState)
                self.main_window.showNormal()
                self.main_window.activateWindow()
                self.main_window.raise_()
                self.main_window.reset()

        # convert to Qt format and display
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

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # window opacity for slight transparency
        self.setWindowOpacity(0.95)

        self.progress = self.findChild(QProgressBar, "progressBar")
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(100)

        # custom borders - top and sides only, no bottom
        self.centralWidget().setStyleSheet("""
            QWidget#centralwidget {
                background-color: rgba(25, 35, 25, 220);
                border-top: 2px solid rgba(100, 150, 100, 150);
                border-left: 2px solid rgba(100, 150, 100, 150);
                border-right: 2px solid rgba(100, 150, 100, 150);
                border-bottom: none;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.value = 100
        self.timer.start(200) # TIMER INTERVAL

        self.camera_widget = CameraWidget(self)

    def reset(self):
        self.value = 100
        self.progress.setValue(self.value)
        self.setWindowState(Qt.WindowNoState)
        self.resize(600, 220)
        self.timer.start(200) # TIMER INTERVAL

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