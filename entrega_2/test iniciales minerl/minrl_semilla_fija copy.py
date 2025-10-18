import gym
import minerl
import logging

# Esto hace que se vea información extra en la terminal
logging.basicConfig(level=logging.DEBUG)

# Creamos el entorno de MineRL
env = gym.make('MineRLBasaltFindCave-v0')

# Reiniciamos el entorno con semilla fija
obs = env.reset(seed=12345)  # <--- semilla fija

done = False

while not done:
    # Acción aleatoria
    action = env.action_space.sample()
    # Evitar que el agente cierre el episodio con ESC
    action["ESC"] = 0

    obs, reward, done, _ = env.step(action)
    env.render()

env.close()
