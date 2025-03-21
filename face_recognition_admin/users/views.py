from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
import base64
import uuid 
from django.shortcuts import render, redirect
from django import forms
import os
import sys
from django.views.decorators.csrf import csrf_exempt
import base64
from io import BytesIO
from PIL import Image
import cv2
import time
import face_recognition

# Add the path to the src folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

CURRENT_DIR = os.path.dirname(__file__)
USERS_IMG_DIR = os.path.join(CURRENT_DIR,'..' ,'static', 'users_imgage')

# Import UserImageManager and HistoryManager
from firebase.user_image_manager import UserImageManager
from firebase.history_manager import HistoryManager

# Correctly locate the face_recognition_.py file
face_recognition_module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'face_recognition'))
sys.path.append(face_recognition_module_path)
from face_recognition_ import known_people_loader, cam_face_recognition

class UserForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=100)
    last_name = forms.CharField(label='Sobrenome', max_length=100)
    gender = forms.ChoiceField(label='Gênero', choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])
    image = forms.ImageField(label='Imagem', required=False)  # Campo opcional

# Caminho da pasta temp_user
temp_user_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src','local_database','temp_user'))

manager = UserImageManager()
history_manager = HistoryManager()

# View para processar o formulário
def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            gender = form.cleaned_data['gender']

            captured_image = request.POST.get('captured_image')  # Imagem da webcam

            if captured_image:
                # Converte a imagem base64 em arquivo e salva na pasta temp_user

                image_data = captured_image.split(',')[1]
                image_binary = base64.b64decode(image_data)

                image_path = os.path.join(temp_user_folder, f"{name}.png")
                with open(image_path, 'wb') as f:
                    f.write(image_binary)
            
            try:
                user_id = manager.create_user(name, last_name, gender)
                return redirect('success')
            except Exception as e:
                return render(request, 'users/add_user.html', {'form': form, 'error': str(e)})
    else:
        form = UserForm()
    return render(request, 'users/add_user.html', {'form': form})

# View to setup the camera
def camera_setup(request):
    return render(request, 'users/camera_setup.html')

# View para mostrar a página de sucesso
def success_view(request):
    return render(request, 'users/success.html')

def index(request):
    return render(request, 'users/index.html')

def list_users(request):
    #users = manager.firebase_manager.get_all_users()  # Obtendo todos os usuários do Firebase
    
    # Obtenha todos os usuarios localmente
    users = manager.get_all_local_users()

    # Convertendo os dados para uma lista de dicionários
    users_list = []
    for user_id, user_data in users.items():
        users_list.append({
            'user_id': user_id,
            'name': user_data.get('name', ''),
            'last_name': user_data.get('last_name', ''),
            'gender': user_data.get('gender', ''),
            'image_64': user_data.get('image_64', ''),  # Base64 da imagem
        })

    return render(request, 'users/list_users.html', {'users': users_list})

@csrf_exempt
def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            manager.delete_user(user_id)
            return JsonResponse({'message': f'Usuário {user_id} excluído com sucesso.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def edit_user(request, user_id):
    user_data = manager.firebase_manager.get_user(user_id)
    
    if not user_data:
        return render(request, 'users/error.html', {'message': 'Usuário não encontrado'})
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            gender = form.cleaned_data['gender']
            captured_image = request.POST.get('captured_image')  # Imagem capturada pela webcam

            image_path = None
            
            if 'image' in request.FILES:
                # Se o usuário fez upload de uma imagem
                image = request.FILES['image']
                image_path = os.path.join(temp_user_folder, image.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

            elif captured_image:
                # Se o usuário capturou uma imagem com a webcam
                image_data = captured_image.split(',')[1]  # Remove o cabeçalho data:image/png;base64,
                image_binary = base64.b64decode(image_data)
                image_path = os.path.join(temp_user_folder, f"{user_id}.png")
                with open(image_path, 'wb') as f:
                    f.write(image_binary)

            # Atualiza os dados do usuário
            try:
                manager.update_user_data(name, last_name, gender, user_id)
                return redirect('list_users')
            except Exception as e:
                return render(request, 'users/edit_user.html', {'form': form, 'user_id': user_id, 'error': str(e)})
        
    else:
        form = UserForm(initial={
            'name': user_data.get('name', ''),
            'last_name': user_data.get('last_name', ''),
            'gender': user_data.get('gender', ''),
        })

    return render(request, 'users/edit_user.html', {'form': form, 'user_id': user_id})

def list_history(request):
    history_data = history_manager.get_all_history()

    # Convertendo o dicionário aninhado em uma lista de eventos
    history_list = []
    for user_id, user_histories in history_data.items():
        for history_id, history in user_histories.items():
            history_list.append({
                'user_id': history.get('user_id', ''),
                'name': history.get('name', ''),
                'date': history.get('date', ''),
                'time': history.get('time', ''),
                'status': history.get('status', '')
            })

    # Ordenando os eventos por data e hora
    history_list.sort(key=lambda x: (x['date'], x['time']), reverse=True)

    return render(request, 'users/history.html', {'history': history_list})

def generate_video_feed():
    known_persons = known_people_loader(USERS_DIRECTORY)
    face_recognizer = cam_face_recognition(known_persons)
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Process the frame with face recognition
        face_recognizer.draw_square(frame)
        if time.time() - face_recognizer.last_check_time >= face_recognizer.wait_time:
            roi = frame[face_recognizer.y_start:face_recognizer.y_end, face_recognizer.x_start:face_recognizer.x_end]
            rgb_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_roi)
            if face_encodings:
                person = face_recognizer.recognize_face(face_encodings)
                if person:
                    face_recognizer.display_person_info(frame, person)
                else:
                    analysis = face_recognizer.analyze_face(roi)
                    face_recognizer.display_unknown_person_info(frame, analysis)
            face_recognizer.last_check_time = time.time()

        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    video_capture.release()

def video_feed(request):
    return StreamingHttpResponse(generate_video_feed(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


