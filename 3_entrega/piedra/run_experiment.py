import subprocess
import sys

# List of algorithms to test
algorithms = ['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random']
episodes = 50

# Path to pre-trained wood agent models (optional)
wood_model_path = "../entrenamiento_acumulado"

print("Running Stage 2 (Stone Pickaxe) experiments for 6 algorithms...")

for algo in algorithms:
    print(f"\n{'='*40}")
    print(f"Running {algo}...")
    print(f"{'='*40}")
    
    # Option to load pre-trained model from wood stage
    # Uncomment if you want to continue from wood agent training
    # model_file = f"{wood_model_path}/{algo}_model.pkl"
    # if os.path.exists(model_file):
    #     subprocess.run([sys.executable, "stone_agent.py", "--algorithm", algo, "--episodes", str(episodes), "--load-model", model_file])
    # else:
    #     subprocess.run([sys.executable, "stone_agent.py", "--algorithm", algo, "--episodes", str(episodes)])
    
    # Train from scratch for Stage 2
    subprocess.run([sys.executable, "stone_agent.py", "--algorithm", algo, "--episodes", str(episodes)])

print("\n" + "="*40)
print("All experiments completed!")
print("="*40)
