import subprocess
import sys
import time
import argparse

"""
Script para ejecutar múltiples algoritmos de RL en paralelo usando diferentes puertos de Minecraft.

Uso:
    python run_parallel_experiments.py --episodes 50
    
Nota: Asegúrate de tener múltiples instancias de Minecraft ejecutándose en diferentes puertos.
      Por defecto, se usan los puertos: 10000, 10001, 10002, 10003, 10004, 10005
"""

# Configuración de algoritmos y puertos
ALGORITHMS_CONFIG = [
    {'algorithm': 'qlearning', 'port': 10000},
    {'algorithm': 'sarsa', 'port': 10001},
    {'algorithm': 'expected_sarsa', 'port': 10002},
    {'algorithm': 'double_q', 'port': 10003},
    {'algorithm': 'monte_carlo', 'port': 10004},
    {'algorithm': 'random', 'port': 10005},
]

def run_parallel_experiments(episodes=50, algorithms_config=None):
    """
    Ejecuta múltiples experimentos en paralelo.
    
    Args:
        episodes: Número de episodios por algoritmo
        algorithms_config: Lista de diccionarios con 'algorithm' y 'port'
    """
    if algorithms_config is None:
        algorithms_config = ALGORITHMS_CONFIG
    
    print(f"{'='*60}")
    print(f"Ejecutando {len(algorithms_config)} algoritmos en paralelo...")
    print(f"Episodios por algoritmo: {episodes}")
    print(f"{'='*60}\n")
    
    # Mostrar configuración
    for config in algorithms_config:
        print(f"  {config['algorithm']:20s} -> Puerto {config['port']}")
    print()
    
    # Iniciar procesos en paralelo
    processes = []
    start_time = time.time()
    
    for config in algorithms_config:
        algo = config['algorithm']
        port = config['port']
        
        print(f"Iniciando {algo} en puerto {port}...")
        
        # Ejecutar proceso en segundo plano
        process = subprocess.Popen(
            [sys.executable, 'wood_agent.py', 
             '--algorithm', algo, 
             '--episodes', str(episodes),
             '--port', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        processes.append({
            'process': process,
            'algorithm': algo,
            'port': port,
            'start_time': time.time()
        })
        
        # Pequeña pausa entre inicios para evitar conflictos
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"Todos los procesos iniciados. Esperando finalización...")
    print(f"{'='*60}\n")
    
    # Esperar a que todos los procesos terminen
    results = []
    for proc_info in processes:
        process = proc_info['process']
        algo = proc_info['algorithm']
        port = proc_info['port']
        
        print(f"Esperando a {algo} (puerto {port})...")
        
        # Esperar a que termine
        stdout, stderr = process.communicate()
        elapsed = time.time() - proc_info['start_time']
        
        results.append({
            'algorithm': algo,
            'port': port,
            'return_code': process.returncode,
            'elapsed_time': elapsed,
            'stdout': stdout,
            'stderr': stderr
        })
        
        if process.returncode == 0:
            print(f"  ✓ {algo} completado en {elapsed:.2f}s")
        else:
            print(f"  ✗ {algo} falló con código {process.returncode}")
    
    # Resumen final
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"RESUMEN DE EJECUCIÓN")
    print(f"{'='*60}")
    print(f"Tiempo total: {total_time:.2f}s")
    print(f"\nResultados por algoritmo:")
    
    for result in results:
        status = "✓ OK" if result['return_code'] == 0 else f"✗ ERROR ({result['return_code']})"
        print(f"  {result['algorithm']:20s} (puerto {result['port']:5d}): {status} - {result['elapsed_time']:.2f}s")
    
    # Guardar logs si hay errores
    for result in results:
        if result['return_code'] != 0:
            log_file = f"error_{result['algorithm']}_port{result['port']}.log"
            with open(log_file, 'w') as f:
                f.write(f"STDOUT:\n{result['stdout']}\n\n")
                f.write(f"STDERR:\n{result['stderr']}\n")
            print(f"\n  Error log guardado: {log_file}")
    
    print(f"\n{'='*60}\n")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Ejecutar múltiples algoritmos de RL en paralelo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  
  # Ejecutar todos los algoritmos con configuración por defecto
  python run_parallel_experiments.py
  
  # Ejecutar con 100 episodios
  python run_parallel_experiments.py --episodes 100
  
  # Ejecutar solo algunos algoritmos
  python run_parallel_experiments.py --algorithms qlearning sarsa --ports 10000 10001
  
IMPORTANTE: Debes tener instancias de Minecraft ejecutándose en cada puerto antes de iniciar.
        """
    )
    
    parser.add_argument('--episodes', type=int, default=50, 
                        help='Número de episodios por algoritmo (default: 50)')
    parser.add_argument('--algorithms', nargs='+', 
                        choices=['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random'],
                        help='Algoritmos específicos a ejecutar (default: todos)')
    parser.add_argument('--ports', nargs='+', type=int,
                        help='Puertos correspondientes a cada algoritmo')
    
    args = parser.parse_args()
    
    # Configurar algoritmos personalizados si se especifican
    if args.algorithms:
        if args.ports and len(args.ports) != len(args.algorithms):
            print("ERROR: El número de puertos debe coincidir con el número de algoritmos")
            sys.exit(1)
        
        # Usar puertos especificados o generar automáticamente
        ports = args.ports if args.ports else [10000 + i for i in range(len(args.algorithms))]
        
        custom_config = [
            {'algorithm': algo, 'port': port}
            for algo, port in zip(args.algorithms, ports)
        ]
        
        run_parallel_experiments(args.episodes, custom_config)
    else:
        run_parallel_experiments(args.episodes)
