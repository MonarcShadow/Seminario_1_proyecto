"""
Script de prueba para verificar que todos los módulos funcionan correctamente
"""

import sys

print("="*60)
print("🧪 VERIFICACIÓN DE MÓDULOS - AGENTE MADERA")
print("="*60)

# 1. Verificar imports básicos
print("\n1. Verificando imports básicos...")
try:
    import numpy as np
    print("   ✓ numpy")
except ImportError as e:
    print(f"   ✗ numpy: {e}")

try:
    import pickle
    print("   ✓ pickle")
except ImportError as e:
    print(f"   ✗ pickle: {e}")

# 2. Verificar MalmoPython
print("\n2. Verificando MalmoPython...")
try:
    import MalmoPython as Malmo
    print("   ✓ MalmoPython importado")
    print(f"   Versión de Python: {sys.version}")
except ImportError as e:
    print(f"   ✗ MalmoPython: {e}")
    print("   ⚠️  Asegúrate de que Malmo esté instalado correctamente")

# 3. Verificar módulos del proyecto
print("\n3. Verificando módulos del proyecto...")
try:
    from agente_rl import AgenteQLearning
    print("   ✓ agente_rl.AgenteQLearning")
except ImportError as e:
    print(f"   ✗ agente_rl: {e}")

try:
    from entorno_malmo import EntornoMalmo
    print("   ✓ entorno_malmo.EntornoMalmo")
except ImportError as e:
    print(f"   ✗ entorno_malmo: {e}")

# 4. Probar crear instancias
print("\n4. Probando crear instancias...")
try:
    from agente_rl import AgenteQLearning
    agente = AgenteQLearning(alpha=0.1, gamma=0.95, epsilon=0.3)
    print(f"   ✓ Agente creado")
    print(f"     - Estados en tabla Q: {len(agente.Q)}")
    print(f"     - Acciones disponibles: {len(agente.ACCIONES)}")
    print(f"     - Epsilon: {agente.epsilon}")
except Exception as e:
    print(f"   ✗ Error al crear agente: {e}")

# 5. Probar estado discretizado
print("\n5. Probando discretización de estado...")
try:
    from agente_rl import AgenteQLearning
    agente = AgenteQLearning()
    
    # Observación de prueba
    obs_prueba = {
        "Yaw": 45,
        "YPos": 64,
        "XPos": 0,
        "ZPos": 0,
        "near5x3x5": ["air"] * 75,
        "inventory": [],
        "LineOfSight": {"type": "air"}
    }
    
    estado = agente.obtener_estado_discretizado(obs_prueba)
    print(f"   ✓ Estado discretizado: {estado}")
    print(f"     - Tipo: {type(estado)}")
    print(f"     - Longitud: {len(estado)}")
except Exception as e:
    print(f"   ✗ Error en discretización: {e}")

# 6. Probar elegir acción
print("\n6. Probando selección de acción...")
try:
    accion_idx = agente.elegir_accion(estado)
    comando = agente.obtener_comando(accion_idx)
    print(f"   ✓ Acción elegida: {accion_idx} -> {comando}")
except Exception as e:
    print(f"   ✗ Error al elegir acción: {e}")

# 7. Verificar todos los comandos
print("\n7. Verificando comandos disponibles...")
try:
    print("   Acciones del agente:")
    for idx, cmd in agente.ACCIONES.items():
        print(f"     {idx}: {cmd}")
    print(f"   ✓ Total de acciones: {len(agente.ACCIONES)}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 8. Verificar guardado/cargado de modelo
print("\n8. Probando guardado/cargado de modelo...")
try:
    import tempfile
    import os
    
    # Crear archivo temporal
    temp_file = os.path.join(tempfile.gettempdir(), "test_modelo_madera.pkl")
    
    # Guardar
    agente.guardar_modelo(temp_file)
    print(f"   ✓ Modelo guardado en: {temp_file}")
    
    # Cargar
    agente2 = AgenteQLearning()
    agente2.cargar_modelo(temp_file)
    print(f"   ✓ Modelo cargado exitosamente")
    print(f"     - Epsilon cargado: {agente2.epsilon}")
    
    # Limpiar
    os.remove(temp_file)
    print(f"   ✓ Archivo temporal eliminado")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Resumen final
print("\n" + "="*60)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*60)
print("\n📋 Siguiente paso: ejecutar 'python mundo_rl.py' para entrenar")
print("   (Asegúrate de que Minecraft con Malmo esté corriendo)\n")
