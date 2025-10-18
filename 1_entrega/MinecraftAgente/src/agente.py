import time
from mcpi.minecraft import Minecraft

mc = Minecraft.create()

class Agente:
    def __init__(self, inicio):
        self.mc = mc
        self.inicio = inicio

    def mover_camino(self, camino):
        """Recorre un camino en Minecraft paso a paso"""
        for (x, z) in camino:
            self.mc.player.setTilePos(x, self.inicio[1], z)
            time.sleep(0.3)

    def reiniciar(self):
        self.mc.postToChat("💀 Reiniciando...")
        time.sleep(1)
        self.mc.player.setTilePos(self.inicio[0], self.inicio[1], self.inicio[2])
