import sys
import os
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from tracker import Tracker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

from video_stream import VideoStream

current_dir = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(current_dir, '..', 'media', 'TestVideo.mp4')


# Carregar o modelo YOLO
model = YOLO('../yolo_models/yolov8m.pt')

def rgb_event(event, x, y, flags, param):
    """Função de callback para capturar a posição do mouse e imprimir as coordenadas RGB."""
    if event == cv2.EVENT_MOUSEMOVE:
        colors_bgr = [x, y]
        print(colors_bgr)

# Configuração da janela para exibir o vídeo e registrar os eventos do mouse
cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', rgb_event)

# Definir áreas para detecção de entrada e saída
area1 = [(0, 600), (1920, 600), (1920, 560), (0, 560)]
area2 = [(0, 480), (1920, 480), (1920, 520), (0, 520)]

# Inicialização do fluxo de vídeo (arquivo ou câmera)
video_stream = VideoStream(video_path)

#camera (0)
#video_stream = VideoStream(0)

# Inicialização do rastreador e contadores de entrada/saída
tracker = Tracker()
people_entering = {}
people_exiting = {}
entering = set()
exiting = set()

while True:
    # Captura do frame atual
    ret, frame = video_stream.read()
    if not ret:
        break

    # Detecção de objetos no frame
    results = model.predict(frame)
    bbox_data = results[0].boxes.data
    bbox_df = pd.DataFrame(bbox_data).astype("float")

    # List para armazenar as coordenadas dos bounding boxes
    bbox_list = []
    for _, row in bbox_df.iterrows():
        x1, y1, x2, y2, _, label = map(int, row)
        if label == 0:  # Apenas pessoas
            bbox_list.append([x1, y1, x2, y2])

    # Atualizar os IDs dos objetos rastreados
    bbox_ids = tracker.update(bbox_list)
    for bbox in bbox_ids:
        x3, y3, x4, y4, obj_id = bbox
        result_in_area2 = cv2.pointPolygonTest(np.array(area2, np.int32), (x4, y4), False)

        if result_in_area2 >= 0:
            people_entering[obj_id] = (x4, y4)
            cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 0, 255), 2)

        if obj_id in people_entering:
            result_in_area1 = cv2.pointPolygonTest(np.array(area1, np.int32), (x4, y4), False)
            if result_in_area1 >= 0:
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                cv2.circle(frame, (x4, y4), 5, (255, 0, 255), -1)
                cv2.putText(frame, str(obj_id), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                entering.add(obj_id)

        # Detecção de saída de pessoas
        result_in_area1 = cv2.pointPolygonTest(np.array(area1, np.int32), (x4, y4), False)
        if result_in_area1 >= 0:
            people_exiting[obj_id] = (x4, y4)
            cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)

        if obj_id in people_exiting:
            result_in_area2 = cv2.pointPolygonTest(np.array(area2, np.int32), (x4, y4), False)
            if result_in_area2 >= 0:
                cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 255), 2)
                cv2.circle(frame, (x4, y4), 5, (255, 0, 255), -1)
                cv2.putText(frame, str(obj_id), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                exiting.add(obj_id)

    # Desenhar as áreas de entrada e saída
    cv2.polylines(frame, [np.array(area1, np.int32)], True, (255, 0, 0), 2)
    cv2.polylines(frame, [np.array(area2, np.int32)], True, (255, 0, 0), 2)

    # Contagem de pessoas entrando e saindo
    people_in = len(entering)
    people_out = len(exiting)

    # Adicionando a contagem de pessoas entrando e saindo no frame
    cv2.putText(frame, "Descendo: ", (0, 80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, str(people_in), (150, 80), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, "Subindo: ", (0, 140), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 255), 2)
    cv2.putText(frame, str(people_out), (150, 140), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 0, 255), 2)

    # Exibir o frame atualizado
    video_stream.display(frame, window_name="RGB")
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Liberação dos recursos
video_stream.release()

