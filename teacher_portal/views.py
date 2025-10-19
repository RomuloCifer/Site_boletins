from django.shortcuts import render, redirect
# Importa o "segurança" que exige que o usuário esteja logado
from django.contrib.auth.decorators import login_required
# Importa o modelo Turma para podermos buscar as turmas
from core.models import Turma
from django.contrib import messages

# Esta é a view do Dashboard que estava faltando
@login_required(login_url='teacher_portal:login')
def dashboard_view(request):
    """
    Página inicial do professor após o login.
    Filtra e exibe apenas as turmas associadas a ele.
    """
    try:
        # 1. Pega o perfil de professor do usuário logado
        professor = request.user.professor
        
        # 2. Filtra as turmas onde o 'professor_responsavel' é esse professor
        turmas_do_professor = Turma.objects.filter(
            professor_responsavel=professor
        ).order_by('nome')

    except AttributeError:
        # Caso de segurança: se o usuário logado não for um professor
        # (ex: o 'admin' tentou logar aqui), ele não terá o '.professor'
        turmas_do_professor = [] 

    context = {
        'turmas': turmas_do_professor,
    }
    
    # Renderiza o template do dashboard (que já criamos)
    return render(request, 'teacher_portal/dashboard.html', context)

@login_required(login_url='teacher_portal:login')
def lancamento_notas_view(request, turma_id):
    try:
        turma = Turma.objects.get(
            id=turma_id, 
            professor_responsavel=request.user.professor
        )
    except Turma.DoesNotExist:
        messages.error(request, "Turma não encontrada ou você não tem permissão para acessá-la.")
        return redirect('teacher_portal:dashboard')

    # Busca apenas os alunos
    alunos_da_turma = turma.alunos.all().order_by('nome_completo')

    context = {
        'turma': turma,
        'alunos': alunos_da_turma,
    }

    # O HTML que vamos renderizar (a "grade")
    return render(request, 'teacher_portal/lancamento_notas.html', context)