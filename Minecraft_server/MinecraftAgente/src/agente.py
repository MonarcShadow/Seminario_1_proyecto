# src/agente.py
from mcpi.minecraft import Minecraft
import time

class Agente:
    def __init__(self, host="localhost", port=4711):
        self.mc = Minecraft.create(address=host, port=port)

    def decir(self, mensaje):
        self.mc.postToChat(f"[Agente] {mensaje}")

    def posicion(self):
        return self.mc.player.getTilePos()

    def mover_a(self, x, y, z):
        self.mc.player.setTilePos(x, y, z)

    def caminar_derecha(self, pasos=5, delay=0.5):
        x, y, z = self.posicion()
        for i in range(1, pasos+1):
            self.mover_a(x+i, y, z)
            time.sleep(delay)
