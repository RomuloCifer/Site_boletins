from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import AuditLog
from core.logging_utils import SimpleLogger

class Command(BaseCommand):
    help = 'Testa o sistema de auditoria'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Testando sistema de auditoria...'))
        
        # Criar um usuário de teste se não existir
        user, created = User.objects.get_or_create(
            username='teste_audit',
            defaults={
                'email': 'teste@exemplo.com',
                'is_staff': False,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'✅ Usuário de teste criado: {user.username}')
        else:
            self.stdout.write(f'ℹ️  Usando usuário existente: {user.username}')
        
        # Testar diferentes tipos de log
        try:
            # Log de ação simples
            SimpleLogger.log_action(
                user=user,
                action='TEST',
                description='Teste do sistema de auditoria',
                severity='LOW'
            )
            self.stdout.write('✅ Log de ação criado')
            
            # Log de login
            SimpleLogger.log_login(user, success=True, ip_address='127.0.0.1', user_agent='Test Browser')
            self.stdout.write('✅ Log de login criado')
            
            # Log de importação
            SimpleLogger.log_import(user, 'ALUNOS', 5, 0)
            self.stdout.write('✅ Log de importação criado')
            
            # Log de erro
            SimpleLogger.log_error(user, 'Erro de teste para auditoria')
            self.stdout.write('✅ Log de erro criado')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao criar logs: {e}'))
            return
        
        # Verificar se os logs foram criados
        total_logs = AuditLog.objects.filter(usuario=user).count()
        self.stdout.write(f'📊 Total de logs criados para o usuário: {total_logs}')
        
        # Exibir os últimos logs
        ultimos_logs = AuditLog.objects.filter(usuario=user).order_by('-timestamp')[:5]
        
        self.stdout.write('\n📋 Últimos logs de auditoria:')
        for log in ultimos_logs:
            self.stdout.write(f'  • {log.timestamp.strftime("%d/%m/%Y %H:%M")} - {log.acao} - {log.descricao[:50]}...')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Teste de auditoria concluído com sucesso!'))
        self.stdout.write('💡 Você pode visualizar os logs no admin em: http://127.0.0.1:8000/admin/core/auditlog/')