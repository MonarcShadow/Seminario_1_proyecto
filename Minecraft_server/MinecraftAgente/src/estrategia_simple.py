# src/estrategia_simple.py
def mover_linea(inicio, pasos=5):
    x, y, z = inicio
    return [(x+i, y, z) for i in range(1, pasos+1)]
