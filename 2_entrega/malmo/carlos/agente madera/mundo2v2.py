"""
Script Principal: Entrenamiento del Agente RL para Recolección de Madera
Objetivo: Conseguir 3 bloques de madera picando árboles

Autor: Sistema de IA
"""

import sys
import time
import json
import MalmoPython as Malmo

from agente_madera_rl import AgenteMaderaQLearning
from entorno_madera import EntornoMadera


# ============================================================================
# CONFIGURACIÓN DEL MUNDO (XML de Malmo)
# ============================================================================

def obtener_mision_xml(seed=42):
    """
    Genera XML de la misión con mundo normal, árboles y pico de madera inicial
    
    Parámetros:
    -----------
    seed: int
        Semilla para generación del mundo
    """
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <About>
    <Summary>Entrenamiento RL - Recolección de Madera (Objetivo: 3 bloques)</Summary>
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
      <!-- Mundo normal con árboles -->
      <DefaultWorldGenerator seed="{seed}" forceReset="false"/>
      
      <ServerQuitFromTimeUp timeLimitMs="120000"/>  <!-- 2 minutos máximo -->
      <ServerQuitWhenAnyAgentFinishes/>
    </ServerHandlers>
  </ServerSection>

  <AgentSection mode="Survival">
    <Name>AgenteMadera</Name>
    <AgentStart>
      <!-- Spawn en zona con árboles (ajustar según seed) -->
      <Placement x="0" y="64" z="0" pitch="0" yaw="0"/>
      
      <!-- Inventario inicial: Hacha de madera en slot 0 (hotbar) -->
      <Inventory>
        <InventoryItem slot="0" type="wooden_axe"/>
      </Inventory>
    </AgentStart>
    
    <AgentHandlers>
      <!-- ==================== OBSERVACIONES ==================== -->
      
      <!-- Estadísticas completas (posición, salud, inventario, etc.) -->
      <ObservationFromFullStats/>
      
      <!-- Rejilla 5x5x5 para percepción local de bloques -->
      <ObservationFromGrid>
        <Grid name="near5x5x5">
          <min x="-2" y="-2" z="-2"/>
          <max x="2" y="2" z="2"/>
        </Grid>
      </ObservationFromGrid>
      
      <!-- Raycast para detectar qué bloque está mirando -->
      <ObservationFromRay/>
      
      <!-- Información del inventario -->
      <ObservationFromFullInventory/>
      
      <!-- Detectar entidades cercanas -->
      <ObservationFromNearbyEntities>
        <Range name="entities" xrange="20" yrange="10" zrange="20"/>
      </ObservationFromNearbyEntities>
      
      <!-- ==================== RECOMPENSAS ==================== -->
      
      <!-- Recompensa por recolectar madera -->
      <RewardForCollectingItem>
        <Item reward="100.0" type="log"/>
        <Item reward="100.0" type="log2"/>
      </RewardForCollectingItem>
      
      <!-- Pequeño costo por comando (fomenta eficiencia) -->
      <RewardForSendingCommand reward="-0.5"/>
      
      <!-- ==================== COMANDOS ==================== -->
      
      <!-- Comandos discretos de movimiento -->
      <DiscreteMovementCommands/>
      
      <!-- Comandos continuos para atacar/picar -->
      <ContinuousMovementCommands>
        <ModifierList type="deny-list">
          <command>move</command>
          <command>turn</command>
          <command>strafe</command>
          <command>jump</command>
          <command>crouch</command>
        </ModifierList>
      </ContinuousMovementCommands>
      
      <!-- ==================== CONDICIONES DE SALIDA ==================== -->
      
      <!-- El agente termina cuando consigue 3 maderas -->
      <AgentQuitFromCollectingItem>
        <Item type="log" amount="3"/>
      </AgentQuitFromCollectingItem>
      
    </AgentHandlers>
  </AgentSection>
</Mission>
'''


# ============================================================================
# FUNCIONES DE ENTRENAMIENTO
# ============================================================================

def ejecutar_episodio(agent_host, agente, entorno, max_pasos=800, verbose=True):
    """
    Ejecuta un episodio completo de entrenamiento
    
    Parámetros:
    -----------
    agent_host: MalmoPython.AgentHost
        Cliente de Malmo
    agente: AgenteMaderaQLearning
        Agente de RL
    entorno: EntornoMadera
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
    objetivo_completado = False
    madera_recolectada = 0
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"🎮 EPISODIO #{agente.episodios_completados + 1}")
        print(f"   Epsilon: {agente.epsilon:.4f} | Objetivo: 3 bloques de madera")
        print(f"{'='*70}")
    
    # Esperar a tener primera observación
    time.sleep(2)
    
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
        
        # 3. EJECUTAR ACCIÓN
        entorno.ejecutar_accion(comando)
        
        # 4. OBSERVAR RESULTADO Y RECOMPENSAS DE MALMO
        if not entorno.actualizar_world_state():
            break
        
        # Capturar recompensas de Malmo
        recompensa_malmo = 0.0
        for reward in entorno.world_state.rewards:
            recompensa_malmo += reward.getValue()
        
        obs_siguiente = entorno.obtener_observacion()
        if obs_siguiente is None:
            break
        
        siguiente_estado = agente.obtener_estado_discretizado(obs_siguiente)
        
        # 5. CALCULAR RECOMPENSA TOTAL
        recompensa = entorno.calcular_recompensa(obs_siguiente, comando, recompensa_malmo)
        
        # 6. VERIFICAR OBJETIVO
        objetivo_completado, madera_recolectada = entorno.verificar_objetivo_completado(obs_siguiente)
        
        # 7. ACTUALIZAR Q-TABLE
        agente.actualizar_q(estado, accion_idx, recompensa, siguiente_estado, objetivo_completado)
        
        # 8. MOSTRAR PROGRESO
        if verbose and pasos % 30 == 0:
            x = obs_siguiente.get("XPos", 0)
            y = obs_siguiente.get("YPos", 64)
            z = obs_siguiente.get("ZPos", 0)
            
            linea_vista = obs_siguiente.get("LineOfSight", {})
            mirando = linea_vista.get("type", "air")
            
            print(f"   Paso {pasos:3d} | Pos: ({x:5.1f}, {y:5.1f}, {z:5.1f}) | "
                  f"Mirando: {mirando:12s} | Madera: {madera_recolectada}/3 | R: {recompensa:+7.2f}")
        
        if objetivo_completado:
            print(f"\n   🏆 ¡¡¡OBJETIVO COMPLETADO en paso {pasos}!!!")
            print(f"   🪵 Madera recolectada: {madera_recolectada} bloques")
            break
        
        pasos += 1
        time.sleep(0.05)  # Pequeña pausa entre acciones
    
    # Finalizar episodio
    agente.finalizar_episodio(madera_recolectada)
    
    return {
        'pasos': pasos,
        'exito': objetivo_completado,
        'madera': madera_recolectada,
        'recompensa_total': agente.historial_recompensas[-1]
    }


def entrenar(num_episodios=30, guardar_cada=5, modelo_path="modelo_madera_ql.pkl"):
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
    print("\n" + "="*70)
    print("🚀 INICIANDO ENTRENAMIENTO: RECOLECCIÓN DE MADERA")
    print("="*70)
    print("📋 Objetivo: Entrenar agente para conseguir 3 bloques de madera")
    print("🪓 Herramienta inicial: Pico de madera en hotbar")
    print("="*70)
    
    # 1. INICIALIZAR MALMO
    agent_host = Malmo.AgentHost()
    
    try:
        agent_host.parse(sys.argv)
    except RuntimeError as e:
        print(f'ERROR: {e}')
        print(agent_host.getUsage())
        exit(1)
    
    # 2. CREAR AGENTE
    agente = AgenteMaderaQLearning(
        alpha=0.15,
        gamma=0.95,
        epsilon=0.4,
        epsilon_decay=0.995
    )
    
    # Intentar cargar modelo previo
    try:
        agente.cargar_modelo(modelo_path)
    except:
        print("⚠ Iniciando entrenamiento desde cero")
    
    # 3. CREAR ENTORNO
    entorno = EntornoMadera(agent_host)
    
    # 4. CONFIGURACIÓN DE CONEXIÓN
    client_pool = Malmo.ClientPool()
    client_pool.add(Malmo.ClientInfo("127.0.0.1", 10001))
    
    # 5. BUCLE DE ENTRENAMIENTO
    exitos = 0
    madera_total_acumulada = 0
    
    for episodio in range(num_episodios):
        # Generar misión
        mision_xml = obtener_mision_xml(seed=42)  # Mismo mundo para consistencia
        mission = Malmo.MissionSpec(mision_xml, True)
        mission_record = Malmo.MissionRecordSpec()
        
        # Iniciar misión
        print(f"\n📡 Iniciando misión (episodio {episodio + 1}/{num_episodios})...")
        
        max_reintentos = 3
        for intento in range(max_reintentos):
            try:
                agent_host.startMission(mission, client_pool, mission_record, 0, f"Madera_EP{episodio}")
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
        stats = ejecutar_episodio(agent_host, agente, entorno, 
                                 max_pasos=800, 
                                 verbose=(episodio % 3 == 0))
        
        if stats['exito']:
            exitos += 1
        
        madera_total_acumulada += stats['madera']
        
        # Mostrar resumen
        print(f"\n📊 Resumen Episodio #{episodio + 1}")
        print(f"   Pasos: {stats['pasos']}")
        print(f"   Éxito: {'✓ SÍ' if stats['exito'] else '✗ NO'}")
        print(f"   Madera recolectada: {stats['madera']}/3")
        print(f"   Recompensa total: {stats['recompensa_total']:.2f}")
        print(f"   Tasa de éxito global: {exitos}/{episodio + 1} ({100*exitos/(episodio+1):.1f}%)")
        print(f"   Madera promedio: {madera_total_acumulada/(episodio+1):.2f}")
        
        # Guardar modelo periódicamente
        if (episodio + 1) % guardar_cada == 0:
            agente.guardar_modelo(modelo_path)
            agente.imprimir_estadisticas()
        
        # Pequeña pausa entre episodios
        time.sleep(1)
    
    # Guardar modelo final
    print("\n" + "="*70)
    print("🏁 ENTRENAMIENTO COMPLETADO")
    print("="*70)
    agente.guardar_modelo(modelo_path)
    agente.imprimir_estadisticas()
    
    print(f"\n✓ Modelo final guardado en: {modelo_path}")
    print(f"✓ Episodios exitosos: {exitos}/{num_episodios} ({100*exitos/num_episodios:.1f}%)")
    print(f"✓ Madera promedio por episodio: {madera_total_acumulada/num_episodios:.2f}")


# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print("MalmoPython importado correctamente")
    
    # Parámetros de entrenamiento
    NUM_EPISODIOS = 30
    MODELO_PATH = "modelo_agente_madera.pkl"
    
    try:
        entrenar(
            num_episodios=NUM_EPISODIOS,
            guardar_cada=5,
            modelo_path=MODELO_PATH
        )
    except KeyboardInterrupt:
        print("\n\n⚠ Entrenamiento interrumpido por usuario")
        print("El modelo parcial ha sido guardado")
    except Exception as e:
        print(f"\n❌ Error durante entrenamiento: {e}")
        import traceback
        traceback.print_exc()
