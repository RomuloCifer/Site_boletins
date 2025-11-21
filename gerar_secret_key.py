"""
Script para gerar SECRET_KEY segura para Django
Use este valor no arquivo .env ou nas variáveis do Railway
"""

import secrets

print("=" * 60)
print("🔐 GERANDO SECRET_KEY PARA PRODUÇÃO")
print("=" * 60)
print()
print("Copie e cole esta chave no seu .env ou Railway:")
print()
print(secrets.token_urlsafe(50))
print()
print("=" * 60)
print("⚠️  NUNCA compartilhe esta chave!")
print("⚠️  Use uma chave diferente para cada ambiente!")
print("=" * 60)
