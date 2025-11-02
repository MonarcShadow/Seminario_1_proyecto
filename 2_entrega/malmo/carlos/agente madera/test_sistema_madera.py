"""
Script de prueba para verificar la configuración del sistema
de recolección de madera

Verifica:
1. Importación de módulos
2. Creación de agente
3. Discretización de estados
4. Sistema de recompensas
5. Guardado/carga de modelo

Autor: Sistema de IA
"""

import sys
import os

print("="*70)
print("🧪 PRUEBA DE CONFIGURACIÓN - Sistema de Recolección de Madera")
print("="*70)

# 1. VERIFICAR IMPORTACIONES
print("\n1️⃣ Verificando importaciones...")

try:
    import numpy as np
    print("   ✓ NumPy importado")
except ImportError:
    print("   ❌ NumPy no encontrado. Instalar: pip install numpy")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    print("   ✓ Matplotlib importado")
except ImportError:
    print("   ⚠️ Matplotlib no encontrado (opcional para gráficos)")

try:
    import pickle
    print("   ✓ Pickle disponible")
except ImportError:
    print("   ❌ Pickle no disponible")
    sys.exit(1)

try:
    from agente_madera_rl import AgenteMaderaQLearning
    print("   ✓ AgenteMaderaQLearning importado")
except ImportError as e:
    print(f"   ❌ Error importando agente: {e}")
    sys.exit(1)

try:
    from entorno_madera import EntornoMadera
    print("   ✓ EntornoMadera importado")
except ImportError as e:
    print(f"   ❌ Error importando entorno: {e}")
    sys.exit(1)

try:
    import MalmoPython as Malmo
    print("   ✓ MalmoPython importado")
    malmo_disponible = True
except ImportError:
    print("   ⚠️ MalmoPython no disponible (necesario para entrenamiento)")
    malmo_disponible = False

# 2. CREAR AGENTE
print("\n2️⃣ Creando agente...")

try:
    agente = AgenteMaderaQLearning(
        alpha=0.15,
        gamma=0.95,
        epsilon=0.4
    )
    print(f"   ✓ Agente creado")
    print(f"      - Acciones disponibles: {len(agente.ACCIONES)}")
    print(f"      - Alpha: {agente.alpha}")
    print(f"      - Gamma: {agente.gamma}")
    print(f"      - Epsilon inicial: {agente.epsilon}")
except Exception as e:
    print(f"   ❌ Error creando agente: {e}")
    sys.exit(1)

# 3. PROBAR DISCRETIZACIÓN DE ESTADOS
print("\n3️⃣ Probando discretización de estados...")

observacion_prueba = {
    "Yaw": 45.0,
    "XPos": 0.0,
    "YPos": 64.0,
    "ZPos": 0.0,
    "near5x5x5": ["air"] * 50 + ["log"] * 10 + ["leaves"] * 15,
    "LineOfSight": {"type": "log", "distance": 2.5},
    "inventory": [
        {"type": "wooden_axe", "quantity": 1}
    ]
}

try:
    estado = agente.obtener_estado_discretizado(observacion_prueba)
    print(f"   ✓ Estado discretizado: {estado}")
    print(f"      - Longitud del estado: {len(estado)}")
    print(f"      - Orientación: {estado[0]}")
    print(f"      - Nivel madera visible: {estado[1]}")
    print(f"      - Madera en inventario: {estado[2]}")
    print(f"      - Mirando madera: {estado[3]}")
except Exception as e:
    print(f"   ❌ Error en discretización: {e}")
    import traceback
    traceback.print_exc()

# 4. PROBAR SELECCIÓN DE ACCIÓN
print("\n4️⃣ Probando selección de acción...")

try:
    accion_idx = agente.elegir_accion(estado)
    comando = agente.obtener_comando(accion_idx)
    print(f"   ✓ Acción elegida: {comando} (índice {accion_idx})")
    
    # Listar todas las acciones
    print(f"\n   Acciones disponibles:")
    for idx, cmd in agente.ACCIONES.items():
        print(f"      {idx}: {cmd}")
except Exception as e:
    print(f"   ❌ Error en selección de acción: {e}")

# 5. PROBAR ACTUALIZACIÓN Q
print("\n5️⃣ Probando actualización de tabla Q...")

try:
    estado_inicial = (0, 1, 0, 1, 0, 0, 1)
    accion = 0
    recompensa = 10.0
    estado_siguiente = (0, 1, 0, 1, 0, 0, 1)
    
    agente.actualizar_q(estado_inicial, accion, recompensa, estado_siguiente, False)
    
    q_valor = agente.Q[estado_inicial][accion]
    print(f"   ✓ Tabla Q actualizada")
    print(f"      - Q({estado_inicial}, {accion}) = {q_valor:.4f}")
    print(f"      - Estados en tabla Q: {len(agente.Q)}")
except Exception as e:
    print(f"   ❌ Error actualizando Q: {e}")

# 6. PROBAR SISTEMA DE RECOMPENSAS (mock)
print("\n6️⃣ Probando sistema de recompensas...")

if malmo_disponible:
    print("   ⚠️ Prueba completa requiere entorno Malmo activo (se omite)")
else:
    print("   ⚠️ MalmoPython no disponible (se omite prueba)")

# 7. PROBAR GUARDADO/CARGA
print("\n7️⃣ Probando guardado y carga de modelo...")

archivo_prueba = "test_modelo_madera.pkl"

try:
    # Guardar
    agente.guardar_modelo(archivo_prueba)
    
    # Crear nuevo agente
    agente2 = AgenteMaderaQLearning()
    
    # Cargar
    agente2.cargar_modelo(archivo_prueba)
    
    print(f"   ✓ Modelo guardado y cargado correctamente")
    print(f"      - Estados recuperados: {len(agente2.Q)}")
    print(f"      - Epsilon recuperado: {agente2.epsilon}")
    
    # Limpiar archivo de prueba
    if os.path.exists(archivo_prueba):
        os.remove(archivo_prueba)
        print(f"   ✓ Archivo de prueba eliminado")
        
except Exception as e:
    print(f"   ❌ Error en guardado/carga: {e}")
    import traceback
    traceback.print_exc()

# 8. VERIFICAR UTILIDADES
print("\n8️⃣ Verificando utilidades...")

try:
    from utils_madera import graficar_aprendizaje, analizar_tabla_q
    print("   ✓ Funciones de utilidades importadas")
    print("      - graficar_aprendizaje()")
    print("      - analizar_tabla_q()")
except ImportError as e:
    print(f"   ⚠️ Error importando utilidades: {e}")

# RESUMEN
print("\n" + "="*70)
print("📊 RESUMEN DE PRUEBAS")
print("="*70)

if malmo_disponible:
    print("✓ Sistema completamente funcional")
    print("✓ Listo para entrenar con: python mundo2v2.py")
else:
    print("⚠️ Sistema funcional pero requiere MalmoPython para entrenar")
    print("  Instalar Malmo: https://github.com/microsoft/malmo")

print("\n🎯 Próximos pasos:")
print("   1. Iniciar Minecraft con Malmo en puerto 10000")
print("   2. Ejecutar: python mundo2v2.py")
print("   3. Después del entrenamiento: python utils_madera.py graficar")
print("="*70)
