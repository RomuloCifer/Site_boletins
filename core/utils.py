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