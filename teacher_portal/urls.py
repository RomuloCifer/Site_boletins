from django.urls import path
from django.contrib.auth import views as auth_views # Importamos as views prontas do Django

app_name = 'teacher_portal'

urlpatterns = [
    # --- PÁGINA DE LOGIN ---
    path(
        'login/', 
        auth_views.LoginView.as_view(
            # Dizemos ao Django para usar nosso template customizado
            template_name='teacher_portal/login.html',
            # Após o login, para onde o usuário deve ir?
            redirect_authenticated_user=True 
        ),
        name='login'
    ),

    # --- PÁGINA DE LOGOUT ---
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    
    # Vamos adicionar o Dashboard (Pilar 3) aqui em breve
]