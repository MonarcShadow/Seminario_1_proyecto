"""
Utilidades para visualización y análisis del entrenamiento RL

Autor: Sistema de IA
"""

import matplotlib.pyplot as plt
import numpy as np
import pickle


def graficar_aprendizaje(modelo_path="modelo_agente_agua.pkl", guardar=True):
    """
    Genera gráficos del proceso de aprendizaje
    
    Parámetros:
    -----------
    modelo_path: str
        Ruta del archivo del modelo
    guardar: bool
        Si True, guarda las gráficas en archivos
    """
    # Cargar datos
    try:
        with open(modelo_path, 'rb') as f:
            datos = pickle.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {modelo_path}")
        return
    
    recompensas = datos['historial_recompensas']
    pasos = datos['historial_pasos']
    epsilons = datos['historial_epsilon']
    
    if len(recompensas) == 0:
        print("⚠ No hay datos para graficar")
        return
    
    # Crear figura con 3 subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('Análisis de Entrenamiento - Agente RL', fontsize=16, fontweight='bold')
    
    episodios = range(1, len(recompensas) + 1)
    
    # 1. RECOMPENSAS POR EPISODIO
    ax1 = axes[0]
    ax1.plot(episodios, recompensas, alpha=0.6, label='Recompensa por episodio')
    
    # Media móvil (ventana de 10)
    if len(recompensas) >= 10:
        ventana = 10
        media_movil = np.convolve(recompensas, np.ones(ventana)/ventana, mode='valid')
        ax1.plot(range(ventana, len(recompensas)+1), media_movil, 
                color='red', linewidth=2, label=f'Media móvil ({ventana} eps)')
    
    ax1.set_xlabel('Episodio')
    ax1.set_ylabel('Recompensa Total')
    ax1.set_title('Evolución de Recompensas')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. PASOS POR EPISODIO
    ax2 = axes[1]
    ax2.plot(episodios, pasos, color='green', alpha=0.6, label='Pasos por episodio')
    
    if len(pasos) >= 10:
        ventana = 10
        media_movil_pasos = np.convolve(pasos, np.ones(ventana)/ventana, mode='valid')
        ax2.plot(range(ventana, len(pasos)+1), media_movil_pasos,
                color='darkgreen', linewidth=2, label=f'Media móvil ({ventana} eps)')
    
    ax2.set_xlabel('Episodio')
    ax2.set_ylabel('Número de Pasos')
    ax2.set_title('Eficiencia del Agente (menos pasos = mejor)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. DECAIMIENTO DE EPSILON (EXPLORACIÓN)
    ax3 = axes[2]
    ax3.plot(episodios, epsilons, color='orange', linewidth=2)
    ax3.set_xlabel('Episodio')
    ax3.set_ylabel('Epsilon (tasa de exploración)')
    ax3.set_title('Decaimiento de Exploración')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if guardar:
        filename = 'analisis_entrenamiento.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {filename}")
    
    plt.show()


def analizar_tabla_q(modelo_path="modelo_agente_agua.pkl", top_n=10):
    """
    Analiza la tabla Q aprendida
    
    Parámetros:
    -----------
    modelo_path: str
        Ruta del archivo del modelo
    top_n: int
        Mostrar los N estados con mayor valor Q
    """
    try:
        with open(modelo_path, 'rb') as f:
            datos = pickle.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {modelo_path}")
        return
    
    Q = datos['Q']
    
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE LA TABLA Q")
    print("="*80)
    print(f"Total de estados visitados: {len(Q)}")
    
    # Acciones
    acciones_nombres = ["move 1", "turn 1", "turn -1", "jumpmove 1"]
    
    # Encontrar estados con mayor valor Q
    valores_maximos = []
    for estado, valores_q in Q.items():
        max_q = np.max(valores_q)
        mejor_accion = np.argmax(valores_q)
        valores_maximos.append((estado, max_q, mejor_accion, valores_q))
    
    # Ordenar por valor Q máximo
    valores_maximos.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🏆 Top {top_n} estados con mayor valor Q:\n")
    print(f"{'#':<4} {'Estado':<50} {'Mejor Acción':<15} {'Max Q':>10}")
    print("-" * 80)
    
    for i, (estado, max_q, mejor_accion, valores_q) in enumerate(valores_maximos[:top_n]):
        estado_str = str(estado)
        if len(estado_str) > 47:
            estado_str = estado_str[:44] + "..."
        
        print(f"{i+1:<4} {estado_str:<50} {acciones_nombres[mejor_accion]:<15} {max_q:>10.2f}")
    
    # Estadísticas generales
    print("\n" + "="*80)
    print("📈 ESTADÍSTICAS DE VALORES Q")
    print("="*80)
    
    todos_valores = []
    for valores_q in Q.values():
        todos_valores.extend(valores_q)
    
    if todos_valores:
        print(f"Valor Q promedio: {np.mean(todos_valores):.4f}")
        print(f"Valor Q máximo: {np.max(todos_valores):.4f}")
        print(f"Valor Q mínimo: {np.min(todos_valores):.4f}")
        print(f"Desviación estándar: {np.std(todos_valores):.4f}")
    
    # Distribución de acciones preferidas
    print("\n" + "="*80)
    print("🎯 DISTRIBUCIÓN DE ACCIONES PREFERIDAS")
    print("="*80)
    
    acciones_conteo = [0, 0, 0, 0]
    for valores_q in Q.values():
        mejor_accion = np.argmax(valores_q)
        acciones_conteo[mejor_accion] += 1
    
    total = sum(acciones_conteo)
    for i, (nombre, count) in enumerate(zip(acciones_nombres, acciones_conteo)):
        porcentaje = 100 * count / total if total > 0 else 0
        barra = "█" * int(porcentaje / 2)
        print(f"{nombre:<15}: {count:>5} ({porcentaje:>5.1f}%) {barra}")
    
    print("="*80 + "\n")


def simular_episodio_greedy(agente, entorno, agent_host, max_pasos=200):
    """
    Simula un episodio usando solo explotación (sin exploración)
    Útil para evaluar el desempeño real del agente entrenado
    
    Parámetros:
    -----------
    agente: AgenteQLearning
        Agente entrenado
    entorno: EntornoMalmo
        Entorno de Malmo
    agent_host: MalmoPython.AgentHost
        Cliente de Malmo
    max_pasos: int
        Máximo de pasos
    
    Retorna:
    --------
    dict: Estadísticas del episodio
    """
    epsilon_original = agente.epsilon
    agente.epsilon = 0.0  # Sin exploración
    
    entorno.reset()
    pasos = 0
    recompensa_total = 0
    trayectoria = []
    
    print("\n🎬 SIMULACIÓN EN MODO GREEDY (sin exploración)")
    print("="*60)
    
    while entorno.actualizar_world_state() and pasos < max_pasos:
        obs = entorno.obtener_observacion()
        if obs is None:
            time.sleep(0.1)
            continue
        
        # Estado actual
        estado = agente.obtener_estado_discretizado(obs)
        
        # Elegir mejor acción (greedy)
        accion_idx = agente.elegir_accion(estado)
        comando = agente.obtener_comando(accion_idx)
        
        # Ejecutar
        entorno.ejecutar_accion(comando)
        
        # Observar resultado
        if not entorno.actualizar_world_state():
            break
        
        obs_siguiente = entorno.obtener_observacion()
        if obs_siguiente is None:
            break
        
        # Recompensa
        recompensa = entorno.calcular_recompensa(obs_siguiente, comando)
        recompensa_total += recompensa
        
        # Guardar trayectoria
        x = obs_siguiente.get("XPos", 0)
        y = obs_siguiente.get("YPos", 64)
        z = obs_siguiente.get("ZPos", 0)
        trayectoria.append((x, y, z))
        
        # Mostrar progreso
        if pasos % 10 == 0:
            print(f"Paso {pasos:3d}: Pos({x:5.1f}, {y:5.1f}, {z:5.1f}) | "
                  f"Acción: {comando:12s} | R acum: {recompensa_total:+7.2f}")
        
        # Verificar éxito
        if entorno.verificar_agua_encontrada(obs_siguiente):
            print(f"\n✓ ¡AGUA ENCONTRADA en paso {pasos}!")
            break
        
        pasos += 1
        time.sleep(0.15)
    
    # Restaurar epsilon
    agente.epsilon = epsilon_original
    
    print("\n" + "="*60)
    print(f"📊 RESULTADO DE SIMULACIÓN")
    print(f"   Pasos totales: {pasos}")
    print(f"   Recompensa total: {recompensa_total:.2f}")
    print(f"   Distancia recorrida: {len(trayectoria)} posiciones")
    print("="*60 + "\n")
    
    return {
        'pasos': pasos,
        'recompensa_total': recompensa_total,
        'trayectoria': trayectoria
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "graficar":
            graficar_aprendizaje()
        elif comando == "analizar":
            analizar_tabla_q()
        else:
            print("Comandos disponibles:")
            print("  python utils.py graficar  - Generar gráficos de entrenamiento")
            print("  python utils.py analizar  - Analizar tabla Q")
    else:
        print("Uso: python utils.py [graficar|analizar]")
