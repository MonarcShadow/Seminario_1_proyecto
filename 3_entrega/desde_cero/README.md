# From Scratch Agent - Stage 5 (Complete Pipeline)

## Descripción General
**Quinta y última etapa** del entrenamiento jerárquico. El agente demuestra que el transfer learning funciona completando **TODO EL TECH TREE** desde casi cero (solo diamond_axe inicial).

## Inventario Inicial
El agente comienza **CASI VACÍO**:
- **Slot 0**: `diamond_axe` (1) ← Solo para recolectar wood

**¡El agente debe obtener TODO lo demás!**

## Objetivo
Completar **TODAS las etapas del tech tree**:

### 🎯 Tech Tree Completo
1. **Stage 1**: Recolectar 3 wood → Craftear wooden_pickaxe
2. **Stage 2**: Recolectar 3 stone → Craftear stone_pickaxe
3. **Stage 3**: Recolectar 3 iron ore → Craftear iron_pickaxe
4. **Stage 4**: Recolectar 1 diamond ← **OBJETIVO FINAL**

### Condiciones de Terminación
- ✅ **Éxito**: El agente recolecta 1 diamante (completando todas las etapas previas)
- ⏱️ **Timeout**: 300 segundos (5 minutos) ← **MÁS TIEMPO** que otras etapas

## Mundo/Entorno
- **Tipo**: Flat world con TODOS los recursos
- **Dimensiones**: 21x21 (x: -10 a 10, z: -10 a 10)
- **Spawn**: (0.5, 4, 0.5)
- **Piso**: Obsidian (y=3, indestructible)
- **Paredes**: Obsidian perimetral (y=4 a y=6)
- **Bloques generados**:
  - **Diamond ore**: 3-5 bloques (MUY RARO) en y=4
  - **Iron ore**: ~20 bloques en y=4-5
  - **Stone**: ~25 bloques en y=4-5
  - **Wood (log)**: ~20 bloques en y=4-5

**Este es el mundo más completo con todos los recursos disponibles.**

## Características Técnicas

### Espacio de Estados
**10 elementos** (idéntico a diamond_agent):
1. `surroundings` (tuple): Grid 5x5x3 del entorno
2. `wood_count` (int): Cantidad de wood/log
3. `stone_count` (int): Cantidad de stone
4. `iron_count` (int): Cantidad de iron_ore/iron_ingot
5. `diamond_count` (int): Cantidad de diamond
6. `planks_count` (int): Cantidad de planks
7. `sticks_count` (int): Cantidad de sticks
8. `has_wooden_pickaxe` (bool): Tiene pico de madera
9. `has_stone_pickaxe` (bool): Tiene pico de piedra
10. `has_iron_pickaxe` (bool): Tiene pico de hierro

### Espacio de Acciones
**12 acciones** (idénticas a TODAS las etapas):
```python
actions = [
    "move 1", "move -1",           # 0, 1: Adelante/atrás
    "strafe 1", "strafe -1",       # 2, 3: Izquierda/derecha
    "turn 1", "turn -1",           # 4, 5: Girar
    "pitch 0.1", "pitch -0.1",     # 6, 7: Mirar arriba/abajo
    "attack 1",                    # 8: Atacar/minar
    "craft_wooden_pickaxe",        # 9: Stage 1 craft
    "craft_stone_pickaxe",         # 10: Stage 2 craft
    "craft_iron_pickaxe"           # 11: Stage 3 craft
]
```

**TODOS los craft actions se usan en este agente.**

### Selección Automática de Herramientas
**Hardcoded** (no aprendido) - Prioridad jerárquica:
- `diamond_ore` → Selecciona `iron_pickaxe`
- `iron_ore` → Selecciona `stone_pickaxe`
- `stone` → Selecciona `wooden_pickaxe`
- `log` → Selecciona `diamond_axe`

### Crafting Jerárquico
**Auto-crafting de componentes** (como wood_agent y iron_agent):

#### Wooden Pickaxe
```
Si wood >= 3:
  1. Craftear planks desde wood (1 wood = 4 planks)
  2. Craftear sticks desde planks (2 planks = 4 sticks)
  3. Craftear wooden_pickaxe (3 planks + 2 sticks)
```

#### Stone Pickaxe
```
Si stone >= 3 AND has_wooden_pickaxe:
  1. Craftear sticks si es necesario
  2. Craftear stone_pickaxe (3 stone + 2 sticks)
```

#### Iron Pickaxe
```
Si iron >= 3 AND has_stone_pickaxe:
  1. Craftear sticks si es necesario
  2. Craftear iron_pickaxe (3 iron + 2 sticks)
```

### Sistema de Recompensas
```xml
<RewardForCollectingItem>
    <Item reward="1000" type="log"/>
    <Item reward="2000" type="stone"/>
    <Item reward="5000" type="iron_ore"/>
    <Item reward="5000" type="iron_ingot"/>
    <Item reward="100000" type="diamond"/>  ← RECOMPENSA MASIVA
</RewardForCollectingItem>

<RewardForTouchingBlockType>
    <Block reward="-1" type="lava"/>
    <Block reward="-100" type="obsidian"/>
</RewardForTouchingBlockType>
```

**Nota**: Recompensa por diamond es 100,000 (el doble de Stage 4) debido a la complejidad.

## Transfer Learning
El agente carga por defecto el modelo entrenado de **Stage 4 (Diamond)**:
```
../entrenamiento_acumulado/{algorithm}_diamond_model.pkl
```

### Pipeline Completo de Transfer Learning
```
Stage 1 (Wood)     →  wood_model.pkl
      ↓
Stage 2 (Stone)    →  stone_model.pkl
      ↓
Stage 3 (Iron)     →  iron_model.pkl
      ↓
Stage 4 (Diamond)  →  diamond_model.pkl
      ↓
Stage 5 (Scratch)  →  scratch_model.pkl  ← ESTA ETAPA
```

### ¿Qué se transfiere?
- ✅ **Políticas de movimiento**: Exploración eficiente
- ✅ **Políticas de minado**: Atacar bloques correctamente
- ✅ **Políticas de navegación**: Evitar obstáculos
- ✅ **Políticas de crafting**: Preferencias de craft actions
- ✅ **Q-values**: Conocimiento acumulado de 4 etapas previas

## Uso

### Entrenamiento Individual
```bash
cd desde_cero

# Con transfer learning (RECOMENDADO)
python from_scratch_agent.py --algorithm qlearning --episodes 50

# Desde cero (NO RECOMENDADO - muy difícil)
python from_scratch_agent.py --algorithm qlearning --episodes 50 --load-model none

# Con puerto personalizado
python from_scratch_agent.py --algorithm sarsa --episodes 50 --port 10002
```

### Entrenamiento Paralelo (6 algoritmos simultáneos)
```bash
cd desde_cero
python run_parallel_experiments.py
```
**Puertos utilizados**: 10001-10006

**⚠️ ADVERTENCIA**: Este es el experimento más largo (5 minutos por episodio × 50 episodios × 6 algoritmos = ~25 horas si fueran secuenciales, ~4 horas en paralelo)

### Análisis de Resultados
```bash
cd desde_cero
python analyze_results.py
```

## Archivos Generados

### Modelos
```
../entrenamiento_acumulado/
├── qlearning_scratch_model.pkl
├── sarsa_scratch_model.pkl
├── expected_sarsa_scratch_model.pkl
├── double_q_scratch_model.pkl
├── monte_carlo_scratch_model.pkl
└── random_scratch_model.pkl
```

### Métricas
```
metrics_data/
├── qlearning_FromScratchAgent_{timestamp}.csv
├── qlearning_FromScratchAgent_{timestamp}.png
└── ... (para cada algoritmo)
```

### Logs (modo paralelo)
```
resultados/
├── qlearning_scratch_log.txt
├── sarsa_scratch_log.txt
└── ... (para cada algoritmo)
```

## Pipeline Completo de Entrenamiento

### Secuencia Completa (TODOS los 5 Stages)
```bash
# Stage 1: Wood (sin transfer learning)
cd madera
python wood_agent.py --algorithm qlearning --episodes 50

# Stage 2: Stone (carga wood_model.pkl)
cd ../piedra
python stone_agent.py --algorithm qlearning --episodes 50 \
    --load-model ../entrenamiento_acumulado/qlearning_model.pkl

# Stage 3: Iron (carga stone_model.pkl)
cd ../hierro
python iron_agent.py --algorithm qlearning --episodes 50 \
    --load-model ../entrenamiento_acumulado/qlearning_stone_model.pkl

# Stage 4: Diamond (carga iron_model.pkl)
cd ../diamante
python diamond_agent.py --algorithm qlearning --episodes 50 \
    --load-model ../entrenamiento_acumulado/qlearning_iron_model.pkl

# Stage 5: From Scratch (carga diamond_model.pkl) ← ESTA ETAPA
cd ../desde_cero
python from_scratch_agent.py --algorithm qlearning --episodes 50 \
    --load-model ../entrenamiento_acumulado/qlearning_diamond_model.pkl
```

## Métricas Recolectadas
- **total_reward**: Recompensa acumulada (puede ser MUY alta)
- **steps**: Número de pasos por episodio (hasta 15,000)
- **epsilon**: Valor de exploración (ε)
- **success**: Si se completó el tech tree (obtuvo diamond)
- **diamond_collected**: Cantidad de diamante recolectado (objetivo: 1)
- **max_diamond**: Máximo diamante en inventario
- **iron_collected**: Hierro recolectado
- **max_iron**: Máximo hierro en inventario
- **stone_collected**: Stone recolectado
- **max_stone**: Máximo stone en inventario
- **wood_collected**: Wood recolectado
- **max_wood**: Máximo wood en inventario
- **action_distribution**: Distribución de acciones ejecutadas

## Diferencias con Otros Stages

### vs Stage 4 (Diamond)
1. **Inventario inicial**: Solo diamond_axe (vs 6 items)
2. **Crafting**: Requiere 3 craft actions (vs 0)
3. **Etapas**: Debe completar 4 sub-objetivos (vs 1)
4. **Tiempo**: 300 segundos (vs 120)
5. **Recursos**: Todos los recursos presentes (vs solo diamond/iron/stone)
6. **Complejidad**: MÁXIMA - requiere secuencia completa

### vs Stage 1 (Wood)
1. **Objetivo**: Diamond (vs wooden_pickaxe)
2. **Profundidad**: 4 etapas (vs 1)
3. **Transfer learning**: Carga diamond_model (vs entrenar desde cero)
4. **Recompensa**: 100,000 por diamond (vs objetivo implícito)

## Desafíos Técnicos
1. **Largo horizonte temporal**: Hasta 15,000 pasos por episodio
2. **Sparse rewards**: Recompensas espaciadas (wood → stone → iron → diamond)
3. **Dependencias secuenciales**: No puedes minar diamond sin iron_pickaxe
4. **Espacio de estados grande**: Combinación de todos los recursos
5. **Decisiones multi-etapa**: Requiere planificación a largo plazo

## Verificación de Transfer Learning

### Prueba de Eficacia
Para verificar que el transfer learning funciona:

```bash
# 1. Entrenar CON transfer learning
python from_scratch_agent.py --algorithm qlearning --episodes 50 \
    --load-model ../entrenamiento_acumulado/qlearning_diamond_model.pkl

# 2. Entrenar SIN transfer learning
python from_scratch_agent.py --algorithm qlearning --episodes 50

# 3. Comparar métricas:
#    - Episodios hasta primer éxito
#    - Recompensa promedio
#    - Tasa de éxito
```

**Expectativa**: El agente con transfer learning debería:
- ✅ Lograr el primer éxito más rápido
- ✅ Tener mayor recompensa promedio
- ✅ Mayor tasa de éxito final

## Interpretación de Resultados

### Éxito Parcial
El agente puede tener éxito parcial:
- ✅ Crafted wooden_pickaxe (Stage 1 completo)
- ✅ Crafted stone_pickaxe (Stage 2 completo)
- ❌ No crafted iron_pickaxe (Stage 3 incompleto)
- ❌ No diamond (Stage 4 incompleto)

### Éxito Completo
```
Wood: 3+ → Wooden Pick ✓ → Stone: 3+ → Stone Pick ✓ → 
Iron: 3+ → Iron Pick ✓ → Diamond: 1 ✓
```

## Conclusión
**Stage 5** es la demostración final de que el aprendizaje jerárquico funciona. Un agente que comienza casi vacío puede completar un tech tree complejo gracias al conocimiento transferido de las 4 etapas anteriores.

Este es el **test definitivo** del sistema de transfer learning implementado.
