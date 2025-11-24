"""
From Scratch Agent - Stage 5 (Complete Pipeline)
Agente que inicia casi vacío y debe completar TODAS las etapas del tech tree:
1. Recolectar 3 wood → Craftear wooden pickaxe
2. Recolectar 3 stone → Craftear stone pickaxe  
3. Recolectar 3 iron ore → Craftear iron pickaxe
4. Recolectar 1 diamond

Carga modelo pre-entrenado de Stage 4 (diamond) para transfer learning completo.
Este agente demuestra que el aprendizaje jerárquico funciona en un escenario completo.
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

def generar_mundo_completo_xml(seed=123456):
    """
    Genera el XML del mundo COMPLETO con todos los recursos necesarios:
    - Wood (log blocks): ~20 bloques
    - Stone: ~25 bloques  
    - Iron ore: ~20 bloques
    - Diamond ore: 3-5 bloques (raro)
    
    Este es el mundo más complejo, requiere todos los recursos.
    """
    rng = random.Random(seed)
    
    drawing_xml = ""
    
    # 1. Piso de obsidian (y=3)
    drawing_xml += '<DrawCuboid x1="-10" y1="3" z1="-10" x2="10" y2="3" z2="10" type="obsidian"/>\n'
    
    # 2. Paredes de obsidian perimetrales (y=4 to y=6)
    drawing_xml += '<DrawCuboid x1="-10" y1="4" z1="-10" x2="-10" y2="6" z2="10" type="obsidian"/>\n'
    drawing_xml += '<DrawCuboid x1="10" y1="4" z1="-10" x2="10" y2="6" z2="10" type="obsidian"/>\n'
    drawing_xml += '<DrawCuboid x1="-10" y1="4" z1="-10" x2="10" y2="6" z2="-10" type="obsidian"/>\n'
    drawing_xml += '<DrawCuboid x1="-10" y1="4" z1="10" x2="10" y2="6" z2="10" type="obsidian"/>\n'
    
    all_positions = set()
    
    # 3. Generar diamond ore (3-5 bloques - MUY RARO)
    num_diamond = rng.randint(3, 5)
    diamond_positions = set()
    
    for _ in range(num_diamond):
        attempts = 0
        while attempts < 100:
            x = rng.randint(-9, 9)
            z = rng.randint(-9, 9)
            y = 4
            
            if abs(x) <= 1 and abs(z) <= 1:
                attempts += 1
                continue
            
            pos = (x, y, z)
            if pos not in all_positions:
                all_positions.add(pos)
                diamond_positions.add(pos)
                drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="diamond_ore"/>\n'
                break
            attempts += 1
    
    # 4. Iron ore (~20 bloques)
    num_iron = rng.randint(18, 22)
    iron_positions = set()
    
    for _ in range(num_iron):
        attempts = 0
        while attempts < 100:
            x = rng.randint(-9, 9)
            z = rng.randint(-9, 9)
            y = rng.choice([4, 5])
            
            if abs(x) <= 1 and abs(z) <= 1:
                attempts += 1
                continue
            
            pos = (x, y, z)
            if pos not in all_positions:
                all_positions.add(pos)
                iron_positions.add(pos)
                drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="iron_ore"/>\n'
                break
            attempts += 1
    
    # 5. Stone (~25 bloques)
    num_stone = rng.randint(23, 27)
    stone_positions = set()
    
    for _ in range(num_stone):
        attempts = 0
        while attempts < 100:
            x = rng.randint(-9, 9)
            z = rng.randint(-9, 9)
            y = rng.choice([4, 5])
            
            if abs(x) <= 1 and abs(z) <= 1:
                attempts += 1
                continue
            
            pos = (x, y, z)
            if pos not in all_positions:
                all_positions.add(pos)
                stone_positions.add(pos)
                drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="stone"/>\n'
                break
            attempts += 1
    
    # 6. Wood/Log (~20 bloques)
    num_wood = rng.randint(18, 22)
    wood_positions = set()
    
    for _ in range(num_wood):
        attempts = 0
        while attempts < 100:
            x = rng.randint(-9, 9)
            z = rng.randint(-9, 9)
            y = rng.choice([4, 5])
            
            if abs(x) <= 1 and abs(z) <= 1:
                attempts += 1
                continue
            
            pos = (x, y, z)
            if pos not in all_positions:
                all_positions.add(pos)
                wood_positions.add(pos)
                drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="log"/>\n'
                break
            attempts += 1
    
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary>Complete Tech Tree - Stage 5 (From Scratch)</Summary>
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
                <ServerQuitFromTimeUp timeLimitMs="300000"/>
                <ServerQuitWhenAnyAgentFinishes/>
            </ServerHandlers>
        </ServerSection>
        <AgentSection mode="Survival">
            <Name>FromScratchAgent</Name>
            <AgentStart>
                <Placement x="0.5" y="4" z="0.5" yaw="0"/>
                <Inventory>
                    <!-- Starting ALMOST empty - only diamond axe for wood -->
                    <InventoryItem slot="0" type="diamond_axe"/>
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
                <CraftCommands/>
                <MissionQuitCommands/>
                <ObservationFromRecentCommands/>
                <ObservationFromHotBar/>
                <ObservationFromFullInventory/>
                <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="5" yrange="3" zrange="5"/>
                </ObservationFromNearbyEntities>
                <RewardForCollectingItem>
                    <Item reward="1000" type="log"/>
                    <Item reward="2000" type="stone"/>
                    <Item reward="5000" type="iron_ore"/>
                    <Item reward="5000" type="iron_ingot"/>
                    <Item reward="100000" type="diamond"/>
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
    Enhanced state representation for complete tech tree
    Returns: (surroundings_tuple, wood_count, stone_count, iron_count, diamond_count, 
              planks_count, sticks_count, has_wooden_pickaxe, has_stone_pickaxe, has_iron_pickaxe)
    
    State size: 10 elements (idéntico a diamond_agent)
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
            elif item_type in ["iron_ore", "iron_ingot"]:
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
            elif item_type == "iron_ore":
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

def train_agent(algorithm="qlearning", num_episodes=50, load_model=None, env_seed=123456, port=10000):
    """
    Entrena un agente en el tech tree completo (Stage 5).

    env_seed: semilla del entorno
    port: puerto para conectar con Minecraft
    """
    # Action space (IDENTICAL to all stages for transfer learning compatibility)
    actions = [
        "move 1", "move -1",           # 0, 1
        "strafe 1", "strafe -1",       # 2, 3
        "turn 1", "turn -1",           # 4, 5
        "pitch 0.1", "pitch -0.1",     # 6, 7
        "attack 1",                    # 8
        "craft_wooden_pickaxe",        # 9: Stage 1 craft
        "craft_stone_pickaxe",         # 10: Stage 2 craft
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
    
    # Load pre-trained model from Stage 4 (Diamond) if provided
    if load_model:
        print(f"Loading pre-trained model from: {load_model}")
        agent.load_model(load_model)
    
    # Initialize metrics
    metrics = MetricsLogger(f"{algorithm}_FromScratchAgent")
    
    # Initialize Malmo
    agent_host = MalmoPython.AgentHost()
    # Note: No llamamos a agent_host.parse(sys.argv) para evitar conflictos
    # con los argumentos de argparse de Python (--algorithm, --episodes, etc.)
    
    # Connect to Minecraft on specified port
    client_pool = MalmoPython.ClientPool()
    client_info = MalmoPython.ClientInfo("127.0.0.1", port)
    client_pool.add(client_info)
    
    # Training loop
    for episode in range(1, num_episodes + 1):
        print(f"\n{'='*60}")
        print(f"Episode {episode}/{num_episodes} - {algorithm.upper()}")
        print(f"{'='*60}")
        
        # Generate mission with fixed seed
        mission_xml = generar_mundo_completo_xml(seed=env_seed)
        mission = MalmoPython.MissionSpec(mission_xml, True)
        mission_record = MalmoPython.MissionRecordSpec()
        
        # Start mission
        max_retries = 3
        for retry in range(max_retries):
            try:
                agent_host.startMission(mission, client_pool, mission_record, 0, "FromScratchStage5")
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print(f"Error starting mission: {e}")
                    exit(1)
                else:
                    print(f"Retry {retry + 1}/{max_retries}...")
                    time.sleep(2)
        
        # Wait for mission to start
        print(f"Waiting for mission (Episode {episode})...", end=" ", flush=True)
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            print(".", end="", flush=True)
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print(f"Error: {error.text}")
        
        print()
        
        # Episode variables
        state = get_state(world_state)
        action = agent.choose_action(state) if state else 0
        total_reward = 0
        steps = 0
        
        # Track collection metrics
        wood_collected = 0
        stone_collected = 0
        iron_collected = 0
        diamond_collected = 0
        max_wood = 0
        max_stone = 0
        max_iron = 0
        max_diamond = 0
        prev_wood = 0
        prev_stone = 0
        prev_iron = 0
        prev_diamond = 0
        
        # Track action distribution
        action_counts = {
            'move': 0,
            'turn': 0,
            'attack': 0,
            'craft': 0
        }
        
        # Pitch auto-reset tracking
        pitch_start_time = None
        pitch_threshold = 30.0
        
        def auto_select_tool(world_state, agent_host):
            """
            Automatically selects the optimal tool based on the block in front.
            Complete tech tree: Handles all block types
            """
            if world_state.number_of_observations_since_last_state > 0:
                try:
                    obs = json.loads(world_state.observations[-1].text)
                    surroundings = obs.get("surroundings5x5", [])
                    
                    if len(surroundings) > 37:
                        front_block = surroundings[37]
                        
                        # Priority: diamond > iron > stone > wood
                        if front_block == 'diamond_ore':
                            # Find iron_pickaxe
                            for slot in range(9):
                                item_key = f"InventorySlot_{slot}_item"
                                if item_key in obs and obs[item_key] == "iron_pickaxe":
                                    agent_host.sendCommand(f"hotbar.{slot+1} 1")
                                    agent_host.sendCommand(f"hotbar.{slot+1} 0")
                                    return
                        elif front_block == 'iron_ore':
                            # Find stone_pickaxe
                            for slot in range(9):
                                item_key = f"InventorySlot_{slot}_item"
                                if item_key in obs and obs[item_key] == "stone_pickaxe":
                                    agent_host.sendCommand(f"hotbar.{slot+1} 1")
                                    agent_host.sendCommand(f"hotbar.{slot+1} 0")
                                    return
                        elif front_block == 'stone':
                            # Find wooden_pickaxe
                            for slot in range(9):
                                item_key = f"InventorySlot_{slot}_item"
                                if item_key in obs and obs[item_key] == "wooden_pickaxe":
                                    agent_host.sendCommand(f"hotbar.{slot+1} 1")
                                    agent_host.sendCommand(f"hotbar.{slot+1} 0")
                                    return
                        elif front_block == 'log':
                            # Use diamond_axe (should be in slot 0)
                            for slot in range(9):
                                item_key = f"InventorySlot_{slot}_item"
                                if item_key in obs and obs[item_key] == "diamond_axe":
                                    agent_host.sendCommand(f"hotbar.{slot+1} 1")
                                    agent_host.sendCommand(f"hotbar.{slot+1} 0")
                                    return
                except Exception:
                    pass
        
        # Main episode loop
        while world_state.is_mission_running:
            steps += 1
            
            if state:
                # Execute action
                action_str = actions[action]
                
                # Handle crafting actions with hierarchical logic
                if action_str == "craft_wooden_pickaxe":
                    _, wood, stone, iron, diamond, planks, sticks, has_wood_pick, has_stone_pick, has_iron_pick = state
                    
                    if not has_wood_pick and wood >= 3:
                        # Auto-craft planks and sticks if needed
                        if planks < 3:
                            needed_planks = 3 - planks
                            wood_to_craft = (needed_planks + 3) // 4  # 1 wood = 4 planks
                            for _ in range(wood_to_craft):
                                agent_host.sendCommand("craft planks")
                                time.sleep(0.1)
                            print(f"  >> Auto-crafted {wood_to_craft * 4} planks from {wood_to_craft} wood")
                            time.sleep(0.2)
                        
                        # Update state to get current planks
                        world_state = agent_host.getWorldState()
                        state = get_state(world_state)
                        if state:
                            _, wood, stone, iron, diamond, planks, sticks, has_wood_pick, has_stone_pick, has_iron_pick = state
                        
                        if sticks < 2:
                            needed_sticks = 2 - sticks
                            planks_to_craft = (needed_sticks + 3) // 4  # 2 planks = 4 sticks
                            for _ in range(planks_to_craft):
                                agent_host.sendCommand("craft stick")
                                time.sleep(0.1)
                            print(f"  >> Auto-crafted {planks_to_craft * 4} sticks from {planks_to_craft * 2} planks")
                            time.sleep(0.2)
                        
                        # Craft wooden pickaxe
                        agent_host.sendCommand("craft wooden_pickaxe")
                        time.sleep(0.2)
                        print(f"  >> Auto-crafting wooden pickaxe (Wood: {wood})...")
                        print("="*60)
                        print("🎉 SUCCESS! Crafted wooden pickaxe!")
                        print("="*60)
                    else:
                        if has_wood_pick:
                            pass  # Already have pickaxe
                        else:
                            print(f"  Cannot craft wooden pickaxe (need 3 wood)")
                
                elif action_str == "craft_stone_pickaxe":
                    _, wood, stone, iron, diamond, planks, sticks, has_wood_pick, has_stone_pick, has_iron_pick = state
                    
                    if not has_stone_pick and stone >= 3 and has_wood_pick:
                        # Ensure we have sticks
                        if sticks < 2 and planks >= 2:
                            agent_host.sendCommand("craft stick")
                            time.sleep(0.1)
                            agent_host.sendCommand("craft stick")
                            time.sleep(0.1)
                            print(f"  >> Auto-crafted 4 sticks from 2 planks")
                            time.sleep(0.2)
                        
                        # Craft stone pickaxe
                        agent_host.sendCommand("craft stone_pickaxe")
                        time.sleep(0.2)
                        print(f"  >> Auto-crafting stone pickaxe (Stone: {stone})...")
                        print("="*60)
                        print("🎉 SUCCESS! Crafted stone pickaxe!")
                        print("="*60)
                    else:
                        print(f"  Cannot craft stone pickaxe (need 3 stone + wooden pickaxe)")
                
                elif action_str == "craft_iron_pickaxe":
                    _, wood, stone, iron, diamond, planks, sticks, has_wood_pick, has_stone_pick, has_iron_pick = state
                    
                    if not has_iron_pick and iron >= 3 and has_stone_pick:
                        # Ensure we have sticks
                        if sticks < 2 and planks >= 2:
                            agent_host.sendCommand("craft stick")
                            time.sleep(0.1)
                            agent_host.sendCommand("craft stick")
                            time.sleep(0.1)
                            print(f"  >> Auto-crafted 4 sticks from 2 planks")
                            time.sleep(0.2)
                        
                        # Craft iron pickaxe
                        agent_host.sendCommand("craft iron_pickaxe")
                        time.sleep(0.2)
                        print(f"  >> Auto-crafting iron pickaxe (Iron: {iron})...")
                        print("="*60)
                        print("🎉 SUCCESS! Crafted iron pickaxe!")
                        print("="*60)
                    else:
                        print(f"  Cannot craft iron pickaxe (need 3 iron + stone pickaxe)")
                
                else:
                    agent_host.sendCommand(action_str)
                
                # Track action distribution
                if 'move' in action_str or 'strafe' in action_str or 'pitch' in action_str:
                    action_counts['move'] += 1
                elif 'turn' in action_str:
                    action_counts['turn'] += 1
                elif 'attack' in action_str:
                    # Auto-select optimal tool before attacking
                    auto_select_tool(world_state, agent_host)
                    action_counts['attack'] += 1
                elif 'craft' in action_str:
                    action_counts['craft'] += 1
                
                time.sleep(0.02)
                
                world_state = agent_host.getWorldState()
                next_state = get_state(world_state)
                
                # Auto-reset pitch
                if world_state.number_of_observations_since_last_state > 0:
                    try:
                        obs_json = json.loads(world_state.observations[-1].text)
                        pitch_val = obs_json.get('Pitch', obs_json.get('pitch'))
                        
                        if pitch_val is not None:
                            pitch = float(pitch_val)
                            if abs(pitch) > pitch_threshold:
                                if pitch_start_time is None:
                                    pitch_start_time = time.time()
                                elif time.time() - pitch_start_time >= 10.0:
                                    print(f"  [AUTO-RESET] Pitch {pitch:.2f}° -> 0°")
                                    try:
                                        agent_host.sendCommand("setPitch 0")
                                    except Exception:
                                        pass
                                    try:
                                        agent_host.sendCommand("pitch 0")
                                    except Exception:
                                        pass
                                    pitch_start_time = None
                            else:
                                pitch_start_time = None
                    except (ValueError, KeyError):
                        pass
                
                # Calculate reward
                reward = 0
                for r in world_state.rewards:
                    reward += r.getValue()
                
                total_reward += reward
                
                if reward != 0:
                    print(f"  [REWARD] Step {steps}: {reward}")
                
                # Track collection progress
                if next_state:
                    _, wood, stone, iron, diamond, planks, sticks, has_wood_pick, has_stone_pick, has_iron_pick = next_state
                    
                    # Track max values
                    max_wood = max(max_wood, wood)
                    max_stone = max(max_stone, stone)
                    max_iron = max(max_iron, iron)
                    max_diamond = max(max_diamond, diamond)
                    
                    # Detect collection events
                    if wood > prev_wood:
                        wood_collected += (wood - prev_wood)
                        print(f"  [COLLECT] +{wood - prev_wood} Wood! Total: {wood}")
                    if stone > prev_stone:
                        stone_collected += (stone - prev_stone)
                        print(f"  [COLLECT] +{stone - prev_stone} Stone! Total: {stone}")
                    if iron > prev_iron:
                        iron_collected += (iron - prev_iron)
                        print(f"  [COLLECT] +{iron - prev_iron} Iron! Total: {iron}")
                    if diamond > prev_diamond:
                        diamond_collected += (diamond - prev_diamond)
                        print(f"  [COLLECT] 💎 +{diamond - prev_diamond} DIAMOND! Total: {diamond}")
                        print(f"{'='*60}")
                        print(f"🎉🎉🎉 COMPLETE SUCCESS! DIAMOND OBTAINED! 🎉🎉🎉")
                        print(f"{'='*60}")
                        agent_host.sendCommand("quit")
                    
                    prev_wood = wood
                    prev_stone = stone
                    prev_iron = iron
                    prev_diamond = diamond
                    
                    # Progress reporting every 1000 steps
                    if steps % 1000 == 0:
                        print(f"  [Progress] Wood: {wood}, Stone: {stone}, Iron: {iron}, Diamond: {diamond}")
                        print(f"            Picks: Wood={has_wood_pick}, Stone={has_stone_pick}, Iron={has_iron_pick}")
                
                # Update agent
                next_action = agent.choose_action(next_state) if next_state else 0
                agent.update(state, action, reward, next_state, next_action)
                
                state = next_state
                action = next_action
            else:
                time.sleep(0.02)
                world_state = agent_host.getWorldState()
                state = get_state(world_state)
                if state:
                    action = agent.choose_action(state)
        
        # Episode end
        episode_success = (max_diamond >= 1)
        
        print(f"Episode {episode} ended. Reward: {total_reward}, Wood: {max_wood}, " + 
              f"Stone: {max_stone}, Iron: {max_iron}, Diamond: {max_diamond}, Success: {episode_success}")
        
        # Collect metrics
        metrics.collect_episode(
            episode=episode,
            total_reward=total_reward,
            steps=steps,
            epsilon=getattr(agent, 'epsilon', 1.0),
            success=episode_success,
            wood_collected=wood_collected,
            max_wood=max_wood,
            stone_collected=stone_collected,
            max_stone=max_stone,
            iron_collected=iron_collected,
            max_iron=max_iron,
            diamond_collected=diamond_collected,
            max_diamond=max_diamond,
            action_distribution=action_counts
        )
        
        # Save model periodically
        if episode % 10 == 0:
            model_dir = os.path.join(parent_dir, "entrenamiento_acumulado")
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, f"{algorithm}_scratch_model.pkl")
            agent.save_model(model_path)
            print(f"Model saved to: {model_path}")
        
        time.sleep(0.5)
    
    # Final save
    model_dir = os.path.join(parent_dir, "entrenamiento_acumulado")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{algorithm}_scratch_model.pkl")
    agent.save_model(model_path)
    print(f"\nFinal model saved to: {model_path}")
    
    # Save and plot metrics
    metrics.save_and_plot(agent_name="FromScratchAgent")
    
    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train From Scratch Agent (Stage 5 - Complete Pipeline)')
    parser.add_argument('--algorithm', type=str, default='qlearning',
                       choices=['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random'],
                       help='RL algorithm to use')
    parser.add_argument('--episodes', type=int, default=50,
                       help='Number of training episodes')
    parser.add_argument('--load-model', type=str, default=None,
                       help='Path to pre-trained model from Stage 4 (diamond_agent)')
    parser.add_argument('--seed', type=int, default=123456,
                       help='Environment seed for reproducibility')
    parser.add_argument('--port', type=int, default=10000,
                       help='Minecraft client port')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Stage 5: From Scratch Agent (Complete Tech Tree)")
    print(f"Algorithm: {args.algorithm}")
    print(f"Episodes: {args.episodes}")
    print(f"Environment Seed: {args.seed}")
    print(f"Port: {args.port}")
    if args.load_model:
        print(f"Loading model: {args.load_model}")
    print(f"{'='*60}\n")
    
    train_agent(
        algorithm=args.algorithm,
        num_episodes=args.episodes,
        load_model=args.load_model,
        env_seed=args.seed,
        port=args.port
    )
