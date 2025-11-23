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
    
    plt.figure(figsize=(12, 8))
    
    for file in csv_files:
        agent_name = os.path.basename(file).split('_WoodAgent')[0]
        episodes = []
        rewards = []
        wood = []
        avg_rewards = []
        
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                episodes.append(int(row['Episode']))
                rewards.append(float(row['TotalReward']))
                wood.append(int(row['WoodCollected']))
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
        max_wood = max(wood)
        total_wood = sum(wood)
        success_rate = sum(1 for w in wood if w > 0) / len(wood) * 100 # Assuming >0 wood is "success"
        
        summary_data.append({
            "Agent": agent_name,
            "AvgTotalReward": avg_total_reward,
            "TotalWood": total_wood,
            "MaxWood": max_wood,
            "SuccessRate": success_rate
        })
        
        # Plotting
        plt.plot(episodes, rewards, label=agent_name)

    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Agent Performance Comparison')
    plt.legend()
    plt.grid(True)
    plt.savefig('comparison_plots.png')
    print("Comparison plot saved to comparison_plots.png")
    
    # Save summary table
    with open('summary_table.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Agent", "AvgTotalReward", "TotalWood", "MaxWood", "SuccessRate"])
        writer.writeheader()
        writer.writerows(summary_data)
        
    print("\nSummary Table:")
    print(f"{'Agent':<20} | {'Avg Reward':<12} | {'Total Wood':<12} | {'Max Wood':<10} | {'Success %':<10}")
    print("-" * 80)
    for row in summary_data:
        print(f"{row['Agent']:<20} | {row['AvgTotalReward']:<12.2f} | {row['TotalWood']:<12} | {row['MaxWood']:<10} | {row['SuccessRate']:<10.1f}")
    print("\nSummary table saved to summary_table.csv")

if __name__ == "__main__":
    analyze_results()
