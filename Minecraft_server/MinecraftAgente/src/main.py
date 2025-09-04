# src/main.py
from agente import Agente
from estrategia_simple import mover_linea
import time

def main():
    agente = Agente()
    agente.decir("Iniciando misión...")

    x, y, z = agente.posicion()

    # Estrategia simple: moverse en línea recta
    camino = mover_linea((x, y, z), pasos=30)

    for pos in camino:
        agente.mover_a(*pos)
        time.sleep(1)

    agente.decir("¡He terminado de moverme!")

if __name__ == "__main__":
    main()
