from django.contrib import admin # type: ignore
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin #type: ignore
from django.contrib.auth.models import User # type: ignore

from .models import Professor, Turma, Aluno, Competencia, LancamentoDeNota, TipoTurma, ConfiguracaoSistema, ProblemaRelatado, AuditLog, SystemMetrics, UserPreference

class ProfessorInline(admin.StackedInline): # Inline para o modelo Professor
    model = Professor # Modelo vinculado
    can_delete = False # Não permite exclusão
    verbose_name_plural = 'Professores' # Nome plural no admin
    fields = ('nome_completo', 'data_contratacao')  # Adiciona nome_completo

class ProfessorUserAdmin(BaseUserAdmin): # Extende o UserAdmin padrão
    inlines = (ProfessorInline,) # Adiciona o inline de Professor

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('is_staff',)}), 
    )
admin.site.unregister(User) # Desregistra o modelo User padrão
admin.site.register(User, ProfessorUserAdmin) # Registra o User com o novo admin

# -----------------------------------------------------------
# 2. Registros (Turma, Competencia, Notas)
# -----------------------------------------------------------

class AlunoInline(admin.TabularInline): # Inline para o modelo Aluno
    model = Aluno # Modelo vinculado
    extra = 0 # Número extra de formulários vazios

@admin.register(TipoTurma)
class TipoTurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome', 'descricao')
    fields = ('nome', 'descricao')  # Remove o campo de competências do formulário
    
    class Meta:
        verbose_name = 'Tipo de Turma'
        verbose_name_plural = 'Tipos de Turma'

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_turma', 'identificador_turma', 'boletim_tipo', 'professor_responsavel', 'get_total_alunos') # Campos exibidos na lista
    search_fields = ('tipo_turma__nome', 'identificador_turma') # Campos pesquisáveis
    list_filter = ('tipo_turma', 'boletim_tipo') # Filtro por tipo de turma e tipo de boletim
    inlines = [AlunoInline] # Adiciona o inline de Aluno
    fields = ('tipo_turma', 'identificador_turma', 'boletim_tipo', 'professor_responsavel') # Ordem dos campos no formulário

    def get_total_alunos(self, obj):
        return obj.alunos.count()
    get_total_alunos.short_description = 'Total de Alunos'

@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_nota') # Campos exibidos na lista
    list_filter = ('tipo_nota',) # Filtros laterais

@admin.register(LancamentoDeNota)
class LancamentoDeNotaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'competencia', 'nota_valor') # Campos exibidos na lista
    list_filter = ('competencia',) # Filtros laterais
    search_fields = ('aluno__nome_completo', 'competencia__nome') # Campos pesquisáveis

@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor', 'descricao', 'data_atualizacao')
    search_fields = ('nome', 'descricao')
    readonly_fields = ('data_atualizacao',)
    
    fieldsets = (
        (None, {
            'fields': ('nome', 'valor', 'descricao')
        }),
        ('Informações', {
            'fields': ('data_atualizacao',)
        }),
    )

@admin.register(ProblemaRelatado)
class ProblemaRelatadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'origem', 'professor_display', 'turma', 'tipo_problema', 'status', 'prioridade', 'data_relato')
    list_filter = ('origem', 'status', 'prioridade', 'tipo_problema', 'data_relato')
    search_fields = ('titulo', 'descricao', 'professor__user__first_name', 'professor__user__last_name', 'turma__nome')
    readonly_fields = ('data_relato', 'data_atualizacao')
    
    fieldsets = (
        ('Informações do Problema', {
            'fields': ('origem', 'professor', 'turma', 'aluno', 'tipo_problema', 'titulo', 'descricao')
        }),
        ('Status e Prioridade', {
            'fields': ('status', 'prioridade')
        }),
        ('Resolução', {
            'fields': ('resposta_admin', 'resolvido_por', 'data_resolucao')
        }),
        ('Timestamps', {
            'fields': ('data_relato', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def professor_display(self, obj):
        if obj.professor:
            return obj.professor.user.get_full_name() or obj.professor.user.username
        return "Sistema"
    professor_display.short_description = "Professor/Sistema"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('professor__user', 'turma', 'aluno')
    
    def save_model(self, request, obj, form, change):
        # Se estiver marcando como resolvido e não tem data de resolução
        if obj.status == 'RESOLVIDO' and not obj.data_resolucao:
            from django.utils import timezone
            obj.data_resolucao = timezone.now()
            obj.resolvido_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin para logs de auditoria"""
    list_display = ('timestamp', 'usuario', 'acao', 'severidade', 'descricao_resumida', 'ip_address')
    list_filter = ('acao', 'severidade', 'timestamp', 'modelo_afetado')
    search_fields = ('descricao', 'usuario__username', 'ip_address')
    readonly_fields = ('timestamp', 'usuario', 'acao', 'severidade', 'modelo_afetado', 
                      'objeto_id', 'descricao', 'detalhes_json', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)
    
    def descricao_resumida(self, obj):
        return obj.descricao[:50] + "..." if len(obj.descricao) > 50 else obj.descricao
    descricao_resumida.short_description = "Descrição"
    
    def has_add_permission(self, request):
        return False  # Não permite criação manual
    
    def has_change_permission(self, request, obj=None):
        return False  # Não permite edição
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Apenas superuser pode deletar


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    """Admin para métricas do sistema"""
    list_display = ('timestamp', 'metric_name', 'metric_value', 'resumo_dados')
    list_filter = ('metric_name', 'timestamp')
    readonly_fields = ('timestamp', 'metric_name', 'metric_value', 'additional_data')
    ordering = ('-timestamp',)
    
    def resumo_dados(self, obj):
        if obj.additional_data:
            return str(obj.additional_data)[:30] + "..."
        return "-"
    resumo_dados.short_description = "Dados Adicionais"
    
    def has_add_permission(self, request):
        return False  # Não permite criação manual
    
    def has_change_permission(self, request, obj=None):
        return False  # Não permite edição


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme_color', 'dashboard_emoji', 'background_gradient_start', 'background_gradient_end')
    search_fields = ('user__username',)
    list_filter = ('theme_color',)
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Personalização Visual', {
            'fields': ('dashboard_emoji', 'background_gradient_start', 'background_gradient_end', 'theme_color')
        }),
        ('Mensagens', {
            'fields': ('custom_welcome_message',)
        }),
    )