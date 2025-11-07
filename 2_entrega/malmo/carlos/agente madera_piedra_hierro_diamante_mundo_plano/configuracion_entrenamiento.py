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

import os
import re

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


# ============================================================================
# FUNCIONES PARA APLICAR CONFIGURACIÓN
# ============================================================================

def aplicar_configuracion():
    """
    Aplica la configuración a los archivos de entrenamiento
    Modifica directamente los valores en los archivos Python
    """
    print("="*70)
    print("🔧 APLICANDO CONFIGURACIÓN AL SISTEMA DE ENTRENAMIENTO")
    print("="*70)
    
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Aplicar a agente_rl.py
    aplicar_a_agente_rl(directorio_actual)
    
    # Aplicar a entorno_malmo.py
    aplicar_a_entorno_malmo(directorio_actual)
    
    # Aplicar a mundo_rl.py
    aplicar_a_mundo_rl(directorio_actual)
    
    print("\n" + "="*70)
    print("✅ CONFIGURACIÓN APLICADA EXITOSAMENTE")
    print("="*70)
    print("\n💡 Ahora puedes ejecutar el entrenamiento:")
    print("   malmoenv && python3 mundo_rl.py 10")
    print()


def aplicar_a_agente_rl(directorio):
    """Aplica configuración a agente_rl.py"""
    archivo = os.path.join(directorio, 'agente_rl.py')
    
    print(f"\n📝 Actualizando {archivo}...")
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Actualizar parámetros de Q-Learning en __init__
    contenido = re.sub(
        r'alpha=[\d.]+',
        f"alpha={PARAMETROS_QLEARNING['alpha']}",
        contenido
    )
    contenido = re.sub(
        r'gamma=[\d.]+',
        f"gamma={PARAMETROS_QLEARNING['gamma']}",
        contenido
    )
    contenido = re.sub(
        r'epsilon=[\d.]+',
        f"epsilon={PARAMETROS_QLEARNING['epsilon_inicial']}",
        contenido
    )
    contenido = re.sub(
        r'epsilon_min=[\d.]+',
        f"epsilon_min={PARAMETROS_QLEARNING['epsilon_min']}",
        contenido
    )
    contenido = re.sub(
        r'epsilon_decay=[\d.]+',
        f"epsilon_decay={PARAMETROS_QLEARNING['epsilon_decay']}",
        contenido
    )
    
    # Actualizar parámetros por fase
    for fase, params in PARAMETROS_POR_FASE.items():
        # Buscar y reemplazar el diccionario de parámetros por fase
        patron = rf'{fase}: {{"alpha": [\d.]+, "epsilon": [\d.]+, "recompensa_mult": [\d.]+ }}'
        reemplazo = f'{fase}: {{"alpha": {params["alpha"]}, "epsilon": {params["epsilon"]}, "recompensa_mult": {params["recompensa_mult"]}}}'
        contenido = re.sub(patron, reemplazo, contenido)
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("   ✓ Parámetros Q-Learning actualizados")
    print("   ✓ Parámetros por fase actualizados")


def aplicar_a_entorno_malmo(directorio):
    """Aplica configuración a entorno_malmo.py"""
    archivo = os.path.join(directorio, 'entorno_malmo.py')
    
    print(f"\n📝 Actualizando {archivo}...")
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Actualizar multiplicadores de fase
    for fase, mult in MULTIPLICADOR_FASE.items():
        patron = rf'{fase}: [\d.]+,\s+# (MADERA|PIEDRA|HIERRO|DIAMANTE)'
        reemplazo = rf'{fase}: {mult},   # \1'
        contenido = re.sub(patron, reemplazo, contenido)
    
    # Actualizar recompensas por material obtenido
    contenido = re.sub(
        r'recompensa = 200\.0 \* diff',
        f'recompensa = {RECOMPENSA_MATERIAL_OBTENIDO["madera"]} * diff',
        contenido
    )
    contenido = re.sub(
        r'recompensa = 250\.0 \* diff',
        f'recompensa = {RECOMPENSA_MATERIAL_OBTENIDO["piedra"]} * diff',
        contenido
    )
    contenido = re.sub(
        r'recompensa = 300\.0 \* diff',
        f'recompensa = {RECOMPENSA_MATERIAL_OBTENIDO["hierro"]} * diff',
        contenido
    )
    contenido = re.sub(
        r'recompensa = 500\.0 \* diff',
        f'recompensa = {RECOMPENSA_MATERIAL_OBTENIDO["diamante"]} * diff',
        contenido
    )
    
    # Actualizar recompensas de ataque correcto
    patron_ataque = r'recompensas_ataque = \{[^}]+\}'
    reemplazo_ataque = f'''recompensas_ataque = {{
                    0: {RECOMPENSA_ATAQUE_CORRECTO[0]},   # Picar madera
                    1: {RECOMPENSA_ATAQUE_CORRECTO[1]},   # Picar piedra
                    2: {RECOMPENSA_ATAQUE_CORRECTO[2]},   # Picar hierro
                    3: {RECOMPENSA_ATAQUE_CORRECTO[3]},  # Picar diamante
                }}'''
    contenido = re.sub(patron_ataque, reemplazo_ataque, contenido)
    
    # Actualizar castigos por herramienta incorrecta
    patron_castigo = r'castigos_herramienta = \{[^}]+\}'
    reemplazo_castigo = f'''castigos_herramienta = {{
                    1: {CASTIGO_HERRAMIENTA_INCORRECTA[1]},  # Piedra sin pico de madera
                    2: {CASTIGO_HERRAMIENTA_INCORRECTA[2]},  # Hierro sin pico de piedra
                    3: {CASTIGO_HERRAMIENTA_INCORRECTA[3]}, # Diamante sin pico de hierro
                }}'''
    contenido = re.sub(patron_castigo, reemplazo_castigo, contenido)
    
    # Actualizar recompensas de proximidad muy cerca
    patron_muy_cerca = r'recompensas_muy_cerca = \{[^}]+\}'
    reemplazo_muy_cerca = f'''recompensas_muy_cerca = {{
                0: {RECOMPENSA_OBJETIVO_MUY_CERCA[0]},  # Madera muy cerca
                1: {RECOMPENSA_OBJETIVO_MUY_CERCA[1]},  # Piedra muy cerca
                2: {RECOMPENSA_OBJETIVO_MUY_CERCA[2]},  # Hierro muy cerca
                3: {RECOMPENSA_OBJETIVO_MUY_CERCA[3]},  # Diamante muy cerca
            }}'''
    contenido = re.sub(patron_muy_cerca, reemplazo_muy_cerca, contenido)
    
    # Actualizar recompensas de proximidad cerca
    patron_cerca = r'recompensas_cerca = \{[^}]+\}'
    reemplazo_cerca = f'''recompensas_cerca = {{
                0: {RECOMPENSA_OBJETIVO_CERCA[0]},
                1: {RECOMPENSA_OBJETIVO_CERCA[1]},
                2: {RECOMPENSA_OBJETIVO_CERCA[2]},
                3: {RECOMPENSA_OBJETIVO_CERCA[3]},
            }}'''
    contenido = re.sub(patron_cerca, reemplazo_cerca, contenido)
    
    # Actualizar castigo sin movimiento
    contenido = re.sub(
        r'recompensa = -[\d.]+  # Castigo (aumentado )?por quedarse atascado',
        f'recompensa = {CASTIGO_SIN_MOVIMIENTO}  # Castigo aumentado por quedarse atascado',
        contenido
    )
    
    # Actualizar pasos para castigo
    contenido = re.sub(
        r'if self\.pasos_sin_movimiento > \d+:',
        f'if self.pasos_sin_movimiento > {PASOS_PARA_CASTIGO_MOVIMIENTO}:',
        contenido
    )
    
    # Actualizar recompensa por pitch útil
    contenido = re.sub(
        r"recompensa = 10\.0  # Recompensa moderada solo cuando es útil",
        f"recompensa = {RECOMPENSA_PITCH_UTIL}  # Recompensa moderada solo cuando es útil",
        contenido
    )
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("   ✓ Multiplicadores de fase actualizados")
    print("   ✓ Recompensas por material actualizadas")
    print("   ✓ Recompensas de ataque actualizadas")
    print("   ✓ Recompensas de proximidad actualizadas")
    print("   ✓ Castigos actualizados")


def aplicar_a_mundo_rl(directorio):
    """Aplica configuración a mundo_rl.py"""
    archivo = os.path.join(directorio, 'mundo_rl.py')
    
    print(f"\n📝 Actualizando {archivo}...")
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Actualizar max_pasos
    contenido = re.sub(
        r'max_pasos = \d+  # [^\n]+',
        f'max_pasos = {EPISODIO_CONFIG["max_pasos"]}  # ~{EPISODIO_CONFIG["max_pasos"]*0.6/60:.1f} minutos con 0.6s por paso',
        contenido
    )
    
    # Actualizar timeout de misión
    contenido = re.sub(
        r'<ServerQuitFromTimeUp timeLimitMs="\d+"/>',
        f'<ServerQuitFromTimeUp timeLimitMs="{EPISODIO_CONFIG["timeout_mision_ms"]}"/>',
        contenido
    )
    
    # Actualizar delay entre comandos
    contenido = re.sub(
        r'time\.sleep\(0\.5\)  # Esperar a que se ejecute el comando',
        f'time.sleep({EPISODIO_CONFIG["delay_entre_comandos"]})  # Esperar a que se ejecute el comando',
        contenido
    )
    
    # Actualizar mostrar progreso cada N pasos
    contenido = re.sub(
        r'# Mostrar progreso cada \d+ pasos\n        if pasos % \d+ == 0:',
        f'# Mostrar progreso cada {EPISODIO_CONFIG["mostrar_progreso_cada"]} pasos\n        if pasos % {EPISODIO_CONFIG["mostrar_progreso_cada"]} == 0:',
        contenido
    )
    
    # Actualizar cantidad de materiales
    contenido = re.sub(
        r"num_madera = random\.randint\(\d+, \d+\)",
        f"num_madera = random.randint{MUNDO_CONFIG['cantidad_madera']}",
        contenido
    )
    contenido = re.sub(
        r"num_piedra = random\.randint\(\d+, \d+\)",
        f"num_piedra = random.randint{MUNDO_CONFIG['cantidad_piedra']}",
        contenido
    )
    contenido = re.sub(
        r"num_hierro = random\.randint\(\d+, \d+\)",
        f"num_hierro = random.randint{MUNDO_CONFIG['cantidad_hierro']}",
        contenido
    )
    contenido = re.sub(
        r"num_diamante = random\.randint\(\d+, \d+\)",
        f"num_diamante = random.randint{MUNDO_CONFIG['cantidad_diamante']}",
        contenido
    )
    
    # Actualizar radio
    contenido = re.sub(
        r'radio = \d+  # \d+x\d+ área total',
        f'radio = {MUNDO_CONFIG["radio"]}  # {MUNDO_CONFIG["radio"]*2}x{MUNDO_CONFIG["radio"]*2} área total',
        contenido
    )
    
    # Actualizar tipo de suelo
    contenido = re.sub(
        r'type="(obsidian|stone)"/>\n    \n    # Muro de obsidiana perimetral',
        f'type="{MUNDO_CONFIG["tipo_suelo"]}"/>\n    \n    # Muro de obsidiana perimetral',
        contenido
    )
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("   ✓ Configuración de episodio actualizada")
    print("   ✓ Configuración de mundo actualizada")
    print("   ✓ Cantidades de materiales actualizadas")


def mostrar_resumen_configuracion():
    """Muestra un resumen de la configuración actual"""
    print("\n" + "="*70)
    print("📊 RESUMEN DE CONFIGURACIÓN ACTUAL")
    print("="*70)
    
    print("\n🧠 PARÁMETROS Q-LEARNING:")
    for key, value in PARAMETROS_QLEARNING.items():
        print(f"   {key:20} = {value}")
    
    print("\n💰 RECOMPENSAS POR MATERIAL:")
    for material, recompensa in RECOMPENSA_MATERIAL_OBTENIDO.items():
        print(f"   {material:20} = +{recompensa}")
    
    print("\n⚔️  RECOMPENSAS POR ATAQUE:")
    for fase, recompensa in RECOMPENSA_ATAQUE_CORRECTO.items():
        fase_nombre = ['MADERA', 'PIEDRA', 'HIERRO', 'DIAMANTE'][fase]
        print(f"   Fase {fase} ({fase_nombre:8}) = +{recompensa}")
    
    print("\n📍 RECOMPENSAS POR PROXIMIDAD (MUY CERCA):")
    for fase, recompensa in RECOMPENSA_OBJETIVO_MUY_CERCA.items():
        fase_nombre = ['MADERA', 'PIEDRA', 'HIERRO', 'DIAMANTE'][fase]
        print(f"   {fase_nombre:20} = +{recompensa}")
    
    print("\n🔢 MULTIPLICADORES POR FASE:")
    for fase, mult in MULTIPLICADOR_FASE.items():
        fase_nombre = ['MADERA', 'PIEDRA', 'HIERRO', 'DIAMANTE'][fase]
        print(f"   Fase {fase} ({fase_nombre:8}) = x{mult}")
    
    print("\n⚙️  CONFIGURACIÓN DE EPISODIO:")
    print(f"   Max pasos           = {EPISODIO_CONFIG['max_pasos']} (~{EPISODIO_CONFIG['max_pasos']*0.6/60:.1f} min)")
    print(f"   Timeout misión      = {EPISODIO_CONFIG['timeout_mision_ms']/1000:.0f}s")
    print(f"   Delay comandos      = {EPISODIO_CONFIG['delay_entre_comandos']}s")
    print(f"   Mostrar progreso    = cada {EPISODIO_CONFIG['mostrar_progreso_cada']} pasos")
    
    print("\n🗺️  CONFIGURACIÓN DE MUNDO:")
    print(f"   Radio (área)        = {MUNDO_CONFIG['radio']} ({MUNDO_CONFIG['radio']*2}x{MUNDO_CONFIG['radio']*2})")
    print(f"   Madera              = {MUNDO_CONFIG['cantidad_madera']}")
    print(f"   Piedra              = {MUNDO_CONFIG['cantidad_piedra']}")
    print(f"   Hierro              = {MUNDO_CONFIG['cantidad_hierro']}")
    print(f"   Diamante            = {MUNDO_CONFIG['cantidad_diamante']}")
    
    print("="*70)


if __name__ == "__main__":
    """
    Ejecuta este archivo para aplicar la configuración:
    
    python3 configuracion_entrenamiento.py
    
    Esto actualizará automáticamente los archivos de entrenamiento
    con los valores definidos arriba.
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--resumen':
        mostrar_resumen_configuracion()
    else:
        mostrar_resumen_configuracion()
        print("\n" + "="*70)
        respuesta = input("¿Deseas aplicar esta configuración? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'y', 'yes']:
            aplicar_configuracion()
        else:
            print("\n❌ Operación cancelada. No se aplicaron cambios.")
            print("💡 Puedes ver solo el resumen con: python3 configuracion_entrenamiento.py --resumen")

