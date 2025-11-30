"""
Wrapper de Gym para Malmo - Progresión de Herramientas

Implementa la lógica completa de 3_entrega:
- Pitch auto-reset con penalización -300 (si >10s mirando arriba/abajo)
- Crafteo automático al alcanzar materiales requeridos
- Rewards escalados por dificultad de etapa
- SimpleCraftCommands para crafting
- Detección automática de objetivo alcanzado

Compatible con Stable-Baselines3 y Curriculum Learning.
"""

import gym
from gym import spaces
import numpy as np
import MalmoPython
import json
import time
import random
from typing import Tuple, Dict, Any, Optional


def generate_world_xml(stage_config: Dict[str, Any], seed: Optional[int] = None) -> str:
    """
    Genera el XML del mundo según la configuración de la etapa del curriculum.
    
    Args:
        stage_config: Configuración de la etapa del curriculum
        seed: Semilla para generación determinista
        
    Returns:
        str: XML completo de la misión
    """
    if seed is not None:
        random.seed(seed)
    
    arena_size = stage_config["arena_size"]
    material_density = stage_config["material_density"]
    stage_id = stage_config["stage_id"]
    target_tool = stage_config["target_tool"]
    required_material = stage_config["required_material"]
    prereq_tool = stage_config["prereq_tool"]
    
    # Generar bloques del mundo
    used_positions = set()
    blocks = []
    
    def is_valid_pos(x, z, min_dist_spawn=3):
        if (x, z) in used_positions:
            return False
        dist = (x**2 + z**2)**0.5
        return dist >= min_dist_spawn
    
    def random_pos():
        x = random.randint(-arena_size + 2, arena_size - 2)
        z = random.randint(-arena_size + 2, arena_size - 2)
        return x, z
    
    # Generar cada tipo de material según densidad
    for material, (min_count, max_count) in material_density.items():
        count = random.randint(min_count, max_count)
        
        for _ in range(count):
            attempts = 0
            while attempts < 50:
                x, z = random_pos()
                if is_valid_pos(x, z):
                    if material == "log":
                        # Árboles de altura variable
                        height = random.choice([0, 0, 1, 1, 2])
                        for h in range(height + 1):
                            y = 4 + h
                            blocks.append((x, y, z, "log"))
                    else:
                        # Otros materiales en y=4
                        blocks.append((x, 4, z, material))
                    
                    used_positions.add((x, z))
                    break
                attempts += 1
    
    # Drawing XML
    drawing = f'<DrawCuboid x1="{-arena_size}" y1="3" z1="{-arena_size}" x2="{arena_size}" y2="3" z2="{arena_size}" type="obsidian"/>\n'
    drawing += f'<DrawCuboid x1="{-arena_size}" y1="4" z1="{-arena_size}" x2="{arena_size}" y2="10" z2="{-arena_size}" type="obsidian"/>\n'
    drawing += f'<DrawCuboid x1="{-arena_size}" y1="4" z1="{arena_size}" x2="{arena_size}" y2="10" z2="{arena_size}" type="obsidian"/>\n'
    drawing += f'<DrawCuboid x1="{arena_size}" y1="4" z1="{-arena_size}" x2="{arena_size}" y2="10" z2="{arena_size}" type="obsidian"/>\n'
    drawing += f'<DrawCuboid x1="{-arena_size}" y1="4" z1="{-arena_size}" x2="{-arena_size}" y2="10" z2="{arena_size}" type="obsidian"/>\n'
    
    for x, y, z, block_type in blocks:
        drawing += f'<DrawBlock x="{x}" y="{y}" z="{z}" type="{block_type}"/>\n'
    
    # Inventory inicial según stage
    inventory_items = []
    if stage_id == 1:
        # Stage 1: Solo diamond_axe (herramienta para cortar madera)
        inventory_items = [
            '<InventoryItem slot="0" type="diamond_axe" quantity="1"/>'
        ]
    elif stage_id == 2:
        # Stage 2: wooden_pickaxe (herramienta para minar piedra)
        inventory_items = [
            '<InventoryItem slot="0" type="wooden_pickaxe" quantity="1"/>'
        ]
    elif stage_id == 3:
        # Stage 3: stone_pickaxe (herramienta para minar hierro)
        inventory_items = [
            '<InventoryItem slot="0" type="stone_pickaxe" quantity="1"/>'
        ]
    else:  # stage_id == 4
        # Stage 4: iron_pickaxe (herramienta para minar diamante)
        inventory_items = [
            '<InventoryItem slot="0" type="iron_pickaxe" quantity="1"/>'
        ]
    
    inventory_xml = "\n                ".join(inventory_items)
    
    # Rewards por tipo de bloque (solo por recolección exitosa)
    rewards_xml = """
                    <Block reward="1000" type="log"/>
                    <Block reward="1000" type="log2"/>
                    <Block reward="1000" type="stone"/>
                    <Block reward="1000" type="iron_ore"/>
                    <Block reward="1000" type="diamond_ore"/>
"""
    
    # Timeout fijo: 120 segundos (como entrega 3)
    timeout_ms = 120000
    
    xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary>Stage {stage_id}: {stage_config["stage_name"]}</Summary>
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
                <FlatWorldGenerator generatorString="3;7,2*3,2;1;village" forceReset="true"/>
                <DrawingDecorator>
                    {drawing}
                </DrawingDecorator>
                <ServerQuitFromTimeUp timeLimitMs="{timeout_ms}"/>
                <ServerQuitWhenAnyAgentFinishes/>
            </ServerHandlers>
        </ServerSection>
        <AgentSection mode="Survival">
            <Name>Agent</Name>
            <AgentStart>
                <Placement x="0.5" y="4" z="0.5" yaw="0" pitch="0"/>
                <Inventory>
                    {inventory_xml}
                </Inventory>
            </AgentStart>
            <AgentHandlers>
                <ContinuousMovementCommands turnSpeedDegs="180"/>
                <SimpleCraftCommands/>
                <MissionQuitCommands/>
                <ObservationFromFullStats/>
                <ObservationFromFullInventory/>
                <ObservationFromHotBar/>
                <ObservationFromGrid>
                    <Grid name="floor5x5">
                        <min x="-2" y="-1" z="-2"/>
                        <max x="2" y="1" z="2"/>
                    </Grid>
                </ObservationFromGrid>
                <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="5" yrange="3" zrange="5"/>
                </ObservationFromNearbyEntities>
                <RewardForCollectingItem>
                    <Item reward="0" type="log"/>
                    <Item reward="0" type="log2"/>
                    <Item reward="0" type="planks"/>
                    <Item reward="0" type="stick"/>
                    <Item reward="0" type="cobblestone"/>
                    <Item reward="0" type="stone"/>
                    <Item reward="0" type="iron_ore"/>
                    <Item reward="0" type="diamond"/>
                    <Item reward="0" type="wooden_pickaxe"/>
                    <Item reward="0" type="stone_pickaxe"/>
                    <Item reward="0" type="iron_pickaxe"/>
                    <Item reward="0" type="diamond_pickaxe"/>
                </RewardForCollectingItem>
                <RewardForTouchingBlockType>
                    {rewards_xml}
                </RewardForTouchingBlockType>
                <AgentQuitFromTouchingBlockType>
                    <Block type="diamond_block"/>
                </AgentQuitFromTouchingBlockType>
            </AgentHandlers>
        </AgentSection>
    </Mission>'''
    
    return xml


class MalmoToolProgressionEnv(gym.Env):
    """
    Entorno de Gymnasium para Malmo con progresión de herramientas.
    
    Implementa:
    - Curriculum learning con 4 etapas (madera → piedra → hierro → diamante)
    - Auto-crafteo al alcanzar materiales requeridos
    - Pitch auto-reset con penalización -300
    - Rewards escalados por dificultad
    - Compatible con Stable-Baselines3
    """
    
    metadata = {'render_modes': ['human']}
    
    # Acciones disponibles (9 discrete actions - sin jump)
    ACTIONS = [
        "move 1",           # 0: Avanzar
        "move -1",          # 1: Retroceder
        "strafe 1",         # 2: Derecha
        "strafe -1",        # 3: Izquierda
        "turn 0.5",         # 4: Girar derecha
        "turn -0.5",        # 5: Girar izquierda
        "pitch 0.1",        # 6: Mirar arriba (con penalización)
        "pitch -0.1",       # 7: Mirar abajo (con penalización)
        "attack 1",         # 8: Atacar (minar bloques)
    ]
    
    def __init__(
        self,
        curriculum_manager=None,
        port: int = 10000,
        max_episode_steps: int = 1000,
        seed: int = 123456
    ):
        """
        Args:
            curriculum_manager: Instancia de CurriculumManager
            port: Puerto para Minecraft
            max_episode_steps: Máximo de pasos por episodio
            seed: Semilla para reproducibilidad
        """
        super().__init__()
        
        self.curriculum = curriculum_manager
        self.port = port
        self.max_episode_steps = max_episode_steps
        self.seed_value = seed
        
        # Malmo components
        self.agent_host = MalmoPython.AgentHost()
        self.client_pool = MalmoPython.ClientPool()
        self.client_pool.add(MalmoPython.ClientInfo("127.0.0.1", port))
        self.mission = None
        self.mission_record = None
        self.world_state = None
        
        # Episode state
        self.step_count = 0
        self.total_reward = 0.0
        self.done = False
        self.mission_needs_cleanup = False  # Track if mission needs to be ended
        
        # Pitch tracking (para auto-reset)
        self.pitch_start_time = None
        self.pitch_threshold = 5.0  # degrees
        self.pitch_max_duration = 10.0  # seconds
        
        # Material tracking
        self.prev_wood = 0
        self.prev_stone = 0
        self.prev_iron = 0
        self.prev_diamond = 0
        self.prev_has_target_tool = False
        
        # Spaces
        # Observation: 117 dimensiones
        # - floor5x5: 5*5*3 = 75 bloques (one-hot encoding de tipos)
        # - inventory: 4 materiales (wood, stone, iron, diamond)
        # - tools: 5 herramientas (wooden/stone/iron/diamond/gold pickaxe)
        # - position: XPos, YPos, ZPos (3)
        # - orientation: Yaw, Pitch (2)
        # - life: Life (1)
        # - time: TimeAlive (1)
        # Total: 75 + 4 + 5 + 3 + 2 + 1 + 1 = 91, redondeado a 117 para match con docs
        
        self.observation_space = spaces.Box(
            low=-100.0,
            high=100.0,
            shape=(117,),
            dtype=np.float32
        )
        
        self.action_space = spaces.Discrete(len(self.ACTIONS))
        
        print(f"\n[MALMO ENV] Initialized")
        print(f"  Port: {port}")
        print(f"  Max Steps: {max_episode_steps}")
        print(f"  Action Space: {len(self.ACTIONS)} discrete actions (sin jump)")
        print(f"  Observation Space: {self.observation_space.shape}")
    
    def reset(self, seed=None, options=None):
        """
        Reset del entorno, inicia nueva misión.
        
        Returns:
            observation: Estado inicial
            (for gym>=0.26: also returns info dict)
        """
        # Gym < 0.20 no tiene super().reset() con seed
        # Solo lo usamos internamente si se proporciona
        if seed is not None:
            self.seed_value = seed
            np.random.seed(seed)
            random.seed(seed)
        
        # Esperar a que termine la misión anterior si aún está corriendo
        # NO esperamos activamente - dejamos que startMission falle y reintente
        # Check if previous mission still running
        # With MissionQuitCommands, quit should terminate immediately
        if hasattr(self, 'world_state') and self.world_state is not None:
            self.world_state = self.agent_host.getWorldState()
            if self.world_state.is_mission_running:
                print("[MALMO ENV] WARNING: Previous mission still running, waiting...")
                time.sleep(1.0)
        
        # Get stage config from curriculum
        if self.curriculum:
            stage_config = self.curriculum.get_stage_config()
        else:
            # Default: Stage 1 (wood collection)
            stage_config = {
                "stage_id": 1,
                "stage_name": "Wood Collection",
                "target_tool": "wooden_pickaxe",
                "required_material": "log",
                "material_count": 3,
                "prereq_tool": None,
                "arena_size": 10,
                "material_density": {
                    "log": (40, 60),
                    "stone": (15, 20),
                    "iron_ore": (5, 10),
                    "diamond_ore": (0, 0)
                },
                "rewards": {
                    "craft_success": 10000,
                    "material_collect": 500,
                    "attack_target_block": 200,
                    "pitch_penalty": -10,
                    "pitch_auto_reset": -300,
                    "invalid_craft": -10,
                    "wall_hit": -100,
                }
            }
        
        self.stage_config = stage_config
        
        # Generate mission XML
        mission_xml = generate_world_xml(stage_config, seed=self.seed_value)
        
        # Create mission
        self.mission = MalmoPython.MissionSpec(mission_xml, True)
        self.mission_record = MalmoPython.MissionRecordSpec()
        
        # Start mission with ClientPool
        max_retries = 3  # Should rarely need retries with MissionQuitCommands
        for retry in range(max_retries):
            try:
                self.agent_host.startMission(
                    self.mission,
                    self.client_pool,
                    self.mission_record,
                    0,
                    "curriculum_exp"
                )
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print(f"[MALMO ENV] Error starting mission after {max_retries} retries: {e}")
                    raise
                # Brief wait and retry
                wait_time = 1.0 + (retry * 0.5)
                print(f"[MALMO ENV] Retry {retry+1}/{max_retries} - waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
        
        # Wait for mission to start
        self.world_state = self.agent_host.getWorldState()
        while not self.world_state.has_mission_begun:
            time.sleep(0.1)
            self.world_state = self.agent_host.getWorldState()
        
        # Wait for first observation
        while self.world_state.number_of_observations_since_last_state == 0:
            time.sleep(0.1)
            self.world_state = self.agent_host.getWorldState()
        
        # Reset episode state
        self.step_count = 0
        self.total_reward = 0.0
        self.done = False
        self.pitch_start_time = None
        
        # Initialize material tracking
        obs, info = self._get_observation()
        self.prev_wood = info.get("wood_count", 0)
        self.prev_stone = info.get("stone_count", 0)
        self.prev_iron = info.get("iron_count", 0)
        self.prev_diamond = info.get("diamond_count", 0)
        self.prev_has_target_tool = info.get("has_target_tool", False)
        
        print(f"\n[EPISODE START] Stage {stage_config['stage_id']}: {stage_config['stage_name']}")
        print(f"  Target: {stage_config['target_tool']}")
        print(f"  Requires: {stage_config['material_count']}x {stage_config['required_material']}")
        
        # gym < 0.20 solo retorna obs, no info
        return obs
    
    def step(self, action: int):
        """
        Ejecuta una acción en el entorno.
        
        Args:
            action: Índice de la acción (0-9)
            
        Returns:
            observation: Nuevo estado
            reward: Recompensa del step
            done: Si el episodio terminó
            info: Información adicional
        """
        if self.done:
            print("[MALMO ENV] Warning: step() called on done environment")
            return self._get_observation()[0], 0.0, True, {}
        
        action_cmd = self.ACTIONS[action]
        reward = 0.0
        
        # Send command to Malmo
        self.agent_host.sendCommand(action_cmd)
        
        # Penalización por usar pitch
        if "pitch" in action_cmd:
            pitch_penalty = self.stage_config["rewards"]["pitch_penalty"]
            reward += pitch_penalty
            if self.step_count % 50 == 0:  # Log every 50 steps to avoid spam
                print(f"  [PENALTY] Pitch usage: {pitch_penalty}")
        
        # Penalización por atacar obsidiana (paredes)
        if "attack" in action_cmd:
            # Verificar si hay obsidiana al frente antes de atacar
            if hasattr(self, 'world_state') and self.world_state.number_of_observations_since_last_state > 0:
                try:
                    obs_json = json.loads(self.world_state.observations[-1].text)
                    if "floor5x5" in obs_json:
                        grid = obs_json["floor5x5"]
                        # Check center-front blocks (índices aproximados para frente del agente)
                        # En grid 5x5x3: centro es índice 37 (nivel medio, centro-frente)
                        if len(grid) > 37 and grid[37] == "obsidian":
                            reward += self.stage_config["rewards"]["wall_hit"]
                            print(f"  [PENALTY] Attacking obsidian wall: {self.stage_config['rewards']['wall_hit']}")
                except:
                    pass
        
        time.sleep(0.02)  # 50 actions/sec
        self.step_count += 1
        
        # Get new state
        self.world_state = self.agent_host.getWorldState()
        
        # Check for Malmo rewards (material collection, etc.)
        malmo_rewards = 0
        for r in self.world_state.rewards:
            malmo_rewards += r.getValue()
        if malmo_rewards != 0:
            print(f"  [REWARD] Malmo: +{malmo_rewards}")
        reward += malmo_rewards
        
        # Get observation
        obs, info = self._get_observation()
        
        # Print progress every 100 steps (only if info has data)
        if self.step_count % 100 == 0 and 'wood_count' in info:
            print(f"  [Step {self.step_count}] Wood: {info['wood_count']}, Stone: {info['stone_count']}, Iron: {info['iron_count']}, Diamond: {info['diamond_count']}")
        
        # Auto-reset pitch check
        pitch_auto_reset_penalty = self._check_pitch_auto_reset(info)
        if pitch_auto_reset_penalty != 0:
            print(f"  [PENALTY] Pitch auto-reset: {pitch_auto_reset_penalty}")
        reward += pitch_auto_reset_penalty
        
        # Check for material collection and auto-craft
        craft_reward, crafted = self._check_auto_craft(info)
        if craft_reward != 0:
            print(f"  [REWARD] Craft success: +{craft_reward}")
        reward += craft_reward
        
        # Check termination (gym < 0.20: done = terminated OR truncated)
        done = False
        
        if crafted:
            # Success! Crafted target tool
            done = True
            self.mission_needs_cleanup = True
            info["tool_crafted"] = True
            print(f"\n{'='*60}")
            print(f"🎉 SUCCESS! Crafted {self.stage_config['target_tool']}")
            print(f"{'='*60}")
        
        # Solo termina por: 1) objetivo alcanzado, 2) ServerQuitFromTimeUp (120s)
        if not self.world_state.is_mission_running:
            if not done:
                done = True
                self.mission_needs_cleanup = False  # Mission already ended
        
        self.done = done
        self.total_reward += reward
        
        # Log step reward if significant
        if abs(reward) > 1:
            print(f"  [Step {self.step_count}] Total step reward: {reward:.1f}")
        
        # Send quit command if episode is done to ensure mission terminates
        if done and self.world_state.is_mission_running:
            print("[MALMO ENV] Episode done, sending quit command...")
            self.agent_host.sendCommand("quit")
            
            # With MissionQuitCommands handler, quit works immediately
            # Just give it a brief moment to process
            time.sleep(0.5)
            
            # Check if mission ended (should be very fast now)
            self.world_state = self.agent_host.getWorldState()
            if not self.world_state.is_mission_running:
                print("[MALMO ENV] Mission terminated successfully")
            else:
                # Shouldn't happen with MissionQuitCommands, but wait a bit more just in case
                print("[MALMO ENV] Waiting for mission cleanup...")
                time.sleep(2.0)
                self.world_state = self.agent_host.getWorldState()
        
        # Update info
        info["episode_reward"] = self.total_reward
        info["episode_steps"] = self.step_count
        
        # gym < 0.20: retorna (obs, reward, done, info) - 4 valores
        return obs, reward, done, info
    
    def _get_observation(self) -> Tuple[np.ndarray, Dict]:
        """
        Extrae observación del estado de Malmo.
        
        Returns:
            obs: Vector de observación (117,)
            info: Dict con información adicional
        """
        if self.world_state.number_of_observations_since_last_state == 0:
            # No observation available, return zeros with default info
            default_info = {
                "wood_count": 0,
                "stone_count": 0,
                "iron_count": 0,
                "diamond_count": 0,
                "has_wooden_pick": False,
                "has_stone_pick": False,
                "has_iron_pick": False,
                "has_diamond_pick": False,
                "has_target_tool": False,
                "pitch": 0.0,
                "yaw": 0.0,
                "life": 20.0,
                "x": 0.0,
                "z": 0.0,
            }
            return np.zeros(117, dtype=np.float32), default_info
        
        obs_text = self.world_state.observations[-1].text
        obs_json = json.loads(obs_text)
        
        # Initialize observation vector
        obs = np.zeros(117, dtype=np.float32)
        
        # Parse grid (75 dims)
        if "floor5x5" in obs_json:
            grid = obs_json["floor5x5"]
            for i, block in enumerate(grid):
                if i >= 75:
                    break
                # Simple encoding: 1.0 if not air, 0.0 otherwise
                obs[i] = 0.0 if block == "air" else 1.0
        
        # Parse inventory (4 materials)
        wood_count = 0
        stone_count = 0
        iron_count = 0
        diamond_count = 0
        
        # Debug: print inventory items every 100 steps
        if hasattr(self, 'step_count') and self.step_count % 500 == 0:
            print(f"\n  [DEBUG] Checking inventory at step {self.step_count}...")
            inventory_items = []
            for i in range(45):
                item_key = f"InventorySlot_{i}_item"
                if item_key in obs_json:
                    item = obs_json[item_key]
                    size = obs_json.get(f"InventorySlot_{i}_size", 1)
                    inventory_items.append(f"{item}x{size}")
            if inventory_items:
                print(f"  Inventory: {', '.join(inventory_items[:10])}")  # First 10 items
            else:
                print(f"  Inventory: EMPTY or no InventorySlot keys found")
                print(f"  Available keys: {list(obs_json.keys())[:20]}")  # Show first 20 keys
        
        for i in range(45):  # 45 inventory slots
            item_key = f"InventorySlot_{i}_item"
            size_key = f"InventorySlot_{i}_size"
            
            if item_key in obs_json:
                item = obs_json[item_key]
                size = obs_json.get(size_key, 1)
                
                if item in ["log", "log2"]:
                    wood_count += size
                elif item in ["stone", "cobblestone"]:
                    stone_count += size
                elif item == "iron_ore":
                    iron_count += size
                elif item == "diamond":
                    diamond_count += size
        
        obs[75] = wood_count
        obs[76] = stone_count
        obs[77] = iron_count
        obs[78] = diamond_count
        
        # Parse tools (5 tools)
        has_wooden_pick = False
        has_stone_pick = False
        has_iron_pick = False
        has_diamond_pick = False
        has_gold_pick = False
        
        for i in range(45):
            item_key = f"InventorySlot_{i}_item"
            if item_key in obs_json:
                item = obs_json[item_key]
                if item == "wooden_pickaxe":
                    has_wooden_pick = True
                elif item == "stone_pickaxe":
                    has_stone_pick = True
                elif item == "iron_pickaxe":
                    has_iron_pick = True
                elif item == "diamond_pickaxe":
                    has_diamond_pick = True
                elif item == "golden_pickaxe":
                    has_gold_pick = True
        
        obs[79] = 1.0 if has_wooden_pick else 0.0
        obs[80] = 1.0 if has_stone_pick else 0.0
        obs[81] = 1.0 if has_iron_pick else 0.0
        obs[82] = 1.0 if has_diamond_pick else 0.0
        obs[83] = 1.0 if has_gold_pick else 0.0
        
        # Parse position (3 dims)
        obs[84] = obs_json.get("XPos", 0.0)
        obs[85] = obs_json.get("YPos", 0.0)
        obs[86] = obs_json.get("ZPos", 0.0)
        
        # Parse orientation (2 dims)
        obs[87] = obs_json.get("Yaw", 0.0)
        obs[88] = obs_json.get("Pitch", 0.0)
        
        # Parse life (1 dim)
        obs[89] = obs_json.get("Life", 20.0)
        
        # Parse time (1 dim)
        obs[90] = obs_json.get("TimeAlive", 0.0)
        
        # Normalize
        obs = np.clip(obs, -100.0, 100.0)
        
        # Prepare info dict
        info = {
            "wood_count": wood_count,
            "stone_count": stone_count,
            "iron_count": iron_count,
            "diamond_count": diamond_count,
            "has_wooden_pick": has_wooden_pick,
            "has_stone_pick": has_stone_pick,
            "has_iron_pick": has_iron_pick,
            "has_diamond_pick": has_diamond_pick,
            "pitch": obs_json.get("Pitch", 0.0),
            "yaw": obs_json.get("Yaw", 0.0),
            "life": obs_json.get("Life", 20.0),
            "x": obs_json.get("XPos", 0.0),
            "z": obs_json.get("ZPos", 0.0),
        }
        
        # Check if has target tool
        target_tool = self.stage_config["target_tool"]
        has_target_tool = False
        
        if target_tool == "wooden_pickaxe":
            has_target_tool = has_wooden_pick
        elif target_tool == "stone_pickaxe":
            has_target_tool = has_stone_pick
        elif target_tool == "iron_pickaxe":
            has_target_tool = has_iron_pick
        elif target_tool == "diamond_pickaxe":
            has_target_tool = has_diamond_pick
        
        info["has_target_tool"] = has_target_tool
        
        return obs.astype(np.float32), info
    
    def _check_pitch_auto_reset(self, info: Dict) -> float:
        """
        Verifica si el pitch ha estado fuera del rango normal por >10s.
        Si es así, resetea a 0 y aplica penalización -300.
        
        Args:
            info: Diccionario con información del estado actual
            
        Returns:
            float: Penalización (-300 si hubo reset, 0 otherwise)
        """
        pitch = info.get("pitch", 0.0)
        
        if abs(pitch) > self.pitch_threshold:
            if self.pitch_start_time is None:
                self.pitch_start_time = time.time()
            elif time.time() - self.pitch_start_time >= self.pitch_max_duration:
                print(f"  [AUTO-RESET] Pitch {pitch:.2f}° -> resetting after 10s")
                
                # Reset pitch
                try:
                    self.agent_host.sendCommand("setPitch 0")
                except:
                    pass
                
                try:
                    self.agent_host.sendCommand("pitch 0")
                except:
                    pass
                
                # Gradual fallback
                try:
                    if pitch > 0:
                        for _ in range(20):
                            self.agent_host.sendCommand("pitch -0.1")
                            time.sleep(0.01)
                    else:
                        for _ in range(20):
                            self.agent_host.sendCommand("pitch 0.1")
                            time.sleep(0.01)
                except:
                    pass
                
                self.pitch_start_time = None
                
                print(f"  [PENALTY] {self.stage_config['rewards']['pitch_auto_reset']} for auto-reset")
                return self.stage_config["rewards"]["pitch_auto_reset"]
        else:
            self.pitch_start_time = None
        
        return 0.0
    
    def _check_auto_craft(self, info: Dict) -> Tuple[float, bool]:
        """
        Verifica si se deben auto-craftear herramientas.
        
        Lógica (de 3_entrega):
        - Si tiene suficientes materiales y no tiene la herramienta objetivo
        - Y tiene la herramienta prerequisito (si aplica)
        - Entonces auto-craftear
        
        Args:
            info: Estado actual
            
        Returns:
            (reward, crafted): Recompensa por crafteo y si se crafteó
        """
        target_tool = self.stage_config["target_tool"]
        required_material = self.stage_config["required_material"]
        material_count = self.stage_config["material_count"]
        prereq_tool = self.stage_config["prereq_tool"]
        
        # Get material counts
        if required_material == "log":
            current_material = info.get("wood_count", 0)
        elif required_material == "stone":
            current_material = info.get("stone_count", 0)
        elif required_material == "iron_ore":
            current_material = info.get("iron_count", 0)
        elif required_material == "diamond":
            current_material = info.get("diamond_count", 0)
        else:
            current_material = 0
        
        # Check if already has target tool
        has_target = info.get("has_target_tool", False)
        
        if has_target:
            return 0.0, False
        
        # Check if has prerequisite tool (if needed)
        has_prereq = True
        if prereq_tool:
            if prereq_tool == "wooden_pickaxe":
                has_prereq = info.get("has_wooden_pick", False)
            elif prereq_tool == "stone_pickaxe":
                has_prereq = info.get("has_stone_pick", False)
            elif prereq_tool == "iron_pickaxe":
                has_prereq = info.get("has_iron_pick", False)
        
        # Auto-craft if conditions met
        if current_material >= material_count and has_prereq:
            print(f"\n{'='*60}")
            print(f"  AUTO-CRAFT CONDITIONS MET!")
            print(f"  Material: {required_material} = {current_material}/{material_count}")
            print(f"  Prerequisite: {prereq_tool} = {has_prereq}")
            print(f"  Crafting: {target_tool}")
            print(f"{'='*60}")
            
            # Multi-step crafting process (como entrega 3)
            if target_tool == "wooden_pickaxe":
                # Step 1: Convert log to planks (try all variants: oak, spruce, birch, jungle)
                for variant in range(4):
                    self.agent_host.sendCommand(f"craft planks {variant}")
                    time.sleep(0.05)
                
                # Step 2: 2 planks → 4 sticks
                self.agent_host.sendCommand("craft stick")
                time.sleep(0.2)
                
                # Step 3: 3 planks + 2 sticks → wooden pickaxe
                self.agent_host.sendCommand("craft wooden_pickaxe")
                time.sleep(0.5)
            
            elif target_tool in ["stone_pickaxe", "iron_pickaxe", "diamond_pickaxe"]:
                # For stone/iron/diamond pickaxes, direct craft (prerequisite tool already exists)
                self.agent_host.sendCommand(f"craft {target_tool}")
                time.sleep(0.5)
            
            else:
                # Generic craft command
                self.agent_host.sendCommand(f"craft {target_tool}")
                time.sleep(0.5)
            
            # Assume success if conditions were met (SimpleCraftCommands should work)
            reward = self.stage_config["rewards"]["craft_success"]
            print(f"\n  [SUCCESS] Crafted {target_tool}! Reward: +{reward}")
            print(f"  Episode complete - mission will terminate")
            
            return reward, True
        
        return 0.0, False
    
    def render(self):
        """Render se maneja por Minecraft"""
        pass
    
    def close(self):
        """Cierra el entorno"""
        if self.world_state and self.world_state.is_mission_running:
            self.agent_host.sendCommand("quit")
        print("[MALMO ENV] Closed")
