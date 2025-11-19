"""
Comando Django para migrar notas conceituais do sistema antigo (I-D-C-A) para o novo (A-B-C-D)
Execute com: python manage.py migrar_notas_conceituais
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import LancamentoDeNota, Competencia

class Command(BaseCommand):
    help = 'Migra notas conceituais do sistema antigo (I-D-C-A) para o novo (A-B-C-D)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Executa sem salvar alterações (apenas mostra o que seria alterado)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será salva'))
        
        # Mapeamento do sistema antigo para o novo
        mapeamento = {
            'I': 'D',  # Iniciante → D (Ainda não atingiu)
            'D': 'C',  # Desenvolvendo → C (Atinge parcialmente)  
            'C': 'B',  # Consegue → B (Atinge satisfatoriamente)
            'A': 'A',  # Avançado → A (Atinge plenamente) - se mantém
        }
        
        # Buscar todas as notas conceituais
        notas_conceituais = LancamentoDeNota.objects.filter(
            competencia__tipo_nota='ABC'
        ).select_related('aluno', 'competencia')
        
        alteracoes = []
        total_notas = notas_conceituais.count()
        
        self.stdout.write(f'Analisando {total_notas} notas conceituais...')
        
        for nota in notas_conceituais:
            valor_antigo = nota.nota_valor
            if valor_antigo in mapeamento:
                valor_novo = mapeamento[valor_antigo]
                if valor_antigo != valor_novo:  # Só migra se realmente mudou
                    alteracoes.append({
                        'nota': nota,
                        'antigo': valor_antigo,
                        'novo': valor_novo
                    })
        
        if not alteracoes:
            self.stdout.write(self.style.SUCCESS('✅ Todas as notas já estão no formato correto A-B-C-D!'))
            return
        
        self.stdout.write(f'Encontradas {len(alteracoes)} notas para migrar:')
        
        for alteracao in alteracoes:
            nota = alteracao['nota']
            self.stdout.write(
                f"  • {nota.aluno.nome_completo} - {nota.competencia.nome}: "
                f"{alteracao['antigo']} → {alteracao['novo']}"
            )
        
        if not dry_run:
            try:
                with transaction.atomic():
                    for alteracao in alteracoes:
                        alteracao['nota'].nota_valor = alteracao['novo']
                        alteracao['nota'].save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {len(alteracoes)} notas migradas com sucesso!')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro durante a migração: {e}')
                )
        else:
            self.stdout.write(
                self.style.WARNING(f'DRY-RUN: {len(alteracoes)} notas seriam migradas')
            )