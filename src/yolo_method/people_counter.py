import sys
import os
import cv2
import pandas as pd
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QLabel, QStackedWidget
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen

# Local imports
from tracker import Tracker
from video_stream import VideoStream
from ultralytics import YOLO

##############################################################################
# Model path adjustment
##############################################################################
model_str = "yolov8m.pt"
current_dir = os.path.dirname(os.path.abspath(__file__))

if hasattr(sys, '_MEIPASS'):
    model_path = os.path.join(sys._MEIPASS, model_str)
else:
    #If the model is located in ÿolo_models" inside "yolo_method" :
    model_path = os.path.join(current_dir, "yolo_models", model_str)

print("DEBUG: model_path =", model_path)


##############################################################################
# Class PeopleCounter (YOLO + Tracker + counting)
##############################################################################
class PeopleCounter:
    def __init__(self, model_path):
        self.model = YOLO(model_path, verbose=True)
        self.tracker = Tracker()

        # Dictionaries for counting
        self.people_entering = {}
        self.people_exiting = {}
        self.entering = set()
        self.exiting = set()

    def process_frame(self, frame, area1, area2):
        """
        Receives a frame (BGR), areas (area1, area2) and returns processed frame.
        """
        results = self.model.predict(frame, conf=0.5, classes=[0])
        if len(results) == 0:
            return frame
        boxes_data = results[0].boxes.data

        bbox_list = []
        bbox_df = pd.DataFrame(boxes_data).astype("float")
        for _, row in bbox_df.iterrows():
            x1, y1, x2, y2, _, label = map(int, row)
            if label == 0:
                bbox_list.append([x1, y1, x2, y2])

        # Updates tracker
        bbox_ids = self.tracker.update(bbox_list)

        # Draws polygons for ilustration
        for quad in area1:
            cv2.polylines(frame, [np.array(quad, np.int32)], True, (255, 0, 0), 2)
        for quad in area2:
            cv2.polylines(frame, [np.array(quad, np.int32)], True, (0, 255, 0), 2)

        # Verifies in/out 
        for bbox in bbox_ids:
            x3, y3, x4, y4, obj_id = bbox
            self.handle_entrance_exit(frame, x3, y3, x4, y4, obj_id, area1, area2)

        # Draws counting 
        self.display_count(frame)
        return frame

    def handle_entrance_exit(self, frame, x3, y3, x4, y4, obj_id, area1, area2):
        # Verifies area2 → people_entering
        for quad in area2:
            if cv2.pointPolygonTest(np.array(quad, np.int32), (x4, y4), False) >= 0:
                self.people_entering[obj_id] = (x4, y4)
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                cv2.putText(frame, str(obj_id), (x3, y3),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                break

        # If it is in people_entering, check if reaches area1
        if obj_id in self.people_entering:
            for quad in area1:
                if cv2.pointPolygonTest(np.array(quad, np.int32), (x4, y4), False) >= 0:
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                    cv2.circle(frame, (x4, y4), 5, (255, 0, 255), -1)
                    cv2.putText(frame, str(obj_id), (x3, y3),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    self.entering.add(obj_id)
                    break

        # Verifies area1 → people_exiting
        for quad in area1:
            if cv2.pointPolygonTest(np.array(quad, np.int32), (x4, y4), False) >= 0:
                self.people_exiting[obj_id] = (x4, y4)
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                cv2.putText(frame, str(obj_id), (x3, y3),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                break

        # If it is in people_exiting, check if reaches área2
        if obj_id in self.people_exiting:
            for quad in area2:
                if cv2.pointPolygonTest(np.array(quad, np.int32), (x4, y4), False) >= 0:
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                    cv2.circle(frame, (x4, y4), 5, (255, 0, 255), -1)
                    cv2.putText(frame, str(obj_id), (x3, y3),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    self.exiting.add(obj_id)
                    break

    def display_count(self, frame):
        people_in = len(self.entering)
        people_out = len(self.exiting)
        cv2.putText(frame, "Subindo:", (10,80),
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,0,255),2)
        cv2.putText(frame, str(people_in),(160,80),
                    cv2.FONT_HERSHEY_COMPLEX,0.7,(0,0,255),2)

        cv2.putText(frame, "Descendo:", (10,140),
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, (255,0,255),2)
        cv2.putText(frame, str(people_out),(160,140),
                    cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,255),2)


##############################################################################
# VideoWidget - drawing the static frame 
##############################################################################
class VideoWidget(QLabel):
    areas_done_signal = pyqtSignal()  # Emits when both areas (area1, area2) are defined

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)

        # Stores polygons
        self.area1 = []
        self.area2 = []

        self.current_points = []
        self.drawing = False
        self.current_point = None
        self.areas_defined = False

    def set_frame(self, frame):
        if frame is None:
            return
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.setFixedSize(w, h)
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.areas_defined:
            x = event.pos().x()
            y = event.pos().y()
            self.current_points.append((x, y))

            if len(self.current_points) == 4:
                if len(self.area1) < 1:
                    self.area1.append(self.current_points.copy())
                else:
                    self.area2.append(self.current_points.copy())

                self.current_points.clear()
                self.drawing = False

                if len(self.area1) == 1 and len(self.area2) == 1:
                    self.areas_defined = True
                    QMessageBox.information(
                        self, "Áreas Definidas",
                        "As duas áreas foram definidas. Agora o vídeo irá iniciar."
                    )
                    self.areas_done_signal.emit()

            self.update()

    def mouseMoveEvent(self, event):
        if len(self.current_points) > 0 and not self.areas_defined:
            self.drawing = True
            self.current_point = (event.pos().x(), event.pos().y())
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        if self.pixmap():
            painter.drawPixmap(0, 0, self.pixmap())

        # Draws area1 in red
        pen_area1 = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen_area1)
        for quadrilateral in self.area1:
            self.draw_polygon(painter, quadrilateral)

        # Draws area2 in green
        pen_area2 = QPen(Qt.green, 2, Qt.SolidLine)
        painter.setPen(pen_area2)
        for quadrilateral in self.area2:
            self.draw_polygon(painter, quadrilateral)

        # Draws current polygon  (blue)
        pen_current = QPen(Qt.blue, 2, Qt.SolidLine)
        painter.setPen(pen_current)
        if len(self.current_points) > 0:
            for i, pt in enumerate(self.current_points):
                painter.drawEllipse(pt[0] - 3, pt[1] - 3, 6, 6)
                if i > 0:
                    pprev = self.current_points[i - 1]
                    painter.drawLine(pprev[0], pprev[1], pt[0], pt[1])

            if self.drawing and self.current_point:
                last_pt = self.current_points[-1]
                painter.drawLine(last_pt[0], last_pt[1], self.current_point[0], self.current_point[1])

    def draw_polygon(self, painter, points):
        if len(points) == 4:
            for i in range(4):
                p1 = points[i]
                p2 = points[(i+1) % 4]
                painter.drawLine(p1[0], p1[1], p2[0], p2[1])


##############################################################################
# Page 0: StartWidget (Starting page)
##############################################################################
class StartWidget(QWidget):
    """
    It simply displays two buttons: "Open Video" and "Open Camera". (For now)
    Emits signals to tell the MainWindow which option the user has chosen.
    """
    open_video_signal = pyqtSignal()
    open_camera_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.btn_open_video = QPushButton("Abrir Vídeo")
        self.btn_open_video.clicked.connect(self.open_video_clicked)
        layout.addWidget(self.btn_open_video)

        self.btn_open_camera = QPushButton("Abrir Câmera")
        self.btn_open_camera.clicked.connect(self.open_camera_clicked)
        layout.addWidget(self.btn_open_camera)

    def open_video_clicked(self):
        self.open_video_signal.emit()

    def open_camera_clicked(self):
        self.open_camera_signal.emit()


##############################################################################
# Page 1: VideoPage (processing video/cam)
##############################################################################
class VideoPage(QWidget):
    """
    Contains the VideoWidget and a "Back" button to return to the home screen.
    Logic:
      - When opening video/camera, it only reads 1 frame and displays static.
      - Defines areas (VideoWidget).
      - When areas completed, start QTimer to play the entire video.
      - When closing or clicking "Back", we stop the video and release it.
    """
    back_to_start_signal = pyqtSignal()  # emited by clicking "Voltar"

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Back Button
        btn_back = QPushButton("Voltar")
        btn_back.clicked.connect(self.on_back_clicked)
        main_layout.addWidget(btn_back)

        # VideoWidget
        self.video_widget = VideoWidget()
        main_layout.addWidget(self.video_widget)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # PeopleCounter instance
        self.people_counter = PeopleCounter(model_path)

        # Video/camera stream variable
        self.video_stream = None

        # Connects signal from defined areas
        self.video_widget.areas_done_signal.connect(self.start_video_processing)

    def on_back_clicked(self):
        """
        User clicked "Back" → we stopped the timer, released the video and output the signal.
        """
        self.close_video()
        self.back_to_start_signal.emit()

    def open_video_file(self, file_path=None):
        """
       Opens a video file (if 'file_path' is given).
        If None, it shows dialog (optional).
        """
        if file_path is None:
            # Example if you want to open a dialogue here
            pass
        try:
            self.video_stream = VideoStream(file_path)
        except ValueError as e:
            QMessageBox.critical(self, "Erro ao abrir vídeo", str(e))
            return
        self.show_first_frame()

    def open_camera(self):
        """
        Open camera (index 0).
        """
        try:
            self.video_stream = VideoStream(0)
        except ValueError as e:
            QMessageBox.critical(self, "Erro ao abrir câmera", str(e))
            return
        self.show_first_frame()

    def show_first_frame(self):
        """
        Reads only 1 frame and displays it in the video_widget. 
        It remains static until the user draws the areas.
        """
        if not self.video_stream:
            return
        ret, frame = self.video_stream.read()
        if not ret:
            QMessageBox.critical(self, "Erro", "Não foi possível ler o primeiro frame.")
            self.close_video()
            return
        self.video_widget.set_frame(frame)

    def start_video_processing(self):
        """
        Called when areas are defined. Starts the loop (timer) to process frames.
        """
        if self.video_stream:
            self.timer.start(30)  # ~33 FPS

    def update_frame(self):
        """
        Lê frames continuamente e faz a detecção. 
        """
        if not self.video_stream:
            return
        ret, frame = self.video_stream.read()
        if not ret:
            # End of video
            self.timer.stop()
            return

        area1 = self.video_widget.area1
        area2 = self.video_widget.area2

        frame_processed = self.people_counter.process_frame(frame, area1, area2)
        self.video_widget.set_frame(frame_processed)

    def close_video(self):
        """
        Stops the timer and frees up video/camera resources.
        """
        self.timer.stop()
        if self.video_stream:
            self.video_stream.release()
            self.video_stream = None


##############################################################################
# MainWindow - Manages both pages via QStackedWidget
##############################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contador de Pessoas (PyQt) - Fullscreen + Retorno")

        # StackedWidget with 2 pages: start_widget (page 0) and video_page (page 1)
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Page 0: Home screen
        self.start_widget = StartWidget()
        self.stacked.addWidget(self.start_widget)

        # Page 1: Video Screen
        self.video_page = VideoPage()
        self.stacked.addWidget(self.video_page)

        # Home page signals
        self.start_widget.open_video_signal.connect(self.on_open_video_clicked)
        self.start_widget.open_camera_signal.connect(self.on_open_camera_clicked)

        # "Back" sign on video page
        self.video_page.back_to_start_signal.connect(self.on_back_to_start)

        # Initially shows page 0
        self.stacked.setCurrentIndex(0)

    def on_open_video_clicked(self):
        """
        "Open Video" button on the home page.
        Open dialog, get file path, go to page 1 and open the video.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecione o arquivo de vídeo", "",
            "Vídeos (*.mp4 *.avi *.mov);;Todos (*)", options=options
        )
        if file_path:
            # We move to the video page
            self.stacked.setCurrentIndex(1)
            self.video_page.open_video_file(file_path)

    def on_open_camera_clicked(self):
        """
        "Open Camera" button on the home page.
        Go to page 1 and open webcam.
        """
        self.stacked.setCurrentIndex(1)
        self.video_page.open_camera()

    def on_back_to_start(self):
        """
        Called when the user clicks "Back" on the video page.
        Returns to page 0 (start_widget).
        """
        self.stacked.setCurrentIndex(0)

    def closeEvent(self, event):
        # If you are on the video page, release
        if self.stacked.currentIndex() == 1:
            self.video_page.close_video()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    # Show full screen
    window.showFullScreen()
    # If you just want it maximized (title bar visible):
    # window.showMaximized()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
