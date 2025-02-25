from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
from django.shortcuts import render, redirect
from django import forms
import os
import sys

# Adiciona o caminho da pasta src ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

CURRENT_DIR = os.path.dirname(__file__)
USERS_IMG_DIR = os.path.join(CURRENT_DIR,'..' ,'static', 'users_imgage')

# Agora pode importar o UserImageManager
from firebase.user_image_manager import UserImageManager


# Definição do formulário
class UserForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=100)
    last_name = forms.CharField(label='Sobrenome', max_length=100)
    gender = forms.ChoiceField(label='Gênero', choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])
    image = forms.ImageField(label='Imagem')

# Caminho da pasta temp_user
temp_user_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src','local_database','temp_user'))

# Criando o usuário no Firebase
manager = UserImageManager()

# View para processar o formulário
def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['image']
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            gender = form.cleaned_data['gender']
            
            # Salvando a imagem na pasta temp_user
            image_path = os.path.join(temp_user_folder, image.name)
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
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
    users = manager.firebase_manager.get_all_users()  # Obtendo todos os usuários do Firebase
    
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


def update_user(request, user_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        image = request.FILES.get('image')

        print(name, last_name, gender, user_id)

        if image:
            image_path = os.path.join(temp_user_folder, image.name)
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

        try:
            manager.update_user_data(name, last_name, gender, user_id)
            return JsonResponse({"message": "Usuário atualizado com sucesso!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Requisição inválida"}, status=400)