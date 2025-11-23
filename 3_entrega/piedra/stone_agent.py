import os
import sys
import time
import json
import random
import argparse

# Add parent directory to sys.path to import shared modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(parent_dir, 'madera'))

from algorithms import QLearningAgent, RandomAgent, SarsaAgent, ExpectedSarsaAgent, DoubleQLearningAgent, MonteCarloAgent
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

def generar_mundo_piedra_xml(seed=None):
    """
    Generates XML for stone mining world
    Agent starts with wooden pickaxe, planks, and sticks
    """
    if seed is not None:
        random.seed(seed)
    
    # Config - Arena with stone blocks
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
        x = random.randint(-radio + 2, radio - 2)
        z = random.randint(-radio + 2, radio - 2)
        return x, z
    
    # 1. Generate Stone (High Density: 30-40 blocks)
    num_piedra = random.randint(30, 40)
    for _ in range(num_piedra):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                bloques_generados.append((x, 4, z, "stone"))
                posiciones_usadas.add((x, z))
                break
            intentos += 1

    # 2. Generate some wood for variety (optional, lower density)
    num_madera = random.randint(5, 10)
    for _ in range(num_madera):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                altura = random.choice([0, 1])
                tipo = 'log'
                for h in range(altura + 1):
                    y = 4 + h
                    bloques_generados.append((x, y, z, tipo))
                posiciones_usadas.add((x, z))
                break
            intentos += 1
            
    # Drawing XML
    drawing_xml = ""
    # Obsidian floor and walls
    drawing_xml += f'<DrawCuboid x1="{-radio}" y1="3" z1="{-radio}" x2="{radio}" y2="3" z2="{radio}" type="obsidian"/>\n'
    drawing_xml += f'<DrawCuboid x1="{-radio}" y1="4" z1="{-radio}" x2="{radio}" y2="10" z2="{-radio}" type="obsidian"/>\n'
    drawing_xml += f'<DrawCuboid x1="{-radio}" y1="4" z1="{radio}" x2="{radio}" y2="10" z2="{radio}" type="obsidian"/>\n'
    drawing_xml += f'<DrawCuboid x1="{radio}" y1="4" z1="{-radio}" x2="{radio}" y2="10" z2="{radio}" type="obsidian"/>\n'
    drawing_xml += f'<DrawCuboid x1="{-radio}" y1="4" z1="{-radio}" x2="{-radio}" y2="10" z2="{radio}" type="obsidian"/>\n'
    
    for x, y, z, tipo in bloques_generados:
        drawing_xml += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="{tipo}"/>\n'

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary>Stone Pickaxe Crafting - Stage 2</Summary>
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
            <Name>StoneGatherer</Name>
            <AgentStart>
                <Placement x="0.5" y="4" z="0.5" yaw="0"/>
                <Inventory>
                    <!-- Starting inventory from successful wood stage -->
                    <InventoryItem slot="0" type="wooden_pickaxe"/>
                    <InventoryItem slot="1" type="stick" quantity="2"/>
                    <InventoryItem slot="2" type="planks" quantity="7"/>
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
                    <Item reward="1000" type="log"/>
                    <Item reward="2000" type="stone"/>
                    <Item reward="5000" type="iron_ore"/>
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
    Returns: (surroundings_tuple, wood_count, stone_count, iron_count, has_wooden_pickaxe, has_stone_pickaxe)
    """
    if not world_state.number_of_observations_since_last_state:
        return None
    
    msg = world_state.observations[-1].text
    obs = json.loads(msg)
    
    # Get surroundings (now 5x5 grid)
    surroundings = tuple(obs.get("surroundings5x5", []))
    
    # Count inventory items
    wood_count = 0
    stone_count = 0
    iron_count = 0
    has_wooden_pickaxe = False
    has_stone_pickaxe = False
    
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
            elif item_type == "iron_ore":
                iron_count += quantity
            elif item_type == "wooden_pickaxe":
                has_wooden_pickaxe = True
            elif item_type == "stone_pickaxe":
                has_stone_pickaxe = True
    
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
            elif item_type == "wooden_pickaxe":
                has_wooden_pickaxe = True
            elif item_type == "stone_pickaxe":
                has_stone_pickaxe = True
    
    return (surroundings, wood_count, stone_count, iron_count, has_wooden_pickaxe, has_stone_pickaxe)

def train_agent(algorithm="qlearning", num_episodes=50, load_model=None):
    # Action space (same as wood agent for compatibility)
    actions = [
        "move 1", "move -1",
        "strafe 1", "strafe -1",
        "turn 1", "turn -1",
        "pitch 0.1", "pitch -0.1",
        "jump 1",
        "attack 1",
        "craft_wooden_pickaxe",  # Not used in this stage but kept for compatibility
        "craft_stone_pickaxe"
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
        print(f"Unknown algorithm: {algorithm}")
        return

    # Load pre-trained model if provided
    if load_model and os.path.exists(load_model):
        print(f"Loading pre-trained model from {load_model}...")
        agent.load_model(load_model)

    metrics = MetricsLogger(f"{algorithm}_StoneAgent")
    agent_host = MalmoPython.AgentHost()
    
    print(f"Starting Stage 2 training with {algorithm}...")
    
    # Create ClientPool
    client_pool = MalmoPython.ClientPool()
    client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))
    client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10001))

    for episode in range(num_episodes):
        agent.start_episode()
        mission_xml = generar_mundo_piedra_xml(seed=episode)
        my_mission = MalmoPython.MissionSpec(mission_xml, True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        
        max_retries = 3
        for retry in range(max_retries):
            try:
                agent_host.startMission(my_mission, client_pool, my_mission_record, 0, "stone_agent_exp")
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
        
        # Initial state
        while world_state.is_mission_running and world_state.number_of_observations_since_last_state == 0:
             world_state = agent_host.getWorldState()
             time.sleep(0.1)
        
        state = get_state(world_state)
        action = agent.choose_action(state) if state else None

        def handle_crafting(action, state, agent_host):
            """Handle crafting actions"""
            if action == "craft_stone_pickaxe":
                _, wood, stone, iron, has_wood_pick, has_stone_pick = state
                if stone >= 3 and has_wood_pick and not has_stone_pick:
                    return (True, 5000, "✓✓✓ Attempting to craft stone pickaxe...", False)
                else:
                    return (False, -10, "Cannot craft stone pickaxe (need 3 stone + wooden pickaxe)", False)
            elif action == "craft_wooden_pickaxe":
                # Not used in this stage
                return (False, -10, "Already have wooden pickaxe", False)
            
            return (False, 0, "", False)

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
                    action_counts["attack"] += 1
                    # Reward for attacking stone
                    if state:
                        surroundings, _, _, _, _, _ = state
                        if len(surroundings) > 40:
                            front_blocks = [surroundings[i] for i in [37, 38, 39, 40] if i < len(surroundings)]
                            for block in front_blocks:
                                if block == 'stone':
                                    total_reward += 200
                                    break
                elif "craft" in action:
                    action_counts["craft"] += 1
                
                time.sleep(0.02)
                
                world_state = agent_host.getWorldState()
                next_state = get_state(world_state)
                
                # Check if episode goal achieved (crafted stone pickaxe)
                if next_state:
                    _, check_wood, check_stone, check_iron, has_wood_pick, has_stone_pick = next_state
                    
                    # Show progress
                    if steps % 100 == 0:
                        print(f"  [Progress] Stone: {check_stone}/3, Has Wood Pick: {has_wood_pick}, Has Stone Pick: {has_stone_pick}")
                    
                    # Auto-craft when has 3+ stone and wooden pickaxe
                    if check_stone >= 3 and has_wood_pick and not has_stone_pick:
                        print(f"\n  >> Auto-crafting stone pickaxe (Stone: {check_stone})...")
                        
                        # Update max_stone before crafting
                        max_stone = max(max_stone, check_stone)
                        
                        # Craft stone pickaxe (uses 3 stone + 2 sticks)
                        agent_host.sendCommand("craft stone_pickaxe")
                        time.sleep(0.3)
                        
                        # Verify crafting
                        world_state = agent_host.getWorldState()
                        if world_state.number_of_observations_since_last_state > 0:
                            verify_obs = json.loads(world_state.observations[-1].text)
                            verify_has_stone_pick = False
                            for i in range(45):
                                item_key = f"InventorySlot_{i}_item"
                                if item_key in verify_obs and verify_obs[item_key] == "stone_pickaxe":
                                    verify_has_stone_pick = True
                                    break
                            
                            if verify_has_stone_pick:
                                print(f"\n{'='*60}")
                                print(f"🎉 SUCCESS! Crafted stone pickaxe - Stage 2 complete!")
                                print(f"{'='*60}")
                                total_reward += 10000  # Success reward
                                
                                # Update next_state to reflect post-crafting inventory
                                world_state = agent_host.getWorldState()
                                next_state = get_state(world_state)
                                
                                agent_host.sendCommand("quit")
                                break
                            else:
                                print("  ⚠ Warning: Stone pickaxe not confirmed in inventory")
                
                reward = sum(r.getValue() for r in world_state.rewards)
                
                # Track collection by inventory changes
                if next_state:
                    _, cur_wood, cur_stone, cur_iron, _, _ = next_state
                    
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
        final_stone_count = 0
        
        if next_state:
            _, _, final_stone_count, _, _, has_stone_pick = next_state
            if has_stone_pick:
                episode_success = True
        
        if not episode_success and total_reward >= 10000:
            episode_success = True
        
        print(f"Episode {episode} ended. Reward: {total_reward}, Stone in inventory: {final_stone_count}, Stone collected: {max_stone}, Wood: {max_wood}, Iron: {max_iron}, Success: {episode_success}")
        metrics.log_episode(episode, steps, max_stone, total_reward, agent.epsilon, action_counts)
        agent.end_episode()
        agent.save_model(f"{algorithm}_stone_model.pkl")
        time.sleep(0.5)

    metrics.plot_metrics()
    agent.save_model(f"{algorithm}_stone_model.pkl")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Stone Pickaxe Agent - Stage 2')
    parser.add_argument('--algorithm', type=str, default='qlearning', 
                        choices=['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random'],
                        help='RL algorithm to use')
    parser.add_argument('--episodes', type=int, default=50, help='Number of episodes')
    parser.add_argument('--load-model', type=str, default=None, 
                        help='Path to pre-trained wood agent model to continue training')
    
    args = parser.parse_args()
    train_agent(args.algorithm, args.episodes, args.load_model)
