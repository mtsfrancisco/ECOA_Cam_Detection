from django.urls import path
from .views import add_user, success_view, index, list_users, update_user

urlpatterns = [
    path('', index, name='index'),
    path('add/', add_user, name='add_user'),
    path('success/', success_view, name='success'),
    path('list/', list_users, name='list_users'),
    path("update_user/<str:user_id>/", update_user, name="update_user"),
]
