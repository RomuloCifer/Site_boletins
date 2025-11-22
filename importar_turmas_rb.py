import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SistemaNotas.settings')
django.setup()

from core.models import Turma, TipoTurma, Professor
from django.contrib.auth.models import User

# Mapeamento de professores (nome no CSV -> username)
professor_map = {
    'ALANA': 'alanarb',
    'TAYNÁ': 'taynarb',
    'ADRIANO': 'adrianorb',
    'WENDEL': 'wendelrb',
    'MATHEUS': 'matheusrb',
    'RAFAEL': 'rafaelrb',
    'ANA LUIZA': 'analuizarb',
    'BRUNA': 'brunarb',
    'DIANNA': 'diannarb',
    'EDUARDA': 'eduardarb',
}

# Mapeamento de tipos de turma (prefixo -> TipoTurma, boletim_tipo)
tipo_turma_map = {
    'BA5': ('Basic 5', 'material_antigo'),
    'B5': ('Basic 5', 'material_antigo'),
    'BA6': ('Basic 6', 'material_antigo'),
    'B6': ('Basic 6', 'material_antigo'),
    'EX1': ('Express Pack 1', 'adolescentes_adultos'),
    'EX2': ('Express Pack 2', 'adolescentes_adultos'),
    'EX3': ('Express Pack 3', 'adolescentes_adultos'),
    'CX4': ('Cultura Express 4', 'material_antigo'),
    'IT1': ('Inter Teens 1', 'adolescentes_adultos'),
    'IT2': ('Inter Teens 2', 'adolescentes_adultos'),
    'JA': ('Junior A', 'junior'),
    'JB': ('Junior B', 'junior'),
    'JC': ('Junior C', 'junior'),
    'JD': ('Junior D', 'junior'),
    'LS1': ('Lion Stars Blue 1', 'lion_stars'),
    'LS2': ('Lion Stars Blue 2', 'lion_stars'),
    'LB2': ('Lion Stars Blue 2', 'lion_stars'),
    'MA1': ('MAC 1', 'adolescentes_adultos'),
    'MA2': ('MAC 2', 'adolescentes_adultos'),
    'PA1': ('Cultura Express 5', 'material_antigo'),
    'PA2': ('Cultura Express 6', 'material_antigo'),
    'LE1': ('Teen League 1', 'adolescentes_adultos'),
    'LE2': ('Teen League 2', 'adolescentes_adultos'),
    'LE3': ('Teen League 3', 'adolescentes_adultos'),
    'LE4': ('Teen League 4', 'adolescentes_adultos'),
    'UI1': ('Upper Intermediate 1', 'adolescentes_adultos'),
    'UI3': ('Upper Intermediate 3', 'adolescentes_adultos'),
    # VIPs - extrair tipo base
    'VIPEX1': ('Express Pack 1', 'adolescentes_adultos'),
    'VIPEX3': ('Express Pack 3', 'adolescentes_adultos'),
    'VIPIT1': ('Inter Teens 1', 'adolescentes_adultos'),
    'VIPIT2': ('Inter Teens 2', 'adolescentes_adultos'),
    'VIPMA1': ('MAC 1', 'adolescentes_adultos'),
    'VIPMA2': ('MAC 2', 'adolescentes_adultos'),
    'VIPPA3': ('New Plus Adult 3', 'adolescentes_adultos'),
    'VIPLE1': ('Teen League 1', 'adolescentes_adultos'),
    'VIPLE2': ('Teen League 2', 'adolescentes_adultos'),
    'VIPLE3': ('Teen League 3', 'adolescentes_adultos'),
    'VIPB6': ('Basic 6', 'material_antigo'),
    'VIPCE4': ('Cultura Express 4', 'material_antigo'),
    'VIPUP': ('Upper Intermediate 1', 'adolescentes_adultos'),
    'VIPUP1': ('Upper Intermediate 1', 'adolescentes_adultos'),
    'VIPUP2': ('Upper Intermediate 1', 'adolescentes_adultos'),
}

def extrair_tipo_base(codigo_turma):
    """Extrai o tipo base do código da turma"""
    codigo_upper = codigo_turma.upper()
    
    # Ignorar Lion Cubs e FUN MEE
    if codigo_upper.startswith('LC') or codigo_upper.startswith('MEE'):
        return None
    
    # Tentar matches mais específicos primeiro (VIPs e códigos de 4+ letras)
    for prefixo in ['VIPCE4', 'VIPEX3', 'VIPEX1', 'VIPIT2', 'VIPIT1', 'VIPMA2', 'VIPMA1', 
                    'VIPPA3', 'VIPLE3', 'VIPLE2', 'VIPLE1', 'VIPUP2', 'VIPUP1', 'VIPUP', 'VIPB6']:
        if codigo_upper.startswith(prefixo):
            return prefixo
    
    # Códigos de 3 letras
    for prefixo in ['CX4', 'BA5', 'BA6', 'EX1', 'EX2', 'EX3', 'IT1', 'IT2', 
                    'LS1', 'LS2', 'LB2', 'MA1', 'MA2', 'PA1', 'PA2', 
                    'LE1', 'LE2', 'LE3', 'LE4', 'UI1', 'UI3']:
        if codigo_upper.startswith(prefixo):
            return prefixo
    
    # Códigos de 2 letras
    for prefixo in ['JA', 'JB', 'JC', 'JD', 'B5', 'B6']:
        if codigo_upper.startswith(prefixo):
            return prefixo
    
    # LEAG/LEA sem número
    if codigo_upper.startswith('LEA') and not any(codigo_upper.startswith(f'LEA{i}') for i in range(10)):
        # LEAMW09BRU = LEAG3
        if 'MW09' in codigo_upper or 'TT09' in codigo_upper:
            return 'LE3'
    
    return None

# Ler arquivo CSV
csv_path = r'C:\Users\User\Desktop\ALUNOS RB CÓDIGOS .xlsx - Turmas.csv'

criadas = 0
puladas = 0
erros = []

print("🚀 Iniciando importação de turmas de Rio Bonito...\n")

try:
    with open(csv_path, 'r', encoding='utf-8') as file:
        linhas = file.readlines()
        
        # Remover duplicatas (arquivo tem linhas repetidas)
        turmas_processadas = set()
        
        for idx, linha in enumerate(linhas, 1):
            linha = linha.strip()
            if not linha:
                continue
            
            partes = linha.split(',')
            if len(partes) < 3:
                if len(partes) == 2:
                    # Linha sem professor, ignorar
                    continue
                erros.append(f"❌ Linha {idx}: Formato inválido - '{linha}'")
                continue
            
            codigo = partes[0].strip()
            nome_turma = partes[1].strip()
            prof_nome = partes[2].strip()
            
            # Pular duplicatas
            if codigo in turmas_processadas:
                continue
            
            turmas_processadas.add(codigo)
            
            # Ignorar Lion Cubs e FUN MEE
            if codigo.upper().startswith('LC') or codigo.upper().startswith('MEE'):
                puladas += 1
                print(f"⏭️  Pulando {codigo} - Lion Cubs/FUN MEE (não suportado)")
                continue
            
            # Ignorar se não tem professor
            if not prof_nome:
                puladas += 1
                print(f"⏭️  Pulando {codigo} - Sem professor")
                continue
            
            try:
                # Verificar se turma já existe
                if Turma.objects.filter(identificador_turma=codigo).exists():
                    puladas += 1
                    print(f"⏭️  Pulando {codigo} - já existe")
                    continue
                
                # Buscar tipo base
                tipo_base = extrair_tipo_base(codigo)
                if not tipo_base:
                    erros.append(f"❌ {codigo}: Tipo de turma não identificado")
                    continue
                
                # Buscar TipoTurma
                if tipo_base not in tipo_turma_map:
                    erros.append(f"❌ {codigo}: Tipo '{tipo_base}' não mapeado")
                    continue
                
                tipo_turma_nome, boletim_tipo = tipo_turma_map[tipo_base]
                
                try:
                    tipo_turma = TipoTurma.objects.get(nome=tipo_turma_nome)
                except TipoTurma.DoesNotExist:
                    erros.append(f"❌ {codigo}: TipoTurma '{tipo_turma_nome}' não existe no banco")
                    continue
                
                # Buscar professor
                username = professor_map.get(prof_nome.upper())
                if not username:
                    erros.append(f"❌ {codigo}: Professor '{prof_nome}' não mapeado")
                    continue
                
                try:
                    user = User.objects.get(username=username)
                    professor = Professor.objects.get(user=user)
                except (User.DoesNotExist, Professor.DoesNotExist):
                    erros.append(f"❌ {codigo}: Professor '{username}' não existe no banco")
                    continue
                
                # Criar turma
                turma = Turma.objects.create(
                    identificador_turma=codigo,
                    tipo_turma=tipo_turma,
                    professor_responsavel=professor,
                    boletim_tipo=boletim_tipo
                )
                
                criadas += 1
                print(f"✅ Criada: {codigo} - {turma.nome} ({tipo_turma_nome}) - Prof: {prof_nome}")
                
            except Exception as e:
                erros.append(f"❌ {codigo}: Erro ao criar - {str(e)}")

except FileNotFoundError:
    print(f"❌ Arquivo não encontrado: {csv_path}")
    exit(1)
except Exception as e:
    print(f"❌ Erro ao ler arquivo: {str(e)}")
    exit(1)

print("\n" + "="*60)
print(f"📊 RESUMO DA IMPORTAÇÃO DE TURMAS - RIO BONITO")
print("="*60)
print(f"✅ Turmas criadas: {criadas}")
print(f"⏭️  Turmas puladas: {puladas}")
print(f"❌ Erros: {len(erros)}")

if erros:
    print("\n🔴 ERROS ENCONTRADOS:")
    for erro in erros[:30]:
        print(erro)
    if len(erros) > 30:
        print(f"\n... e mais {len(erros) - 30} erros")
