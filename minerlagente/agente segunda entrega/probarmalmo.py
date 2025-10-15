import sys, time
import MalmoPython as Malmo

print(f"Python version: {sys.version}")
print("MalmoPython importado correctamente")

agent_host = Malmo.AgentHost()

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
        <DrawBlock x="-2" y="5" z="0" type="diamond_block"/>
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


for _ in range(50):
    agent_host.sendCommand("move 1")
    agent_host.sendCommand("jump 1")
    time.sleep(0.1)
agent_host.sendCommand("move 0")
agent_host.sendCommand("jump 0")
print("Tipo de world_state:", type(world_state))
print("Atributos:", dir(world_state))
print("Misión terminada.")
