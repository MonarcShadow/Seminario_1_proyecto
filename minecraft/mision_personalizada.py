import gym
import os
# Para la versión 0.4.4, la clase MineRLEnv está en este submódulo específico.
from minerl.env.minerl_env import MineRLEnv

# ¡IMPORTANTE! Reemplaza 'NOMBRE_DE_TU_MUNDO'
MINECRAFT_WORLD_NAME = 'laberinto' # <--- ASEGÚRATE DE CAMBIAR ESTO

MISSION_XML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mi_mision.xml')

# --- MÉTODO CORRECTO PARA MINERL v0.4.4 ---

# 1. Lee el contenido del archivo de misión XML
with open(MISSION_XML_PATH, 'r') as f:
    mission_xml = f.read()

# 2. Registra la misión usando el método de clase de MineRLEnv
#    Esta era la forma de hacerlo en las versiones 0.x
MineRLEnv.register_mission(
    'MiEntornoPersonalizado-v0',
    mission_xml,
    world_name=MINECRAFT_WORLD_NAME,
    force_reset=True
)

# 3. Crea el entorno usando gym.make() con el ID que registramos
env = gym.make('MiEntornoPersonalizado-v0')

# --- FIN DEL MÉTODO CORRECTO ---

if __name__ == '__main__':
    print("¡Entorno para MineRL v0.4.4 creado exitosamente!")
    print("Iniciando simulación...")

    obs = env.reset()
    done = False
    
    for i in range(1000):
        action = env.action_space.noop()
        action['forward'] = 1
        action['camera'] = [0, 2]

        obs, reward, done, info = env.step(action)
        env.render()
        if done:
            break
            
    print("Simulación finalizada.")
    env.close()