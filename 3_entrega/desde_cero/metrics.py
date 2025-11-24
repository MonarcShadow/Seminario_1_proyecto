"""
Metrics Collection Module - Stage 3 (Iron Ore)
Recolecta y visualiza métricas de entrenamiento para el agente de hierro.
"""

import csv
import time
import os
import matplotlib.pyplot as plt

class MetricsLogger:
    def __init__(self, agent_name, save_dir="metrics_data"):
        self.agent_name = agent_name
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        self.filename = os.path.join(save_dir, f"{agent_name}_{int(time.time())}.csv")
        self.headers = ["Episode", "Steps", "IronCollected", "TotalReward", "AvgReward", "Epsilon", "MoveActions", "TurnActions", "AttackActions"]
        
        with open(self.filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)
            
        self.episode_data = []
    
    def log_episode(self, episode, steps, iron, reward, epsilon, action_counts):
        avg_reward = reward / steps if steps > 0 else 0
        move_count = action_counts.get("move", 0)
        turn_count = action_counts.get("turn", 0)
        attack_count = action_counts.get("attack", 0)
        
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([episode, steps, iron, reward, avg_reward, epsilon, move_count, turn_count, attack_count])
        
        self.episode_data.append({
            "Episode": episode,
            "Steps": steps,
            "IronCollected": iron,
            "TotalReward": reward,
            "AvgReward": avg_reward,
            "Epsilon": epsilon,
            "MoveActions": move_count,
            "TurnActions": turn_count,
            "AttackActions": attack_count
        })
        print(f"Episode {episode}: Steps={steps}, Iron={iron}, Reward={reward:.2f}, AvgRew={avg_reward:.2f}, Eps={epsilon:.2f}")
    
    def plot_metrics(self):
        episodes = [d["Episode"] for d in self.episode_data]
        rewards = [d["TotalReward"] for d in self.episode_data]
        iron = [d["IronCollected"] for d in self.episode_data]
        avg_rewards = [d["AvgReward"] for d in self.episode_data]
        
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.plot(episodes, rewards, label='Total Reward')
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.title('Reward per Episode')
        plt.legend()
        
        plt.subplot(1, 3, 2)
        plt.plot(episodes, iron, label='Iron Collected', color='orange')
        plt.xlabel('Episode')
        plt.ylabel('Iron')
        plt.title('Iron Collected')
        plt.legend()
        
        plt.subplot(1, 3, 3)
        plt.plot(episodes, avg_rewards, label='Avg Reward/Step', color='green')
        plt.xlabel('Episode')
        plt.ylabel('Avg Reward')
        plt.title('Efficiency (Reward per Step)')
        plt.legend()
        
        plot_path = self.filename.replace('.csv', '.png')
        plt.savefig(plot_path)
        print(f"Plots saved to {plot_path}")
