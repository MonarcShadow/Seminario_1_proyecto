"""
Parallel Experiment Runner - Stage 3 (Iron Ore)
Ejecuta todos los algoritmos en paralelo usando diferentes puertos de Minecraft.
Carga modelos pre-entrenados de Stage 2 (stone) por defecto.
"""

import subprocess
import sys
import os
import time

def main():
    """
    Ejecuta 6 algoritmos en paralelo, cada uno en un puerto diferente.
    Puertos: 10001-10006
    Transfer Learning: Carga modelos stone_model.pkl por defecto
    """
    algorithms = ['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random']
    base_port = 10001
    episodes = 50
    env_seed = 123456
    
    print("\n" + "="*70)
    print("EXPERIMENTOS PARALELOS - STAGE 3 (IRON ORE)")
    print("="*70)
    print(f"Algoritmos: {', '.join([a.upper() for a in algorithms])}")
    print(f"Episodios: {episodes}")
    print(f"Semilla: {env_seed}")
    print(f"Puertos: {base_port} a {base_port + len(algorithms) - 1}")
    print(f"Transfer Learning: Modelos de Stage 2 (stone) cargados por defecto")
    print("="*70)
    
    processes = []
    
    for i, algorithm in enumerate(algorithms):
        port = base_port + i
        
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
        stone_model_path = f"../entrenamiento_acumulado/{algorithm}_stone_model.pkl"
        if os.path.exists(stone_model_path):
            cmd.extend(['--load-model', stone_model_path])
            print(f"✓ {algorithm.upper()} (Puerto {port}) - Cargando: {stone_model_path}")
        else:
            print(f"⚠ {algorithm.upper()} (Puerto {port}) - Sin modelo previo, entrenando desde cero")
        
        # Start process
        try:
            # Redirect stdout/stderr to files for each algorithm
            log_file = open(f"resultados/{algorithm}_iron_log.txt", "w")
            process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT
            )
            processes.append({
                'name': algorithm,
                'process': process,
                'port': port,
                'log_file': log_file
            })
            print(f"  → Proceso iniciado (PID: {process.pid})")
        except Exception as e:
            print(f"✗ Error iniciando {algorithm}: {e}")
    
    print("\n" + "="*70)
    print(f"✓ {len(processes)} procesos ejecutándose en paralelo")
    print("="*70)
    print("\nEsperando a que todos los experimentos terminen...")
    print("(Esto puede tomar varios minutos)")
    print("\nLogs en tiempo real:")
    for p in processes:
        print(f"  • {p['name']}: resultados/{p['name']}_iron_log.txt")
    
    # Wait for all processes to complete
    completed = []
    failed = []
    
    while len(completed) + len(failed) < len(processes):
        for p in processes:
            if p['name'] not in completed and p['name'] not in failed:
                poll = p['process'].poll()
                if poll is not None:
                    # Process finished
                    if poll == 0:
                        completed.append(p['name'])
                        print(f"\n✓ {p['name'].upper()} completado exitosamente")
                    else:
                        failed.append(p['name'])
                        print(f"\n✗ {p['name'].upper()} falló (código: {poll})")
                    p['log_file'].close()
        
        time.sleep(5)  # Check every 5 seconds
    
    # Summary
    print("\n" + "="*70)
    print("RESUMEN DE EXPERIMENTOS PARALELOS")
    print("="*70)
    print(f"✓ Completados ({len(completed)}): {', '.join(completed)}")
    if failed:
        print(f"✗ Fallidos ({len(failed)}): {', '.join(failed)}")
    print("="*70)
    
    # Run analysis
    if completed:
        print("\nEjecutando análisis de resultados...")
        try:
            subprocess.run([sys.executable, 'analyze_results.py'], check=True)
            print("✓ Análisis completado")
        except Exception as e:
            print(f"✗ Error en análisis: {e}")

if __name__ == "__main__":
    main()
