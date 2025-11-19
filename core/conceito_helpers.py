"""
Funções auxiliares para o sistema de notas conceituais A-B-C-D
"""

def get_conceito_display(nota_valor):
    """
    Retorna a descrição completa de uma nota conceitual
    """
    conceitos = {
        'A': 'A - Atinge plenamente (100-90%)',
        'B': 'B - Atinge satisfatoriamente (89-75%)', 
        'C': 'C - Atinge parcialmente (74-60%)',
        'D': 'D - Ainda não atingiu / Não há evidências para avaliação (59% ou menos)'
    }
    return conceitos.get(nota_valor.upper(), nota_valor) if nota_valor else ''

def get_conceito_range(nota_valor):
    """
    Retorna o range percentual de uma nota conceitual
    """
    ranges = {
        'A': (90, 100),
        'B': (75, 89),
        'C': (60, 74), 
        'D': (0, 59)
    }
    return ranges.get(nota_valor.upper(), None) if nota_valor else None

def get_conceito_por_percentual(percentual):
    """
    Converte um percentual numérico para conceito A-B-C-D
    """
    try:
        pct = float(percentual)
        if pct >= 90:
            return 'A'
        elif pct >= 75:
            return 'B'
        elif pct >= 60:
            return 'C'
        else:
            return 'D'
    except (ValueError, TypeError):
        return None