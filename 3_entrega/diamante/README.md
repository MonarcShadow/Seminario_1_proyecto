# Diamond Collection Agent - Stage 4

## Descripción General
Cuarta etapa del entrenamiento jerárquico. El agente busca **1 diamante** usando el pico de hierro obtenido en la etapa anterior.

## Inventario Inicial
El agente comienza con el inventario de un episodio exitoso de Stage 3:
- **Slot 0**: `diamond_axe` (1)
- **Slot 1**: `planks` (1)
- **Slot 2**: `stick` (2)
- **Slot 3**: `wooden_pickaxe` (1)
- **Slot 4**: `stone_pickaxe` (1)
- **Slot 5**: `iron_pickaxe` (1) ← **Herramienta principal**

## Objetivo
**Recolectar 1 diamante** usando el pico de hierro.

### Condiciones de Terminación
- ✅ **Éxito**: El agente recolecta 1 diamante
- ⏱️ **Timeout**: 120 segundos (2 minutos)

## Mundo/Entorno
- **Tipo**: Flat world con bloques dispersos
- **Dimensiones**: 21x21 (x: -10 a 10, z: -10 a 10)
- **Spawn**: (0.5, 4, 0.5)
- **Piso**: Obsidian (y=3, indestructible)
- **Paredes**: Obsidian perimetral (y=4 a y=6)
- **Bloques generados**:
  - **Diamond ore**: 3-5 bloques (MUY RARO) en y=4
  - **Iron ore**: 10-15 bloques en y=4-5
  - **Stone**: 15-20 bloques en y=4-5

## Características Técnicas

### Espacio de Estados
10 elementos:
1. `surroundings` (tuple): Grid 5x5x3 del entorno
2. `wood_count` (int): Cantidad de wood/log
3. `stone_count` (int): Cantidad de stone
4. `iron_count` (int): Cantidad de iron_ore/iron_ingot
5. `diamond_count` (int): Cantidad de diamond ← **NUEVO**
6. `planks_count` (int): Cantidad de planks
7. `sticks_count` (int): Cantidad de sticks
8. `has_wooden_pickaxe` (bool): Tiene pico de madera
9. `has_stone_pickaxe` (bool): Tiene pico de piedra
10. `has_iron_pickaxe` (bool): Tiene pico de hierro

### Espacio de Acciones
**12 acciones** (idénticas a todas las etapas para compatibilidad):
```python
actions = [
    "move 1", "move -1",           # 0, 1: Adelante/atrás
    "strafe 1", "strafe -1",       # 2, 3: Izquierda/derecha
    "turn 1", "turn -1",           # 4, 5: Girar
    "pitch 0.1", "pitch -0.1",     # 6, 7: Mirar arriba/abajo
    "attack 1",                    # 8: Atacar/minar
    "craft_wooden_pickaxe",        # 9: (No usado)
    "craft_stone_pickaxe",         # 10: (No usado)
    "craft_iron_pickaxe"           # 11: (No usado)
]
```

### Selección Automática de Herramientas
**Hardcoded** (no aprendido):
- `diamond_ore` → Selecciona `iron_pickaxe` automáticamente
- `iron_ore` → Selecciona `stone_pickaxe` automáticamente
- `stone` → Selecciona `wooden_pickaxe` automáticamente

### Sistema de Recompensas
```xml
<RewardForCollectingItem>
    <Item reward="500" type="log"/>
    <Item reward="1000" type="stone"/>
    <Item reward="5000" type="iron_ore"/>
    <Item reward="5000" type="iron_ingot"/>
    <Item reward="50000" type="diamond"/>  ← RECOMPENSA MASIVA
</RewardForCollectingItem>

<RewardForTouchingBlockType>
    <Block reward="-1" type="lava"/>
    <Block reward="-100" type="obsidian"/>
</RewardForTouchingBlockType>
```

## Transfer Learning
El agente carga por defecto el modelo entrenado de **Stage 3 (Iron)**:
```
../entrenamiento_acumulado/{algorithm}_iron_model.pkl
```

### Compatibilidad
- ✅ **Espacio de acciones idéntico**: 12 acciones
- ✅ **Q-table compatible**: Las dimensiones coinciden
- ✅ **Políticas transferibles**: Movimiento, exploración y minado se transfieren directamente

## Uso

### Entrenamiento Individual
```bash
cd diamante

# Con transfer learning (recomendado)
python diamond_agent.py --algorithm qlearning --episodes 50

# Desde cero (no recomendado)
python diamond_agent.py --algorithm qlearning --episodes 50 --load-model none

# Con puerto personalizado
python diamond_agent.py --algorithm sarsa --episodes 50 --port 10002
```

### Entrenamiento Paralelo (6 algoritmos simultáneos)
```bash
cd diamante
python run_parallel_experiments.py
```
**Puertos utilizados**: 10001-10006

### Análisis de Resultados
```bash
cd diamante
python analyze_results.py
```

## Archivos Generados

### Modelos
```
../entrenamiento_acumulado/
├── qlearning_diamond_model.pkl
├── sarsa_diamond_model.pkl
├── expected_sarsa_diamond_model.pkl
├── double_q_diamond_model.pkl
├── monte_carlo_diamond_model.pkl
└── random_diamond_model.pkl
```

### Métricas
```
metrics_data/
├── qlearning_DiamondAgent_{timestamp}.csv
├── qlearning_DiamondAgent_{timestamp}.png
└── ... (para cada algoritmo)
```

### Logs (modo paralelo)
```
resultados/
├── qlearning_diamond_log.txt
├── sarsa_diamond_log.txt
└── ... (para cada algoritmo)
```

## Pipeline Completo de Entrenamiento

### Secuencia de Transfer Learning
```
Stage 1 (Wood) → Stage 2 (Stone) → Stage 3 (Iron) → Stage 4 (Diamond) → Stage 5 (From Scratch)
     ↓                ↓                  ↓                  ↓                    ↓
wood_model.pkl → stone_model.pkl → iron_model.pkl → diamond_model.pkl → scratch_model.pkl
```

### Ejemplo de Ejecución Completa
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

# Stage 4: Diamond (carga iron_model.pkl) ← ESTA ETAPA
cd ../diamante
python diamond_agent.py --algorithm qlearning --episodes 50 \
    --load-model ../entrenamiento_acumulado/qlearning_iron_model.pkl

# Stage 5: From Scratch (carga diamond_model.pkl)
cd ../desde_cero
python from_scratch_agent.py --algorithm qlearning --episodes 50 \
    --load-model ../entrenamiento_acumulado/qlearning_diamond_model.pkl
```

## Métricas Recolectadas
- **total_reward**: Recompensa acumulada
- **steps**: Número de pasos por episodio
- **epsilon**: Valor de exploración (ε)
- **success**: Si se recolectó el diamante
- **diamond_collected**: Cantidad de diamante recolectado
- **max_diamond**: Máximo diamante en inventario
- **iron_collected**: Hierro recolectado (secundario)
- **max_iron**: Máximo hierro en inventario
- **action_distribution**: Distribución de acciones ejecutadas

## Diferencias con Stage 3
1. **Objetivo**: 1 diamond (vs 3 iron ore + craft)
2. **Rareza**: Diamond es MUY raro (3-5 bloques vs 20-30 iron)
3. **Herramienta**: Requiere iron_pickaxe (vs stone_pickaxe)
4. **Recompensa**: 50,000 puntos por diamond (vs 5,000 por iron)
5. **Sin crafting**: No necesita craftear nada (solo recolectar)
6. **Estado**: Agrega `diamond_count` (10 elementos vs 9)

## Siguiente Etapa
**Stage 5**: `from_scratch_agent.py` en carpeta `desde_cero/`
- Inicia con inventario vacío (solo diamond_axe)
- Debe completar TODAS las etapas: wood → stone → iron → diamond
- Usa transfer learning de diamond_model.pkl
