"""
Metrics Collection Module - Stage 3 (Iron Ore)
Recolecta y visualiza métricas de entrenamiento para el agente de hierro.
"""

import csv
import os
import matplotlib.pyplot as plt
from collections import defaultdict

class MetricsCollector:
    def __init__(self, algorithm_name):
        self.algorithm_name = algorithm_name
        self.csv_filename = f"resultados/{algorithm_name}_iron_metrics.csv"
        
        # Create results directory if it doesn't exist
        os.makedirs("resultados", exist_ok=True)
        
        # Initialize CSV file with headers
        with open(self.csv_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Episode', 'Steps', 'IronCollected', 'TotalReward', 'AvgReward', 
                'Epsilon', 'MoveActions', 'TurnActions', 'AttackActions'
            ])
        
        # In-memory storage for plotting
        self.episodes = []
        self.steps_list = []
        self.iron_list = []
        self.rewards = []
        self.epsilons = []
        self.move_actions = []
        self.turn_actions = []
        self.attack_actions = []
    
    def log_episode(self, episode, steps, iron_collected, total_reward, epsilon, action_counts):
        """
        Log episode metrics to CSV and memory.
        
        Parameters:
        - episode: número de episodio
        - steps: pasos totales del episodio
        - iron_collected: cantidad de hierro recolectado
        - total_reward: recompensa total del episodio
        - epsilon: valor de exploración actual
        - action_counts: dict con conteo de acciones {'move': x, 'turn': y, 'attack': z}
        """
        avg_reward = total_reward / steps if steps > 0 else 0
        
        # Write to CSV
        with open(self.csv_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                episode, steps, iron_collected, total_reward, avg_reward,
                epsilon, action_counts['move'], action_counts['turn'], action_counts['attack']
            ])
        
        # Store in memory for plotting
        self.episodes.append(episode)
        self.steps_list.append(steps)
        self.iron_list.append(iron_collected)
        self.rewards.append(total_reward)
        self.epsilons.append(epsilon)
        self.move_actions.append(action_counts['move'])
        self.turn_actions.append(action_counts['turn'])
        self.attack_actions.append(action_counts['attack'])
    
    def plot_metrics(self):
        """
        Genera gráficos de las métricas recolectadas.
        3 plots: Iron Collected, Total Reward, Epsilon Decay
        """
        if len(self.episodes) == 0:
            print("No hay datos para graficar")
            return
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle(f'{self.algorithm_name.upper()} - Iron Stage Metrics', fontsize=16)
        
        # Plot 1: Iron Collected
        axes[0].plot(self.episodes, self.iron_list, 'b-', linewidth=2)
        axes[0].set_xlabel('Episode')
        axes[0].set_ylabel('Iron Collected')
        axes[0].set_title('Iron Collection Progress')
        axes[0].grid(True, alpha=0.3)
        axes[0].axhline(y=3, color='r', linestyle='--', label='Goal (3 iron)')
        axes[0].legend()
        
        # Plot 2: Total Reward
        axes[1].plot(self.episodes, self.rewards, 'g-', linewidth=2)
        axes[1].set_xlabel('Episode')
        axes[1].set_ylabel('Total Reward')
        axes[1].set_title('Reward per Episode')
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Epsilon Decay
        axes[2].plot(self.episodes, self.epsilons, 'r-', linewidth=2)
        axes[2].set_xlabel('Episode')
        axes[2].set_ylabel('Epsilon')
        axes[2].set_title('Exploration Rate (Epsilon)')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = f"resultados/{self.algorithm_name}_iron_metrics.png"
        plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
        print(f"\n✓ Gráficos guardados en: {plot_filename}")
        
        # Optionally show plot (commented out for batch processing)
        # plt.show()
        plt.close()
