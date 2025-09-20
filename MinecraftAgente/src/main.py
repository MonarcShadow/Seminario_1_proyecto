import os
import time
import matplotlib.pyplot as plt
import csv
import numpy as np

from agente import Agente
from laberinto import generar_laberinto
from laberinto import generarlaberinto1
from laberinto import generarlaberinto2
from laberinto import generarlaberinto3
from busqueda import bfs, dfs, greedy, a_star

#definir muros del laberinto

paredes1=[
        # Muros ejemplo para laberinto 1
        (1,3),(1, 11),(1,16),
        (2,3),(2,11),(2,16),
        (3,5),(3,6),(3,7),(3,8),(3,11),(3,16),(3,18),(3,19),(3,20),(3,21),(3,22),(3,23),
        (4,1),(4,2),(4,5),(4,6),(4,7),(4,8),(4,9),(4,11),(4,13),(4,14),(4,15),(4,16),(4,18),(4,19),(4,20),(4,21),(4,22),(4,23),
        (5,9),(5,11),(5,13),
        (6,9),(6,11),(6,13),
        (7,3),(7,9),(7,11),(7,13),(7,17),(7,18),(7,19),(7,20),
        (8,3),(8,9),(8,11),(8,13),(8,16),
        (9,3),(9,4),(9,5),(9,6),(9,7),(9,9),(9,11),(9,13),(9,17),(9,18),(9,19),(9,20),(9,21),(9,22),(9,23),
        (10,7),(10,9),(10,11),(10,13),(10,17),
        (11,7),(11,9),(11,13),(11,17),(11,21),
        (12,1),(12,2),(12,3),(12,4),(12,7),(12,9),(12,10),(12,11),(12,12),(12,13),(12,17),(12,18),(12,19),(12,20),(12,21),
        (13,7),(13,9),(13,15),(13,21),
        (14,9),(14,15),(14,21),
        (15,3),(15,4),(15,5),(15,6),(15,7),(15,8),(15,9),(15,12),(15,15),(15,21),
        (16,6),(16,15),(16,21),
        (17,6),(17,11),(17,12),(17,13),(17,14),(17,15),(17,16),(17,17),(17,18),(17,21),
        (18,1),(18,2),(18,3),(18,4),(18,6),(18,17),(18,21),
        (19,6),(19,7),(19,8),(19,9),(19,10),(19,11),(19,17),
        (20,2),(20,3),(20,4),(20,5),(20,6),(20,13),(20,14),(20,15),(20,16),(20,17),(20,18),(20,19),(20,20),(20,22),(20,23),
        (21,10),(21,16),(21,20),
        (22,1),(22,2),(22,3),(22,4),(22,7),(22,10),(22,13),(22,16),(22,17),(22,18),(22,20),
        (23,7),(23,10),(23,13),(23,20)
    ]
paredes2=[
        # Muros ejemplo para laberinto 2
        (1,3),(1, 11),(1,16),
        (2,3),(2,11),(2,16),
        (3,5),(3,6),(3,7),(3,8),(3,11),(3,16),(3,18),(3,19),(3,20),(3,21),(3,22),(3,23),
        (4,1),(4,2),(4,5),(4,6),(4,7),(4,8),(4,9),(4,11),(4,13),(4,14),(4,15),(4,16),(4,18),(4,19),(4,20),(4,21),(4,22),(4,23),
        (5,9),(5,11),(5,13),
        (6,9),(6,11),(6,13),
        (7,3),(7,9),(7,11),(7,13),(7,17),(7,18),(7,19),(7,20),
        (8,3),(8,9),(8,11),(8,13),(8,16),
        (9,3),(9,4),(9,5),(9,6),(9,7),(9,9),(9,11),(9,13),(9,17),(9,18),(9,19),(9,20),(9,21),(9,22),(9,23),
        (10,7),(10,9),(10,11),(10,13),(10,17),
        
    ]
paredes3=[
        # Muros ejemplo para laberinto 3
        (14,9),(14,15),(14,21),
        (15,3),(15,4),(15,5),(15,6),(15,7),(15,8),(15,9),(15,12),(15,15),(15,21),
        (16,6),(16,15),(16,21),
        (17,6),(17,11),(17,12),(17,13),(17,14),(17,15),(17,16),(17,17),(17,18),(17,21),
        (18,1),(18,2),(18,3),(18,4),(18,6),(18,17),(18,21),
        (19,6),(19,7),(19,8),(19,9),(19,10),(19,11),(19,17),
        (20,2),(20,3),(20,4),(20,5),(20,6),(20,13),(20,14),(20,15),(20,16),(20,17),(20,18),(20,19),(20,20),(20,22),(20,23),
        (21,10),(21,16),(21,20),
        (22,1),(22,2),(22,3),(22,4),(22,7),(22,10),(22,13),(22,16),(22,17),(22,18),(22,20),
        (23,7),(23,10),(23,13),(23,20)
    ]
paredes_laberinto=[paredes1,paredes2,paredes3]
for i in range(len(paredes_laberinto)):
    # -------------------------
    # Generar laberinto en Minecraft
    # -------------------------
    inicio_world, salida_world = generar_laberinto(paredes=paredes_laberinto[i],laberinto_num=i)
    base_x = inicio_world[0] - 1
    base_y = inicio_world[1]
    base_z = inicio_world[2] - 1

    # Coordenadas en grilla
    N = 25
    
    if i==0:
        grid_inicio = (1, 1)
        grid_salida = (23, 23)
    elif i==1:
        grid_inicio = (1, 1)
        grid_salida = (12, 12)
    else:
        grid_inicio = (1, 1)
        grid_salida = (1, 23)

    # Construir laberinto (0 = libre, 1 = muro)
    laberinto = {(x, z): 0 for x in range(N) for z in range(N)}
    paredes_internas = paredes_laberinto[i]
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

