"""
Script Principal: Entrenamiento del Agente RL en Malmo
Búsqueda de agua usando Q-Learning

Autor: Sistema de IA
"""

import sys
import time
import json
import MalmoPython as Malmo

from agente_rl import AgenteQLearning
from entorno_malmo import EntornoMalmo


# ============================================================================
# CONFIGURACIÓN DEL MUNDO (XML de Malmo)
# ============================================================================

def obtener_mision_xml(seed=None, spawn_x=None, spawn_z=None):
    """
    Genera XML de la misión con configuración para RL
    
    Parámetros:
    -----------
    seed: int o None
        Semilla para generación del mundo (None = aleatorio)
    spawn_x, spawn_z: float o None
        Coordenadas de spawn (None = spawn natural)
    """
    seed_attr = f'seed="{seed}" forceReset="true"' if seed is not None else ""
    
    # Configurar spawn
    if spawn_x is not None and spawn_z is not None:
        spawn_placement = f'''
      <Placement x="{spawn_x}" y="64" z="{spawn_z}" pitch="30" yaw="0"/>'''
    else:
        spawn_placement = "\n      <!-- Spawn natural del mundo (sin coordenadas fijas) -->"
    
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <About>
    <Summary>Entrenamiento RL - Búsqueda de Agua</Summary>
  </About>

  <ServerSection>
    <ServerInitialConditions>
      <Time>
        <StartTime>6000</StartTime>
        <AllowPassageOfTime>false</AllowPassageOfTime>
      </Time>
      <Weather>clear</Weather>
      <AllowSpawning>false</AllowSpawning>
    </ServerInitialConditions>
    <ServerHandlers>
      <!-- Mundo normal generado con semilla fija para reproducibilidad -->
      <DefaultWorldGenerator {seed_attr}/>
      
      <ServerQuitFromTimeUp timeLimitMs="60000"/>  <!-- 60 segundos máximo -->
      <ServerQuitWhenAnyAgentFinishes/>
    </ServerHandlers>
  </ServerSection>

  <AgentSection mode="Survival">
    <Name>AgentRL</Name>
    <AgentStart>{spawn_placement}
    </AgentStart>
    <AgentHandlers>
      <!-- OBSERVACIONES -->
      <ObservationFromFullStats/>
      
      <!-- Rejilla 5x3x5 para percepción local -->
      <ObservationFromGrid>
        <Grid name="near5x3x5">
          <min x="-2" y="-1" z="-2"/>
          <max x="2" y="1" z="2"/>
        </Grid>
      </ObservationFromGrid>
      
      <!-- Raycast para ver qué mira el agente -->
      <ObservationFromRay/>
      
      <!-- Detectar entidades cercanas (útil para biomas) -->
      <ObservationFromNearbyEntities>
        <Range name="entities" xrange="10" yrange="5" zrange="10"/>
      </ObservationFromNearbyEntities>
      
      <!-- RECOMPENSAS DEL MUNDO -->
      <RewardForTouchingBlockType>
        <Block reward="100.0" type="water" behaviour="onceOnly"/>
        <Block reward="100.0" type="flowing_water" behaviour="onceOnly"/>
      </RewardForTouchingBlockType>
      
      <!-- Costo por acción (ya manejado en código, pero puede reforzarse aquí) -->
      <RewardForSendingCommand reward="-0.5"/>
      
      <!-- COMANDOS -->
      <DiscreteMovementCommands/>
      
      <!-- CONDICIONES DE SALIDA -->
      <AgentQuitFromTouchingBlockType>
        <Block type="water"/>
        <Block type="flowing_water"/>
      </AgentQuitFromTouchingBlockType>
      
      <AgentQuitFromReachingPosition>
        <Marker x="0" y="50" z="0" tolerance="2.0" description="Caída crítica"/>
      </AgentQuitFromReachingPosition>
    </AgentHandlers>
  </AgentSection>
</Mission>
'''


# ============================================================================
# FUNCIONES DE ENTRENAMIENTO
# ============================================================================

def ejecutar_episodio(agent_host, agente, entorno, max_pasos=500, verbose=True):
    """
    Ejecuta un episodio completo de entrenamiento
    
    Parámetros:
    -----------
    agent_host: MalmoPython.AgentHost
        Cliente de Malmo
    agente: AgenteQLearning
        Agente de RL
    entorno: EntornoMalmo
        Wrapper del entorno
    max_pasos: int
        Máximo de pasos por episodio
    verbose: bool
        Mostrar información detallada
    
    Retorna:
    --------
    dict: Estadísticas del episodio
    """
    entorno.reset()
    pasos = 0
    agua_encontrada = False
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🎮 EPISODIO #{agente.episodios_completados + 1}")
        print(f"   Epsilon: {agente.epsilon:.4f} (exploración)")
        print(f"{'='*60}")
    
    while entorno.actualizar_world_state() and pasos < max_pasos:
        obs = entorno.obtener_observacion()
        
        if obs is None:
            time.sleep(0.1)
            continue
        
        # 1. OBTENER ESTADO ACTUAL
        estado = agente.obtener_estado_discretizado(obs)
        
        # 2. ELEGIR ACCIÓN (ε-greedy)
        accion_idx = agente.elegir_accion(estado)
        comando = agente.obtener_comando(accion_idx)
        
        # 2.5 SISTEMA ANTI-STUCK: Si está muy atascado, forzar movimiento hacia adelante
        if entorno.pasos_sin_movimiento > 10:
            # Forzar secuencia de escape: girar 180° y avanzar
            if entorno.pasos_sin_movimiento == 11:
                comando = "turn 1"
                if verbose:
                    print(f"   ⚠️ SISTEMA ANTI-STUCK: Girando para escapar...")
            elif entorno.pasos_sin_movimiento == 12:
                comando = "turn 1"
            else:
                comando = "jumpmove 1"
                if verbose:
                    print(f"   ⚠️ SISTEMA ANTI-STUCK: Saltando hacia adelante...")
                entorno.pasos_sin_movimiento = 0  # Resetear después de secuencia
        
        # 3. EJECUTAR ACCIÓN
        entorno.ejecutar_accion(comando, duracion=0.1)  # Cambio: 0.4 → 0.1 seg
        
        # 4. OBSERVAR RESULTADO Y RECOMPENSAS DE MALMO
        if not entorno.actualizar_world_state():
            break
        
        # Capturar recompensas de Malmo (ej: +100 por tocar agua, -0.5 por comando)
        recompensa_malmo = 0.0
        for reward in entorno.world_state.rewards:
            recompensa_malmo += reward.getValue()
        
        obs_siguiente = entorno.obtener_observacion()
        if obs_siguiente is None:
            break
        
        siguiente_estado = agente.obtener_estado_discretizado(obs_siguiente)
        
        # 5. CALCULAR RECOMPENSA (incluye recompensas de Malmo)
        recompensa = entorno.calcular_recompensa(obs_siguiente, comando, recompensa_malmo)
        
        # 6. VERIFICAR SI TOCÓ AGUA (usa recompensa de Malmo)
        agua_encontrada = entorno.verificar_agua_encontrada(obs_siguiente, recompensa_malmo)
        
        # 7. ACTUALIZAR Q-TABLE
        agente.actualizar_q(estado, accion_idx, recompensa, siguiente_estado, agua_encontrada)
        
        # 8. MOSTRAR PROGRESO
        if verbose and pasos % 20 == 0:
            x = obs_siguiente.get("XPos", 0)
            y = obs_siguiente.get("YPos", 64)
            z = obs_siguiente.get("ZPos", 0)
            print(f"   Paso {pasos:3d} | Pos: ({x:5.1f}, {y:5.1f}, {z:5.1f}) | "
                  f"Acción: {comando:12s} | R: {recompensa:+6.2f}")
        
        if agua_encontrada:
            print(f"\n   🎉 ¡AGUA ENCONTRADA en paso {pasos}!")
            break
        
        pasos += 1
        time.sleep(0.1)
    
    # Finalizar episodio
    agente.finalizar_episodio()
    
    return {
        'pasos': pasos,
        'exito': agua_encontrada,
        'recompensa_total': agente.historial_recompensas[-1]
    }


def entrenar(num_episodios=50, guardar_cada=10, modelo_path="modelo_ql.pkl"):
    """
    Bucle principal de entrenamiento
    
    Parámetros:
    -----------
    num_episodios: int
        Cantidad de episodios a entrenar
    guardar_cada: int
        Guardar modelo cada N episodios
    modelo_path: str
        Ruta para guardar/cargar el modelo
    """
    print("\n" + "="*60)
    print("🚀 INICIANDO ENTRENAMIENTO DE AGENTE RL")
    print("="*60)
    
    # 1. INICIALIZAR MALMO
    agent_host = Malmo.AgentHost()
    
    # 2. CREAR AGENTE
    agente = AgenteQLearning(
        alpha=0.1,
        gamma=0.95,
        epsilon=0.3,
        epsilon_decay=0.995
    )
    
    # Intentar cargar modelo previo
    try:
        agente.cargar_modelo(modelo_path)
    except:
        print("⚠ Iniciando entrenamiento desde cero")
    
    # 3. CREAR ENTORNO
    entorno = EntornoMalmo(agent_host)
    
    # 4. CONFIGURACIÓN DE CONEXIÓN
    client_pool = Malmo.ClientPool()
    client_pool.add(Malmo.ClientInfo("127.0.0.1", 10001))
    
    # 5. BUCLE DE ENTRENAMIENTO
    exitos = 0
    import random
    
    for episodio in range(num_episodios):
        # Generar misión con spawn ALEATORIO para variar condiciones iniciales
        if episodio < 10:
            seed = 123456  # Mismo mundo para aprender básicos
            # Spawn aleatorio en área de 100 bloques de radio
            spawn_x = random.uniform(-100, 100)
            spawn_z = random.uniform(-100, 100)
        else:
            seed = None  # Mundos aleatorios para generalizar
            spawn_x = None
            spawn_z = None
        
        mision_xml = obtener_mision_xml(seed, spawn_x, spawn_z)
        mission = Malmo.MissionSpec(mision_xml, True)
        mission_record = Malmo.MissionRecordSpec()
        
        # Iniciar misión
        print(f"\n📡 Iniciando misión (episodio {episodio + 1}/{num_episodios})...")
        
        max_reintentos = 3
        for intento in range(max_reintentos):
            try:
                agent_host.startMission(mission, client_pool, mission_record, 0, f"RL_EP{episodio}")
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
        
        print("✓ Misión iniciada")
        
        # Ejecutar episodio
        stats = ejecutar_episodio(agent_host, agente, entorno, max_pasos=500, verbose=(episodio % 5 == 0))
        
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
        
        # Esperar entre episodios (reducido para entrenamiento más rápido)
        time.sleep(0.5)  # Cambio: 2 → 0.5 seg
    
    # Guardar modelo final
    print("\n" + "="*60)
    print("🏁 ENTRENAMIENTO COMPLETADO")
    print("="*60)
    agente.guardar_modelo(modelo_path)
    agente.imprimir_estadisticas()
    
    print(f"\n✓ Modelo final guardado en: {modelo_path}")
    print(f"✓ Episodios exitosos: {exitos}/{num_episodios} ({100*exitos/num_episodios:.1f}%)")


# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print("MalmoPython importado correctamente")
    
    # Parámetros de entrenamiento
    NUM_EPISODIOS = 50
    MODELO_PATH = "modelo_agente_agua.pkl"
    
    try:
        entrenar(
            num_episodios=NUM_EPISODIOS,
            guardar_cada=10,
            modelo_path=MODELO_PATH
        )
    except KeyboardInterrupt:
        print("\n\n⚠ Entrenamiento interrumpido por usuario")
        print("El modelo parcial ha sido guardado")
    except Exception as e:
        print(f"\n❌ Error durante entrenamiento: {e}")
        import traceback
        traceback.print_exc()
