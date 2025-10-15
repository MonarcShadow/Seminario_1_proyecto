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

# Mission XML con ORDEN CORRECTO de elementos
missionXML = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <About>
    <Summary>Navegacion con busqueda de agua</Summary>
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
      <!-- Mundo plano para evitar spawn bajo tierra -->
      <FlatWorldGenerator generatorString="3;7,2*3,2;1;"/>
      
      <!-- Crear área de juego: plataforma de spawn y agua -->
      <DrawingDecorator>
        <!-- Plataforma de spawn segura (césped) -->
        <DrawCuboid x1="-5" y1="3" z1="-5" x2="5" y2="3" z2="5" type="grass"/>
        
        <!-- Agua cerca para que el agente la encuentre -->
        <DrawCuboid x1="8" y1="3" z1="8" x2="15" y2="3" z2="15" type="water"/>
        <DrawCuboid x1="-15" y1="3" z1="-15" x2="-8" y2="3" z2="-8" type="water"/>
        
        <!-- Limpiar espacio arriba para evitar asfixia -->
        <DrawCuboid x1="-5" y1="4" z1="-5" x2="5" y2="10" z2="5" type="air"/>
      </DrawingDecorator>
      
      <ServerQuitWhenAnyAgentFinishes/>
    </ServerHandlers>
  </ServerSection>

  <AgentSection mode="Survival">
    <Name>Navigator</Name>
    <AgentStart>
      <Placement x="0.5" y="4" z="0.5" yaw="0"/>
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
      
      <!-- Comandos -->
      <ContinuousMovementCommands/>
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
    yaw = obs.get("Yaw", 0)
    life = obs.get("Life", 20)
    
    # Verificar si está en agua usando LineOfSight
    los = obs.get("LineOfSight", {})
    los_type = los.get("type", "") if isinstance(los, dict) else ""
    
    water_blocks = ["water", "flowing_water"]
    if los_type in water_blocks:
        return State.WATER_FOUND, None
    
    # Usar distancia y dirección para detectar peligros/obstáculos
    # (Simplificado sin grid - se basará más en movimiento aleatorio inteligente)
    
    # Si la vida bajó, probablemente cayó o hay peligro
    if life < 19:
        return State.DANGER_FALL, "turn"
    
    # Estado por defecto: buscando
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
    """
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
def select_action(state, direction_hint, probabilities):
    """
    Selecciona acción basada en estado y probabilidades
    """
    if state == State.WATER_FOUND:
        return "stop"
    
    if direction_hint == "turn":
        # Elegir dirección con mayor probabilidad
        best_direction = max(probabilities.items(), key=lambda x: x[1])[0]
        if best_direction == "east":
            return "turn 0.5"
        elif best_direction == "west":
            return "turn -0.5"
        else:
            return "turn 1.0"
    
    elif direction_hint == "jump":
        return "jump 1"
    
    elif direction_hint == "forward":
        return "move 1"
    
    return "move 0"

# ========== INICIAR MISIÓN ==========
mission = Malmo.MissionSpec(missionXML, True)
mission_record = Malmo.MissionRecordSpec()

# CORRECCIÓN: Puerto correcto es 10001
client_pool = Malmo.ClientPool()
client_pool.add(Malmo.ClientInfo("127.0.0.1", 10001))

print("Iniciando misión...")
agent_host.startMission(mission, client_pool, mission_record, 0, "NavigatorBot")

print("Esperando cliente...")
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:", error.text)
print("\n¡Misión iniciada! 🚀")

# ========== LOOP PRINCIPAL ==========
current_state = State.SEARCHING
previous_state = State.SEARCHING
total_reward = 0
step_count = 0
max_steps = 500

while world_state.is_mission_running and step_count < max_steps:
    world_state = agent_host.getWorldState()
    
    for error in world_state.errors:
        print("Error:", error.text)
    
    # Procesar recompensas
    for reward in world_state.rewards:
        total_reward += reward.getValue()
        print(f"💰 Recompensa recibida: {reward.getValue()}")
    
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
        
        # Seleccionar acción
        action = select_action(current_state, direction_hint, probabilities)
        
        # Mostrar información
        print(f"\n📍 Paso {step_count}")
        print(f"   Posición: ({x:.1f}, {y:.1f}, {z:.1f}) Yaw: {yaw:.1f}°")
        print(f"   Estado: {current_state}")
        print(f"   Vida: {obs.get('Life', 20):.1f}")
        print(f"   Probabilidades: N:{probabilities['north']:.2f} S:{probabilities['south']:.2f} "
              f"E:{probabilities['east']:.2f} W:{probabilities['west']:.2f}")
        print(f"   Acción: {action}")
        print(f"   Recompensa acumulada: {total_reward:.1f}")
        
        # Ejecutar acción
        if action != "stop":
            agent_host.sendCommand(action)
            time.sleep(0.5)
        
        step_count += 1
    
    time.sleep(0.1)

print(f"\n🏁 Misión terminada")
print(f"   Estados explorados: {step_count}")
print(f"   Recompensa total: {total_reward:.1f}")
print(f"   Estado final: {current_state}")
