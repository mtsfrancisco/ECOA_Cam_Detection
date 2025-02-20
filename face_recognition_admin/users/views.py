from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django import forms
import os
import sys

# Adiciona o caminho da pasta src ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

# Agora pode importar o UserImageManager
# Talvez precise tirar o src do caminho
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
            name = form.cleaned_data['name']
            last_name = form.cleaned_data['last_name']
            gender = form.cleaned_data['gender']
            image = request.FILES['image']
            
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
