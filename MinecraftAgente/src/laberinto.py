from mcpi.minecraft import Minecraft

mc = Minecraft.create()

def generar_laberinto(origen_x=0, origen_y=5, origen_z=0, tam=25):
    """Genera un laberinto fijo de 25x25 con paredes y caminos"""
    # Limpieza del área
    mc.setBlocks(origen_x-2, origen_y, origen_z-2,
                 origen_x+tam+2, origen_y+5, origen_z+tam+2, 0)

    # Paredes exteriores
    mc.setBlocks(origen_x, origen_y, origen_z,
                 origen_x+tam, origen_y+3, origen_z, 1)  # muro norte
    mc.setBlocks(origen_x, origen_y, origen_z+tam,
                 origen_x+tam, origen_y+3, origen_z+tam, 1)  # muro sur
    mc.setBlocks(origen_x, origen_y, origen_z,
                 origen_x, origen_y+3, origen_z+tam, 1)  # muro oeste
    mc.setBlocks(origen_x+tam, origen_y, origen_z,
                 origen_x+tam, origen_y+3, origen_z+tam, 1)  # muro este

    # Suelo plano
    mc.setBlocks(origen_x, origen_y-1, origen_z,
                 origen_x+tam, origen_y-1, origen_z+tam, 2)

    # Laberinto interno fijo (paredes)
    paredes = [
        (5, 0), (5, 1), (5, 2), (5, 3), (5, 4),
        (10, 5), (11, 5), (12, 5), (13, 5),
        (15, 10), (15, 11), (15, 12),
        (20, 15), (20, 16), (20, 17), (20, 18),
    ]

    for (x, z) in paredes:
        mc.setBlocks(origen_x+x, origen_y, origen_z+z,
                     origen_x+x, origen_y+2, origen_z+z, 1)

    # Posición de inicio y salida
    inicio = (origen_x+1, origen_y, origen_z+1)
    salida = (origen_x+tam-1, origen_y, origen_z+tam-1)

    mc.setBlock(inicio[0], inicio[1], inicio[2], 35, 5)  # lana verde
    mc.setBlock(salida[0], salida[1], salida[2], 35, 14) # lana roja

    return inicio, salida
