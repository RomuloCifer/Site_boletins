import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SistemaNotas.settings')
django.setup()

from core.models import Turma, Aluno

# Ler arquivo CSV
csv_path = r'C:\Users\User\Downloads\ALUNOS RB CÓDIGOS .xlsx - Alunos.csv'

criados = 0
pulados = 0
erros = []

print("🚀 Iniciando importação de alunos de Rio Bonito...\n")

try:
    with open(csv_path, 'r', encoding='utf-8') as file:
        linhas = file.readlines()
        
        for idx, linha in enumerate(linhas, 1):
            linha = linha.strip()
            if not linha:
                continue
            
            partes = linha.split(',')
            if len(partes) != 2:
                erros.append(f"❌ Linha {idx}: Formato inválido - '{linha}'")
                continue
            
            nome_completo = partes[0].strip()
            codigo_turma = partes[1].strip()
            
            try:
                # Buscar turma
                try:
                    turma = Turma.objects.get(identificador_turma=codigo_turma)
                except Turma.DoesNotExist:
                    erros.append(f"❌ {nome_completo}: Turma '{codigo_turma}' não encontrada")
                    continue
                
                # Verificar se aluno já existe
                if Aluno.objects.filter(nome_completo=nome_completo, turma=turma).exists():
                    pulados += 1
                    print(f"⏭️  Pulando {nome_completo} ({codigo_turma}) - já existe")
                    continue
                
                # Criar aluno
                aluno = Aluno.objects.create(
                    nome_completo=nome_completo,
                    turma=turma
                )
                
                criados += 1
                if criados % 50 == 0:
                    print(f"✅ {criados} alunos criados...")
                
            except Exception as e:
                erros.append(f"❌ {nome_completo} ({codigo_turma}): {str(e)}")

except FileNotFoundError:
    print(f"❌ Arquivo não encontrado: {csv_path}")
    exit(1)
except Exception as e:
    print(f"❌ Erro ao ler arquivo: {str(e)}")
    exit(1)

print("\n" + "="*60)
print(f"📊 RESUMO DA IMPORTAÇÃO DE ALUNOS - RIO BONITO")
print("="*60)
print(f"✅ Alunos criados: {criados}")
print(f"⏭️  Alunos pulados: {pulados}")
print(f"❌ Erros: {len(erros)}")

if erros:
    print("\n🔴 ERROS ENCONTRADOS:")
    for erro in erros[:20]:
        print(erro)
    if len(erros) > 20:
        print(f"\n... e mais {len(erros) - 20} erros")
