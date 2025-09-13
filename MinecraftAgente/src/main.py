# src/main.py
import os
import time
import random
import csv
import matplotlib.pyplot as plt
import numpy as np

from agente import Agente        # clase Agente (usa mcpi)
from busqueda import bfs_todos   # BFS que explora todo y devuelve (caminos_fallidos, camino_final, metricas)
from laberinto import generar_laberinto  # construye laberinto en Minecraft y devuelve inicio_world, salida_world

# -------------------------
# Generar laberinto en Minecraft
# -------------------------
inicio_world, salida_world = generar_laberinto()   # devuelve coords mundo (x,y,z) de inicio y salida
# Deducir base de la rejilla (porque generar_laberinto colocó inicio en base_x+1, base_z+1)
base_x = inicio_world[0] - 1
base_y = inicio_world[1]
base_z = inicio_world[2] - 1

# Coordenadas de la grilla (índices 0..24)
N = 25
grid_inicio = (1, 1)
grid_salida = (23, 23)

# Construir representación de la grilla (0 = libre, 1 = muro)
laberinto = {(x, z): 0 for x in range(N) for z in range(N)}
# Paredes internas (mismas que usaste)
paredes_internas = [
    (5,0),(5,1),(5,2),(5,3),(5,4),
    (10,5),(11,5),(12,5),(13,5),
    (15,10),(15,11),(15,12),
    (20,15),(20,16),(20,17),(20,18)
]
for (x, z) in paredes_internas:
    laberinto[(x, z)] = 1

# Perímetro como muros
for i in range(N):
    laberinto[(0,i)] = 1
    laberinto[(N-1,i)] = 1
    laberinto[(i,0)] = 1
    laberinto[(i,N-1)] = 1

# -------------------------
# Ejecutar BFS (explora TODO)
# -------------------------
caminos_fallidos_all, camino_final, metricas = bfs_todos(laberinto, grid_inicio, grid_salida)

# Si no hay camino final, camino_final será [] o None
if camino_final is None:
    camino_final = []

# Tomar 20 caminos aleatorios de los fallidos (si hay más)
if len(caminos_fallidos_all) > 20:
    caminos_malos = random.sample(caminos_fallidos_all, 20)
else:
    caminos_malos = list(caminos_fallidos_all)

# -------------------------
# Inicializar agente (usa la posición mundo de inicio)
# -------------------------
agente = Agente(inicio_world)   # Agente espera coords mundo (x,y,z)

# -------------------------
# Preparar figura (matplotlib)
# -------------------------
plt.ion()
fig, ax = plt.subplots(figsize=(7,7))
ax.set_xlim(-0.5, N - 0.5)
ax.set_ylim(-0.5, N - 0.5)
ax.set_title("Exploración de caminos - laberinto 25x25")
ax.set_xlabel("X (grilla)")
ax.set_ylabel("Z (grilla)")

# Dibujar muros (negro)
paredes_x = [x for (x,z),v in laberinto.items() if v == 1]
paredes_z = [z for (x,z),v in laberinto.items() if v == 1]
ax.scatter(paredes_x, paredes_z, c="black", marker="s", s=40, label="Muro")

# Marcar inicio y salida en la grilla (0..24)
ax.scatter(grid_inicio[0], grid_inicio[1], c="green", marker="o", s=140, label="Inicio (1,1)")
ax.scatter(grid_salida[0], grid_salida[1], c="red", marker="*", s=180, label="Salida (23,23)")

# Dibujar TODOS los caminos malos en gris (fijos)
#gray_lines = []
#for camino in caminos_malos:
 #   if not camino:
  #    continue
   # xs, zs = zip(*camino)
    #ln, = ax.plot(xs, zs, color="gray", alpha=0.4, linewidth=1)  # quedan fijos
    #gray_lines.append(ln)

# Punto que representa al bot en el gráfico (rojo)
punto, = ax.plot([], [], "ro", markersize=8, zorder=5)

plt.legend(loc="upper right")
plt.pause(0.2)

# -------------------------
# Función util: convertir coordenadas de grilla -> mundo (centrado)
# -------------------------
def grid_a_mundo(mx, mz):
    """Convierte (mx,mz) índices de grilla a coordenadas mundo centradas (float)."""
    wx = base_x + mx + 0.5
    wy = base_y       # altura para caminar (por encima del piso)
    wz = base_z + mz + 0.5
    return (wx, wy, wz)

# Función para animar un camino (resaltando en amarillo mientras se recorre)
def recorrer_y_animar(camino, color_actual="yellow", delay=0.18):
    if not camino:
        return

    xs, zs = zip(*camino)
    linea_actual, = ax.plot(xs, zs, color=color_actual, linewidth=2.2, zorder=4)
    plt.pause(0.05)

    for (mx, mz) in camino:
        punto.set_data([mx], [mz])
        wx, wy, wz = grid_a_mundo(mx, mz)
        agente.mc.player.setPos(wx, wy, wz)
        plt.pause(delay)

    plt.pause(0.25)
    linea_actual.remove()  # borrar resaltado
    # 🔹 dejar gris fijo después de recorrer
    ax.plot(xs, zs, color="gray", alpha=0.4, linewidth=1)
    punto.set_data([], [])
    plt.pause(0.05)


# -------------------------
# Recorrer caminos malos (aleatorios seleccionados)
# -------------------------
for i, camino in enumerate(caminos_malos):
    ax.set_title(f"Explorando caminos: intento {i+1}/{len(caminos_malos)} (long={len(camino)})")
    plt.pause(0.05)
    recorrer_y_animar(camino, color_actual="yellow", delay=0.16)
    # reiniciar agente en mundo a la posición de inicio_world (respawn simulado)
    agente.reiniciar()
    time.sleep(0.25)

# -------------------------
# Recorrer el camino correcto (si existe) — resaltar en verde y dejarlo
# -------------------------
if camino_final:
    # dibujar el camino correcto en verde (permanente)
    xs_f, zs_f = zip(*camino_final)
    ax.plot(xs_f, zs_f, color="green", linewidth=2.5, zorder=3, label="Camino correcto")
    plt.pause(0.05)
    # ahora animar el movimiento final con el punto y mover en mundo
    ax.set_title("Camino correcto (verde) — recorriendo")
    plt.pause(0.05)
    # animar but NOT remove the green line
    linea_final, = ax.plot(xs_f, zs_f, color="green", linewidth=2.5, zorder=3)
    for (mx, mz) in camino_final:
        punto.set_data([mx], [mz])
        wx, wy, wz = grid_a_mundo(mx, mz)
        agente.mc.player.setPos(wx, wy, wz)
        plt.pause(0.12)
    punto.set_data([], [])
    agente.mc.postToChat("✅ ¡El agente encontró la salida!")
else:
    ax.set_title("No se encontró camino correcto")
    agente.mc.postToChat("❌ No hay salida encontrada por BFS")

plt.pause(0.5)

# -------------------------
# Guardar métricas
# -------------------------
os.makedirs("../resultados", exist_ok=True)
csv_path = os.path.join("..", "resultados", "metricas.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Tipo", "ID", "Longitud", "ProfundidadMax", "Revisitas/Observaciones"])
    # escribir caminos malos (los que mostramos)
    for idx, c in enumerate(caminos_malos):
        writer.writerow(["malo", idx, len(c), len(c), 0])
    # camino final
    if camino_final:
        writer.writerow(["final", 0, len(camino_final), len(camino_final), 0])
    # métricas globales desde BFS (si las devolvió)
    writer.writerow([])
    writer.writerow(["Métricas globales"])
    if isinstance(metricas, dict):
        for k, v in metricas.items():
            writer.writerow([k, v])

# -------------------------
# Heatmap de exploración (frecuencia de visitas)
# -------------------------
visitas = np.zeros((N, N), dtype=int)
for camino in caminos_malos:
    for (mx, mz) in camino:
        visitas[mz, mx] += 1
if camino_final:
    for (mx, mz) in camino_final:
        visitas[mz, mx] += 1

plt.figure(figsize=(6,6))
plt.title("Mapa de calor de exploración")
img = plt.imshow(visitas, cmap="hot", origin="lower", extent=[-0.5, N-0.5, -0.5, N-0.5])
plt.colorbar(img, label="Número de visitas")
plt.scatter(grid_inicio[0], grid_inicio[1], c="green", marker="o", s=140)
plt.scatter(grid_salida[0], grid_salida[1], c="red", marker="*", s=180)
plt.savefig(os.path.join("..","resultados","heatmap.png"), dpi=200)
plt.show()

# Mantener ventana interactiva abierta un poco
time.sleep(1.0)
