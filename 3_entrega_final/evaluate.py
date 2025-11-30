"""
Script de evaluación para modelos entrenados.

Evalúa un modelo en todos los stages del curriculum y genera métricas detalladas.
"""

import os
import sys
import argparse
import json
import numpy as np
from datetime import datetime
from typing import Dict, List

from stable_baselines3 import PPO, DQN, A2C
from sb3_contrib import TRPO
from stable_baselines3.common.monitor import Monitor

from src.malmo_env_wrapper import MalmoToolProgressionEnv
from src.curriculum_manager import CurriculumManager


def evaluate_model(
    model,
    env,
    num_episodes: int = 10,
    render: bool = False,
    verbose: bool = True
) -> Dict:
    """
    Evalúa un modelo en el entorno dado.
    
    Args:
        model: Modelo de SB3 cargado
        env: Entorno de evaluación
        num_episodes: Número de episodios a evaluar
        render: Si renderizar (no aplicable en Malmo)
        verbose: Si imprimir progreso
    
    Returns:
        Dict con métricas de evaluación
    """
    episode_rewards = []
    episode_lengths = []
    success_count = 0
    
    for episode in range(num_episodes):
        obs = env.reset()
        done = False
        episode_reward = 0
        episode_length = 0
        
        if verbose:
            print(f"\n[EVAL] Episode {episode + 1}/{num_episodes}")
        
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            episode_reward += reward
            episode_length += 1
            
            if verbose and episode_length % 200 == 0:
                print(f"  Step {episode_length}: Reward = {episode_reward:.1f}")
        
        # Check success
        success = info.get("tool_crafted", False)
        if success:
            success_count += 1
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        
        if verbose:
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"  {status} - Reward: {episode_reward:.1f}, Length: {episode_length}")
    
    # Calculate metrics
    metrics = {
        "num_episodes": num_episodes,
        "mean_reward": np.mean(episode_rewards),
        "std_reward": np.std(episode_rewards),
        "min_reward": np.min(episode_rewards),
        "max_reward": np.max(episode_rewards),
        "mean_length": np.mean(episode_lengths),
        "std_length": np.std(episode_lengths),
        "success_rate": success_count / num_episodes,
        "success_count": success_count,
        "episode_rewards": episode_rewards,
        "episode_lengths": episode_lengths
    }
    
    return metrics


def parse_args():
    parser = argparse.ArgumentParser(description='Evaluate trained RL models')
    
    parser.add_argument('--model', type=str, required=True,
                       help='Path to trained model (.zip file)')
    parser.add_argument('--algorithm', type=str, required=True, 
                       choices=['ppo', 'dqn', 'a2c', 'trpo'],
                       help='Algorithm used to train the model')
    parser.add_argument('--episodes', type=int, default=10,
                       help='Number of evaluation episodes (default: 10)')
    parser.add_argument('--stage', type=int, default=None, choices=[1, 2, 3, 4],
                       help='Curriculum stage to evaluate (default: all stages)')
    parser.add_argument('--port', type=int, default=10000,
                       help='Malmo port (default: 10000)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for evaluation (default: 42)')
    parser.add_argument('--output', type=str, default='results/evaluation_results.json',
                       help='Output file for results (default: results/evaluation_results.json)')
    parser.add_argument('--verbose', action='store_true',
                       help='Print detailed progress')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Create output directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Check model file exists
    if not os.path.exists(args.model):
        print(f"[ERROR] Model file not found: {args.model}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"MODEL EVALUATION")
    print(f"{'='*70}")
    print(f"Model: {args.model}")
    print(f"Algorithm: {args.algorithm.upper()}")
    print(f"Episodes per stage: {args.episodes}")
    print(f"Seed: {args.seed}")
    print(f"{'='*70}\n")
    
    # Determine stages to evaluate
    stages_to_eval = [args.stage] if args.stage else [1, 2, 3, 4]
    
    all_results = {}
    
    for stage_id in stages_to_eval:
        print(f"\n{'='*70}")
        print(f"EVALUATING STAGE {stage_id}")
        print(f"{'='*70}")
        
        # Create curriculum manager for specific stage
        curriculum = CurriculumManager(start_stage=stage_id)
        
        # Create environment
        env = MalmoToolProgressionEnv(
            curriculum_manager=curriculum,
            port=args.port,
            max_episode_steps=2000,  # Longer for evaluation
            seed=args.seed
        )
        env = Monitor(env)
        
        # Load model
        try:
            if args.algorithm == 'ppo':
                model = PPO.load(args.model, env=env)
            elif args.algorithm == 'dqn':
                model = DQN.load(args.model, env=env)
            elif args.algorithm == 'a2c':
                model = A2C.load(args.model, env=env)
            elif args.algorithm == 'trpo':
                model = TRPO.load(args.model, env=env)
            else:
                raise ValueError(f"Unknown algorithm: {args.algorithm}")
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            env.close()
            continue
        
        # Evaluate
        print(f"\nRunning {args.episodes} evaluation episodes...")
        metrics = evaluate_model(
            model=model,
            env=env,
            num_episodes=args.episodes,
            verbose=args.verbose
        )
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"STAGE {stage_id} RESULTS")
        print(f"{'='*70}")
        print(f"Success Rate: {metrics['success_rate']:.1%} ({metrics['success_count']}/{metrics['num_episodes']})")
        print(f"Mean Reward: {metrics['mean_reward']:.1f} ± {metrics['std_reward']:.1f}")
        print(f"Mean Length: {metrics['mean_length']:.1f} ± {metrics['std_length']:.1f}")
        print(f"Reward Range: [{metrics['min_reward']:.1f}, {metrics['max_reward']:.1f}]")
        print(f"{'='*70}\n")
        
        # Store results
        all_results[f"stage_{stage_id}"] = metrics
        
        # Close environment
        env.close()
    
    # Save results to file
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "model_path": args.model,
        "algorithm": args.algorithm,
        "num_episodes": args.episodes,
        "seed": args.seed,
        "results": all_results
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n[EVAL] Results saved to: {args.output}")
    
    # Print final summary
    print(f"\n{'='*70}")
    print(f"OVERALL EVALUATION SUMMARY")
    print(f"{'='*70}")
    for stage_name, metrics in all_results.items():
        stage_num = stage_name.split('_')[1]
        print(f"Stage {stage_num}: {metrics['success_rate']:.1%} success, {metrics['mean_reward']:.1f} avg reward")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
