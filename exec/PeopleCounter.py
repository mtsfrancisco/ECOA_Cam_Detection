import sys
import os
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
import traceback
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Include path to the utils folder
print("=====================PROGRAM STARTING============================")
from tracker import Tracker
from video_stream import VideoStream

import math


class Tracker:
    def __init__(self):
        # Store the center positions of the objects
        self.center_points = {}
        # Keep the count of the IDs
        # each time a new object id detected, the count will increase by one
        self.id_count = 0


    def update(self, objects_rect):
        # Objects boxes and ids
        objects_bbs_ids = []

        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 35:
                    self.center_points[id] = (cx, cy)
#                    print(self.center_points)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break

            # New object is detected we assign the ID to that object
            if same_object_detected is False:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        # Clean the dictionary by center points to remove IDS not used anymore
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        # Update dictionary with IDs not used removed
        self.center_points = new_center_points.copy()
        return objects_bbs_ids

class PeopleCounter:
    def __init__(self, video_path):
        # Start yolo model and video path
        self.model = YOLO('yolov8m.pt')
        self.tracker = Tracker()
        self.video_stream = VideoStream(video_path)
        
        # Define entering and exting areas
        self.area1 = []
        self.area2 = []

        #Areas 1 and 2 for the TestVideo.mp4
        #self.area1 = [(0, 600), (1920, 600), (1920, 560), (0, 560)]
        #self.area2 = [(0, 480), (1920, 480), (1920, 520), (0, 520)]
        
        # Start counters and lists of people entering and exiting
        self.people_entering = {}
        self.people_exiting = {}
        self.entering = set()
        self.exiting = set()

    def select_points(self,event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Add the point to the corresponding array
            if len(self.area1) < 4:
                self.area1.append((x, y))
                print(f"Ponto adicionado ao array 1: {x}, {y}")
            elif len(self.area2) < 4:
                self.area2.append((x, y))
                print(f"Ponto adicionado ao array 2: {x}, {y}")

            if len(self.area1) == 4 and len(self.area2) == 4:
                 print("8 pontos selecionados. O vídeo irá continuar.")
                 cv2.setMouseCallback('Frame', lambda *args: None)

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

        else:
            self.video_stream.display(frame, window_name="RGB")
            cv2.putText(frame, "Selecione os pontos da area 1 e 2", (0, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
            cv2.setMouseCallback("RGB", self.select_points)
            # Main process to capture and process frames

            while len(self.area1) < 4 or len(self.area2) < 4:
                cv2.waitKey(1)

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
    # Tentar abrir uma janela para o usuário selecionar o vídeo
    Tk().withdraw()  # Ocultar a janela principal do Tkinter
    user_input = askopenfilename(title="Selecione o vídeo", filetypes=[("Arquivos de vídeo", "*.mp4")])
    
    if user_input:  # Se o usuário selecionar um arquivo, use-o
        return user_input
    
    # Caso contrário, use o caminho embutido
    if hasattr(sys, '_MEIPASS'):  # Quando executado como executável
        return 0
    
    # Quando executado como script Python
    return 0


# Video path
# Instance and run the people counter
#people_counter = PeopleCounter(video_path)
#people_counter.run()

video_path = get_video_path()

people_counter = PeopleCounter(video_path)
people_counter.run()
