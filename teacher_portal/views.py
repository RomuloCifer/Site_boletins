from django.shortcuts import render, redirect, get_object_or_404
# Importa o "segurança" que exige que o usuário esteja logado
from django.contrib.auth.decorators import login_required
# Importa o modelo Turma para podermos buscar as turmas
from core.models import Turma, Aluno, LancamentoDeNota, ConfiguracaoSistema, ProblemaRelatado
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.conf import settings
from core.logging_utils import SimpleLogger
import urllib.parse
from datetime import datetime, date
import math


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
        ).order_by('tipo_turma__nome', 'identificador_turma')

        # 3. Calcula estatísticas de progresso para cada turma
        turmas_com_estatisticas = []
        for turma in turmas_do_professor:
            # Busca alunos e competências da turma
            alunos_da_turma = Aluno.objects.filter(turma=turma)
            competencias_da_turma = turma.competencias.all() if turma.competencias else []
            
            total_alunos = alunos_da_turma.count()
            total_competencias = len(competencias_da_turma)
            
            # Calcula estatísticas
            if total_alunos > 0 and total_competencias > 0:
                # Total de notas possíveis na turma
                total_notas_possiveis = total_alunos * total_competencias
                
                # Notas já lançadas na turma
                notas_lancadas = LancamentoDeNota.objects.filter(
                    aluno__turma=turma,
                    competencia__in=competencias_da_turma
                ).count()
                
                # Porcentagem de conclusão da turma
                progresso_turma = int((notas_lancadas / total_notas_possiveis) * 100)
                
                # Alunos com todas as notas completas
                alunos_completos = 0
                for aluno in alunos_da_turma:
                    notas_do_aluno = LancamentoDeNota.objects.filter(
                        aluno=aluno,
                        competencia__in=competencias_da_turma
                    ).count()
                    if notas_do_aluno == total_competencias:
                        alunos_completos += 1
                        
                # Porcentagem de alunos com notas completas
                alunos_completos_percent = int((alunos_completos / total_alunos) * 100) if total_alunos > 0 else 0
            else:
                progresso_turma = 0
                notas_lancadas = 0
                total_notas_possiveis = 0
                alunos_completos = 0
                alunos_completos_percent = 0
            
            turmas_com_estatisticas.append({
                'turma': turma,
                'total_alunos': total_alunos,
                'total_competencias': total_competencias,
                'notas_lancadas': notas_lancadas,
                'total_notas_possiveis': total_notas_possiveis,
                'progresso_turma': progresso_turma,
                'alunos_completos': alunos_completos,
                'alunos_completos_percent': alunos_completos_percent,
                # Status visual baseado no progresso
                'status_class': 'complete' if progresso_turma >= 90 else 'good' if progresso_turma >= 70 else 'warning' if progresso_turma >= 40 else 'critical'
            })

    except AttributeError:
        # Caso de segurança: se o usuário logado não for um professor
        # (ex: o 'admin' tentou logar aqui), ele não terá o '.professor'
        turmas_do_professor = []
        turmas_com_estatisticas = [] 

    # ===== LÓGICA DA DATA LIMITE =====
    # Data limite para conclusão das notas (configurável)
    data_limite = ConfiguracaoSistema.get_data_limite_notas()
    data_hoje = date.today()
    
    # Calcula dias restantes
    dias_restantes = (data_limite - data_hoje).days
    
    # Calcula total de ALUNOS que precisam estar 100% completos
    total_alunos_pendentes = 0
    total_alunos_completos = 0
    total_alunos_geral = 0
    
    for turma_info in turmas_com_estatisticas:
        total_alunos_geral += turma_info['total_alunos']
        total_alunos_completos += turma_info['alunos_completos']
    
    total_alunos_pendentes = total_alunos_geral - total_alunos_completos
    
    # Calcula progresso geral baseado em alunos completos
    progresso_geral = 0
    if total_alunos_geral > 0:
        progresso_geral = int((total_alunos_completos / total_alunos_geral) * 100)
    
    # Calcula alunos por dia necessários para 100%
    alunos_por_dia = 0
    if dias_restantes > 0 and total_alunos_pendentes > 0:
        alunos_por_dia = math.ceil(total_alunos_pendentes / dias_restantes)
    
    # Determina status da deadline
    deadline_status = 'deadline-good'
    if dias_restantes <= 5:
        deadline_status = 'deadline-urgent'
    elif dias_restantes <= 10:
        deadline_status = 'deadline-warning'

    context = {
        'turmas': turmas_do_professor,
        'turmas_com_estatisticas': turmas_com_estatisticas,
        # Dados da data limite (nova lógica baseada em alunos)
        'data_limite': data_limite,
        'dias_restantes': dias_restantes,
        'total_alunos_pendentes': total_alunos_pendentes,
        'alunos_por_dia': alunos_por_dia,
        'deadline_status': deadline_status,
        'progresso_geral': progresso_geral,
        'total_alunos_geral': total_alunos_geral,
        'total_alunos_completos': total_alunos_completos,
    }
    
    # Adiciona preferências do usuário se existirem
    from core.models import UserPreference
    try:
        preferences = UserPreference.objects.get(user=request.user)
        context['user_preferences'] = preferences
    except UserPreference.DoesNotExist:
        context['user_preferences'] = None
    
    # Todos podem personalizar, mas lidia tem recurso especial
    context['can_customize'] = True
    context['is_special_user'] = (request.user.username == 'lidia')
    
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
    alunos_da_turma = Aluno.objects.filter(
        turma=turma
    ).order_by('nome_completo')
    
    # Busca as competências da turma através do tipo de turma
    competencias_da_turma = turma.competencias.all() if turma.competencias else []
    total_competencias = len(competencias_da_turma)
    
    # Calcula o progresso de cada aluno
    alunos_com_progresso = []
    for aluno in alunos_da_turma:
        # Conta quantas competências o aluno já tem nota lançada
        notas_lancadas = LancamentoDeNota.objects.filter(
            aluno=aluno,
            competencia__in=competencias_da_turma
        ).count()
        
        # Calcula a porcentagem
        if total_competencias > 0:
            progresso = int((notas_lancadas / total_competencias) * 100)
        else:
            progresso = 0
            
        alunos_com_progresso.append({
            'aluno': aluno,
            'progresso': progresso
        })

    context = {
        'turma': turma,
        'alunos': alunos_da_turma,
        'alunos_com_progresso': alunos_com_progresso,
    }

    # O HTML que vamos renderizar (a "grade")
    return render(request, 'teacher_portal/lancamento_notas.html', context)

@login_required(login_url='teacher_portal:login')
def lancamento_notas_aluno_view(request, turma_id, aluno_id):
    """
    Esta view mostra o formulário de notas para UM aluno específico
    e processa o salvamento (incluindo Salvar/Próximo).
    """
    
    # --- Busca os objetos principais (precisamos deles no GET e no POST) ---
    turma = get_object_or_404(Turma, pk=turma_id, professor_responsavel__user=request.user)
    aluno = get_object_or_404(Aluno, pk=aluno_id, turma=turma)
    
    # Pega as competências que esta turma específica deve ter
    competencias_da_turma = turma.competencias.all().order_by('nome') if turma.competencias else []

    if request.method == 'POST':
        # --- LÓGICA DE SALVAR (POST) ---
        
        for comp in competencias_da_turma:
            # Pega o valor do input (ex: 'nota-12')
            nota_valor_str = request.POST.get(f'nota-{comp.id}')

            # Só salva se o professor digitou algo
            if nota_valor_str is not None and nota_valor_str.strip() != '':
                # update_or_create é perfeito aqui:
                # Tenta achar uma nota (aluno, competencia).
                # Se achar, ATUALIZA o valor.
                # Se não achar, CRIA uma nova.
                nota_obj, created = LancamentoDeNota.objects.update_or_create(
                    aluno=aluno,
                    competencia=comp,
                    defaults={'nota_valor': nota_valor_str}
                )
                
                # Log da ação
                try:
                    action = 'CREATE' if created else 'UPDATE'
                    description = f"Nota {action.lower()} para {aluno.nome_completo} em {comp.nome}: {nota_valor_str}"
                    SimpleLogger.log_action(
                        user=request.user,
                        action=action,
                        description=description,
                        severity='LOW',
                        request=request
                    )
                except Exception as e:
                    # Log de erro se falhar
                    SimpleLogger.log_error(request.user, f"Erro ao registrar log de nota: {e}", request)
                    
            # (Opcional: se o valor for vazio, você pode querer deletar a nota)
            # else:
            #    LancamentoDeNota.objects.filter(aluno=aluno, competencia=comp).delete()

        # --- LÓGICA DE REDIRECIONAMENTO (Salvar/Voltar vs Salvar/Próximo) ---
        acao = request.POST.get('acao') # Pega o 'name' do botão clicado
        
        if acao == 'salvar_voltar':
            messages.success(request, f"Notas de {aluno.nome_completo} salvas.")
            return redirect('teacher_portal:lancamento_notas', turma_id=turma.pk)
        
        elif acao == 'salvar_proximo':
            # 1. Pega todos os alunos da turma, na ordem correta
            alunos_da_turma = Aluno.objects.filter(turma=turma).order_by('nome_completo')
            
            # 2. Transforma em uma lista de IDs para achar o próximo
            lista_ids_alunos = list(alunos_da_turma.values_list('pk', flat=True))
            
            # 3. Acha o índice (posição) do aluno atual
            try:
                indice_atual = lista_ids_alunos.index(aluno.pk)
            except ValueError:
                # (Segurança) Se o aluno não estiver na lista, apenas volte
                return redirect('teacher_portal:lancamento_notas', turma_id=turma.pk)

            # 4. Verifica se há um próximo aluno
            if indice_atual + 1 < len(lista_ids_alunos):
                proximo_aluno_id = lista_ids_alunos[indice_atual + 1]
                messages.success(request, f"Notas de {aluno.nome_completo} salvas. Carregando próximo aluno...")
                return redirect('teacher_portal:lancamento_notas_aluno', turma_id=turma.pk, aluno_id=proximo_aluno_id)
            else:
                # Era o último aluno
                messages.success(request, f"Notas de {aluno.nome_completo} salvas. Você finalizou o último aluno da turma.")
                return redirect('teacher_portal:lancamento_notas', turma_id=turma.pk)
        
        # (Plano B) Se 'acao' não for nenhum dos dois, apenas volte para a lista
        return redirect('teacher_portal:lancamento_notas', turma_id=turma.pk)

    else:
        # --- LÓGICA DE EXIBIÇÃO (GET) ---
        
        # Busca as notas que JÁ EXISTEM para este aluno
        notas_existentes_qs = LancamentoDeNota.objects.filter(aluno=aluno)
        
        # Converte o queryset em um dicionário para acesso rápido
        # (Chave: comp.pk, Valor: nota_valor)
        notas_map = {nota.competencia.pk: nota.nota_valor for nota in notas_existentes_qs}

        # Prepara a lista de competências com o valor da nota (se existir)
        competencias_com_notas = []
        for comp in competencias_da_turma:
            competencias_com_notas.append({
                'competencia': comp,
                'nota_valor': notas_map.get(comp.pk, '') # Retorna '' (vazio) se a nota não foi lançada
            })

        context = {
            'turma': turma,
            'aluno': aluno,
            # Enviamos esta lista 'pré-processada' para o template
            'competencias_com_notas': competencias_com_notas,
        }
        return render(request, 'teacher_portal/lancamento_notas_aluno.html', context)


class CustomLoginView(LoginView):
    """View customizada de login com variáveis de suporte."""
    template_name = 'teacher_portal/login.html'
    redirect_authenticated_user = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar informações de suporte WhatsApp
        whatsapp_number = getattr(settings, 'WHATSAPP_SUPPORT_NUMBER', '5522999136252')
        support_message = getattr(settings, 'SUPPORT_MESSAGE', 'Olá! Estou com dificuldades para acessar o Portal do Professor. Podem me ajudar?')
        
        # Criar URL do WhatsApp
        whatsapp_url = f"https://wa.me/{whatsapp_number}?text={urllib.parse.quote(support_message)}"
        
        context.update({
            'whatsapp_support_url': whatsapp_url,
            'support_phone': whatsapp_number,
            'support_message': support_message
        })
        
        return context


@login_required(login_url='teacher_portal:login')
def detalhes_turma_view(request, turma_id):
    """
    View para exibir detalhes da turma com opção de relatar problemas
    """
    try:
        professor = request.user.professor
        turma = get_object_or_404(Turma, id=turma_id, professor_responsavel=professor)
        
        # Buscar alunos da turma
        alunos_da_turma = Aluno.objects.filter(turma=turma).order_by('nome_completo')
        
        # Estatísticas da turma
        total_alunos = alunos_da_turma.count()
        competencias_da_turma = turma.competencias.all() if turma.competencias else []
        total_competencias = len(competencias_da_turma)
        
        # Problemas relatados desta turma
        problemas_turma = ProblemaRelatado.objects.filter(
            professor=professor, 
            turma=turma
        ).order_by('-data_relato')[:5]  # Últimos 5 problemas
        
        context = {
            'turma': turma,
            'alunos_da_turma': alunos_da_turma,
            'total_alunos': total_alunos,
            'total_competencias': total_competencias,
            'competencias': competencias_da_turma,
            'problemas_recentes': problemas_turma,
        }
        
        return render(request, 'teacher_portal/detalhes_turma.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao carregar detalhes da turma: {str(e)}')
        return redirect('teacher_portal:dashboard')


@login_required(login_url='teacher_portal:login')
def relatar_problema_view(request, turma_id):
    """
    View para professores relatarem problemas sobre suas turmas
    """
    try:
        professor = request.user.professor
        turma = get_object_or_404(Turma, id=turma_id, professor_responsavel=professor)
        
        if request.method == 'POST':
            # Processar o formulário
            tipo_problema = request.POST.get('tipo_problema')
            titulo = request.POST.get('titulo')
            descricao = request.POST.get('descricao')
            aluno_id = request.POST.get('aluno_id')
            
            # Validações básicas
            if not all([tipo_problema, titulo, descricao]):
                messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                return redirect('teacher_portal:relatar_problema', turma_id=turma_id)
            
            # Criar o problema
            problema = ProblemaRelatado.objects.create(
                origem='PROFESSOR',  # Especifica que foi relatado por um professor
                professor=professor,
                turma=turma,
                aluno_id=aluno_id if aluno_id else None,
                tipo_problema=tipo_problema,
                titulo=titulo,
                descricao=descricao,
                prioridade='ALTA' if tipo_problema in ['ALUNO_DUPLICADO', 'TURMA_ERRADA'] else 'MEDIA'
            )
            
            messages.success(request, f'Problema relatado com sucesso! Número do protocolo: #{problema.id}')
            return redirect('teacher_portal:detalhes_turma', turma_id=turma_id)
        
        # GET - Exibir formulário
        alunos_da_turma = Aluno.objects.filter(turma=turma).order_by('nome_completo')
        
        context = {
            'turma': turma,
            'alunos_da_turma': alunos_da_turma,
            'tipos_problema': ProblemaRelatado.TIPO_PROBLEMA_CHOICES,
        }
        
        return render(request, 'teacher_portal/relatar_problema.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao acessar a página: {str(e)}')
        return redirect('teacher_portal:dashboard')


@login_required(login_url='teacher_portal:login')
def meus_problemas_view(request):
    """
    View para professores visualizarem seus problemas relatados
    """
    try:
        professor = request.user.professor
        
        # Filtrar problemas do professor
        problemas = ProblemaRelatado.objects.filter(
            professor=professor
        ).order_by('-data_relato')
        
        # Estatísticas
        total_problemas = problemas.count()
        problemas_pendentes = problemas.filter(status='PENDENTE').count()
        problemas_resolvidos = problemas.filter(status='RESOLVIDO').count()
        
        context = {
            'problemas': problemas,
            'total_problemas': total_problemas,
            'problemas_pendentes': problemas_pendentes,
            'problemas_resolvidos': problemas_resolvidos,
        }
        
        return render(request, 'teacher_portal/meus_problemas.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao carregar problemas: {str(e)}')
        return redirect('teacher_portal:dashboard')


@login_required(login_url='teacher_portal:login')
def personalizar_dashboard(request):
    """
    View para personalizar o dashboard (disponível para todos os usuários)
    """
    from core.models import UserPreference
    
    # Busca ou cria preferências do usuário
    preferences, created = UserPreference.objects.get_or_create(
        user=request.user,
        defaults={
            'theme_color': 'purple',
            'dashboard_emoji': '📚',
            'background_gradient_start': '#667eea',
            'background_gradient_end': '#764ba2',
            'custom_welcome_message': ''
        }
    )
    
    if request.method == 'POST':
        # Atualiza as preferências
        preferences.dashboard_emoji = request.POST.get('dashboard_emoji', '📚')
        preferences.background_gradient_start = request.POST.get('gradient_start', '#667eea')
        preferences.background_gradient_end = request.POST.get('gradient_end', '#764ba2')
        preferences.custom_welcome_message = request.POST.get('welcome_message', '')
        preferences.save()
        
        messages.success(request, '✨ Personalização salva com sucesso!')
        return redirect('teacher_portal:dashboard')
    
    context = {
        'preferences': preferences,
    }
    
    return render(request, 'teacher_portal/personalizar_dashboard.html', context)