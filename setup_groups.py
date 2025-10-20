#!/usr/bin/env python
"""
Script para configurar grupos e permissões do sistema.
Execute: python manage.py shell < setup_groups.py
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Competencia, TipoTurma, Turma, Aluno, LancamentoDeNota

def setup_groups_and_permissions():
    """Configura grupos e permissões do sistema"""
    
    # 1. Criar grupos
    admin_group, created = Group.objects.get_or_create(name='Administradores')
    coord_group, created = Group.objects.get_or_create(name='Coordenadores')
    secretaria_group, created = Group.objects.get_or_create(name='Secretaria')
    professor_group, created = Group.objects.get_or_create(name='Professores')
    
    print("Grupos criados:")
    print(f"- Administradores: {admin_group}")
    print(f"- Coordenadores: {coord_group}")
    print(f"- Secretaria: {secretaria_group}")
    print(f"- Professores: {professor_group}")
    
    # 2. Obter ContentTypes
    competencia_ct = ContentType.objects.get_for_model(Competencia)
    tipo_turma_ct = ContentType.objects.get_for_model(TipoTurma)
    turma_ct = ContentType.objects.get_for_model(Turma)
    aluno_ct = ContentType.objects.get_for_model(Aluno)
    nota_ct = ContentType.objects.get_for_model(LancamentoDeNota)
    
    # 3. Configurar permissões para ADMINISTRADORES (TODAS)
    all_permissions = Permission.objects.filter(
        content_type__in=[competencia_ct, tipo_turma_ct, turma_ct, aluno_ct, nota_ct]
    )
    admin_group.permissions.set(all_permissions)
    
    # 4. Configurar permissões para COORDENADORES
    coord_permissions = [
        # Turmas - pode ver, adicionar e modificar (não deletar)
        'view_turma', 'add_turma', 'change_turma',
        # Alunos - pode ver, adicionar e modificar (não deletar)
        'view_aluno', 'add_aluno', 'change_aluno',
        # Competências - pode ver, adicionar e modificar (não deletar)
        'view_competencia', 'add_competencia', 'change_competencia',
        # Notas - pode ver e modificar
        'view_lancamentodenota', 'change_lancamentodenota',
        # Tipos de turma - apenas visualizar
        'view_tipoturma',
    ]
    
    coord_perms = Permission.objects.filter(
        codename__in=coord_permissions,
        content_type__in=[competencia_ct, tipo_turma_ct, turma_ct, aluno_ct, nota_ct]
    )
    coord_group.permissions.set(coord_perms)
    
    # 5. Configurar permissões para SECRETARIA
    secretaria_permissions = [
        # Alunos - pode ver, adicionar e modificar (importação)
        'view_aluno', 'add_aluno', 'change_aluno',
        # Turmas - apenas visualizar
        'view_turma',
        # Competências - apenas visualizar
        'view_competencia',
        # Tipos de turma - apenas visualizar
        'view_tipoturma',
    ]
    
    secretaria_perms = Permission.objects.filter(
        codename__in=secretaria_permissions,
        content_type__in=[competencia_ct, tipo_turma_ct, turma_ct, aluno_ct, nota_ct]
    )
    secretaria_group.permissions.set(secretaria_perms)
    
    # 6. Configurar permissões para PROFESSORES
    professor_permissions = [
        # Alunos - apenas visualizar
        'view_aluno',
        # Turmas - apenas visualizar
        'view_turma',
        # Competências - apenas visualizar
        'view_competencia',
        # Notas - pode ver, adicionar e modificar (apenas das suas turmas)
        'view_lancamentodenota', 'add_lancamentodenota', 'change_lancamentodenota',
    ]
    
    professor_perms = Permission.objects.filter(
        codename__in=professor_permissions,
        content_type__in=[competencia_ct, tipo_turma_ct, turma_ct, aluno_ct, nota_ct]
    )
    professor_group.permissions.set(professor_perms)
    
    print("\n✅ Grupos e permissões configurados com sucesso!")
    print("\nResumo das permissões:")
    print("👑 ADMINISTRADORES: Acesso total")
    print("📊 COORDENADORES: Ver/editar turmas, alunos, competências, notas")
    print("📝 SECRETARIA: Importar alunos, visualizar dados básicos")
    print("👨‍🏫 PROFESSORES: Lançar notas nas suas turmas")

if __name__ == '__main__':
    setup_groups_and_permissions()