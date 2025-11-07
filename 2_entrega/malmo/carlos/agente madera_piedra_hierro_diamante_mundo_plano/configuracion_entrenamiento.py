"""
Configuración Centralizada de Entrenamiento y Recompensas
Agente Progresivo: Madera → Piedra → Hierro → Diamante

INSTRUCCIONES:
1. Modifica los valores aquí para ajustar el comportamiento del agente
2. No necesitas editar otros archivos
3. Los cambios se aplican automáticamente al importar este módulo

Autor: Sistema de IA
Fecha: Noviembre 2025
"""

# ============================================================================
# PARÁMETROS DE ENTRENAMIENTO Q-LEARNING
# ============================================================================

PARAMETROS_QLEARNING = {
    # Tasa de aprendizaje (qué tanto actualiza con nueva información)
    # Valores típicos: 0.05 - 0.3
    # Más alto = aprende más rápido pero puede ser inestable
    'alpha': 0.1,
    
    # Factor de descuento (importancia de recompensas futuras)
    # Valores típicos: 0.9 - 0.99
    # Más alto = considera más el futuro
    'gamma': 0.95,
    
    # Exploración inicial (% de acciones aleatorias)
    # Valores típicos: 0.3 - 0.5
    # Más alto = más exploración, menos explotación
    'epsilon_inicial': 0.4,
    
    # Exploración mínima (límite inferior)
    # Valores típicos: 0.01 - 0.1
    'epsilon_min': 0.05,
    
    # Decaimiento de epsilon por episodio
    # Valores típicos: 0.99 - 0.999
    # Más alto = decae más lentamente
    'epsilon_decay': 0.995,
}

# Parámetros adaptativos por fase (ajuste fino)
# El agente usa estos valores cuando está en cada fase
PARAMETROS_POR_FASE = {
    0: {  # FASE MADERA
        'alpha': 0.10,           # Aprendizaje estándar
        'epsilon': 0.40,         # Exploración alta (primera fase)
        'recompensa_mult': 1.0   # Sin multiplicador
    },
    1: {  # FASE PIEDRA
        'alpha': 0.12,           # Aprende un poco más rápido
        'epsilon': 0.35,         # Menos exploración
        'recompensa_mult': 1.2   # 20% más recompensas
    },
    2: {  # FASE HIERRO
        'alpha': 0.15,           # Aprendizaje más rápido
        'epsilon': 0.30,         # Menos exploración
        'recompensa_mult': 1.5   # 50% más recompensas
    },
    3: {  # FASE DIAMANTE
        'alpha': 0.20,           # Aprendizaje muy rápido
        'epsilon': 0.25,         # Mínima exploración
        'recompensa_mult': 2.0   # 100% más recompensas (fase final)
    }
}


# ============================================================================
# RECOMPENSAS POR OBTENER MATERIALES EN INVENTARIO
# ============================================================================
# Estas son las RECOMPENSAS MÁS GRANDES - se dan cuando el material
# realmente aparece en el inventario del agente

RECOMPENSA_MATERIAL_OBTENIDO = {
    'madera': 200.0,      # Por cada bloque de madera obtenido
    'piedra': 250.0,      # Por cada bloque de piedra obtenido
    'hierro': 300.0,      # Por cada lingote de hierro obtenido
    'diamante': 500.0,    # Por cada diamante obtenido (¡OBJETIVO FINAL!)
}


# ============================================================================
# RECOMPENSAS POR ATACAR CORRECTAMENTE
# ============================================================================
# Se dan cuando el agente pica el bloque correcto con la herramienta correcta

RECOMPENSA_ATAQUE_CORRECTO = {
    0: 30.0,    # Fase 0: Picar madera
    1: 40.0,    # Fase 1: Picar piedra con pico de madera
    2: 50.0,    # Fase 2: Picar hierro con pico de piedra
    3: 100.0,   # Fase 3: Picar diamante con pico de hierro
}

# Castigos por atacar con herramienta INCORRECTA
# (evita que pierda tiempo picando sin obtener el drop)
CASTIGO_HERRAMIENTA_INCORRECTA = {
    0: -30.0,    # Fase 0: No aplica (madera no requiere herramienta)
    1: -40.0,    # Fase 1: Picar piedra sin pico de madera
    2: -50.0,    # Fase 2: Picar hierro sin pico de piedra
    3: -100.0,   # Fase 3: Picar diamante sin pico de hierro
}

# Castigos por atacar SIN objetivo frente (malgastar acción)
CASTIGO_ATAQUE_VACIO = {
    0: -30.0,
    1: -35.0,
    2: -40.0,
    3: -50.0,
}


# ============================================================================
# RECOMPENSAS POR PROXIMIDAD AL OBJETIVO
# ============================================================================
# Guían al agente hacia el material correcto

# Cuando el objetivo está MUY CERCA (distancia ≤ 2 bloques)
RECOMPENSA_OBJETIVO_MUY_CERCA = {
    0: 20.0,   # Madera muy cerca
    1: 25.0,   # Piedra muy cerca
    2: 30.0,   # Hierro muy cerca
    3: 50.0,   # Diamante muy cerca
}

# Cuando el objetivo está CERCA (distancia ≤ 4 bloques)
RECOMPENSA_OBJETIVO_CERCA = {
    0: 10.0,   # Madera cerca
    1: 12.0,   # Piedra cerca
    2: 15.0,   # Hierro cerca
    3: 25.0,   # Diamante cerca
}


# ============================================================================
# RECOMPENSAS/CASTIGOS POR MOVIMIENTO
# ============================================================================

# Castigo por quedarse atascado sin moverse
CASTIGO_SIN_MOVIMIENTO = -2.0

# Número de pasos sin movimiento antes de castigar
PASOS_PARA_CASTIGO_MOVIMIENTO = 5


# ============================================================================
# RECOMPENSAS POR USAR PITCH (mirar arriba/abajo)
# ============================================================================

# Recompensa SOLO cuando hay objetivo vertical cerca
RECOMPENSA_PITCH_UTIL = 10.0

# Distancia horizontal máxima para considerar pitch útil
DISTANCIA_PITCH_UTIL = 1  # bloques


# ============================================================================
# CASTIGOS POR FASE INCORRECTA
# ============================================================================
# Castiga buscar materiales de fases anteriores

CASTIGO_FASE_INCORRECTA = {
    1: -10.0,   # Fase 1: buscar madera (ya debería tener 3)
    2: -15.0,   # Fase 2: buscar madera/piedra
    3: -20.0,   # Fase 3: buscar madera/piedra/hierro
}


# ============================================================================
# MULTIPLICADORES POR FASE
# ============================================================================
# Multiplican TODAS las recompensas según la fase actual
# Hace que fases avanzadas sean más importantes

MULTIPLICADOR_FASE = {
    0: 1.0,    # MADERA: sin multiplicador
    1: 1.2,    # PIEDRA: +20% todas las recompensas
    2: 1.5,    # HIERRO: +50% todas las recompensas
    3: 2.0,    # DIAMANTE: +100% todas las recompensas
}


# ============================================================================
# CONFIGURACIÓN DEL EPISODIO
# ============================================================================

EPISODIO_CONFIG = {
    # Máximo de pasos por episodio
    # Con 0.6s por paso: 200 pasos ≈ 2 minutos
    'max_pasos': 200,
    
    # Timeout de la misión en milisegundos
    # 120000 ms = 2 minutos
    'timeout_mision_ms': 120000,
    
    # Tiempo de espera entre comandos (segundos)
    'delay_entre_comandos': 0.5,
    
    # Tiempo de espera para observaciones (segundos)
    'delay_observaciones': 0.1,
    
    # Mostrar progreso cada N pasos
    'mostrar_progreso_cada': 50,
}


# ============================================================================
# CONFIGURACIÓN DEL MUNDO
# ============================================================================

MUNDO_CONFIG = {
    # Radio del área (50x50 = radio 25)
    'radio': 25,
    
    # Cantidad de materiales a generar
    'cantidad_madera': (15, 20),    # (mínimo, máximo)
    'cantidad_piedra': (15, 20),
    'cantidad_hierro': (8, 12),
    'cantidad_diamante': (3, 5),
    
    # Altura máxima de torres de bloques
    'altura_maxima_torres': 2,
    
    # Distancia mínima del spawn para materiales raros
    'distancia_min_diamante': 8,
    
    # Tipo de suelo
    'tipo_suelo': 'obsidian',  # No confundir con piedra objetivo
    
    # Tipo de muro perimetral
    'tipo_muro': 'obsidian',
    'altura_muro': (4, 10),  # (y_inicio, y_fin)
}


# ============================================================================
# REQUISITOS POR FASE
# ============================================================================
# Cuántos materiales se necesitan para avanzar a la siguiente fase

REQUISITOS_FASE = {
    0: {'madera': 3},      # Fase 0: necesita 3 madera → Fase 1
    1: {'piedra': 3},      # Fase 1: necesita 3 piedra → Fase 2
    2: {'hierro': 3},      # Fase 2: necesita 3 hierro → Fase 3
    3: {'diamante': 1},    # Fase 3: necesita 1 diamante → ¡OBJETIVO COMPLETADO!
}


# ============================================================================
# GUÍA DE AJUSTE
# ============================================================================
"""
CÓMO AJUSTAR PARA DIFERENTES COMPORTAMIENTOS:

1. AGENTE APRENDE MUY LENTO:
   - Aumentar 'alpha' (ej: 0.15 - 0.3)
   - Aumentar recompensas por proximidad (+50%)
   - Disminuir 'epsilon_decay' (ej: 0.99 para explorar más tiempo)

2. AGENTE NO ENCUENTRA MATERIALES:
   - Aumentar RECOMPENSA_OBJETIVO_CERCA (ej: +50%)
   - Aumentar RECOMPENSA_OBJETIVO_MUY_CERCA (ej: +100%)
   - Aumentar 'epsilon_inicial' (más exploración)

3. AGENTE SE DISTRAE CON MATERIALES INCORRECTOS:
   - Aumentar CASTIGO_FASE_INCORRECTA (más negativo)
   - Disminuir recompensas por proximidad de fases anteriores
   - Aumentar MULTIPLICADOR_FASE para fases avanzadas

4. ENTRENAMIENTO MUY LARGO:
   - Aumentar 'max_pasos' (más tiempo por episodio)
   - Disminuir 'epsilon_decay' (explora menos tiempo)
   - Aumentar 'alpha' (aprende más rápido)

5. AGENTE PICA SIN HERRAMIENTA CORRECTA:
   - Aumentar CASTIGO_HERRAMIENTA_INCORRECTA (más negativo)
   - Aumentar RECOMPENSA_ATAQUE_CORRECTO (mayor diferencia)

6. AGENTE SE QUEDA ATASCADO:
   - Aumentar CASTIGO_SIN_MOVIMIENTO (más negativo)
   - Disminuir PASOS_PARA_CASTIGO_MOVIMIENTO (castiga antes)
   - Aumentar recompensa por proximidad (incentivo para moverse hacia objetivo)
"""
