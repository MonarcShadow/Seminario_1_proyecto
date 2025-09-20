# busqueda_pc.py - Versión reducida para prueba de conceptos

def buscar(agente, estrategia):
    print("[Búsqueda] Iniciando búsqueda con estrategia simple...")

    pasos = ["arriba", "derecha", "derecha", "abajo"]
    for paso in pasos:
        agente.mover(paso)

    print("[Búsqueda] Finalizada")
    return agente.posicion
