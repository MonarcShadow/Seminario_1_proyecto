"""
Experiment Runner - Stage 4 (Diamond)
Ejecuta todos los algoritmos secuencialmente para recolección de diamante.
Carga modelos pre-entrenados de Stage 3 (iron) por defecto.
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
    - load_model: si True, carga el modelo de iron por defecto
    """
    print(f"\n{'='*70}")
    print(f"EJECUTANDO: {algorithm.upper()} - Stage 4 (Diamond)")
    print(f"{'='*70}")
    
    # Build command
    cmd = [
        sys.executable,
        'diamond_agent.py',
        '--algorithm', algorithm,
        '--episodes', str(episodes),
        '--seed', str(env_seed),
        '--port', str(port)
    ]
    
    # Add model loading by default
    if load_model:
        iron_model_path = f"../entrenamiento_acumulado/{algorithm}_iron_model.pkl"
        if os.path.exists(iron_model_path):
            cmd.extend(['--load-model', iron_model_path])
            print(f"✓ Cargando modelo pre-entrenado: {iron_model_path}")
        else:
            print(f"⚠ Warning: No se encontró modelo de iron para {algorithm}, entrenando desde cero")
    
    # Run experiment
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✓ {algorithm.upper()} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {algorithm.upper()} falló con código {e.returncode}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠ {algorithm.upper()} interrumpido por el usuario")
        return False

def main():
    """
    Ejecuta todos los algoritmos secuencialmente.
    """
    # Configuration
    algorithms = ['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random']
    episodes = 50
    env_seed = 123456  # Semilla fija para todos los algoritmos
    port = 10000
    
    print("\n" + "="*70)
    print("EXPERIMENTO COMPLETO - Stage 4 (Diamond Collection)")
    print("="*70)
    print(f"Algoritmos: {', '.join([a.upper() for a in algorithms])}")
    print(f"Episodios por algoritmo: {episodes}")
    print(f"Semilla del entorno: {env_seed}")
    print(f"Puerto: {port}")
    print("="*70 + "\n")
    
    results = {}
    
    for algorithm in algorithms:
        success = run_experiment(
            algorithm=algorithm,
            episodes=episodes,
            env_seed=env_seed,
            port=port,
            load_model=True
        )
        results[algorithm] = success
        
        # Pausa entre algoritmos
        if algorithm != algorithms[-1]:
            print("\n⏸  Esperando 5 segundos antes del siguiente algoritmo...")
            import time
            time.sleep(5)
    
    # Summary
    print("\n" + "="*70)
    print("RESUMEN DE EXPERIMENTOS")
    print("="*70)
    for algo, success in results.items():
        status = "✓ EXITOSO" if success else "✗ FALLIDO"
        print(f"{algo.upper():20s} : {status}")
    print("="*70 + "\n")
    
    # Count successes
    successful = sum(1 for s in results.values() if s)
    print(f"Total exitosos: {successful}/{len(algorithms)}")
    
    if successful == len(algorithms):
        print("\n🎉 ¡Todos los experimentos completados exitosamente!")
    elif successful > 0:
        print(f"\n⚠ {len(algorithms) - successful} experimento(s) fallaron")
    else:
        print("\n✗ Todos los experimentos fallaron")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Experimento interrumpido por el usuario")
        sys.exit(1)
