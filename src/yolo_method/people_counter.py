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

# Imports locais
from tracker import Tracker
from video_stream import VideoStream
from ultralytics import YOLO

##############################################################################
# Ajuste do caminho do modelo
##############################################################################
model_str = "yolov8m.pt"
current_dir = os.path.dirname(os.path.abspath(__file__))

if hasattr(sys, '_MEIPASS'):
    model_path = os.path.join(sys._MEIPASS, model_str)
else:
    # Se o modelo estiver em "yolo_models" dentro de "yolo_method":
    model_path = os.path.join(current_dir, "yolo_models", model_str)

print("DEBUG: model_path =", model_path)


##############################################################################
# Classe PeopleCounter (YOLO + Tracker + contagem)
##############################################################################
class PeopleCounter:
    def __init__(self, model_path):
        self.model = YOLO(model_path, verbose=True)
        self.tracker = Tracker()

        # Dicionários e conjuntos para contagem
        self.people_entering = {}
        self.people_exiting = {}
        self.entering = set()
        self.exiting = set()

    def process_frame(self, frame, area1, area2):
        """
        Recebe frame (BGR), áreas (area1, area2) e retorna frame processado.
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

        # Atualiza tracker
        bbox_ids = self.tracker.update(bbox_list)

        # Desenha polígonos para ilustrar
        for quad in area1:
            cv2.polylines(frame, [np.array(quad, np.int32)], True, (255, 0, 0), 2)
        for quad in area2:
            cv2.polylines(frame, [np.array(quad, np.int32)], True, (0, 255, 0), 2)

        # Verifica entradas/saídas
        for bbox in bbox_ids:
            x3, y3, x4, y4, obj_id = bbox
            self.handle_entrance_exit(frame, x3, y3, x4, y4, obj_id, area1, area2)

        # Desenha contagens
        self.display_count(frame)
        return frame

    def handle_entrance_exit(self, frame, x3, y3, x4, y4, obj_id, area1, area2):
        # Verifica área2 → people_entering
        for quad in area2:
            if cv2.pointPolygonTest(np.array(quad, np.int32), (x4, y4), False) >= 0:
                self.people_entering[obj_id] = (x4, y4)
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                cv2.putText(frame, str(obj_id), (x3, y3),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                break

        # Se está em people_entering, checa se alcançou área1
        if obj_id in self.people_entering:
            for quad in area1:
                if cv2.pointPolygonTest(np.array(quad, np.int32), (x4, y4), False) >= 0:
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                    cv2.circle(frame, (x4, y4), 5, (255, 0, 255), -1)
                    cv2.putText(frame, str(obj_id), (x3, y3),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    self.entering.add(obj_id)
                    break

        # Verifica área1 → people_exiting
        for quad in area1:
            if cv2.pointPolygonTest(np.array(quad, np.int32), (x4, y4), False) >= 0:
                self.people_exiting[obj_id] = (x4, y4)
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                cv2.putText(frame, str(obj_id), (x3, y3),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                break

        # Se está em people_exiting, checa se alcançou área2
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
# VideoWidget - para desenhar as áreas no frame estático
##############################################################################
class VideoWidget(QLabel):
    areas_done_signal = pyqtSignal()  # Emite quando ambas as áreas (area1, area2) estão definidas

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)

        # Armazena polígonos
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

        # Desenha area1 em vermelho
        pen_area1 = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen_area1)
        for quadrilateral in self.area1:
            self.draw_polygon(painter, quadrilateral)

        # Desenha area2 em verde
        pen_area2 = QPen(Qt.green, 2, Qt.SolidLine)
        painter.setPen(pen_area2)
        for quadrilateral in self.area2:
            self.draw_polygon(painter, quadrilateral)

        # Desenha polígono atual (azul)
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
# Página 0: StartWidget (tela inicial com dois botões)
##############################################################################
class StartWidget(QWidget):
    """
    Simplesmente exibe dois botões: "Abrir Vídeo" e "Abrir Câmera".
    Emite sinais para informar ao MainWindow qual opção o usuário escolheu.
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
# Página 1: VideoPage (onde processamos vídeo/câmera)
##############################################################################
class VideoPage(QWidget):
    """
    Contém o VideoWidget e um botão de "Voltar" para retornar à tela inicial.
    Lógica:
      - Ao abrir vídeo/câmera, lê só 1 frame e exibe estático.
      - Define áreas (VideoWidget).
      - Quando áreas concluídas, inicia o QTimer para rodar o vídeo todo.
      - Ao fechar ou clicar em "Voltar", paramos o vídeo e liberamos.
    """
    back_to_start_signal = pyqtSignal()  # emitido ao clicar em "Voltar"

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Botão Voltar
        btn_back = QPushButton("Voltar")
        btn_back.clicked.connect(self.on_back_clicked)
        main_layout.addWidget(btn_back)

        # VideoWidget
        self.video_widget = VideoWidget()
        main_layout.addWidget(self.video_widget)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Instancia PeopleCounter
        self.people_counter = PeopleCounter(model_path)

        # Variável de fluxo de vídeo/câmera
        self.video_stream = None

        # Conecta sinal de áreas definidas
        self.video_widget.areas_done_signal.connect(self.start_video_processing)

    def on_back_clicked(self):
        """
        Usuário clicou em "Voltar" → paramos o timer, liberamos o vídeo e emitimos o sinal.
        """
        self.close_video()
        self.back_to_start_signal.emit()

    def open_video_file(self, file_path=None):
        """
        Abre um arquivo de vídeo (caso 'file_path' seja dado).
        Caso seja None, mostra diálogo (opcional).
        """
        if file_path is None:
            # Exemplo se quiser abrir diálogo aqui
            pass
        try:
            self.video_stream = VideoStream(file_path)
        except ValueError as e:
            QMessageBox.critical(self, "Erro ao abrir vídeo", str(e))
            return
        self.show_first_frame()

    def open_camera(self):
        """
        Abre câmera (índice 0).
        """
        try:
            self.video_stream = VideoStream(0)
        except ValueError as e:
            QMessageBox.critical(self, "Erro ao abrir câmera", str(e))
            return
        self.show_first_frame()

    def show_first_frame(self):
        """
        Lê só 1 frame e exibe no video_widget. 
        Fica estático até o usuário desenhar as áreas.
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
        Chamado quando as áreas são definidas. Inicia o loop (timer) para processar frames.
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
            # Fim do vídeo
            self.timer.stop()
            return

        area1 = self.video_widget.area1
        area2 = self.video_widget.area2

        frame_processed = self.people_counter.process_frame(frame, area1, area2)
        self.video_widget.set_frame(frame_processed)

    def close_video(self):
        """
        Para o timer e libera recursos do vídeo/câmera.
        """
        self.timer.stop()
        if self.video_stream:
            self.video_stream.release()
            self.video_stream = None


##############################################################################
# MainWindow - Gerencia as duas páginas via QStackedWidget
##############################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contador de Pessoas (PyQt) - Fullscreen + Retorno")

        # StackedWidget com 2 páginas: start_widget (página 0) e video_page (página 1)
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Página 0: tela inicial
        self.start_widget = StartWidget()
        self.stacked.addWidget(self.start_widget)

        # Página 1: tela de vídeo
        self.video_page = VideoPage()
        self.stacked.addWidget(self.video_page)

        # Sinais da página inicial
        self.start_widget.open_video_signal.connect(self.on_open_video_clicked)
        self.start_widget.open_camera_signal.connect(self.on_open_camera_clicked)

        # Sinal de "Voltar" na página de vídeo
        self.video_page.back_to_start_signal.connect(self.on_back_to_start)

        # Inicialmente mostra página 0
        self.stacked.setCurrentIndex(0)

    def on_open_video_clicked(self):
        """
        Botão "Abrir Vídeo" da página inicial.
        Abre diálogo, pega caminho do arquivo, vai para página 1 e abre o vídeo.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecione o arquivo de vídeo", "",
            "Vídeos (*.mp4 *.avi *.mov);;Todos (*)", options=options
        )
        if file_path:
            # Passamos para a página de vídeo
            self.stacked.setCurrentIndex(1)
            self.video_page.open_video_file(file_path)

    def on_open_camera_clicked(self):
        """
        Botão "Abrir Câmera" da página inicial.
        Vai para página 1 e abre webcam.
        """
        self.stacked.setCurrentIndex(1)
        self.video_page.open_camera()

    def on_back_to_start(self):
        """
        Chamada quando o usuário clica em "Voltar" na página de vídeo.
        Retorna para a página 0 (start_widget).
        """
        self.stacked.setCurrentIndex(0)

    def closeEvent(self, event):
        # Se estiver na página de vídeo, liberar
        if self.stacked.currentIndex() == 1:
            self.video_page.close_video()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    # Mostrar em tela cheia
    window.showFullScreen()
    # Se quiser só maximizado (barra de título visível):
    # window.showMaximized()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
