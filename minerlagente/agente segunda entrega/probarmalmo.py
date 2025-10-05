import MalmoPython as Malmo
import time

# Crear el agente
agent_host = Malmo.AgentHost()

# Definir una misión mínima en XML
missionXML = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

  <About>
    <Summary>Prueba Malmo</Summary>
  </About>

  <ServerSection>
    <ServerInitialConditions>
      <Time>
        <StartTime>1000</StartTime>
        <AllowPassageOfTime>true</AllowPassageOfTime>
      </Time>
    </ServerInitialConditions>
    <ServerHandlers>
      <FlatWorldGenerator generatorString="3;7,2;1;"/>
      <DrawingDecorator>
        <DrawBlock x="0" y="4" z="0" type="diamond_block"/>
      </DrawingDecorator>
      <ServerQuitWhenAnyAgentFinishes/>
    </ServerHandlers>
  </ServerSection>

  <AgentSection mode="Survival">
    <Name>CarlosBot</Name>
    <AgentStart>
      <Placement x="0.5" y="4" z="0.5" yaw="90"/>
    </AgentStart>
    <AgentHandlers>
      <ObservationFromFullStats/>
      <ContinuousMovementCommands/>
      <AgentQuitFromTouchingBlockType>
        <Block type="diamond_block"/>
      </AgentQuitFromTouchingBlockType>
    </AgentHandlers>
  </AgentSection>

</Mission>
'''

# Convertir a misión
mission = Malmo.MissionSpec(missionXML, True)
mission_record = Malmo.MissionRecordSpec()

# Iniciar misión
print("Iniciando misión...")
agent_host.startMission(mission, mission_record)

# Esperar a que se conecte el cliente de Minecraft
print("Esperando cliente...")
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    time.sleep(0.1)
    world_state = agent_host.getWorldState()

print("¡Misión iniciada! 🚀")

# Mandar comandos de movimiento
for _ in range(50):
    agent_host.sendCommand("move 1")   # Avanzar
    time.sleep(0.1)

print("Misión terminada.")
