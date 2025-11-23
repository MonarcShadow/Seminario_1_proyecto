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
    
    plt.figure(figsize=(16, 10))
    
    for file in csv_files:
        agent_name = os.path.basename(file).split('_StoneAgent')[0]
        if '_StoneAgent' not in os.path.basename(file):
            # Try other patterns
            agent_name = os.path.basename(file).replace('.csv', '').split('_')[0]
            
        episodes = []
        rewards = []
        wood = []
        stone = []
        iron = []
        pickaxe = []
        avg_rewards = []
        
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                episodes.append(int(row['Episode']))
                rewards.append(float(row['TotalReward']))
                wood.append(int(row['WoodCollected']))
                stone.append(int(row['StoneCollected']))
                iron.append(int(row.get('IronCollected', 0)))
                pickaxe.append(int(row.get('PickaxeCrafted', 0)))
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
        total_wood = sum(wood)
        max_wood = max(wood)
        total_stone = sum(stone)
        max_stone = max(stone)
        total_iron = sum(iron)
        max_iron = max(iron)
        total_pickaxes = sum(pickaxe)
        success_rate = (sum(pickaxe) / len(pickaxe) * 100) if pickaxe else 0
        
        summary_data.append({
            "Agent": agent_name,
            "AvgTotalReward": avg_total_reward,
            "TotalWood": total_wood,
            "MaxWood": max_wood,
            "TotalStone": total_stone,
            "MaxStone": max_stone,
            "TotalIron": total_iron,
            "MaxIron": max_iron,
            "TotalPickaxes": total_pickaxes,
            "SuccessRate": success_rate
        })
        
        # Plotting rewards comparison
        plt.subplot(2, 3, 1)
        plt.plot(episodes, rewards, label=agent_name)
        
        # Plotting stone collection
        plt.subplot(2, 3, 2)
        plt.plot(episodes, stone, label=agent_name)
        
        # Plotting wood collection
        plt.subplot(2, 3, 3)
        plt.plot(episodes, wood, label=agent_name)
        
        # Plotting iron collection
        plt.subplot(2, 3, 4)
        plt.plot(episodes, iron, label=agent_name)
        
        # Plotting pickaxe crafting success
        plt.subplot(2, 3, 5)
        plt.plot(episodes, pickaxe, label=agent_name, marker='o')
        
        # Plotting average reward efficiency
        plt.subplot(2, 3, 6)
        plt.plot(episodes, avg_rewards, label=agent_name)

    # Configure subplots
    plt.subplot(2, 3, 1)
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Total Reward per Episode')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 3, 2)
    plt.xlabel('Episode')
    plt.ylabel('Stone Collected')
    plt.title('Stone Collection Progress')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 3, 3)
    plt.xlabel('Episode')
    plt.ylabel('Wood Collected')
    plt.title('Wood Collection Progress')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 3, 4)
    plt.xlabel('Episode')
    plt.ylabel('Iron Collected')
    plt.title('Iron Collection Progress')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 3, 5)
    plt.xlabel('Episode')
    plt.ylabel('Pickaxe Crafted (0/1)')
    plt.title('Stone Pickaxe Crafting Success')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 3, 6)
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
        writer = csv.DictWriter(f, fieldnames=["Agent", "AvgTotalReward", "TotalWood", "MaxWood", "TotalStone", "MaxStone", "TotalIron", "MaxIron", "TotalPickaxes", "SuccessRate"])
        writer.writeheader()
        writer.writerows(summary_data)
        
    print("\nSummary Table - Stone Agent Performance:")
    print(f"{'Agent':<20} | {'Avg Reward':<12} | {'Total Wood':<11} | {'Max Wood':<9} | {'Total Stone':<12} | {'Max Stone':<10} | {'Total Iron':<11} | {'Pickaxes':<10} | {'Success %':<10}")
    print("-" * 150)
    for row in summary_data:
        print(f"{row['Agent']:<20} | {row['AvgTotalReward']:<12.2f} | {row['TotalWood']:<11} | {row['MaxWood']:<9} | {row['TotalStone']:<12} | {row['MaxStone']:<10} | {row['TotalIron']:<11} | {row['TotalPickaxes']:<10} | {row['SuccessRate']:<10.1f}")
    print("\nSummary table saved to summary_table_stone.csv")

if __name__ == "__main__":
    analyze_results()
