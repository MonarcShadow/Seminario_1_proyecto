"""
Script de entrenamiento con PPO para progresión de herramientas.

Sistema de Curriculum Learning con 4 etapas:
1. Madera (wooden_pickaxe) - 3 wood → craft
2. Piedra (stone_pickaxe) - 3 stone + wooden_pickaxe → craft
3. Hierro (iron_pickaxe) - 3 iron + stone_pickaxe → craft
4. Diamante (diamond_pickaxe) - 1 diamond + iron_pickaxe → craft

Cada etapa usa el modelo pre-entrenado de la etapa anterior.

Referencia: Schulman et al. (2017) - "Proximal Policy Optimization Algorithms"
"""

import os
import sys
import argparse
from datetime import datetime
import torch
import numpy as np

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.logger import configure

from src.malmo_env_wrapper import MalmoToolProgressionEnv
from src.curriculum_manager import CurriculumManager


class CurriculumCallback(BaseCallback):
    """
    Callback para integrar el curriculum manager con SB3.
    """
    
    def __init__(self, curriculum_manager, save_path, verbose=0):
        super().__init__(verbose)
        self.curriculum = curriculum_manager
        self.save_path = save_path
        self.episode_rewards = []
        self.episode_lengths = []
        self.current_episode_reward = 0
        self.current_episode_length = 0
    
    def _on_step(self) -> bool:
        """
        Called at each step.
        """
        # Accumulate reward
        self.current_episode_reward += self.locals['rewards'][0]
        self.current_episode_length += 1
        
        # Check if episode ended
        if self.locals['dones'][0]:
            info = self.locals['infos'][0]
            success = info.get("tool_crafted", False)
            
            # Log to curriculum
            advanced = self.curriculum.log_episode(
                success=success,
                total_reward=self.current_episode_reward,
                episode_info=info
            )
            
            # Save episode stats
            self.episode_rewards.append(self.current_episode_reward)
            self.episode_lengths.append(self.current_episode_length)
            
            # Log to tensorboard
            self.logger.record("curriculum/stage", self.curriculum.current_stage.stage_id)
            self.logger.record("curriculum/stage_episodes", self.curriculum.current_stage.episodes_completed)
            self.logger.record("curriculum/episode_reward", self.current_episode_reward)
            self.logger.record("curriculum/episode_length", self.current_episode_length)
            self.logger.record("curriculum/success", 1.0 if success else 0.0)
            
            # Reset counters
            self.current_episode_reward = 0
            self.current_episode_length = 0
            
            # Si avanzó de etapa, guardar modelo
            if advanced:
                print(f"\n[CALLBACK] Stage advanced! Saving model...")
                model_path = os.path.join(
                    self.save_path,
                    f"stage_{self.curriculum.current_stage.stage_id - 1}_checkpoint.zip"
                )
                self.model.save(model_path)
                print(f"  Saved to: {model_path}")
        
        return True


def parse_args():
    parser = argparse.ArgumentParser(description='Train PPO agent with curriculum learning')
    
    # Training parameters
    parser.add_argument('--episodes', type=int, default=2000,
                       help='Total number of episodes (default: 2000)')
    parser.add_argument('--curriculum', action='store_true',
                       help='Use curriculum learning (highly recommended)')
    parser.add_argument('--start-stage', type=int, default=1, choices=[1, 2, 3, 4],
                       help='Starting curriculum stage (1-4, default: 1)')
    
    # PPO hyperparameters
    parser.add_argument('--learning-rate', type=float, default=3e-4,
                       help='Learning rate (default: 3e-4)')
    parser.add_argument('--n-steps', type=int, default=2048,
                       help='Number of steps per update (default: 2048)')
    parser.add_argument('--batch-size', type=int, default=64,
                       help='Minibatch size (default: 64)')
    parser.add_argument('--n-epochs', type=int, default=10,
                       help='Number of epochs per update (default: 10)')
    parser.add_argument('--gamma', type=float, default=0.99,
                       help='Discount factor (default: 0.99)')
    parser.add_argument('--clip-range', type=float, default=0.2,
                       help='PPO clip range (default: 0.2)')
    
    # Environment parameters
    parser.add_argument('--port', type=int, default=10000,
                       help='Malmo port (default: 10000)')
    parser.add_argument('--seed', type=int, default=123456,
                       help='Random seed (default: 123456)')
    parser.add_argument('--max-steps', type=int, default=1000,
                       help='Max steps per episode (default: 1000)')
    
    # Logging
    parser.add_argument('--log-dir', type=str, default='logs',
                       help='Directory for logs (default: logs)')
    parser.add_argument('--model-dir', type=str, default='models',
                       help='Directory for saved models (default: models)')
    
    # Resume training
    parser.add_argument('--resume', type=str, default=None,
                       help='Path to model to resume training from')
    
    return parser.parse_args()


def train():
    args = parse_args()
    
    # Create directories
    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(args.model_dir, exist_ok=True)
    
    # Timestamp for unique run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"ppo_curriculum_{timestamp}" if args.curriculum else f"ppo_single_{timestamp}"
    
    print("\n" + "="*70)
    print("PPO TRAINING - TOOL PROGRESSION")
    print("="*70)
    print(f"Run: {run_name}")
    print(f"Curriculum Learning: {args.curriculum}")
    print(f"Start Stage: {args.start_stage}")
    print(f"Episodes: {args.episodes}")
    print(f"Learning Rate: {args.learning_rate}")
    print(f"Port: {args.port}")
    print("="*70 + "\n")
    
    # Initialize curriculum manager
    curriculum = None
    if args.curriculum:
        curriculum = CurriculumManager(
            start_stage=args.start_stage,
            log_dir=os.path.join(args.log_dir, run_name, "curriculum")
        )
    
    # Create environment
    env = MalmoToolProgressionEnv(
        curriculum_manager=curriculum,
        port=args.port,
        max_episode_steps=args.max_steps,
        seed=args.seed
    )
    
    # Wrap with Monitor
    log_path = os.path.join(args.log_dir, run_name)
    env = Monitor(env, log_path)
    
    # Configure logger
    logger = configure(log_path, ["stdout", "tensorboard"])
    
    # Create or load model
    if args.resume:
        print(f"\n[TRAIN] Resuming from {args.resume}")
        model = PPO.load(args.resume, env=env)
        model.set_logger(logger)
    else:
        # Check if there's a pretrained model from previous stage
        if curriculum and curriculum.current_stage_idx > 0:
            pretrained_path = curriculum.get_pretrained_model_path()
            if pretrained_path:
                print(f"\n[TRAIN] Loading pretrained model: {pretrained_path}")
                try:
                    model = PPO.load(pretrained_path, env=env)
                    model.set_logger(logger)
                    print("  ✓ Pretrained model loaded successfully")
                except Exception as e:
                    print(f"  ✗ Error loading pretrained model: {e}")
                    print("  Starting from scratch instead")
                    model = PPO(
                        "MlpPolicy",
                        env,
                        learning_rate=args.learning_rate,
                        n_steps=args.n_steps,
                        batch_size=args.batch_size,
                        n_epochs=args.n_epochs,
                        gamma=args.gamma,
                        clip_range=args.clip_range,
                        verbose=1,
                        tensorboard_log=log_path
                    )
                    model.set_logger(logger)
            else:
                # No pretrained model, start from scratch
                model = PPO(
                    "MlpPolicy",
                    env,
                    learning_rate=args.learning_rate,
                    n_steps=args.n_steps,
                    batch_size=args.batch_size,
                    n_epochs=args.n_epochs,
                    gamma=args.gamma,
                    clip_range=args.clip_range,
                    verbose=1,
                    tensorboard_log=log_path
                )
                model.set_logger(logger)
        else:
            # Stage 1 or no curriculum, start from scratch
            model = PPO(
                "MlpPolicy",
                env,
                learning_rate=args.learning_rate,
                n_steps=args.n_steps,
                batch_size=args.batch_size,
                n_epochs=args.n_epochs,
                gamma=args.gamma,
                clip_range=args.clip_range,
                verbose=1,
                tensorboard_log=log_path
            )
            model.set_logger(logger)
    
    # Create callbacks
    callbacks = []
    
    if curriculum:
        curriculum_callback = CurriculumCallback(
            curriculum_manager=curriculum,
            save_path=args.model_dir,
            verbose=1
        )
        callbacks.append(curriculum_callback)
    
    # Calculate total timesteps
    # Aproximadamente: episodes * max_steps
    total_timesteps = args.episodes * args.max_steps
    
    print(f"\n[TRAIN] Starting training...")
    print(f"  Total timesteps: {total_timesteps:,}")
    print(f"  Estimated episodes: {args.episodes}")
    print(f"  Max steps/episode: {args.max_steps}")
    print()
    
    # Train
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=callbacks
        )
    except KeyboardInterrupt:
        print("\n[TRAIN] Training interrupted by user")
    except Exception as e:
        print(f"\n[TRAIN] Training error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Save final model
        final_model_path = os.path.join(args.model_dir, f"{run_name}_final.zip")
        model.save(final_model_path)
        print(f"\n[TRAIN] Final model saved to: {final_model_path}")
        
        # Print curriculum summary
        if curriculum:
            print(curriculum.get_summary())
        
        # Close environment
        env.close()
    
    print("\n[TRAIN] Training complete!")


if __name__ == "__main__":
    train()
