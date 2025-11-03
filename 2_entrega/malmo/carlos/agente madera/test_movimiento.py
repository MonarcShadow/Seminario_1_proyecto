"""
Script de prueba para verificar que los comandos de movimiento funcionan
"""

import sys
import time
import MalmoPython as Malmo
import os


def cargar_configuracion():
    """Carga configuración desde .config"""
    config = {'ip': '127.0.0.1', 'puerto': 10001, 'seed': "12asdasd3456"}
    
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
        print(f"✓ Config: IP={config['ip']}, Puerto={config['puerto']}, Seed={config['seed']}")
    except:
        print("⚠ Usando config por defecto")
    
    return config


def obtener_mision_xml_simple():
    """Genera XML con mundo plano para pruebas seguras"""
    return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <About>
    <Summary>Prueba de Movimiento - Mundo Plano</Summary>
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
      <!-- Mundo plano para evitar caídas o sofocación -->
      <FlatWorldGenerator generatorString="3;7,2*3,2;1;village"/>
      <ServerQuitFromTimeUp timeLimitMs="60000"/>
    </ServerHandlers>
  </ServerSection>

  <AgentSection mode="Survival">
    <Name>TestAgent</Name>
    <AgentStart>
      <!-- Spawn en Y=4 (sobre el pasto del mundo plano) -->
      <Placement x="0.5" y="4" z="0.5" pitch="0" yaw="0"/>
    </AgentStart>
    <AgentHandlers>
      <ObservationFromFullStats/>
      <ObservationFromGrid>
        <Grid name="floor3x3">
          <min x="-1" y="-1" z="-1"/>
          <max x="1" y="-1" z="1"/>
        </Grid>
      </ObservationFromGrid>
      <DiscreteMovementCommands/>
    </AgentHandlers>
  </AgentSection>
</Mission>
'''


def probar_movimientos():
    """Prueba secuencial de comandos"""
    print("\n" + "="*60)
    print("🧪 PRUEBA DE MOVIMIENTOS - AGENTE MADERA")
    print("="*60)
    
    # Cargar configuración
    config = cargar_configuracion()
    
    # Inicializar Malmo
    agent_host = Malmo.AgentHost()
    
    # Configurar conexión
    client_pool = Malmo.ClientPool()
    client_pool.add(Malmo.ClientInfo(config['ip'], config['puerto']))
    
    # Crear misión (mundo plano)
    mision_xml = obtener_mision_xml_simple()
    mission = Malmo.MissionSpec(mision_xml, True)
    mission_record = Malmo.MissionRecordSpec()
    
    # Iniciar misión
    print("\n📡 Iniciando misión de prueba...")
    try:
        agent_host.startMission(mission, client_pool, mission_record, 0, "TestMovimiento")
    except Exception as e:
        print(f"❌ Error al iniciar: {e}")
        return
    
    # Esperar inicio
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
    
    print("✓ Misión iniciada\n")
    
    # Secuencia de prueba
    comandos = [
        ("move 1", "Avanzar", 1.0),
        ("turn 1", "Girar derecha", 1.0),
        ("move 1", "Avanzar", 1.0),
        ("turn -1", "Girar izquierda", 1.0),
        ("jumpmove 1", "Saltar y avanzar", 1.0),
        ("attack 1", "Atacar", 0.5),
    ]
    
    print("🎮 Ejecutando secuencia de comandos:\n")
    
    for i, (comando, descripcion, duracion) in enumerate(comandos, 1):
        print(f"{i}. {descripcion:20s} [{comando}]", end=" ")
        
        # Enviar comando
        agent_host.sendCommand(comando)
        time.sleep(duracion)
        
        # Obtener posición
        world_state = agent_host.getWorldState()
        if world_state.number_of_observations_since_last_state > 0:
            import json
            obs_text = world_state.observations[-1].text
            obs = json.loads(obs_text)
            x = obs.get("XPos", 0)
            y = obs.get("YPos", 0)
            z = obs.get("ZPos", 0)
            yaw = obs.get("Yaw", 0)
            pitch = obs.get("Pitch", 0)
            print(f"→ Pos: ({x:.1f}, {y:.1f}, {z:.1f}) | Yaw: {yaw:.0f}° | Pitch: {pitch:.0f}°")
        else:
            print("→ Sin observaciones")
        
        time.sleep(0.5)
    
    print("\n✅ Prueba completada")
    print("\n💡 Verifica en Minecraft:")
    print("   - ¿El agente se movió hacia adelante?")
    print("   - ¿Giró correctamente?")
    print("   - ¿El pitch está en 0° (mirando al frente)?")
    print("   - ¿El jumpmove lo hizo saltar y avanzar?")
    
    # Esperar antes de salir
    time.sleep(3)


if __name__ == "__main__":
    print("Python version:", sys.version)
    
    try:
        probar_movimientos()
    except KeyboardInterrupt:
        print("\n\n⚠ Prueba interrumpida")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
