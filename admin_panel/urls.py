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
    # URLs para gerenciar turmas
    path(
        'turmas/nova/',
        views.nova_turma_view,
        name='nova_turma'
    ),
    path(
        'turmas/configurar/<int:turma_id>/',
        views.configurar_turma_view,
        name='configurar_turma'
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
    # URLs para geração de boletins
    path(
        'boletim/download-word/<int:aluno_id>/',
        views.visualizar_boletim_markdown,
        name='download_boletim_word'
    ),
    path(
        'boletim/aluno/<int:aluno_id>/',
        views.gerar_boletim_individual,
        name='gerar_boletim_individual'
    ),
    path(
        'boletim/turma/<int:turma_id>/',
        views.gerar_boletins_turma,
        name='gerar_boletins_turma'
    ),
    path(
        'api/verificar-notas-turma/<int:turma_id>/',
        views.verificar_notas_turma,
        name='verificar_notas_turma'
    ),
]