"""
Management command para criar competências e tipos de turma
Uso: python manage.py setup_sistema
"""

from django.core.management.base import BaseCommand
from core.models import Competencia, TipoTurma

class Command(BaseCommand):
    help = 'Cria competências e tipos de turma automaticamente'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Iniciando criação de competências e tipos de turma...")
        
        # Definir todas as competências únicas
        todas_competencias = [
            'Produção Oral',
            'Produção Escrita',
            'Avaliações de Progresso',
            'Compreensão Oral',
            'Compreensão Escrita',
            'Writing Bit 01',
            'Writing Bit 02',
            'Checkpoints',
            'Comunicação Oral',
            'Comunicação Escrita',
            'Compreensão de Leitura',
            'Interesse pela Aprendizagem',
            'Colaboração',
            'Engajamento',
        ]
        
        # Criar competências
        self.stdout.write("\n📝 Criando competências...")
        competencias_criadas = {}
        for nome_comp in todas_competencias:
            comp, created = Competencia.objects.get_or_create(
                nome=nome_comp,
                defaults={'tipo_nota': 'ABC'}  # Conceitual por padrão
            )
            competencias_criadas[nome_comp] = comp
            if created:
                self.stdout.write(f"  ✅ Criada: {nome_comp}")
            else:
                self.stdout.write(f"  ⏭️  Já existe: {nome_comp}")
        
        # Configuração dos tipos de turma
        tipos_config = {
            'Adolescentes - Adultos': [
                'Produção Oral',
                'Produção Escrita',
                'Avaliações de Progresso',
            ],
            'Material Antigo': [
                'Produção Oral',
                'Produção Escrita',
                'Compreensão Oral',
                'Compreensão Escrita',
                'Writing Bit 01',
                'Writing Bit 02',
                'Checkpoints',
            ],
            'Lion Stars': [
                'Comunicação Oral',
                'Compreensão Oral',
                'Interesse pela Aprendizagem',
                'Colaboração',
                'Engajamento',
            ],
            'Junior': [
                'Comunicação Oral',
                'Compreensão Oral',
                'Comunicação Escrita',
                'Compreensão de Leitura',
                'Interesse pela Aprendizagem',
                'Colaboração',
                'Engajamento',
            ]
        }
        
        # Criar tipos de turma
        self.stdout.write("\n📚 Criando tipos de turma e associando competências...")
        for nome_tipo, competencias_nomes in tipos_config.items():
            tipo_turma, created = TipoTurma.objects.get_or_create(
                nome=nome_tipo,
                defaults={'descricao': f'Tipo de turma para {nome_tipo}'}
            )
            
            if created:
                self.stdout.write(f"\n  ✅ Criado: {nome_tipo}")
            else:
                self.stdout.write(f"\n  ⏭️  Já existe: {nome_tipo}")
            
            # Associar competências
            competencias_tipo = [competencias_criadas[nome] for nome in competencias_nomes]
            tipo_turma.competencias.set(competencias_tipo)
            self.stdout.write(f"     📌 {len(competencias_tipo)} competências associadas")
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🎉 CONCLUÍDO!"))
        self.stdout.write(f"   • Competências: {Competencia.objects.count()}")
        self.stdout.write(f"   • Tipos de turma: {TipoTurma.objects.count()}")
        self.stdout.write("="*60)
