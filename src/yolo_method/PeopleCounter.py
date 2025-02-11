import cv2
import face_recognition
import os
import time
from deepface import DeepFace
import json

class Person:
    def __init__(self, name, encoding, image):
        self.name = name
        self.encoding = encoding
        self.image = image

class PersonsLoader:
    def __init__(self, users_directory):
        self.users_directory = users_directory
        self.persons = []
        self.known_face_encodings = []
        self.load_known_people()

    def load_known_people(self):
        """Carrega as faces conhecidas e armazena em uma lista de objetos Person."""
        for user_folder in os.listdir(self.users_directory):
            user_path = os.path.join(self.users_directory, user_folder)
            if os.path.isdir(user_path):
                json_file = None
                for filename in os.listdir(user_path):
                    if filename.lower().endswith(".json"):
                        json_file = os.path.join(user_path, filename)
                        break
                if json_file:
                    with open(json_file, "r") as f:
                        person_data = json.load(f)
                        person_name = person_data.get("name", user_folder)
                        person_last_name = person_data.get("last_name", user_folder)

                for filename in os.listdir(user_path):
                    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                        file_path = os.path.join(user_path, filename)
                        image = face_recognition.load_image_file(file_path)
                        encodings = face_recognition.face_encodings(image)

                        if encodings:
                            self.persons.append(Person(
                                name=f"{person_name} {person_last_name}",
                                encoding=encodings[0],
                                image=cv2.imread(file_path),
                            ))
                            self.known_face_encodings.append(encodings[0])

        print("Pessoas carregadas:")                  
        for person in self.persons:
            print(person.name)
        print("====================================")

class WebcamFaceRecognizer:
    def __init__(self, face_recognizer, wait_time=5):
        self.face_recognizer = face_recognizer
        self.wait_time = wait_time
        self.last_check_time = time.time() - wait_time
        self.video_capture = cv2.VideoCapture(0)
        self.frame_width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.square_size = 500
        self.x_start = self.frame_width // 2 - self.square_size // 2
        self.y_start = self.frame_height // 2 - self.square_size // 2
        self.x_end = self.x_start + self.square_size
        self.y_end = self.y_start + self.square_size

    def draw_square(self, frame):
        """Desenha um quadrado no meio da tela."""
        cv2.rectangle(frame, (self.x_start, self.y_start), (self.x_end, self.y_end), (0, 255, 0), 2)

    def analyze_face(self, roi):
        """Analisa a face na região de interesse (ROI) usando DeepFace."""
        temp_roi_path = "temp_roi.jpg"
        cv2.imwrite(temp_roi_path, roi)
        try:
            analysis = DeepFace.analyze(img_path=temp_roi_path, actions=["age", "gender", "race", "emotion"], enforce_detection=False)
            if analysis:
                return analysis[0]
        except Exception as e:
            print(f"Erro ao analisar a face: {e}")
        finally:
            if os.path.exists(temp_roi_path):
                os.remove(temp_roi_path)
        return None

    def recognize_face(self, rgb_roi):
        """Reconhece a face na região de interesse (ROI) usando face_recognition."""
        face_encodings = face_recognition.face_encodings(rgb_roi)
        if face_encodings:
            face_encoding = face_encodings[0]
            matches = face_recognition.compare_faces(self.face_recognizer.known_face_encodings, face_encoding, tolerance=0.8)
            face_distances = face_recognition.face_distance(self.face_recognizer.known_face_encodings, face_encoding)

            if any(matches):
                best_match_index = matches.index(True)
                return self.face_recognizer.persons[best_match_index]
        return None

    def display_person_info(self, frame, person, analysis):
        """Exibe informações da pessoa reconhecida no frame."""
        person_image = cv2.resize(person.image, (self.square_size, self.square_size))
        frame[0:self.square_size, 0:self.square_size] = person_image
        frame[0:self.square_size, self.square_size:self.square_size * 2] = cv2.resize(frame[self.y_start:self.y_end, self.x_start:self.x_end], (self.square_size, self.square_size))
        cv2.putText(frame, person.name, (10, self.square_size + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        print(f"Pessoa reconhecida: {person.name}")

    def display_unknown_person_info(self, frame, analysis):
        """Exibe informações de uma pessoa não reconhecida no frame."""
        cv2.putText(frame, "Pessoa não conhecida", (10, self.square_size + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Age: {analysis['age']}", (10, self.square_size + 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Gender: {analysis['dominant_gender']}", (10, self.square_size + 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Race: {analysis['dominant_race']}", (10, self.square_size + 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Emotion: {analysis['dominant_emotion']}", (10, self.square_size + 170), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        print("Pessoa não reconhecida")

    def run(self):
        """Executa o loop principal de detecção e reconhecimento de faces."""
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                break

            self.draw_square(frame)

            if time.time() - self.last_check_time >= self.wait_time:
                roi = frame[self.y_start:self.y_end, self.x_start:self.x_end]
                rgb_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

                analysis = self.analyze_face(roi)
                if analysis:
                    person = self.recognize_face(rgb_roi)
                    if person:
                        self.display_person_info(frame, person, analysis)
                    else:
                        self.display_unknown_person_info(frame, analysis)

                    cv2.imshow("Webcam", frame)
                    cv2.waitKey(4000)

                self.last_check_time = time.time()

            cv2.imshow("Webcam", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video_capture.release()
        cv2.destroyAllWindows()

# Caminho para a pasta "users"
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
USERS_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "..", "local_database", "users")

# Inicializa e executa o detector de faces
face_recognizer = PersonsLoader(USERS_DIRECTORY)
webcam_detector = WebcamFaceRecognizer(face_recognizer)
webcam_detector.run()