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
        (1,3),(1, 11),(1,16),
        (2,3),(2,11),(2,16),
        (3,5),(3,6),(3,7),(3,8),(3,11),(3,16),(3,18),(3,19),(3,20),(3,21),(3,22),(3,23),
        (4,1),(4,2),(4,5),(4,6),(4,7),(4,8),(4,9),(4,11),(4,13),(4,14),(4,15),(4,16),(4,18),(4,19),(4,20),(4,21),(4,22),(4,23),
        (5,9),(5,11),(5,13),
        (6,9),(6,11),(6,13),
        (7,3),(7,9),(7,11),(7,13),(7,17),(7,18),(7,19),(7,20),
        (8,3),(8,9),(8,11),(8,13),(8,16),
        (9,3),(9,4),(9,5),(9,6),(9,7),(9,9),(9,11),(9,13),(9,17),(9,18),(9,19),(9,20),(9,21),(9,22),(9,23),
        (10,7),(10,9),(10,11),(10,13),(10,17),
        (11,7),(11,9),(11,13),(11,17),(11,21),
        (12,1),(12,2),(12,3),(12,4),(12,7),(12,9),(12,10),(12,11),(12,12),(12,13),(12,17),(12,18),(12,19),(12,20),(12,21),
        (13,7),(13,9),(13,15),(13,21),
        (14,9),(14,15),(14,21),
        (15,3),(15,4),(15,5),(15,6),(15,7),(15,8),(15,9),(15,12),(15,15),(15,21),
        (16,6),(16,15),(16,21),
        (17,6),(17,11),(17,12),(17,13),(17,14),(17,15),(17,16),(17,17),(17,18),(17,21),
        (18,1),(18,2),(18,3),(18,4),(18,6),(18,17),(18,21),
        (19,6),(19,7),(19,8),(19,9),(19,10),(19,11),(19,17),
        (20,2),(20,3),(20,4),(20,5),(20,6),(20,13),(20,14),(20,15),(20,16),(20,17),(20,18),(20,19),(20,20),(20,22),(20,23),
        (21,10),(21,16),(21,20),
        (22,1),(22,2),(22,3),(22,4),(22,7),(22,10),(22,13),(22,16),(22,17),(22,18),(22,20),
        (23,7),(23,10),(23,13),(23,20)
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




def generarlaberinto1(origen_x=0, origen_y=5, origen_z=0, tam=25):
    # Limpieza y construcción similar a la actual
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

    paredes = [
        # Muros ejemplo para laberinto 1
        (5,0), (5,1), (5,2), (5,3), (5,4),
        (10,5), (11,5), (12,5), (13,5),
        (15,10), (15,11), (15,12),
        (20,15), (20,16), (20,17), (20,18)
    ]
    # Construcción muros; usa el loop que tienes en la función
    for x, z in paredes:
        mc.setBlocks(origen_x+x, origen_y, origen_z+z, origen_x+x, origen_y+2, origen_z+z, 1)
    inicio = (origen_x + 1, origen_y, origen_z + 1)
    salida = (origen_x + tam - 1, origen_y, origen_z + tam - 1)
    mc.setBlock(inicio[0], inicio[1], inicio[2], 35, 5)  # lana verde
    mc.setBlock(salida[0], salida[1], salida[2], 35, 14)  # lana roja
    return inicio, salida

def generarlaberinto2(origen_x=0, origen_y=5, origen_z=0, tam=25):
    paredes = [
        # Distinta distribución de muros para laberinto 2
        (2,3), (3,3), (4,3), (5,3), (6,3),
        (7,10), (8,10), (9,10), (10,10),
        (15,5), (15,6), (15,7),
        (18,18), (19,18)
    ]
    for x, z in paredes:
        mc.setBlocks(origen_x+x, origen_y, origen_z+z, origen_x+x, origen_y+2, origen_z+z, 1)
    inicio = (origen_x + 1, origen_y, origen_z + 1)
    salida = (origen_x + tam - 5, origen_y, origen_z + tam - 2)
    mc.setBlock(inicio[0], inicio[1], inicio[2], 35, 5)
    mc.setBlock(salida[0], salida[1], salida[2], 35, 14)
    return inicio, salida

def generarlaberinto3(origen_x=0, origen_y=5, origen_z=0, tam=25):
    paredes = [
        # Otra distribución diferente para laberinto 3
        (1,10), (2,10), (3,10), (4,10), (5,10),
        (10,15), (11,15), (12,15),
        (14,20), (15,20), (16,20),
        (21,21), (22,21)
    ]
    for x, z in paredes:
        mc.setBlocks(origen_x+x, origen_y, origen_z+z, origen_x+x, origen_y+2, origen_z+z, 1)
    inicio = (origen_x + 1, origen_y, origen_z + 1)
    salida = (origen_x + 3, origen_y, origen_z + tam - 1)
    mc.setBlock(inicio[0], inicio[1], inicio[2], 35, 5)
    mc.setBlock(salida[0], salida[1], salida[2], 35, 14)
    return inicio, salida
