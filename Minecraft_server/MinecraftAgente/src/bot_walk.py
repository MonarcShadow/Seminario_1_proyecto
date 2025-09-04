from mcpi.minecraft import Minecraft
import time

def caminar(mc, x, y, z, dx, dz, pasos, delay=0.3):
    """
    Mueve al jugador paso a paso en la dirección indicada.
    dx, dz: incrementos en X y Z
    pasos: cantidad de bloques a mover
    delay: tiempo entre pasos
    """
    for _ in range(pasos):
        x += dx
        z += dz
        mc.player.setTilePos(x, y, z)
        time.sleep(delay)
    return x, y, z

def main():
    # Conectarse al servidor
    mc = Minecraft.create()

    # Obtener la posición inicial del jugador
    pos = mc.player.getTilePos()
    x, y, z = pos.x, pos.y, pos.z

    # Mensaje en el chat
    mc.postToChat("El bot empieza a caminar...")

    # Caminar 10 bloques hacia adelante (+Z)
    x, y, z = caminar(mc, x, y, z, dx=0, dz=1, pasos=100)

    # Caminar 5 bloques a la derecha (+X)
    x, y, z = caminar(mc, x, y, z, dx=1, dz=0, pasos=50)

    # Mensaje de fin
    mc.postToChat("El bot terminó su caminata 🚶‍♂️")

if __name__ == "__main__":
    main()
