from collections import deque

def bfs_todos(laberinto, inicio, salida):
    """BFS que explora todo y retorna caminos fallidos + camino correcto + métricas"""
    queue = deque([[inicio]])
    visitados = set()
    caminos_fallidos = []
    camino_final = None
    nodos_expandidos = 0
    revisitas = 0
    profundidad_max = 0

    while queue:
        camino = queue.popleft()
        nodo = camino[-1]
        if nodo in visitados:
            revisitas += 1
            continue
        visitados.add(nodo)

        nodos_expandidos += 1
        profundidad_max = max(profundidad_max, len(camino))

        if nodo == salida:
            camino_final = camino
            continue  # seguimos para capturar más caminos

        # Expansión
        for vecino in vecinos(laberinto, nodo):
            nuevo_camino = list(camino)
            nuevo_camino.append(vecino)
            queue.append(nuevo_camino)

        caminos_fallidos.append(camino)

    metricas = {
        "nodos_expandidos": nodos_expandidos,
        "profundidad_max": profundidad_max,
        "revisitas": revisitas,
    }

    return caminos_fallidos, camino_final, metricas


def vecinos(laberinto, nodo):
    x, z = nodo
    movimientos = [(1,0), (-1,0), (0,1), (0,-1)]
    res = []
    for dx, dz in movimientos:
        nx, nz = x+dx, z+dz
        if (nx, nz) in laberinto and laberinto[(nx,nz)] == 0:  # 0 = camino
            res.append((nx, nz))
    return res
