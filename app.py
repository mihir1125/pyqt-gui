import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from model_processing import format_frames
from enum import Enum
import random

import cv2

def processBatch(dummy):
    return random.choice([
        [[-17, 0]],
        [[-15, 0]],
    ]
    )

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel()
        self.FeedLabel.setStyleSheet(f"border: 10px solid {Status.NORMAL.value}")
        self.VBL.addWidget(self.FeedLabel)

        self.StopBTN = QPushButton("Stop")
        self.VBL.addWidget(self.StopBTN)
        self.StopBTN.clicked.connect(self.stopFeed)

        self.cameraFeedWorker = CameraFeedWorker()
        self.cameraFeedWorker.BatchReady.connect(self.getModelResult)
        self.cameraFeedWorker.ImageUpdate.connect(self.imageUpdateSlot)
        self.cameraFeedWorker.start()

        self.setLayout(self.VBL)

    def imageUpdateSlot(self, image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(image))
        
    def getModelResult(self, batch):
        result = processBatch(batch)
        if result[0][0] > -16:
            self.FeedLabel.setStyleSheet(f"border: 10px solid {Status.ANOMALY.value}")
        else:
            self.FeedLabel.setStyleSheet(f"border: 10px solid {Status.NORMAL.value}")
        print(result)

    def stopFeed(self):
        self.cameraFeedWorker.stop()


class CameraFeedWorker(QThread):
    ImageUpdate = pyqtSignal(QImage)
    BatchReady = pyqtSignal(list)
    def run(self):
        self.ThreadActive = True
        # capture = cv2.VideoCapture("http://192.168.31.191:4747/video")
        # capture = cv2.VideoCapture("http://192.168.221.80:4747/video")
        capture = cv2.VideoCapture("Robbery014_x264.mp4")
        batch_size = 120
        output_size = (224, 224)
        count = 0
        batch = []
        while self.ThreadActive and capture.isOpened():            
            ret, frame = capture.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ConvertToQtImage = QImage(
                    image.data,
                    image.shape[1],
                    image.shape[0],
                    QImage.Format.Format_RGB888,
                )
                pic = ConvertToQtImage.scaled(
                    640, 480, Qt.AspectRatioMode.KeepAspectRatio
                )
                self.ImageUpdate.emit(pic)
                
                # Creating batches
                if count < batch_size:
                    batch.append(format_frames(frame, output_size))
                    count += 1
                else:
                    count = 0
                    self.BatchReady.emit(batch)
                    batch = []
                
            else:
                print("Failed to capture frame")
                break

    def stop(self):
        self.ThreadActive = False
        self.quit()

class Status(Enum):
    NORMAL = "#02B875"
    ANOMALY = "#DB3535"

if __name__ == "__main__":
    app = QApplication([])
    rootWindow = MainWindow()
    rootWindow.show()
    sys.exit(app.exec())
