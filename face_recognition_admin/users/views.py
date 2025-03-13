from django.shortcuts import render
from django.http import JsonResponse
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

# Add the path to the src folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

CURRENT_DIR = os.path.dirname(__file__)
USERS_IMG_DIR = os.path.join(CURRENT_DIR,'..' ,'static', 'users_imgage')

# Agora pode importar o UserImageManager
from firebase.user_image_manager import UserImageManager

class UserForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=100)
    last_name = forms.CharField(label='Sobrenome', max_length=100)
    gender = forms.ChoiceField(label='Gênero', choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])
    image = forms.ImageField(label='Imagem', required=False)  # Campo opcional

# Caminho da pasta temp_user
temp_user_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src','local_database','temp_user'))

# Criando o usuário no Firebase
manager = UserImageManager()

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


