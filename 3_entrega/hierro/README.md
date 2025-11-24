# Stage 3 - Iron Ore Collection Agent

## Objetivo
Recolectar **3 iron ore** → Craftear **iron pickaxe** (pico de hierro).

**Simplificación**: Los iron ore se convierten automáticamente en iron ingots al ser recolectados (no requiere fundición).

## Requisitos de Inicio
El agente comienza con el inventario de un episodio exitoso de Stage 2:
- 1x Diamond Axe (hotbar slot 0)
- 3x Planks (hotbar slots 1-3, oak)
- 1x Wooden Pickaxe (hotbar slot 4)
- 1x Stone Pickaxe (hotbar slot 5)

## Entorno
- **Dimensiones**: 21x21 (x: -10 a 10, z: -10 a 10)
- **Spawn**: (0.5, 4, 0.5)
- **Piso**: Obsidian (y=3, indestructible)
- **Paredes**: Obsidian perimetral (y=4 a y=6)
- **Iron Ore**: 20-30 bloques dispersos (y=4 y y=5)
- **Stone**: 10-15 bloques adicionales para variedad
- **Seed**: Generación determinística con seed=123456

## Sistema de Recompensas
- **+5000**: Por cada iron_ore/iron_ingot recolectado
- **+1000**: Por cada stone recolectado
- **+500**: Por cada log recolectado
- **+15000**: Por craftear iron pickaxe (éxito)
- **-1**: Por tocar lava
- **-100**: Por tocar obsidian
- **-300**: Por corrección automática de pitch (mirar arriba/abajo >10s)

## Espacio de Acciones (10 acciones)
```python
actions = [
    "move 1",              # Mover adelante
    "move -1",             # Mover atrás
    "strafe 1",            # Mover derecha
    "strafe -1",           # Mover izquierda
    "turn 1",              # Girar derecha
    "turn -1",             # Girar izquierda
    "pitch 0.1",           # Mirar arriba
    "pitch -0.1",          # Mirar abajo
    "attack 1",            # Atacar (minar)
    "craft_iron_pickaxe"   # Craftear pico de hierro (automático cuando hay 3+ iron)
]
```

## Representación de Estado
```python
state = (
    surroundings_tuple,    # Grid 5x5 de bloques cercanos
    wood_count,            # Cantidad de madera
    stone_count,           # Cantidad de piedra
    iron_count,            # Cantidad de hierro (ore + ingots)
    planks_count,          # Cantidad de planks
    sticks_count,          # Cantidad de sticks
    has_wooden_pickaxe,    # Bool
    has_stone_pickaxe,     # Bool
    has_iron_pickaxe       # Bool - Indica éxito
)
```

## Algoritmos Disponibles
1. **Q-Learning** - Temporal Difference con Q(s,a)
2. **SARSA** - On-policy TD control
3. **Expected SARSA** - Promedio de valores esperados
4. **Double Q-Learning** - Dos Q-tables para reducir sesgo
5. **Monte Carlo** - Aprendizaje episódico con retornos completos
6. **Random** - Baseline: acciones aleatorias

## Transfer Learning (Entrenamiento Jerárquico)
Este stage está diseñado para **continuar el entrenamiento** desde Stage 2:

### Uso con Modelos Pre-entrenados
```bash
# Cargar modelo de stone manualmente
python iron_agent.py --algorithm qlearning \
    --load-model ../entrenamiento_acumulado/qlearning_stone_model.pkl

# run_experiment.py y run_parallel_experiments.py cargan automáticamente
python run_experiment.py           # Carga stone models por defecto
python run_parallel_experiments.py  # Carga stone models por defecto
```

### Estructura de Modelos
```
entrenamiento_acumulado/
├── qlearning_model.pkl          # Stage 1 (wood)
├── qlearning_stone_model.pkl    # Stage 2 (stone)
├── qlearning_iron_model.pkl     # Stage 3 (iron) ← Generado aquí
├── sarsa_model.pkl
├── sarsa_stone_model.pkl
├── sarsa_iron_model.pkl
... (similar para cada algoritmo)
```

## Archivos del Proyecto

### Core
- **iron_agent.py**: Agente principal de recolección de hierro
- **algorithms.py**: Implementaciones de los 6 algoritmos RL
- **metrics.py**: Recolección y visualización de métricas

### Ejecución
- **run_experiment.py**: Ejecuta todos los algoritmos secuencialmente (1 puerto)
- **run_parallel_experiments.py**: Ejecuta 6 algoritmos en paralelo (puertos 10001-10006)

### Análisis
- **analyze_results.py**: Compara rendimiento de algoritmos
  - Iron Collected por episodio
  - Total Reward por episodio
  - Average Iron Collected (barras)
  - Success Rate (% episodios con 3+ iron)

## Uso

### Entrenamiento Individual
```bash
# Entrenamiento desde cero
python iron_agent.py --algorithm qlearning --episodes 50

# Con transfer learning desde stone
python iron_agent.py --algorithm qlearning --episodes 50 \
    --load-model ../entrenamiento_acumulado/qlearning_stone_model.pkl

# Con seed personalizada y puerto personalizado
python iron_agent.py --algorithm sarsa --episodes 100 \
    --env-seed 999999 --port 10005
```

### Experimentos Completos
```bash
# Secuencial (carga stone models automáticamente)
python run_experiment.py

# Paralelo (carga stone models automáticamente)
python run_parallel_experiments.py
```

### Análisis de Resultados
```bash
python analyze_results.py
```

Genera:
- `resultados/iron_algorithm_comparison.png`: Gráficos comparativos
- Resumen estadístico en consola

## Métricas Recolectadas
Cada algoritmo genera:
- **CSV**: `resultados/{algorithm}_iron_metrics.csv`
  - Episode, Steps, IronCollected, TotalReward, AvgReward
  - Epsilon, MoveActions, TurnActions, AttackActions

- **Gráficos individuales**: `resultados/{algorithm}_iron_metrics.png`
  - Iron Collection Progress
  - Reward per Episode
  - Exploration Rate (Epsilon)

- **Logs (paralelo)**: `resultados/{algorithm}_iron_log.txt`

## Configuración de Puertos
- **Entrenamiento individual**: Puerto 10000 (default)
- **Paralelo**: Puertos 10001-10006 (1 por algoritmo)

Asegúrate de tener 6 instancias de Minecraft corriendo:
```bash
# Terminal 1
./launchClient.sh -port 10001

# Terminal 2
./launchClient.sh -port 10002

# ... hasta 10006
```

## Lógica de Crafteo Jerárquica (Automática)

Similar a `wood_agent.py` y `stone_agent.py`, el agente implementa **crafteo jerárquico**:

### Proceso de Crafteo Iron Pickaxe
Cuando el agente tiene **3+ iron ore** y **stone pickaxe**:

**1. Verificar materiales necesarios**
- Iron pickaxe requiere: **3 iron ingots + 2 sticks**
- Verificar: `sticks_count >= 2`

**2. Craftear sticks si faltan** (automático)
- Si `sticks < 2`: 
  - Calcular: `sticks_needed = 2 - sticks`
  - Calcular: `planks_needed` (2 planks → 4 sticks)
  - Verificar: `planks_count >= planks_needed`
  - Ejecutar: `agent_host.sendCommand("craft stick")`
  - Actualizar inventario: `+4 sticks`, `-2 planks`

**3. Craftear iron pickaxe**
- Ejecutar: `agent_host.sendCommand("craft iron_pickaxe")`
- Verificar: Iron pickaxe en inventario
- Si éxito: **+15,000 puntos** → Episodio termina

Esta lógica garantiza que el agente **siempre pueda completar el crafteo** si tiene los recursos base (3 iron, stone pickaxe, 1+ planks).

## Condición de Éxito
El episodio termina exitosamente cuando:
- **Ha crafteado iron pickaxe** (3 iron + 2 sticks + stone pickaxe)
- El crafteo es **automático** y **jerárquico** cuando se tienen los materiales

Recompensa final: **+15000 puntos**

Tiempo límite: **120 segundos** (2 minutos)

## Limitaciones y Simplificaciones
1. **No requiere fundición**: Iron ore → Iron ingots automáticamente
2. **Auto-crafteo**: Cuando tiene 3+ iron + stone pickaxe, crafteará automáticamente iron pickaxe
3. **Tiempo límite**: 120 segundos por episodio
4. **Auto-reset de pitch**: Si el agente mira arriba/abajo >10s, se resetea automáticamente (penalización -300)
5. **Inventario pre-cargado**: Comienza con herramientas y materiales de Stage 2 exitoso

## Progresión de Stages
```
Stage 1 (Wood)  →  Stage 2 (Stone)  →  Stage 3 (Iron)
   ↓                    ↓                     ↓
wood_model.pkl → stone_model.pkl → iron_model.pkl
```

Cada stage puede cargar el modelo del anterior para **transfer learning**.

## Resultados Esperados
- **Algoritmos con memoria** (Q-Learning, SARSA, etc.): Deberían aprender a localizar y minar iron ore eficientemente
- **Random**: Baseline, recolección aleatoria
- **Con transfer learning**: Convergencia más rápida gracias a conocimiento previo de navegación y minado

## Troubleshooting
- **Error de conexión**: Verificar que Minecraft esté corriendo en el puerto correcto
- **No se genera .pkl**: Verificar que existe `../entrenamiento_acumulado/`
- **Modelo stone no encontrado**: Ejecutar primero Stage 2 o entrenar sin `--load-model`
