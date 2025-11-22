"""
Script para rodar migrations remotamente no Railway
"""
import os
import django

# Configurar Django para usar o banco PostgreSQL do Railway
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SistemaNotas.settings')
os.environ['DB_ENGINE'] = 'django.db.backends.postgresql'
os.environ['DB_NAME'] = 'railway'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'aeKHhylFpMlFTeiUABFDKczuvYrzuOjb'
os.environ['DB_HOST'] = 'postgres.railway.internal'
os.environ['DB_PORT'] = '5432'
os.environ['USE_HTTPS'] = 'False'  # Para rodar localmente
os.environ['DEBUG'] = 'True'  # Para ver erros

django.setup()

from django.core.management import call_command

print("🔄 Rodando migrations no PostgreSQL do Railway...")
call_command('migrate', '--noinput')
print("✅ Migrations concluídas!")

print("\n🔄 Coletando arquivos estáticos...")
call_command('collectstatic', '--noinput')
print("✅ Arquivos estáticos coletados!")

print("\n🎉 Deploy concluído com sucesso!")
