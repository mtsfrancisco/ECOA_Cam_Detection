from django.urls import path
from .views import add_user, success_view

urlpatterns = [
    path('add/', add_user, name='add_user'),
    path('success/', success_view, name='success'),
]
