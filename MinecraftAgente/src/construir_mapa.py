# construir_mapa.py

from mcpi.minecraft import Minecraft
from laberinto import laberinto, inicio, meta
import time

mc = Minecraft.create()

def construir_laberinto(base_x=None, base_y=None, base_z=None, wall_height=3):
    """
    Construye el laberinto en Minecraft. 
    Si base_x/base_y/base_z son None, usa la posición actual del jugador como referencia.
    Devuelve (BASE_X, BASE_Y, BASE_Z) usados.
    """
    # Tomar la posición del jugador si no se especifica base
    pos = mc.player.getTilePos()
    if base_x is None:
        base_x = pos.x + 2   # desplazar un poco delante del jugador
    if base_y is None:
        base_y = pos.y
    if base_z is None:
        base_z = pos.z + 2

    filas = len(laberinto)
    cols = len(laberinto[0])

    # Limpiar un área segura (un poco más grande)
    margin = 2
    mc.setBlocks(base_x - margin, base_y, base_z - margin,
                 base_x + cols + margin, base_y + wall_height + 2, base_z + filas + margin, 0)

    # Construir piso (césped) y muros
    for y in range(filas):
        for x in range(cols):
            world_x = base_x + x
            world_z = base_z + y
            # Piso
            mc.setBlock(world_x, base_y - 1, world_z, 2)  # césped (id 2)
            if laberinto[y][x] == 1:
                # muro de 'stone' (id 1) de wall_height
                for h in range(wall_height):
                    mc.setBlock(world_x, base_y + h, world_z, 1)
            else:
                # mantener espacio libre (aire)
                for h in range(wall_height):
                    mc.setBlock(world_x, base_y + h, world_z, 0)

    # Marcar entrada y salida con lana (verde y roja)
    sx, sy = inicio
    tx, ty = meta
    mc.setBlock(base_x + sx, base_y, base_z + sy, 35, 5)   # lana verde (entrada)
    mc.setBlock(base_x + tx, base_y, base_z + ty, 35, 14)  # lana roja (salida)

    mc.postToChat("Laberinto construido en ({},{},{})".format(base_x, base_y, base_z))
    time.sleep(0.5)
    return base_x, base_y, base_z
