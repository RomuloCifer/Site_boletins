from django.contrib import admin # type: ignore
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin #type: ignore
from django.contrib.auth.models import User # type: ignore

from .models import Professor, Turma, Aluno, Competencia, LancamentoDeNota, TipoTurma, ConfiguracaoSistema

class ProfessorInline(admin.StackedInline): # Inline para o modelo Professor
    model = Professor # Modelo vinculado
    can_delete = False # Não permite exclusão
    verbose_name_plural = 'Professores' # Nome plural no admin

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
    list_display = ('nome', 'descricao', 'get_total_competencias')
    search_fields = ('nome', 'descricao')
    filter_horizontal = ('competencias',)
    
    def get_total_competencias(self, obj):
        return obj.competencias.count()
    get_total_competencias.short_description = 'Total de Competências'

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_turma', 'identificador_turma', 'professor_responsavel', 'get_total_alunos') # Campos exibidos na lista
    search_fields = ('tipo_turma__nome', 'identificador_turma') # Campos pesquisáveis
    list_filter = ('tipo_turma',) # Filtro por tipo de turma
    inlines = [AlunoInline] # Adiciona o inline de Aluno

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