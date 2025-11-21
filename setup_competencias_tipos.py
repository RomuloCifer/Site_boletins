"""
Script para criar competências e tipos de turma automaticamente
Execute: python manage.py shell < setup_competencias_tipos.py
Ou via Railway: railway run python manage.py shell < setup_competencias_tipos.py
"""

import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SistemaNotas.settings')
django.setup()

from core.models import Competencia, TipoTurma

def setup_competencias_e_tipos():
    """
    Cria todas as competências e tipos de turma necessários para o sistema
    """
    print("🚀 Iniciando criação de competências e tipos de turma...")
    
    # Definir todas as competências únicas usadas no sistema
    todas_competencias = [
        # Para Adolescentes/Adultos e Material Antigo
        'Produção Oral',
        'Produção Escrita',
        'Avaliações de Progresso',
        'Compreensão Oral',
        'Compreensão Escrita',
        'Writing Bit 01',
        'Writing Bit 02',
        'Checkpoints',
        # Para Lion Stars e Junior
        'Comunicação Oral',
        'Comunicação Escrita',
        'Compreensão de Leitura',
        'Interesse pela Aprendizagem',
        'Colaboração',
        'Engajamento',
    ]
    
    # Criar competências
    print("\n📝 Criando competências...")
    competencias_criadas = {}
    for nome_comp in todas_competencias:
        comp, created = Competencia.objects.get_or_create(
            nome=nome_comp,
            defaults={'descricao': f'Avaliação de {nome_comp}'}
        )
        competencias_criadas[nome_comp] = comp
        if created:
            print(f"  ✅ Criada: {nome_comp}")
        else:
            print(f"  ⏭️  Já existe: {nome_comp}")
    
    # Mapear tipos de turma com suas competências
    tipos_config = {
        'Adolescentes - Adultos': {
            'boletim_tipo': 'adolescentes_adultos',
            'competencias': [
                'Produção Oral',
                'Produção Escrita',
                'Avaliações de Progresso',
            ]
        },
        'Material Antigo': {
            'boletim_tipo': 'material_antigo',
            'competencias': [
                'Produção Oral',
                'Produção Escrita',
                'Compreensão Oral',
                'Compreensão Escrita',
                'Writing Bit 01',
                'Writing Bit 02',
                'Checkpoints',
            ]
        },
        'Lion Stars': {
            'boletim_tipo': 'lion_stars',
            'competencias': [
                'Comunicação Oral',
                'Compreensão Oral',
                'Interesse pela Aprendizagem',
                'Colaboração',
                'Engajamento',
            ]
        },
        'Junior': {
            'boletim_tipo': 'junior',
            'competencias': [
                'Comunicação Oral',
                'Compreensão Oral',
                'Comunicação Escrita',
                'Compreensão de Leitura',
                'Interesse pela Aprendizagem',
                'Colaboração',
                'Engajamento',
            ]
        }
    }
    
    # Criar tipos de turma e associar competências
    print("\n📚 Criando tipos de turma e associando competências...")
    for nome_tipo, config in tipos_config.items():
        tipo_turma, created = TipoTurma.objects.get_or_create(
            nome=nome_tipo,
            defaults={
                'boletim_tipo': config['boletim_tipo'],
                'descricao': f'Tipo de turma para {nome_tipo}'
            }
        )
        
        if created:
            print(f"\n  ✅ Criado tipo: {nome_tipo}")
        else:
            print(f"\n  ⏭️  Já existe tipo: {nome_tipo}")
            # Atualizar boletim_tipo se necessário
            if tipo_turma.boletim_tipo != config['boletim_tipo']:
                tipo_turma.boletim_tipo = config['boletim_tipo']
                tipo_turma.save()
                print(f"     🔄 Atualizado boletim_tipo para: {config['boletim_tipo']}")
        
        # Associar competências
        competencias_tipo = [competencias_criadas[nome] for nome in config['competencias']]
        tipo_turma.competencias.set(competencias_tipo)
        print(f"     📌 Competências associadas: {len(competencias_tipo)}")
        for comp_nome in config['competencias']:
            print(f"        • {comp_nome}")
    
    print("\n" + "="*60)
    print("🎉 CONCLUÍDO! Competências e tipos de turma configurados!")
    print("="*60)
    
    # Resumo
    print("\n📊 RESUMO:")
    print(f"   • Total de competências: {Competencia.objects.count()}")
    print(f"   • Total de tipos de turma: {TipoTurma.objects.count()}")
    print("\n✅ Agora você pode criar turmas escolhendo o tipo!")

if __name__ == '__main__':
    try:
        setup_competencias_e_tipos()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
