# Em teacher_portal/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views 
# --- ADIÇÃO IMPORTANTE ---
from . import views  # Importa o arquivo views.py que acabamos de preencher

app_name = 'teacher_portal'

urlpatterns = [
    # --- PÁGINA DE LOGIN ---
    path(
        'login/', 
        auth_views.LoginView.as_view(
            template_name='teacher_portal/login.html',
            redirect_authenticated_user=True 
        ),
        name='login'
    ),

    # --- PÁGINA DE LOGOUT ---
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='teacher_portal:login' # Redireciona para a página de login após o logout
        ),
        name='logout'
    ),
    
    # --- PÁGINA DO DASHBOARD ---
    path(
        'dashboard/',
        views.dashboard_view, #  a chamada para a view
        name='dashboard'      
    ),
]