# Entrega 4: Algoritmos de RL Modernos con Deep Learning y Curriculum Learning

## 📋 Cambios Principales respecto a Entrega 3

### 1. **Algoritmos Modernos (2015-2023)**
- ✅ **PPO (Proximal Policy Optimization, 2017)** - Estado del arte en RL
- ✅ **TRPO (Trust Region Policy Optimization, 2015)** - Predecesor de PPO, optimización con restricción de confianza
- ✅ **DQN (Deep Q-Network, 2015)** - Q-Learning con redes neuronales profundas
- ✅ **A2C (Advantage Actor-Critic, 2016)** - Método actor-crítico asíncrono
- ❌ ~~Q-Learning tabular (1989)~~ - Obsoleto
- ❌ ~~SARSA tabular (1994)~~ - Obsoleto
- ❌ ~~Monte Carlo (1940s-1950s)~~ - Demasiado antiguo

### 2. **Deep Learning Integration**
- **Redes Neuronales Profundas**: Todos los algoritmos usan PyTorch/TensorFlow
- **Feature Extraction**: CNN para procesar observaciones visuales
- **Arquitecturas modernas**: MLP para estados, CNN para imágenes
- **Librerías confiables**: Stable-Baselines3 (implementación verificada y optimizada)

### 3. **Curriculum Learning - Progresión de Herramientas**
Entrenamiento progresivo en 4 etapas con **transfer learning** (cada stage usa el modelo pre-entrenado del anterior):

#### **Stage 1: Madera (~500 episodios)**
- **Objetivo**: Recolectar 3 madera → Craftear `wooden_pickaxe`
- **Arena**: 10×10 con alta densidad de árboles (40-60 logs)
- **Inventario inicial**: planks + sticks (para crafteo)
- **Propósito**: Aprender movimiento, ataque, y concepto de recolección
- **Success threshold**: 60% (avanza cuando alcanza este %)

#### **Stage 2: Piedra (~500 episodios)**
- **Objetivo**: Recolectar 3 stone → Craftear `stone_pickaxe`
- **Arena**: 10×10 con alta densidad de piedra (30-40 stone)
- **Inventario inicial**: `wooden_pickaxe` + materiales para crafting
- **Pre-requisito**: Tener wooden_pickaxe para craftear
- **Success threshold**: 55%
- **Transfer learning**: Carga modelo entrenado de Stage 1

#### **Stage 3: Hierro (~600 episodios)**
- **Objetivo**: Recolectar 3 iron_ore → Craftear `iron_pickaxe`
- **Arena**: 10×10 con alta densidad de hierro (20-30 iron_ore)
- **Inventario inicial**: `stone_pickaxe` + materiales
- **Pre-requisito**: Tener stone_pickaxe para craftear
- **Success threshold**: 50% (más difícil)
- **Transfer learning**: Carga modelo entrenado de Stage 2

#### **Stage 4: Diamante (~800 episodios)**
- **Objetivo**: Recolectar 1 diamond → Craftear `diamond_pickaxe`
- **Arena**: 10×10 con baja densidad de diamantes (3-6 diamond_ore)
- **Inventario inicial**: `iron_pickaxe` + materiales
- **Pre-requisito**: Tener iron_pickaxe para craftear
- **Success threshold**: 45% (muy difícil)
- **Transfer learning**: Carga modelo entrenado de Stage 3

**Características clave**:
- ✅ **Auto-crafteo**: Cuando alcanza materiales requeridos, craftea automáticamente
- ✅ **Pitch auto-reset**: Si mira arriba/abajo >10s → reset a 0° con penalización -300
- ✅ **Rewards escalados**: Aumentan con dificultad de stage (500→1000→1500→2000)
- ✅ **SimpleCraftCommands**: XML configurado para crafteo automático de herramientas
- ✅ **Detección de éxito**: Episodio termina al craftear la herramienta objetivo

### 4. **Arquitectura de Redes Neuronales**

#### **PPO, TRPO & A2C (Actor-Critic)**
```
Actor Network:
  Input: Observation (state vector)
  → Dense(64, ReLU)
  → Dense(64, ReLU)
  → Output: Action probabilities (softmax)

Critic Network:
  Input: Observation
  → Dense(64, ReLU)
  → Dense(64, ReLU)
  → Output: Value estimate (scalar)
```

#### **DQN (Q-Network)**
```
Q-Network:
  Input: Observation
  → Dense(128, ReLU)
  → Dense(128, ReLU)
  → Dense(64, ReLU)
  → Output: Q-values para cada acción
```

### 5. **Justificación Técnica**

#### **¿Por qué PPO?**
- **Paper**: "Proximal Policy Optimization Algorithms" (Schulman et al., 2017)
- **Ventajas**: 
  - Estable y robusto
  - No requiere ajuste fino de hiperparámetros
  - Estado del arte en robótica y juegos
- **Uso real**: OpenAI Five (Dota 2), OpenAI Rubik's Cube

#### **¿Por qué TRPO?**
- **Paper**: "Trust Region Policy Optimization" (Schulman et al., 2015)
- **Ventajas**:
  - Garantías teóricas de mejora monótona
  - Restricción de región de confianza (KL divergence)
  - Predecesor directo de PPO
  - Más estable que métodos vanilla policy gradient
- **Uso real**: Robótica de alta precisión, tareas de manipulación

#### **¿Qué modelo de Deep Learning usa?**
- **Optimizador**: Adam (learning rate: 3e-4)
- **Arquitectura**: Multi-Layer Perceptron (MLP) con 2 capas ocultas
- **Función de activación**: ReLU
- **Normalización**: Layer Normalization
- **Regularización**: Gradient clipping (0.5)

#### **¿Cómo se entrena la Q en DQN?**
```python
# Red neuronal aproxima Q(s,a)
Q_predicted = q_network(state)[action]

# Target usando red objetivo (frozen)
Q_target = reward + gamma * max(target_network(next_state))

# Loss: Mean Squared Error
loss = MSE(Q_predicted, Q_target)

# Backpropagation con Adam optimizer
optimizer.zero_grad()
loss.backward()
optimizer.step()

# Actualizar target network cada N pasos
if steps % target_update_freq == 0:
    target_network.load_state_dict(q_network.state_dict())
```

## 📁 Estructura del Proyecto

```
4_entrega/
├── README.md                          # Este archivo
├── requirements.txt                   # Dependencias (Stable-Baselines3, PyTorch, etc.)
├── setup.sh                          # Script de instalación
│
├── src/
│   ├── malmo_env_wrapper.py          # Wrapper Gym para Malmo
│   ├── curriculum_manager.py         # Gestor de curriculum learning
│   ├── feature_extractor.py          # Extracción de características
│   ├── custom_policies.py            # Políticas personalizadas para SB3
│   └── utils.py                      # Utilidades
│
├── configs/
│   ├── ppo_config.yaml               # Configuración PPO
│   ├── trpo_config.yaml              # Configuración TRPO
│   ├── dqn_config.yaml               # Configuración DQN
│   ├── a2c_config.yaml               # Configuración A2C
│   └── curriculum_stages.yaml        # Definición de etapas
│
├── train_ppo.py                      # Script de entrenamiento PPO
├── train_trpo.py                     # Script de entrenamiento TRPO
├── train_dqn.py                      # Script de entrenamiento DQN
├── train_a2c.py                      # Script de entrenamiento A2C
├── train_curriculum.py               # Script con curriculum learning
│
├── evaluate.py                       # Evaluación de modelos
├── compare_algorithms.py             # Comparación entre algoritmos
├── visualize_training.py             # Visualización de métricas
│
├── models/                           # Modelos entrenados guardados
├── logs/                            # TensorBoard logs
└── results/                         # Resultados y gráficos
```

## 🚀 Instalación

### Requisitos
- Python 3.8+
- PyTorch 1.10+
- CUDA (opcional, para GPU)

### Setup
```bash
cd 4_entrega
pip install -r requirements.txt
```

## 💻 Uso

### Opción A: Experimento Completo Automatizado (Recomendado) 🚀

El script `run_full_experiment` entrena todos los algoritmos en paralelo, evalúa y compara automáticamente.

#### **Windows (PowerShell)**
```powershell
# Testing rápido (50 episodios, ~1-2 horas)
.\run_full_experiment.ps1 -Mode fast

# Producción completa (3000 episodios, ~24-48 horas)
.\run_full_experiment.ps1 -Mode full
```

#### **Linux/WSL (Bash)**
```bash
# Testing rápido
chmod +x run_full_experiment.sh
./run_full_experiment.sh fast

# Producción completa
./run_full_experiment.sh full
```

**El script hace todo automáticamente:**
1. ✅ Entrena PPO, TRPO, DQN, A2C en **paralelo** (puertos distintos: 10000, 10003, 10001, 10002)
2. ✅ Espera a que todos terminen
3. ✅ Evalúa cada modelo en los 4 stages
4. ✅ Genera comparación con gráficos
5. ✅ Guarda todo en `results/experiment_TIMESTAMP/`

**Output generado:**
```
results/experiment_TIMESTAMP/
  ├── ppo_evaluation.json
  ├── trpo_evaluation.json
  ├── dqn_evaluation.json
  ├── a2c_evaluation.json
  ├── comparison_results_*.json
  └── algorithm_comparison_*.png  (gráfico comparativo)

logs/experiment_TIMESTAMP/
  ├── ppo_training.log
  ├── trpo_training.log
  ├── dqn_training.log
  ├── a2c_training.log
  └── comparison.log
```

---

### Opción B: Entrenamiento Manual Individual

### 1. Entrenamiento con PPO (Recomendado)
```bash
# Testing rápido (30 episodios por stage, avanza con 30% completado)
python train_ppo.py --episodes 50 --curriculum

# Producción (cambiar episodes_per_stage a 500 en curriculum_manager.py)
python train_ppo.py --episodes 5000 --curriculum
```

### 2. Entrenamiento con TRPO
```bash
# Testing rápido
python train_trpo.py --episodes 50 --curriculum

# Producción
python train_trpo.py --episodes 5000 --curriculum
```

### 3. Entrenamiento con DQN
```bash
# Testing rápido
python train_dqn.py --episodes 50 --curriculum

# Producción
python train_dqn.py --episodes 5000 --curriculum
```

### 4. Entrenamiento con A2C
```bash
# Testing rápido
python train_a2c.py --episodes 50 --curriculum

# Producción
python train_a2c.py --episodes 5000 --curriculum
```

### 5. Evaluación
```bash
# Evaluar un modelo en un stage específico
python evaluate.py --algorithm ppo --model models/ppo_curriculum_*_final.zip --stage 1 --episodes 10

# Evaluar en todos los stages
python evaluate.py --algorithm ppo --model models/ppo_curriculum_*_final.zip --episodes 10
```

### 6. Comparación de Algoritmos
```bash
# Comparar PPO, TRPO, DQN y A2C en todos los stages
python compare_algorithms.py \
  --models models/ppo_curriculum_*_final.zip models/trpo_curriculum_*_final.zip models/dqn_curriculum_*_final.zip models/a2c_curriculum_*_final.zip \
  --algorithms ppo trpo dqn a2c \
  --episodes 10 \
  --stages 1 2 3 4
```

**Nota**: Por defecto, el curriculum usa 30 episodios por stage para testing rápido. Para entrenamiento completo, editar `src/curriculum_manager.py` y cambiar `episodes_per_stage` de 30 a 500-800.

## 📊 Métricas y Evaluación

### Métricas Registradas
- **Reward por episodio**: Recompensa acumulada
- **Success rate**: % episodios con objetivo cumplido
- **Episode length**: Pasos por episodio
- **Loss**: Pérdida de la red neuronal
- **Learning rate**: Tasa de aprendizaje adaptativa
- **Entropy**: Exploración vs explotación
- **Value loss**: Error en estimación de valor (A2C/PPO)
- **Policy loss**: Error en política (A2C/PPO)

### Visualización
```bash
# TensorBoard
tensorboard --logdir logs/

# Gráficos personalizados
python visualize_training.py --log_dir logs/PPO_1
```

## 🔬 Fundamento Teórico

### PPO (Proximal Policy Optimization)
- **Paper**: [Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
- **Tipo**: Policy Gradient con restricción de confianza
- **Ventaja**: Estable, sample-efficient, fácil de ajustar

### TRPO (Trust Region Policy Optimization)
- **Paper**: [Schulman et al., 2015](https://arxiv.org/abs/1502.05477)
- **Tipo**: Policy Gradient con región de confianza (KL divergence)
- **Ventaja**: Garantías teóricas de mejora monótona, más estable que vanilla policy gradient

### DQN (Deep Q-Network)
- **Paper**: [Mnih et al., 2015](https://www.nature.com/articles/nature14236)
- **Tipo**: Value-based con replay buffer y target network
- **Ventaja**: Aprende directamente de píxeles

### A2C (Advantage Actor-Critic)
- **Paper**: [Mnih et al., 2016](https://arxiv.org/abs/1602.01783)
- **Tipo**: Actor-Critic con ventaja normalizada
- **Ventaja**: Balancea exploración/explotación

### Curriculum Learning
- **Paper**: [Bengio et al., 2009](https://ronan.collobert.com/pub/matos/2009_curriculum_icml.pdf)
- **Implementación**: Progresión de herramientas (madera → piedra → hierro → diamante)
- **Característica**: Cada stage usa modelo pre-entrenado del anterior
- **Lógica**: Auto-crafteo al alcanzar materiales, pitch auto-reset con penalización -300

## 📚 Referencias

1. **Stable-Baselines3**: https://stable-baselines3.readthedocs.io/
2. **OpenAI Spinning Up**: https://spinningup.openai.com/
3. **PyTorch RL Tutorials**: https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
4. **Malmo Platform**: https://github.com/microsoft/malmo

