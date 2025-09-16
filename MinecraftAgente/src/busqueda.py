import time
import heapq
from collections import deque

# ---------------------
# BFS
# ---------------------
def bfs(laberinto, inicio, salida):
    start_time = time.time()
    queue = deque([(inicio, [inicio])])
    visitados = set([inicio])
    nodos_expandidos = 0
    profundidad_max = 0

    while queue:
        (x, z), camino = queue.popleft()
        nodos_expandidos += 1
        profundidad_max = max(profundidad_max, len(camino))

        if (x, z) == salida:
            return camino, {
                "nodos_expandidos": nodos_expandidos,
                "longitud": len(camino),
                "profundidad_max": profundidad_max,
                "tiempo": round(time.time() - start_time, 4),
                "optimo": "Sí"
            }

        for dx, dz in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, nz = x+dx, z+dz
            if (nx, nz) in laberinto and laberinto[(nx, nz)] == 0 and (nx, nz) not in visitados:
                visitados.add((nx, nz))
                queue.append(((nx, nz), camino + [(nx, nz)]))

    return None, {}

# ---------------------
# DFS
# ---------------------
def dfs(laberinto, inicio, salida):
    start_time = time.time()
    stack = [(inicio, [inicio])]
    visitados = set()
    nodos_expandidos = 0
    profundidad_max = 0

    while stack:
        (x, z), camino = stack.pop()
        nodos_expandidos += 1
        profundidad_max = max(profundidad_max, len(camino))

        if (x, z) == salida:
            return camino, {
                "nodos_expandidos": nodos_expandidos,
                "longitud": len(camino),
                "profundidad_max": profundidad_max,
                "tiempo": round(time.time() - start_time, 4),
                "optimo": "No"
            }

        if (x, z) not in visitados:
            visitados.add((x, z))
            for dx, dz in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, nz = x+dx, z+dz
                if (nx, nz) in laberinto and laberinto[(nx, nz)] == 0:
                    stack.append(((nx, nz), camino + [(nx, nz)]))

    return None, {}

# ---------------------
# Greedy Best-First
# ---------------------
def greedy(laberinto, inicio, salida):
    start_time = time.time()
    heap = [(heuristica(inicio, salida), inicio, [inicio])]
    visitados = set()
    nodos_expandidos = 0
    profundidad_max = 0

    while heap:
        _, (x, z), camino = heapq.heappop(heap)
        nodos_expandidos += 1
        profundidad_max = max(profundidad_max, len(camino))

        if (x, z) == salida:
            return camino, {
                "nodos_expandidos": nodos_expandidos,
                "longitud": len(camino),
                "profundidad_max": profundidad_max,
                "tiempo": round(time.time() - start_time, 4),
                "optimo": "No"
            }

        if (x, z) not in visitados:
            visitados.add((x, z))
            for dx, dz in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, nz = x+dx, z+dz
                if (nx, nz) in laberinto and laberinto[(nx, nz)] == 0:
                    heapq.heappush(heap, (heuristica((nx, nz), salida), (nx, nz), camino + [(nx, nz)]))

    return None, {}

# ---------------------
# A*
# ---------------------
def a_star(laberinto, inicio, salida):
    start_time = time.time()
    heap = [(heuristica(inicio, salida), 0, inicio, [inicio])]
    visitados = set()
    nodos_expandidos = 0
    profundidad_max = 0

    while heap:
        f, g, (x, z), camino = heapq.heappop(heap)
        nodos_expandidos += 1
        profundidad_max = max(profundidad_max, len(camino))

        if (x, z) == salida:
            return camino, {
                "nodos_expandidos": nodos_expandidos,
                "longitud": len(camino),
                "profundidad_max": profundidad_max,
                "tiempo": round(time.time() - start_time, 4),
                "optimo": "Sí"
            }

        if (x, z) not in visitados:
            visitados.add((x, z))
            for dx, dz in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, nz = x+dx, z+dz
                if (nx, nz) in laberinto and laberinto[(nx, nz)] == 0:
                    g2 = g + 1
                    f2 = g2 + heuristica((nx, nz), salida)
                    heapq.heappush(heap, (f2, g2, (nx, nz), camino + [(nx, nz)]))

    return None, {}

# ---------------------
# Heurística Manhattan
# ---------------------
def heuristica(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
