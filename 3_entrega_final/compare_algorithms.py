"""
Script de comparación entre algoritmos de RL.

Compara el rendimiento de múltiples modelos entrenados (PPO, DQN, A2C, etc.)
y genera gráficos comparativos.
"""

import os
import sys
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, List, Tuple

from stable_baselines3 import PPO, DQN, A2C
from sb3_contrib import TRPO
from stable_baselines3.common.monitor import Monitor

from src.malmo_env_wrapper import MalmoToolProgressionEnv
from src.curriculum_manager import CurriculumManager


def load_model(model_path: str, algorithm: str, env):
    """Carga un modelo según el algoritmo especificado"""
    if algorithm == 'ppo':
        return PPO.load(model_path, env=env)
    elif algorithm == 'dqn':
        return DQN.load(model_path, env=env)
    elif algorithm == 'a2c':
        return A2C.load(model_path, env=env)
    elif algorithm == 'trpo':
        return TRPO.load(model_path, env=env)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


def evaluate_model(model, env, num_episodes: int = 10) -> Dict:
    """Evalúa un modelo y retorna métricas"""
    episode_rewards = []
    episode_lengths = []
    success_count = 0
    
    for episode in range(num_episodes):
        obs = env.reset()
        done = False
        episode_reward = 0
        episode_length = 0
        
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            episode_reward += reward
            episode_length += 1
        
        success = info.get("tool_crafted", False)
        if success:
            success_count += 1
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
    
    return {
        "mean_reward": np.mean(episode_rewards),
        "std_reward": np.std(episode_rewards),
        "mean_length": np.mean(episode_lengths),
        "std_length": np.std(episode_lengths),
        "success_rate": success_count / num_episodes,
        "episode_rewards": episode_rewards,
        "episode_lengths": episode_lengths
    }


def plot_comparison(results: Dict, output_dir: str):
    """Genera gráficos comparativos entre algoritmos"""
    
    algorithms = list(results.keys())
    stages = sorted([int(s.split('_')[1]) for s in results[algorithms[0]].keys()])
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Algorithm Comparison Across Curriculum Stages', fontsize=16, fontweight='bold')
    
    # 1. Success Rate Comparison
    ax = axes[0, 0]
    x = np.arange(len(stages))
    width = 0.2
    
    for i, algo in enumerate(algorithms):
        success_rates = [results[algo][f'stage_{s}']['success_rate'] for s in stages]
        ax.bar(x + i * width, success_rates, width, label=algo.upper())
    
    ax.set_xlabel('Curriculum Stage')
    ax.set_ylabel('Success Rate')
    ax.set_title('Success Rate by Stage')
    ax.set_xticks(x + width * (len(algorithms) - 1) / 2)
    ax.set_xticklabels([f'Stage {s}' for s in stages])
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1])
    
    # 2. Mean Reward Comparison
    ax = axes[0, 1]
    
    for algo in algorithms:
        mean_rewards = [results[algo][f'stage_{s}']['mean_reward'] for s in stages]
        std_rewards = [results[algo][f'stage_{s}']['std_reward'] for s in stages]
        ax.errorbar(stages, mean_rewards, yerr=std_rewards, marker='o', 
                   label=algo.upper(), capsize=5, capthick=2)
    
    ax.set_xlabel('Curriculum Stage')
    ax.set_ylabel('Mean Reward')
    ax.set_title('Average Reward by Stage')
    ax.set_xticks(stages)
    ax.set_xticklabels([f'Stage {s}' for s in stages])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Episode Length Comparison
    ax = axes[1, 0]
    
    for algo in algorithms:
        mean_lengths = [results[algo][f'stage_{s}']['mean_length'] for s in stages]
        std_lengths = [results[algo][f'stage_{s}']['std_length'] for s in stages]
        ax.errorbar(stages, mean_lengths, yerr=std_lengths, marker='s',
                   label=algo.upper(), capsize=5, capthick=2)
    
    ax.set_xlabel('Curriculum Stage')
    ax.set_ylabel('Mean Episode Length (steps)')
    ax.set_title('Episode Length by Stage')
    ax.set_xticks(stages)
    ax.set_xticklabels([f'Stage {s}' for s in stages])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. Overall Performance Heatmap
    ax = axes[1, 1]
    
    # Create performance matrix (success_rate as metric)
    perf_matrix = np.zeros((len(algorithms), len(stages)))
    for i, algo in enumerate(algorithms):
        for j, stage in enumerate(stages):
            perf_matrix[i, j] = results[algo][f'stage_{stage}']['success_rate']
    
    im = ax.imshow(perf_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    
    # Add text annotations
    for i in range(len(algorithms)):
        for j in range(len(stages)):
            text = ax.text(j, i, f'{perf_matrix[i, j]:.1%}',
                         ha="center", va="center", color="black", fontweight='bold')
    
    ax.set_xticks(np.arange(len(stages)))
    ax.set_yticks(np.arange(len(algorithms)))
    ax.set_xticklabels([f'Stage {s}' for s in stages])
    ax.set_yticklabels([a.upper() for a in algorithms])
    ax.set_title('Success Rate Heatmap')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Success Rate', rotation=270, labelpad=20)
    
    plt.tight_layout()
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f'algorithm_comparison_{timestamp}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n[PLOT] Comparison plot saved to: {output_path}")
    
    plt.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Compare multiple RL algorithm models')
    
    parser.add_argument('--models', type=str, nargs='+', required=True,
                       help='Paths to trained models (.zip files)')
    parser.add_argument('--algorithms', type=str, nargs='+', required=True,
                       choices=['ppo', 'dqn', 'a2c', 'trpo'],
                       help='Algorithms corresponding to each model')
    parser.add_argument('--episodes', type=int, default=10,
                       help='Number of evaluation episodes per stage (default: 10)')
    parser.add_argument('--stages', type=int, nargs='+', default=[1, 2, 3, 4],
                       choices=[1, 2, 3, 4],
                       help='Stages to evaluate (default: all)')
    parser.add_argument('--port', type=int, default=10000,
                       help='Malmo port (default: 10000)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory for results (default: results)')
    parser.add_argument('--no-plot', action='store_true',
                       help='Skip generating plots')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Validate inputs
    if len(args.models) != len(args.algorithms):
        print("[ERROR] Number of models and algorithms must match")
        sys.exit(1)
    
    for model_path in args.models:
        if not os.path.exists(model_path):
            print(f"[ERROR] Model not found: {model_path}")
            sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"ALGORITHM COMPARISON")
    print(f"{'='*70}")
    print(f"Models: {len(args.models)}")
    for model, algo in zip(args.models, args.algorithms):
        print(f"  - {algo.upper()}: {model}")
    print(f"Episodes per stage: {args.episodes}")
    print(f"Stages: {args.stages}")
    print(f"{'='*70}\n")
    
    # Store all results
    all_results = {}
    
    # Evaluate each model
    for model_path, algorithm in zip(args.models, args.algorithms):
        print(f"\n{'='*70}")
        print(f"EVALUATING {algorithm.upper()} MODEL")
        print(f"{'='*70}")
        
        algo_results = {}
        
        for stage_id in args.stages:
            print(f"\nStage {stage_id}...")
            
            # Create environment
            curriculum = CurriculumManager(start_stage=stage_id)
            env = MalmoToolProgressionEnv(
                curriculum_manager=curriculum,
                port=args.port,
                max_episode_steps=2000,
                seed=args.seed
            )
            env = Monitor(env)
            
            try:
                # Load model
                model = load_model(model_path, algorithm, env)
                
                # Evaluate
                metrics = evaluate_model(model, env, args.episodes)
                
                # Store results
                algo_results[f'stage_{stage_id}'] = metrics
                
                print(f"  Success Rate: {metrics['success_rate']:.1%}")
                print(f"  Mean Reward: {metrics['mean_reward']:.1f} ± {metrics['std_reward']:.1f}")
                
            except Exception as e:
                print(f"  [ERROR] Failed to evaluate: {e}")
                algo_results[f'stage_{stage_id}'] = {
                    "mean_reward": 0,
                    "std_reward": 0,
                    "mean_length": 0,
                    "std_length": 0,
                    "success_rate": 0,
                    "episode_rewards": [],
                    "episode_lengths": []
                }
            finally:
                env.close()
        
        all_results[algorithm] = algo_results
    
    # Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(args.output_dir, f'comparison_results_{timestamp}.json')
    
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "models": dict(zip(args.algorithms, args.models)),
        "num_episodes": args.episodes,
        "stages": args.stages,
        "seed": args.seed,
        "results": all_results
    }
    
    with open(json_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n[SAVE] Results saved to: {json_path}")
    
    # Generate comparison plots
    if not args.no_plot:
        try:
            plot_comparison(all_results, args.output_dir)
        except Exception as e:
            print(f"\n[WARNING] Failed to generate plots: {e}")
    
    # Print final summary table
    print(f"\n{'='*70}")
    print(f"COMPARISON SUMMARY")
    print(f"{'='*70}")
    print(f"{'Algorithm':<12} {'Stage 1':<12} {'Stage 2':<12} {'Stage 3':<12} {'Stage 4':<12}")
    print(f"{'-'*70}")
    
    for algo in all_results.keys():
        row = f"{algo.upper():<12}"
        for stage in args.stages:
            sr = all_results[algo][f'stage_{stage}']['success_rate']
            row += f"{sr:>11.1%} "
        print(row)
    
    print(f"{'='*70}\n")
    
    # Determine winner
    overall_scores = {}
    for algo in all_results.keys():
        scores = [all_results[algo][f'stage_{s}']['success_rate'] for s in args.stages]
        overall_scores[algo] = np.mean(scores)
    
    winner = max(overall_scores, key=overall_scores.get)
    print(f"🏆 Best Overall Performance: {winner.upper()} ({overall_scores[winner]:.1%} avg success rate)\n")


if __name__ == "__main__":
    main()
