import gym
import minerl
import logging

env = gym.make("MineRLObtainDiamondShovel-v0")

obs = env.reset()
done = False

while not done:
    action = env.action_space.noop()
    # Acción simple: atacar/usar, por ejemplo:
    action['attack'] = 1  # Golpear continuamente
    action['forward'] = 1  # Puede moverse hacia adelante
    # Puedes agregar lógica para girar o cambiar cámara si no detecta bloques cerca

    obs, reward, done, _ = env.step(action)
    env.render()

env.close()
