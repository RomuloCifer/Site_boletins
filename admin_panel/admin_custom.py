from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.urls import path, reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from core.models import Professor, Aluno, Turma, Competencia, LancamentoDeNota, TipoTurma, ConfiguracaoSistema, ProblemaRelatado, AuditLog, SystemMetrics
from admin_panel.views import analisar_problemas_sistema

class CustomAdminSite(AdminSite):
    site_header = 'Coordenação Acadêmica'
    site_title = 'Sistema de Gestão Educacional'
    index_title = 'Dashboard Administrativo'

    def logout(self, request, extra_context=None):
        """
        Override do logout para redirecionar para a página de login do admin
        """
        if request.method == 'POST':
            logout(request)
            return HttpResponseRedirect(reverse_lazy('admin:login'))
        
        # Se for GET, mostra a página de confirmação de logout
        context = {
            'title': 'Logout',
            'site_title': self.site_title,
            'site_header': self.site_header,
            'site_url': '/',
            'has_permission': request.user.is_active and request.user.is_staff,
        }
        if extra_context:
            context.update(extra_context)
            
        return render(request, 'admin/logged_out.html', context)

    def index(self, request, extra_context=None):
        """
        Display the main admin index page with custom statistics and problem detection.
        """
        # Dados básicos
        context = {
            'total_professores': Professor.objects.count(),
            'total_alunos': Aluno.objects.count(),
            'total_turmas': Turma.objects.count(),
            'total_competencias': Competencia.objects.count(),
        }
        
        # Análise de problemas
        problemas_sistema = analisar_problemas_sistema()
        context['problemas_sistema'] = problemas_sistema
        
        # Adicionar app_list para manter as funcionalidades de administração
        app_list = self.get_app_list(request)
        context['app_list'] = app_list
        
        if extra_context:
            context.update(extra_context)
            
        return render(request, 'admin/index.html', context)

    def get_urls(self):
        """
        Add custom admin URLs for problem resolution
        """
        urls = super().get_urls()
        custom_urls = [
            path('problemas/', self.admin_view(self.problemas_view), name='admin_problemas'),
            path('problemas/duplicados/', self.admin_view(self.duplicados_view), name='admin_duplicados'),
            path('problemas/turmas-sem-professor/', self.admin_view(self.turmas_sem_professor_view), name='admin_turmas_sem_professor'),
            path('problemas/professores-sem-turma/', self.admin_view(self.professores_sem_turma_view), name='admin_professores_sem_turma'),
        ]
        return custom_urls + urls

    def problemas_view(self, request):
        """
        View para exibir todos os problemas detectados
        """
        problemas_sistema = analisar_problemas_sistema()
        
        context = {
            'title': 'Possíveis Problemas do Sistema',
            'problemas_sistema': problemas_sistema,
            'opts': {'app_label': 'admin_panel'},
        }
        
        return render(request, 'admin/problemas.html', context)
    
    def duplicados_view(self, request):
        """
        View para gerenciar alunos duplicados
        """
        problemas_sistema = analisar_problemas_sistema()
        alunos_duplicados = problemas_sistema['problemas_detalhados']['alunos_duplicados']
        
        context = {
            'title': 'Gerenciar Alunos Duplicados',
            'alunos_duplicados': alunos_duplicados,
            'opts': {'app_label': 'admin_panel'},
        }
        
        return render(request, 'admin/duplicados.html', context)
    
    def turmas_sem_professor_view(self, request):
        """
        View para gerenciar turmas sem professor
        """
        problemas_sistema = analisar_problemas_sistema()
        turmas_problema = problemas_sistema['problemas_detalhados']['turmas_sem_professor']
        
        context = {
            'title': 'Turmas sem Professor',
            'turmas_problema': turmas_problema,
            'opts': {'app_label': 'admin_panel'},
        }
        
        return render(request, 'admin/turmas_sem_professor.html', context)
    
    def professores_sem_turma_view(self, request):
        """
        View para gerenciar professores sem turma
        """
        problemas_sistema = analisar_problemas_sistema()
        professores_problema = problemas_sistema['problemas_detalhados']['professores_sem_turma']
        
        context = {
            'title': 'Professores sem Turma',
            'professores_problema': professores_problema,
            'opts': {'app_label': 'admin_panel'},
        }
        
        return render(request, 'admin/professores_sem_turma.html', context)

# Criar uma instância do admin site personalizado
admin_site = CustomAdminSite(name='custom_admin')

# Registrar todos os modelos do core.admin.py no admin customizado
from core.admin import ProfessorUserAdmin, TipoTurmaAdmin, TurmaAdmin, ProblemaRelatadoAdmin, AuditLogAdmin, SystemMetricsAdmin
from core.models import AuditLog, SystemMetrics

# Registrar User com customização
admin_site.register(User, ProfessorUserAdmin)

# Registrar outros modelos
admin_site.register(TipoTurma, TipoTurmaAdmin)
admin_site.register(Turma, TurmaAdmin)
admin_site.register(Professor)
admin_site.register(Aluno)
admin_site.register(Competencia)
admin_site.register(LancamentoDeNota)
admin_site.register(ConfiguracaoSistema)
admin_site.register(ProblemaRelatado, ProblemaRelatadoAdmin)

# Registrar modelos de auditoria
admin_site.register(AuditLog, AuditLogAdmin)
admin_site.register(SystemMetrics, SystemMetricsAdmin)