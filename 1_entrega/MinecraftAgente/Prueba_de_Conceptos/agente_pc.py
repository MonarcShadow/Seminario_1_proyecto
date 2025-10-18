# agente_pc.py - Versión reducida para prueba de conceptos

class Agente:
    def __init__(self):
        self.posicion = (0, 0)  # simulamos coordenadas en 2D
        print("[Agente] Inicializado en posición", self.posicion)

    def mover(self, direccion):
        x, y = self.posicion
        if direccion == "arriba":
            y += 1
        elif direccion == "abajo":
            y -= 1
        elif direccion == "derecha":
            x += 1
        elif direccion == "izquierda":
            x -= 1
        self.posicion = (x, y)
        print(f"[Agente] Movido {direccion}, nueva posición: {self.posicion}")
        return self.posicion
