import cv2
import face_recognition
import os
import time
from deepface import DeepFace
import os
import json

# Caminho para a pasta "people"
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
USERS_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "..", "local_database", "users")

class Person:
    def __init__(self, name, encoding, image):
        self.name = name
        self.encoding = encoding
        self.image = image

# Carrega as faces conhecidas
persons = []
known_face_encodings = []

def load_known_people(directory):
    """Carrega as faces conhecidas e armazena em uma lista de objetos KnownFace. E fazer o load dos encondings no array known_face_encodings"""
    for user_folder in os.listdir(directory):
        user_path = os.path.join(directory, user_folder)
        if os.path.isdir(user_path):
            json_file = None
            for filename in os.listdir(user_path):
                if filename.lower().endswith(".json"):
                    json_file = os.path.join(user_path, filename)
                    break
            if json_file:
                # Lê o arquivo JSON para obter o nome da pessoa
                with open(json_file, "r") as f:
                    person_data = json.load(f)
                    person_name = person_data.get("name", user_folder)  # Usa o nome do JSON ou o nome da pasta como fallback
                    person_last_name = person_data.get("last_name", user_folder) 

            for filename in os.listdir(user_path):
                if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    file_path = os.path.join(user_path, filename)
                    image = face_recognition.load_image_file(file_path)
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings:
                        persons.append(Person(
                            name=person_name + ' ' + person_last_name,
                            encoding=encodings[0],
                            image=cv2.imread(file_path),
                        ))
                        known_face_encodings.append(encodings[0])

load_known_people(USERS_DIRECTORY)

# Inicializa a webcam
video_capture = cv2.VideoCapture(0)

# Dimensões do quadrado no meio da tela
frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
square_size = 500
x_start = frame_width // 2 - square_size // 2
y_start = frame_height // 2 - square_size // 2
x_end = x_start + square_size
y_end = y_start + square_size

# Tempo de espera entre verificações
wait_time = 5
last_check_time = time.time() - wait_time

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Desenha o quadrado no meio da tela
    cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)

    # Verifica se o tempo de espera passou
    if time.time() - last_check_time >= wait_time:
        # Recorta a área do quadrado
        roi = frame[y_start:y_end, x_start:x_end]
        rgb_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

        # Salva a ROI temporariamente para análise com DeepFace
        temp_roi_path = "temp_roi.jpg"
        cv2.imwrite(temp_roi_path, roi)

        try:
            # Analisa a face com DeepFace para idade e gênero
            analysis = DeepFace.analyze(img_path=temp_roi_path, actions=["age", "gender", "race", "emotion"], enforce_detection=False)

            if analysis:
                # Pega os resultados da análise
                age = analysis[0]["age"]
                gender = analysis[0]["dominant_gender"]
                race = analysis[0]["dominant_race"]
                emotion = analysis[0]["dominant_emotion"]

                # Procura faces na região do quadrado usando face_recognition
                face_encodings = face_recognition.face_encodings(rgb_roi)

                if face_encodings:
                    # Usa apenas a primeira face detectada
                    face_encoding = face_encodings[0]

                    # Compara com as faces conhecidas
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.8)
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    print(f"Distâncias: {face_distances}")

                    if any(matches):
                        # Identifica a face com menor distância
                        best_match_index = matches.index(True)

                        # Mostra a foto da pessoa conhecida
                        person_image = persons[best_match_index].image
                        person_name = persons[best_match_index].name

                        person_image = cv2.resize(person_image, (square_size, square_size))

                        # Coloca a imagem da pessoa reconhecida no frame
                        frame[0:square_size, 0:square_size] = person_image
                        frame[0:square_size, square_size:square_size * 2] = roi

                        # Adiciona o nome da pessoa reconhecida e informações abaixo das imagens
                        cv2.putText(frame, person_name, (10, square_size + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        #cv2.putText(frame, f"Age: {age}", (10, square_size + 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        #cv2.putText(frame, f"Gender: {gender}", (10, square_size + 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                        print(f"Pessoa reconhecida: {person_name}")

                        # Exibe o frame da webcam com as imagens por 4 segundos
                        cv2.imshow("Webcam", frame)
                        cv2.waitKey(4000)
                    else:

                        cv2.putText(frame, "Pessoa nao conhecida", (10, square_size + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(frame, f"Age: {age}", (10, square_size + 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(frame, f"Gender: {gender}", (10, square_size + 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(frame, f"Race: {race}", (10, square_size + 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(frame, f"Emotion: {emotion}", (10, square_size + 170), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                        print("Pessoa não reconhecida")
                        cv2.imshow("Webcam", frame)
                        cv2.waitKey(4000)
                else:
                    print("Nenhum rosto detectado")
            else:
                print("Nenhuma face detectada para análise de idade e gênero")
        except Exception as e:
            print(f"Erro ao analisar a face: {e}")

        # Atualiza o último tempo de verificação
        last_check_time = time.time()

    # Exibe o frame da webcam
    cv2.imshow("Webcam", frame)

    # Verifica se a tecla 'q' foi pressionada para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tempo_roi = "temp_roi.jpg"
try:
    # Verifica se o arquivo existe
    if os.path.exists(tempo_roi):
        os.remove(tempo_roi)  # Exclui o arquivo
        print(f"Imagem temoraria excluida")
    else:
        print(f"O arquivo '{tempo_roi}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro ao excluir o arquivo: {e}")

# Libera a webcam e fecha as janelas
video_capture.release()
cv2.destroyAllWindows()