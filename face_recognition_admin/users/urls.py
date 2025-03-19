from django.urls import path
from .views import add_user, success_view, index, list_users, edit_user, delete_user, camera_setup, list_history

urlpatterns = [
    path('', index, name='index'),
    path('add/', add_user, name='add_user'),
    path('success/', success_view, name='success'),
    path('list/', list_users, name='list_users'),
    path('edit_user/<str:user_id>/', edit_user, name='edit_user'),
    path('delete_user/<str:user_id>/', delete_user, name='delete_user'),
    path('camera_setup/', camera_setup, name='camera_setup'),
    path('list_history/', list_history, name='list_history'),
]
