"""
Parallel Experiment Runner - Stage 5 (From Scratch)
Ejecuta todos los algoritmos en paralelo usando diferentes puertos de Minecraft.
Carga modelos pre-entrenados de Stage 4 (diamond) por defecto.
"""

import subprocess
import sys
import os
import time

def main():
    """
    Ejecuta 6 algoritmos en paralelo, cada uno en un puerto diferente.
    Puertos: 10001-10006
    Transfer Learning: Carga modelos diamond_model.pkl por defecto
    """
    algorithms = ['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random']
    base_port = 10001
    episodes = 50
    env_seed = 123456
    
    print("\n" + "="*70)
    print("EXPERIMENTOS PARALELOS - STAGE 5 (FROM SCRATCH - COMPLETE)")
    print("="*70)
    print(f"Algoritmos: {', '.join([a.upper() for a in algorithms])}")
    print(f"Episodios: {episodes}")
    print(f"Semilla: {env_seed}")
    print(f"Puertos: {base_port} a {base_port + len(algorithms) - 1}")
    print(f"Transfer Learning: Modelos de Stage 4 (diamond) cargados por defecto")
    print("="*70)
    
    processes = []
    
    for i, algorithm in enumerate(algorithms):
        port = base_port + i
        
        # Build command
        cmd = [
            sys.executable,
            'from_scratch_agent.py',
            '--algorithm', algorithm,
            '--episodes', str(episodes),
            '--seed', str(env_seed),
            '--port', str(port)
        ]
        
        # Add model loading by default
        diamond_model_path = f"../entrenamiento_acumulado/{algorithm}_diamond_model.pkl"
        if os.path.exists(diamond_model_path):
            cmd.extend(['--load-model', diamond_model_path])
            print(f"✓ {algorithm.upper()} (Puerto {port}) - Cargando: {diamond_model_path}")
        else:
            print(f"⚠ {algorithm.upper()} (Puerto {port}) - Sin modelo previo, entrenando desde cero")
        
        # Start process
        try:
            # Redirect stdout/stderr to files for each algorithm
            os.makedirs("resultados", exist_ok=True)
            log_file = open(f"resultados/{algorithm}_scratch_log.txt", "w")
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
    print("(Esto puede tomar MUCHO tiempo - pipeline completo)")
    print("\nLogs en tiempo real:")
    for p in processes:
        print(f"  - resultados/{p['name']}_scratch_log.txt")
    
    # Wait for all processes
    try:
        while any(p['process'].poll() is None for p in processes):
            time.sleep(5)
            # Show status
            running = sum(1 for p in processes if p['process'].poll() is None)
            completed = len(processes) - running
            print(f"\rProgreso: {completed}/{len(processes)} completados", end="", flush=True)
        
        print("\n\n" + "="*70)
        print("RESULTADOS")
        print("="*70)
        
        # Check exit codes
        all_success = True
        for p in processes:
            exit_code = p['process'].returncode
            status = "✓ EXITOSO" if exit_code == 0 else f"✗ FALLIDO (código {exit_code})"
            print(f"{p['name'].upper():20s} (Puerto {p['port']}): {status}")
            p['log_file'].close()
            if exit_code != 0:
                all_success = False
        
        print("="*70)
        
        if all_success:
            print("\n🎉🎉🎉 ¡TODOS LOS EXPERIMENTOS COMPLETADOS EXITOSAMENTE! 🎉🎉🎉")
            print("✓ Pipeline completo de transfer learning demostrado")
        else:
            print("\n⚠ Algunos experimentos fallaron. Revisa los logs en resultados/")
            
    except KeyboardInterrupt:
        print("\n\n⚠ Interrumpido por el usuario. Terminando procesos...")
        for p in processes:
            if p['process'].poll() is None:
                p['process'].terminate()
                p['log_file'].close()
        print("✓ Todos los procesos terminados")

if __name__ == "__main__":
    main()
