import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal, Qt

import cv2


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        self.StopBTN = QPushButton("Stop")
        self.VBL.addWidget(self.StopBTN)
        self.StopBTN.clicked.connect(self.stopFeed)

        self.cameraFeedWorker = CameraFeedWorker()
        self.cameraFeedWorker.ImageUpdate.connect(self.imageUpdateSlot)
        self.cameraFeedWorker.start()

        self.setLayout(self.VBL)

    def imageUpdateSlot(self, image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(image))

    def stopFeed(self):
        self.cameraFeedWorker.stop()


class CameraFeedWorker(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def run(self):
        self.ThreadActive = True
        capture = cv2.VideoCapture(0)
        while self.ThreadActive:
            ret, frame = capture.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                flippedImage = cv2.flip(image, 1)
                ConvertToQtImage = QImage(
                    flippedImage.data,
                    flippedImage.shape[1],
                    flippedImage.shape[0],
                    QImage.Format.Format_RGB888,
                )
                pic = ConvertToQtImage.scaled(
                    640, 480, Qt.AspectRatioMode.KeepAspectRatio
                )
                self.ImageUpdate.emit(pic)
            else:
                print("Failed to capture frame")
                break

    def stop(self):
        self.ThreadActive = False
        self.quit()


class NotificationWorker(QThread):
    AnomalyDetected = pyqtSignal()


if __name__ == "__main__":
    app = QApplication([])
    rootWindow = MainWindow()
    rootWindow.show()
    sys.exit(app.exec())
