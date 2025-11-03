"""
Script Principal: Entrenamiento del Agente RL en Malmo
Búsqueda y Recolección de Madera usando Q-Learning

Autor: Sistema de IA
"""

import sys
import time
import json
import os
import MalmoPython as Malmo

from agente_rl import AgenteQLearning
from entorno_malmo import EntornoMalmo


# ============================================================================
# CARGAR CONFIGURACIÓN DESDE .config
# ============================================================================

def cargar_configuracion():
    """
    Carga la configuración desde el archivo .config
    
    Retorna:
    --------
    dict: Configuración con ip, puerto y semilla
    """
    config = {
        'ip': '127.0.0.1',
        'puerto': 10001,
        'seed': 12345678
    }
    
    # Buscar archivo .config en el directorio padre (malmo/)
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.config')
    
    try:
        with open(config_path, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if '=' in linea and not linea.startswith('#'):
                    clave, valor = linea.split('=', 1)
                    clave = clave.strip()
                    valor = valor.strip().strip('"')
                    
                    if clave == 'carlos':
                        config['ip'] = valor
                    elif clave == 'seed':
                        config['seed'] = int(valor)
        
        print(f"✓ Configuración cargada desde: {config_path}")
        print(f"  IP: {config['ip']}")
        print(f"  Puerto: {config['puerto']}")
        print(f"  Semilla: {config['seed']}")
    except FileNotFoundError:
        print(f"⚠ No se encontró {config_path}, usando valores por defecto")
    except Exception as e:
        print(f"⚠ Error al leer configuración: {e}, usando valores por defecto")
    
    return config


# ============================================================================
# CONFIGURACIÓN DEL MUNDO (XML de Malmo)
# ============================================================================

def obtener_mision_xml(seed=None, spawn_x=None, spawn_z=None, mundo_plano=False):
    """
    Genera XML de la misión con configuración para RL - Recolección de Madera
    
    Parámetros:
    -----------
    seed: int o None
        Semilla para generación del mundo (None = aleatorio)
    spawn_x, spawn_z: float o None
        Coordenadas de spawn (None = spawn natural)
    mundo_plano: bool
        Si True, genera mundo plano en lugar de normal (útil para pruebas)
    """
    seed_attr = f'seed="{seed}" forceReset="true"' if seed is not None else ""
    
    # Configurar generador de mundo
    if mundo_plano:
        # Mundo plano con árboles para pruebas
        world_generator = '<FlatWorldGenerator generatorString="3;7,2*3,2;1;village,biome_1,decoration"/>'
        spawn_y = 4  # Altura del mundo plano
    else:
        # Mundo normal generado
        world_generator = f'<DefaultWorldGenerator {seed_attr}/>'
        spawn_y = 64
    
    # Configurar spawn
    if spawn_x is not None and spawn_z is not None:
        spawn_placement = f'''
      <Placement x="{spawn_x}" y="{spawn_y}" z="{spawn_z}" pitch="0" yaw="0"/>'''
    else:
        spawn_placement = f"\n      <!-- Spawn natural del mundo (altura Y={spawn_y}) -->"
    
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <About>
    <Summary>Entrenamiento RL - Búsqueda y Recolección de Madera</Summary>
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
      <!-- Generador de mundo (normal con semilla o plano para pruebas) -->
      {world_generator}
      
      <ServerQuitFromTimeUp timeLimitMs="120000"/>  <!-- 120 segundos máximo -->
      <ServerQuitWhenAnyAgentFinishes/>
    </ServerHandlers>
  </ServerSection>

  <AgentSection mode="Survival">
    <Name>AgentRL_Madera</Name>
    <AgentStart>{spawn_placement}
      <Inventory>
        <!-- El agente empieza sin herramientas (manos desnudas) -->
      </Inventory>
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
      
      <!-- Inventario para saber si recogió madera -->
      <ObservationFromFullInventory/>
      
      <!-- Detectar entidades cercanas (items droppeados) -->
      <ObservationFromNearbyEntities>
        <Range name="entities" xrange="10" yrange="5" zrange="10"/>
      </ObservationFromNearbyEntities>
      
      <!-- RECOMPENSAS DEL MUNDO -->
      <!-- Recompensa por recolectar bloques de madera o tablas -->
      <RewardForCollectingItem>
        <Item type="log" reward="50.0"/>
        <Item type="log2" reward="50.0"/>
        <Item type="planks" reward="50.0"/>
      </RewardForCollectingItem>
      
      <!-- Costo por acción -->
      <RewardForSendingCommand reward="-0.5"/>
      
      <!-- COMANDOS -->
      <DiscreteMovementCommands/>
      
      <!-- CONDICIONES DE SALIDA -->
      <!-- NO usar AgentQuitFromCollectingItem porque termina con 1 item -->
      <!-- La terminación se maneja en código Python verificando cantidad -->
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
    madera_obtenida = False
    
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
        
        # 2.5 SISTEMA ANTI-STUCK: Si está muy atascado, forzar movimiento (igual que agente agua)
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
        
        # 2.6 HEURÍSTICA: Si ve madera enfrente Y YA ESTÁ PICANDO, continuar (solo si no está en anti-stuck)
        # IMPORTANTE: Solo aplicar si el agente YA eligió attack, no forzar attack en otras acciones
        if entorno.pasos_sin_movimiento < 10:  # No interferir con anti-stuck
            # Solo mantener attack si YA está picando y sigue viendo madera
            if "attack" in comando and estado[2] == 1 and estado[8] == 1:  # madera_frente y mirando_madera
                # Ya está picando correctamente, mantener el comando
                pass
            # Si acaba de terminar de picar, sugerir moverse para recoger drops
            elif entorno.pasos_picando == 0 and not entorno.picando_actualmente:
                # Detectar si hay items cerca
                entities = obs.get("entities", [])
                hay_items_cerca = any(e.get("name") == "item" for e in entities)
                if hay_items_cerca and "move" not in comando:
                    # Solo sugerir si el agente no ya eligió moverse
                    if verbose and pasos % 25 == 0:
                        print(f"   � Sugerencia: hay items cerca para recoger")
        
        # 3. EJECUTAR ACCIÓN (duración corta como agente agua)
        entorno.ejecutar_accion(comando, duracion=0.1)
        
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
        
        # 5. CALCULAR RECOMPENSA
        recompensa = entorno.calcular_recompensa(obs_siguiente, comando, recompensa_malmo)
        
        # 6. VERIFICAR SI OBTUVO MADERA
        madera_obtenida = entorno.verificar_madera_obtenida(obs_siguiente)
        
        # 7. ACTUALIZAR Q-TABLE
        agente.actualizar_q(estado, accion_idx, recompensa, siguiente_estado, madera_obtenida)
        
        # 8. MOSTRAR PROGRESO
        if verbose and pasos % 25 == 0:
            x = obs_siguiente.get("XPos", 0)
            y = obs_siguiente.get("YPos", 64)
            z = obs_siguiente.get("ZPos", 0)
            inventario = obs_siguiente.get("inventory", [])
            print(f"   Paso {pasos:3d} | Pos: ({x:5.1f}, {y:5.1f}, {z:5.1f}) | "
                  f"Acción: {comando:12s} | R: {recompensa:+6.2f} | Inv: {len(inventario)}")
        
        if madera_obtenida:
            print(f"\n   🎉 ¡OBJETIVO COMPLETADO en paso {pasos}!")
            print(f"   ✅ Alcanzó el objetivo: 2+ bloques de madera O 8+ tablas")
            break
        
        pasos += 1
        time.sleep(0.1)  # Pequeña pausa entre iteraciones
    
    # Finalizar episodio
    agente.finalizar_episodio()
    
    return {
        'pasos': pasos,
        'exito': madera_obtenida,
        'recompensa_total': agente.historial_recompensas[-1]
    }


def entrenar(num_episodios=50, guardar_cada=10, modelo_path="modelo_agente_madera.pkl", 
             mundo_plano=False, epsilon_override=None, mostrar_cada=10):
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
    mundo_plano: bool
        Si True, usa mundo plano para pruebas. Si False, mundo normal
    epsilon_override: float or None
        Si se especifica, fuerza este valor de epsilon (útil para ejecución sin exploración)
    mostrar_cada: int
        Mostrar detalles cada N episodios
    """
    print("\n" + "="*60)
    print("🚀 INICIANDO ENTRENAMIENTO DE AGENTE RL - RECOLECCIÓN DE MADERA")
    print("="*60)
    
    # 0. CARGAR CONFIGURACIÓN
    config = cargar_configuracion()
    SEED_FIJA = config['seed']
    
    # 1. INICIALIZAR MALMO
    agent_host = Malmo.AgentHost()
    
    # 2. CREAR AGENTE
    agente = AgenteQLearning(
        alpha=0.1,
        gamma=0.95,
        epsilon=0.4,  # Más exploración inicial para madera
        epsilon_decay=0.995
    )
    
    # Intentar cargar modelo previo
    try:
        agente.cargar_modelo(modelo_path)
    except:
        print("⚠ Iniciando entrenamiento desde cero")
    
    # Aplicar epsilon_override si se especificó (para ejecución sin exploración)
    if epsilon_override is not None:
        agente.epsilon = epsilon_override
        print(f"🎯 Epsilon forzado a: {epsilon_override} (modo {'EXPLOTACIÓN' if epsilon_override == 0 else 'PERSONALIZADO'})")
    
    # 3. CREAR ENTORNO
    entorno = EntornoMalmo(agent_host)
    
    # 4. CONFIGURACIÓN DE CONEXIÓN
    client_pool = Malmo.ClientPool()
    client_pool.add(Malmo.ClientInfo(config['ip'], config['puerto']))
    
    # 5. BUCLE DE ENTRENAMIENTO
    exitos = 0
    import random
    
    for episodio in range(num_episodios):
        # Usar semilla fija para mundo predecible
        seed = SEED_FIJA
        
        # Spawn natural del mundo (Minecraft elige posición segura)
        # El agente puede tener obstáculos en algunas direcciones pero no todas
        spawn_x = None
        spawn_z = None
        
        mision_xml = obtener_mision_xml(seed, spawn_x, spawn_z, mundo_plano=mundo_plano)
        mission = Malmo.MissionSpec(mision_xml, True)
        mission_record = Malmo.MissionRecordSpec()
        
        # Iniciar misión
        print(f"\n📡 Iniciando misión (episodio {episodio + 1}/{num_episodios})...")
        
        max_reintentos = 3
        for intento in range(max_reintentos):
            try:
                agent_host.startMission(mission, client_pool, mission_record, 0, f"RL_Madera_EP{episodio}")
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
        
        print("✓ Misión iniciada (mundo normal)")
        
        # Esperar más tiempo en mundo normal (tarda más en generar terreno)
        print("⏳ Esperando generación de terreno...")
        time.sleep(5)
        
        # Verificar que la misión sigue corriendo
        world_state = agent_host.getWorldState()
        if not world_state.is_mission_running:
            print("❌ La misión terminó inmediatamente. Saltando episodio...")
            for error in world_state.errors:
                print(f"   Error: {error.text}")
            continue
        
        # Verificar que tenemos observaciones
        if world_state.number_of_observations_since_last_state == 0:
            print("⏳ Esperando observaciones iniciales...")
            time.sleep(2)
        
        print("✓ Agente spawneado correctamente, iniciando episodio...")
        
        # Ejecutar episodio
        stats = ejecutar_episodio(agent_host, agente, entorno, max_pasos=800, verbose=(episodio % 5 == 0))
        
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
        time.sleep(0.5)
    
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
    MODELO_PATH = "modelo_agente_madera.pkl"
    
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
