"""
Iron Pickaxe Crafting Agent - Stage 3
Usa un pico de piedra (stone pickaxe) para recolectar 3 iron ore y craftear un iron pickaxe.
Comienza con el inventario de un episodio exitoso de Stage 2.
Objetivo: Recolectar 3 iron ingots → Craftear iron pickaxe
Compatible con entrenamiento jerárquico: puede cargar modelos pre-entrenados de Stage 2.
"""

import os
import sys
import time
import json
import random
import argparse

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

from algorithms import QLearningAgent, SarsaAgent, ExpectedSarsaAgent, DoubleQLearningAgent, MonteCarloAgent, RandomAgent
from metrics import MetricsLogger

# Malmo setup
malmo_dir = os.environ.get('MALMO_DIR', '')
if malmo_dir:
    sys.path.append(os.path.join(malmo_dir, 'Python_Examples'))

try:
    import MalmoPython
except ImportError as e:
    print(f"Error importing MalmoPython: {e}")
    import traceback
    traceback.print_exc()
    print("Please check your MALMO_DIR environment variable and ensure dependencies are installed.")
    sys.exit(1)


def generar_mundo_completo_xml(seed=None):
    """
    Genera el drawing XML del mundo COMPLETO con TODOS los materiales.
    ESTA FUNCIÓN ES IDÉNTICA EN LOS 5 AGENTES.
    """
    rng = random.Random(seed) if seed is not None else random
    
    radio = 10
    posiciones_usadas = set()
    bloques_generados = []
    
    def pos_valida(x, z, min_dist_spawn=3):
        if (x, z) in posiciones_usadas:
            return False
        dist_spawn = (x**2 + z**2)**0.5
        if dist_spawn < min_dist_spawn:
            return False
        return True
    
    def generar_posicion_aleatoria():
        x = rng.randint(-radio + 2, radio - 2)
        z = rng.randint(-radio + 2, radio - 2)
        return x, z
    
    # 1. Wood blocks (40-60)
    num_madera = rng.randint(40, 60)
    for _ in range(num_madera):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                altura = rng.choice([0, 0, 1, 1, 2])
                tipo = "log"
                for h in range(altura + 1):
                    y = 4 + h
                    bloques_generados.append((x, y, z, tipo))
                posiciones_usadas.add((x, z))
                break
            intentos += 1
    
    # 2. Stone blocks (30-40)
    num_piedra = rng.randint(30, 40)
    for _ in range(num_piedra):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                bloques_generados.append((x, 4, z, "stone"))
                posiciones_usadas.add((x, z))
                break
            intentos += 1
    
    # 3. Iron ore (20-30) - Se puede minar con stone_pickaxe
    num_hierro = rng.randint(20, 30)
    for _ in range(num_hierro):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                bloques_generados.append((x, 4, z, "iron_ore"))  # ✅ CORRECTO
                posiciones_usadas.add((x, z))
                break
            intentos += 1

    
    # 4. Diamond ore (3-5 bloques)
    num_diamante = rng.randint(3, 5)
    for _ in range(num_diamante):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                bloques_generados.append((x, 4, z, "diamond_ore"))
                posiciones_usadas.add((x, z))
                break
            intentos += 1
    
    drawing_xml = ""
    
    # Piso de obsidian (y=3)
    drawing_xml += '<DrawCuboid x1="-10" y1="3" z1="-10" x2="10" y2="3" z2="10" type="obsidian"/>\n'
    
    # Paredes de obsidian
    drawing_xml += '<DrawCuboid x1="-10" y1="4" z1="-10" x2="-10" y2="10" z2="10" type="obsidian"/>\n'
    drawing_xml += '<DrawCuboid x1="10" y1="4" z1="-10" x2="10" y2="10" z2="10" type="obsidian"/>\n'
    drawing_xml += '<DrawCuboid x1="-10" y1="4" z1="-10" x2="10" y2="10" z2="-10" type="obsidian"/>\n'
    drawing_xml += '<DrawCuboid x1="-10" y1="4" z1="10" x2="10" y2="10" z2="10" type="obsidian"/>\n'
    
    # Dibujar todos los bloques
    for x, y, z, tipo in bloques_generados:
        drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="{tipo}"/>\n'
    
    return drawing_xml


def generar_mundo_xml(seed=None):
    """
    Genera el XML completo para iron_agent (Stage 3).
    Usa el mismo mundo que todos los demás agentes, solo cambia el inventario.
    """
    drawing_xml = generar_mundo_completo_xml(seed)
    
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary>Iron Pickaxe Crafting - Stage 3</Summary>
        </About>
        <ServerSection>
            <ServerInitialConditions>
                <Time>
                    <StartTime>6000</StartTime>
                    <AllowPassageOfTime>false</AllowPassageOfTime>
                </Time>
                <Weather>clear</Weather>
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
            <Name>IronGatherer</Name>
            <AgentStart>
                <Placement x="0.5" y="4" z="0.5" yaw="0"/>
                <Inventory>
                    <!-- Starting inventory from successful stone stage -->
                    <InventoryItem slot="0" type="diamond_axe"/>
                    <InventoryItem slot="1" type="planks" quantity="3"/>
                    <InventoryItem slot="2" type="wooden_pickaxe"/>
                    <InventoryItem slot="3" type="stone_pickaxe"/>
                </Inventory>
            </AgentStart>
            <AgentHandlers>
                <ObservationFromFullStats/>
                <ObservationFromGrid>
                    <Grid name="floor5x5">
                        <min x="-2" y="-1" z="-2"/>
                        <max x="2" y="-1" z="2"/>
                    </Grid>
                     <Grid name="surroundings5x5">
                        <min x="-2" y="0" z="-2"/>
                        <max x="2" y="2" z="2"/>
                    </Grid>
                </ObservationFromGrid>
                <ContinuousMovementCommands turnSpeedDegs="180"/>
                <DiscreteMovementCommands/>
                <InventoryCommands/>
                <SimpleCraftCommands/>
                <MissionQuitCommands/>
                <ObservationFromRecentCommands/>
                <ObservationFromHotBar/>
                <ObservationFromFullInventory/>
                <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="5" yrange="3" zrange="5"/>
                </ObservationFromNearbyEntities>
                <RewardForCollectingItem>
                    <Item reward="500" type="log"/>
                    <Item reward="1000" type="stone"/>
                    <Item reward="5000" type="iron_ingot"/>
                    <Item reward="10000" type="diamond"/>
                </RewardForCollectingItem>
                <RewardForTouchingBlockType>
                    <Block reward="-1" type="lava"/>
                    <Block reward="-100" type="obsidian"/>
                </RewardForTouchingBlockType>
            </AgentHandlers>
        </AgentSection>
    </Mission>'''


def get_state(world_state):
    """
    Enhanced state representation including inventory for Tech Tree
    Returns: (surroundings_tuple, wood_count, stone_count, iron_count, diamond_count,
              planks_count, sticks_count, has_wooden_pickaxe, has_stone_pickaxe, has_iron_pickaxe)
    
    10 elementos - DEBE SER IDÉNTICO entre todos los stages para compatibilidad .pkl
    """
    if not world_state.number_of_observations_since_last_state:
        return None
    
    msg = world_state.observations[-1].text
    obs = json.loads(msg)
    
    # Get surroundings (5x5 grid)
    surroundings = tuple(obs.get("surroundings5x5", []))
    
    # Count inventory items
    wood_count = 0
    stone_count = 0
    iron_count = 0
    diamond_count = 0
    planks_count = 0
    sticks_count = 0
    has_wooden_pickaxe = False
    has_stone_pickaxe = False
    has_iron_pickaxe = False
    
    # Method 1: Check flat inventory structure
    for i in range(45):
        item_key = f"InventorySlot_{i}_item"
        size_key = f"InventorySlot_{i}_size"
        
        if item_key in obs:
            item_type = obs[item_key]
            quantity = obs.get(size_key, 1)
            
            if item_type == "log":
                wood_count += quantity
            elif item_type == "stone":
                stone_count += quantity
            elif item_type in ["iron_ore", "iron_ingot", "iron_block"]:
                iron_count += quantity
            elif item_type == "diamond":
                diamond_count += quantity
            elif item_type == "planks":
                planks_count += quantity
            elif item_type == "stick":
                sticks_count += quantity
            elif item_type == "wooden_pickaxe":
                has_wooden_pickaxe = True
            elif item_type == "stone_pickaxe":
                has_stone_pickaxe = True
            elif item_type == "iron_pickaxe":
                has_iron_pickaxe = True
    
    # Method 2: Also check list format (backup)
    if "inventory" in obs:
        for item in obs["inventory"]:
            item_type = item.get("type", "")
            quantity = item.get("quantity", 0)
            
            if item_type == "log":
                wood_count += quantity
            elif item_type == "stone":
                stone_count += quantity
            elif item_type in ["iron_ore", "iron_ingot", "iron_block"]:
                iron_count += quantity
            elif item_type == "diamond":
                diamond_count += quantity
            elif item_type == "planks":
                planks_count += quantity
            elif item_type == "stick":
                sticks_count += quantity
            elif item_type == "wooden_pickaxe":
                has_wooden_pickaxe = True
            elif item_type == "stone_pickaxe":
                has_stone_pickaxe = True
            elif item_type == "iron_pickaxe":
                has_iron_pickaxe = True
    
    return (surroundings, wood_count, stone_count, iron_count, diamond_count,
            planks_count, sticks_count, has_wooden_pickaxe, has_stone_pickaxe, has_iron_pickaxe)


def auto_select_tool(world_state, agent_host):
    """
    Automatically selects the optimal tool based on the block in front.
    Stage 3 (Iron): Uses stone_pickaxe for iron_block
    """
    if world_state.number_of_observations_since_last_state > 0:
        try:
            obs = json.loads(world_state.observations[-1].text)
            surroundings = obs.get("surroundings5x5", [])
            
            if len(surroundings) > 37:
                front_block = surroundings[37]
                
                # Stage 3: Select stone_pickaxe for iron_block
                if front_block == 'iron_ore':
                    # Find stone_pickaxe in hotbar (slots 0-8)
                    for slot in range(9):
                        item_key = f"InventorySlot_{slot}_item"
                        if item_key in obs and obs[item_key] == "stone_pickaxe":
                            agent_host.sendCommand(f"hotbar.{slot+1} 1")
                            agent_host.sendCommand(f"hotbar.{slot+1} 0")
                            break
        except Exception:
            pass


def handle_crafting(action, state, agent_host):
    """
    Handle crafting actions with intelligent sub-crafting
    If missing sticks/planks, auto-craft them first
    """
    if action == "craft_iron_pickaxe":
        _, wood, stone, iron, diamond, planks, sticks, has_wood_pick, has_stone_pick, has_iron_pick = state
        
        # Check requirements: 3 iron + 2 sticks
        if iron >= 3 and has_stone_pick and not has_iron_pick:
            # Check if we have enough sticks
            if sticks < 2:
                # Need to craft sticks from planks
                if planks >= 2:
                    print("  [AUTO-CRAFT] Crafting sticks from planks...")
                    agent_host.sendCommand("craft stick")
                    time.sleep(0.2)
                    return (False, 50, "Crafted sticks", False)
                elif wood >= 1:
                    # Craft planks from wood first
                    print("  [AUTO-CRAFT] Crafting planks from wood...")
                    agent_host.sendCommand("craft planks")
                    time.sleep(0.2)
                    return (False, 50, "Crafted planks", False)
                else:
                    return (False, -10, "Need more materials for sticks", False)
            else:
                # Have everything, craft iron pickaxe
                return (True, 5000, "✓✓✓ Attempting to craft iron pickaxe...", False)
        else:
            return (False, -10, "Cannot craft iron pickaxe (need 3 iron + stone pickaxe)", False)
    elif action == "craft_stone_pickaxe" or action == "craft_wooden_pickaxe":
        return (False, -10, "Already have required pickaxes", False)
    
    return (False, 0, "", False)


def train_agent(algorithm="qlearning", num_episodes=50, load_model=None, env_seed=123456, port=10000):
    """
    Entrena un agente en el entorno de recolección de hierro (Stage 3).

    env_seed: semilla del entorno. Con el mismo valor, el layout de bloques
    será siempre el mismo entre episodios y algoritmos.
    port: puerto para conectar con Minecraft (default: 10000)
    """
    # Action space (incluye craft de iron pickaxe)
    # Standardized action space for transfer learning compatibility
    # All stages must have identical action spaces
    actions = [
        "move 1", "move -1",           # 0, 1: Forward/backward
        "strafe 1", "strafe -1",       # 2, 3: Left/right strafe
        "turn 1", "turn -1",           # 4, 5: Turn left/right
        "pitch 0.1", "pitch -0.1",     # 6, 7: Look up/down
        "attack 1",                    # 8: Attack/mine
        "craft_wooden_pickaxe",        # 9: Stage 1 craft (not used here)
        "craft_stone_pickaxe",         # 10: Stage 2 craft (not used here)
        "craft_iron_pickaxe"           # 11: Stage 3 craft
    ]
    
    # Initialize agent
    if algorithm == "qlearning":
        agent = QLearningAgent(actions)
    elif algorithm == "sarsa":
        agent = SarsaAgent(actions)
    elif algorithm == "expected_sarsa":
        agent = ExpectedSarsaAgent(actions)
    elif algorithm == "double_q":
        agent = DoubleQLearningAgent(actions)
    elif algorithm == "monte_carlo":
        agent = MonteCarloAgent(actions)
    elif algorithm == "random":
        agent = RandomAgent(actions)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    # Load pre-trained model from Stage 2 if provided
    if load_model and os.path.exists(load_model):
        print(f"Loading pre-trained model from: {load_model}")
        agent.load_model(load_model)
    
    # Initialize metrics
    metrics = MetricsLogger(f"{algorithm}_IronAgent")
    
    # Initialize Malmo
    agent_host = MalmoPython.AgentHost()
    
    # Map each algorithm to a specific port (10001-10006)
    algorithm_ports = {
        'qlearning': 10001,
        'sarsa': 10002,
        'expected_sarsa': 10003,
        'double_q': 10004,
        'monte_carlo': 10005,
        'random': 10006
    }
    # Override port with algorithm-specific port if not manually specified
    if port == 10000:  # default value means user didn't specify --port
        port = algorithm_ports.get(algorithm, 10001)
    
    print(f"Starting Stage 3 training with {algorithm} on port {port}...")
    
    # Create ClientPool
    client_pool = MalmoPython.ClientPool()
    client_pool.add(MalmoPython.ClientInfo("127.0.0.1", port))

    # Mismo escenario de bloques para todos los episodios
    mission_xml = generar_mundo_xml(seed=env_seed)

    for episode in range(num_episodes):
        agent.start_episode()
        my_mission = MalmoPython.MissionSpec(mission_xml, True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        
        max_retries = 3
        for retry in range(max_retries):
            try:
                agent_host.startMission(my_mission, client_pool, my_mission_record, 0, "iron_agent_exp")
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:", e)
                    exit(1)
                time.sleep(2)

        print(f"Waiting for mission (Episode {episode})...", end=' ')
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            print(".", end="")
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)
        print()

        total_reward = 0
        steps = 0
        wood_collected = 0
        stone_collected = 0
        iron_collected = 0
        prev_wood = 0
        prev_stone = 0
        prev_iron = 0
        max_wood = 0
        max_stone = 0
        max_iron = 0
        action_counts = {"move": 0, "turn": 0, "attack": 0, "craft": 0}
        
        # Track pitch time for auto-reset using observation 'Pitch'
        pitch_start_time = None
        pitch_threshold = 5.0  # degrees: consider >5° as looking up/down
        
        # Initial state - CORRECCIÓN: inicializar state antes del bucle
        while world_state.is_mission_running and world_state.number_of_observations_since_last_state == 0:
            world_state = agent_host.getWorldState()
            time.sleep(0.1)
        
        state = get_state(world_state)
        action = agent.choose_action(state) if state else None
        next_state = None

        while world_state.is_mission_running:
            if state and action:
                # Check if it's a crafting action
                if action.startswith("craft_"):
                    success, craft_reward, msg, should_quit = handle_crafting(action, state, agent_host)
                    if msg and success:
                        print(f"  {msg}")
                    total_reward += craft_reward
                else:
                    agent_host.sendCommand(action)
                
                steps += 1
                
                # Auto-reset pitch
                if steps % 20 == 0:
                    agent_host.sendCommand("pitch 0")
                
                # Track action types
                if "move" in action or "strafe" in action:
                    action_counts["move"] += 1
                elif "turn" in action or "pitch" in action:
                    action_counts["turn"] += 1
                    if "pitch" in action:
                        total_reward -= 10
                elif "jump" in action:
                    action_counts["move"] += 1
                elif "attack" in action:
                    # Auto-select optimal tool before attacking
                    auto_select_tool(world_state, agent_host)
                    
                    action_counts["attack"] += 1
                    # Reward for attacking iron_block
                    if state:
                        surroundings, _, _, _, _, _, _, _, _, _ = state
                        if len(surroundings) > 40:
                            front_blocks = [surroundings[i] for i in [37, 38, 39, 40] if i < len(surroundings)]
                            for block in front_blocks:
                                if block == 'iron_block':
                                    total_reward += 200
                                    break
                elif "craft" in action:
                    action_counts["craft"] += 1
                
                time.sleep(0.02)
                
                world_state = agent_host.getWorldState()
                next_state = get_state(world_state)
                
                # Auto-reset pitch if agent has been looking up/down for >10 seconds
                if world_state.number_of_observations_since_last_state > 0:
                    try:
                        obs_json = json.loads(world_state.observations[-1].text)
                        pitch_val = obs_json.get('Pitch', None)
                        if pitch_val is None:
                            pitch_val = obs_json.get('pitch', None)
                        
                        if pitch_val is not None:
                            pitch = float(pitch_val)
                            if abs(pitch) > pitch_threshold:
                                if pitch_start_time is None:
                                    pitch_start_time = time.time()
                                elif time.time() - pitch_start_time >= 10.0:
                                    print(f"  [AUTO-RESET] Pitch {pitch:.2f}° -> resetting to 0° after 10s")
                                    try:
                                        agent_host.sendCommand("setPitch 0")
                                    except Exception:
                                        pass
                                    try:
                                        agent_host.sendCommand("pitch 0")
                                    except Exception:
                                        pass
                                    try:
                                        if pitch > 0:
                                            for _ in range(20):
                                                agent_host.sendCommand("pitch -0.1")
                                                time.sleep(0.01)
                                        elif pitch < 0:
                                            for _ in range(20):
                                                agent_host.sendCommand("pitch 0.1")
                                                time.sleep(0.01)
                                    except Exception:
                                        pass
                                    total_reward -= 300
                                    print("  [PENALTY] -300 applied for auto-reset correction")
                                    pitch_start_time = None
                            else:
                                pitch_start_time = None
                    except Exception:
                        pass
                
                # Check if episode goal achieved (crafted iron pickaxe)
                if next_state:
                    _, check_wood, check_stone, check_iron, check_diamond, check_planks, check_sticks, has_wood_pick, has_stone_pick, has_iron_pick = next_state
                    
                    # Show progress
                    if steps % 100 == 0:
                        print(f"  [Progress] Iron: {check_iron}/3, Has Stone Pick: {has_stone_pick}, Has Iron Pick: {has_iron_pick}")
                    
                    # Auto-craft when has 3+ iron and stone pickaxe
                    if check_iron >= 3 and has_stone_pick and not has_iron_pick:
                        print(f"\n  >> Auto-crafting iron pickaxe (Iron: {check_iron})...")
                        
                        # Update max_iron before crafting
                        max_iron = max(max_iron, check_iron)
                        
                        # Check if we need to craft sticks first
                        if check_sticks < 2:
                            if check_planks >= 2:
                                print("  [AUTO-CRAFT] Need sticks, crafting from planks...")
                                agent_host.sendCommand("craft stick")
                                time.sleep(0.3)
                                continue
                            elif check_wood >= 1:
                                print("  [AUTO-CRAFT] Need planks first, crafting from wood...")
                                agent_host.sendCommand("craft planks")
                                time.sleep(0.3)
                                continue
                        
                        # Craft iron pickaxe (uses 3 iron + 2 sticks)
                        agent_host.sendCommand("craft iron_pickaxe")
                        time.sleep(0.3)
                        
                        # Verify crafting
                        world_state = agent_host.getWorldState()
                        if world_state.number_of_observations_since_last_state > 0:
                            verify_obs = json.loads(world_state.observations[-1].text)
                            verify_has_iron_pick = False
                            for i in range(45):
                                item_key = f"InventorySlot_{i}_item"
                                if item_key in verify_obs and verify_obs[item_key] == "iron_pickaxe":
                                    verify_has_iron_pick = True
                                    break
                            
                            if verify_has_iron_pick:
                                print(f"\n{'='*60}")
                                print(f"🎉 SUCCESS! Crafted iron pickaxe - Stage 3 complete!")
                                print(f"{'='*60}")
                                total_reward += 15000  # Success reward
                                
                                # Update next_state to reflect post-crafting inventory
                                world_state = agent_host.getWorldState()
                                next_state = get_state(world_state)
                                
                                agent_host.sendCommand("quit")
                                break
                            else:
                                print("  ⚠ Warning: Iron pickaxe not confirmed in inventory")
                
                reward = sum(r.getValue() for r in world_state.rewards)
                
                # Track collection by inventory changes
                if next_state:
                    _, cur_wood, cur_stone, cur_iron, _, _, _, _, _, _ = next_state
                    
                    if cur_wood > prev_wood:
                        wood_collected += (cur_wood - prev_wood)
                        print(f"  [COLLECT] +{cur_wood - prev_wood} Wood! Total: {wood_collected}")
                    if cur_stone > prev_stone:
                        stone_collected += (cur_stone - prev_stone)
                        print(f"  [COLLECT] +{cur_stone - prev_stone} Stone! Total: {stone_collected}")
                    if cur_iron > prev_iron:
                        iron_collected += (cur_iron - prev_iron)
                        print(f"  [COLLECT] +{cur_iron - prev_iron} Iron! Total: {iron_collected}")
                    
                    # Track maximum collected
                    max_wood = max(max_wood, wood_collected)
                    max_stone = max(max_stone, stone_collected)
                    max_iron = max(max_iron, iron_collected)
                    
                    prev_wood = cur_wood
                    prev_stone = cur_stone
                    prev_iron = cur_iron
                
                if reward != 0:
                    print(f"  [REWARD] Step {steps}: {reward}")
                
                total_reward += reward
                
                if next_state:
                    if algorithm == "sarsa":
                        next_action = agent.learn(state, action, reward, next_state, done=False)
                        action = next_action
                    else:
                        agent.learn(state, action, reward, next_state, done=False)
                        action = agent.choose_action(next_state)
                    
                    state = next_state
                else:
                    if not world_state.is_mission_running:
                        agent.learn(state, action, reward, state, done=True)
            else:
                world_state = agent_host.getWorldState()
                state = get_state(world_state)
                if state:
                    action = agent.choose_action(state)

        # Check if episode was successful
        episode_success = False
        final_iron_count = 0
        
        if next_state:
            _, _, _, final_iron_count, _, _, _, _, _, has_iron_pick = next_state
            if has_iron_pick:
                episode_success = True
        
        if not episode_success and total_reward >= 15000:
            episode_success = True
        
        print(f"Episode {episode} ended. Reward: {total_reward}, Iron in inventory: {final_iron_count}, Iron collected: {max_iron}, Stone: {max_stone}, Wood: {max_wood}, Success: {episode_success}")
        metrics.log_episode(episode, steps, max_iron, total_reward, agent.epsilon, action_counts)
        agent.end_episode()
        os.makedirs('../entrenamiento_acumulado', exist_ok=True)
        agent.save_model(f"../entrenamiento_acumulado/{algorithm}_iron_model.pkl")
        time.sleep(0.5)

    metrics.plot_metrics()
    os.makedirs('../entrenamiento_acumulado', exist_ok=True)
    agent.save_model(f"../entrenamiento_acumulado/{algorithm}_iron_model.pkl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Iron Pickaxe Agent - Stage 3')
    parser.add_argument('--algorithm', type=str, default='qlearning', 
                        choices=['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random'],
                        help='RL algorithm to use')
    parser.add_argument('--episodes', type=int, default=50, help='Number of episodes')
    parser.add_argument('--load-model', type=str, default=None, 
                        help='Path to pre-trained stone agent model to continue training')
    parser.add_argument('--env-seed', type=int, default=123456,
                        help='Environment seed (fixed layout of blocks)')
    parser.add_argument('--port', type=int, default=10000,
                        help='Minecraft server port (default: 10000)')
    
    args = parser.parse_args()
    train_agent(args.algorithm, args.episodes, args.load_model, args.env_seed, args.port)
