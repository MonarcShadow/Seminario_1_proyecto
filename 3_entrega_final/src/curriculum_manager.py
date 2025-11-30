"""
Curriculum Learning Manager - Tool Progression System

Sistema de aprendizaje curricular basado en progresión de herramientas:
Stage 1: Recolectar 3 madera → craftear pico de madera
Stage 2: Recolectar 3 piedra → craftear pico de piedra (con modelo pre-entrenado de Stage 1)
Stage 3: Recolectar 3 hierro → craftear pico de hierro (con modelo pre-entrenado de Stage 2)
Stage 4: Recolectar 1 diamante → craftear pico de diamante (con modelo pre-entrenado de Stage 3)

Basado en el sistema de 3_entrega con auto-crafteo y penalizaciones por pitch.
"""

import os
import json
from typing import Dict, Tuple, Optional
import numpy as np


class CurriculumStage:
    """Representa una etapa del curriculum"""
    
    def __init__(
        self,
        stage_id: int,
        name: str,
        target_tool: str,
        required_material: str,
        material_count: int,
        prereq_tool: Optional[str],
        success_threshold: float = 0.5,
        episodes_per_stage: int = 500
    ):
        self.stage_id = stage_id
        self.name = name
        self.target_tool = target_tool
        self.required_material = required_material
        self.material_count = material_count
        self.prereq_tool = prereq_tool  # Tool needed before crafting (None for first stage)
        self.success_threshold = success_threshold
        self.episodes_per_stage = episodes_per_stage
        
        # Tracking metrics
        self.episodes_completed = 0
        self.successes = 0
        self.total_reward = 0.0
        self.success_history = []  # Last 50 episodes


class CurriculumManager:
    """
    Gestiona la progresión del curriculum de herramientas.
    
    Progresión:
    1. Madera (Stage 1): Recolecta 3 wood → craftea wooden_pickaxe
    2. Piedra (Stage 2): Recolecta 3 stone → craftea stone_pickaxe (requiere wooden_pickaxe)
    3. Hierro (Stage 3): Recolecta 3 iron → craftea iron_pickaxe (requiere stone_pickaxe)
    4. Diamante (Stage 4): Recolecta 1 diamond → craftea diamond_pickaxe (requiere iron_pickaxe)
    """
    
    def __init__(self, start_stage: int = 1, log_dir: str = "curriculum_logs"):
        """
        Args:
            start_stage: Etapa inicial (1-4)
            log_dir: Directorio para logs del curriculum
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Definir las 4 etapas del curriculum
        # NOTA: episodes_per_stage reducido a 30 para testing rápido
        # Para producción, usar 500+ episodios por stage
        self.stages = [
            CurriculumStage(
                stage_id=1,
                name="Wood Collection",
                target_tool="wooden_pickaxe",
                required_material="log",
                material_count=3,
                prereq_tool=None,  # No requiere herramienta previa
                success_threshold=0.6,  # 60% success rate
                episodes_per_stage=30  # Reducido de 500 para testing
            ),
            CurriculumStage(
                stage_id=2,
                name="Stone Collection",
                target_tool="stone_pickaxe",
                required_material="stone",
                material_count=3,
                prereq_tool="wooden_pickaxe",
                success_threshold=0.55,  # 55% success rate
                episodes_per_stage=30  # Reducido de 500 para testing
            ),
            CurriculumStage(
                stage_id=3,
                name="Iron Collection",
                target_tool="iron_pickaxe",
                required_material="iron_ore",
                material_count=3,
                prereq_tool="stone_pickaxe",
                success_threshold=0.50,  # 50% success rate (más difícil)
                episodes_per_stage=30  # Reducido de 600 para testing
            ),
            CurriculumStage(
                stage_id=4,
                name="Diamond Collection",
                target_tool="diamond_pickaxe",
                required_material="diamond",
                material_count=1,
                prereq_tool="iron_pickaxe",
                success_threshold=0.45,  # 45% success rate (muy difícil)
                episodes_per_stage=30  # Reducido de 800 para testing
            )
        ]
        
        self.current_stage_idx = start_stage - 1
        self.total_episodes = 0
        
        print(f"\n{'='*70}")
        print(f"CURRICULUM MANAGER INITIALIZED")
        print(f"{'='*70}")
        print(f"Starting at Stage {start_stage}: {self.current_stage.name}")
        print(f"Target: Craft {self.current_stage.target_tool}")
        print(f"Requires: {self.current_stage.material_count}x {self.current_stage.required_material}")
        if self.current_stage.prereq_tool:
            print(f"Prerequisite: {self.current_stage.prereq_tool}")
        print(f"{'='*70}\n")
    
    @property
    def current_stage(self) -> CurriculumStage:
        """Retorna la etapa actual"""
        return self.stages[self.current_stage_idx]
    
    def log_episode(self, success: bool, total_reward: float, episode_info: Dict) -> bool:
        """
        Registra el resultado de un episodio.
        
        Args:
            success: Si se completó el objetivo (craftear la herramienta)
            total_reward: Recompensa total del episodio
            episode_info: Información adicional del episodio
            
        Returns:
            bool: True si se avanzó a la siguiente etapa
        """
        stage = self.current_stage
        stage.episodes_completed += 1
        self.total_episodes += 1
        
        if success:
            stage.successes += 1
        
        stage.total_reward += total_reward
        stage.success_history.append(1 if success else 0)
        
        # Mantener solo últimos 50 episodios
        if len(stage.success_history) > 50:
            stage.success_history.pop(0)
        
        # Calcular success rate de últimos episodios
        recent_success_rate = np.mean(stage.success_history) if stage.success_history else 0.0
        overall_success_rate = stage.successes / stage.episodes_completed if stage.episodes_completed > 0 else 0.0
        
        # Log progress
        if stage.episodes_completed % 10 == 0:
            print(f"\n[CURRICULUM] Stage {stage.stage_id}: {stage.name}")
            print(f"  Episodes: {stage.episodes_completed}/{stage.episodes_per_stage}")
            print(f"  Success Rate (overall): {overall_success_rate:.1%}")
            print(f"  Success Rate (last 50): {recent_success_rate:.1%}")
            print(f"  Avg Reward: {stage.total_reward / stage.episodes_completed:.1f}")
        
        # Verificar si avanzar a siguiente etapa
        advanced = False
        if self._should_advance(stage, recent_success_rate, overall_success_rate):
            advanced = self._advance_stage()
        
        # Guardar checkpoint
        self._save_checkpoint()
        
        return advanced
    
    def _should_advance(self, stage: CurriculumStage, recent_sr: float, overall_sr: float) -> bool:
        """
        Determina si debe avanzar a la siguiente etapa.
        
        Condiciones:
        1. Ha completado suficientes episodios (min 30% del target para testing)
        2. Success rate reciente >= threshold O success rate overall >= threshold + 5%
        """
        if self.current_stage_idx >= len(self.stages) - 1:
            return False  # Ya está en la última etapa
        
        min_episodes = int(stage.episodes_per_stage * 0.3)  # Reducido de 0.5 a 0.3 para testing
        has_enough_episodes = stage.episodes_completed >= min_episodes
        
        # Success rate criterio: reciente >= threshold O overall >= threshold + margen
        meets_success_threshold = (
            recent_sr >= stage.success_threshold or 
            overall_sr >= (stage.success_threshold + 0.05)
        )
        
        return has_enough_episodes and meets_success_threshold
    
    def _advance_stage(self) -> bool:
        """Avanza a la siguiente etapa del curriculum"""
        if self.current_stage_idx >= len(self.stages) - 1:
            return False
        
        old_stage = self.current_stage
        self.current_stage_idx += 1
        new_stage = self.current_stage
        
        print(f"\n{'='*70}")
        print(f"🎓 CURRICULUM ADVANCEMENT!")
        print(f"{'='*70}")
        print(f"Completed Stage {old_stage.stage_id}: {old_stage.name}")
        print(f"  Total Episodes: {old_stage.episodes_completed}")
        print(f"  Success Rate: {old_stage.successes / old_stage.episodes_completed:.1%}")
        print(f"  Avg Reward: {old_stage.total_reward / old_stage.episodes_completed:.1f}")
        print(f"\nAdvancing to Stage {new_stage.stage_id}: {new_stage.name}")
        print(f"  Target: Craft {new_stage.target_tool}")
        print(f"  Requires: {new_stage.material_count}x {new_stage.required_material}")
        if new_stage.prereq_tool:
            print(f"  Prerequisite: {new_stage.prereq_tool}")
        print(f"{'='*70}\n")
        
        return True
    
    def get_stage_config(self) -> Dict:
        """
        Retorna la configuración de la etapa actual para el entorno.
        
        Returns:
            Dict con configuración del XML y rewards
        """
        stage = self.current_stage
        
        config = {
            "stage_id": stage.stage_id,
            "stage_name": stage.name,
            "target_tool": stage.target_tool,
            "required_material": stage.required_material,
            "material_count": stage.material_count,
            "prereq_tool": stage.prereq_tool,
            
            # Rewards específicos por etapa
            "rewards": {
                "craft_success": 10000,  # Craftear la herramienta objetivo
                "material_collect": 500 * stage.stage_id,  # Aumenta con dificultad
                "attack_target_block": 200 * stage.stage_id,
                "pitch_penalty": -10,  # Penalización por usar pitch
                "pitch_auto_reset": -300,  # Penalización por auto-reset (>10s mirando arriba/abajo)
                "invalid_craft": -10,  # Intentar craftear sin materiales
                "wall_hit": -100,  # Golpear obsidiana
            },
            
            # XML generation params
            "arena_size": 10,  # Tamaño fijo del mundo
            "material_density": self._get_material_density(stage.stage_id),
        }
        
        return config
    
    def _get_material_density(self, stage_id: int) -> Dict[str, Tuple[int, int]]:
        """
        Retorna la densidad de materiales para cada etapa.
        
        Returns:
            Dict con rangos (min, max) de bloques por tipo
        """
        if stage_id == 1:  # Wood
            return {
                "log": (40, 60),      # Alta densidad de madera
                "stone": (15, 20),    # Piedra presente
                "iron_ore": (5, 10),  # Hierro presente
                "diamond_ore": (0, 0) # Sin diamantes
            }
        elif stage_id == 2:  # Stone
            return {
                "log": (10, 15),      # Poca madera (ya tiene pico)
                "stone": (30, 40),    # Alta densidad de piedra
                "iron_ore": (8, 12),  # Hierro presente
                "diamond_ore": (0, 0) # Sin diamantes
            }
        elif stage_id == 3:  # Iron
            return {
                "log": (5, 8),        # Muy poca madera
                "stone": (15, 20),    # Piedra moderada
                "iron_ore": (20, 30), # Alta densidad de hierro
                "diamond_ore": (2, 4) # Aparecen diamantes (preview)
            }
        else:  # stage_id == 4, Diamond
            return {
                "log": (3, 5),        # Mínima madera
                "stone": (10, 15),    # Poca piedra
                "iron_ore": (10, 15), # Hierro moderado
                "diamond_ore": (3, 6) # Baja densidad de diamantes (difícil)
            }
    
    def get_pretrained_model_path(self) -> Optional[str]:
        """
        Retorna el path del modelo pre-entrenado de la etapa anterior.
        
        Returns:
            str: Path al modelo o None si es la primera etapa
        """
        if self.current_stage_idx == 0:
            return None  # Primera etapa, no hay modelo previo
        
        prev_stage = self.stages[self.current_stage_idx - 1]
        model_path = os.path.join("models", f"stage_{prev_stage.stage_id}_{prev_stage.target_tool}.zip")
        
        if os.path.exists(model_path):
            print(f"\n[CURRICULUM] Loading pretrained model from Stage {prev_stage.stage_id}")
            print(f"  Path: {model_path}")
            return model_path
        else:
            print(f"\n[CURRICULUM] Warning: Pretrained model not found at {model_path}")
            print(f"  Starting Stage {self.current_stage.stage_id} from scratch")
            return None
    
    def _save_checkpoint(self):
        """Guarda el estado del curriculum"""
        checkpoint_path = os.path.join(self.log_dir, "curriculum_checkpoint.json")
        
        data = {
            "current_stage_idx": self.current_stage_idx,
            "total_episodes": self.total_episodes,
            "stages": []
        }
        
        for stage in self.stages:
            stage_data = {
                "stage_id": stage.stage_id,
                "name": stage.name,
                "episodes_completed": stage.episodes_completed,
                "successes": stage.successes,
                "total_reward": stage.total_reward,
                "success_history": stage.success_history
            }
            data["stages"].append(stage_data)
        
        with open(checkpoint_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_checkpoint(self, checkpoint_path: str):
        """Carga el estado del curriculum desde un checkpoint"""
        if not os.path.exists(checkpoint_path):
            print(f"[CURRICULUM] Checkpoint not found: {checkpoint_path}")
            return
        
        with open(checkpoint_path, 'r') as f:
            data = json.load(f)
        
        self.current_stage_idx = data["current_stage_idx"]
        self.total_episodes = data["total_episodes"]
        
        for stage_data in data["stages"]:
            stage = self.stages[stage_data["stage_id"] - 1]
            stage.episodes_completed = stage_data["episodes_completed"]
            stage.successes = stage_data["successes"]
            stage.total_reward = stage_data["total_reward"]
            stage.success_history = stage_data["success_history"]
        
        print(f"\n[CURRICULUM] Loaded checkpoint")
        print(f"  Current Stage: {self.current_stage.stage_id} - {self.current_stage.name}")
        print(f"  Total Episodes: {self.total_episodes}")
    
    def get_summary(self) -> str:
        """Retorna un resumen del progreso del curriculum"""
        lines = [
            "\n" + "="*70,
            "CURRICULUM PROGRESS SUMMARY",
            "="*70,
        ]
        
        for i, stage in enumerate(self.stages):
            status = "✓ COMPLETED" if i < self.current_stage_idx else \
                     "→ CURRENT" if i == self.current_stage_idx else \
                     "  PENDING"
            
            lines.append(f"\nStage {stage.stage_id}: {stage.name} [{status}]")
            lines.append(f"  Target: {stage.target_tool}")
            
            if stage.episodes_completed > 0:
                sr = stage.successes / stage.episodes_completed
                avg_rew = stage.total_reward / stage.episodes_completed
                lines.append(f"  Episodes: {stage.episodes_completed}")
                lines.append(f"  Success Rate: {sr:.1%}")
                lines.append(f"  Avg Reward: {avg_rew:.1f}")
        
        lines.append("="*70)
        return "\n".join(lines)


# Callback para Stable-Baselines3
class CurriculumCallback:
    """
    Callback para integrar CurriculumManager con Stable-Baselines3.
    
    Se llama después de cada episodio para actualizar el curriculum.
    """
    
    def __init__(self, curriculum_manager: CurriculumManager):
        self.curriculum = curriculum_manager
        self.episode_rewards = []
        self.episode_lengths = []
        self.current_episode_reward = 0
        self.current_episode_length = 0
    
    def on_step(self, reward: float, done: bool, info: Dict) -> bool:
        """
        Llamado después de cada step.
        
        Args:
            reward: Recompensa del step
            done: Si el episodio terminó
            info: Información adicional
            
        Returns:
            bool: True para continuar entrenamiento
        """
        self.current_episode_reward += reward
        self.current_episode_length += 1
        
        if done:
            success = info.get("tool_crafted", False)
            
            # Log episode al curriculum
            advanced = self.curriculum.log_episode(
                success=success,
                total_reward=self.current_episode_reward,
                episode_info=info
            )
            
            # Reset counters
            self.episode_rewards.append(self.current_episode_reward)
            self.episode_lengths.append(self.current_episode_length)
            self.current_episode_reward = 0
            self.current_episode_length = 0
            
            # Si avanzó de etapa, retornar False para reiniciar entorno
            if advanced:
                print("\n[CALLBACK] Stage advanced - environment will be reconfigured")
                return False
        
        return True
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas del entrenamiento"""
        return {
            "mean_episode_reward": np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0,
            "mean_episode_length": np.mean(self.episode_lengths[-100:]) if self.episode_lengths else 0,
            "total_episodes": len(self.episode_rewards)
        }
