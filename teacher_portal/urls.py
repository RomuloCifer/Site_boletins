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
        views.CustomLoginView.as_view(),
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
    path(
        'turma/<int:turma_id>/',  # 
        views.lancamento_notas_view, # 
        name='lancamento_notas'
    ),
    path(
        'turma/<int:turma_id>/aluno/<int:aluno_id>/',
        views.lancamento_notas_aluno_view, #
        name='lancamento_notas_aluno'
    ),
]