#################################
# IMPORTS 
#################################
import sys
import os
import shutil

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QComboBox
)
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from PyQt5.QtGui import QPixmap, QImage

import firebase_admin
from firebase_admin import credentials

current_dir = os.path.dirname(os.path.abspath(__file__))
service_account_path = os.path.join(current_dir, 'src', 'firebase', 'serviceAccountKey.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://ecoa-camera-default-rtdb.firebaseio.com'
    })

#################################
# IMPORTS DO SEU PROJETO
#################################
# Não estamos mais fazendo monkey patch no main.py,
# pois vamos deixar o fire.py inicializar o Firebase (com a verificação interna).
from src.firebase.user_image_manager import UserImageManager
from src.firebase.fire import FirebaseManager

#################################
# 1) HOME PAGE
#################################
class HomePage(QWidget):
    """
    Tela inicial com dois botões:
      - 'Câmeras' (YOLO)
      - 'Reconhecimento Facial'
    Emite sinais para que o MainWindow decida para qual funcionalidade ir.
    """
    go_to_cameras_signal = pyqtSignal()
    go_to_face_rec_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label_title = QLabel("Bem-vindo! Escolha uma opção:")
        layout.addWidget(label_title)
        btn_cameras = QPushButton("Câmeras")
        btn_cameras.clicked.connect(lambda: self.go_to_cameras_signal.emit())
        layout.addWidget(btn_cameras)
        btn_face = QPushButton("Reconhecimento Facial")
        btn_face.clicked.connect(lambda: self.go_to_face_rec_signal.emit())
        layout.addWidget(btn_face)
        self.setLayout(layout)

#################################
# 2) VIDEO PAGE (YOLO)
#################################
# Supondo que o VideoPage já exista em src/yolo_method/people_counter.py.
from src.yolo_method.people_counter import VideoPage

#################################
# 3) PÁGINAS DE RECONHECIMENTO FACIAL (ESTRUTURA SEMELHANTE AO SITE)
#################################

# 3.1 – Página Index do Reconhecimento Facial (equivalente a index.html)
class IndexFacePage(QWidget):
    go_add_user_signal = pyqtSignal()
    go_list_users_signal = pyqtSignal()
    go_run_face_signal = pyqtSignal()  # Novo sinal para reconhecimento facial

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("Reconhecimento Facial - Index")
        layout.addWidget(label)
        btn_add = QPushButton("Adicionar Usuário")
        btn_add.clicked.connect(lambda: self.go_add_user_signal.emit())
        layout.addWidget(btn_add)
        btn_list = QPushButton("Ver Todos os Usuários")
        btn_list.clicked.connect(lambda: self.go_list_users_signal.emit())
        layout.addWidget(btn_list)
        # Botão novo para iniciar reconhecimento facial
        btn_run = QPushButton("Realizar Reconhecimento Facial")
        btn_run.clicked.connect(lambda: self.go_run_face_signal.emit())
        layout.addWidget(btn_run)
        self.setLayout(layout)

# 3.2 – Página de Adição de Usuário
class AddUserPage(QWidget):
    go_back_signal = pyqtSignal()
    go_success_signal = pyqtSignal(str)  # Emite mensagem de sucesso

    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserImageManager()
        self.chosen_image_path = None
        layout = QVBoxLayout()
        label = QLabel("Adicionar Usuário")
        layout.addWidget(label)
        form_layout = QFormLayout()
        self.input_name = QLineEdit()
        self.input_last_name = QLineEdit()
        self.input_gender = QComboBox()
        self.input_gender.addItems(["M", "F", "O"])
        form_layout.addRow("Nome:", self.input_name)
        form_layout.addRow("Sobrenome:", self.input_last_name)
        form_layout.addRow("Gênero:", self.input_gender)
        layout.addLayout(form_layout)
        btn_upload = QPushButton("Escolher Imagem (upload)")
        btn_upload.clicked.connect(self.choose_image_from_disk)
        layout.addWidget(btn_upload)
        btn_photo = QPushButton("Tirar Foto (Webcam)")
        btn_photo.clicked.connect(self.take_photo_with_webcam)
        layout.addWidget(btn_photo)
        btn_save = QPushButton("Adicionar Usuário")
        btn_save.clicked.connect(self.save_user)
        layout.addWidget(btn_save)
        btn_back = QPushButton("Voltar")
        btn_back.clicked.connect(lambda: self.go_back_signal.emit())
        layout.addWidget(btn_back)
        self.setLayout(layout)

    def choose_image_from_disk(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecione a imagem", "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.chosen_image_path = file_path
            QMessageBox.information(self, "Imagem Selecionada", f"Imagem: {file_path}")

    def take_photo_with_webcam(self):
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            QMessageBox.critical(self, "Erro", "Não foi possível abrir a webcam")
            return
        saved_image_path = None
        temp_dir = self.user_manager.temp_dir
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('Webcam (W = salvar, Q = sair)', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('w'):
                image_filename = os.path.join(temp_dir, 'photo.jpg')
                cv2.imwrite(image_filename, frame)
                saved_image_path = image_filename
                print(f'Imagem salva em {image_filename}')
                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        if saved_image_path:
            self.chosen_image_path = saved_image_path
            QMessageBox.information(self, "Foto Salva", f"Imagem: {saved_image_path}")

    def save_user(self):
        name = self.input_name.text().strip()
        last_name = self.input_last_name.text().strip()
        gender = self.input_gender.currentText()
        if not name or not last_name:
            QMessageBox.warning(self, "Campos Incompletos", "Preencha Nome e Sobrenome")
            return
        if self.chosen_image_path and os.path.exists(self.chosen_image_path):
            import shutil
            temp_dir = self.user_manager.temp_dir
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)
            dst_path = os.path.join(temp_dir, 'photo.jpg')
            # Verifica se os caminhos são diferentes antes de copiar
            if not os.path.samefile(self.chosen_image_path, dst_path):
                shutil.copy2(self.chosen_image_path, dst_path)
        else:
            QMessageBox.warning(self, "Sem Imagem", "Não há imagem selecionada/tirada.")
            return
        try:
            new_id = self.user_manager.create_user(name, last_name, gender)
            self.go_success_signal.emit(f"Usuário {new_id} criado com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

# 3.3 – Página de Listagem de Usuários
class ListUsersPage(QWidget):
    go_back_signal = pyqtSignal()
    go_edit_user_signal = pyqtSignal(str)  # Passa user_id
    go_success_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserImageManager()
        self.firebase_manager = FirebaseManager()
        layout = QVBoxLayout()
        label = QLabel("Lista de Usuários")
        layout.addWidget(label)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        btn_back = QPushButton("Voltar")
        btn_back.clicked.connect(lambda: self.go_back_signal.emit())
        layout.addWidget(btn_back)
        self.setLayout(layout)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_users()

    def load_users(self):
        self.list_widget.clear()
        all_users = self.firebase_manager.get_all_users()
        if not all_users:
            return
        for uid, data in all_users.items():
            name = data.get("name", "")
            last_name = data.get("last_name", "")
            item_text = f"{uid} - {name} {last_name}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, uid)
            self.list_widget.addItem(item)
        self.list_widget.itemDoubleClicked.connect(self.edit_selected_user)

    def edit_selected_user(self, item):
        if not item:
            return
        uid = item.data(Qt.UserRole)
        self.go_edit_user_signal.emit(uid)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            item = self.list_widget.currentItem()
            if item:
                uid = item.data(Qt.UserRole)
                self.delete_user(uid)
        else:
            super().keyPressEvent(event)

    def delete_user(self, user_id):
        reply = QMessageBox.question(self, "Confirmar", f"Excluir usuário {user_id}?")
        if reply == QMessageBox.Yes:
            try:
                msg = self.user_manager.delete_user(user_id)
                QMessageBox.information(self, "OK", msg)
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

# 3.4 – Página de Edição de Usuário
class EditUserPage(QWidget):
    go_back_signal = pyqtSignal()
    go_success_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserImageManager()
        self.current_user_id = None
        self.chosen_image_path = None
        layout = QVBoxLayout()
        label = QLabel("Modificar Usuário")
        layout.addWidget(label)
        self.form_layout = QFormLayout()
        self.input_name = QLineEdit()
        self.input_last_name = QLineEdit()
        self.input_gender = QComboBox()
        self.input_gender.addItems(["M", "F", "O"])
        self.form_layout.addRow("Nome:", self.input_name)
        self.form_layout.addRow("Sobrenome:", self.input_last_name)
        self.form_layout.addRow("Gênero:", self.input_gender)
        layout.addLayout(self.form_layout)
        btn_upload = QPushButton("Escolher Nova Imagem")
        btn_upload.clicked.connect(self.choose_image_from_disk)
        layout.addWidget(btn_upload)
        btn_save = QPushButton("Salvar Alterações")
        btn_save.clicked.connect(self.save_changes)
        layout.addWidget(btn_save)
        btn_back = QPushButton("Voltar")
        btn_back.clicked.connect(lambda: self.go_back_signal.emit())
        layout.addWidget(btn_back)
        self.setLayout(layout)

    def load_user_data(self, user_id):
        self.current_user_id = user_id
        fm = FirebaseManager()
        data = fm.get_user(user_id)
        if not data:
            QMessageBox.critical(self, "Erro", f"Usuário {user_id} não encontrado.")
            return
        self.input_name.setText(data.get("name", ""))
        self.input_last_name.setText(data.get("last_name", ""))
        gender = data.get("gender", "O")
        idx = self.input_gender.findText(gender)
        if idx >= 0:
            self.input_gender.setCurrentIndex(idx)

    def choose_image_from_disk(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecione a nova imagem", "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.chosen_image_path = file_path
            QMessageBox.information(self, "Nova Imagem", file_path)

    def save_changes(self):
        if not self.current_user_id:
            QMessageBox.warning(self, "Erro", "Nenhum usuário carregado.")
            return
        name = self.input_name.text().strip()
        last_name = self.input_last_name.text().strip()
        gender = self.input_gender.currentText()
        if not name or not last_name:
            QMessageBox.warning(self, "Campos Incompletos", "Preencha nome e sobrenome.")
            return
        if self.chosen_image_path:
            import shutil
            temp_dir = self.user_manager.temp_dir
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            dst_path = os.path.join(temp_dir, 'photo.jpg')
            shutil.copy2(self.chosen_image_path, dst_path)
        try:
            updated_id = self.user_manager.update_user_data(name, last_name, gender, self.current_user_id)
            self.go_success_signal.emit(f"Usuário {updated_id} modificado!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

# 3.5 – Página de Sucesso (Opcional)
class SuccessPage(QWidget):
    go_back_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.label_msg = QLabel("Sucesso!")
        layout.addWidget(self.label_msg)
        btn_back = QPushButton("Voltar ao Início do Reconhecimento Facial")
        btn_back.clicked.connect(lambda: self.go_back_signal.emit())
        layout.addWidget(btn_back)
        self.setLayout(layout)

    def set_success_text(self, text):
        self.label_msg.setText(text)

#################################
# 4) FUNÇÃO DE RECONHECIMENTO FACIAL
#    (Aproveitando o código da pasta face_recognition)
#################################
# Criaremos um worker para rodar a classe cam_face_recognition em uma thread separada
from PyQt5.QtCore import QThread

class FaceRecWorker(QThread):
    recognized_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Importa a classe cam_face_recognition do módulo face_recognition_
        from src.face_recognition.face_recognition_ import cam_face_recognition, known_people_loader
        # Carrega pessoas conhecidas (ajuste conforme sua implementação)
        # Se o construtor de known_people_loader não precisar de parâmetros, ou passe o diretório correto
        self.known_people = known_people_loader(os.path.join(os.path.dirname(__file__), 'src', 'local_database', 'users'))
        self.recognizer = cam_face_recognition(self.known_people, wait_time=5)
    
    def run(self):
        try:
            # Aqui chamamos o método run() que executa o loop de reconhecimento.
            # Para integração, vamos supor que esse método retorna o nome reconhecido quando encontrar um rosto,
            # ou retorna uma string indicando "Não reconhecido" após um tempo.
            result = self.recognizer.run()  # OBS: O método run() do seu código original pode precisar ser adaptado para retornar algo.
            if result:
                self.recognized_signal.emit(result)
            else:
                self.error_signal.emit("Rosto não reconhecido")
        except Exception as e:
            self.error_signal.emit(str(e))

# Página para rodar o reconhecimento facial usando o worker acima.
class FaceRecRunPage(QWidget):
    back_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.label_info = QLabel("Clique em 'Iniciar' para realizar reconhecimento facial.")
        layout.addWidget(self.label_info)
        self.video_label = QLabel("Video Feed")
        layout.addWidget(self.video_label)
        btn_start = QPushButton("Iniciar Reconhecimento Facial")
        btn_start.clicked.connect(self.start_recognition)
        layout.addWidget(btn_start)
        btn_back = QPushButton("Voltar")
        btn_back.clicked.connect(lambda: self.back_signal.emit())
        layout.addWidget(btn_back)
        self.setLayout(layout)
        self.worker = None  # Worker do reconhecimento

    def start_recognition(self):
        if self.worker is None:
            self.worker = FaceRecWorker()
            self.worker.recognized_signal.connect(self.on_recognized)
            self.worker.error_signal.connect(self.on_error)
            self.worker.start()
        else:
            # Se já existe um worker, reinicia-o
            self.worker.terminate()
            self.worker = FaceRecWorker()
            self.worker.recognized_signal.connect(self.on_recognized)
            self.worker.error_signal.connect(self.on_error)
            self.worker.start()

    def on_recognized(self, name):
        QMessageBox.information(self, "Sucesso", f"Rosto reconhecido: {name}")
        # Você pode optar por parar a thread ou voltar ao index
        self.worker.terminate()
        self.worker = None

    def on_error(self, error_msg):
        QMessageBox.warning(self, "Aviso", error_msg)
        self.worker.terminate()
        self.worker = None

#################################
# 5) FACE REC CONTAINER
#################################
class FaceRecContainer(QWidget):
    """
    Container com todas as páginas de Reconhecimento Facial, semelhante ao fluxo do site:
      - IndexFacePage
      - AddUserPage
      - ListUsersPage
      - EditUserPage
      - SuccessPage
      - FaceRecRunPage (para reconhecimento em tempo real)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stacked = QStackedWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked)
        self.setLayout(main_layout)
        # Índice 0: IndexFacePage
        self.index_page = IndexFacePage()
        self.index_page.go_add_user_signal.connect(self.go_add_user)
        self.index_page.go_list_users_signal.connect(self.go_list_users)
        self.index_page.go_run_face_signal.connect(self.go_run_face)
        self.stacked.addWidget(self.index_page)
        # Índice 1: AddUserPage
        self.add_user_page = AddUserPage()
        self.add_user_page.go_back_signal.connect(self.go_index)
        self.add_user_page.go_success_signal.connect(self.go_success)
        self.stacked.addWidget(self.add_user_page)
        # Índice 2: ListUsersPage
        self.list_users_page = ListUsersPage()
        self.list_users_page.go_back_signal.connect(self.go_index)
        self.list_users_page.go_edit_user_signal.connect(self.go_edit_user)
        self.stacked.addWidget(self.list_users_page)
        # Índice 3: EditUserPage
        self.edit_user_page = EditUserPage()
        self.edit_user_page.go_back_signal.connect(self.go_list_users)
        self.edit_user_page.go_success_signal.connect(self.go_success)
        self.stacked.addWidget(self.edit_user_page)
        # Índice 4: SuccessPage
        self.success_page = SuccessPage()
        self.success_page.go_back_signal.connect(self.go_index)
        self.stacked.addWidget(self.success_page)
        # Índice 5: FaceRecRunPage (novo)
        self.face_run_page = FaceRecRunPage()
        self.face_run_page.back_signal.connect(self.go_index)
        self.stacked.addWidget(self.face_run_page)
        # Inicia na página index
        self.stacked.setCurrentIndex(0)

    def go_index(self):
        self.stacked.setCurrentIndex(0)

    def go_add_user(self):
        self.stacked.setCurrentIndex(1)

    def go_list_users(self):
        self.stacked.setCurrentIndex(2)

    def go_edit_user(self, user_id):
        self.edit_user_page.load_user_data(user_id)
        self.stacked.setCurrentIndex(3)

    def go_success(self, msg):
        self.success_page.set_success_text(msg)
        self.stacked.setCurrentIndex(4)

    def go_run_face(self):
        self.stacked.setCurrentIndex(5)

#################################
# 6) MAIN WINDOW
#################################
class MainWindow(QMainWindow):
    """
    Janela principal com três funcionalidades:
      - Índice 0: HomePage (botões: 'Câmeras' e 'Reconhecimento Facial')
      - Índice 1: VideoPage (YOLO)
      - Índice 2: FaceRecContainer (fluxo de CRUD + reconhecimento facial)
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ECOA_CAM_DETECTION")
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)
        # Índice 0: HomePage
        self.home_page = HomePage()
        self.home_page.go_to_cameras_signal.connect(self.go_to_cameras)
        self.home_page.go_to_face_rec_signal.connect(self.go_to_face_rec)
        self.stacked.addWidget(self.home_page)
        # Índice 1: VideoPage (YOLO)
        self.video_page = VideoPage()
        self.video_page.back_to_start_signal.connect(self.go_home)
        self.stacked.addWidget(self.video_page)
        # Índice 2: FaceRecContainer
        self.face_rec_container = FaceRecContainer()
        self.stacked.addWidget(self.face_rec_container)
        self.stacked.setCurrentIndex(0)

    def go_home(self):
        self.stacked.setCurrentIndex(0)

    def go_to_cameras(self):
        reply = QMessageBox.question(
            self,
            "Selecione a fonte",
            "Deseja abrir a webcam (Yes) ou um arquivo de vídeo (No)?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.video_page.open_camera()
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Selecione o arquivo de vídeo",
                "",
                "Vídeos (*.mp4 *.avi *.mov);;Todos (*)"
            )
            if file_path:
                self.video_page.open_video_file(file_path)
        self.stacked.setCurrentIndex(1)

    def go_to_face_rec(self):
        self.stacked.setCurrentIndex(2)

#################################
# 7) FUNÇÃO MAIN
#################################
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
