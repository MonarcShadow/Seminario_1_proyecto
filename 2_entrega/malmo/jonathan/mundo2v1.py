import sys
import time
import json
import random
import MalmoPython as Malmo
from collections import Counter

print(f"Python version: {sys.version}")
print("MalmoPython importado correctamente")

# Crear el agente host
agent_host = Malmo.AgentHost()

# Mission XML - Mundo NORMAL generado proceduralmente
missionXML = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <About>
    <Summary>Navegacion con busqueda de agua en mundo normal</Summary>
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
      <!-- Mundo normal generado por defecto - Sin coordenadas fijas -->
      <DefaultWorldGenerator seed="123456" forceReset="true"/>
      
      <ServerQuitWhenAnyAgentFinishes/>
    </ServerHandlers>
  </ServerSection>

  <AgentSection mode="Survival">
    <Name>Navigator</Name>
    <AgentStart>
      <!-- Sin coordenadas fijas - spawn aleatorio según el mundo generado -->
    </AgentStart>
    <AgentHandlers>
      <!-- Observaciones compatibles con Malmo 0.37.0 -->
      <ObservationFromFullStats/>
      <ObservationFromRay/>
      <ObservationFromNearbyEntities>
        <Range name="entities" xrange="40" yrange="40" zrange="40"/>
      </ObservationFromNearbyEntities>
      
      <!-- Recompensas -->
      <RewardForTouchingBlockType>
        <Block reward="100.0" type="water" behaviour="onceOnly"/>
        <Block reward="100.0" type="flowing_water" behaviour="onceOnly"/>
      </RewardForTouchingBlockType>
      
      <RewardForSendingCommand reward="-1.0"/>
      
      <!-- Comandos - Solo discretos para movimiento preciso -->
      <DiscreteMovementCommands/>
      
      <!-- Condiciones de salida -->
      <AgentQuitFromTouchingBlockType>
        <Block type="water"/>
        <Block type="flowing_water"/>
      </AgentQuitFromTouchingBlockType>
    </AgentHandlers>
  </AgentSection>
</Mission>
'''

# ========== DEFINICIÓN DE ESTADOS ==========
class State:
    """Estados del agente basados en el entorno"""
    SEARCHING = "searching"  # Buscando agua
    OBSTACLE_AHEAD = "obstacle_ahead"  # Obstáculo al frente
    DANGER_FALL = "danger_fall"  # Peligro de caída
    WATER_FOUND = "water_found"  # Agua encontrada
    
# ========== FUNCIÓN DE TRANSICIÓN DE ESTADO ==========
def get_state(obs):
    """
    Determina el estado actual basado en observaciones
    Retorna: (estado, sugerencia_direccion)
    """
    # Obtener información básica
    y_pos = obs.get("YPos", 64)
    x_pos = obs.get("XPos", 0)
    z_pos = obs.get("ZPos", 0)
    life = obs.get("Life", 20)
    
    # Verificar usando LineOfSight (método principal en mundo natural)
    los = obs.get("LineOfSight", {})
    if isinstance(los, dict):
        los_type = los.get("type", "")
        los_distance = los.get("distance", 100)
        
        water_blocks = ["water", "flowing_water", "stationary_water"]
        if los_type in water_blocks:
            print("🎯 ¡AGUA DETECTADA POR LINE OF SIGHT!")
            return State.WATER_FOUND, None
        
        # NO detectar abismos por "air" - permite bajar desniveles libremente
        # El agente puede caer hasta 5 bloques sin daño significativo
        
        # Detectar obstáculos INMEDIATOS que bloquean el movimiento
        # Incluir bloques de terreno para desniveles en mundo natural
        
        # Bloques sólidos que pueden ser obstáculos (incluye terreno)
        solid_blocks = ["stone", "dirt", "grass", "sand", "gravel", "log", "wood", 
                       "planks", "cobblestone", "bedrock", "sandstone", "clay"]
        
        # CLAVE: Solo considerar obstáculo si está MUY MUY cerca (< 1 bloque)
        # Esto evita detectar bloques lejanos en el suelo como obstáculos
        if los_type in solid_blocks and los_distance < 1.0:
            print(f"🚧 Obstáculo INMEDIATO: {los_type} a {los_distance:.2f}m - Saltando")
            return State.OBSTACLE_AHEAD, "jump"
        
        # IGNORAR estos bloques (decorativos, se atraviesan)
        passable_blocks = ["tallgrass", "leaves", "double_plant", "air", 
                          "yellow_flower", "red_flower", "deadbush", "sapling"]
        if los_type in passable_blocks:
            pass  # Se puede pasar a través
    
    # Detectar caídas PELIGROSAS (solo > 5 bloques)
    # Caídas pequeñas (1-5 bloques) son seguras en Minecraft
    # Usamos la vida para detectar daño por caída REAL, no anticipado
    if "IsAlive" in obs and obs.get("IsAlive") == True:
        # Solo considerar peligro si la vida está MUY baja (cayó mucho)
        if life < 15.0:  # Menos de 15 corazones = cayó mucho o está en combate
            print("⚠️ Vida CRÍTICA - posible caída grande o daño")
            return State.DANGER_FALL, "turn"
    
    # Siempre buscar (modo exploración activo - permite caídas pequeñas)
    return State.SEARCHING, "forward"

# ========== PROBABILIDAD DE ENCONTRAR OBJETIVO ==========
def calculate_water_probability(state, floor_blocks, feet_blocks):
    """
    Calcula probabilidad de encontrar agua según estado actual
    Retorna: dict con probabilidades por dirección
    """
    # Probabilidades uniformes (simplificado sin grid)
    probabilities = {
        "north": 0.25,
        "south": 0.25,
        "east": 0.25,
        "west": 0.25
    }
    
    # Reducir probabilidad si hay obstáculos
    if state == State.OBSTACLE_AHEAD:
        probabilities["north"] *= 0.1
    elif state == State.DANGER_FALL:
        probabilities["north"] *= 0.0
    
    # Normalizar probabilidades
    total = sum(probabilities.values())
    if total > 0:
        probabilities = {k: v/total for k, v in probabilities.items()}
    
    return probabilities

# ========== FUNCIÓN DE RECOMPENSA ==========
def calculate_reward(state, action, prev_state, total_steps):
    """sw
    Calcula recompensa para la función de valor Q
    """
    rewards = {
        State.WATER_FOUND: 100.0,      # Objetivo alcanzado
        State.SEARCHING: -1.0,          # Costo por paso
        State.OBSTACLE_AHEAD: -5.0,     # Penalización por obstáculo
        State.DANGER_FALL: -10.0,       # Penalización por peligro
    }
    
    base_reward = rewards.get(state, 0)
    
    # Penalización por tiempo
    time_penalty = -0.1 * (total_steps / 100)
    
    # Bonificación por progreso (cambio de estado searching a water_found)
    progress_bonus = 0
    if prev_state == State.SEARCHING and state == State.WATER_FOUND:
        progress_bonus = 50.0
    
    return base_reward + time_penalty + progress_bonus

# ========== FUNCIÓN DE SELECCIÓN DE ACCIÓN ==========
# Variables globales para estrategia de búsqueda en espiral
steps_in_direction = 0
steps_before_turn = 10  # Caminar más pasos en mundo natural (más disperso)
turns_made = 0
last_position = (0, 0, 0)
stuck_counter = 0
consecutive_turns = 0  # Contador de giros consecutivos sin avanzar

def select_action(state, direction_hint, probabilities, step_count, current_position):
    """
    Selecciona acción basada en estado con estrategia de búsqueda en espiral
    Usa comandos DISCRETOS para movimiento preciso
    """
    global steps_in_direction, steps_before_turn, turns_made, last_position, stuck_counter, consecutive_turns
    
    if state == State.WATER_FOUND:
        print("🎉 ¡MISIÓN COMPLETA! Agua encontrada en mundo natural")
        return "stop"
    
    # Detectar si está atascado (misma posición)
    distance_moved = ((current_position[0] - last_position[0])**2 + 
                     (current_position[2] - last_position[2])**2)**0.5
    
    if distance_moved < 0.2:  # Se movió menos de 0.2 bloques (básicamente inmóvil)
        stuck_counter += 1
        consecutive_turns += 1
        
        # Si lleva MUCHOS giros sin avanzar (más de 8), forzar movimiento adelante
        if consecutive_turns > 8:
            print(f"🚨 DEMASIADOS GIROS ({consecutive_turns})! Forzando movimiento hacia adelante...")
            consecutive_turns = 0
            stuck_counter = 0
            steps_in_direction = 0
            return "jumpmove 1"  # Intentar avanzar a la fuerza
        
        # ESTRATEGIA NORMAL: Girar cuando está atascado
        if stuck_counter >= 1:
            print(f"🔒 ATASCADO (inmóvil)! Girando 90° para buscar ruta libre...")
            stuck_counter = 0
            steps_in_direction = 0  # Reiniciar contador
            return "turn 1"  # GIRAR inmediatamente
    else:
        stuck_counter = 0  # Reset si se movió exitosamente
        consecutive_turns = 0  # Reset contador de giros si avanzó
    
    last_position = current_position
    
    # Si hay peligro, girar inmediatamente
    if state == State.DANGER_FALL:
        steps_in_direction = 0
        return "turn 1"
    
    # Si hay obstáculo CERCANO al frente, intentar saltar Y avanzar
    if state == State.OBSTACLE_AHEAD and direction_hint == "jump":
        print("⛰️ Obstáculo cercano - Saltando y avanzando...")
        return "jumpmove 1"
    
    # Estrategia de búsqueda en espiral/patrón
    if steps_in_direction >= steps_before_turn:
        # Es hora de girar según el patrón
        steps_in_direction = 0
        turns_made += 1
        
        # Cada 2 giros, aumentar la distancia antes de girar (espiral)
        if turns_made % 2 == 0:
            steps_before_turn += 4  # Incremento mayor para mundo natural
        
        # COMANDO DISCRETO: girar 90 grados a la derecha
        return "turn 1"
    else:
        # Continuar en la dirección actual - USAR JUMPMOVE para superar desniveles
        steps_in_direction += 1
        print(f"➡️ Avanzando con salto automático... (paso {steps_in_direction}/{steps_before_turn})")
        return "jumpmove 1"  # En vez de "move 1", usar "jumpmove 1" por defecto

# ========== INICIAR MISIÓN ==========
mission = Malmo.MissionSpec(missionXML, True)
mission_record = Malmo.MissionRecordSpec()

# Puerto por defecto de Minecraft Malmo es 10000
# Usar IP del adaptador WSL de Windows (vEthernet)
client_pool = Malmo.ClientPool()
client_pool.add(Malmo.ClientInfo("172.28.224.1", 10000))

print("Iniciando misión en MUNDO NORMAL...")
agent_host.startMission(mission, client_pool, mission_record, 0, "NavigatorBot")

print("Esperando cliente...")
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:", error.text)
print("\n¡Misión iniciada! 🚀 Explorando mundo natural...")

# ========== LOOP PRINCIPAL ==========
current_state = State.SEARCHING
previous_state = State.SEARCHING
total_reward = 0
step_count = 0
max_steps = 2000  # Más pasos para mundo natural (más grande y complejo)

while world_state.is_mission_running and step_count < max_steps:
    world_state = agent_host.getWorldState()
    
    for error in world_state.errors:
        print("Error:", error.text)
    
    # Procesar recompensas
    for reward in world_state.rewards:
        total_reward += reward.getValue()
        if reward.getValue() > 50:  # Solo mostrar recompensas grandes
            print(f"💰 ¡GRAN RECOMPENSA!: {reward.getValue()}")
    
    if world_state.number_of_observations_since_last_state > 0:
        obs_text = world_state.observations[-1].text
        obs = json.loads(obs_text)
        
        # Posición actual
        x = obs.get("XPos", 0)
        y = obs.get("YPos", 0)
        z = obs.get("ZPos", 0)
        yaw = obs.get("Yaw", 0)
        
        # Determinar estado
        previous_state = current_state
        current_state, direction_hint = get_state(obs)
        
        # Calcular probabilidades
        probabilities = calculate_water_probability(current_state, None, None)
        
        # Calcular recompensa
        step_reward = calculate_reward(current_state, None, previous_state, step_count)
        
        # Seleccionar acción con estrategia de espiral (pasando posición actual)
        current_position = (x, y, z)
        action = select_action(current_state, direction_hint, probabilities, step_count, current_position)
        
        # Mostrar información (cada 10 pasos para mejor seguimiento, o cuando hay eventos importantes)
        if step_count % 10 == 0 or current_state == State.WATER_FOUND or current_state == State.OBSTACLE_AHEAD or stuck_counter > 0:
            print(f"\n📍 Paso {step_count}")
            print(f"   Posición: ({x:.1f}, {y:.1f}, {z:.1f}) Yaw: {yaw:.1f}°")
            print(f"   Estado: {current_state}")
            print(f"   Vida: {obs.get('Life', 20):.1f}")
            print(f"   Pasos en dirección: {steps_in_direction}/{steps_before_turn}, Giros: {turns_made}")
            los_info = obs.get('LineOfSight', {})
            if isinstance(los_info, dict):
                los_type = los_info.get('type', 'N/A')
                los_dist = los_info.get('distance', 999)
                print(f"   LineOfSight: {los_type} (dist: {los_dist:.2f}m)")
            print(f"   Atascado: {stuck_counter}/2")
            print(f"   Acción: {action}")
            print(f"   Recompensa acumulada: {total_reward:.1f}")
        
        # Ejecutar acción
        if action == "stop":
            print("🛑 Deteniendo agente")
            break
        else:
            # Ejecutar comando discreto
            agent_host.sendCommand(action)
            time.sleep(0.6)  # Tiempo razonable para mundo natural
        
        step_count += 1
    
    time.sleep(0.1)

print(f"\n🏁 Misión terminada")
print(f"   Estados explorados: {step_count}")
print(f"   Recompensa total: {total_reward:.1f}")
print(f"   Estado final: {current_state}")
