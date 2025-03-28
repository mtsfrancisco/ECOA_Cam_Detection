import cv2
import face_recognition
import os
import time
from deepface import DeepFace
from datetime import datetime
import json
import csv
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.firebase.history_manager import HistoryManager
from src.firebase.user_image_manager import UserImageManager

# Path to the "users" folder
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
USERS_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "..", "local_database", "users")
HISTORY_CSV_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "recognized_people.csv")

class Person:
    """Class representing a person with their name, face encoding, image, and user ID."""
    def __init__(self, name, encoding, image, user_id):
        self.name = name
        self.encoding = encoding
        self.image = image
        self.user_id = user_id

class known_people_loader:
    """Class responsible for loading known people from the local database."""
    def __init__(self, users_directory):
        self.users_directory = users_directory
        self.persons = []
        self.known_face_encodings = []
        self.load_known_people()

    def load_known_people(self):
        """Load known faces and store them in a list of Person objects."""

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
                                user_id = person_data.get("user_id")
                            ))
                            self.known_face_encodings.append(encodings[0])

class cam_face_recognition:
    """Class responsible for recognizing faces using the webcam."""
    def __init__(self, known_persons, wait_time=3, csv_file=HISTORY_CSV_DIRECTORY):
        self.known_persons = known_persons
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
        self.history_manager = HistoryManager()

        self.csv_file = csv_file

        # Ensure the directory structure exists
        csv_dir = os.path.dirname(self.csv_file)
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)

        # If the CSV file does not exist, create it with headers
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Name"])  # Column headers

    def draw_square(self, frame):
        """Draws a square in the middle of the screen."""
        cv2.rectangle(frame, (self.x_start, self.y_start), (self.x_end, self.y_end), (0, 255, 0), 2)

    def analyze_face(self, roi):
        """Analyze the face in the region of interest (ROI) using DeepFace."""
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

    def recognize_face(self, face_encodings):
        """Recognizes the face in the region of interest (ROI) using face_recognition."""
        if face_encodings:
            face_encoding = face_encodings[0]
            # Reccomended tolerance level should be set to 0.4
            matches = face_recognition.compare_faces(self.known_persons.known_face_encodings, face_encoding, tolerance=0.4)
            face_distances = face_recognition.face_distance(self.known_persons.known_face_encodings, face_encoding)
            print(f"Distâncias: {face_distances}")

            if any(matches):
                best_match_index = matches.index(True)
                return self.known_persons.persons[best_match_index]
        return None

    def display_person_info(self, frame, person):
        """Displays information about the recognized person in the frame."""
        person_image = cv2.resize(person.image, (self.square_size, self.square_size))
        frame[0:self.square_size, 0:self.square_size] = person_image
        frame[0:self.square_size, self.square_size:self.square_size * 2] = cv2.resize(frame[self.y_start:self.y_end, self.x_start:self.x_end], (self.square_size, self.square_size))
        cv2.putText(frame, person.name, (10, self.square_size + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Getting the current time stamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Formatting data for json type
        date, time = timestamp.split(" ")
        history_data = {
            "user_id": person.user_id,
            "name": person.name,
            "date": date,
            "time": time,
            "status": "Feature in developement"
        }

        print("\n Found user_id " + person.user_id + "\n")
        # Adding history to the database
        self.history_manager.add_history(person.user_id, history_data)

        with open(self.csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, person.name])
        
        print(f"Pessoa reconhecida: {person.name} às {timestamp}")

    def display_unknown_person_info(self, frame, analysis):
        """Displays information about an unrecognized person in the frame."""
        cv2.putText(frame, "Pessoa nao conhecida", (10, self.square_size + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Age: {analysis['age']}", (10, self.square_size + 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Gender: {analysis['dominant_gender']}", (10, self.square_size + 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Race: {analysis['dominant_race']}", (10, self.square_size + 140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Emotion: {analysis['dominant_emotion']}", (10, self.square_size + 170), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        print("Pessoa não reconhecida")

    def run(self):
        """Runs the main loop of face detection and recognition."""
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                break

            self.draw_square(frame)

            if time.time() - self.last_check_time >= self.wait_time:
                roi = frame[self.y_start:self.y_end, self.x_start:self.x_end]
                rgb_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_roi)
                if face_encodings:
                    person = self.recognize_face(face_encodings) # best match index
                    if person:
                        self.display_person_info(frame, person)
                        cv2.imshow("Webcam", frame)
                        cv2.waitKey(4000)
                    else:
                        # Uses DeepFace library (Consider removing if too slow)
                        analysis = self.analyze_face(roi)
                        self.display_unknown_person_info(frame, analysis)
                        cv2.imshow("Webcam", frame)
                        cv2.waitKey(4000)
                else:
                    print("Nenhuma face detectada.")

                self.last_check_time = time.time()

            cv2.imshow("Webcam", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video_capture.release()
        cv2.destroyAllWindows()


def main():
    """Main function to initialize and run the face recognition system."""
    known_persons = known_people_loader(USERS_DIRECTORY)
    face_recognizer = cam_face_recognition(known_persons)
    face_recognizer.run()

if __name__ == "__main__":
    #UserImageManager = UserImageManager()
    #UserImageManager.recover_users()
    img_path = os.path.join(CURRENT_DIRECTORY, "Matheus.jpg")
    objs = DeepFace.analyze(
    img_path = img_path, 
    actions = ['age', 'gender', 'race', 'emotion'],
    enforce_detection=False
    )
    main()




