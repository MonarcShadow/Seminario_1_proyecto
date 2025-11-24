"""
Iron Pickaxe Crafting Agent - Stage 3
Usa un pico de piedra (stone pickaxe) para recolectar 3 iron ore y craftear un iron pickaxe.
Comienza con el inventario de un episodio exitoso de Stage 2.
Objetivo: Recolectar 3 iron ore → Craftear iron pickaxe
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

from algorithms import QLearningAgent, SarsaAgent, ExpectedSarsaAgent, DoubleQAgent, MonteCarloAgent, RandomAgent
from metrics import MetricsCollector

try:
    import MalmoPython
except ImportError:
    print("Error: MalmoPython no está instalado o no se puede importar")
    sys.exit(1)

def generar_mundo_hierro_xml(seed=123456):
    """
    Genera el XML del mundo con iron ore disperso.
    - seed: semilla para generación determinística de bloques
    - Spawn: (0.5, 4, 0.5)
    - Dimensiones: 21x21 (x: -10 to 10, z: -10 to 10)
    - Piso: Obsidian (y=3, no se puede romper)
    - Paredes: Obsidian perimetral
    - Iron ore: 20-30 bloques dispersos en y=4 y y=5
    - Stone (opcional): 10-15 bloques adicionales para variedad
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
    
    # 3. Generar iron ore (20-30 bloques)
    num_iron = rng.randint(20, 30)
    iron_positions = set()
    
    for _ in range(num_iron):
        attempts = 0
        while attempts < 100:
            x = rng.randint(-9, 9)
            z = rng.randint(-9, 9)
            y = rng.choice([4, 5])
            
            # Evitar spawn area (centro 3x3)
            if abs(x) <= 1 and abs(z) <= 1:
                attempts += 1
                continue
            
            pos = (x, y, z)
            if pos not in iron_positions:
                iron_positions.add(pos)
                drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="iron_ore"/>\n'
                break
            attempts += 1
    
    # 4. Opcional: algunos bloques de stone para variedad (10-15)
    num_stone = rng.randint(10, 15)
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
            if pos not in iron_positions and pos not in stone_positions:
                stone_positions.add(pos)
                drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="stone"/>\n'
                break
            attempts += 1
    
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
                <CraftCommands/>
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
                    <Item reward="5000" type="iron_ore"/>
                    <Item reward="5000" type="iron_ingot"/>
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
    Returns: (surroundings_tuple, wood_count, stone_count, iron_count, has_wooden_pickaxe, has_stone_pickaxe, has_iron_pickaxe)
    
    Nota: iron_ore se convierte automáticamente en iron_ingot al recolectar (simplificación)
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
    iron_count = 0  # Incluye tanto iron_ore como iron_ingot
    planks_count = 0
    sticks_count = 0
    has_wooden_pickaxe = False
    has_stone_pickaxe = False
    has_iron_pickaxe = False
    
    # Method 1: Check flat inventory structure (InventorySlot_0_item, etc.)
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
            elif item_type in ["iron_ore", "iron_ingot"]:  # Contar ambos como iron
                iron_count += quantity
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
    
    return (surroundings, wood_count, stone_count, iron_count, planks_count, sticks_count, has_wooden_pickaxe, has_stone_pickaxe, has_iron_pickaxe)

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
        agent = DoubleQAgent(actions)
    elif algorithm == "monte_carlo":
        agent = MonteCarloAgent(actions)
    elif algorithm == "random":
        agent = RandomAgent(actions)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    # Load pre-trained model from Stage 2 if provided
    if load_model:
        print(f"Loading pre-trained model from: {load_model}")
        agent.load_model(load_model)
    
    # Initialize metrics
    metrics = MetricsCollector(algorithm)
    
    # Initialize Malmo
    agent_host = MalmoPython.AgentHost()
    try:
        agent_host.parse(sys.argv)
    except RuntimeError as e:
        print(f'ERROR: {e}')
        print(agent_host.getUsage())
        exit(1)
    
    if agent_host.receivedArgument("help"):
        print(agent_host.getUsage())
        exit(0)
    
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
        mission_xml = generar_mundo_hierro_xml(seed=env_seed)
        mission = MalmoPython.MissionSpec(mission_xml, True)
        mission_record = MalmoPython.MissionRecordSpec()
        
        # Start mission
        max_retries = 3
        for retry in range(max_retries):
            try:
                agent_host.startMission(mission, client_pool, mission_record, 0, "IronStage3")
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print(f"Error starting mission: {e}")
                    exit(1)
                else:
                    print(f"Retry {retry + 1}/{max_retries}...")
                    time.sleep(2)
        
        # Wait for mission to start
        print("Waiting for mission to start...")
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print(f"Error: {error.text}")
        
        print("Mission started!")
        
        # Episode variables
        state = get_state(world_state)
        action = agent.choose_action(state) if state else 0
        total_reward = 0
        steps = 0
        
        # Track collection metrics
        wood_collected = 0
        stone_collected = 0
        iron_collected = 0
        max_wood = 0
        max_stone = 0
        max_iron = 0
        prev_wood = 0
        prev_stone = 0
        prev_iron = 0
        
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
            Stage 3 (Iron): Uses stone_pickaxe for iron_ore
            """
            if world_state.number_of_observations_since_last_state > 0:
                try:
                    obs = json.loads(world_state.observations[-1].text)
                    surroundings = obs.get("surroundings5x5", [])
                    
                    if len(surroundings) > 37:
                        front_block = surroundings[37]
                        
                        # Stage 3: Select stone_pickaxe for iron_ore
                        if front_block == 'iron_ore':
                            # Find stone_pickaxe in hotbar (slots 0-8)
                            for slot in range(9):
                                item_key = f"InventorySlot_{slot}_item"
                                if item_key in obs and obs[item_key] == "stone_pickaxe":
                                    agent_host.sendCommand(f"hotbar.{slot+1} 1")  # Select slot (1-indexed)
                                    agent_host.sendCommand(f"hotbar.{slot+1} 0")
                                    break
                except Exception:
                    pass
        
        # Main episode loop
        while world_state.is_mission_running:
            steps += 1
            
            if state:
                # Execute action
                action_str = actions[action]
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
                    _, check_wood, check_stone, check_iron, check_planks, check_sticks, has_wood_pick, has_stone_pick, has_iron_pick = next_state
                    
                    # Show progress
                    if steps % 100 == 0:
                        print(f"  [Progress] Iron: {check_iron}/3, Planks: {check_planks}, Sticks: {check_sticks}, Has Stone Pick: {has_stone_pick}, Has Iron Pick: {has_iron_pick}")
                    
                    # Auto-craft when has 3+ iron and stone pickaxe
                    if check_iron >= 3 and has_stone_pick and not has_iron_pick:
                        print(f"\n  >> Auto-crafting iron pickaxe (Iron: {check_iron}, Planks: {check_planks}, Sticks: {check_sticks})...")
                        
                        # Update max_iron before crafting
                        max_iron = max(max_iron, check_iron)
                        
                        # Check if we need to craft sticks first
                        if check_sticks < 2:
                            sticks_needed = 2 - check_sticks
                            planks_needed = 1 if sticks_needed <= 4 else 2
                            
                            if check_planks >= planks_needed:
                                print(f"  >> Crafting sticks first (need {sticks_needed} sticks, have {check_planks} planks)...")
                                agent_host.sendCommand("craft stick")
                                time.sleep(0.3)
                                check_sticks += 4
                                check_planks -= 2
                                print(f"  >> Crafted 4 sticks! Now have {check_sticks} sticks, {check_planks} planks")
                            else:
                                print(f"  ⚠ Warning: Not enough planks to craft sticks (need {planks_needed}, have {check_planks})")
                                total_reward -= 500
                        
                        # Now craft iron pickaxe
                        print(f"  >> Crafting iron pickaxe (Iron: {check_iron}, Sticks: {check_sticks})...")
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
                    _, cur_wood, cur_stone, cur_iron, cur_planks, cur_sticks, _, _, _ = next_state
                    
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
            _, _, _, final_iron_count, _, _, has_iron_pick = next_state
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
    parser = argparse.ArgumentParser(description='Run Iron Ore Agent - Stage 3')
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
