from django.contrib import admin # type: ignore
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin #type: ignore
from django.contrib.auth.models import User # type: ignore

from .models import Professor, Turma, Aluno, Competencia, LancamentoDeNota

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

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'identificador_turma', 'professor_responsavel') # Campos exibidos na lista
    search_fields = ('nome', 'identificador_turma') # Campos pesquisáveis
    inlines = [AlunoInline] # Adiciona o inline de Aluno

    filter_horizontal = ('competencias',) # Filtro horizontal para ManyToManyField

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