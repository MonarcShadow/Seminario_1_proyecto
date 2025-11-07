"""
Ejecutar Modelo Entrenado (Sin Exploración)
Usa el modelo guardado con epsilon=0 (solo explotación)

Autor: Sistema de IA
Fecha: Noviembre 2025
"""

import MalmoPython
import json
import time
import sys
from agente_rl import AgenteQLearningProgresivo
from entorno_malmo import EntornoMalmoProgresivo
from mundo_rl import generar_mundo_plano_xml
from config import crear_client_pool


def ejecutar_modelo(modelo_path='modelo_progresivo.pkl', num_episodios=5, seed=123456):
    """
    Ejecuta el modelo entrenado sin exploración
    
    Parámetros:
    -----------
    modelo_path: str
        Ruta al modelo entrenado
    num_episodios: int
        Número de episodios a ejecutar
    seed: int
        Semilla para generación de mundo
    """
    
    print("\n" + "="*70)
    print("🎮 EJECUTANDO MODELO ENTRENADO")
    print("   (Sin exploración - epsilon = 0)")
    print("="*70)
    print(f"Modelo: {modelo_path}")
    print(f"Episodios: {num_episodios}")
    print(f"Semilla: {seed}")
    print("="*70 + "\n")
    
    # Inicializar Malmo
    agent_host = MalmoPython.AgentHost()
    try:
        agent_host.parse(sys.argv)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        print(agent_host.getUsage())
        exit(1)
    
    # Crear agente
    agente = AgenteQLearningProgresivo()
    
    # Cargar modelo
    if not agente.cargar_modelo(modelo_path):
        print("❌ No se pudo cargar el modelo. Entrena primero con mundo_rl.py")
        return
    
    # Crear entorno
    entorno = EntornoMalmoProgresivo(agent_host)
    
    # Estadísticas
    exitos = 0
    estadisticas = []
    
    # Ejecutar episodios
    for episodio in range(1, num_episodios + 1):
        print(f"\n{'='*60}")
        print(f"EPISODIO {episodio} (MODELO ENTRENADO)")
        print(f"{'='*60}\n")
        
        # Generar misión
        mission_xml = generar_mundo_plano_xml(seed=seed)
        mission = MalmoPython.MissionSpec(mission_xml, True)
        mission_record = MalmoPython.MissionRecordSpec()
        
        # Configurar cliente (Minecraft en Windows - ver config.py)
        client_pool = crear_client_pool()
        
        # Iniciar misión
        max_reintentos = 3
        for intento in range(max_reintentos):
            try:
                agent_host.startMission(mission, client_pool, 
                                       mission_record, 0, f"RL_Ejecucion_EP{episodio}")
                break
            except Exception as e:
                if intento == max_reintentos - 1:
                    print(f"❌ Error: {e}")
                    continue
                print(f"⚠️  Reintentando... ({intento + 1}/{max_reintentos})")
                time.sleep(2)
        
        # Esperar inicio
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
        
        print("✓ Misión iniciada\n")
        time.sleep(2)
        
        # Limpiar y dar pico
        print("🧹 Limpiando inventario...")
        agent_host.sendCommand("chat /clear")
        time.sleep(0.5)
        
        print("⛏️  Dando pico de madera...")
        agent_host.sendCommand("chat /give @p wooden_pickaxe 1")
        time.sleep(0.5)
        
        # Resetear entorno
        entorno.reset_episodio()
        
        # Variables
        pasos = 0
        recompensa_acumulada = 0.0
        max_pasos = 1000
        objetivo_completado = False
        
        # Loop principal (SIN EXPLORACIÓN - epsilon=0)
        print("🎮 Ejecutando política aprendida...\n")
        
        while world_state.is_mission_running and pasos < max_pasos:
            pasos += 1
            
            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                obs = json.loads(msg)
                
                fase_actual = entorno.fase_actual
                estado = agente.obtener_estado_discretizado(obs, fase_actual)
                
                # EPSILON = 0 (sin exploración, solo explotación)
                accion = agente.elegir_accion(estado, fase_actual, epsilon_override=0.0)
                
                comando = agente.ACCIONES[accion]
                agent_host.sendCommand(comando)
                time.sleep(0.05)
                
                time.sleep(0.1)
                world_state = agent_host.getWorldState()
                
                if world_state.number_of_observations_since_last_state > 0:
                    msg = world_state.observations[-1].text
                    obs_nueva = json.loads(msg)
                    
                    recompensa = entorno.calcular_recompensa(obs_nueva, accion, fase_actual)
                    recompensa_acumulada += recompensa
                    
                    # Verificar progresión
                    entorno.verificar_progresion_fase(obs_nueva)
                    
                    # Verificar objetivo final
                    if entorno.fase_actual == 3 and entorno.materiales_recolectados['diamante'] >= 1:
                        objetivo_completado = True
                        print("\n💎 ¡OBJETIVO FINAL ALCANZADO!")
                        break
                    
                    # Mostrar progreso
                    if pasos % 50 == 0:
                        fase_num, fase_nombre = entorno.obtener_fase_actual()
                        progreso = entorno.obtener_progreso()
                        print(f"\n📊 Paso {pasos} | Fase: {fase_nombre} | Recompensa: {recompensa_acumulada:.1f}")
                        print(f"   Progreso: M:{progreso['madera']} P:{progreso['piedra']} H:{progreso['hierro']} D:{progreso['diamante']}")
                
                # Verificar muerte
                if 'IsAlive' in obs and not obs['IsAlive']:
                    print("\n💀 Agente murió")
                    break
            
            world_state = agent_host.getWorldState()
        
        # Fin episodio
        print(f"\n{'='*60}")
        print(f"FIN EPISODIO {episodio}")
        print(f"{'='*60}")
        print(f"Pasos: {pasos}")
        print(f"Recompensa: {recompensa_acumulada:.2f}")
        print(f"Objetivo: {'✓ COMPLETADO' if objetivo_completado else '✗ NO COMPLETADO'}")
        
        progreso = entorno.obtener_progreso()
        print(f"\nProgreso final:")
        print(f"  🌲 Madera:   {progreso['madera']}")
        print(f"  🪨 Piedra:   {progreso['piedra']}")
        print(f"  ⚙️  Hierro:   {progreso['hierro']}")
        print(f"  💎 Diamante: {progreso['diamante']}")
        print(f"  Fase: {entorno.obtener_fase_actual()[1]}")
        print(f"{'='*60}\n")
        
        if objetivo_completado:
            exitos += 1
        
        estadisticas.append({
            'episodio': episodio,
            'pasos': pasos,
            'recompensa': recompensa_acumulada,
            'exito': objetivo_completado,
        })
        
        time.sleep(2)
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE EJECUCIÓN")
    print("="*70)
    print(f"Episodios ejecutados: {num_episodios}")
    print(f"Objetivos completados: {exitos}/{num_episodios}")
    print(f"Tasa de éxito: {100*exitos/num_episodios:.1f}%")
    
    if estadisticas:
        recompensa_media = sum(s['recompensa'] for s in estadisticas) / len(estadisticas)
        pasos_medio = sum(s['pasos'] for s in estadisticas) / len(estadisticas)
        print(f"Recompensa media: {recompensa_media:.2f}")
        print(f"Pasos medio: {pasos_medio:.1f}")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    # Parámetros
    modelo = 'modelo_progresivo.pkl'
    num_eps = 5
    seed = 123456
    
    if len(sys.argv) > 1:
        try:
            num_eps = int(sys.argv[1])
        except:
            pass
    
    if len(sys.argv) > 2:
        try:
            seed = int(sys.argv[2])
        except:
            pass
    
    ejecutar_modelo(modelo_path=modelo, num_episodios=num_eps, seed=seed)
