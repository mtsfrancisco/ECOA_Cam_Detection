import sys
import os
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Include path to the utils folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
current_dir = os.path.dirname(os.path.abspath(__file__))

from tracker import Tracker
from video_stream import VideoStream

if hasattr(sys, '_MEIPASS'):
    model_path = os.path.join(sys._MEIPASS, 'yolov8m.pt')
else:
    model_path = os.path.join(current_dir, '..', 'yolo_models', 'yolov8m.pt')

class PeopleCounter:
    def __init__(self, video_path):
        # Test current directory
        print("Current directory:", current_dir)

        # Start yolo model and video path
        self.model = YOLO(model_path, verbose=True)
        self.tracker = Tracker()
        self.video_stream = VideoStream(video_path)
        
        # Define entering and exting areas
        self.current_points = []  # Pontos do quadrilátero em criação
        self.area1 = []  # Área 1 - primeiro quadriláteros
        self.area2 = []  # Área 2 - segundo quadriláteros
        self.drawing = False  # Indica se estamos em modo interativo

        #Areas 1 and 2 for the TestVideo.mp4
        #self.area1 = [(0, 600), (1920, 600), (1920, 560), (0, 560)]
        #self.area2 = [(0, 480), (1920, 480), (1920, 520), (0, 520)]
        
        # Start counters and lists of people entering and exiting
        self.people_entering = {}
        self.people_exiting = {}
        self.entering = set()
        self.exiting = set()

    def mouse_callback(self, event, x, y, flags, param):
        """Callback para eventos do mouse."""
        if event == cv2.EVENT_LBUTTONDOWN:  # Clique do botão esquerdo
            self.current_points.append((x, y))  # Adiciona o ponto clicado
            if len(self.current_points) == 4:  # Finaliza o quadrilátero após 4 pontos
                if len(self.area1) < 1:  # Se não houver quadrilátero em area1
                    self.area1.append(self.current_points.copy())
                else:  # Quando area1 estiver preenchida, preenche area2
                    self.area2.append(self.current_points.copy())
                self.current_points = []  # Reseta os pontos para o próximo quadrilátero
                self.drawing = False

        elif event == cv2.EVENT_MOUSEMOVE and len(self.current_points) > 0:  # Movimento do mouse
            self.drawing = True  # Ativa o modo interativo
            self.current_point = (x, y)  # Atualiza o ponto atual do mouse

    def process_frame(self, frame):
        # Detect objects in the frame
        results = self.model.predict(frame)
        bbox_data = results[0].boxes.data
        bbox_df = pd.DataFrame(bbox_data).astype("float")
        
        # List to store the coordinates of the bounding boxes
        bbox_list = []
        for _, row in bbox_df.iterrows():
            x1, y1, x2, y2, _, label = map(int, row)
            if label == 0: # Only people
                bbox_list.append([x1, y1, x2, y2])
        
        # Update the IDs of the tracked objects
        bbox_ids = self.tracker.update(bbox_list)
        for bbox in bbox_ids:
            x3, y3, x4, y4, obj_id = bbox
            self.handle_entrance_exit(frame, x3, y3, x4, y4, obj_id)
        
        # Draw entrance and exit areas
        cv2.polylines(frame, [np.array(self.area1, np.int32)], True, (255, 0, 0), 2)
        cv2.polylines(frame, [np.array(self.area2, np.int32)], True, (255, 0, 0), 2)
        
        # Add people count to the frame
        self.display_count(frame)

    def handle_entrance_exit(self, frame, x3, y3, x4, y4, obj_id):
        # Check if the object is in the defined areas
        if cv2.pointPolygonTest(np.array(self.area2, np.int32), (x4, y4), False) >= 0:
            self.people_entering[obj_id] = (x4, y4)
            cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
            cv2.putText(frame, str(obj_id), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        
        # Count people entering (descendo no video)
        if obj_id in self.people_entering:
            if cv2.pointPolygonTest(np.array(self.area1, np.int32), (x4, y4), False) >= 0:
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                cv2.circle(frame, (x4, y4), 5, (255, 0, 255), -1)
                cv2.putText(frame, str(obj_id), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                self.entering.add(obj_id)
        
        if cv2.pointPolygonTest(np.array(self.area1, np.int32), (x4, y4), False) >= 0:
            self.people_exiting[obj_id] = (x4, y4)
            cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
            cv2.putText(frame, str(obj_id), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        
        # Count people exiting (subindo no video)
        if obj_id in self.people_exiting:
            if cv2.pointPolygonTest(np.array(self.area2, np.int32), (x4, y4), False) >= 0:
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                cv2.circle(frame, (x4, y4), 5, (255, 0, 255), -1)
                cv2.putText(frame, str(obj_id), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                self.exiting.add(obj_id)

    def display_count(self, frame):
        # Displays the count of people entering and leaving
        people_in = len(self.entering)
        people_out = len(self.exiting)
        cv2.putText(frame, "Descendo: ", (0, 80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, str(people_in), (150, 80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "Subindo: ", (0, 140), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 255), 2)
        cv2.putText(frame, str(people_out), (150, 140), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 255), 2)

    def run(self):
        # Create window and set the mouse callback
        ret, frame = self.video_stream.read()

        if not ret:
            print("Error reading video")
            self.video_stream.release()

        """Método principal para executar o programa."""
        cv2.namedWindow("Quadrilateral Drawer")
        cv2.setMouseCallback("Quadrilateral Drawer", self.mouse_callback)
        

        while True:
            temp_img = frame.copy()  # Cópia da imagem para desenho temporário

            # Desenhar os quadriláteros em área 1
            for quadrilateral in self.area1:
                for i in range(4):
                    cv2.line(temp_img, quadrilateral[i], quadrilateral[(i + 1) % 4], (0, 0, 255), 2)

            # Desenhar os quadriláteros em área 2
            for quadrilateral in self.area2:
                for i in range(4):
                    cv2.line(temp_img, quadrilateral[i], quadrilateral[(i + 1) % 4], (0, 255, 0), 2)

            # Desenhar os pontos fixos do quadrilátero em criação
            for point in self.current_points:
                cv2.circle(temp_img, point, 5, (0, 0, 255), -1)

            # Desenhar as linhas fixas do quadrilátero em criação
            if len(self.current_points) > 1:
                for i in range(len(self.current_points) - 1):
                    cv2.line(temp_img, self.current_points[i], self.current_points[i + 1], (0, 0, 255), 2)

            # Desenhar a linha interativa
            if self.drawing and len(self.current_points) < 4:
                cv2.line(temp_img, self.current_points[-1], self.current_point, (0, 255, 0), 2)
                if len(self.current_points) == 3:  # Linha do primeiro ao terceiro ponto enquanto desenha o quarto
                    cv2.line(temp_img, self.current_points[0], self.current_point, (0, 255, 0), 2)

            cv2.imshow("Quadrilateral Drawer", temp_img)

            # Sair ao pressionar a tecla ESC
            key = cv2.waitKey(1)
            if key == 27 or len(self.area1) == 1 and len(self.area2) == 1:  # Limite de dois quadriláteros
                break

        print("Pontos a area 1: ", self.area1)
        print("Pontos a area 2: ", self.area2)

        while True:
            ret, frame = self.video_stream.read()
            if not ret:
                break
            
            self.process_frame(frame)
            self.video_stream.display(frame, window_name="RGB")
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        self.video_stream.release()


def get_video_path():
    # Try to open a window for the user to select the video
    Tk().withdraw()  # Hide the main Tkinter window
    user_input = askopenfilename(title="Select video file", filetypes=[("Video file", "*.mp4")])
    
    if user_input:  # If the user selects a file, use it
        return user_input
    
    # Otherwise, use the embedded path
    if hasattr(sys, '_MEIPASS'):  # When executed as an executable
        return 0
    
    # When executed as a Python script
    return 0

# Video path
video_path = get_video_path()

# Instance and run the people counter
people_counter = PeopleCounter(video_path)
people_counter.run()