"""
Utilidades para visualización y análisis del entrenamiento RL - Madera

Autor: Sistema de IA
"""
import time
import matplotlib.pyplot as plt
import numpy as np
import pickle


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
    
    if len(recompensas) == 0:
        print("⚠ No hay datos para graficar")
        return
    
    # Crear figura con 3 subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('Análisis de Entrenamiento - Agente RL (Madera)', fontsize=16, fontweight='bold')
    
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
        Número de mejores estados a mostrar
    """
    try:
        with open(modelo_path, 'rb') as f:
            datos = pickle.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {modelo_path}")
        return
    
    Q = datos['Q']
    
    if len(Q) == 0:
        print("⚠ Tabla Q vacía")
        return
    
    print("\n" + "="*70)
    print(f"📊 ANÁLISIS DE LA TABLA Q")
    print("="*70)
    print(f"Total de estados explorados: {len(Q)}")
    
    # Mapeo de índices a nombres de acciones
    ACCIONES = {
        0: "move 1",
        1: "turn 1",
        2: "turn -1",
        3: "jumpmove 1",
        4: "attack 1",
    }
    
    # Encontrar estados con mejores valores Q
    mejores_estados = []
    
    for estado, valores_q in Q.items():
        max_q = np.max(valores_q)
        mejor_accion = np.argmax(valores_q)
        mejores_estados.append((estado, max_q, mejor_accion, valores_q))
    
    # Ordenar por valor Q máximo
    mejores_estados.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🏆 Top {top_n} estados con mejores valores Q:\n")
    
    for i, (estado, max_q, mejor_accion, valores_q) in enumerate(mejores_estados[:top_n], 1):
        print(f"{i}. Estado: {estado}")
        print(f"   Valor Q máximo: {max_q:.2f}")
        print(f"   Mejor acción: {ACCIONES[mejor_accion]}")
        
        # Decodificar estado
        orientacion, madera_cerca, madera_frente, distancia_madera, \
        obstaculo_frente, aire_frente, tiene_madera, altura, mirando_madera = estado
        
        print(f"   Decodificado:")
        print(f"     - Orientación: {['Norte', 'Este', 'Sur', 'Oeste'][orientacion]}")
        print(f"     - Madera cerca: {'Sí' if madera_cerca else 'No'}")
        print(f"     - Madera frente: {'Sí' if madera_frente else 'No'}")
        print(f"     - Distancia madera: {['Muy cerca', 'Cerca', 'Lejos', 'No visible'][distancia_madera]}")
        print(f"     - Tiene madera: {'Sí' if tiene_madera else 'No'}")
        print(f"     - Mirando madera: {'Sí' if mirando_madera else 'No'}")
        print(f"   Valores Q todas acciones: {valores_q}")
        print()
    
    # Estadísticas generales
    todos_valores = []
    for valores_q in Q.values():
        todos_valores.extend(valores_q)
    
    print(f"\n📈 Estadísticas de valores Q:")
    print(f"   Máximo: {np.max(todos_valores):.2f}")
    print(f"   Mínimo: {np.min(todos_valores):.2f}")
    print(f"   Promedio: {np.mean(todos_valores):.2f}")
    print(f"   Desviación estándar: {np.std(todos_valores):.2f}")
    
    # Análisis de acciones preferidas
    conteo_acciones = {i: 0 for i in range(5)}
    for valores_q in Q.values():
        mejor_accion = np.argmax(valores_q)
        conteo_acciones[mejor_accion] += 1
    
    print(f"\n🎯 Distribución de acciones preferidas:")
    for accion_idx, cuenta in sorted(conteo_acciones.items(), key=lambda x: x[1], reverse=True):
        porcentaje = (cuenta / len(Q)) * 100
        print(f"   {ACCIONES[accion_idx]:15s}: {cuenta:4d} estados ({porcentaje:5.1f}%)")
    
    print("="*70 + "\n")


def mostrar_resumen(modelo_path="modelo_agente_madera.pkl"):
    """
    Muestra un resumen completo del entrenamiento
    """
    try:
        with open(modelo_path, 'rb') as f:
            datos = pickle.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {modelo_path}")
        return
    
    recompensas = datos['historial_recompensas']
    pasos = datos['historial_pasos']
    episodios = datos['episodios']
    epsilon = datos['epsilon']
    
    if len(recompensas) == 0:
        print("⚠ No hay datos disponibles")
        return
    
    print("\n" + "="*70)
    print(f"📋 RESUMEN DEL ENTRENAMIENTO - RECOLECCIÓN DE MADERA")
    print("="*70)
    print(f"\n📌 Información General:")
    print(f"   Total episodios: {episodios}")
    print(f"   Estados en tabla Q: {len(datos['Q'])}")
    print(f"   Epsilon final: {epsilon:.4f}")
    
    # Calcular tasa de éxito (recompensa > 100 indica éxito)
    exitos = sum(1 for r in recompensas if r > 100)
    tasa_exito = (exitos / len(recompensas)) * 100
    
    print(f"\n🎯 Rendimiento:")
    print(f"   Episodios exitosos: {exitos}/{len(recompensas)} ({tasa_exito:.1f}%)")
    print(f"   Mejor recompensa: {np.max(recompensas):.2f}")
    print(f"   Peor recompensa: {np.min(recompensas):.2f}")
    print(f"   Recompensa promedio: {np.mean(recompensas):.2f}")
    
    print(f"\n⏱️ Eficiencia:")
    print(f"   Pasos promedio: {np.mean(pasos):.1f}")
    print(f"   Mínimo pasos (mejor): {np.min(pasos)}")
    print(f"   Máximo pasos: {np.max(pasos)}")
    
    # Últimos 10 episodios
    if len(recompensas) >= 10:
        print(f"\n📊 Últimos 10 episodios:")
        print(f"   Recompensa promedio: {np.mean(recompensas[-10:]):.2f}")
        print(f"   Pasos promedio: {np.mean(pasos[-10:]):.1f}")
        exitos_recientes = sum(1 for r in recompensas[-10:] if r > 100)
        print(f"   Tasa de éxito: {exitos_recientes}/10 ({exitos_recientes*10:.0f}%)")
    
    # Tendencia
    if len(recompensas) >= 20:
        primeros_10 = np.mean(recompensas[:10])
        ultimos_10 = np.mean(recompensas[-10:])
        mejora = ultimos_10 - primeros_10
        mejora_pct = (mejora / abs(primeros_10)) * 100 if primeros_10 != 0 else 0
        
        print(f"\n📈 Tendencia de aprendizaje:")
        print(f"   Primeros 10 episodios: {primeros_10:.2f}")
        print(f"   Últimos 10 episodios: {ultimos_10:.2f}")
        print(f"   Mejora: {mejora:+.2f} ({mejora_pct:+.1f}%)")
    
    print("="*70 + "\n")


def exportar_politica(modelo_path="modelo_agente_madera.pkl", output_path="politica_madera.txt"):
    """
    Exporta la política aprendida a un archivo de texto legible
    """
    try:
        with open(modelo_path, 'rb') as f:
            datos = pickle.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {modelo_path}")
        return
    
    Q = datos['Q']
    
    ACCIONES = {
        0: "move 1",
        1: "turn 1",
        2: "turn -1",
        3: "jumpmove 1",
        4: "attack 1",
    }
    
    with open(output_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write("POLÍTICA APRENDIDA - AGENTE RECOLECCIÓN DE MADERA\n")
        f.write("="*70 + "\n\n")
        
        # Ordenar estados por valor Q máximo
        estados_ordenados = sorted(
            [(estado, valores_q) for estado, valores_q in Q.items()],
            key=lambda x: np.max(x[1]),
            reverse=True
        )
        
        for estado, valores_q in estados_ordenados:
            mejor_accion = np.argmax(valores_q)
            max_q = np.max(valores_q)
            
            f.write(f"Estado: {estado}\n")
            f.write(f"Mejor acción: {ACCIONES[mejor_accion]} (Q={max_q:.2f})\n")
            
            # Decodificar
            orientacion, madera_cerca, madera_frente, distancia_madera, \
            obstaculo_frente, aire_frente, tiene_madera, altura, mirando_madera = estado
            
            f.write(f"  Orientación: {['Norte', 'Este', 'Sur', 'Oeste'][orientacion]}\n")
            f.write(f"  Madera cerca: {'Sí' if madera_cerca else 'No'}\n")
            f.write(f"  Madera frente: {'Sí' if madera_frente else 'No'}\n")
            f.write(f"  Mirando madera: {'Sí' if mirando_madera else 'No'}\n")
            f.write(f"  Tiene madera: {'Sí' if tiene_madera else 'No'}\n")
            f.write(f"  Valores Q: {valores_q}\n\n")
    
    print(f"✓ Política exportada a: {output_path}")


# ============================================================================
# EJECUCIÓN DE UTILIDADES
# ============================================================================

if __name__ == "__main__":
    import sys
    
    modelo = "modelo_agente_madera.pkl"
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "graficar":
            graficar_aprendizaje(modelo)
        elif comando == "analizar":
            analizar_tabla_q(modelo)
        elif comando == "resumen":
            mostrar_resumen(modelo)
        elif comando == "exportar":
            exportar_politica(modelo)
        elif comando == "todo":
            mostrar_resumen(modelo)
            analizar_tabla_q(modelo, top_n=10)
            graficar_aprendizaje(modelo)
        else:
            print("Comandos disponibles: graficar, analizar, resumen, exportar, todo")
    else:
        print("\n🔧 Utilidades de Análisis - Agente Recolección de Madera")
        print("="*60)
        print("Uso: python utils.py [comando]")
        print("\nComandos disponibles:")
        print("  graficar  - Genera gráficos de aprendizaje")
        print("  analizar  - Analiza tabla Q")
        print("  resumen   - Muestra resumen del entrenamiento")
        print("  exportar  - Exporta política a archivo txt")
        print("  todo      - Ejecuta todos los análisis")
        print("\nEjemplo: python utils.py todo")
