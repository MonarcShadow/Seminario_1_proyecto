"""
Utilidades para el Agente Progresivo
"""

def imprimir_barra_progreso(actual, total, longitud=40):
    """Imprime barra de progreso ASCII"""
    porcentaje = actual / total
    lleno = int(longitud * porcentaje)
    vacio = longitud - lleno
    
    barra = '█' * lleno + '░' * vacio
    print(f"[{barra}] {actual}/{total} ({porcentaje*100:.1f}%)")


def fase_a_emoji(fase):
    """Convierte número de fase a emoji"""
    emojis = {
        0: "🌲",
        1: "🪨",
        2: "⚙️",
        3: "💎"
    }
    return emojis.get(fase, "❓")


def calcular_estadisticas_episodios(estadisticas):
    """
    Calcula estadísticas agregadas de múltiples episodios
    
    Returns:
    --------
    dict: Estadísticas calculadas
    """
    if not estadisticas:
        return {}
    
    total = len(estadisticas)
    exitos = sum(1 for s in estadisticas if s['objetivo_completado'])
    
    recompensa_total = sum(s['recompensa'] for s in estadisticas)
    recompensa_media = recompensa_total / total
    
    pasos_total = sum(s['pasos'] for s in estadisticas)
    pasos_medio = pasos_total / total
    
    # Contar episodios por fase alcanzada
    fases_alcanzadas = {0: 0, 1: 0, 2: 0, 3: 0}
    for s in estadisticas:
        fases_alcanzadas[s['fase_final']] += 1
    
    return {
        'total_episodios': total,
        'exitos': exitos,
        'tasa_exito': exitos / total,
        'recompensa_media': recompensa_media,
        'pasos_medio': pasos_medio,
        'fases_alcanzadas': fases_alcanzadas,
    }


def imprimir_tabla_resultados(estadisticas):
    """Imprime tabla formateada de resultados"""
    print("\n" + "="*80)
    print("📊 TABLA DE RESULTADOS")
    print("="*80)
    print(f"{'EP':<4} {'Pasos':<6} {'Recomp':<8} {'Fase':<10} {'M':<3} {'P':<3} {'H':<3} {'D':<3} {'Éxito'}")
    print("-"*80)
    
    for s in estadisticas[-20:]:  # Últimos 20 episodios
        fase_nombre = {0: "MADERA", 1: "PIEDRA", 2: "HIERRO", 3: "DIAMANTE"}.get(s['fase_final'], "?")
        exito_str = "✓" if s['objetivo_completado'] else "✗"
        
        print(f"{s['episodio']:<4} {s['pasos']:<6} {s['recompensa']:>7.1f} {fase_nombre:<10} "
              f"{s['madera']:<3} {s['piedra']:<3} {s['hierro']:<3} {s['diamante']:<3} {exito_str}")
    
    print("="*80 + "\n")


def convertir_mineral_a_lingote(obs):
    """
    Simula conversión de mineral de hierro a lingote
    (simplificación del proyecto)
    """
    # En el proyecto real, esto se hace automáticamente en el entorno
    pass
