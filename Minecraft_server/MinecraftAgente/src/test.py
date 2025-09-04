from mcpi.minecraft import Minecraft

mc = Minecraft.create()  # Conecta al servidor (localhost:4711)
mc.postToChat("¡Hola desde Python!")
