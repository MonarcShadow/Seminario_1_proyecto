"""
Experiment Runner - Stage 3 (Iron Ore)
Ejecuta todos los algoritmos secuencialmente para recolección de hierro.
Carga modelos pre-entrenados de Stage 2 (stone) por defecto.
"""

import subprocess
import os
import sys

def run_experiment(algorithm, episodes=50, env_seed=123456, port=10000, load_model=True):
    """
    Ejecuta un experimento con un algoritmo específico.
    
    Parameters:
    - algorithm: nombre del algoritmo
    - episodes: número de episodios
    - env_seed: semilla del entorno
    - port: puerto de Minecraft
    - load_model: si True, carga el modelo de stone por defecto
    """
    print(f"\n{'='*70}")
    print(f"EJECUTANDO: {algorithm.upper()} - Stage 3 (Iron Ore)")
    print(f"{'='*70}")
    
    # Build command
    cmd = [
        sys.executable,
        'iron_agent.py',
        '--algorithm', algorithm,
        '--episodes', str(episodes),
        '--env-seed', str(env_seed),
        '--port', str(port)
    ]
    
    # Add model loading by default
    if load_model:
        stone_model_path = f"../entrenamiento_acumulado/{algorithm}_stone_model.pkl"
        if os.path.exists(stone_model_path):
            cmd.extend(['--load-model', stone_model_path])
            print(f"✓ Cargando modelo pre-entrenado: {stone_model_path}")
        else:
            print(f"⚠ Warning: No se encontró modelo de stone para {algorithm}, entrenando desde cero")
    
    # Run experiment
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✓ {algorithm.upper()} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error ejecutando {algorithm}: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠ Experimento {algorithm} interrumpido por el usuario")
        return False

def main():
    """Ejecuta todos los algoritmos secuencialmente."""
    algorithms = ['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random']
    
    # Configuration
    episodes = 50
    env_seed = 123456
    port = 10000
    
    print("\n" + "="*70)
    print("EXPERIMENTOS - STAGE 3 (IRON ORE)")
    print("="*70)
    print(f"Episodios por algoritmo: {episodes}")
    print(f"Semilla del entorno: {env_seed}")
    print(f"Puerto Minecraft: {port}")
    print(f"Transfer Learning: Modelos de Stage 2 (stone) cargados por defecto")
    print("="*70)
    
    successful = []
    failed = []
    
    for algo in algorithms:
        success = run_experiment(algo, episodes, env_seed, port, load_model=True)
        
        if success:
            successful.append(algo)
        else:
            failed.append(algo)
        
        # Wait between experiments
        import time
        time.sleep(2)
    
    # Summary
    print("\n" + "="*70)
    print("RESUMEN DE EXPERIMENTOS")
    print("="*70)
    print(f"✓ Exitosos ({len(successful)}): {', '.join(successful)}")
    if failed:
        print(f"✗ Fallidos ({len(failed)}): {', '.join(failed)}")
    print("="*70)
    
    # Run analysis
    if successful:
        print("\nEjecutando análisis de resultados...")
        try:
            subprocess.run([sys.executable, 'analyze_results.py'], check=True)
            print("✓ Análisis completado")
        except Exception as e:
            print(f"✗ Error en análisis: {e}")

if __name__ == "__main__":
    main()
