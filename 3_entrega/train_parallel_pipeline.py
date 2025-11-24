#!/usr/bin/env python3
"""
Script para entrenar el pipeline completo de 5 etapas en paralelo.
Ejecuta los 6 algoritmos simultáneamente usando puertos 10001-10006.

Uso:
    python train_parallel_pipeline.py --episodes 50
    python train_parallel_pipeline.py --episodes 100 --inicio 1 --final 3
    python train_parallel_pipeline.py --episodes 50 --inicio 2 --final 5 --continuar no
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path
import signal
import os

# Mapeo de etapas
STAGES = {
    1: {
        'name': 'madera',
        'script': 'wood_agent.py',
        'load_model': None,  # Primera etapa no carga modelo
        'save_suffix': ''
    },
    2: {
        'name': 'piedra',
        'script': 'stone_agent.py',
        'load_model': 'model.pkl',
        'save_suffix': '_stone'
    },
    3: {
        'name': 'hierro',
        'script': 'iron_agent.py',
        'load_model': 'stone_model.pkl',
        'save_suffix': '_iron'
    },
    4: {
        'name': 'diamante',
        'script': 'diamond_agent.py',
        'load_model': 'iron_model.pkl',
        'save_suffix': '_diamond'
    },
    5: {
        'name': 'desde_cero',
        'script': 'from_scratch_agent.py',
        'load_model': 'diamond_model.pkl',
        'save_suffix': '_scratch'
    }
}

ALGORITHMS = ['qlearning', 'sarsa', 'expected_sarsa', 'double_q', 'monte_carlo', 'random']

ALGORITHM_PORTS = {
    'qlearning': 10001,
    'sarsa': 10002,
    'expected_sarsa': 10003,
    'double_q': 10004,
    'monte_carlo': 10005,
    'random': 10006
}

# Para manejar Ctrl+C
processes = []

def signal_handler(sig, frame):
    """Maneja Ctrl+C para terminar todos los procesos."""
    print("\n\n❌ Interrupción detectada. Terminando todos los procesos...")
    for proc in processes:
        if proc.poll() is None:  # Si el proceso sigue corriendo
            proc.terminate()
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)


def run_stage_parallel(stage_num, episodes, continuar, base_dir):
    """
    Ejecuta una etapa con los 6 algoritmos en paralelo.
    
    Args:
        stage_num: Número de etapa (1-5)
        episodes: Número de episodios
        continuar: Si True, carga modelo anterior; si False, entrena desde cero
        base_dir: Directorio base del proyecto
    
    Returns:
        True si todos los algoritmos terminaron exitosamente
    """
    stage = STAGES[stage_num]
    stage_dir = base_dir / stage['name']
    script_path = stage_dir / stage['script']
    
    print(f"\n{'='*80}")
    print(f"🚀 ETAPA {stage_num}/5: {stage['name'].upper()}")
    print(f"{'='*80}")
    print(f"📂 Directorio: {stage_dir}")
    print(f"📄 Script: {stage['script']}")
    print(f"📊 Episodios: {episodes}")
    print(f"🔄 Continuar entrenamiento: {'Sí' if continuar else 'No'}")
    
    if not script_path.exists():
        print(f"❌ ERROR: No se encuentra {script_path}")
        return False
    
    # Preparar comandos para cada algoritmo
    commands = []
    for algo in ALGORITHMS:
        cmd = [
            'python',
            stage['script'],
            '--algorithm', algo,
            '--episodes', str(episodes),
            '--port', str(ALGORITHM_PORTS[algo])
        ]
        
        # Agregar --load-model si es necesario
        if continuar and stage['load_model'] and stage_num > 1:
            model_path = base_dir / 'entrenamiento_acumulado' / f"{algo}_{stage['load_model']}"
            if model_path.exists():
                cmd.extend(['--load-model', str(model_path)])
                print(f"  ✓ {algo:20} → Cargará {model_path.name}")
            else:
                print(f"  ⚠ {algo:20} → Modelo {model_path.name} no existe, entrenará desde cero")
        else:
            print(f"  ✓ {algo:20} → Entrenará desde cero")
        
        commands.append((algo, cmd, stage_dir))
    
    print(f"\n🔥 Iniciando {len(ALGORITHMS)} procesos en paralelo...")
    print(f"   Puertos: 10001-10006 (localhost)\n")
    
    # Iniciar todos los procesos
    global processes
    processes = []
    start_time = time.time()
    
    for algo, cmd, cwd in commands:
        port = ALGORITHM_PORTS[algo]
        log_file = stage_dir / 'resultados' / f'log_{algo}_{int(time.time())}.txt'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'w') as f:
            proc = subprocess.Popen(
                cmd,
                cwd=str(cwd),
                stdout=f,
                stderr=subprocess.STDOUT,
                text=True
            )
            processes.append(proc)
            print(f"  ✓ [{algo:18}] PID={proc.pid:6} Puerto={port} Log={log_file.name}")
    
    print(f"\n⏳ Esperando a que terminen los {len(processes)} procesos...")
    print("   (Esto puede tomar varios minutos dependiendo de los episodios)")
    print("   Presiona Ctrl+C para cancelar\n")
    
    # Esperar a que terminen todos
    completed = []
    failed = []
    
    while len(completed) + len(failed) < len(processes):
        for i, proc in enumerate(processes):
            if proc in completed or proc in failed:
                continue
            
            ret = proc.poll()
            if ret is not None:
                algo = ALGORITHMS[i]
                if ret == 0:
                    completed.append(proc)
                    elapsed = time.time() - start_time
                    print(f"  ✅ [{algo:18}] Completado (Exit={ret}) - {elapsed:.1f}s transcurridos")
                else:
                    failed.append(proc)
                    print(f"  ❌ [{algo:18}] ERROR (Exit={ret})")
        
        time.sleep(2)  # Verificar cada 2 segundos
    
    elapsed = time.time() - start_time
    print(f"\n{'='*80}")
    print(f"✅ ETAPA {stage_num} COMPLETADA en {elapsed:.1f} segundos ({elapsed/60:.1f} minutos)")
    print(f"   Exitosos: {len(completed)}/{len(processes)}")
    print(f"   Fallidos:  {len(failed)}/{len(processes)}")
    print(f"{'='*80}")
    
    # Verificar que los modelos se guardaron
    if continuar and stage_num < 5:  # Si hay siguiente etapa
        models_saved = []
        for algo in ALGORITHMS:
            model_name = f"{algo}{stage['save_suffix']}_model.pkl"
            model_path = base_dir / 'entrenamiento_acumulado' / model_name
            if model_path.exists():
                models_saved.append(algo)
        
        print(f"\n📦 Modelos guardados: {len(models_saved)}/{len(ALGORITHMS)}")
        for algo in models_saved:
            print(f"   ✓ {algo}{stage['save_suffix']}_model.pkl")
    
    return len(failed) == 0


def main():
    parser = argparse.ArgumentParser(
        description='Entrena el pipeline completo en paralelo (6 algoritmos simultáneos)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Entrenar pipeline completo (etapas 1-5) con 50 episodios
  python train_parallel_pipeline.py --episodes 50
  
  # Entrenar solo etapas 1-3 con 100 episodios
  python train_parallel_pipeline.py --episodes 100 --inicio 1 --final 3
  
  # Entrenar etapas 2-5 sin cargar modelos previos (sobreescribir)
  python train_parallel_pipeline.py --episodes 50 --inicio 2 --final 5 --continuar no
  
  # Entrenar desde etapa 3 hasta 5 con transfer learning
  python train_parallel_pipeline.py --episodes 75 --inicio 3 --continuar si

Notas:
  - Requiere 6 clientes de Minecraft abiertos (puertos 10001-10006)
  - Los logs se guardan en {stage}/resultados/log_{algorithm}_{timestamp}.txt
  - Los modelos se guardan en entrenamiento_acumulado/
        """
    )
    
    parser.add_argument('--episodes', type=int, default=50,
                        help='Número de episodios por algoritmo (default: 50)')
    parser.add_argument('--inicio', type=int, default=1, choices=[1, 2, 3, 4, 5],
                        help='Etapa inicial (1=madera, 2=piedra, 3=hierro, 4=diamante, 5=desde_cero)')
    parser.add_argument('--final', type=int, default=5, choices=[1, 2, 3, 4, 5],
                        help='Etapa final (default: 5)')
    parser.add_argument('--continuar', type=str, default='si', choices=['si', 'no'],
                        help='Cargar entrenamiento anterior (si) o empezar desde cero (no)')
    
    args = parser.parse_args()
    
    # Validaciones
    if args.inicio > args.final:
        print("❌ ERROR: --inicio debe ser menor o igual a --final")
        sys.exit(1)
    
    continuar = args.continuar.lower() == 'si'
    base_dir = Path(__file__).parent.absolute()
    
    # Imprimir configuración
    print("="*80)
    print("🎮 ENTRENAMIENTO PARALELO DEL PIPELINE DE TRANSFER LEARNING")
    print("="*80)
    print(f"📍 Directorio base: {base_dir}")
    print(f"📊 Episodios por algoritmo: {args.episodes}")
    print(f"🎯 Etapas: {args.inicio} → {args.final}")
    print(f"🔄 Modo: {'Transfer Learning (cargar modelos)' if continuar else 'Desde cero (sobreescribir)'}")
    print(f"🌐 Puertos: 10001-10006 (localhost)")
    print(f"🤖 Algoritmos: {', '.join(ALGORITHMS)}")
    print("="*80)
    
    # Verificar que existen las carpetas
    for stage_num in range(args.inicio, args.final + 1):
        stage_dir = base_dir / STAGES[stage_num]['name']
        if not stage_dir.exists():
            print(f"❌ ERROR: No existe la carpeta {stage_dir}")
            sys.exit(1)
    
    print("\n⚠️  IMPORTANTE: Asegúrate de tener 6 clientes de Minecraft abiertos")
    print("   en puertos 10001, 10002, 10003, 10004, 10005, 10006")
    print("\n¿Continuar? (Presiona Enter para iniciar o Ctrl+C para cancelar)")
    input()
    
    # Ejecutar etapas secuencialmente (pero cada etapa ejecuta 6 algoritmos en paralelo)
    total_start = time.time()
    
    for stage_num in range(args.inicio, args.final + 1):
        success = run_stage_parallel(stage_num, args.episodes, continuar, base_dir)
        
        if not success:
            print(f"\n❌ ERROR en etapa {stage_num}. Abortando pipeline.")
            sys.exit(1)
        
        # Pausa entre etapas
        if stage_num < args.final:
            print(f"\n⏸️  Pausa de 10 segundos antes de la siguiente etapa...")
            time.sleep(10)
    
    # Resumen final
    total_time = time.time() - total_start
    num_stages = args.final - args.inicio + 1
    
    print("\n" + "="*80)
    print("🎉 PIPELINE COMPLETO FINALIZADO")
    print("="*80)
    print(f"⏱️  Tiempo total: {total_time:.1f} segundos ({total_time/60:.1f} minutos)")
    print(f"📊 Etapas completadas: {num_stages}")
    print(f"🤖 Algoritmos entrenados: {len(ALGORITHMS)} por etapa")
    print(f"📦 Total de modelos generados: {len(ALGORITHMS) * num_stages}")
    print("\n📂 Revisa los resultados en:")
    for stage_num in range(args.inicio, args.final + 1):
        stage_name = STAGES[stage_num]['name']
        print(f"   - {stage_name}/resultados/")
    print(f"   - entrenamiento_acumulado/")
    print("\n📈 Para analizar los resultados, ejecuta en cada carpeta:")
    print("   python analyze_results.py")
    print("="*80)


if __name__ == '__main__':
    main()
