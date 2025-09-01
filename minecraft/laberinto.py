import malmo.MalmoPython as Malmo
import time

mission_xml = open("laberinto.xml", "r").read()
agent_host = Malmo.AgentHost()

mission = Malmo.MissionSpec(mission_xml, True)
mission_record = Malmo.MissionRecordSpec()

# Iniciar misión
agent_host.startMission(mission, mission_record)

print("Esperando a que inicie la misión...")
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
print("¡Misión iniciada!")

# Mover el agente en el laberinto
agent_host.sendCommand("move 1")
agent_host.sendCommand("turn 1")
time.sleep(2)
agent_host.sendCommand("move 1")
