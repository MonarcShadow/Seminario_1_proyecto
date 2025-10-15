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
        <!-- Plataforma grande de césped para que el agente explore -->
        <DrawCuboid x1="-20" y1="3" z1="-20" x2="20" y2="3" z2="20" type="grass"/>
        
        <!-- Agua cerca para que el agente la encuentre -->
        <DrawCuboid x1="10" y1="3" z1="10" x2="15" y2="3" z2="15" type="water"/>
        <DrawCuboid x1="-15" y1="3" z1="-15" x2="-10" y2="3" z2="-10" type="water"/>
        
        <!-- Limpiar espacio arriba -->
        <DrawCuboid x1="-20" y1="4" z1="-20" x2="20" y2="10" z2="20" type="air"/>
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
    y_pos = obs.get("YPos", 4)
    x_pos = obs.get("XPos", 0)
    z_pos = obs.get("ZPos", 0)
    
    # Verificar si está en agua por posición
    # El agua está en (10-15, 3, 10-15) o (-15--10, 3, -15--10)
    agua_zona1 = 10 <= x_pos <= 15 and 10 <= z_pos <= 15
    agua_zona2 = -15 <= x_pos <= -10 and -15 <= z_pos <= -10
    
    if agua_zona1 or agua_zona2:
        print("🎯 ¡AGUA DETECTADA POR POSICIÓN!")
        return State.WATER_FOUND, None
    
    # Verificar usando LineOfSight
    los = obs.get("LineOfSight", {})
    if isinstance(los, dict):
        los_type = los.get("type", "")
        water_blocks = ["water", "flowing_water", "stationary_water"]
        if los_type in water_blocks:
            print("🎯 ¡AGUA DETECTADA POR LINE OF SIGHT!")
            return State.WATER_FOUND, None
    
    # Siempre buscar (modo exploración activo)
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
# Variables globales para estrategia de búsqueda en espiral
steps_in_direction = 0
steps_before_turn = 8  # Caminar 8 pasos antes de girar
turns_made = 0

def select_action(state, direction_hint, probabilities, step_count):
    """
    Selecciona acción basada en estado con estrategia de búsqueda en espiral
    Usa comandos DISCRETOS para movimiento preciso
    """
    global steps_in_direction, steps_before_turn, turns_made
    
    if state == State.WATER_FOUND:
        print("🎉 ¡MISIÓN COMPLETA! Agua encontrada")
        return "stop"
    
    # Estrategia de búsqueda en espiral/patrón
    if steps_in_direction >= steps_before_turn:
        # Es hora de girar
        steps_in_direction = 0
        turns_made += 1
        
        # Cada 2 giros, aumentar la distancia antes de girar (espiral)
        if turns_made % 2 == 0:
            steps_before_turn += 3
        
        # COMANDO DISCRETO: girar 90 grados a la derecha
        return "turn 1"
    else:
        # Continuar en la dirección actual
        steps_in_direction += 1
        # COMANDO DISCRETO: mover 1 bloque hacia adelante
        return "move 1"

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
max_steps = 1000  # Aumentado para dar más tiempo de exploración

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
        
        # Seleccionar acción con estrategia de espiral
        action = select_action(current_state, direction_hint, probabilities, step_count)
        
        # Mostrar información (cada 5 pasos para mejor seguimiento)
        if step_count % 5 == 0 or current_state == State.WATER_FOUND:
            print(f"\n📍 Paso {step_count}")
            print(f"   Posición: ({x:.1f}, {y:.1f}, {z:.1f}) Yaw: {yaw:.1f}°")
            print(f"   Estado: {current_state}")
            print(f"   Vida: {obs.get('Life', 20):.1f}")
            print(f"   Pasos en dirección: {steps_in_direction}/{steps_before_turn}, Giros: {turns_made}")
            print(f"   Comando: '{action}'")
            print(f"   Recompensa acumulada: {total_reward:.1f}")
        
        # Ejecutar acción
        if action == "stop":
            print("🛑 Deteniendo agente")
            break
        else:
            # Ejecutar comando discreto
            print(f"   ➤ Enviando: {action}", end="")
            agent_host.sendCommand(action)
            print(" ✓")
            time.sleep(0.8)  # Más tiempo para completar movimiento discreto
        
        step_count += 1
    
    time.sleep(0.1)

print(f"\n🏁 Misión terminada")
print(f"   Estados explorados: {step_count}")
print(f"   Recompensa total: {total_reward:.1f}")
print(f"   Estado final: {current_state}")
