import pandas as pd # Para processar arquivos CSV/Excel
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required # Garante que apenas administradores acessem
from django.contrib import messages
from django.http import JsonResponse
from core.models import Turma, Aluno, Professor, Competencia, LancamentoDeNota, TipoTurma
from .decorators import group_required, admin_only, coordinador_or_admin, secretaria_or_above
import io
# Create your views here.

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
    
    context = {
        'turmas_com_progresso': turmas_com_progresso,
        'total_turmas': turmas.count(),
        'total_alunos_geral': sum(t['total_alunos'] for t in turmas_com_progresso),
        'total_notas_lancadas_geral': sum(t['notas_lancadas'] for t in turmas_com_progresso),
        'total_notas_possiveis_geral': sum(t['total_notas_possiveis'] for t in turmas_com_progresso),
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

    # 2. Dados detalhados de competências por unidade/tipo
    competencias_detalhadas = []
    for competencia in Competencia.objects.all():
        # Agrupa por tipo de turma
        tipos_stats = {}
        
        for tipo in TipoTurma.objects.filter(competencias=competencia):
            turmas_do_tipo = Turma.objects.filter(tipo_turma=tipo)
            notas_do_tipo = []
            
            for turma in turmas_do_tipo:
                notas_turma = LancamentoDeNota.objects.filter(
                    competencia=competencia,
                    aluno__turma=turma
                )
                
                if competencia.tipo_nota == 'NUM':
                    for nota in notas_turma:
                        try:
                            valor = float(nota.nota_valor)
                            notas_do_tipo.append(valor)
                        except ValueError:
                            pass
            
            if notas_do_tipo:
                media = sum(notas_do_tipo) / len(notas_do_tipo)
                tipos_stats[tipo.nome] = {
                    'media': round(media, 1),
                    'total_notas': len(notas_do_tipo),
                    'min': min(notas_do_tipo),
                    'max': max(notas_do_tipo)
                }
        
        if tipos_stats:
            competencias_detalhadas.append({
                'nome': competencia.nome,
                'tipo_nota': competencia.tipo_nota,
                'por_tipo': tipos_stats
            })

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

    # 5. Evolução temporal das notas (últimos 30 dias)
    from datetime import datetime, timedelta
    
    try:
        data_limite = datetime.now() - timedelta(days=30)
        
        evolucao_temporal = []
        notas_recentes = LancamentoDeNota.objects.filter(
            data_lancamento__gte=data_limite
        ).order_by('data_lancamento')
        
        # Agrupar por semana
        semanas_stats = {}
        for nota in notas_recentes:
            # Calcular número da semana
            semana = nota.data_lancamento.isocalendar()[1]
            ano = nota.data_lancamento.year
            chave_semana = f"{ano}-S{semana}"
            
            if chave_semana not in semanas_stats:
                semanas_stats[chave_semana] = {
                    'notas_lancadas': 0,
                    'data': nota.data_lancamento.strftime('%d/%m')
                }
            
            semanas_stats[chave_semana]['notas_lancadas'] += 1
        
        evolucao_temporal = [
            {
                'periodo': periodo,
                'notas_lancadas': dados['notas_lancadas'],
                'data': dados['data']
            }
            for periodo, dados in semanas_stats.items()
        ]
    except Exception as e:
        # Se houver erro na evolução temporal, retorna lista vazia
        evolucao_temporal = []

    data = {
        'tipos_progresso': tipos_progresso,
        'competencias_detalhadas': competencias_detalhadas,
        'professores_detalhados': professores_detalhados,
        'ranking_competencias': ranking_competencias,
        'evolucao_temporal': evolucao_temporal,
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