import os
import sys
import time
import json
import random
import argparse

# Add current directory to sys.path to ensure local modules can be imported
# This is necessary for the portable Python environment which might not add it automatically
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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


def generar_mundo_plano_xml(seed=None):
    """
    Generates XML for a flat world with trees, stone, and ores.
    Adapted from mundo_rl.py

    Ahora usa un RNG local basado en 'seed' para que el mundo
    sea determinista sin afectar el random global.
    """
    # RNG local (no toca random.seed global)
    rng = random.Random(seed) if seed is not None else random

    # Config - Smaller Arena, High Density
    radio = 10  # Reduced from 20
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

    # 1. Generate Wood (Very High Density: 40-60 blocks)
    # Only generate 'log' (not log2) to avoid SimpleCraftCommands crashes with acacia
    num_madera = rng.randint(40, 60)

    for _ in range(num_madera):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                altura = rng.choice([0, 0, 1, 1, 2])
                tipo = 'log'  # Only log (oak/spruce/birch/jungle), no log2 (acacia/dark_oak)
                for h in range(altura + 1):
                    y = 4 + h
                    bloques_generados.append((x, y, z, tipo))
                posiciones_usadas.add((x, z))
                break
            intentos += 1

    # 2. Generate Stone (High Density: 15-20 blocks)
    num_piedra = rng.randint(15, 20)
    for _ in range(num_piedra):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                bloques_generados.append((x, 4, z, "stone"))
                posiciones_usadas.add((x, z))
                break
            intentos += 1

    # 3. Generate Iron Ore (Medium Density: 5-10 blocks)
    num_hierro = rng.randint(5, 10)
    for _ in range(num_hierro):
        intentos = 0
        while intentos < 50:
            x, z = generar_posicion_aleatoria()
            if pos_valida(x, z):
                bloques_generados.append((x, 4, z, "iron_ore"))
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
            <Summary>Wood Gathering RL</Summary>
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
            <Name>WoodGatherer</Name>
            <AgentStart>
                <Placement x="0.5" y="4" z="0.5" yaw="0"/>
                <Inventory>
                    <!-- Diamond axe for fast wood breaking -->
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
                <MissionQuitCommands/>
                <ObservationFromRecentCommands/>
                <ObservationFromHotBar/>
                <ObservationFromFullInventory/>
                <!-- Allow instant breaking of specific blocks only -->
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
                    <Block reward="-100" type="obsidian"/>  <!-- Heavy penalty for hitting walls -->
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
    # This is the format used by ObservationFromFullInventory
    for i in range(45):
        item_key = f"InventorySlot_{i}_item"
        size_key = f"InventorySlot_{i}_size"

        if item_key in obs:
            item_type = obs[item_key]
            quantity = obs.get(size_key, 1)

            if item_type == "log":  # Only count craftable wood (not log2/acacia)
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

            if item_type == "log":  # Only count craftable wood (not log2/acacia)
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


def train_agent(algorithm="qlearning", num_episodes=50, env_seed=12345):
    """
    Entrena un agente en el entorno de recolección de madera.

    env_seed: semilla del entorno. Con el mismo valor, el layout de bloques
    (madera, piedra, hierro) será siempre el mismo entre episodios y algoritmos.
    """
    # Action space with contextual jump and pitch
    actions = [
        "move 1", "move -1",           # Forward/backward
        "strafe 1", "strafe -1",       # Left/right strafe
        "turn 1", "turn -1",           # Turn left/right
        "pitch 0.1", "pitch -0.1",     # Look up/down (small angles)
        "jump 1",                      # Jump (should use when obstacle ahead)
        "attack 1",                    # Attack/mine
        "craft_wooden_pickaxe",
        "craft_stone_pickaxe"
    ]

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

    metrics = MetricsLogger(f"{algorithm}_WoodAgent")
    agent_host = MalmoPython.AgentHost()

    print(f"Starting training with {algorithm}...")

    # Create ClientPool to support multiple ports (10000, 10001)
    client_pool = MalmoPython.ClientPool()
    client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))
    client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10001))

    # Mismo escenario de bloques para todos los episodios
    mission_xml = generar_mundo_plano_xml(seed=env_seed)

    for episode in range(num_episodes):
        agent.start_episode()
        my_mission = MalmoPython.MissionSpec(mission_xml, True)
        my_mission_record = MalmoPython.MissionRecordSpec()

        max_retries = 3
        for retry in range(max_retries):
            try:
                # Use client_pool to connect to specific ports
                agent_host.startMission(my_mission, client_pool, my_mission_record, 0, "wood_agent_exp")
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
        # Track previous inventory to detect collection
        prev_wood = 0
        prev_stone = 0
        prev_iron = 0
        # Track maximum collected (doesn't decrease when used for crafting)
        max_wood = 0
        max_stone = 0
        max_iron = 0
        action_counts = {"move": 0, "turn": 0, "attack": 0, "craft": 0}

        # Initial state
        while world_state.is_mission_running and world_state.number_of_observations_since_last_state == 0:
            world_state = agent_host.getWorldState()
            time.sleep(0.1)

        state = get_state(world_state)

        # For SARSA, we need initial action
        action = agent.choose_action(state) if state else None

        def handle_crafting(action, state, agent_host):
            """
            Handle crafting actions and return custom reward
            Returns: (success, reward, message, should_quit)
            """
            if action == "craft_wooden_pickaxe":
                _, wood, stone, iron, has_wood_pick, has_stone_pick = state
                if wood >= 3 and not has_wood_pick:
                    # SUCCESS! Agent collected 3 wood - episode complete
                    # Try to craft using SimpleCraftCommands
                    agent_host.sendCommand("craft wooden_pickaxe")
                    time.sleep(0.1)
                    return (True, 5000, "✓✓✓ SUCCESS! Collected 3 wood - Episode Complete!", True)
                else:
                    return (False, -10, "Cannot craft wooden pickaxe (need 3 wood)", False)

            elif action == "craft_stone_pickaxe":
                _, wood, stone, iron, has_wood_pick, has_stone_pick = state
                if stone >= 3 and has_wood_pick and not has_stone_pick:
                    agent_host.sendCommand("craft stone_pickaxe")
                    time.sleep(0.1)
                    return (True, 10000, "✓✓✓ SUCCESS! Crafted Stone Pickaxe!", True)
                else:
                    return (False, -10, "Cannot craft stone pickaxe (need 3 stone + wooden pickaxe)", False)

            return (False, 0, "", False)

        next_state = None  # definimos aquí para usarlo después del bucle

        while world_state.is_mission_running:
            if state and action:
                # Check if it's a crafting action
                if action.startswith("craft_"):
                    success, craft_reward, msg, should_quit = handle_crafting(action, state, agent_host)
                    if msg:
                        print(f"  {msg}")
                    total_reward += craft_reward

                    # If episode is successful, end mission
                    if should_quit and success:
                        print(f"\n{'='*60}")
                        print("🎉 EPISODE SUCCESS: Agent collected 3 wood!")
                        print(f"{'='*60}")
                        agent_host.sendCommand("quit")
                        break
                else:
                    agent_host.sendCommand(action)

                steps += 1

                # Auto-reset pitch every 20 steps to keep camera centered
                if steps % 20 == 0:
                    agent_host.sendCommand("pitch 0")  # Reset to horizontal

                # Track action type and apply contextual rewards
                if "move" in action or "strafe" in action:
                    action_counts["move"] += 1
                elif "turn" in action or "pitch" in action:
                    action_counts["turn"] += 1
                    # Penalize excessive pitch usage
                    if "pitch" in action:
                        total_reward -= 10  # Increased from -0.5
                elif "jump" in action:
                    action_counts["move"] += 1
                    # Smart jump rewards: check if there's an obstacle in front
                    if state:
                        surroundings, _, _, _, _, _ = state
                        # Check center-front block (index depends on grid layout)
                        # In a 5x5x3 grid, center front is approximately index 37
                        if len(surroundings) > 37:
                            front_block = surroundings[37] if surroundings[37] != 'air' else None
                            if front_block and front_block not in ['air', 'lava']:
                                # Good jump! There's an obstacle
                                total_reward += 50  # Increased from 2
                            else:
                                # Bad jump! Nothing to jump over
                                total_reward -= 50  # Increased from -2
                elif "attack" in action:
                    action_counts["attack"] += 1
                    # Reward for attacking valuable blocks (encourages persistence)
                    if state:
                        surroundings, _, _, _, _, _ = state
                        # Check what's in front of the agent (center-front position in 5x5x3 grid)
                        # Grid layout: 5x5 horizontal x 3 vertical = 75 blocks
                        # Center front at eye level is around index 37-40
                        if len(surroundings) > 40:
                            # Check blocks in front at different heights
                            front_blocks = [surroundings[i] for i in [37, 38, 39, 40] if i < len(surroundings)]

                            # Reward for hitting valuable blocks
                            for block in front_blocks:
                                if block in ['log', 'log2']:
                                    total_reward += 100  # Increased from 1
                                    break
                                elif block == 'stone':
                                    total_reward += 200  # Increased from 2
                                    break
                                elif block == 'iron_ore':
                                    total_reward += 300  # Increased from 3
                                    break
                elif "craft" in action:
                    action_counts["craft"] += 1

                time.sleep(0.02)  # Very fast actions (50 actions/second)

                world_state = agent_host.getWorldState()
                next_state = get_state(world_state)

                # Check if episode goal achieved (crafted wooden pickaxe)
                if next_state:
                    _, check_wood, check_stone, check_iron, has_wood_pick, has_stone_pick = next_state

                    # Show progress every 100 steps
                    if steps % 100 == 0 and check_wood > 0:
                        print(f"  [Progress] Wood: {check_wood}/3, Has Pick: {has_wood_pick}")

                    # Auto-craft when has 3+ wood but no pickaxe yet
                    if check_wood >= 3 and not has_wood_pick:
                        print(f"\n  >> Auto-crafting wooden pickaxe (Wood: {check_wood})...")

                        # Update max_wood before crafting (wood will be consumed)
                        max_wood = max(max_wood, check_wood)

                        # Step 1: Convert log to planks (only supported variants)
                        # Try log variants: 0=oak, 1=spruce, 2=birch, 3=jungle
                        for variant in range(4):
                            agent_host.sendCommand(f"craft planks {variant}")
                            time.sleep(0.05)

                        # Step 2: 2 planks → 4 sticks
                        agent_host.sendCommand("craft stick")
                        time.sleep(0.2)

                        # Step 3: 3 planks + 2 sticks → wooden pickaxe
                        agent_host.sendCommand("craft wooden_pickaxe")
                        time.sleep(0.3)

                        # Verify crafting
                        world_state = agent_host.getWorldState()
                        if world_state.number_of_observations_since_last_state > 0:
                            verify_obs = json.loads(world_state.observations[-1].text)
                            verify_has_pick = False
                            for i in range(45):
                                item_key = f"InventorySlot_{i}_item"
                                if item_key in verify_obs and verify_obs[item_key] == "wooden_pickaxe":
                                    verify_has_pick = True
                                    break

                            if verify_has_pick:
                                print(f"\n{'='*60}")
                                print(f"🎉 SUCCESS! Crafted wooden pickaxe - Episode complete!")
                                print(f"{'='*60}")
                                total_reward += 10000  # Massive success reward

                                # Update next_state to reflect post-crafting inventory
                                world_state = agent_host.getWorldState()
                                next_state = get_state(world_state)

                                agent_host.sendCommand("quit")
                                break
                            else:
                                print("  ⚠ Warning: Pickaxe not confirmed in inventory")

                reward = sum(r.getValue() for r in world_state.rewards)

                # Track collection by inventory changes (more reliable than rewards)
                if next_state:
                    _, cur_wood, cur_stone, cur_iron, _, _ = next_state

                    # Detect inventory increases
                    if cur_wood > prev_wood:
                        wood_collected += (cur_wood - prev_wood)
                        print(f"  [COLLECT] +{cur_wood - prev_wood} Wood! Total: {wood_collected}")
                    if cur_stone > prev_stone:
                        stone_collected += (cur_stone - prev_stone)
                        print(f"  [COLLECT] +{cur_stone - prev_stone} Stone! Total: {stone_collected}")
                    if cur_iron > prev_iron:
                        iron_collected += (cur_iron - prev_iron)
                        print(f"  [COLLECT] +{cur_iron - prev_iron} Iron! Total: {iron_collected}")

                    # Track maximum collected (for final metrics)
                    max_wood = max(max_wood, wood_collected)
                    max_stone = max(max_stone, stone_collected)
                    max_iron = max(max_iron, iron_collected)

                    # Update previous counts
                    prev_wood = cur_wood
                    prev_stone = cur_stone
                    prev_iron = cur_iron

                # Debug: Show rewards when they occur
                reward = sum(r.getValue() for r in world_state.rewards)
                if reward != 0:
                    print(f"  [REWARD] Step {steps}: {reward}")

                total_reward += reward

                if next_state:
                    # For SARSA, learn returns the next action
                    # For others, it returns None and we choose it here
                    if algorithm == "sarsa":
                        next_action = agent.learn(state, action, reward, next_state, done=False)
                        action = next_action
                    else:
                        agent.learn(state, action, reward, next_state, done=False)
                        action = agent.choose_action(next_state)

                    state = next_state
                else:
                    # Mission might have ended or no obs
                    if not world_state.is_mission_running:
                        agent.learn(state, action, reward, state, done=True)  # Terminal update
            else:
                world_state = agent_host.getWorldState()
                state = get_state(world_state)
                if state:
                    action = agent.choose_action(state)

        # Check if episode was successful by checking if wooden pickaxe is in inventory
        episode_success = False
        final_wood_count = 0

        if next_state:
            _, final_wood_count, _, _, has_wooden_pick, _ = next_state
            if has_wooden_pick:
                episode_success = True

        # Fallback: also check by reward if state wasn't captured
        if not episode_success and total_reward >= 10000:
            episode_success = True

        print(f"Episode {episode} ended. Reward: {total_reward}, Wood in inventory: {final_wood_count}, Wood collected: {max_wood}, Stone: {max_stone}, Iron: {max_iron}, Success: {episode_success}")
        metrics.log_episode(episode, steps, max_wood, total_reward, agent.epsilon, action_counts)
        agent.end_episode()
        agent.save_model(f"{algorithm}_model.pkl")
        time.sleep(0.5)

    metrics.plot_metrics()
    agent.save_model(f"{algorithm}_model.pkl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Wood Gathering Agent')
    parser.add_argument('--algorithm', type=str, default='qlearning',
                        choices=['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random'],
                        help='RL algorithm to use')
    parser.add_argument('--episodes', type=int, default=50, help='Number of episodes')
    parser.add_argument('--env-seed', type=int, default=12345,
                        help='Environment seed (fixed layout of blocks)')

    args = parser.parse_args()
    train_agent(args.algorithm, args.episodes, args.env_seed)
