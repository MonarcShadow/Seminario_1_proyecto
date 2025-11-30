"""
Utilidades y helpers para entrenamiento de RL en Malmo.
"""

import numpy as np
from stable_baselines3.common.callbacks import BaseCallback
from typing import Optional


def get_mission_xml() -> str:
    """
    Retorna el XML de la misión de Malmo.
    
    Este XML define el entorno, objetivos, observaciones, etc.
    Los placeholders (ARENA_WIDTH, etc.) son reemplazados por el curriculum manager.
    """
    
    mission_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    
      <About>
        <Summary>Wood Collection with Deep RL</Summary>
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
          <FlatWorldGenerator generatorString="3;7,2*3,2;1;village"/>
          
          <DrawingDecorator>
            <!-- Arena obsidiana 20x20 (o tamaño variable según curriculum) -->
            <DrawCuboid x1="-10" y1="4" z1="-10" x2="10" y2="10" z2="10" type="obsidian"/>
            <DrawCuboid x1="-9" y1="4" z1="-9" x2="9" y2="9" z2="9" type="air"/>
            <DrawCuboid x1="-9" y1="4" z1="-9" x2="9" y2="4" z2="9" type="grass"/>
            
            <!-- Árboles generados aleatoriamente -->
            <!-- El número de árboles es controlado por el curriculum -->
            <DrawLine x1="-5" y1="4" z1="-5" x2="-5" y2="7" z2="-5" type="log"/>
            <DrawLine x1="-5" y1="7" z1="-5" x2="-5" y2="8" z2="-5" type="leaves"/>
            
            <DrawLine x1="5" y1="4" z1="5" x2="5" y2="6" z2="5" type="log"/>
            <DrawLine x1="5" y1="6" z1="5" x2="5" y2="7" z2="5" type="leaves"/>
            
            <DrawLine x1="-3" y1="4" z1="7" x2="-3" y2="8" z2="7" type="log"/>
            <DrawCuboid x1="-4" y1="8" z1="6" x2="-2" y2="9" z2="8" type="leaves"/>
            
            <DrawLine x1="6" y1="4" z1="-6" x2="6" y2="7" z2="-6" type="log"/>
            <DrawCuboid x1="5" y1="7" z1="-7" x2="7" y2="8" z2="-5" type="leaves"/>
          </DrawingDecorator>
          
          <ServerQuitFromTimeUp timeLimitMs="120000"/>
          <ServerQuitWhenAnyAgentFinishes/>
        </ServerHandlers>
      </ServerSection>
      
      <AgentSection mode="Survival">
        <Name>WoodCollector</Name>
        <AgentStart>
          <Placement x="0.5" y="5.0" z="0.5" yaw="0" pitch="0"/>
          <Inventory>
            <InventoryItem slot="0" type="diamond_axe"/>
          </Inventory>
        </AgentStart>
        
        <AgentHandlers>
          <!-- Comandos de movimiento -->
          <ContinuousMovementCommands turnSpeedDegs="180"/>
          <AbsoluteMovementCommands/>
          
          <!-- Comandos discretos -->
          <DiscreteMovementCommands/>
          <InventoryCommands/>
          <SimpleCraftCommands/>
          
          <!-- Observaciones -->
          <ObservationFromFullStats/>
          <ObservationFromHotBar/>
          <ObservationFromRay/>
          <ObservationFromNearbyEntities>
            <Range name="entities" xrange="40" yrange="10" zrange="40"/>
          </ObservationFromNearbyEntities>
          
          <!-- Grid de bloques 3x3x3 alrededor del agente -->
          <ObservationFromGrid>
            <Grid name="grid">
              <min x="-1" y="-1" z="-1"/>
              <max x="1" y="1" z="1"/>
            </Grid>
          </ObservationFromGrid>
          
          <!-- Video frames (opcional para debugging) -->
          <!-- <VideoProducer want_depth="false">
            <Width>640</Width>
            <Height>480</Height>
          </VideoProducer> -->
          
          <!-- Recompensas (manejadas por el wrapper) -->
          <RewardForCollectingItem>
            <Item type="log" reward="100"/>
            <Item type="log2" reward="100"/>
          </RewardForCollectingItem>
          
          <AgentQuitFromReachingCommandQuota total="1500"/>
        </AgentHandlers>
      </AgentSection>
    </Mission>
    """
    
    return mission_xml


class CurriculumCallback(BaseCallback):
    """
    Callback para manejar el progreso del curriculum learning durante el entrenamiento.
    """
    
    def __init__(self, curriculum_manager, env, verbose=0):
        super(CurriculumCallback, self).__init__(verbose)
        self.curriculum_manager = curriculum_manager
        self.env = env
        self.episode_count = 0
        self.episode_rewards = []
        self.episode_successes = []
        
    def _on_step(self) -> bool:
        """
        Llamado después de cada paso en el entorno.
        """
        # Verificar si terminó un episodio
        if self.locals.get('dones')[0]:
            self.episode_count += 1
            
            # Obtener info del episodio
            info = self.locals.get('infos')[0]
            wood_collected = info.get('wood_collected', 0)
            
            # Determinar si fue exitoso según objetivo de la etapa
            stage = self.curriculum_manager.get_current_stage()
            success = wood_collected >= stage.wood_goal
            
            # Registrar en curriculum manager
            self.curriculum_manager.record_episode(success, wood_collected)
            
            # Logging
            if self.verbose > 0 and self.episode_count % 10 == 0:
                stage_info = self.curriculum_manager.get_stage_info()
                print(f"\nEpisode {self.episode_count}")
                print(f"  Stage: {stage_info['stage_name']}")
                print(f"  Wood collected: {wood_collected}/{stage.wood_goal}")
                print(f"  Success rate: {stage_info['recent_success_rate']:.2%}")
                
        return True
        
    def _on_rollout_end(self) -> None:
        """
        Llamado al final de cada rollout (conjunto de episodios).
        """
        # Aquí se podría actualizar el entorno si cambió la etapa
        # En la práctica, esto requiere reiniciar el entorno, lo cual
        # Stable-Baselines3 maneja automáticamente en el siguiente reset
        pass


class EpisodeLogger:
    """
    Logger simple para rastrear métricas por episodio.
    """
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.episodes = []
        
        # Crear archivo con headers
        with open(log_file, 'w') as f:
            f.write("Episode,Steps,WoodCollected,TotalReward,Success,StageIndex,StageName\n")
    
    def log_episode(
        self,
        episode: int,
        steps: int,
        wood_collected: int,
        total_reward: float,
        success: bool,
        stage_index: int,
        stage_name: str
    ):
        """Log un episodio completo"""
        with open(self.log_file, 'a') as f:
            f.write(f"{episode},{steps},{wood_collected},{total_reward:.2f},"
                   f"{int(success)},{stage_index},{stage_name}\n")
                   
        self.episodes.append({
            'episode': episode,
            'steps': steps,
            'wood_collected': wood_collected,
            'total_reward': total_reward,
            'success': success,
            'stage_index': stage_index,
            'stage_name': stage_name
        })


def print_network_architecture(model):
    """
    Imprime la arquitectura de las redes neuronales del modelo.
    """
    print("\n" + "="*60)
    print("NETWORK ARCHITECTURE")
    print("="*60)
    
    if hasattr(model, 'policy'):
        policy = model.policy
        
        # Actor network
        if hasattr(policy, 'action_net'):
            print("\nActor Network (Policy):")
            print(policy.action_net)
            
        # Critic network
        if hasattr(policy, 'value_net'):
            print("\nCritic Network (Value Function):")
            print(policy.value_net)
            
        # Feature extractor
        if hasattr(policy, 'features_extractor'):
            print("\nFeature Extractor:")
            print(policy.features_extractor)
            
    print("="*60 + "\n")


def count_parameters(model) -> dict:
    """
    Cuenta los parámetros entrenables del modelo.
    
    Returns:
        Dict con número de parámetros por componente
    """
    params = {
        'total': 0,
        'actor': 0,
        'critic': 0,
        'features': 0
    }
    
    if hasattr(model, 'policy'):
        policy = model.policy
        
        # Total parameters
        params['total'] = sum(p.numel() for p in policy.parameters() if p.requires_grad)
        
        # Actor parameters
        if hasattr(policy, 'action_net'):
            params['actor'] = sum(p.numel() for p in policy.action_net.parameters() if p.requires_grad)
            
        # Critic parameters
        if hasattr(policy, 'value_net'):
            params['critic'] = sum(p.numel() for p in policy.value_net.parameters() if p.requires_grad)
            
        # Feature extractor parameters
        if hasattr(policy, 'features_extractor'):
            params['features'] = sum(p.numel() for p in policy.features_extractor.parameters() if p.requires_grad)
            
    return params


def compute_metrics_from_logs(log_file: str) -> dict:
    """
    Calcula métricas a partir del archivo de logs.
    """
    import pandas as pd
    
    df = pd.read_csv(log_file)
    
    metrics = {
        'total_episodes': len(df),
        'avg_reward': df['TotalReward'].mean(),
        'avg_steps': df['Steps'].mean(),
        'avg_wood': df['WoodCollected'].mean(),
        'success_rate': df['Success'].mean(),
        'max_wood': df['WoodCollected'].max(),
        'min_steps_success': df[df['Success'] == 1]['Steps'].min() if any(df['Success']) else None
    }
    
    # Métricas por etapa
    if 'StageIndex' in df.columns:
        stage_metrics = df.groupby('StageIndex').agg({
            'Success': 'mean',
            'WoodCollected': 'mean',
            'TotalReward': 'mean',
            'Steps': 'mean'
        }).to_dict('index')
        
        metrics['by_stage'] = stage_metrics
        
    return metrics


def format_time(seconds: float) -> str:
    """Formatear segundos a HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
