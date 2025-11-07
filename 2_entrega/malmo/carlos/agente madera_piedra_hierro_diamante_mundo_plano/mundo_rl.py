"""
Generador de Mundo Plano Controlado para Entrenamiento
Coloca materiales (madera, piedra, hierro, diamante) en posiciones aleatorias
dentro de un área delimitada por muros de obsidiana

Autor: Sistema de IA
Fecha: Noviembre 2025
"""

import random
import MalmoPython
import json
import time
from agente_rl import AgenteQLearningProgresivo
from entorno_malmo import EntornoMalmoProgresivo
from config import crear_client_pool


def generar_mundo_plano_xml(seed=None):
    """
    Genera XML de misión con mundo plano controlado
    
    Características:
    - Mundo plano de piedra
    - Spawn en centro (0, 4, 0)
    - Área de 50x50 bloques delimitada por muro de obsidiana
    - Materiales distribuidos aleatoriamente:
      * 15-20 bloques de madera (oak, spruce)
      * 15-20 bloques de piedra/cobblestone
      * 8-12 menas de hierro
      * 3-5 menas de diamante
    - Algunos materiales en altura (torres de 1-3 bloques)
    
    Parámetros:
    -----------
    seed: int
        Semilla para generación aleatoria (reproducibilidad)
    
    Returns:
    --------
    str: XML de la misión
    """
    
    if seed is not None:
        random.seed(seed)
    
    # Configuración del área
    centro_x, centro_z = 0, 0
    radio = 25  # 50x50 área total
    
    # Listas para almacenar posiciones (evitar solapamiento)
    posiciones_usadas = set()
    
    # Generar posiciones para cada tipo de material
    bloques_madera = []
    bloques_piedra = []
    bloques_hierro = []
    bloques_diamante = []
    
    def pos_valida(x, z, min_dist_spawn=3):
        """Verifica si posición es válida (no usada, lejos del spawn)"""
        if (x, z) in posiciones_usadas:
            return False
        dist_spawn = (x**2 + z**2)**0.5
        if dist_spawn < min_dist_spawn:
            return False
        return True
    
    def generar_posicion_aleatoria():
        """Genera posición aleatoria dentro del área"""
        x = random.randint(-radio + 2, radio - 2)
        z = random.randint(-radio + 2, radio - 2)
        return x, z
    
    # 1. GENERAR MADERA (15-20 bloques)
    num_madera = random.randint(15, 20)
    # Solo usar 'log' (Oak) - es válido en el XML
    # Para variar, podemos usar log2 (Acacia/Dark Oak) también
    tipos_madera = ['log', 'log2']  # Oak y Acacia/Dark Oak
    
    for _ in range(num_madera):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                # Altura aleatoria (0-2 bloques arriba del suelo)
                altura = random.choice([0, 0, 0, 1, 1, 2])  # Más probable en suelo
                tipo = random.choice(tipos_madera)
                
                for h in range(altura + 1):
                    y = 4 + h
                    bloques_madera.append((x, y, z, tipo))
                
                posiciones_usadas.add((x, z))
                break
            intentos += 1
    
    # 2. GENERAR PIEDRA (15-20 bloques)
    num_piedra = random.randint(15, 20)
    tipos_piedra = ['stone', 'cobblestone']
    
    for _ in range(num_piedra):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                altura = random.choice([0, 0, 0, 1, 1, 2])
                tipo = random.choice(tipos_piedra)
                
                for h in range(altura + 1):
                    y = 4 + h
                    bloques_piedra.append((x, y, z, tipo))
                
                posiciones_usadas.add((x, z))
                break
            intentos += 1
    
    # 3. GENERAR HIERRO (8-12 bloques)
    num_hierro = random.randint(8, 12)
    
    for _ in range(num_hierro):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                altura = random.choice([0, 0, 1, 1, 2])
                
                for h in range(altura + 1):
                    y = 4 + h
                    bloques_hierro.append((x, y, z, 'iron_ore'))
                
                posiciones_usadas.add((x, z))
                break
            intentos += 1
    
    # 4. GENERAR DIAMANTE (3-5 bloques) - Más raros
    num_diamante = random.randint(3, 5)
    
    for _ in range(num_diamante):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z, min_dist_spawn=8):  # Más lejos del spawn
                altura = random.choice([0, 1, 1, 2])
                
                for h in range(altura + 1):
                    y = 4 + h
                    bloques_diamante.append((x, y, z, 'diamond_ore'))
                
                posiciones_usadas.add((x, z))
                break
            intentos += 1
    
    # Construir XML de DrawingDecorator
    drawing_xml = ""
    
    # Suelo de piedra (50x50)
    drawing_xml += f'<DrawCuboid x1="{-radio}" y1="3" z1="{-radio}" x2="{radio}" y2="3" z2="{radio}" type="stone"/>\n'
    
    # Muro de obsidiana perimetral (altura 1-10)
    # Muro Norte
    drawing_xml += f'<DrawCuboid x1="{-radio}" y1="4" z1="{-radio}" x2="{radio}" y2="10" z2="{-radio}" type="obsidian"/>\n'
    # Muro Sur
    drawing_xml += f'<DrawCuboid x1="{-radio}" y1="4" z1="{radio}" x2="{radio}" y2="10" z2="{radio}" type="obsidian"/>\n'
    # Muro Este
    drawing_xml += f'<DrawCuboid x1="{radio}" y1="4" z1="{-radio}" x2="{radio}" y2="10" z2="{radio}" type="obsidian"/>\n'
    # Muro Oeste
    drawing_xml += f'<DrawCuboid x1="{-radio}" y1="4" z1="{-radio}" x2="{-radio}" y2="10" z2="{radio}" type="obsidian"/>\n'
    
    # Colocar bloques de madera
    for x, y, z, tipo in bloques_madera:
        drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="{tipo}"/>\n'
    
    # Colocar bloques de piedra
    for x, y, z, tipo in bloques_piedra:
        drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="{tipo}"/>\n'
    
    # Colocar hierro
    for x, y, z, tipo in bloques_hierro:
        drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="{tipo}"/>\n'
    
    # Colocar diamante
    for x, y, z, tipo in bloques_diamante:
        drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="{tipo}"/>\n'
    
    # XML completo de la misión
    xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    
    <About>
        <Summary>Entorno Controlado - Progresión Multi-Material</Summary>
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
            <FlatWorldGenerator generatorString="3;7,2*3,2;1;" forceReset="true"/>
            
            <DrawingDecorator>
                {drawing_xml}
            </DrawingDecorator>
            
            <ServerQuitFromTimeUp timeLimitMs="120000"/>
            <ServerQuitWhenAnyAgentFinishes/>
        </ServerHandlers>
    </ServerSection>
    
    <AgentSection mode="Survival">
        <Name>Agente_Progresivo</Name>
        
        <AgentStart>
            <Placement x="0.5" y="4.0" z="0.5" pitch="0" yaw="0"/>
            <Inventory>
            </Inventory>
        </AgentStart>
        
        <AgentHandlers>
            <ObservationFromFullStats/>
            <ObservationFromFullInventory/>
            <ObservationFromGrid>
                <Grid name="floor3x3">
                    <min x="-2" y="-2" z="-2"/>
                    <max x="2" y="2" z="2"/>
                </Grid>
            </ObservationFromGrid>
            
            <ContinuousMovementCommands turnSpeedDegs="180"/>
            <InventoryCommands/>
            <ChatCommands/>
        </AgentHandlers>
    </AgentSection>
</Mission>'''
    
    # Estadísticas de generación
    print("\n" + "="*60)
    print("🗺️  MUNDO PLANO GENERADO")
    print("="*60)
    print(f"Área: {radio*2}x{radio*2} bloques")
    print(f"Spawn: (0, 4, 0)")
    print(f"\nMateriales colocados:")
    print(f"  🌲 Madera:   {len(set((x,z) for x,y,z,t in bloques_madera))} ubicaciones ({len(bloques_madera)} bloques)")
    print(f"  🪨 Piedra:   {len(set((x,z) for x,y,z,t in bloques_piedra))} ubicaciones ({len(bloques_piedra)} bloques)")
    print(f"  ⚙️  Hierro:   {len(set((x,z) for x,y,z,t in bloques_hierro))} ubicaciones ({len(bloques_hierro)} bloques)")
    print(f"  💎 Diamante: {len(set((x,z) for x,y,z,t in bloques_diamante))} ubicaciones ({len(bloques_diamante)} bloques)")
    print(f"\nSemilla: {seed if seed else 'aleatoria'}")
    print("="*60 + "\n")
    
    return xml


def ejecutar_episodio(agent_host, agente, entorno, episodio, seed=None):
    """
    Ejecuta un episodio completo de entrenamiento en mundo plano
    
    Returns:
    --------
    dict: Estadísticas del episodio
    """
    
    print(f"\n{'='*60}")
    print(f"EPISODIO {episodio}")
    print(f"{'='*60}\n")
    
    # Generar misión
    mission_xml = generar_mundo_plano_xml(seed=seed)
    mission = MalmoPython.MissionSpec(mission_xml, True)
    mission_record = MalmoPython.MissionRecordSpec()
    
    # Configurar cliente (Minecraft en Windows - ver config.py)
    client_pool = crear_client_pool()
    
    # Iniciar misión
    max_reintentos = 3
    for intento in range(max_reintentos):
        try:
            agent_host.startMission(mission, client_pool, mission_record, 0, f"RL_Progresivo_EP{episodio}")
            break
        except Exception as e:
            if intento == max_reintentos - 1:
                print(f"❌ Error al iniciar misión: {e}")
                return None
            print(f"⚠️  Reintentando... ({intento + 1}/{max_reintentos})")
            time.sleep(2)
    
    # Esperar inicio
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
    
    print("✓ Misión iniciada\n")
    time.sleep(2)
    
    # LIMPIAR INVENTARIO
    print("🧹 Limpiando inventario...")
    agent_host.sendCommand("chat /clear")
    time.sleep(0.5)
    
    # DAR PICO DE MADERA
    print("⛏️  Dando pico de madera inicial...")
    agent_host.sendCommand("chat /give @p wooden_pickaxe 1")
    time.sleep(0.5)
    
    # Resetear entorno
    entorno.reset_episodio()
    
    # Variables del episodio
    pasos = 0
    recompensa_acumulada = 0.0
    max_pasos = 2000  # ~16 minutos con 0.5s por paso
    objetivo_completado = False
    
    pasos_sin_movimiento_consecutivos = 0
    posicion_anterior = None
    
    # Loop principal
    print("🎮 Comenzando episodio...\n")
    
    while world_state.is_mission_running and pasos < max_pasos:
        # Esperar hasta tener observaciones
        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                break
        
        if not world_state.is_mission_running:
            break
            
        pasos += 1
        
        # Obtener observaciones
        msg = world_state.observations[-1].text
        obs = json.loads(msg)
        
        # Obtener fase actual
        fase_actual = entorno.fase_actual
        
        # Obtener estado
        estado = agente.obtener_estado_discretizado(obs, fase_actual)
        
        # Elegir acción
        accion = agente.elegir_accion(estado, fase_actual)
        
        # Ejecutar acción
        comando = agente.ACCIONES[accion]
        agent_host.sendCommand(comando)
        
        # Esperar a que se ejecute el comando
        time.sleep(0.5)
        
        # Obtener nueva observación después del comando
        world_state = agent_host.getWorldState()
        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                break
        
        if not world_state.is_mission_running:
            break
        
        # Procesar nueva observación
        msg = world_state.observations[-1].text
        obs_nueva = json.loads(msg)
        
        # Calcular recompensa
        recompensa = entorno.calcular_recompensa(obs_nueva, accion, fase_actual)
        recompensa_acumulada += recompensa
        
        # Obtener siguiente estado
        siguiente_estado = agente.obtener_estado_discretizado(obs_nueva, fase_actual)
        
        # Verificar progresión de fase
        cambio_fase = entorno.verificar_progresion_fase(obs_nueva)
        
        # Actualizar Q-table
        agente.actualizar_q(estado, accion, recompensa, siguiente_estado, fase_actual, done=False)
        
        # Verificar objetivo final completado
        if entorno.fase_actual == 3 and entorno.materiales_recolectados['diamante'] >= 1:
            objetivo_completado = True
            print("\n💎 ¡OBJETIVO FINAL ALCANZADO!")
            break
        
        # Anti-stuck más agresivo
        xpos = obs_nueva.get('XPos', 0)
        zpos = obs_nueva.get('ZPos', 0)
        pos_actual = (round(xpos, 1), round(zpos, 1))
        
        if posicion_anterior is not None:
            if pos_actual == posicion_anterior:
                pasos_sin_movimiento_consecutivos += 1
            else:
                pasos_sin_movimiento_consecutivos = 0
        
        posicion_anterior = pos_actual
        
        # Si está muy atascado, hacer acción aleatoria
        if pasos_sin_movimiento_consecutivos > 15:
            agent_host.sendCommand("turn 1")
            time.sleep(0.1)
            agent_host.sendCommand("jumpmove 1")
            time.sleep(0.2)
            pasos_sin_movimiento_consecutivos = 0
        
        # Mostrar progreso cada 50 pasos
        if pasos % 50 == 0:
            fase_num, fase_nombre = entorno.obtener_fase_actual()
            progreso = entorno.obtener_progreso()
            print(f"\n📊 Paso {pasos} | Fase: {fase_nombre} | Recompensa: {recompensa_acumulada:.1f}")
            print(f"   Progreso: M:{progreso['madera']} P:{progreso['piedra']} H:{progreso['hierro']} D:{progreso['diamante']}")
        
        # Verificar muerte
        if 'IsAlive' in obs_nueva and not obs_nueva['IsAlive']:
            print("\n💀 Agente murió")
            break
    
    # Fin del episodio - Esperar a que termine la misión
    print(f"\n{'='*60}")
    print(f"FIN EPISODIO {episodio}")
    print(f"{'='*60}")
    print(f"Pasos: {pasos}")
    print(f"Recompensa acumulada: {recompensa_acumulada:.2f}")
    print(f"Objetivo completado: {'✓ SÍ' if objetivo_completado else '✗ NO'}")
    
    progreso = entorno.obtener_progreso()
    print(f"\nProgreso final:")
    print(f"  🌲 Madera:   {progreso['madera']}")
    print(f"  🪨 Piedra:   {progreso['piedra']}")
    print(f"  ⚙️  Hierro:   {progreso['hierro']}")
    print(f"  💎 Diamante: {progreso['diamante']}")
    print(f"  Fase alcanzada: {entorno.FASES.get(entorno.fase_actual, 'DESCONOCIDO')}")
    print(f"{'='*60}\n")
    
    # Esperar a que la misión termine completamente
    print("⏳ Esperando fin de misión...")
    while world_state.is_mission_running:
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
    print("✓ Misión terminada\n")
    
    return {
        'episodio': episodio,
        'pasos': pasos,
        'recompensa': recompensa_acumulada,
        'objetivo_completado': objetivo_completado,
        'fase_final': entorno.fase_actual,
        'madera': entorno.materiales_recolectados['madera'],
        'piedra': entorno.materiales_recolectados['piedra'],
        'hierro': entorno.materiales_recolectados['hierro'],
        'diamante': entorno.materiales_recolectados['diamante'],
    }


def entrenar(num_episodios=100, guardar_cada=10, modelo_path='modelo_progresivo.pkl', seed=123456):
    """
    Función principal de entrenamiento
    
    Parámetros:
    -----------
    num_episodios: int
        Número de episodios de entrenamiento
    guardar_cada: int
        Guardar modelo cada N episodios
    modelo_path: str
        Ruta donde guardar el modelo
    seed: int
        Semilla para generación de mundo (reproducibilidad)
    """
    
    print("\n" + "="*70)
    print("🚀 ENTRENAMIENTO AGENTE PROGRESIVO")
    print("   Madera → Piedra → Hierro → Diamante")
    print("="*70)
    print(f"Episodios: {num_episodios}")
    print(f"Semilla: {seed}")
    print(f"Guardar cada: {guardar_cada} episodios")
    print("="*70 + "\n")
    
    # Inicializar Malmo
    agent_host = MalmoPython.AgentHost()
    try:
        agent_host.parse(sys.argv)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        print(agent_host.getUsage())
        exit(1)
    
    # Crear agente y entorno
    agente = AgenteQLearningProgresivo(
        alpha=0.1,
        gamma=0.95,
        epsilon=0.4,
        epsilon_min=0.05,
        epsilon_decay=0.995
    )
    
    entorno = EntornoMalmoProgresivo(agent_host)
    
    # Intentar cargar modelo existente
    agente.cargar_modelo(modelo_path)
    
    # Estadísticas de entrenamiento
    estadisticas = []
    exitos = 0
    
    # Loop de entrenamiento
    for episodio in range(1, num_episodios + 1):
        stats = ejecutar_episodio(agent_host, agente, entorno, episodio, seed=seed)
        
        if stats:
            estadisticas.append(stats)
            if stats['objetivo_completado']:
                exitos += 1
            
            # Decaer epsilon
            agente.decaer_epsilon()
            
            # Guardar modelo periódicamente
            if episodio % guardar_cada == 0:
                agente.guardar_modelo(modelo_path)
                print(f"\n💾 Modelo guardado en episodio {episodio}")
                print(f"   Tasa de éxito: {exitos}/{episodio} = {100*exitos/episodio:.1f}%")
                print(f"   Epsilon actual: {agente.epsilon:.4f}\n")
        
        time.sleep(2)
    
    # Guardar modelo final
    agente.guardar_modelo(modelo_path)
    
    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN DE ENTRENAMIENTO")
    print("="*70)
    print(f"Episodios completados: {len(estadisticas)}")
    print(f"Objetivos alcanzados: {exitos}")
    print(f"Tasa de éxito: {100*exitos/len(estadisticas):.1f}%")
    
    if estadisticas:
        recompensa_media = sum(s['recompensa'] for s in estadisticas) / len(estadisticas)
        pasos_medio = sum(s['pasos'] for s in estadisticas) / len(estadisticas)
        print(f"Recompensa media: {recompensa_media:.2f}")
        print(f"Pasos medio: {pasos_medio:.1f}")
    
    print("\nEstadísticas de Q-tables:")
    stats_q = agente.obtener_estadisticas()
    for fase, info in stats_q.items():
        print(f"  {fase}: {info['estados']} estados, {info['pares_estado_accion']} pares")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    # Parámetros por defecto
    num_eps = 100
    seed = 123456
    
    # Leer argumentos de línea de comandos
    if len(sys.argv) > 1:
        try:
            num_eps = int(sys.argv[1])
        except:
            pass
    
    if len(sys.argv) > 2:
        try:
            seed = int(sys.argv[2])
        except:
            pass
    
    entrenar(num_episodios=num_eps, guardar_cada=10, seed=seed)
