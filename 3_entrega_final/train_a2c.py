"""
Script de entrenamiento con A2C para progresión de herramientas.

Sistema de Curriculum Learning con 4 etapas usando Advantage Actor-Critic.

Referencia: Mnih et al. (2016) - "Asynchronous Methods for Deep Reinforcement Learning"
"""

import os
import sys
import argparse
from datetime import datetime
import torch
import numpy as np

from stable_baselines3 import A2C
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
                    f"a2c_stage_{self.curriculum.current_stage.stage_id - 1}_checkpoint.zip"
                )
                self.model.save(model_path)
                print(f"  Saved to: {model_path}")
        
        return True


def parse_args():
    parser = argparse.ArgumentParser(description='Train A2C agent with curriculum learning')
    
    # Training parameters
    parser.add_argument('--episodes', type=int, default=2000,
                       help='Total number of episodes (default: 2000)')
    parser.add_argument('--curriculum', action='store_true',
                       help='Use curriculum learning (highly recommended)')
    parser.add_argument('--start-stage', type=int, default=1, choices=[1, 2, 3, 4],
                       help='Starting curriculum stage (1-4, default: 1)')
    
    # A2C hyperparameters
    parser.add_argument('--learning-rate', type=float, default=7e-4,
                       help='Learning rate (default: 7e-4)')
    parser.add_argument('--n-steps', type=int, default=5,
                       help='Number of steps per update (default: 5)')
    parser.add_argument('--gamma', type=float, default=0.99,
                       help='Discount factor (default: 0.99)')
    parser.add_argument('--gae-lambda', type=float, default=1.0,
                       help='GAE lambda for advantage estimation (default: 1.0)')
    parser.add_argument('--ent-coef', type=float, default=0.01,
                       help='Entropy coefficient (default: 0.01)')
    parser.add_argument('--vf-coef', type=float, default=0.5,
                       help='Value function coefficient (default: 0.5)')
    parser.add_argument('--max-grad-norm', type=float, default=0.5,
                       help='Max gradient norm for clipping (default: 0.5)')
    parser.add_argument('--rms-prop-eps', type=float, default=1e-5,
                       help='RMSProp epsilon (default: 1e-5)')
    
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
    
    return parser.parse_args()


def train():
    args = parse_args()
    
    # Create directories
    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(args.model_dir, exist_ok=True)
    
    # Set random seed
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    
    # Initialize curriculum manager
    curriculum = None
    if args.curriculum:
        curriculum = CurriculumManager(
            start_stage=args.start_stage,
            log_dir=os.path.join(args.log_dir, "curriculum")
        )
        print("\n[TRAIN] Curriculum Learning enabled")
        print(curriculum.get_summary())
    
    # Create environment
    env = MalmoToolProgressionEnv(
        curriculum_manager=curriculum,
        port=args.port,
        max_episode_steps=args.max_steps,
        seed=args.seed
    )
    env = Monitor(env)
    
    # Setup logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"a2c_curriculum_{timestamp}" if curriculum else f"a2c_{timestamp}"
    log_path = os.path.join(args.log_dir, run_name)
    
    logger = configure(log_path, ["stdout", "tensorboard"])
    
    print(f"\n[TRAIN] Training A2C with configuration:")
    print(f"  Algorithm: A2C (Advantage Actor-Critic)")
    print(f"  Learning rate: {args.learning_rate}")
    print(f"  N-steps: {args.n_steps}")
    print(f"  Gamma: {args.gamma}")
    print(f"  GAE lambda: {args.gae_lambda}")
    print(f"  Entropy coef: {args.ent_coef}")
    print(f"  Value function coef: {args.vf_coef}")
    print(f"  Log directory: {log_path}")
    
    # Create or load model
    model = None
    
    if curriculum and curriculum.current_stage.stage_id > 1:
        # Try to load pretrained model from previous stage
        prev_stage = curriculum.current_stage.stage_id - 1
        pretrained_path = os.path.join(args.model_dir, f"a2c_stage_{prev_stage}_checkpoint.zip")
        
        if os.path.exists(pretrained_path):
            try:
                print(f"\n[TRAIN] Loading pretrained model from stage {prev_stage}...")
                model = A2C.load(pretrained_path, env=env)
                model.set_logger(logger)
                print(f"  ✓ Successfully loaded pretrained model")
                print(f"  Path: {pretrained_path}")
            except Exception as e:
                print(f"  ✗ Error loading pretrained model: {e}")
                print("  Starting from scratch instead")
                model = A2C(
                    "MlpPolicy",
                    env,
                    learning_rate=args.learning_rate,
                    n_steps=args.n_steps,
                    gamma=args.gamma,
                    gae_lambda=args.gae_lambda,
                    ent_coef=args.ent_coef,
                    vf_coef=args.vf_coef,
                    max_grad_norm=args.max_grad_norm,
                    rms_prop_eps=args.rms_prop_eps,
                    verbose=1,
                    tensorboard_log=log_path
                )
                model.set_logger(logger)
        else:
            # No pretrained model, start from scratch
            model = A2C(
                "MlpPolicy",
                env,
                learning_rate=args.learning_rate,
                n_steps=args.n_steps,
                gamma=args.gamma,
                gae_lambda=args.gae_lambda,
                ent_coef=args.ent_coef,
                vf_coef=args.vf_coef,
                max_grad_norm=args.max_grad_norm,
                rms_prop_eps=args.rms_prop_eps,
                verbose=1,
                tensorboard_log=log_path
            )
            model.set_logger(logger)
    else:
        # Stage 1 or no curriculum, start from scratch
        model = A2C(
            "MlpPolicy",
            env,
            learning_rate=args.learning_rate,
            n_steps=args.n_steps,
            gamma=args.gamma,
            gae_lambda=args.gae_lambda,
            ent_coef=args.ent_coef,
            vf_coef=args.vf_coef,
            max_grad_norm=args.max_grad_norm,
            rms_prop_eps=args.rms_prop_eps,
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
