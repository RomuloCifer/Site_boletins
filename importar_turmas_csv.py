import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SistemaNotas.settings')
django.setup()

from core.models import Turma, TipoTurma, Professor
from django.contrib.auth.models import User

# Turmas já existentes - vamos pular
turmas_existentes = [
    'EP2TT14ALES',
    'JUNBTT18ALE', 
    'MAC1TTALES',
    'MAC2TT19ALE',
    'PA3SEX14ALE'
]

# Mapeamento de professores (nome no CSV -> username)
professor_map = {
    'ANNA CLARA': 'annaclara',
    'ROBERTA': 'robertanf',
    'NATALIA': 'natalianf',
    'GUILHERME': 'guilhermenf',
    'JOSI': 'josinf',
    'JOSIANNE': 'josinf',
    'LIDIA': 'lidia',
    'THYENE': 'thyenenf',
    'ALESSANDRA': 'alessandranf',
    'DORA': 'doranf',
    'JULLIANA': 'juliananf',
    'ROMULO': 'romulonf',
    'CLAUDIA': 'claudianf',
    'RODRIGO': 'rodrigonf',
    'BARBARA': 'barbaranf',
    'ALINE': 'alinenf',
    'MARIA': 'marianf',
}

# Mapeamento de tipos de turma (padrão do nome -> TipoTurma)
tipo_turma_map = {
    'BASIC 5': ('Basic 5', 'material_antigo'),
    'BASIC 6': ('Basic 6', 'material_antigo'),
    'EXP PACK 1': ('Express Pack 1', 'adolescentes_adultos'),
    'EXPRESS PACK 1': ('Express Pack 1', 'adolescentes_adultos'),
    'EXP PACK 2': ('Express Pack 2', 'adolescentes_adultos'),
    'EXPRESS PACK 2': ('Express Pack 2', 'adolescentes_adultos'),
    'EXP PACK 3': ('Express Pack 3', 'adolescentes_adultos'),
    'EXPRESS PACK 3': ('Express Pack 3', 'adolescentes_adultos'),
    'CULT EXP 4': ('Cultura Express 4', 'material_antigo'),
    'CEXP4': ('Cultura Express 4', 'material_antigo'),
    'INTER TEENS 1': ('Inter Teens 1', 'adolescentes_adultos'),
    'INTER TEENS 2': ('Inter Teens 2', 'adolescentes_adultos'),
    'INTER TEENS 3': ('Inter Teens 3', 'adolescentes_adultos'),
    'JUNIOR A': ('Junior A', 'junior'),
    'JUNIOR B': ('Junior B', 'junior'),
    'JUNIOR C': ('Junior C', 'junior'),
    'JUNIOR D': ('Junior D', 'junior'),
    'LION STARS BLUE 1': ('Lion Stars Blue 1', 'lion_stars'),
    'LION STARS BLUE 2': ('Lion Stars Blue 2', 'lion_stars'),
    'MAC 1': ('MAC 1', 'adolescentes_adultos'),
    'MAC 2': ('MAC 2', 'adolescentes_adultos'),
    'PLUS ADULT 1': ('Cultura Express 5', 'material_antigo'),
    'PLUS ADULT 2': ('Cultura Express 6', 'material_antigo'),
    'PLUS ADULT 3': ('New Plus Adult 3', 'adolescentes_adultos'),
    'TEEN LEAGUE 1': ('Teen League 1', 'adolescentes_adultos'),
    'TEEN LEAGUE 2': ('Teen League 2', 'adolescentes_adultos'),
    'TEEN LEAGUE 3': ('Teen League 3', 'adolescentes_adultos'),
    'TEEN LEAGUE 4': ('Teen League 4', 'adolescentes_adultos'),
    'UPPER INT 1': ('Upper Intermediate 1', 'adolescentes_adultos'),
    'UPPER INT 3': ('Upper Intermediate 3', 'adolescentes_adultos'),
}

# Dados das turmas do CSV
turmas_data = [
    ('B5MW14ANNA', 'BASIC 5 SEG QUA 14H', 'ANNA CLARA'),
    ('B5TT14ROB', 'BASIC 5 TER QUI14H', 'ROBERTA'),
    ('B5THU14NAT', 'BASIC 5 QUI15H', 'NATALIA'),
    ('B6MW14ROB', 'BASIC 6 SEG QUA 14', 'ROBERTA'),
    ('B6MW14GUI', 'BASIC 6 SEG QUA 14', 'GUILHERME'),
    ('B6TT1815JOSI', 'BASIC 6 TER QUI 18H15', 'JOSI'),
    ('EP3SEG08LIDIA', 'EXP PACK 3 SEG 08H29', 'LIDIA'),
    ('EP1MW19THYEN', 'EXP PACK 1 SEG QUA 19H30', 'THYENE'),
    ('EP2MW19GUI', 'EXP PACK 2 SEG QUA 19H30', 'GUILHERME'),
    # EP2TT14ALES já existe - pulando
    ('CEXP4TT15GUI', 'CULT EXP 4 TER QUI 15H30', 'GUILHERME'),
    ('EP1SEX14JULLI', 'EXP PACK 1 SEX 14H', 'JULLIANA'),
    ('CEXP4SEXDORA', 'CEXP4 SEX 14H', 'DORA'),
    ('CEXP4TT19ROM', 'CEXP4 TER QUI 19H30', 'ROMULO'),
    ('IT1TT14DORA', 'INTER TEENS 1 TER QUI 14H', 'DORA'),
    ('IT2TT14CLAU', 'INTER TEENS 2 TER QUI 14H', 'CLAUDIA'),
    ('IT3TTRODRI', 'INTER TEENS 3 TER QUI 15H30', 'RODRIGO'),
    ('IT2TT18ROB', 'INTER TEENS 2 TER QUI 18H15', 'ROBERTA'),
    ('IT2SEX13BARB', 'INTER TEENS 2 SEX 13H40', 'BARBARA'),
    ('JUNDTT18ROM', 'JUNIOR D TER QUI 18H10', 'ROMULO'),
    ('JUNAMW18LID', 'JUNIOR A SEG QUA 18H10', 'LIDIA'),
    ('JUNATT9THY', 'JUNIOR A TER QUI 09H', 'THYENE'),
    ('JUNBMWANNA', 'JUNIOR B SEG QUA 10H20', 'ANNA CLARA'),
    ('JUNBMWALIN', 'JUNIOR B SEG QUA 18H15 ALINE', 'ALINE'),
    # JUNBTT18ALE já existe - pulando
    ('JUNBTT18ALE', 'JUNIOR B YTER QUI 18H10', 'ALESSANDRA'),
    ('JUNCMW18JULL', 'JUNIOR C SEG QUA 18H15', 'JULLIANA'),
    ('JUNDTT09ANNA', 'JUNIOR D TER QUI 09H', 'ANNA CLARA'),
    ('JUNDSEX9THY', 'JUNIOR D SEX 09H', 'THYENE'),
    # Lion Cubs - ignorar
    ('LSB2MW9ANNA', 'LION STARS BLUE 2 SEG QUA 09H', 'ANNA CLARA'),
    ('LSB2MW18ROM', 'LION STARS BLUE 1 SEG QUA 18H10', 'ROMULO'),
    ('LSB2MW18THY', 'LION STARS BLUE 2 SEG QUA 18H10', 'THYENE'),
    ('LSB2TT09JULL', 'LION STARS BLUE 1 TER QUI 09H', 'JULLIANA'),
    ('LSB2TT18THYE', 'LION STARS BLUE 2 TER QUI 18H', 'THYENE'),
    # MAC1TTALES já existe - pulando
    ('MAC2TTJOSI', 'MAC 2 TER QUI 15H30', 'JOSIANNE'),
    # MAC2TT19ALE já existe - pulando
    ('MAC2MW14JOSI', 'MAC 2 SEG QUA 14H', 'JOSIANNE'),
    ('PA1TT15CLAU', 'PLUS ADULT 1 TER QUI 15H30', 'CLAUDIA'),
    # PA3SEX14ALE já existe - pulando
    ('PA1SEX13JOSI', 'PLUS ADULT 1 SEX 13H30', 'JOSIANNE'),
    ('PA1SABCLAU', 'PLUS ADULT 1 SÁB 08H', 'CLAUDIA'),
    ('PA2SAB08RODRI', 'PLUS ADULT 2 SÁB 08H', 'RODRIGO'),
    ('PA2MW15MARIA', 'PLUS ADULT 2 SEG QUA 15H30', 'MARIA'),
    ('TL4MW14LIDIA', 'TEEN LEAGUE 4 SEG QUA 14H', 'LIDIA'),
    ('TL2MW15LIDIA', 'TEEN LEAGUE 2 SEG QUA 15H30', 'LIDIA'),
    ('TL1MW18CLAU', 'TEEN LEAGUE 1 SEG QUA 18H15', 'CLAUDIA'),
    ('TL3MW18GUI', 'TEEN LEAGUE 3 SEG QUA 18H15', 'GUILHERME'),
    ('TL2TT09MARIA', 'TEEN LEAGUE 2 TER QUI 09H20', 'MARIA'),
    ('TL3TT09JOSI', 'TEEN LEAGUE 3 TER QUI 09H20', 'JOSIANNE'),
    ('TL1SEG15JOSI', 'TEEN LEAGUE 1 SEG 15H30', 'JOSIANNE'),
    ('TL3TT15DORA', 'TEEN LEAGUE 3 TER QUI 15H30', 'DORA'),
    ('TL3TT18DORA', 'TEEN LEAGUE 3 TER QUI 18H', 'DORA'),
    ('TL4TT18GUI', 'TEEN LEAGUE 4 TER QUI 18H15', 'GUILHERME'),
    ('TL2TT18CLAU', 'TEEN LEAGUE 2 TER QUI 18H15', 'CLAUDIA'),
    ('UPP1TT14RODR', 'UPPER INT 1 TER QUI 14H', 'RODRIGO'),
    ('UPP3TT14GUI', 'UPPER INT 3 TER QUI 14H', 'GUILHERME'),
    ('UPP1TT1930GUI', 'UPPER INT 1 TER QUI 19H30', 'GUILHERME'),
    ('UPP1SEX14ROB', 'UPPER INT 1 SEX 14H15', 'ROBERTA'),
    ('UPP1MW14RODR', 'UPPER INT 1 SEG QUA 14H', 'RODRIGO'),
    ('UPP1MW18JOSI', 'UPPER INT 1 SEG QUA 18H10', 'JOSIANNE'),
    ('UPP3MW17ALIN', 'UPPER INT 3 SEG QUA 17H', 'ALINE'),
    ('EP2SEX16JOSI', 'EXPRESS PACK 2 SEXTA 16H15', 'JOSIANNE'),
    ('EP3THU16', 'EXPRESS PACK 3 QUINTA 16H', 'JULLIANA'),
    ('IT1TT10JULLI', 'VIP DUPLO INTER TEENS TER QUI 10H20', 'JULLIANA'),
    ('MAC1THU19THY', 'VIP MAC 1 QUI 19H30', 'THYENE'),
    ('MAC2TUE8THY', 'VIP DUPLO MAC 2 TER 08H', 'THYENE'),
    ('PA1WF10JOSI', 'VIP PLUS ADULT 1 QUA 8H SEX 10H', 'JOSI'),
    ('PA1MON17THYE', 'VIP PLUS ADULT 1 SEG 17H', 'THYENE'),
    ('PA3TUE20THYE', 'VIP PLUS ADULT 3 TER 20H', 'THYENE'),
    ('PA4THU19JULLI', 'VIP PLUS ADULT 4 QUI 19H', 'JULLIANA'),
    ('UPP1WED17JOSI', 'VIP UPPER INT 1 QUA 17H', 'JOSIANNE'),
    ('UPP3TUE17THY', 'VIP UPPER INT 3 TER 17H', 'THYENE'),
    ('UPP3WED17THY', 'VIP UPPER INT 3 QUA 17H', 'THYENE'),
]

def extrair_tipo_base(nome_turma):
    """Extrai o tipo base do nome da turma"""
    nome_upper = nome_turma.upper()
    
    # Casos especiais
    if 'LION CUBS' in nome_upper:
        return None  # Ignorar Lion Cubs
    if 'LION STARS BLUE 1' in nome_upper:
        return 'LION STARS BLUE 1'
    if 'LION STARS BLUE 2' in nome_upper:
        return 'LION STARS BLUE 2'
    if 'VIP' in nome_upper and 'INTER TEENS' in nome_upper:
        return 'INTER TEENS 1'
    if 'VIP' in nome_upper and 'MAC' in nome_upper:
        if 'MAC 2' in nome_upper or 'MAC2' in nome_upper:
            return 'MAC 2'
        return 'MAC 1'
    if 'VIP' in nome_upper and 'PLUS ADULT' in nome_upper:
        if 'PLUS ADULT 3' in nome_upper or 'PA3' in nome_upper:
            return 'PLUS ADULT 3'
        if 'PLUS ADULT 4' in nome_upper or 'PA4' in nome_upper:
            # PA4 não existe nos tipos, vamos usar PA3
            return 'PLUS ADULT 3'
        if 'PLUS ADULT 2' in nome_upper or 'PA2' in nome_upper:
            return 'PLUS ADULT 2'
        return 'PLUS ADULT 1'
    if 'VIP' in nome_upper and 'UPPER' in nome_upper:
        if 'UPPER INT 3' in nome_upper or 'UPP3' in nome_upper:
            return 'UPPER INT 3'
        return 'UPPER INT 1'
    if 'CEXP4' in nome_upper or 'CULT EXP 4' in nome_upper:
        return 'CULT EXP 4'
    if 'BASIC 5' in nome_upper:
        return 'BASIC 5'
    if 'BASIC 6' in nome_upper:
        return 'BASIC 6'
    if 'EXPRESS PACK 1' in nome_upper or 'EXP PACK 1' in nome_upper:
        return 'EXP PACK 1'
    if 'EXPRESS PACK 2' in nome_upper or 'EXP PACK 2' in nome_upper:
        return 'EXP PACK 2'
    if 'EXPRESS PACK 3' in nome_upper or 'EXP PACK 3' in nome_upper:
        return 'EXP PACK 3'
    if 'INTER TEENS 1' in nome_upper:
        return 'INTER TEENS 1'
    if 'INTER TEENS 2' in nome_upper:
        return 'INTER TEENS 2'
    if 'INTER TEENS 3' in nome_upper:
        return 'INTER TEENS 3'
    if 'JUNIOR A' in nome_upper:
        return 'JUNIOR A'
    if 'JUNIOR B' in nome_upper:
        return 'JUNIOR B'
    if 'JUNIOR C' in nome_upper:
        return 'JUNIOR C'
    if 'JUNIOR D' in nome_upper:
        return 'JUNIOR D'
    if 'MAC 1' in nome_upper:
        return 'MAC 1'
    if 'MAC 2' in nome_upper:
        return 'MAC 2'
    if 'PLUS ADULT 1' in nome_upper:
        return 'PLUS ADULT 1'
    if 'PLUS ADULT 2' in nome_upper:
        return 'PLUS ADULT 2'
    if 'PLUS ADULT 3' in nome_upper:
        return 'PLUS ADULT 3'
    if 'TEEN LEAGUE 1' in nome_upper:
        return 'TEEN LEAGUE 1'
    if 'TEEN LEAGUE 2' in nome_upper:
        return 'TEEN LEAGUE 2'
    if 'TEEN LEAGUE 3' in nome_upper:
        return 'TEEN LEAGUE 3'
    if 'TEEN LEAGUE 4' in nome_upper:
        return 'TEEN LEAGUE 4'
    if 'UPPER INT 1' in nome_upper:
        return 'UPPER INT 1'
    if 'UPPER INT 3' in nome_upper:
        return 'UPPER INT 3'
    
    return None

# Importar turmas
criadas = 0
puladas = 0
erros = []

for codigo, nome, prof_nome in turmas_data:
    # Pular se já existe
    if codigo in turmas_existentes:
        puladas += 1
        print(f"⏭️  Pulando {codigo} - já existe")
        continue
    
    # Pular Lion Cubs
    if 'LION CUBS' in nome.upper():
        puladas += 1
        print(f"⏭️  Pulando {codigo} - Lion Cubs (não suportado)")
        continue
    
    try:
        # Buscar tipo base da turma
        tipo_base = extrair_tipo_base(nome)
        if not tipo_base:
            erros.append(f"❌ {codigo}: Tipo de turma não identificado em '{nome}'")
            continue
        
        # Buscar tipo de turma e boletim
        if tipo_base not in tipo_turma_map:
            erros.append(f"❌ {codigo}: Tipo '{tipo_base}' não mapeado")
            continue
        
        tipo_turma_nome, boletim_tipo = tipo_turma_map[tipo_base]
        
        # Buscar TipoTurma no banco
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

print("\n" + "="*60)
print(f"📊 RESUMO DA IMPORTAÇÃO")
print("="*60)
print(f"✅ Turmas criadas: {criadas}")
print(f"⏭️  Turmas puladas: {puladas}")
print(f"❌ Erros: {len(erros)}")

if erros:
    print("\n🔴 ERROS ENCONTRADOS:")
    for erro in erros:
        print(erro)
