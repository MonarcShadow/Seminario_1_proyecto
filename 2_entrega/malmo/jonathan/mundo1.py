import sys, time
import MalmoPython as Malmo

print(f"Python version: {sys.version}")
print("MalmoPython importado correctamente")

agent_host = Malmo.AgentHost()

missionXML = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <About>
    <Summary>Plano con stats, raycast y rejilla</Summary>
  </About>

  <ServerSection>
    <ServerInitialConditions>
      <Time>
        <StartTime>1000</StartTime>
        <AllowPassageOfTime>true</AllowPassageOfTime>
      </Time>
      <!-- Opcional: clima despejado y día fijo -->
      <!-- <Weather>clear</Weather> -->
    </ServerInitialConditions>
    <ServerHandlers>
      <!-- Mundo superplano (3;7,2;1;) = bedrock capa 0, 2 capas de dirt, césped arriba -->
      <FlatWorldGenerator generatorString="3;7,2;1;"/>
      <DrawingDecorator>
        <!-- Bloque objetivo visible al frente -->
        <DrawBlock x="3" y="5" z="0" type="diamond_block"/>
      </DrawingDecorator>
      <ServerQuitWhenAnyAgentFinishes/>
    </ServerHandlers>
  </ServerSection>

  <AgentSection mode="Survival">
    <Name>Inspector</Name>
    <AgentStart>
      <!-- Arranca un poco elevado sobre el suelo -->
      <Placement x="0.5" y="5" z="0.5" yaw="90"/>
    </AgentStart>
    <AgentHandlers>
      <!-- Posición y orientación (XPos, YPos, ZPos, Yaw, Pitch, etc.) -->
      <ObservationFromFullStats/>

      <!-- Rejilla de 5x3x5 centrada en el agente: desde y-1 a y+1 y radio 2 en X/Z -->
      <ObservationFromGrid>
        <Grid name="near5x3x5">
          <min x="-2" y="-1" z="-2"/>
          <max x="2"  y="1"  z="2"/>
        </Grid>
      </ObservationFromGrid>

      <!-- Raycast para el bloque que mira (LineOfSight con tipo y coordenadas) -->
      <ObservationFromRay/>

      <!-- Movimiento continuo para probar -->
      <ContinuousMovementCommands/>

      <!-- Finaliza al tocar el bloque de diamante -->
      <AgentQuitFromTouchingBlockType>
        <Block type="diamond_block"/>
      </AgentQuitFromTouchingBlockType>
    </AgentHandlers>
  </AgentSection>
</Mission>
'''

mission = Malmo.MissionSpec(missionXML, True)
mission_record = Malmo.MissionRecordSpec()

# 🔹 Indicar el cliente (IP de Windows)
client_pool = Malmo.ClientPool()
client_pool.add(Malmo.ClientInfo("127.0.0.1", 10001))  # Cambia por tu IP real

print("Iniciando misión...")
agent_host.startMission(mission, client_pool, mission_record, 0, "CarlosBot")

print("Esperando cliente...")
world_state = agent_host.getWorldState()
#print("Tipo de world_state:", type(world_state))
#print("Atributos:", dir(world_state))

while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:", error.text)
print("\n¡Misión iniciada! 🚀")


for _ in range(100):
    agent_host.sendCommand("move 1")
    agent_host.sendCommand("jump 1")
    time.sleep(0.1)
agent_host.sendCommand("move 0")
agent_host.sendCommand("jump 0")
print("Tipo de world_state:", type(world_state))
print("Atributos:", dir(world_state))
print("Misión terminada.")
