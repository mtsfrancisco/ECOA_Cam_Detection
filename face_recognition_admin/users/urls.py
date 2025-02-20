from django.urls import path
from .views import add_user, success_view, index

urlpatterns = [
    path('', index, name='index'),
    path('add/', add_user, name='add_user'),
    path('success/', success_view, name='success'),
]
