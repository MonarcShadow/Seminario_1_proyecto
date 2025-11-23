import subprocess
import sys
import time

algorithms = ['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random']
episodes = 50  # 50 episodes x 2 minutes each

print(f"Running experiments for {len(algorithms)} algorithms...")

for algo in algorithms:
    print(f"\n{'='*40}")
    print(f"Running {algo}...")
    print(f"{'='*40}")
    
    start_time = time.time()
    try:
        subprocess.run([sys.executable, 'wood_agent.py', '--algorithm', algo, '--episodes', str(episodes)], check=True)
        print(f"Finished {algo} in {time.time() - start_time:.2f} seconds.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {algo}: {e}")
    
    time.sleep(2) # Cool down

print("\nAll experiments completed.")
