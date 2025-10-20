from django.urls import path
from . import views 

app_name = 'admin_panel' 

urlpatterns = [
    # Dashboard administrativo
    path(
        '', 
        views.dashboard_admin_view, 
        name='dashboard'
    ),
    # Detalhes de uma turma específica
    path(
        'turma/<int:turma_id>/', 
        views.detalhes_turma_view, 
        name='detalhes_turma'
    ),
    #URL para importar alunos via arquivo CSV.
    path(
        'importar-alunos/', 
        views.importar_alunos_view, 
        name='importar_alunos'
    ),
    # URLs para gerenciar competências
    path(
        'competencias/',
        views.gerenciar_competencias_view,
        name='gerenciar_competencias'
    ),
    path(
        'competencias/deletar/<int:competencia_id>/',
        views.deletar_competencia_view,
        name='deletar_competencia'
    ),
    # URLs para gerenciar tipos de turma
    path(
        'tipos-turma/',
        views.gerenciar_tipos_turma_view,
        name='gerenciar_tipos_turma'
    ),
]