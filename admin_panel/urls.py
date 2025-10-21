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
    # Dashboard de analytics
    path(
        'analytics/',
        views.dashboard_analytics_view,
        name='analytics'
    ),
    # API endpoint para dados de gráficos
    path(
        'api/analytics-data/',
        views.dashboard_analytics_data_view,
        name='analytics_data'
    ),
    # Configuração da data limite
    path(
        'configurar-data-limite/',
        views.configurar_data_limite_view,
        name='configurar_data_limite'
    ),
]