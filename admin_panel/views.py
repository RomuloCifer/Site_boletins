import pandas as pd # Para processar arquivos CSV/Excel
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required # Garante que apenas administradores acessem
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from core.models import Turma, Aluno, Professor, Competencia, LancamentoDeNota, TipoTurma, ConfiguracaoSistema
from core.utils import BoletimGenerator
from .decorators import group_required, admin_only, coordinador_or_admin, secretaria_or_above
import io
import re
import unicodedata
from datetime import date, datetime
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
import tempfile
import os
# Create your views here.

def normalizar_nome(nome):
    """Normaliza um nome para detectar duplicatas"""
    if not nome:
        return ""
    
    # Remove acentos
    nome_sem_acento = unicodedata.normalize('NFD', nome)
    nome_sem_acento = ''.join(char for char in nome_sem_acento if unicodedata.category(char) != 'Mn')
    
    # Remove espaços extras, converte para minúsculo
    nome_limpo = re.sub(r'\s+', ' ', nome_sem_acento.lower().strip())
    
    return nome_limpo

def detectar_alunos_duplicados():
    """Detecta possíveis alunos duplicados baseado em nomes completos normalizados"""
    alunos_por_nome = {}
    problemas = []
    
    # Agrupa alunos por nome normalizado
    for aluno in Aluno.objects.all():
        nome_normalizado = normalizar_nome(aluno.nome_completo)
        
        # Só considera duplicata se o nome completo normalizado for idêntico
        # E tiver pelo menos 3 palavras (para evitar nomes muito simples)
        palavras_nome = nome_normalizado.split()
        if len(palavras_nome) >= 3:  # Ex: "ana beatriz santos" (3+ palavras)
            if nome_normalizado not in alunos_por_nome:
                alunos_por_nome[nome_normalizado] = []
            alunos_por_nome[nome_normalizado].append(aluno)
    
    # Encontra grupos com mais de um aluno
    for nome_normalizado, alunos in alunos_por_nome.items():
        if len(alunos) > 1:
            # Verifica se estão na mesma turma (mais crítico)
            turmas_afetadas = set(aluno.turma.nome for aluno in alunos if aluno.turma)
            mesma_turma = len(turmas_afetadas) == 1 and len(alunos) > 1
            
            problemas.append({
                'tipo': 'aluno_duplicado',
                'severidade': 'alta' if mesma_turma else 'media',
                'descricao': f'{len(alunos)} aluno(s) com nome idêntico: {alunos[0].nome_completo}',
                'detalhes': {
                    'alunos': alunos,
                    'mesma_turma': mesma_turma,
                    'turmas': list(turmas_afetadas),
                    'nome_normalizado': nome_normalizado
                }
            })
    
    return problemas

def detectar_turmas_sem_professor():
    """Detecta turmas sem professor responsável"""
    turmas_problema = Turma.objects.filter(professor_responsavel__isnull=True)
    problemas = []
    
    for turma in turmas_problema:
        problemas.append({
            'tipo': 'turma_sem_professor',
            'severidade': 'alta',
            'descricao': f'Turma {turma.nome} sem professor responsável',
            'detalhes': {
                'turma': turma,
                'total_alunos': Aluno.objects.filter(turma=turma).count()
            }
        })
    
    return problemas

def detectar_professores_sem_turma():
    """Detecta professores sem turma atribuída"""
    professores_problema = Professor.objects.filter(turmas__isnull=True)
    problemas = []
    
    for professor in professores_problema:
        nome = professor.user.get_full_name() or professor.user.username
        problemas.append({
            'tipo': 'professor_sem_turma',
            'severidade': 'baixa',  # Sempre baixa prioridade
            'descricao': f'Professor {nome} disponível para atribuição',
            'detalhes': {
                'professor': professor,
                'usuario_ativo': professor.user.is_active,
                'nome_completo': nome
            }
        })
    
    return problemas

def analisar_problemas_sistema():
    """Analisa todos os problemas do sistema e retorna estatísticas organizadas por prioridade"""
    # Importa problemas relatados e detectados automaticamente
    from core.models import ProblemaRelatado
    from core.utils import ProblemaSystemaManager
    
    # Detecta e cria problemas automáticos
    ProblemaSystemaManager.detectar_e_criar_problemas_automaticos()
    
    # Busca todos os problemas por origem
    problemas_professores = ProblemaRelatado.objects.filter(
        origem='PROFESSOR',
        status__in=['PENDENTE', 'EM_ANALISE']
    ).select_related('professor__user', 'turma', 'aluno')
    
    problemas_sistema = ProblemaRelatado.objects.filter(
        origem='SISTEMA',
        status__in=['PENDENTE', 'EM_ANALISE']
    ).select_related('professor__user', 'turma', 'aluno')
    
    # Organiza problemas por prioridade e origem
    problemas_por_prioridade = {
        'alta': {'professores': [], 'sistema': []},
        'media': {'professores': [], 'sistema': []},
        'baixa': {'professores': [], 'sistema': []}
    }
    
    # Mapear prioridades para categorias
    def mapear_prioridade(prioridade):
        if prioridade in ['CRITICA', 'ALTA']:
            return 'alta'
        elif prioridade == 'MEDIA':
            return 'media'
        else:
            return 'baixa'
    
    # Organizar problemas de professores
    for problema in problemas_professores:
        categoria = mapear_prioridade(problema.prioridade)
        problemas_por_prioridade[categoria]['professores'].append({
            'tipo': 'problema_relatado',
            'id': problema.id,
            'titulo': problema.titulo,
            'descricao': problema.descricao,
            'professor': problema.professor,
            'turma': problema.turma,
            'data_relato': problema.data_relato,
            'tipo_problema': problema.get_tipo_problema_display(),
            'prioridade': problema.prioridade,
            'objeto': problema
        })
    
    # Organizar problemas do sistema
    for problema in problemas_sistema:
        categoria = mapear_prioridade(problema.prioridade)
        problemas_por_prioridade[categoria]['sistema'].append({
            'tipo': 'problema_sistema',
            'id': problema.id,
            'titulo': problema.titulo,
            'descricao': problema.descricao,
            'turma': problema.turma,
            'aluno': problema.aluno,
            'data_relato': problema.data_relato,
            'tipo_problema': problema.get_tipo_problema_display(),
            'prioridade': problema.prioridade,
            'objeto': problema
        })
    
    # Contar totais
    total_professores = problemas_professores.count()
    total_sistema = problemas_sistema.count()
    total_geral = total_professores + total_sistema
    
    # Contar por prioridade
    def contar_por_prioridade(queryset, prioridades):
        return queryset.filter(prioridade__in=prioridades).count()
    
    estatisticas = {
        'total_problemas': total_geral,
        'total_por_origem': {
            'professores': total_professores,
            'sistema': total_sistema
        },
        'professores': {
            'alta': contar_por_prioridade(problemas_professores, ['CRITICA', 'ALTA']),
            'media': contar_por_prioridade(problemas_professores, ['MEDIA']),
            'baixa': contar_por_prioridade(problemas_professores, ['BAIXA']),
            'total': total_professores
        },
        'sistema': {
            'alta': contar_por_prioridade(problemas_sistema, ['CRITICA', 'ALTA']),
            'media': contar_por_prioridade(problemas_sistema, ['MEDIA']),
            'baixa': contar_por_prioridade(problemas_sistema, ['BAIXA']),
            'total': total_sistema
        },
        'total_por_prioridade': {
            'alta': contar_por_prioridade(problemas_professores, ['CRITICA', 'ALTA']) + 
                   contar_por_prioridade(problemas_sistema, ['CRITICA', 'ALTA']),
            'media': contar_por_prioridade(problemas_professores, ['MEDIA']) + 
                    contar_por_prioridade(problemas_sistema, ['MEDIA']),
            'baixa': contar_por_prioridade(problemas_professores, ['BAIXA']) + 
                    contar_por_prioridade(problemas_sistema, ['BAIXA'])
        },
        'problemas_detalhados': {
            'por_prioridade': problemas_por_prioridade,
            'todos_professores': list(problemas_professores),
            'todos_sistema': list(problemas_sistema)
        },
        # Backward compatibility para templates existentes
        'alunos_duplicados': {
            'alta': problemas_sistema.filter(tipo_problema='ALUNO_DUPLICADO', prioridade__in=['CRITICA', 'ALTA']).count(),
            'media': problemas_sistema.filter(tipo_problema='ALUNO_DUPLICADO', prioridade='MEDIA').count(),
            'total': problemas_sistema.filter(tipo_problema='ALUNO_DUPLICADO').count()
        },
        'turmas_sem_professor': problemas_sistema.filter(tipo_problema='TURMA_SEM_PROFESSOR').count(),
        'professores_sem_turma': problemas_sistema.filter(tipo_problema='PROFESSOR_SEM_TURMA').count(),
        'problemas_relatados': {
            'alta': problemas_professores.filter(prioridade__in=['CRITICA', 'ALTA']).count(),
            'media': problemas_professores.filter(prioridade='MEDIA').count(),
            'baixa': problemas_professores.filter(prioridade='BAIXA').count(),
            'total': total_professores
        },
        # Dados para análise e relatórios
        'resumo_qualitativo': {
            'nivel_criticidade': 'alta' if (contar_por_prioridade(problemas_professores, ['CRITICA', 'ALTA']) + 
                                           contar_por_prioridade(problemas_sistema, ['CRITICA', 'ALTA'])) > 0 else 
                               'media' if (contar_por_prioridade(problemas_professores, ['MEDIA']) + 
                                         contar_por_prioridade(problemas_sistema, ['MEDIA'])) > 0 else 
                               'baixa' if (contar_por_prioridade(problemas_professores, ['BAIXA']) + 
                                         contar_por_prioridade(problemas_sistema, ['BAIXA'])) > 0 else 'ok',
            'requer_acao_imediata': (contar_por_prioridade(problemas_professores, ['CRITICA', 'ALTA']) + 
                                   contar_por_prioridade(problemas_sistema, ['CRITICA', 'ALTA'])) > 0,
            'situacao_geral': 'crítica' if (contar_por_prioridade(problemas_professores, ['CRITICA', 'ALTA']) + 
                                          contar_por_prioridade(problemas_sistema, ['CRITICA', 'ALTA'])) >= 5 else 
                            'atenção' if (contar_por_prioridade(problemas_professores, ['CRITICA', 'ALTA']) + 
                                        contar_por_prioridade(problemas_sistema, ['CRITICA', 'ALTA'])) > 0 or 
                                       (contar_por_prioridade(problemas_professores, ['MEDIA']) + 
                                        contar_por_prioridade(problemas_sistema, ['MEDIA'])) >= 3 else 'estável',
            'tem_problemas_professores': total_professores > 0,
            'tem_problemas_sistema': total_sistema > 0
        }
    }
    
    return estatisticas

@coordinador_or_admin
def dashboard_admin_view(request):
    """Dashboard administrativo com visão geral de todas as turmas e progresso."""
    
    # Busca todas as turmas ordenadas por tipo e identificador
    turmas = Turma.objects.all().order_by('tipo_turma__nome', 'identificador_turma')
    
    turmas_com_progresso = []
    for turma in turmas:
        # Busca alunos da turma
        alunos_da_turma = Aluno.objects.filter(turma=turma)
        total_alunos = alunos_da_turma.count()
        
        # Busca competências da turma através do tipo de turma
        competencias_da_turma = turma.competencias.all() if turma.competencias else []
        total_competencias = len(competencias_da_turma)
        
        # Calcula o total de notas possíveis (alunos × competências)
        total_notas_possiveis = total_alunos * total_competencias
        
        # Conta quantas notas já foram lançadas
        notas_lancadas = LancamentoDeNota.objects.filter(
            aluno__turma=turma,
            competencia__in=competencias_da_turma
        ).count()
        
        # Calcula a porcentagem geral da turma
        if total_notas_possiveis > 0:
            progresso_turma = int((notas_lancadas / total_notas_possiveis) * 100)
        else:
            progresso_turma = 0
        
        # Informações do professor responsável
        if turma.professor_responsavel:
            nome_completo = turma.professor_responsavel.user.get_full_name()
            professor_nome = nome_completo if nome_completo.strip() else turma.professor_responsavel.user.username
        else:
            professor_nome = "Não atribuído"
        
        turmas_com_progresso.append({
            'turma': turma,
            'total_alunos': total_alunos,
            'total_competencias': total_competencias,
            'notas_lancadas': notas_lancadas,
            'total_notas_possiveis': total_notas_possiveis,
            'progresso_turma': progresso_turma,
            'professor_nome': professor_nome,
        })
    
    # Analisar problemas do sistema
    problemas_sistema = analisar_problemas_sistema()
    
    # Buscar professores agrupados por unidade
    professores_nf = []
    professores_rb = []
    
    for professor in Professor.objects.all().select_related('user'):
        username = professor.user.username
        nome_completo = professor.user.get_full_name()
        nome_display = nome_completo if nome_completo.strip() else username
        
        # Identificar unidade
        if username == 'lidia' or username.endswith('nf'):
            professores_nf.append({
                'id': professor.id,
                'username': username,
                'nome': nome_display
            })
        elif username.endswith('rb'):
            professores_rb.append({
                'id': professor.id,
                'username': username,
                'nome': nome_display
            })
    
    # Ordenar por nome
    professores_nf.sort(key=lambda x: x['nome'])
    professores_rb.sort(key=lambda x: x['nome'])
    
    context = {
        'turmas_com_progresso': turmas_com_progresso,
        'total_turmas': turmas.count(),
        'total_alunos_geral': sum(t['total_alunos'] for t in turmas_com_progresso),
        'total_notas_lancadas_geral': sum(t['notas_lancadas'] for t in turmas_com_progresso),
        'total_notas_possiveis_geral': sum(t['total_notas_possiveis'] for t in turmas_com_progresso),
        'problemas_sistema': problemas_sistema,
        'professores_nf': professores_nf,
        'professores_rb': professores_rb,
    }
    
    return render(request, 'admin_panel/dashboard_admin.html', context)

@coordinador_or_admin
def detalhes_turma_view(request, turma_id):
    """Exibe detalhes específicos de uma turma para coordenação."""
    try:
        turma = Turma.objects.get(pk=turma_id)
    except Turma.DoesNotExist:
        messages.error(request, "Turma não encontrada.")
        return redirect('admin_panel:dashboard')
    
    # Busca alunos da turma
    alunos_da_turma = Aluno.objects.filter(turma=turma).order_by('nome_completo')
    
    # Busca competências da turma através do tipo de turma
    competencias_da_turma = turma.competencias.all() if turma.competencias else []
    total_competencias_turma = len(competencias_da_turma)
    
    # Calcula progresso detalhado de cada aluno
    alunos_com_progresso_detalhado = []
    for aluno in alunos_da_turma:
        if competencias_da_turma:
            notas_aluno = LancamentoDeNota.objects.filter(
                aluno=aluno,
                competencia__in=competencias_da_turma
            )
        else:
            notas_aluno = LancamentoDeNota.objects.none()
            
        # Cria lista de notas na ordem das competências
        notas_ordenadas = []
        for competencia in competencias_da_turma:
            nota = notas_aluno.filter(competencia=competencia).first()
            notas_ordenadas.append({
                'competencia': competencia,
                'nota_valor': nota.nota_valor if nota else None,
                'tem_nota': nota is not None
            })
        
        # Calcula progresso individual
        notas_lancadas = notas_aluno.count()
        progresso_individual = int((notas_lancadas / total_competencias_turma) * 100) if total_competencias_turma > 0 else 0
        
        alunos_com_progresso_detalhado.append({
            'aluno': aluno,
            'notas_ordenadas': notas_ordenadas,
            'progresso_individual': progresso_individual,
            'notas_lancadas': notas_lancadas,
            'total_competencias': total_competencias_turma,
        })
    
    context = {
        'turma': turma,
        'competencias_da_turma': competencias_da_turma,
        'alunos_com_progresso_detalhado': alunos_com_progresso_detalhado,
        'total_alunos': alunos_da_turma.count(),
        'total_competencias': total_competencias_turma,
    }
    
    return render(request, 'admin_panel/detalhes_turma.html', context)


def handle_uploaded_file(uploaded_file):
    """ Processa o arquivo CSV/Excel e retorna uma lista de dicionários com os dados dos alunos."""
    
    if uploaded_file.name.endswith('.csv'):
        # Garantir que estamos no início do arquivo para uma nova leitura
        uploaded_file.seek(0)
        
        try:
            # --- TENTATIVA 1 (Padrão Universal com BOM) ---
            # Vamos tentar esta primeiro, pois seu erro mostra um BOM ('ï»¿')
            text_file = io.TextIOWrapper(uploaded_file, encoding='utf-8-sig')
            df = pd.read_csv(text_file, sep=None, engine='python')
            
        except UnicodeDecodeError:
            # --- TENTATIVA 2 (Plano B: Comum no Brasil/Windows) ---
            # Se falhar (ex: o arquivo não é UTF-8), tente latin-1
            uploaded_file.seek(0) # Volta ao início de novo
            text_file = io.TextIOWrapper(uploaded_file, encoding='latin-1')
            df = pd.read_csv(text_file, sep=None, engine='python')
        
        except Exception as e:
            # Se ambas falharem, mostre o erro.
            raise ValueError(f"Não foi possível processar o CSV. Erro: {e}")

    elif uploaded_file.name.endswith(('.xls', '.xlsx')):
        # Arquivos Excel são lidos de forma diferente e não precisam disso
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Formato de arquivo não suportado. Use CSV ou Excel.")
    
    # Normaliza os nomes das colunas (ex: "Nome Completo" -> "nome_completo")
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_') 
    return df

# Importação de alunos via CSV/Excel
@secretaria_or_above
def importar_alunos_view(request):
    turmas = Turma.objects.all() # Carrega todas as turmas para o dropdown
    if request.method == 'POST': # Verifica se o método é POST
        turma_id = request.POST.get('turma_id') # Obtém a turma selecionada
        uploaded_file = request.FILES.get('arquivo_alunos')  # Obtém o arquivo enviado

        if not turma_id:
            messages.error(request, "Por favor, selecione um modo de importação (Lote ou Turma Específica).")
            return redirect('admin_panel:importar_alunos') # Redireciona de volta à página de importação
        if not uploaded_file:
            messages.error(request, "Nenhum arquivo foi enviado.")
            return redirect('admin_panel:importar_alunos')
        try:

            df = handle_uploaded_file(uploaded_file) # Processa o arquivo
            # Verifica se a coluna 'nome_completo' existe
            if 'nome_completo' not in df.columns:
                colunas_encontradas = list(df.columns)
                messages.error(request, f"O arquivo deve conter uma coluna 'nome_completo'. {colunas_encontradas} foram encontradas.")
                return redirect('admin_panel:importar_alunos')
            # Processamento de dados.
            if turma_id == 'lote':
                if 'identificador_turma' not in df.columns:
                    colunas = list(df.columns)
                    messages.error(request, f"Para importação em lote, o arquivo deve conter a coluna 'identificador_turma'. {colunas} foram encontradas.")
                    return redirect('admin_panel:importar_alunos')
                # Importação em lote para múltiplas turmas
                turmas_map = {t.identificador_turma: t for t in Turma.objects.all()} # Mapeia identificadores para objetos Turma
                alunos_criados = 0 # Contador de alunos criados
                alunos_atualizados = 0 # Contador de alunos atualizados
                erros_turma_nao_encontrada = set() # Armazena identificadores de turmas não encontradas

                for index, row in df.iterrows():
                    id_turma_csv = str(row['identificador_turma'])
                    turma = turmas_map.get(id_turma_csv)

                    if turma:
                        aluno, criado = Aluno.objects.update_or_create(
                            nome_completo=row['nome_completo'],
                            turma=turma,
                            defaults={'matricula': row.get('matricula')}
                            )
                        if criado:
                            alunos_criados += 1
                        else:
                            alunos_atualizados += 1
                    else:
                        erros_turma_nao_encontrada.add(id_turma_csv)
                
                # Mensagens após processamento completo
                messages.success(request, 
                    f"Importação EM LOTE concluída! "
                    f"✅ Criados: {alunos_criados} | 🔄 Atualizados: {alunos_atualizados} | "
                    f"📊 Total processado: {alunos_criados + alunos_atualizados}"
                )
                
                if erros_turma_nao_encontrada:
                    mensagens_erro = ", ".join(erros_turma_nao_encontrada)
                    messages.warning(request, f"⚠️ Turmas não encontradas: {mensagens_erro}. Estes alunos não foram importados.")
            else:
                # O 'try/except' externo vai pegar Turma.DoesNotExist se o ID for inválido
                turma = Turma.objects.get(id=turma_id)
                alunos_criados = 0
                alunos_atualizados = 0

                for index, row in df.iterrows():
                    aluno, criado = Aluno.objects.update_or_create(
                        nome_completo=row['nome_completo'],
                        turma=turma,
                        defaults={'matricula': row.get('matricula')}
                    )
                    if criado:
                        alunos_criados += 1
                    else:
                        alunos_atualizados += 1
                
                messages.success(request, 
                    f"✅ Importação concluída para '{turma.nome}'! "
                    f"📥 Criados: {alunos_criados} | 🔄 Atualizados: {alunos_atualizados} | "
                    f"📊 Total: {alunos_criados + alunos_atualizados} alunos"
                )
        except Turma.DoesNotExist: 
            messages.error(request, "Turma selecionada não existe.")
        except ValueError as ve:
            messages.error(request, "O ID da turma selecionado é inválido.")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro durante a importação: {str(e)}")
        return redirect('admin_panel:importar_alunos') # Redireciona de volta à página de importação
    
 # Se o método não for POST, renderiza o formulário de upload
    context = { # Contexto para o template
        'turmas': turmas,
        'title': 'Importar Alunos via CSV/Excel'
    }
    return render(request, 'admin_panel/importar_alunos.html', context) # Renderiza o template


@coordinador_or_admin
def gerenciar_competencias_view(request):
    """View para gerenciar competências - listar, criar, editar e deletar"""
    competencias = Competencia.objects.all().order_by('nome')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            nome = request.POST.get('nome', '').strip()
            tipo_nota = request.POST.get('tipo_nota')
            
            if not nome:
                messages.error(request, 'O nome da competência é obrigatório.')
            elif len(nome) < 3:
                messages.error(request, 'O nome da competência deve ter pelo menos 3 caracteres.')
            elif not tipo_nota:
                messages.error(request, 'O tipo de nota é obrigatório.')
            elif Competencia.objects.filter(nome__iexact=nome).exists():
                messages.error(request, f'Já existe uma competência com o nome "{nome}".')
            else:
                try:
                    competencia = Competencia.objects.create(
                        nome=nome,
                        tipo_nota=tipo_nota
                    )
                    messages.success(request, f'Competência "{competencia.nome}" criada com sucesso!')
                except Exception as e:
                    messages.error(request, f'Erro ao criar competência: {str(e)}')
        
        elif action == 'edit':
            competencia_id = request.POST.get('competencia_id')
            nome = request.POST.get('nome', '').strip()
            tipo_nota = request.POST.get('tipo_nota')
            
            try:
                competencia = get_object_or_404(Competencia, id=competencia_id)
                
                if not nome:
                    messages.error(request, 'O nome da competência é obrigatório.')
                elif len(nome) < 3:
                    messages.error(request, 'O nome da competência deve ter pelo menos 3 caracteres.')
                elif not tipo_nota:
                    messages.error(request, 'O tipo de nota é obrigatório.')
                elif Competencia.objects.filter(nome__iexact=nome).exclude(id=competencia_id).exists():
                    messages.error(request, f'Já existe uma competência com o nome "{nome}".')
                else:
                    # Verificar se tem notas lançadas antes de alterar tipo
                    notas_existentes = LancamentoDeNota.objects.filter(competencia=competencia).count()
                    if notas_existentes > 0 and competencia.tipo_nota != tipo_nota:
                        messages.warning(
                            request,
                            f'Atenção: A competência "{competencia.nome}" possui {notas_existentes} nota(s) lançada(s). '
                            f'Alterar o tipo de nota pode afetar a exibição das notas existentes.'
                        )
                    
                    nome_anterior = competencia.nome
                    competencia.nome = nome
                    competencia.tipo_nota = tipo_nota
                    competencia.save()
                    
                    if nome_anterior != nome:
                        messages.success(request, f'Competência "{nome_anterior}" foi renomeada para "{nome}" e atualizada com sucesso!')
                    else:
                        messages.success(request, f'Competência "{nome}" atualizada com sucesso!')
                        
            except Exception as e:
                messages.error(request, f'Erro ao editar competência: {str(e)}')
        
        elif action == 'delete':
            competencia_id = request.POST.get('competencia_id')
            force_delete = request.POST.get('force_delete') == 'true'
            
            try:
                competencia = get_object_or_404(Competencia, id=competencia_id)
                
                # Verificar se a competência está sendo usada
                tipos_turma_usando = TipoTurma.objects.filter(competencias=competencia)
                notas_existentes = LancamentoDeNota.objects.filter(competencia=competencia).count()
                
                if (tipos_turma_usando.count() > 0 or notas_existentes > 0) and not force_delete:
                    # Preparar informações detalhadas para o modal de confirmação
                    tipos_info = list(tipos_turma_usando.values_list('nome', flat=True))
                    context_info = {
                        'tipos_turma': tipos_info,
                        'quantidade_tipos': tipos_turma_usando.count(),
                        'notas_existentes': notas_existentes
                    }
                    
                    messages.warning(
                        request, 
                        f'A competência "{competencia.nome}" está sendo usada em {tipos_turma_usando.count()} tipo(s) de turma '
                        f'e possui {notas_existentes} nota(s) lançada(s). Esta ação não pode ser desfeita!'
                    )
                else:
                    nome_competencia = competencia.nome
                    competencia.delete()
                    messages.success(request, f'Competência "{nome_competencia}" deletada com sucesso!')
                    
            except Exception as e:
                messages.error(request, f'Erro ao deletar competência: {str(e)}')
        
        return redirect('admin_panel:gerenciar_competencias')
    
    # Preparar informações adicionais sobre cada competência
    competencias_info = []
    for competencia in competencias:
        tipos_turma = TipoTurma.objects.filter(competencias=competencia)
        notas_count = LancamentoDeNota.objects.filter(competencia=competencia).count()
        
        competencias_info.append({
            'competencia': competencia,
            'tipos_turma': tipos_turma,
            'tipos_turma_count': tipos_turma.count(),
            'notas_count': notas_count,
            'pode_deletar': tipos_turma.count() == 0 and notas_count == 0,
            'tipos_turma_nomes': [tipo.nome for tipo in tipos_turma[:3]]  # Primeiros 3 para exibição
        })
    
    context = {
        'competencias_info': competencias_info,
        'competencias': competencias,  # Mantido para compatibilidade
        'tipo_nota_choices': Competencia.TIPO_NOTA_CHOICES,
        'total_competencias': competencias.count(),
        'title': 'Gerenciar Competências'
    }
    return render(request, 'admin_panel/gerenciar_competencias.html', context)


@admin_only
def deletar_competencia_view(request, competencia_id):
    """View para confirmar e deletar uma competência"""
    if request.method == 'POST':
        try:
            competencia = get_object_or_404(Competencia, id=competencia_id)
            nome_competencia = competencia.nome
            competencia.delete()
            messages.success(request, f'Competência "{nome_competencia}" deletada com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao deletar competência: {str(e)}')
    
    return redirect('admin_panel:gerenciar_competencias')


@admin_only
def gerenciar_tipos_turma_view(request):
    """View para gerenciar tipos de turma"""
    tipos_turma = TipoTurma.objects.all().order_by('nome')
    competencias_disponiveis = Competencia.objects.all().order_by('nome')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao', '')
            competencias_ids = request.POST.getlist('competencias')
            
            if nome:
                try:
                    tipo_turma = TipoTurma.objects.create(
                        nome=nome,
                        descricao=descricao
                    )
                    
                    if competencias_ids:
                        tipo_turma.competencias.set(competencias_ids)
                    
                    messages.success(request, f'Tipo de turma "{tipo_turma.nome}" criado com sucesso!')
                except Exception as e:
                    messages.error(request, f'Erro ao criar tipo de turma: {str(e)}')
            else:
                messages.error(request, 'Nome é obrigatório.')
        
        return redirect('admin_panel:gerenciar_tipos_turma')
    
    context = {
        'tipos_turma': tipos_turma,
        'competencias_disponiveis': competencias_disponiveis,
        'title': 'Gerenciar Tipos de Turma'
    }
    return render(request, 'admin_panel/gerenciar_tipos_turma.html', context)


@coordinador_or_admin
def dashboard_analytics_data_view(request):
    """View que retorna dados JSON para gráficos do dashboard"""
    
    # 1. Dados de progresso por tipo de turma (melhorado)
    tipos_progresso = []
    for tipo in TipoTurma.objects.all():
        turmas_do_tipo = Turma.objects.filter(tipo_turma=tipo)
        if turmas_do_tipo.exists():
            total_notas_possiveis = 0
            total_notas_lancadas = 0
            total_alunos = 0
            
            for turma in turmas_do_tipo:
                alunos_count = Aluno.objects.filter(turma=turma).count()
                total_alunos += alunos_count
                competencias_count = turma.competencias.count() if turma.competencias else 0
                notas_possiveis = alunos_count * competencias_count
                
                if turma.competencias and competencias_count > 0:
                    notas_lancadas = LancamentoDeNota.objects.filter(
                        aluno__turma=turma,
                        competencia__in=turma.competencias.all()
                    ).count()
                else:
                    notas_lancadas = 0
                
                total_notas_possiveis += notas_possiveis
                total_notas_lancadas += notas_lancadas
            
            progresso = int((total_notas_lancadas / total_notas_possiveis) * 100) if total_notas_possiveis > 0 else 0
            
            tipos_progresso.append({
                'nome': tipo.nome,
                'progresso': progresso,
                'notas_lancadas': total_notas_lancadas,
                'notas_possiveis': total_notas_possiveis,
                'turmas_count': turmas_do_tipo.count(),
                'alunos_count': total_alunos
            })

    # 2. Dados simplificados de desempenho por tipo de turma
    tipos_desempenho = []
    for tipo in TipoTurma.objects.all():
        turmas_do_tipo = Turma.objects.filter(tipo_turma=tipo)
        
        if turmas_do_tipo.exists():
            todas_notas = []
            total_alunos = 0
            
            for turma in turmas_do_tipo:
                total_alunos += Aluno.objects.filter(turma=turma).count()
                
                # Buscar todas as notas numéricas desta turma
                notas_turma = LancamentoDeNota.objects.filter(
                    aluno__turma=turma,
                    competencia__tipo_nota='NUM'
                )
                
                for nota in notas_turma:
                    try:
                        valor = float(nota.nota_valor)
                        todas_notas.append(valor)
                    except ValueError:
                        pass
            
            if todas_notas:
                media_tipo = sum(todas_notas) / len(todas_notas)
                tipos_desempenho.append({
                    'nome': tipo.nome,
                    'media': round(media_tipo, 1),
                    'total_notas': len(todas_notas),
                    'total_alunos': total_alunos,
                    'turmas_count': turmas_do_tipo.count()
                })
    
    # Ordenar por média decrescente
    tipos_desempenho.sort(key=lambda x: x['media'], reverse=True)

    # 3. Progresso individual dos professores (mais detalhado)
    professores_detalhados = []
    for professor in Professor.objects.all():
        turmas_prof = Turma.objects.filter(professor_responsavel=professor)
        
        if turmas_prof.exists():
            progresso_por_turma = []
            total_notas_lancadas = 0
            total_notas_possiveis = 0
            
            for turma in turmas_prof:
                alunos_count = Aluno.objects.filter(turma=turma).count()
                competencias_count = turma.competencias.count() if turma.competencias else 0
                notas_possiveis = alunos_count * competencias_count
                
                if turma.competencias and competencias_count > 0:
                    notas_lancadas = LancamentoDeNota.objects.filter(
                        aluno__turma=turma,
                        competencia__in=turma.competencias.all()
                    ).count()
                else:
                    notas_lancadas = 0
                
                progresso_turma = int((notas_lancadas / notas_possiveis) * 100) if notas_possiveis > 0 else 0
                
                progresso_por_turma.append({
                    'turma': turma.identificador_turma,
                    'progresso': progresso_turma,
                    'alunos': alunos_count,
                    'notas_lancadas': notas_lancadas,
                    'notas_possiveis': notas_possiveis
                })
                
                total_notas_lancadas += notas_lancadas
                total_notas_possiveis += notas_possiveis
            
            progresso_geral = int((total_notas_lancadas / total_notas_possiveis) * 100) if total_notas_possiveis > 0 else 0
            
            professores_detalhados.append({
                'nome': professor.user.get_full_name() or professor.user.username,
                'progresso_geral': progresso_geral,
                'turmas': progresso_por_turma,
                'total_alunos': sum(t['alunos'] for t in progresso_por_turma),
                'total_notas_lancadas': total_notas_lancadas,
                'total_notas_possiveis': total_notas_possiveis
            })

    # 4. Análise de desempenho por competência (ranking)
    ranking_competencias = []
    for competencia in Competencia.objects.filter(tipo_nota='NUM'):
        notas = LancamentoDeNota.objects.filter(competencia=competencia)
        
        if notas.exists():
            notas_numericas = []
            for nota in notas:
                try:
                    valor = float(nota.nota_valor)
                    notas_numericas.append(valor)
                except ValueError:
                    pass
            
            if notas_numericas:
                media = sum(notas_numericas) / len(notas_numericas)
                ranking_competencias.append({
                    'nome': competencia.nome,
                    'media': round(media, 1),
                    'total_avaliacoes': len(notas_numericas),
                    'min_nota': min(notas_numericas),
                    'max_nota': max(notas_numericas)
                })
    
    # Ordenar por média decrescente
    ranking_competencias.sort(key=lambda x: x['media'], reverse=True)

    # 5. Distribuição de notas por faixa de desempenho
    distribuicao_notas = {
        'Insuficiente (0-40)': 0,
        'Regular (41-60)': 0, 
        'Bom (61-80)': 0,
        'Excelente (81-100)': 0
    }
    
    # Buscar todas as notas numéricas
    notas_numericas = LancamentoDeNota.objects.filter(
        competencia__tipo_nota='NUM'
    )
    
    total_notas_numericas = 0
    for nota in notas_numericas:
        try:
            valor = float(nota.nota_valor)
            total_notas_numericas += 1
            
            if valor <= 40:
                distribuicao_notas['Insuficiente (0-40)'] += 1
            elif valor <= 60:
                distribuicao_notas['Regular (41-60)'] += 1
            elif valor <= 80:
                distribuicao_notas['Bom (61-80)'] += 1
            else:
                distribuicao_notas['Excelente (81-100)'] += 1
        except ValueError:
            continue
    
    # Converter para percentuais
    if total_notas_numericas > 0:
        distribuicao_percentual = {
            faixa: round((count / total_notas_numericas) * 100, 1)
            for faixa, count in distribuicao_notas.items()
        }
    else:
        distribuicao_percentual = {faixa: 0 for faixa in distribuicao_notas.keys()}

    data = {
        'tipos_progresso': tipos_progresso,
        'tipos_desempenho': tipos_desempenho,
        'professores_detalhados': professores_detalhados,
        'ranking_competencias': ranking_competencias,
        'distribuicao_notas': distribuicao_percentual,
        'total_notas_numericas': total_notas_numericas,
        'resumo': {
            'total_turmas': Turma.objects.count(),
            'total_alunos': Aluno.objects.count(),
            'total_notas': LancamentoDeNota.objects.count(),
            'total_professores': Professor.objects.count(),
            'total_competencias': Competencia.objects.count(),
            'media_geral': round(
                sum(item['media'] for item in ranking_competencias) / len(ranking_competencias), 1
            ) if ranking_competencias else 0
        }
    }
    
    return JsonResponse(data)


@coordinador_or_admin
def dashboard_analytics_view(request):
    """View para exibir a página de analytics com gráficos"""
    context = {
        'title': 'Dashboard Analytics'
    }
    return render(request, 'admin_panel/dashboard_analytics.html', context)


@coordinador_or_admin
def configurar_data_limite_view(request):
    """View para configurar a data limite através de interface gráfica"""
    
    # Busca a configuração atual
    data_limite_atual = ConfiguracaoSistema.get_data_limite_notas()
    
    if request.method == 'POST':
        try:
            # Recebe os dados do formulário
            dia = int(request.POST.get('dia'))
            mes = int(request.POST.get('mes'))
            ano = int(request.POST.get('ano'))
            
            # Valida a data
            nova_data = date(ano, mes, dia)
            
            # Verifica se a data não é no passado
            if nova_data < date.today():
                messages.error(request, 'A data limite não pode ser no passado.')
                return redirect('admin_panel:configurar_data_limite')
            
            # Atualiza ou cria a configuração
            config, created = ConfiguracaoSistema.objects.get_or_create(
                nome='data_limite_notas',
                defaults={
                    'valor': nova_data.isoformat(),
                    'descricao': 'Data limite para entrega de todas as notas pelos professores'
                }
            )
            
            if not created:
                config.valor = nova_data.isoformat()
                config.save()
            
            messages.success(
                request, 
                f'Data limite atualizada com sucesso para {nova_data.strftime("%d/%m/%Y")}!'
            )
            
            return redirect('admin_panel:configurar_data_limite')
            
        except (ValueError, TypeError) as e:
            messages.error(request, 'Data inválida. Verifique os valores inseridos.')
    
    # Preparar dados para o template
    ano_atual = date.today().year
    
    context = {
        'data_limite_atual': data_limite_atual,
        'dias': range(1, 32),  # Dias de 1 a 31
        'anos': range(ano_atual, ano_atual + 5),  # Próximos 5 anos
    }
    
    return render(request, 'admin_panel/configurar_data_limite.html', context)


@admin_only
def nova_turma_view(request):
    """View para criar uma nova turma"""
    tipos_turma = TipoTurma.objects.all().order_by('nome')
    professores = Professor.objects.select_related('user').all().order_by('user__first_name')
    
    if request.method == 'POST':
        tipo_turma_id = request.POST.get('tipo_turma')
        identificador_turma = request.POST.get('identificador_turma')
        professor_id = request.POST.get('professor_responsavel')
        boletim_tipo = request.POST.get('boletim_tipo')
        
        if tipo_turma_id and identificador_turma:
            try:
                tipo_turma = TipoTurma.objects.get(id=tipo_turma_id)
                professor = Professor.objects.get(id=professor_id) if professor_id else None
                
                # Criar a turma
                turma = Turma.objects.create(
                    tipo_turma=tipo_turma,
                    identificador_turma=identificador_turma,
                    professor_responsavel=professor,
                    boletim_tipo=boletim_tipo if boletim_tipo else 'junior'
                )
                
                # As competências agora são automaticamente definidas pelo boletim_tipo
                # através da propriedade turma.competencias
                competencias_count = turma.competencias.count()
                
                messages.success(
                    request, 
                    f'Turma "{turma.nome}" criada com sucesso! ({competencias_count} competências do tipo {turma.get_boletim_tipo_display()})'
                )
                
                return redirect('admin_panel:configurar_turma', turma_id=turma.id)
                
            except Exception as e:
                messages.error(request, f'Erro ao criar turma: {str(e)}')
        else:
            messages.error(request, 'Tipo de turma e identificador são obrigatórios.')
    
    # Buscar as opções de boletim da model Turma
    boletim_tipos = Turma.BOLETIM_TIPOS
    
    context = {
        'title': 'Nova Turma',
        'tipos_turma': tipos_turma,
        'professores': professores,
        'boletim_tipos': boletim_tipos,
    }
    return render(request, 'admin_panel/nova_turma.html', context)


@admin_only
def configurar_turma_view(request, turma_id):
    """View para configurar uma turma recém-criada"""
    turma = get_object_or_404(Turma, id=turma_id)
    
    context = {
        'title': f'Configurar {turma.nome}',
        'turma': turma,
        'total_alunos': turma.alunos.count(),
        'competencias': turma.competencias.all() if turma.competencias else [],
    }
    return render(request, 'admin_panel/configurar_turma.html', context)


# ===============================
# VIEWS PARA GERAÇÃO DE BOLETINS
# ===============================

@coordinador_or_admin
def visualizar_boletim_markdown(request, aluno_id):
    """Permite baixar o boletim de um aluno em formato Word (.docx)"""
    aluno = get_object_or_404(Aluno, id=aluno_id)
    
    try:
        # Gerar boletim em Word usando os novos templates
        boletim_doc = BoletimGenerator.gerar_boletim(aluno)
        
        # Criar resposta HTTP com o arquivo Word
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="boletim_{aluno.nome_completo.replace(" ", "_")}.docx"'
        
        # Salvar o documento na resposta
        boletim_doc.save(response)
        
        return response
    
    except Exception as e:
        messages.error(request, f'Erro ao gerar boletim: {str(e)}')
        return redirect('admin_panel:detalhes_turma', turma_id=aluno.turma.id)


@coordinador_or_admin
def gerar_boletim_individual(request, aluno_id):
    """Gera boletim individual de um aluno usando template Word"""
    aluno = get_object_or_404(Aluno, id=aluno_id)
    
    if not aluno.tem_notas_completas():
        messages.warning(request, f'O aluno {aluno.nome_completo} não possui todas as notas lançadas.')
        return redirect('admin_panel:detalhes_turma', turma_id=aluno.turma.id)
    
    try:
        # Gerar boletim usando template Word da pasta boletins
        boletim_doc = BoletimGenerator.gerar_boletim(aluno)
        
        # Criar buffer temporário para salvar o documento
        buffer = io.BytesIO()
        boletim_doc.save(buffer)
        buffer.seek(0)
        
        # Criar resposta HTTP com arquivo Word
        response = HttpResponse(
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="boletim_{aluno.nome_completo.replace(" ", "_")}.docx"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erro ao gerar boletim: {str(e)}')
        return redirect('admin_panel:detalhes_turma', turma_id=aluno.turma.id)


@coordinador_or_admin
def gerar_boletins_turma(request, turma_id):
    """Gera boletins Word de todos os alunos de uma turma com notas completas"""
    turma = get_object_or_404(Turma, id=turma_id)
    
    # Verificar quais alunos têm notas completas
    alunos_completos = []
    alunos_incompletos = []
    
    for aluno in turma.alunos.filter(ativo=True):
        if aluno.tem_notas_completas():
            alunos_completos.append(aluno)
        else:
            alunos_incompletos.append(aluno)
    
    if not alunos_completos:
        messages.error(request, 'Nenhum aluno da turma possui todas as notas lançadas.')
        return redirect('admin_panel:detalhes_turma', turma_id=turma.id)
    
    # Se for apenas 1 aluno, retorna o arquivo Word individual
    if len(alunos_completos) == 1:
        return gerar_boletim_individual(request, alunos_completos[0].id)
    
    # Para múltiplos alunos, criar um ZIP com todos os boletins Word
    import zipfile
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for aluno in alunos_completos:
            try:
                # Gerar boletim Word para cada aluno
                boletim_doc = BoletimGenerator.gerar_boletim(aluno)
                
                # Salvar em buffer temporário
                doc_buffer = io.BytesIO()
                boletim_doc.save(doc_buffer)
                doc_buffer.seek(0)
                
                # Adicionar ao ZIP
                filename = f"boletim_{aluno.nome_completo.replace(' ', '_')}.docx"
                zip_file.writestr(filename, doc_buffer.read())
                
            except Exception as e:
                logger.error(f"Erro ao gerar boletim para {aluno.nome_completo}: {str(e)}")
    
    zip_buffer.seek(0)
    
    # Criar resposta HTTP com ZIP
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="boletins_{turma.identificador_turma.replace(" ", "_")}.zip"'
    
    # Adicionar mensagem sobre alunos incompletos
    if alunos_incompletos:
        nomes_incompletos = [aluno.nome_completo for aluno in alunos_incompletos]
        messages.warning(
            request, 
            f'Boletins gerados para {len(alunos_completos)} alunos. '
            f'Os seguintes alunos foram pulados por não terem todas as notas: {", ".join(nomes_incompletos)}'
        )
    else:
        messages.success(request, f'Boletins gerados com sucesso para todos os {len(alunos_completos)} alunos da turma.')
    
    return response


@coordinador_or_admin
def verificar_notas_turma(request, turma_id):
    """Verifica o status das notas de uma turma e retorna JSON"""
    turma = get_object_or_404(Turma, id=turma_id)
    
    alunos_status = []
    alunos_completos = 0
    alunos_incompletos = 0
    
    for aluno in turma.alunos.filter(ativo=True):
        tem_completas = aluno.tem_notas_completas()
        progresso = aluno.get_progresso_completo()
        
        alunos_status.append({
            'id': aluno.id,
            'nome': aluno.nome_completo,
            'tem_completas': tem_completas,
            'progresso': progresso
        })
        
        if tem_completas:
            alunos_completos += 1
        else:
            alunos_incompletos += 1
    
    return JsonResponse({
        'alunos_completos': alunos_completos,
        'alunos_incompletos': alunos_incompletos,
        'total_alunos': len(alunos_status),
        'alunos_status': alunos_status,
        'pode_gerar_boletins': alunos_completos > 0
    })