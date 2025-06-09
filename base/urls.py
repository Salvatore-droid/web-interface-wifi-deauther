from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('verify-password/', views.verify_password, name='verify_password'),
    path('scan/', views.scan_networks, name='scan_networks'),
    path('attack/', views.start_attack, name='start_attack'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logs/', views.view_logs, name='view_logs'),
    path('profile/', views.profile, name='profile'),
]