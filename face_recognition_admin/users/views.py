from django.shortcuts import render
from django.http import JsonResponse
import base64
import uuid  # Adicionado para gerar nomes únicos para imagens capturadas
# Create your views here.
from django.shortcuts import render, redirect
from django import forms
import os
import sys
from django.views.decorators.csrf import csrf_exempt

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
        
        # Verifica se a imagem veio da webcam ou foi carregada
        image_base64 = request.POST.get("image_base64", None)

        if form.is_valid():
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            gender = form.cleaned_data['gender']

            # Se for uma imagem carregada do computador
            if 'image' in request.FILES:
                image = request.FILES['image']
                image_path = os.path.join(temp_user_folder, image.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

            # Se for uma imagem capturada da webcam
            elif image_base64:
                format, imgstr = image_base64.split(';base64,')
                ext = format.split('/')[-1]
                image_name = f"{uuid.uuid4()}.{ext}"
                image_path = os.path.join(temp_user_folder, image_name)

                with open(image_path, "wb") as img_file:
                    img_file.write(base64.b64decode(imgstr))

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

class UserForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=100)
    last_name = forms.CharField(label='Sobrenome', max_length=100)
    gender = forms.ChoiceField(label='Gênero', choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])
    image = forms.ImageField(label='Imagem', required=False)  # Campo opcional

def edit_user(request, user_id):
    # Obtém os dados do usuário no Firebase
    user_data = manager.firebase_manager.get_user(user_id)

    if not user_data:
        return render(request, 'users/error.html', {'message': 'Usuário não encontrado'})

    if request.method == 'POST':
        print('Recebendo dados do formulário...')
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            print('Formulário válido')
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            gender = form.cleaned_data['gender']

            # Se houver nova imagem, salvamos na pasta temp_user
            if 'image' in request.FILES:
                image = request.FILES['image']
                image_path = os.path.join(temp_user_folder, image.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
            
            # Chama a função de atualização
            try:
                print('Atualizando usuário...')
                manager.update_user_data(name, last_name, gender, user_id)
                return redirect('list_users')  # Redireciona para a lista de usuários após atualização
            except Exception as e:
                return render(request, 'users/edit_user.html', {'form': form, 'user_id': user_id, 'error': str(e)})
        else:
            # Adicione esta linha para depurar os erros do formulário
            print('Erros do formulário:', form.errors)
    else:
        # Preenche o formulário com os dados atuais do usuário
        form = UserForm(initial={
            'name': user_data.get('name', ''),
            'last_name': user_data.get('last_name', ''),
            'gender': user_data.get('gender', ''),
        })

    return render(request, 'users/edit_user.html', {'form': form, 'user_id': user_id})



