# Entrenamiento Jerárquico de RL - Sistema de 3 Stages

## Resumen del Sistema
Este proyecto implementa un sistema de **entrenamiento jerárquico** de Reinforcement Learning para Minecraft, dividido en 3 stages progresivos:

```
Stage 1 (Wood) → Stage 2 (Stone) → Stage 3 (Iron)
     ↓                ↓                  ↓
wood_model.pkl → stone_model.pkl → iron_model.pkl
```

Cada stage puede cargar los modelos pre-entrenados del stage anterior para **transfer learning**, acelerando el aprendizaje.

---

## Estructura de Carpetas

```
3_entrega/
├── madera/                    # Stage 1 - Wood Collection
│   ├── wood_agent.py         # Recolectar 3 wood → craft wooden pickaxe
│   ├── algorithms.py
│   ├── metrics.py
│   ├── analyze_results.py
│   ├── run_experiment.py
│   ├── run_parallel_experiments.py
│   └── resultados/
│
├── piedra/                    # Stage 2 - Stone Collection
│   ├── stone_agent.py        # Recolectar 3 stone → craft stone pickaxe
│   ├── algorithms.py
│   ├── metrics.py
│   ├── analyze_results.py
│   ├── run_experiment.py     # Carga wood models por defecto
│   ├── run_parallel_experiments.py
│   └── resultados/
│
├── hierro/                    # Stage 3 - Iron Collection
│   ├── iron_agent.py         # Recolectar 3 iron ore con stone pickaxe
│   ├── algorithms.py
│   ├── metrics.py
│   ├── analyze_results.py
│   ├── run_experiment.py     # Carga stone models por defecto
│   ├── run_parallel_experiments.py
│   └── resultados/
│
└── entrenamiento_acumulado/   # Modelos centralizados
    ├── qlearning_model.pkl           # Stage 1
    ├── qlearning_stone_model.pkl     # Stage 2
    ├── qlearning_iron_model.pkl      # Stage 3
    ├── sarsa_model.pkl
    ├── sarsa_stone_model.pkl
    ├── sarsa_iron_model.pkl
    ├── ... (similar para cada algoritmo)
    └── README.md
```

---

## Stages y Objetivos

### Stage 1: Wood Collection (madera/)
**Objetivo**: Recolectar 3 wood → Craftear wooden pickaxe

**Agente**: `wood_agent.py`
- Inventario inicial: Vacío
- Acción especial: `craft_wooden_pickaxe`
- Recompensa éxito: +10,000
- Modelo generado: `{algorithm}_model.pkl`
- **Entrenamiento**: Desde cero

**Comando**:
```bash
cd madera
python run_experiment.py  # Secuencial, entrena desde cero
```

---

### Stage 2: Stone Collection (piedra/)
**Objetivo**: Recolectar 3 stone → Craftear stone pickaxe

**Agente**: `stone_agent.py`
- Inventario inicial: wooden_pickaxe, sticks, planks (episodio exitoso Stage 1)
- Acción especial: `craft_stone_pickaxe`
- Recompensa éxito: +10,000
- Modelo generado: `{algorithm}_stone_model.pkl`
- **Transfer Learning**: Carga `{algorithm}_model.pkl` por defecto

**Comando**:
```bash
cd piedra
python run_experiment.py  # Carga wood models automáticamente
```

---

### Stage 3: Iron Pickaxe Crafting (hierro/)
**Objetivo**: Recolectar 3 iron ore → Craftear iron pickaxe

**Agente**: `iron_agent.py`
- Inventario inicial: diamond_axe, 3 planks, wooden_pickaxe, stone_pickaxe (episodio exitoso Stage 2)
- Acción especial: `craft_iron_pickaxe` (auto-crafteo jerárquico)
- **Crafteo jerárquico**: Si faltan sticks, los craftea automáticamente desde planks (2 planks → 4 sticks)
- Recompensa éxito: +15,000
- Modelo generado: `{algorithm}_iron_model.pkl`
- **Transfer Learning**: Carga `{algorithm}_stone_model.pkl` por defecto
- **Simplificación**: Iron ore → Iron ingots automáticamente

**Comando**:
```bash
cd hierro
python run_experiment.py  # Carga stone models automáticamente
```

---

## Algoritmos Disponibles
Todos los stages incluyen 6 algoritmos:

1. **Q-Learning** - Temporal Difference con Q(s,a)
2. **SARSA** - On-policy TD control
3. **Expected SARSA** - Promedio de valores esperados
4. **Double Q-Learning** - Dos Q-tables para reducir sesgo
5. **Monte Carlo** - Aprendizaje episódico
6. **Random** - Baseline aleatorio

---

## Ejecución de Experimentos

### 1. Entrenamiento Secuencial (Stage por Stage)
```bash
# Stage 1 (desde cero)
cd madera
python run_experiment.py

# Stage 2 (carga wood models)
cd ../piedra
python run_experiment.py

# Stage 3 (carga stone models)
cd ../hierro
python run_experiment.py
```

### 2. Entrenamiento Paralelo (6 algoritmos simultáneos)
```bash
# Stage 1
cd madera
python run_parallel_experiments.py  # Puertos 10001-10006

# Stage 2
cd ../piedra
python run_parallel_experiments.py  # Puertos 10001-10006, carga wood models

# Stage 3
cd ../hierro
python run_parallel_experiments.py  # Puertos 10001-10006, carga stone models
```

**Requisito**: 6 instancias de Minecraft corriendo:
```bash
./launchClient.sh -port 10001
./launchClient.sh -port 10002
./launchClient.sh -port 10003
./launchClient.sh -port 10004
./launchClient.sh -port 10005
./launchClient.sh -port 10006
```

### 3. Entrenamiento Individual con Opciones
```bash
# Entrenar un algoritmo específico con transfer learning
cd hierro
python iron_agent.py --algorithm qlearning --episodes 100 \
    --load-model ../entrenamiento_acumulado/qlearning_stone_model.pkl

# Entrenar sin transfer learning (desde cero)
python iron_agent.py --algorithm sarsa --episodes 50

# Con seed y puerto personalizados
python iron_agent.py --algorithm double_q --episodes 75 \
    --env-seed 999999 --port 10005
```

---

## Transfer Learning - Carga Automática

### Stage 1 (madera/)
- **Carga**: Ninguno (entrena desde cero)
- **Genera**: `{algorithm}_model.pkl`

### Stage 2 (piedra/)
- **Carga**: `{algorithm}_model.pkl` (automático en run scripts)
- **Genera**: `{algorithm}_stone_model.pkl`

### Stage 3 (hierro/)
- **Carga**: `{algorithm}_stone_model.pkl` (automático en run scripts)
- **Genera**: `{algorithm}_iron_model.pkl`

**Nota**: Si no existe el modelo previo, entrena desde cero.

---

## Análisis de Resultados

Cada stage incluye `analyze_results.py` que genera:

1. **Gráficos comparativos** entre algoritmos
2. **Estadísticas**:
   - Recurso promedio recolectado
   - Success rate (%)
   - Reward promedio
   - Máximo recolectado

```bash
cd madera
python analyze_results.py  # → madera/resultados/wood_algorithm_comparison.png

cd ../piedra
python analyze_results.py  # → piedra/resultados/stone_algorithm_comparison.png

cd ../hierro
python analyze_results.py  # → hierro/resultados/iron_algorithm_comparison.png
```

---

## Métricas por Episodio

Cada algoritmo genera:

- **CSV**: `resultados/{algorithm}_{stage}_metrics.csv`
  - Episode, Steps, ResourceCollected, TotalReward, AvgReward
  - Epsilon, MoveActions, TurnActions, AttackActions

- **Gráficos individuales**: `resultados/{algorithm}_{stage}_metrics.png`
  - Resource Collection Progress
  - Reward per Episode
  - Exploration Rate (Epsilon)

---

## Configuración de Hiperparámetros

### QLearningAgent
```python
learning_rate = 0.1
discount_factor = 0.99
epsilon = 1.0
epsilon_decay = 0.995
epsilon_min = 0.01
```

### SarsaAgent
```python
learning_rate = 0.1
discount_factor = 0.99
epsilon = 1.0
epsilon_decay = 0.995
epsilon_min = 0.01
```

### ExpectedSarsaAgent
```python
learning_rate = 0.1
discount_factor = 0.99
epsilon = 1.0
epsilon_decay = 0.995
epsilon_min = 0.01
```

### DoubleQAgent
```python
learning_rate = 0.1
discount_factor = 0.99
epsilon = 1.0
epsilon_decay = 0.995
epsilon_min = 0.01
```

### MonteCarloAgent
```python
discount_factor = 0.99
epsilon = 1.0
epsilon_decay = 0.995
epsilon_min = 0.01
```

### RandomAgent
```python
# Sin parámetros de aprendizaje
# Selecciona acciones aleatoriamente
```

---

## Sistema de Recompensas

### Todas las Stages
- **-1**: Por tocar lava
- **-100**: Por tocar obsidian
- **-300**: Por corrección automática de pitch (mirar arriba/abajo >10s)

### Stage 1 (Wood)
- **+1000**: Por cada log recolectado
- **+10000**: Por craftear wooden pickaxe (éxito)

### Stage 2 (Stone)
- **+1000**: Por cada log
- **+2000**: Por cada stone
- **+5000**: Por cada iron_ore
- **+10000**: Por craftear stone pickaxe (éxito)

### Stage 3 (Iron)
- **+500**: Por cada log
- **+1000**: Por cada stone
- **+5000**: Por cada iron_ore/iron_ingot
- **+15000**: Por craftear iron pickaxe (éxito)

---

## Ventajas del Sistema Jerárquico

1. **Transfer Learning**: Cada stage aprovecha el conocimiento del anterior
2. **Convergencia más rápida**: Los agentes ya saben navegar y minar
3. **Modularidad**: Cada stage es independiente y reutilizable
4. **Escalabilidad**: Fácil agregar nuevos stages
5. **Debugging**: Problemas aislados por stage

---

## Troubleshooting

### Error: "MalmoPython no está instalado"
```bash
# Instalar Malmo
cd ~/MalmoPlatform
./launchClient.sh
```

### Error: "Connection refused"
- Verificar que Minecraft esté corriendo en el puerto correcto
- Para paralelo, asegurarse de tener 6 instancias

### Error: "Modelo no encontrado"
- Ejecutar primero el stage anterior
- O entrenar sin `--load-model`

### Los agentes no aprenden
- Verificar hiperparámetros (epsilon_decay, learning_rate)
- Aumentar número de episodios
- Revisar sistema de recompensas

---

## Próximos Pasos

### Stage 4 (Propuesto): Diamond Collection
- Recolectar 3 diamonds con iron pickaxe
- Requiere navegar a nivel Y < 16
- Mayor complejidad de navegación

### Mejoras Posibles
1. **Deep Q-Networks (DQN)**: Redes neuronales para estados complejos
2. **Prioritized Experience Replay**: Mejorar muestreo de experiencias
3. **Curriculum Learning**: Ajustar dificultad progresivamente
4. **Multi-task Learning**: Entrenar en múltiples stages simultáneamente

---

## Referencias
- **Project Malmo**: https://github.com/microsoft/malmo
- **Minecraft Wiki**: https://minecraft.fandom.com/
- **Reinforcement Learning**: Sutton & Barto (2018)
