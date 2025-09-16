import os
import time
import matplotlib.pyplot as plt
import csv
import numpy as np

from agente import Agente
from laberinto import generar_laberinto
from busqueda import bfs, dfs, greedy, a_star

# -------------------------
# Generar laberinto en Minecraft
# -------------------------
inicio_world, salida_world = generar_laberinto()
base_x = inicio_world[0] - 1
base_y = inicio_world[1]
base_z = inicio_world[2] - 1

# Coordenadas en grilla
N = 25
grid_inicio = (1, 1)
grid_salida = (24, 24)

# Construir laberinto (0 = libre, 1 = muro)
laberinto = {(x, z): 0 for x in range(N) for z in range(N)}
paredes_internas = [
    (5,0),(5,1),(5,2),(5,3),(5,4),
    (10,5),(11,5),(12,5),(13,5),
    (15,10),(15,11),(15,12),
    (20,15),(20,16),(20,17),(20,18)
]
for (x, z) in paredes_internas:
    laberinto[(x, z)] = 1

# Perímetro como muro
for i in range(N):
    laberinto[(i, 0)] = 1
    laberinto[(i, N-1)] = 1
    laberinto[(0, i)] = 1
    laberinto[(N-1, i)] = 1

# -------------------------
# Ejecutar algoritmos de búsqueda
# -------------------------
algoritmos = {
    "BFS": bfs,
    "DFS": dfs,
    "Greedy": greedy,
    "A*": a_star
}

resultados = {}

for nombre, funcion in algoritmos.items():
    print(f"Ejecutando {nombre}...")
    camino, metricas = funcion(laberinto, grid_inicio, grid_salida)
    resultados[nombre] = {"camino": camino, "metricas": metricas}

# -------------------------
# Inicializar agente
# -------------------------
agente = Agente(inicio_world)

# -------------------------
# Configurar gráfico
# -------------------------
plt.ion()
fig, ax = plt.subplots(figsize=(7,7))
ax.set_xlim(-0.5, N - 0.5)
ax.set_ylim(-0.5, N - 0.5)
ax.set_title("Comparación de algoritmos de búsqueda")
ax.set_xlabel("X (grilla)")
ax.set_ylabel("Z (grilla)")

# Dibujar muros
paredes_x = [x for (x,z),v in laberinto.items() if v == 1]
paredes_z = [z for (x,z),v in laberinto.items() if v == 1]
ax.scatter(paredes_x, paredes_z, c="black", marker="s", s=40, label="Muro")

# Marcar inicio y salida
ax.scatter(grid_inicio[0], grid_inicio[1], c="green", marker="o", s=140, label="Inicio")
ax.scatter(grid_salida[0], grid_salida[1], c="red", marker="*", s=180, label="Salida")

# Punto que representa al bot
punto, = ax.plot([], [], "ro", markersize=8, zorder=5)

# -------------------------
# Conversión de grilla -> mundo
# -------------------------
def grid_a_mundo(mx, mz):
    wx = base_x + mx + 0.5
    wy = base_y + 1
    wz = base_z + mz + 0.5
    return (wx, wy, wz)

# -------------------------
# Función para recorrer camino
# -------------------------
def recorrer_camino(camino, color, nombre):
    if not camino:
        return
    xs, zs = zip(*camino)
    ax.plot(xs, zs, color=color, linewidth=2.2, zorder=3, label=nombre)
    plt.pause(0.05)
    for (mx, mz) in camino:
        punto.set_data([mx], [mz])
        wx, wy, wz = grid_a_mundo(mx, mz)
        agente.mc.player.setPos(wx, wy, wz)
        plt.pause(0.12)
    punto.set_data([], [])

# -------------------------
# Recorrer caminos de cada algoritmo
# -------------------------
colores = {"BFS": "blue", "DFS": "orange", "Greedy": "purple", "A*": "green"}

for nombre in algoritmos.keys():
    camino = resultados[nombre]["camino"]
    ax.set_title(f"{nombre}: explorando camino (long={len(camino) if camino else 0})")
    recorrer_camino(camino, colores[nombre], nombre)
    agente.reiniciar()
    time.sleep(0.5)

plt.legend()
plt.ioff()
plt.show()

from datetime import datetime

# -------------------------
# Guardar métricas con fecha y hora
# -------------------------
os.makedirs("../resultados", exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_path = os.path.join("..", "resultados", f"metricas_{timestamp}.csv")

with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Algoritmo", "Longitud", "NodosExpandidos", "ProfundidadMax", "Tiempo(s)", "Optimo"])
    for nombre, datos in resultados.items():
        m = datos["metricas"]
        writer.writerow([
            nombre,
            m.get("longitud", 0),
            m.get("nodos_expandidos", 0),
            m.get("profundidad_max", 0),
            m.get("tiempo", 0),
            m.get("optimo", "No")
        ])

# -------------------------
# Heatmap de visitas
# -------------------------
visitas = np.zeros((N, N), dtype=int)
for nombre, datos in resultados.items():
    for (mx, mz) in datos["camino"] or []:
        visitas[mz, mx] += 1

plt.figure(figsize=(6,6))
plt.title("Mapa de calor de exploración (todos algoritmos)")
img = plt.imshow(visitas, cmap="hot", origin="lower", extent=[-0.5, N-0.5, -0.5, N-0.5])
plt.colorbar(img, label="Número de visitas")
plt.scatter(grid_inicio[0], grid_inicio[1], c="green", marker="o", s=140)
plt.scatter(grid_salida[0], grid_salida[1], c="red", marker="*", s=180)
plt.savefig(os.path.join("..","resultados","heatmap.png"), dpi=200)
plt.show()

