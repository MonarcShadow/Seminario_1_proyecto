"""
Script de Entrenamiento en MUNDO PLANO
Para pruebas iniciales sin problemas de terreno

Uso:
    python entrenar_plano.py [episodios]
    
Ejemplo:
    python entrenar_plano.py 10
"""

import sys
import time
import json
import os
import random
import MalmoPython as Malmo

from agente_rl import AgenteQLearning
from entorno_malmo import EntornoMalmo
from mundo_rl import cargar_configuracion, ejecutar_episodio, obtener_mision_xml


def entrenar_mundo_plano(num_episodios=10, guardar_cada=5, modelo_path="modelo_agente_madera_plano.pkl"):
    """
    Entrenamiento en mundo plano (para pruebas)
    """
    print("\n" + "="*60)
    print("🚀 ENTRENAMIENTO EN MUNDO PLANO - MODO PRUEBA")
    print("="*60)
    print("⚠️  Este modo usa mundo plano para evitar problemas de terreno")
    print("    Úsalo para verificar que el agente funciona correctamente")
    print("="*60)
    
    # 0. CARGAR CONFIGURACIÓN
    config = cargar_configuracion()
    
    # 1. INICIALIZAR MALMO
    agent_host = Malmo.AgentHost()
    
    # 2. CREAR AGENTE
    agente = AgenteQLearning(
        alpha=0.15,           # Un poco más de aprendizaje
        gamma=0.95,
        epsilon=0.5,          # Más exploración
        epsilon_decay=0.99    # Decae más lento
    )
    
    # Intentar cargar modelo previo
    try:
        agente.cargar_modelo(modelo_path)
        print(f"✓ Modelo cargado, continuando entrenamiento...")
    except:
        print("⚠ Iniciando entrenamiento desde cero")
    
    # 3. CREAR ENTORNO
    entorno = EntornoMalmo(agent_host)
    
    # 4. CONFIGURACIÓN DE CONEXIÓN
    client_pool = Malmo.ClientPool()
    client_pool.add(Malmo.ClientInfo(config['ip'], config['puerto']))
    
    # 5. BUCLE DE ENTRENAMIENTO
    exitos = 0
    
    print(f"\n🎮 Iniciando {num_episodios} episodios en mundo plano...\n")
    
    for episodio in range(num_episodios):
        # Spawn FIJO en posición segura (como test_movimiento y debug)
        # Mundo plano con spawn aleatorio puede colocar al agente en agua o dentro de bloques
        spawn_x = 0.5
        spawn_z = 0.5
        
        # Generar misión con MUNDO PLANO
        mision_xml = obtener_mision_xml(
            seed=None,  # No importa en mundo plano
            spawn_x=spawn_x,
            spawn_z=spawn_z,
            mundo_plano=True  # ← CLAVE: mundo plano
        )
        
        mission = Malmo.MissionSpec(mision_xml, True)
        mission_record = Malmo.MissionRecordSpec()
        
        # Iniciar misión
        print(f"\n📡 Iniciando misión {episodio + 1}/{num_episodios}...")
        
        max_reintentos = 3
        for intento in range(max_reintentos):
            try:
                agent_host.startMission(mission, client_pool, mission_record, 0, f"RL_Plano_EP{episodio}")
                break
            except Exception as e:
                if intento == max_reintentos - 1:
                    print(f"❌ Error al iniciar misión: {e}")
                    continue
                print(f"⚠ Reintentando... ({intento + 1}/{max_reintentos})")
                time.sleep(2)
        
        # Esperar inicio
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
        
        print("✓ Misión iniciada (mundo plano)")
        
        # Esperar a que el agente esté completamente spawneado
        time.sleep(2)
        
        # Verificar que la misión sigue corriendo
        world_state = agent_host.getWorldState()
        if not world_state.is_mission_running:
            print("❌ La misión terminó inmediatamente. Posible problema de spawn.")
            for error in world_state.errors:
                print(f"   Error: {error.text}")
            continue
        
        print("✓ Agente spawneado correctamente, iniciando episodio...")
        
        # Ejecutar episodio (más pasos porque mundo plano es grande)
        stats = ejecutar_episodio(
            agent_host, agente, entorno, 
            max_pasos=600,  # Menos pasos que en mundo normal
            verbose=True    # Siempre verbose en modo prueba
        )
        
        if stats['exito']:
            exitos += 1
        
        # Mostrar resumen
        print(f"\n📊 Resumen Episodio #{episodio + 1}")
        print(f"   Pasos: {stats['pasos']}")
        print(f"   Éxito: {'✓' if stats['exito'] else '✗'}")
        print(f"   Recompensa total: {stats['recompensa_total']:.2f}")
        print(f"   Tasa de éxito: {exitos}/{episodio + 1} ({100*exitos/(episodio+1):.1f}%)")
        
        # Guardar modelo periódicamente
        if (episodio + 1) % guardar_cada == 0:
            agente.guardar_modelo(modelo_path)
            agente.imprimir_estadisticas()
        
        # Esperar entre episodios
        time.sleep(1)
    
    # Guardar modelo final
    print("\n" + "="*60)
    print("🏁 ENTRENAMIENTO EN MUNDO PLANO COMPLETADO")
    print("="*60)
    agente.guardar_modelo(modelo_path)
    agente.imprimir_estadisticas()
    
    print(f"\n✓ Modelo guardado en: {modelo_path}")
    print(f"✓ Episodios exitosos: {exitos}/{num_episodios} ({100*exitos/num_episodios:.1f}%)")
    
    if exitos > 0:
        print(f"\n🎉 ¡El agente funcionó correctamente en mundo plano!")
        print(f"   Puedes proceder a entrenar en mundo normal con:")
        print(f"   python mundo_rl.py")
    else:
        print(f"\n⚠️  El agente no tuvo éxitos. Revisa:")
        print(f"   - ¿Hay árboles en el mundo plano generado?")
        print(f"   - ¿Los comandos de movimiento funcionan?")
        print(f"   - ¿El agente se mueve en Minecraft?")


if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print("MalmoPython importado correctamente")
    
    # Parámetros de línea de comandos
    num_episodios = 10
    if len(sys.argv) > 1:
        try:
            num_episodios = int(sys.argv[1])
        except:
            print("⚠️  Uso: python entrenar_plano.py [episodios]")
            print("   Usando valor por defecto: 10 episodios")
    
    print(f"\n🎯 Configuración:")
    print(f"   Episodios: {num_episodios}")
    print(f"   Modo: MUNDO PLANO (pruebas)")
    print(f"   Modelo: modelo_agente_madera_plano.pkl")
    
    try:
        entrenar_mundo_plano(
            num_episodios=num_episodios,
            guardar_cada=5,
            modelo_path="modelo_agente_madera_plano.pkl"
        )
    except KeyboardInterrupt:
        print("\n\n⚠ Entrenamiento interrumpido por usuario")
        print("El modelo parcial ha sido guardado")
    except Exception as e:
        print(f"\n❌ Error durante entrenamiento: {e}")
        import traceback
        traceback.print_exc()
