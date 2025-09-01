import gym
import minerl
import logging
import time

logging.basicConfig(level=logging.INFO)

# Crea el entorno
env = gym.make('MineRLBasaltFindCave-v0')

# Reinicia el entorno
obs = env.reset()

# Caminar hacia adelante por 200 pasos
for step in range(200):
    action = env.action_space.noop()  # acción "vacía"
    action["forward"] = 1             # caminar hacia adelante
    action["jump"] = 0
    action["attack"] = 0
    action["ESC"] = 0                 # evita terminar episodio
    
    obs, reward, done, info = env.step(action)
    env.render()

    # puedes dormir un poco para ver mejor el movimiento
    time.sleep(0.05)

    if done:
        print("El episodio terminó antes de lo esperado.")
        break

env.close()
