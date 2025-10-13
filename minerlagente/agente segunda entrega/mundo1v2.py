import sys
import time
import json
import MalmoPython as Malmo
from collections import Counter

print(f"Python version: {sys.version}")
print("MalmoPython importado correctamente")

# Crear el agente host
agent_host = Malmo.AgentHost()

# Mission XML
missionXML = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <About>
    <Summary>Plano con stats, raycast, rejilla e inventario</Summary>
  </About>

  <ServerSection>
    <ServerInitialConditions>
      <Time>
        <StartTime>1000</StartTime>
        <AllowPassageOfTime>true</AllowPassageOfTime>
      </Time>
      <!-- <Weather>clear</Weather> -->
    </ServerInitialConditions>
    <ServerHandlers>
      <!-- Superplano: bedrock (y=0), dirt x2, grass -->
      <FlatWorldGenerator generatorString="3;7,2;1;"/>
      <DrawingDecorator>
        <DrawBlock x="3" y="5" z="0" type="diamond_block"/>
      </DrawingDecorator>
      <ServerQuitWhenAnyAgentFinishes/>
    </ServerHandlers>
  </ServerSection>

  <AgentSection mode="Survival">
    <Name>Inspector</Name>
    <AgentStart>
      <Placement x="0.5" y="5" z="0.5" yaw="90"/>
    </AgentStart>
    <AgentHandlers>
      <!-- Posición y orientación -->
      <ObservationFromFullStats/>
      <!-- Inventario del jugador -->
      <ObservationFromFullInventory/>
      <!-- Rejilla de bloques alrededor (5x3x5) -->
      <ObservationFromGrid>
        <Grid name="near5x3x5">
          <min x="-2" y="-1" z="-2"/>
          <max x="2"  y="1"  z="2"/>
        </Grid>
      </ObservationFromGrid>
      <!-- Raycast del bloque en mira -->
      <ObservationFromRay/>
      <!-- Comandos de movimiento continuo -->
      <ContinuousMovementCommands/>
      <!-- Termina al tocar el bloque objetivo -->
      <AgentQuitFromTouchingBlockType>
        <Block type="diamond_block"/>
      </AgentQuitFromTouchingBlockType>
    </AgentHandlers>
  </AgentSection>
</Mission>
'''

mission = Malmo.MissionSpec(missionXML, True)
mission_record = Malmo.MissionRecordSpec()

# Cliente
client_pool = Malmo.ClientPool()
client_pool.add(Malmo.ClientInfo("127.0.0.1", 10001))  # Cambia si corresponde

print("Iniciando misión...")
agent_host.startMission(mission, client_pool, mission_record, 0, "CarlosBot")

print("Esperando cliente...")
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:", error.text)
print("\n¡Misión iniciada! 🚀")

# Ejemplo: no moverse, solo observar por ~5 segundos
start_time = time.time()
while world_state.is_mission_running and (time.time() - start_time) < 5.0:
    world_state = agent_host.getWorldState()

    # Imprime errores si aparecen
    for error in world_state.errors:
        print("Error:", error.text)

    # Procesa nuevas observaciones
    if world_state.number_of_observations_since_last_state > 0:
        obs_text = world_state.observations[-1].text
        obs = json.loads(obs_text)

        # Posición y orientación (ObservationFromFullStats)
        x = obs.get("XPos")
        y = obs.get("YPos")
        z = obs.get("ZPos")
        yaw = obs.get("Yaw")
        pitch = obs.get("Pitch")
        if x is not None and y is not None and z is not None:
            print(f"Posición: ({x:.2f}, {y:.2f}, {z:.2f})  Yaw: {yaw:.1f}  Pitch: {pitch:.1f}")

        # Bloque mirado (ObservationFromRay)
        los = obs.get("LineOfSight")
        if los:
            los_type = los.get("type")
            lx, ly, lz = los.get("x"), los.get("y"), los.get("z")
            hitType = los.get("hitType")  # 'block' o 'entity' según schema
            print(f"Mirando: {hitType} '{los_type}' en ({lx}, {ly}, {lz})")

        # Rejilla de bloques alrededor (ObservationFromGrid)
        grid = obs.get("near5x3x5")
        if grid:
            counts = Counter(grid)
            # Muestra los 5 tipos más frecuentes
            print("Bloques cercanos (top 5):", counts.most_common(5))

        # Inventario (ObservationFromInventory)
        inv = obs.get("inventory")
        if inv:
            # inv suele ser lista de objetos con 'slot', 'type', 'quantity'
            occupied = []
            for it in inv:
                slot = it.get("slot")
                btype = it.get("type")
                qty = it.get("quantity")
                if btype and btype not in ("air", "empty"):
                    occupied.append((slot, btype, qty))
            print("Inventario (ocupado, primeros 10):", occupied[:10])

    time.sleep(0.1)

print("Misión terminada.")
