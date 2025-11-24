"""
Results Analysis Script - Stage 3 (Iron Ore)
Compara el rendimiento de todos los algoritmos en la tarea de recolección de hierro.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_algorithm_data(algorithm_name):
    """Carga los datos CSV de un algoritmo específico."""
    csv_path = f"resultados/{algorithm_name}_iron_metrics.csv"
    
    if not os.path.exists(csv_path):
        print(f"⚠ Warning: {csv_path} no encontrado")
        return None
    
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Error leyendo {csv_path}: {e}")
        return None

def plot_comparison():
    """
    Genera gráficos comparativos de todos los algoritmos.
    
    Gráficos:
    1. Iron Collected por episodio (líneas)
    2. Total Reward por episodio (líneas)
    3. Average Iron Collected (barras)
    4. Success Rate (barras) - % de episodios con 3+ iron
    """
    algorithms = ['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random']
    colors = ['blue', 'green', 'orange', 'red', 'purple', 'gray']
    
    # Load all algorithm data
    all_data = {}
    for algo in algorithms:
        df = load_algorithm_data(algo)
        if df is not None:
            all_data[algo] = df
    
    if len(all_data) == 0:
        print("❌ No se encontraron datos para analizar")
        return
    
    print(f"✓ Datos cargados para {len(all_data)} algoritmos: {list(all_data.keys())}")
    
    # Create figure with 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Iron Stage - Algorithm Comparison', fontsize=18, fontweight='bold')
    
    # Plot 1: Iron Collected per Episode (line plot)
    ax1 = axes[0, 0]
    for i, (algo, df) in enumerate(all_data.items()):
        ax1.plot(df['Episode'], df['IronCollected'], 
                label=algo.upper(), color=colors[i], linewidth=2, alpha=0.7)
    ax1.axhline(y=3, color='black', linestyle='--', linewidth=2, label='Goal (3 iron)', alpha=0.5)
    ax1.set_xlabel('Episode', fontsize=12)
    ax1.set_ylabel('Iron Collected', fontsize=12)
    ax1.set_title('Iron Collection Progress', fontsize=14, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Total Reward per Episode (line plot)
    ax2 = axes[0, 1]
    for i, (algo, df) in enumerate(all_data.items()):
        ax2.plot(df['Episode'], df['TotalReward'], 
                label=algo.upper(), color=colors[i], linewidth=2, alpha=0.7)
    ax2.set_xlabel('Episode', fontsize=12)
    ax2.set_ylabel('Total Reward', fontsize=12)
    ax2.set_title('Reward per Episode', fontsize=14, fontweight='bold')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Average Iron Collected (bar chart)
    ax3 = axes[1, 0]
    avg_iron = {}
    for algo, df in all_data.items():
        avg_iron[algo] = df['IronCollected'].mean()
    
    algos_sorted = sorted(avg_iron.keys(), key=lambda x: avg_iron[x], reverse=True)
    values = [avg_iron[a] for a in algos_sorted]
    bars = ax3.bar(range(len(algos_sorted)), values, 
                   color=[colors[algorithms.index(a)] for a in algos_sorted], alpha=0.7)
    ax3.set_xticks(range(len(algos_sorted)))
    ax3.set_xticklabels([a.upper() for a in algos_sorted], rotation=45, ha='right')
    ax3.set_ylabel('Average Iron Collected', fontsize=12)
    ax3.set_title('Average Iron Collection', fontsize=14, fontweight='bold')
    ax3.axhline(y=3, color='red', linestyle='--', linewidth=2, label='Goal (3)', alpha=0.5)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, values)):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Plot 4: Success Rate (% episodes with 3+ iron)
    ax4 = axes[1, 1]
    success_rates = {}
    for algo, df in all_data.items():
        success_count = (df['IronCollected'] >= 3).sum()
        total_episodes = len(df)
        success_rates[algo] = (success_count / total_episodes) * 100
    
    algos_sorted = sorted(success_rates.keys(), key=lambda x: success_rates[x], reverse=True)
    values = [success_rates[a] for a in algos_sorted]
    bars = ax4.bar(range(len(algos_sorted)), values,
                   color=[colors[algorithms.index(a)] for a in algos_sorted], alpha=0.7)
    ax4.set_xticks(range(len(algos_sorted)))
    ax4.set_xticklabels([a.upper() for a in algos_sorted], rotation=45, ha='right')
    ax4.set_ylabel('Success Rate (%)', fontsize=12)
    ax4.set_title('Success Rate (3+ Iron)', fontsize=14, fontweight='bold')
    ax4.set_ylim(0, 100)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, values)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    # Save plot
    output_path = "resultados/iron_algorithm_comparison.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Gráfico comparativo guardado en: {output_path}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS - STAGE 3 (IRON ORE)")
    print("="*60)
    
    for algo in algos_sorted:
        df = all_data[algo]
        print(f"\n{algo.upper()}:")
        print(f"  • Iron promedio: {avg_iron[algo]:.2f}")
        print(f"  • Success rate: {success_rates[algo]:.1f}%")
        print(f"  • Reward promedio: {df['TotalReward'].mean():.1f}")
        print(f"  • Max iron en un episodio: {df['IronCollected'].max()}")
    
    print("\n" + "="*60)
    
    # plt.show()  # Uncomment to display plot
    plt.close()

if __name__ == "__main__":
    print("Analizando resultados de Stage 3 (Iron Ore)...\n")
    plot_comparison()
