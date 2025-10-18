# main_pc.py - Versión reducida para prueba de conceptos

from agente_pc import Agente
from busqueda_pc import buscar
from estrategia_simple_pc import EstrategiaSimple

def main():
    print("=== Prueba de Conceptos - Proyecto Seminario Minecraft ===")

    # Crear agente y estrategia
    agente = Agente()
    estrategia = EstrategiaSimple()

    # Ejecutar búsqueda simple
    resultado = buscar(agente, estrategia)

    print("Resultado final:", resultado)

if __name__ == "__main__":
    main()
