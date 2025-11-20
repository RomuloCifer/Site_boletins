# Utilitários para Otimização de Performance
from django.db.models import Prefetch, Count, Q
from django.core.cache import cache
from django.conf import settings
from core.models import Turma, Aluno, LancamentoDeNota, Professor, Competencia
import logging

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """
    Classe para otimizar queries do banco de dados
    """
    
    @staticmethod
    def get_turmas_com_progresso_otimizado(professor=None):
        """
        Versão otimizada para buscar turmas com estatísticas de progresso
        Reduz significativamente o número de queries ao banco
        """
        # Query base com select_related e prefetch_related
        queryset = Turma.objects.select_related(
            'tipo_turma',
            'professor_responsavel__user'
        ).prefetch_related(
            'competencias',
            Prefetch(
                'alunos',
                queryset=Aluno.objects.only('id', 'nome_completo', 'turma_id')
            ),
            Prefetch(
                'alunos__lancamentos_de_nota',
                queryset=LancamentoDeNota.objects.select_related('competencia')
            )
        )
        
        # Filtrar por professor se especificado
        if professor:
            queryset = queryset.filter(professor_responsavel=professor)
        
        # Anotar com contagens
        queryset = queryset.annotate(
            total_alunos=Count('alunos', distinct=True),
            total_notas_lancadas=Count('alunos__lancamentos_de_nota', distinct=True)
        )
        
        return queryset
    
    @staticmethod
    def get_dashboard_admin_otimizado():
        """
        Query otimizada para o dashboard administrativo
        """
        cache_key = 'dashboard_admin_data'
        cached_data = cache.get(cache_key)
        
        if cached_data and not settings.DEBUG:
            return cached_data
        
        # Query principal otimizada
        turmas = Turma.objects.select_related(
            'tipo_turma',
            'professor_responsavel__user'
        ).prefetch_related(
            'competencias'
        ).annotate(
            total_alunos=Count('alunos', distinct=True),
            total_notas=Count('alunos__lancamentos_de_nota', distinct=True)
        )
        
        data = {
            'turmas': list(turmas),
            'totais': {
                'turmas': turmas.count(),
                'alunos': sum(getattr(t, 'total_alunos', 0) for t in turmas),
                'notas': sum(getattr(t, 'total_notas', 0) for t in turmas)
            }
        }
        
        # Cache por 5 minutos
        cache.set(cache_key, data, 300)
        return data

class CacheManager:
    """
    Gerenciador de cache para dados frequentemente acessados
    """
    
    @staticmethod
    def get_or_set_cache(key, callable_func, timeout=300):
        """
        Busca no cache ou executa função e armazena resultado
        """
        data = cache.get(key)
        if data is None:
            data = callable_func()
            cache.set(key, data, timeout)
        return data
    
    @staticmethod
    def invalidate_turma_cache(turma_id):
        """
        Invalida cache relacionado a uma turma específica
        """
        keys_to_delete = [
            f'turma_progresso_{turma_id}',
            f'turma_detalhes_{turma_id}',
            'dashboard_admin_data',
            'dashboard_analytics_data'
        ]
        cache.delete_many(keys_to_delete)
    
    @staticmethod
    def invalidate_professor_cache(professor_id):
        """
        Invalida cache relacionado a um professor específico
        """
        keys_to_delete = [
            f'professor_dashboard_{professor_id}',
            'dashboard_admin_data'
        ]
        cache.delete_many(keys_to_delete)

class DataValidator:
    """
    Validações de dados e integridade
    """
    
    @staticmethod
    def validate_nota_valor(valor, tipo_nota):
        """
        Valida se o valor da nota está correto para o tipo
        """
        if tipo_nota == 'NUM':
            try:
                num_valor = float(valor)
                if 0 <= num_valor <= 100:
                    return True, num_valor
                else:
                    return False, "Nota numérica deve estar entre 0 e 100"
            except ValueError:
                return False, "Valor deve ser um número"
        
        elif tipo_nota == 'ABC':
            if valor.upper() in ['A', 'B', 'C', 'D']:
                return True, valor.upper()
            else:
                return False, "Nota conceitual deve ser A, B, C ou D"
        
        return False, "Tipo de nota inválido"
    
    @staticmethod
    def validate_import_data(df):
        """
        Valida dados de importação em lote
        """
        errors = []
        warnings = []
        
        # Verificar colunas obrigatórias
        required_columns = ['nome_completo']
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Coluna obrigatória '{col}' não encontrada")
        
        # Verificar dados vazios
        if df['nome_completo'].isnull().any():
            warnings.append("Alguns nomes estão vazios e serão ignorados")
        
        # Verificar nomes duplicados no arquivo
        duplicates = df[df.duplicated(subset=['nome_completo'], keep=False)]
        if not duplicates.empty:
            warnings.append(f"{len(duplicates)} nomes duplicados encontrados no arquivo")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'stats': {
                'total_rows': len(df),
                'valid_names': df['nome_completo'].notna().sum(),
                'duplicates': len(duplicates)
            }
        }

class ProgressCalculator:
    """
    Calculadora de progresso otimizada
    """
    
    @staticmethod
    def calculate_turma_progress(turma):
        """
        Calcula progresso de uma turma de forma otimizada
        """
        if not turma.competencias.exists():
            return {
                'progresso_percentual': 0,
                'alunos_completos': 0,
                'total_alunos': 0,
                'notas_lancadas': 0,
                'notas_possiveis': 0
            }
        
        alunos = turma.alunos.all()
        competencias = turma.competencias.all()
        
        total_alunos = len(alunos)
        total_competencias = len(competencias)
        total_notas_possiveis = total_alunos * total_competencias
        
        # Buscar todas as notas da turma de uma vez
        notas = LancamentoDeNota.objects.filter(
            aluno__in=alunos,
            competencia__in=competencias
        ).select_related('aluno', 'competencia')
        
        # Contar notas por aluno
        notas_por_aluno = {}
        for nota in notas:
            aluno_id = nota.aluno.pk
            if aluno_id not in notas_por_aluno:
                notas_por_aluno[aluno_id] = 0
            notas_por_aluno[aluno_id] += 1
        
        # Contar alunos completos
        alunos_completos = sum(
            1 for count in notas_por_aluno.values() 
            if count >= total_competencias
        )
        
        progresso_percentual = 0
        if total_notas_possiveis > 0:
            progresso_percentual = (len(notas) / total_notas_possiveis) * 100
        
        return {
            'progresso_percentual': int(progresso_percentual),
            'alunos_completos': alunos_completos,
            'total_alunos': total_alunos,
            'notas_lancadas': len(notas),
            'notas_possiveis': total_notas_possiveis
        }


class ProblemaSystemaManager:
    """
    Gerenciador para criação automática de problemas detectados pelo sistema
    """
    
    @staticmethod
    def criar_problema_automatico(tipo_problema, titulo, descricao, professor=None, turma=None, aluno=None, prioridade='MEDIA'):
        """
        Cria um problema detectado automaticamente pelo sistema
        """
        from .models import ProblemaRelatado
        from django.utils import timezone
        
        # Verifica se já existe um problema similar pendente
        problema_existente = ProblemaRelatado.objects.filter(
            origem='SISTEMA',
            tipo_problema=tipo_problema,
            status__in=['PENDENTE', 'EM_ANALISE'],
            turma=turma,
            aluno=aluno
        ).first()
        
        if problema_existente:
            # Atualiza a data do problema existente em vez de criar um novo
            problema_existente.data_atualizacao = timezone.now()
            problema_existente.save()
            return problema_existente
        
        # Cria novo problema
        problema = ProblemaRelatado.objects.create(
            origem='SISTEMA',
            professor=professor,
            turma=turma,
            aluno=aluno,
            tipo_problema=tipo_problema,
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade
        )
        
        logger.info(f"Problema automático criado: {problema}")
        return problema
    
    @staticmethod
    def detectar_e_criar_problemas_automaticos():
        """
        Detecta e cria problemas automaticamente baseado no estado do sistema
        """
        from .models import Turma, Aluno, Professor
        from django.db.models import Count
        
        problemas_criados = []
        
        # 1. Detectar turmas sem professor
        turmas_sem_professor = Turma.objects.filter(professor_responsavel__isnull=True)
        for turma in turmas_sem_professor:
            problema = ProblemaSystemaManager.criar_problema_automatico(
                tipo_problema='TURMA_SEM_PROFESSOR',
                titulo=f'Turma {turma.nome} sem professor responsável',
                descricao=f'A turma {turma.nome} ({turma.identificador_turma}) não possui um professor responsável atribuído.',
                turma=turma,
                prioridade='ALTA'
            )
            problemas_criados.append(problema)
        
        # 2. Detectar professores sem turma
        professores_sem_turma = Professor.objects.filter(turmas__isnull=True)
        for professor in professores_sem_turma:
            problema = ProblemaSystemaManager.criar_problema_automatico(
                tipo_problema='PROFESSOR_SEM_TURMA',
                titulo=f'Professor {professor.user.get_full_name() or professor.user.username} sem turma',
                descricao=f'O professor {professor.user.get_full_name() or professor.user.username} não possui turmas atribuídas.',
                professor=professor,
                prioridade='BAIXA'
            )
            problemas_criados.append(problema)
        
        # 3. Detectar alunos duplicados na mesma turma
        alunos_duplicados = Aluno.objects.values('nome_completo', 'turma').annotate(
            total=Count('id')
        ).filter(total__gt=1)
        
        for duplicado in alunos_duplicados:
            turma = Turma.objects.get(id=duplicado['turma'])
            alunos = Aluno.objects.filter(
                nome_completo=duplicado['nome_completo'],
                turma=turma
            )
            
            problema = ProblemaSystemaManager.criar_problema_automatico(
                tipo_problema='ALUNO_DUPLICADO',
                titulo=f'Aluno duplicado: {duplicado["nome_completo"]} na turma {turma.nome}',
                descricao=f'O aluno {duplicado["nome_completo"]} aparece {duplicado["total"]} vezes na turma {turma.nome}.',
                turma=turma,
                prioridade='ALTA'
            )
            problemas_criados.append(problema)
        
        return problemas_criados


class BoletimGenerator:
    """
    Classe para gerar boletins personalizados usando templates markdown com placeholders
    """
    
    # Mapeamento de tipos de boletim para arquivos de template
    TEMPLATE_MAP = {
        'adolescentes_adultos': 'adolescentes_adultos.md',
        'material_antigo': 'material_antigo.md',
        'lion_stars': 'lion_stars.md',
        'junior': 'junior.md',
    }
    
    # Mapeamento de competências para placeholders por tipo de boletim
    COMPETENCIA_PLACEHOLDERS = {
        'adolescentes_adultos': [
            'producao_oral',
            'producao_escrita',
            'avaliacoes_progresso',
        ],
        'material_antigo': [
            'producao_oral',
            'producao_escrita',
            'compreensao_oral',
            'compreensao_escrita',
            'writing_bit_01',
            'writing_bit_02',
            'checkpoints',
        ],
        'lion_stars': [
            'comunicacao_oral',
            'compreensao_oral',
            'interesse_aprendizagem',
            'colaboracao',
            'engajamento',
        ],
        'junior': [
            'comunicacao_oral',
            'compreensao_oral',
            'comunicacao_escrita',
            'compreensao_escrita',
            'interesse_aprendizagem',
            'colaboracao',
            'engajamento',
        ],
    }
    
    @staticmethod
    def _get_template_path(boletim_tipo):
        """
        Retorna o caminho completo do template de boletim
        """
        import os
        from django.conf import settings
        
        template_file = BoletimGenerator.TEMPLATE_MAP.get(boletim_tipo)
        if not template_file:
            raise ValueError(f"Tipo de boletim '{boletim_tipo}' não encontrado")
        
        # Caminho para a pasta de templates de boletim
        base_dir = settings.BASE_DIR
        template_path = os.path.join(base_dir, 'core', 'templates', 'boletins', template_file)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template de boletim não encontrado: {template_path}")
        
        return template_path
    
    @staticmethod
    def _normalizar_nome_competencia(nome_competencia):
        """
        Normaliza o nome da competência para corresponder aos placeholders
        Remove acentos, caracteres especiais e converte para snake_case
        """
        import unicodedata
        
        # Remove acentos
        nfkd = unicodedata.normalize('NFKD', nome_competencia)
        nome_sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
        
        # Converte para minúsculas e substitui espaços por underscore
        nome_normalizado = nome_sem_acento.lower()
        nome_normalizado = nome_normalizado.replace(' ', '_')
        
        # Remove caracteres especiais, mantendo apenas letras, números e underscore
        nome_normalizado = ''.join(c for c in nome_normalizado if c.isalnum() or c == '_')
        
        # Remove partes entre parênteses (como percentuais)
        if '(' in nome_normalizado:
            nome_normalizado = nome_normalizado.split('(')[0].strip('_')
        
        return nome_normalizado
    
    @staticmethod
    def gerar_boletim(aluno):
        """
        Gera o boletim personalizado para um aluno específico
        
        Args:
            aluno: Instância do model Aluno
            
        Returns:
            str: Conteúdo do boletim em markdown com placeholders preenchidos
            
        Raises:
            ValueError: Se o tipo de boletim da turma não for válido
            FileNotFoundError: Se o template não for encontrado
        """
        turma = aluno.turma
        boletim_tipo = turma.boletim_tipo
        
        # Carrega o template
        template_path = BoletimGenerator._get_template_path(boletim_tipo)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Dados básicos do aluno
        dados_basicos = {
            'aluno': aluno.nome_completo,
            'nivel': turma.tipo_turma.nome if turma.tipo_turma else turma.identificador_turma,
            'professor': turma.professor_responsavel.nome if turma.professor_responsavel else 'N/A',
        }
        
        # Substitui dados básicos
        boletim_content = template_content
        for placeholder, valor in dados_basicos.items():
            boletim_content = boletim_content.replace(f'<<{placeholder}>>', valor)
        
        # Busca as notas do aluno
        notas_dict = aluno.get_notas_boletim()
        
        # Substitui as notas/competências
        placeholders_esperados = BoletimGenerator.COMPETENCIA_PLACEHOLDERS.get(boletim_tipo, [])
        
        for placeholder in placeholders_esperados:
            # Busca a nota correspondente no dicionário de notas
            nota_encontrada = 'N/A'
            
            for competencia_nome, nota_info in notas_dict.items():
                competencia_normalizada = BoletimGenerator._normalizar_nome_competencia(competencia_nome)
                
                if competencia_normalizada == placeholder or placeholder in competencia_normalizada:
                    nota_encontrada = nota_info.get('conceito', 'N/A')
                    break
            
            boletim_content = boletim_content.replace(f'<<{placeholder}>>', nota_encontrada)
        
        logger.info(f"Boletim gerado com sucesso para aluno {aluno.nome_completo} (Turma: {turma.nome})")
        
        return boletim_content
    
    @staticmethod
    def gerar_boletim_turma(turma):
        """
        Gera boletins para todos os alunos de uma turma
        
        Args:
            turma: Instância do model Turma
            
        Returns:
            dict: Dicionário com {aluno_id: boletim_content}
        """
        boletins = {}
        alunos = turma.alunos.filter(ativo=True)
        
        for aluno in alunos:
            try:
                boletim_content = BoletimGenerator.gerar_boletim(aluno)
                boletins[aluno.id] = boletim_content
            except Exception as e:
                logger.error(f"Erro ao gerar boletim para aluno {aluno.nome_completo}: {str(e)}")
                boletins[aluno.id] = None
        
        return boletins