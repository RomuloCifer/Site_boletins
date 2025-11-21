from django.core.management.base import BaseCommand
from core.models import Competencia


class Command(BaseCommand):
    help = 'Cria as competências padrão necessárias para todos os tipos de boletim'

    def handle(self, *args, **options):
        """
        Cria todas as competências padrão usadas nos boletins
        """
        
        competencias_padrao = [
            # Competências para adolescentes_adultos
            {'nome': 'Produção Oral', 'tipo_nota': 'ABC'},
            {'nome': 'Produção Escrita', 'tipo_nota': 'ABC'},
            {'nome': 'Avaliações de Progresso', 'tipo_nota': 'ABC'},
            
            # Competências para material_antigo
            {'nome': 'Compreensão Oral', 'tipo_nota': 'ABC'},
            {'nome': 'Compreensão Escrita', 'tipo_nota': 'ABC'},
            {'nome': 'Writing Bit 01', 'tipo_nota': 'ABC'},
            {'nome': 'Writing Bit 02', 'tipo_nota': 'ABC'},
            {'nome': 'Checkpoints', 'tipo_nota': 'ABC'},
            
            # Competências para lion_stars
            {'nome': 'Comunicação Oral', 'tipo_nota': 'ABC'},
            {'nome': 'Interesse pela Aprendizagem', 'tipo_nota': 'ABC'},
            {'nome': 'Colaboração', 'tipo_nota': 'ABC'},
            {'nome': 'Engajamento', 'tipo_nota': 'ABC'},
            
            # Competências para junior
            {'nome': 'Comunicação Escrita', 'tipo_nota': 'ABC'},
            {'nome': 'Compreensão Escrita', 'tipo_nota': 'ABC'},
        ]
        
        criadas = 0
        existentes = 0
        
        for comp_data in competencias_padrao:
            competencia, created = Competencia.objects.get_or_create(
                nome=comp_data['nome'],
                defaults={'tipo_nota': comp_data['tipo_nota']}
            )
            
            if created:
                criadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Competência criada: {competencia.nome}')
                )
            else:
                existentes += 1
                self.stdout.write(
                    self.style.WARNING(f'○ Competência já existe: {competencia.nome}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Processo concluído!')
        )
        self.stdout.write(f'  Competências criadas: {criadas}')
        self.stdout.write(f'  Competências já existentes: {existentes}')
        self.stdout.write(f'  Total: {criadas + existentes}')
