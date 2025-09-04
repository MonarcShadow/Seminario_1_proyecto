# src/busqueda.py
from collections import deque

def bfs(inicio, objetivo, vecinos_fn):
    """
    inicio: (x, y, z)
    objetivo: (x, y, z)
    vecinos_fn: función que devuelve posiciones vecinas
    """
    visitados = set()
    cola = deque([(inicio, [inicio])])

    while cola:
        nodo, camino = cola.popleft()
        if nodo == objetivo:
            return camino
        if nodo in visitados:
            continue
        visitados.add(nodo)
        for vecino in vecinos_fn(nodo):
            if vecino not in visitados:
                cola.append((vecino, camino + [vecino]))
    return None
