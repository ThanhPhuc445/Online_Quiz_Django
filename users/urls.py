from django.urls import path
from . import views

urlpatterns = [
    # Khi người dùng truy cập /accounts/register/, gọi view 'register'
    path('register/', views.register, name='register'),
]