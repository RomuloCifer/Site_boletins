from django.urls import path
from . import views 

app_name = 'admin_panel' 

urlpatterns = [
    #URL para importar alunos via arquivo CSV.
    path(
        'importar-alunos/', 
        views.importar_alunos_view, 
        name='importar_alunos'
    ),
]