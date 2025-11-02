"""
Utilidades para visualización y análisis del entrenamiento RL
Para el agente de recolección de madera

Autor: Sistema de IA
"""

import matplotlib.pyplot as plt
import numpy as np
import pickle
import time


def graficar_aprendizaje(modelo_path="modelo_agente_madera.pkl", guardar=True):
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
    madera = datos.get('historial_madera', [])
    
    if len(recompensas) == 0:
        print("⚠ No hay datos para graficar")
        return
    
    # Crear figura con 4 subplots
    fig, axes = plt.subplots(4, 1, figsize=(14, 12))
    fig.suptitle('Análisis de Entrenamiento - Agente Recolección de Madera', 
                 fontsize=16, fontweight='bold')
    
    episodios = range(1, len(recompensas) + 1)
    
    # 1. RECOMPENSAS POR EPISODIO
    ax1 = axes[0]
    ax1.plot(episodios, recompensas, alpha=0.6, color='blue', label='Recompensa por episodio')
    
    # Media móvil (ventana de 5)
    if len(recompensas) >= 5:
        ventana = 5
        media_movil = np.convolve(recompensas, np.ones(ventana)/ventana, mode='valid')
        ax1.plot(range(ventana, len(recompensas)+1), media_movil, 
                color='red', linewidth=2, label=f'Media móvil ({ventana} eps)')
    
    ax1.set_xlabel('Episodio')
    ax1.set_ylabel('Recompensa Total')
    ax1.set_title('Evolución de Recompensas')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.3)
    
    # 2. MADERA RECOLECTADA POR EPISODIO
    ax2 = axes[1]
    if len(madera) > 0:
        colores = ['red' if m < 3 else 'green' for m in madera]
        ax2.bar(episodios, madera, color=colores, alpha=0.7, 
               label='Madera recolectada')
        ax2.axhline(y=3, color='gold', linestyle='--', linewidth=2, 
                   label='Objetivo (3 bloques)')
        
        if len(madera) >= 5:
            ventana = 5
            media_movil_madera = np.convolve(madera, np.ones(ventana)/ventana, mode='valid')
            ax2.plot(range(ventana, len(madera)+1), media_movil_madera,
                    color='darkgreen', linewidth=2, label=f'Media móvil ({ventana} eps)')
    
    ax2.set_xlabel('Episodio')
    ax2.set_ylabel('Bloques de Madera')
    ax2.set_title('Madera Recolectada por Episodio (Verde = Éxito ≥3)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, max(madera + [3]) + 0.5 if madera else 4)
    
    # 3. PASOS POR EPISODIO
    ax3 = axes[2]
    ax3.plot(episodios, pasos, color='purple', alpha=0.6, label='Pasos por episodio')
    
    if len(pasos) >= 5:
        ventana = 5
        media_movil_pasos = np.convolve(pasos, np.ones(ventana)/ventana, mode='valid')
        ax3.plot(range(ventana, len(pasos)+1), media_movil_pasos,
                color='darkviolet', linewidth=2, label=f'Media móvil ({ventana} eps)')
    
    ax3.set_xlabel('Episodio')
    ax3.set_ylabel('Número de Pasos')
    ax3.set_title('Eficiencia del Agente (menos pasos = mejor)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. DECAIMIENTO DE EPSILON (EXPLORACIÓN)
    ax4 = axes[3]
    ax4.plot(episodios, epsilons, color='orange', linewidth=2)
    ax4.set_xlabel('Episodio')
    ax4.set_ylabel('Epsilon (tasa de exploración)')
    ax4.set_title('Decaimiento de Exploración')
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, max(epsilons) * 1.1)
    
    plt.tight_layout()
    
    if guardar:
        filename = 'analisis_entrenamiento_madera.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✓ Gráfico guardado: {filename}")
    
    plt.show()


def analizar_tabla_q(modelo_path="modelo_agente_madera.pkl", top_n=15):
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
    print("📊 ANÁLISIS DE LA TABLA Q - RECOLECCIÓN DE MADERA")
    print("="*80)
    print(f"Total de estados visitados: {len(Q)}")
    
    # Acciones
    acciones_nombres = [
        "move 1",
        "turn 1", 
        "turn -1",
        "jumpmove 1",
        "attack 1",
        "strafe 1",
        "strafe -1"
    ]
    
    # Encontrar estados con mayor valor Q
    valores_maximos = []
    for estado, valores_q in Q.items():
        max_q = np.max(valores_q)
        mejor_accion = np.argmax(valores_q)
        valores_maximos.append((estado, max_q, mejor_accion, valores_q))
    
    # Ordenar por valor Q máximo
    valores_maximos.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🏆 Top {top_n} estados con mayor valor Q:\n")
    print(f"{'#':<4} {'Estado':<55} {'Mejor Acción':<15} {'Max Q':>10}")
    print("-" * 85)
    
    for i, (estado, max_q, mejor_accion, valores_q) in enumerate(valores_maximos[:top_n]):
        estado_str = str(estado)
        if len(estado_str) > 52:
            estado_str = estado_str[:49] + "..."
        
        print(f"{i+1:<4} {estado_str:<55} {acciones_nombres[mejor_accion]:<15} {max_q:>10.2f}")
    
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
    
    acciones_conteo = [0] * len(acciones_nombres)
    for valores_q in Q.values():
        mejor_accion = np.argmax(valores_q)
        acciones_conteo[mejor_accion] += 1
    
    total = sum(acciones_conteo)
    for i, (nombre, count) in enumerate(zip(acciones_nombres, acciones_conteo)):
        porcentaje = 100 * count / total if total > 0 else 0
        barra = "█" * int(porcentaje / 2)
        print(f"{nombre:<15}: {count:>5} ({porcentaje:>5.1f}%) {barra}")
    
    # Análisis específico de estados con madera
    print("\n" + "="*80)
    print("🪵 ANÁLISIS DE ESTADOS CON MADERA VISIBLE")
    print("="*80)
    
    estados_con_madera = []
    for estado, valores_q in Q.items():
        # estado = (orientacion, nivel_madera, nivel_inventario, mirando_madera, 
        #           dist_categoria, obstaculo_frente, indicador_hojas)
        if len(estado) >= 4 and estado[1] > 0:  # nivel_madera > 0
            estados_con_madera.append((estado, valores_q))
    
    print(f"Estados con madera visible: {len(estados_con_madera)}")
    
    if estados_con_madera:
        # Analizar acciones preferidas cuando hay madera
        acciones_con_madera = [0] * len(acciones_nombres)
        for estado, valores_q in estados_con_madera:
            mejor_accion = np.argmax(valores_q)
            acciones_con_madera[mejor_accion] += 1
        
        print("\nAcciones preferidas con madera visible:")
        total_madera = sum(acciones_con_madera)
        for i, (nombre, count) in enumerate(zip(acciones_nombres, acciones_con_madera)):
            if count > 0:
                porcentaje = 100 * count / total_madera
                print(f"  {nombre:<15}: {count:>4} ({porcentaje:>5.1f}%)")
    
    print("="*80 + "\n")


def simular_episodio_greedy(agente, entorno, agent_host, max_pasos=500):
    """
    Simula un episodio usando solo explotación (sin exploración)
    Útil para evaluar el desempeño real del agente entrenado
    
    Parámetros:
    -----------
    agente: AgenteMaderaQLearning
        Agente entrenado
    entorno: EntornoMadera
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
    acciones_realizadas = []
    
    print("\n🎬 SIMULACIÓN EN MODO GREEDY (sin exploración)")
    print("="*70)
    
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
        acciones_realizadas.append(comando)
        
        # Ejecutar
        entorno.ejecutar_accion(comando)
        
        # Observar resultado
        if not entorno.actualizar_world_state():
            break
        
        obs_siguiente = entorno.obtener_observacion()
        if obs_siguiente is None:
            break
        
        # Recompensa
        recompensa_malmo = 0.0
        for reward in entorno.world_state.rewards:
            recompensa_malmo += reward.getValue()
        
        recompensa = entorno.calcular_recompensa(obs_siguiente, comando, recompensa_malmo)
        recompensa_total += recompensa
        
        # Guardar trayectoria
        x = obs_siguiente.get("XPos", 0)
        y = obs_siguiente.get("YPos", 64)
        z = obs_siguiente.get("ZPos", 0)
        trayectoria.append((x, y, z))
        
        # Información de inventario
        madera_actual = entorno.obtener_cantidad_madera(obs_siguiente)
        
        # Mostrar progreso
        if pasos % 20 == 0:
            linea_vista = obs_siguiente.get("LineOfSight", {})
            mirando = linea_vista.get("type", "air")
            
            print(f"Paso {pasos:3d}: Pos({x:5.1f}, {y:5.1f}, {z:5.1f}) | "
                  f"Mirando: {mirando:12s} | Madera: {madera_actual}/3 | "
                  f"Acción: {comando:12s} | R acum: {recompensa_total:+7.2f}")
        
        # Verificar éxito
        objetivo_completado, madera_final = entorno.verificar_objetivo_completado(obs_siguiente)
        if objetivo_completado:
            print(f"\n✓ ¡OBJETIVO COMPLETADO en paso {pasos}!")
            print(f"   🪵 Madera recolectada: {madera_final} bloques")
            break
        
        pasos += 1
        time.sleep(0.1)
    
    # Restaurar epsilon
    agente.epsilon = epsilon_original
    
    # Obtener madera final
    obs_final = entorno.obtener_observacion()
    madera_final = entorno.obtener_cantidad_madera(obs_final) if obs_final else 0
    
    print("\n" + "="*70)
    print(f"📊 RESULTADO DE SIMULACIÓN")
    print(f"   Pasos totales: {pasos}")
    print(f"   Madera recolectada: {madera_final}/3")
    print(f"   Éxito: {'SÍ ✓' if madera_final >= 3 else 'NO ✗'}")
    print(f"   Recompensa total: {recompensa_total:.2f}")
    print(f"   Distancia recorrida: {len(trayectoria)} posiciones")
    
    # Resumen de acciones
    from collections import Counter
    conteo_acciones = Counter(acciones_realizadas)
    print(f"\n   Acciones ejecutadas:")
    for accion, cantidad in conteo_acciones.most_common():
        print(f"      {accion:12s}: {cantidad:3d} veces")
    
    print("="*70 + "\n")
    
    return {
        'pasos': pasos,
        'madera': madera_final,
        'exito': madera_final >= 3,
        'recompensa_total': recompensa_total,
        'trayectoria': trayectoria,
        'acciones': acciones_realizadas
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
            print("  python utils_madera.py graficar  - Generar gráficos de entrenamiento")
            print("  python utils_madera.py analizar  - Analizar tabla Q")
    else:
        print("Uso: python utils_madera.py [graficar|analizar]")
