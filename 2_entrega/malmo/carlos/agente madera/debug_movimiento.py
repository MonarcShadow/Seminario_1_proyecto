"""
Debug detallado para diagnosticar por qué el agente no se mueve
"""

import sys
import time
import json
sys.path.insert(0, '/home/carlos/MalmoPlatform/Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6/Python_Examples')
import MalmoPython as Malmo


def obtener_mision_xml_debug():
    """XML simplificado para debug"""
    return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <About>
    <Summary>Debug - Movimiento Básico</Summary>
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
      <FlatWorldGenerator generatorString="3;7,2*3,2;1;"/>
      <ServerQuitFromTimeUp timeLimitMs="30000"/>
    </ServerHandlers>
  </ServerSection>

  <AgentSection mode="Survival">
    <Name>DebugAgent</Name>
    <AgentStart>
      <Placement x="0.5" y="4" z="0.5" pitch="0" yaw="0"/>
    </AgentStart>
    <AgentHandlers>
      <ObservationFromFullStats/>
      <ObservationFromGrid>
        <Grid name="near3x3x3">
          <min x="-1" y="-1" z="-1"/>
          <max x="1" y="1" z="1"/>
        </Grid>
      </ObservationFromGrid>
      <DiscreteMovementCommands/>
    </AgentHandlers>
  </AgentSection>
</Mission>
'''


def ejecutar_comando_debug(agent_host, comando, duracion=0.5):
    """Ejecuta comando y muestra estado detallado"""
    print(f"\n📤 Enviando: {comando}")
    
    # Posición ANTES
    x_antes, z_antes, yaw_antes, pitch_antes = 0, 0, 0, 0
    world_state = agent_host.getWorldState()
    if world_state.number_of_observations_since_last_state > 0:
        obs = json.loads(world_state.observations[-1].text)
        x_antes = obs.get("XPos", 0)
        z_antes = obs.get("ZPos", 0)
        yaw_antes = obs.get("Yaw", 0)
        pitch_antes = obs.get("Pitch", 0)
        print(f"  ANTES: X={x_antes:.2f}, Z={z_antes:.2f}, Yaw={yaw_antes:.1f}°, Pitch={pitch_antes:.1f}°")
    else:
        print("  ANTES: Sin observaciones disponibles")
    
    # EJECUTAR
    agent_host.sendCommand(comando)
    time.sleep(duracion)
    
    # Posición DESPUÉS
    world_state = agent_host.getWorldState()
    for _ in range(5):  # Reintentar si no hay observación
        if world_state.number_of_observations_since_last_state > 0:
            break
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
    
    if world_state.number_of_observations_since_last_state > 0:
        obs = json.loads(world_state.observations[-1].text)
        x_despues = obs.get("XPos", 0)
        z_despues = obs.get("ZPos", 0)
        yaw_despues = obs.get("Yaw", 0)
        pitch_despues = obs.get("Pitch", 0)
        
        # Calcular cambios
        dx = x_despues - x_antes
        dz = z_despues - z_antes
        distancia = (dx**2 + dz**2)**0.5
        
        print(f"  DESPUÉS: X={x_despues:.2f}, Z={z_despues:.2f}, Yaw={yaw_despues:.1f}°, Pitch={pitch_despues:.1f}°")
        print(f"  CAMBIO: ΔX={dx:.3f}, ΔZ={dz:.3f}, Distancia={distancia:.3f}")
        
        # Grid
        grid = obs.get("near3x3x3", [])
        if len(grid) == 27:
            print(f"  GRID: {grid[13]} (abajo), {grid[14]} (centro), {grid[16]} (frente)")
        
        if distancia < 0.01 and "move" in comando:
            print("  ⚠️ NO SE MOVIÓ!")
        elif distancia > 0:
            print(f"  ✅ Se movió {distancia:.3f} bloques")
    else:
        print("  ❌ Sin observaciones")


def main():
    print("\n" + "="*60)
    print("🔍 DEBUG DETALLADO - SISTEMA DE MOVIMIENTO")
    print("="*60)
    
    # Configurar Malmo
    agent_host = Malmo.AgentHost()
    client_pool = Malmo.ClientPool()
    client_pool.add(Malmo.ClientInfo("127.0.0.1", 10001))
    
    # Crear misión
    mission = Malmo.MissionSpec(obtener_mision_xml_debug(), True)
    mission_record = Malmo.MissionRecordSpec()
    
    # Iniciar
    print("\n📡 Iniciando misión...")
    agent_host.startMission(mission, client_pool, mission_record, 0, "Debug")
    
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
    
    print("✓ Misión iniciada")
    time.sleep(1)
    
    # Pruebas
    print("\n" + "="*60)
    print("🧪 PRUEBA 1: Movimiento básico con diferentes duraciones")
    print("="*60)
    
    print("\n--- Intento 1: duracion=0.5 (estándar) ---")
    ejecutar_comando_debug(agent_host, "move 1", duracion=0.5)
    
    print("\n--- Intento 2: duracion=0.1 (rápido, como en entrenamiento) ---")
    ejecutar_comando_debug(agent_host, "move 1", duracion=0.1)
    
    print("\n--- Intento 3: duracion=1.0 (lento, como test_movimiento) ---")
    ejecutar_comando_debug(agent_host, "move 1", duracion=1.0)
    
    print("\n" + "="*60)
    print("🧪 PRUEBA 2: Girar y avanzar")
    print("="*60)
    
    ejecutar_comando_debug(agent_host, "turn 1", duracion=0.5)
    ejecutar_comando_debug(agent_host, "move 1", duracion=0.5)
    
    print("\n" + "="*60)
    print("🧪 PRUEBA 3: Jumpmove")
    print("="*60)
    
    ejecutar_comando_debug(agent_host, "jumpmove 1", duracion=0.5)
    
    print("\n" + "="*60)
    print("✅ Debug completado")
    print("="*60)
    
    time.sleep(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
