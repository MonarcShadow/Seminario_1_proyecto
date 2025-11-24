import os
import csv
import matplotlib.pyplot as plt
import glob

def analyze_results(metrics_dir="metrics_data"):
    csv_files = glob.glob(os.path.join(metrics_dir, "*.csv"))
    
    if not csv_files:
        print("No metrics files found.")
        return

    summary_data = []
    
    plt.figure(figsize=(15, 5))
    
    for file in csv_files:
        agent_name = os.path.basename(file).split('_StoneAgent')[0]
        if '_StoneAgent' not in os.path.basename(file):
            # Try other patterns
            agent_name = os.path.basename(file).replace('.csv', '').split('_')[0]
            
        episodes = []
        rewards = []
        stone = []
        avg_rewards = []
        
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                episodes.append(int(row['Episode']))
                rewards.append(float(row['TotalReward']))
                stone.append(int(row['StoneCollected']))
                # Handle backward compatibility if AvgReward missing
                if 'AvgReward' in row:
                    avg_rewards.append(float(row['AvgReward']))
                else:
                    steps = int(row['Steps'])
                    avg_rewards.append(float(row['TotalReward'])/steps if steps > 0 else 0)

        if not episodes:
            continue
            
        # Calculate summary stats
        avg_total_reward = sum(rewards) / len(rewards)
        total_stone = sum(stone)
        max_stone = max(stone)
        
        summary_data.append({
            "Agent": agent_name,
            "AvgTotalReward": avg_total_reward,
            "TotalStone": total_stone,
            "MaxStone": max_stone
        })
        
        # Plotting rewards comparison
        plt.subplot(1, 3, 1)
        plt.plot(episodes, rewards, label=agent_name)
        
        # Plotting stone collection
        plt.subplot(1, 3, 2)
        plt.plot(episodes, stone, label=agent_name)
        
        # Plotting average reward efficiency
        plt.subplot(1, 3, 3)
        plt.plot(episodes, avg_rewards, label=agent_name)

    # Configure subplots
    plt.subplot(1, 3, 1)
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Total Reward per Episode')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 3, 2)
    plt.xlabel('Episode')
    plt.ylabel('Stone Collected')
    plt.title('Stone Collection Progress')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 3, 3)
    plt.xlabel('Episode')
    plt.ylabel('Avg Reward per Step')
    plt.title('Efficiency (Reward per Step)')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('comparison_plots_stone.png')
    print("Comparison plot saved to comparison_plots_stone.png")
    
    # Save summary table
    with open('summary_table_stone.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Agent", "AvgTotalReward", "TotalStone", "MaxStone"])
        writer.writeheader()
        writer.writerows(summary_data)
        
    print("\nSummary Table - Stone Agent Performance:")
    print(f"{'Agent':<20} | {'Avg Reward':<12} | {'Total Stone':<12} | {'Max Stone':<10}")
    print("-" * 70)
    for row in summary_data:
        print(f"{row['Agent']:<20} | {row['AvgTotalReward']:<12.2f} | {row['TotalStone']:<12} | {row['MaxStone']:<10}")
    print("\nSummary table saved to summary_table_stone.csv")

if __name__ == "__main__":
    analyze_results()
