from django.core.management.base import BaseCommand
from core.models import ConfiguracaoSistema
from datetime import date

class Command(BaseCommand):
    help = 'Configura a data limite padrão para entrega de notas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            type=str,
            help='Data limite no formato YYYY-MM-DD (ex: 2025-11-02)',
            default='2025-11-02'
        )

    def handle(self, *args, **options):
        data_str = options['data']
        
        try:
            # Valida a data
            date.fromisoformat(data_str)
            
            # Cria ou atualiza a configuração
            config, created = ConfiguracaoSistema.objects.get_or_create(
                nome='data_limite_notas',
                defaults={
                    'valor': data_str,
                    'descricao': 'Data limite para entrega de todas as notas pelos professores'
                }
            )
            
            if not created:
                config.valor = data_str
                config.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Data limite atualizada para: {data_str}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Data limite configurada para: {data_str}')
                )
                
        except ValueError:
            self.stdout.write(
                self.style.ERROR(f'Data inválida: {data_str}. Use o formato YYYY-MM-DD')
            )