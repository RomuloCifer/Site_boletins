import pandas as pd # Para processar arquivos CSV/Excel
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required # Garante que apenas administradores acessem
from django.contrib import messages
from core.models import Turma, Aluno
import io
# Create your views here.


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
@staff_member_required
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
                        
                    messages.success(request, 
                    f"Importação EM LOTE concluída. "
                    f"Criados: {alunos_criados} | Atualizados: {alunos_atualizados}."
                )
                    if erros_turma_nao_encontrada:
                        mensagens_erro = ", ".join(erros_turma_nao_encontrada)
                        messages.warning(request, f"As seguintes turmas não foram encontradas: {mensagens_erro}.")
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
                    f"Importação concluída para a Turma '{turma.nome}'. "
                    f"Criados: {alunos_criados} | Atualizados: {alunos_atualizados}."
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