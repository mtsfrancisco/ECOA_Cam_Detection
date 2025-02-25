import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget,
    QVBoxLayout, QPushButton, QMessageBox, QLabel, QLineEdit, QFormLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
import cv2

# ==========================
# YOUR EXISTING IMPORTS
# ==========================
# Example: 
# from src.yolo_method.people_counter import VideoPage
# from src.face_recognition.face_recognition_ import cam_face_recognition
# from src.firebase.user_image_manager import UserImageManager
# from src.firebase.history_manager import HistoryManager
# ...

# ==========================
# HomePage
# ==========================
class HomePage(QWidget):
    """
    This is the initial page with two buttons:
    1) "Câmeras": goes to the YOLO page for people counting.
    2) "Reconhecimento Facial": goes to the facial recognition page.
    """
    go_to_cameras_signal = pyqtSignal()
    go_to_face_rec_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        btn_cameras = QPushButton("Câmeras")
        btn_cameras.clicked.connect(self.go_to_cameras)
        layout.addWidget(btn_cameras)

        btn_face = QPushButton("Reconhecimento Facial")
        btn_face.clicked.connect(self.go_to_face_rec)
        layout.addWidget(btn_face)

        self.setLayout(layout)

    def go_to_cameras(self):
        self.go_to_cameras_signal.emit()

    def go_to_face_rec(self):
        self.go_to_face_rec_signal.emit()


# ==========================
# FaceRecHome
# ==========================
class FaceRecHome(QWidget):
    """
    This page has 3 buttons:
    1) "Realizar Reconhecimento Facial"
    2) "Adicionar Novo Usuário"
    3) "Remover Usuário"
    """
    go_run_face_signal = pyqtSignal()
    go_add_user_signal = pyqtSignal()
    go_remove_user_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        btn_run = QPushButton("Realizar Reconhecimento Facial")
        btn_run.clicked.connect(lambda: self.go_run_face_signal.emit())
        layout.addWidget(btn_run)

        btn_add = QPushButton("Adicionar Novo Usuário")
        btn_add.clicked.connect(lambda: self.go_add_user_signal.emit())
        layout.addWidget(btn_add)

        btn_remove = QPushButton("Remover Usuário")
        btn_remove.clicked.connect(lambda: self.go_remove_user_signal.emit())
        layout.addWidget(btn_remove)

        self.setLayout(layout)


# ==========================
# FaceRecRunPage
# ==========================
class FaceRecRunPage(QWidget):
    """
    This page runs the webcam loop for face recognition.
    When a face is recognized, it shows a pop-up with "Entrada confirmada".
    If not recognized, shows "Rosto não reconhecido".
    """
    back_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.label_info = QLabel("Clique em 'Iniciar' para realizar reconhecimento.")
        layout.addWidget(self.label_info)

        btn_start = QPushButton("Iniciar")
        btn_start.clicked.connect(self.start_recognition)
        layout.addWidget(btn_start)

        btn_back = QPushButton("Voltar")
        btn_back.clicked.connect(lambda: self.back_signal.emit())
        layout.addWidget(btn_back)

        self.setLayout(layout)

        # If you want to instantiate cam_face_recognition here, do so (and adapt logic).
        # self.face_rec = cam_face_recognition(...)

        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)

        self.cap = None

    def start_recognition(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        self.timer.start(30)  # ~30 FPS

    def process_frame(self):
        """
        Simplified logic for demonstration.
        Replace with your cam_face_recognition logic if you prefer.
        """
        ret, frame = self.cap.read()
        if not ret:
            return

        # Here you could run face_recognition checks:
        recognized = False  # Change this according to your recognition result

        # If recognized:
        # QMessageBox.information(self, "Sucesso", "Entrada confirmada!")
        # self.timer.stop()

        # If not recognized but a face was detected:
        # QMessageBox.warning(self, "Aviso", "Rosto não reconhecido!")
        # self.timer.stop()

        # Optionally show the frame or do additional logic

    def closeEvent(self, event):
        """
        Closes the camera properly when the page is closed.
        """
        self.timer.stop()
        if self.cap:
            self.cap.release()
        super().closeEvent(event)


# ==========================
# AddUserPage
# ==========================
class AddUserPage(QWidget):
    """
    This page displays a form (CRUD) to add a new user:
    - Fields: Name, Last Name, Gender, etc.
    - "Tirar Foto" button triggers the camera and saves a photo in temp_user.
    - "Salvar Usuário" button stores user data in Firebase/local.
    """
    back_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.user_manager = None

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.input_name = QLineEdit()
        self.input_lastname = QLineEdit()
        self.input_gender = QLineEdit()
        self.input_userid = QLineEdit()

        form_layout.addRow("Nome:", self.input_name)
        form_layout.addRow("Sobrenome:", self.input_lastname)
        form_layout.addRow("Gênero:", self.input_gender)
        form_layout.addRow("ID (opcional):", self.input_userid)

        layout.addLayout(form_layout)

        btn_take_photo = QPushButton("Tirar Foto")
        btn_take_photo.clicked.connect(self.take_photo)
        layout.addWidget(btn_take_photo)

        btn_save = QPushButton("Salvar Usuário")
        btn_save.clicked.connect(self.save_user)
        layout.addWidget(btn_save)

        btn_back = QPushButton("Voltar")
        btn_back.clicked.connect(lambda: self.back_signal.emit())
        layout.addWidget(btn_back)

        self.setLayout(layout)

    def take_photo(self):
        """
        Opens the camera in an OpenCV window. 
        Press 'w' to save the photo to the 'temp_user' folder. 
        Press 'q' to quit without saving.
        """
        # We import inside the method to avoid issues with circular references.
        if not self.user_manager:
            from src.firebase.user_image_manager import UserImageManager
            self.user_manager = UserImageManager()

        temp_dir = self.user_manager.temp_dir
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            QMessageBox.critical(self, "Error", "Could not open the camera.")
            return

        saved_image_path = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow('Webcam', frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('w'):
                image_filename = os.path.join(temp_dir, 'photo.jpg')
                cv2.imwrite(image_filename, frame)
                saved_image_path = image_filename
                print(f'Image saved as {image_filename}')
                break

            if key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if saved_image_path:
            QMessageBox.information(self, "Photo Saved", f"Image saved as: {saved_image_path}")
        else:
            QMessageBox.warning(self, "No Photo", "No photo was saved.")

    def save_user(self):
        name = self.input_name.text()
        lastname = self.input_lastname.text()
        gender = self.input_gender.text()
        user_id = self.input_userid.text().strip() or None

        if not self.user_manager:
            from src.firebase.user_image_manager import UserImageManager
            self.user_manager = UserImageManager()

        try:
            new_id = self.user_manager.create_user(name, lastname, gender, user_id)
            QMessageBox.information(self, "Sucesso", f"Usuário criado com ID: {new_id}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))


# ==========================
# RemoveUserPage
# ==========================
class RemoveUserPage(QWidget):
    """
    Displays a list of existing users from Firebase, 
    allows the user to select one and remove it, then shows a confirmation.
    """
    back_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.user_manager = None

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_remove = QPushButton("Remover Selecionado")
        btn_remove.clicked.connect(self.remove_user)
        layout.addWidget(btn_remove)

        btn_back = QPushButton("Voltar")
        btn_back.clicked.connect(lambda: self.back_signal.emit())
        layout.addWidget(btn_back)

        self.setLayout(layout)

        self.load_users()

    def load_users(self):
        from src.firebase.fire import FirebaseManager
        fm = FirebaseManager()
        all_users = fm.get_all_users()  # { user_id: { "name": ..., "last_name": ... }, ... }

        if all_users:
            for uid, data in all_users.items():
                item_text = f"{uid} - {data.get('name','')} {data.get('last_name','')}"
                list_item = QListWidgetItem(item_text)
                list_item.setData(0, uid)
                self.list_widget.addItem(list_item)

    def remove_user(self):
        selected_item = self.list_widget.currentItem()
        if not selected_item:
            return
        user_id = selected_item.data(0)

        ret = QMessageBox.question(self, "Confirmar", f"Tem certeza que deseja remover o usuário {user_id}?")
        if ret == QMessageBox.Yes:
            if not self.user_manager:
                from src.firebase.user_image_manager import UserImageManager
                self.user_manager = UserImageManager()

            try:
                msg = self.user_manager.delete_user(user_id)
                QMessageBox.information(self, "Removido", msg)
                self.list_widget.clear()
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))


# ==========================
# MainWindow
# ==========================
class MainWindow(QMainWindow):
    """
    This MainWindow manages all pages with a QStackedWidget:
    - Index 0: HomePage
    - Index 1: VideoPage (YOLO)
    - Index 2: FaceRecHome
    - Index 3: FaceRecRunPage
    - Index 4: AddUserPage
    - Index 5: RemoveUserPage
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ECOA_CAM_DETECTION - Integração YOLO + Reconhecimento Facial")

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # 0) HomePage
        self.home_page = HomePage()
        self.home_page.go_to_cameras_signal.connect(self.go_to_cameras)
        self.home_page.go_to_face_rec_signal.connect(self.go_to_face_rec)
        self.stacked.addWidget(self.home_page)

        # 1) VideoPage (YOLO). Adapt your import according to your code.
        from src.yolo_method.people_counter import VideoPage
        self.video_page = VideoPage()
        self.video_page.back_to_start_signal.connect(self.go_home)
        self.stacked.addWidget(self.video_page)

        # 2) FaceRecHome
        self.face_rec_home = FaceRecHome()
        self.face_rec_home.go_run_face_signal.connect(self.go_run_face)
        self.face_rec_home.go_add_user_signal.connect(self.go_add_user)
        self.face_rec_home.go_remove_user_signal.connect(self.go_remove_user)
        self.stacked.addWidget(self.face_rec_home)

        # 3) FaceRecRunPage
        self.face_run_page = FaceRecRunPage()
        self.face_run_page.back_signal.connect(self.go_face_home)
        self.stacked.addWidget(self.face_run_page)

        # 4) AddUserPage
        self.add_user_page = AddUserPage()
        self.add_user_page.back_signal.connect(self.go_face_home)
        self.stacked.addWidget(self.add_user_page)

        # 5) RemoveUserPage
        self.remove_user_page = RemoveUserPage()
        self.remove_user_page.back_signal.connect(self.go_face_home)
        self.stacked.addWidget(self.remove_user_page)

        self.stacked.setCurrentIndex(0)

    def go_home(self):
        self.stacked.setCurrentIndex(0)

    def go_to_cameras(self):
        self.stacked.setCurrentIndex(1)

    def go_to_face_rec(self):
        self.stacked.setCurrentIndex(2)

    def go_face_home(self):
        self.stacked.setCurrentIndex(2)

    def go_run_face(self):
        self.stacked.setCurrentIndex(3)

    def go_add_user(self):
        self.stacked.setCurrentIndex(4)

    def go_remove_user(self):
        self.stacked.setCurrentIndex(5)

    def closeEvent(self, event):
        # If you need to clean up resources before closing, do it here
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
