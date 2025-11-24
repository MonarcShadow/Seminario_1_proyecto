# Sistema de Aprendizaje Jerárquico con Transfer Learning - Minecraft

## Descripción General
Sistema completo de **aprendizaje por refuerzo jerárquico** en Minecraft usando **transfer learning**. El agente aprende a completar un tech tree complejo dividiéndolo en 5 etapas progresivas, donde cada etapa transfiere conocimiento a la siguiente.

## Estructura del Proyecto

```
3_entrega/
├── madera/              # Stage 1: Recolectar wood → Craftear wooden_pickaxe
├── piedra/              # Stage 2: Recolectar stone → Craftear stone_pickaxe
├── hierro/              # Stage 3: Recolectar iron → Craftear iron_pickaxe
├── diamante/            # Stage 4: Recolectar diamond (objetivo difícil)
├── desde_cero/          # Stage 5: Completar TODO el tech tree desde cero
├── entrenamiento_acumulado/  # Modelos .pkl compartidos entre etapas
└── TRANSFER_LEARNING_COMPATIBILITY.md  # Verificación de compatibilidad
```

## Pipeline de Transfer Learning

### Flujo de Conocimiento
```
Stage 1 (Wood)
    ↓ [wood_model.pkl]
Stage 2 (Stone)
    ↓ [stone_model.pkl]
Stage 3 (Iron)
    ↓ [iron_model.pkl]
Stage 4 (Diamond)
    ↓ [diamond_model.pkl]
Stage 5 (From Scratch)
```

### Detalles de Cada Etapa

| Stage | Carpeta | Inventario Inicial | Objetivo | Tiempo | Transfer From |
|-------|---------|-------------------|----------|--------|---------------|
| 1 | madera/ | Vacío | 3 wood → wooden_pickaxe | 120s | N/A (desde cero) |
| 2 | piedra/ | wooden_pickaxe + items | 3 stone → stone_pickaxe | 120s | Stage 1 |
| 3 | hierro/ | diamond_axe + pickaxes | 3 iron → iron_pickaxe | 120s | Stage 2 |
| 4 | diamante/ | diamond_axe + 3 pickaxes | 1 diamond | 120s | Stage 3 |
| 5 | desde_cero/ | diamond_axe (solo) | Completar TODO | 300s | Stage 4 |

## Algoritmos Implementados

Todos los stages soportan **6 algoritmos de RL**:
1. **Q-Learning**: Aprendizaje off-policy con Q-values
2. **SARSA**: Aprendizaje on-policy
3. **Expected SARSA**: SARSA con expectativa sobre acciones futuras
4. **Double Q-Learning**: Reduce sobreestimación de Q-values
5. **Monte Carlo**: Aprendizaje por episodios completos
6. **Random**: Baseline aleatorio (sin aprendizaje)

## Características Técnicas Clave

### Espacio de Acciones (12 acciones - ESTANDARIZADO)
```python
actions = [
    "move 1", "move -1",           # 0, 1: Movimiento
    "strafe 1", "strafe -1",       # 2, 3: Strafe
    "turn 1", "turn -1",           # 4, 5: Girar
    "pitch 0.1", "pitch -0.1",     # 6, 7: Mirar
    "attack 1",                    # 8: Atacar/Minar
    "craft_wooden_pickaxe",        # 9: Craft Stage 1
    "craft_stone_pickaxe",         # 10: Craft Stage 2
    "craft_iron_pickaxe"           # 11: Craft Stage 3
]
```

**Todas las etapas tienen el MISMO espacio de acciones** para garantizar compatibilidad de transfer learning.

### Espacio de Estados
- **Stages 1-3**: 9 elementos (surroundings + 8 valores)
- **Stages 4-5**: 10 elementos (+ diamond_count)

Componentes:
- `surroundings`: Grid 5x5x3 del entorno
- `wood_count`, `stone_count`, `iron_count`, `diamond_count`
- `planks_count`, `sticks_count`
- `has_wooden_pickaxe`, `has_stone_pickaxe`, `has_iron_pickaxe`

### Selección Automática de Herramientas
**Hardcoded** (no aprendido por el agente):
- `diamond_ore` → `iron_pickaxe`
- `iron_ore` → `stone_pickaxe`
- `stone` → `wooden_pickaxe`
- `log` → `diamond_axe` (bare hands)

### Crafting Jerárquico
Los agentes auto-craftean componentes necesarios:
- Wood → Planks → Sticks → Pickaxe
- Planks → Sticks (si faltan)

## Uso del Sistema

### 1. Entrenamiento Secuencial (Pipeline Completo)

```bash
# Stage 1: Wood (desde cero)
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

# Stage 5: From Scratch (carga diamond_model.pkl)
cd ../desde_cero
python from_scratch_agent.py --algorithm qlearning --episodes 50 \
    --load-model ../entrenamiento_acumulado/qlearning_diamond_model.pkl
```

### 2. Entrenamiento Paralelo (Por Stage)

Cada carpeta tiene `run_parallel_experiments.py`:

```bash
# Entrenar todos los algoritmos en paralelo
cd madera
python run_parallel_experiments.py  # 6 algoritmos simultáneos (puertos 10001-10006)

cd ../piedra
python run_parallel_experiments.py

cd ../hierro
python run_parallel_experiments.py

cd ../diamante
python run_parallel_experiments.py

cd ../desde_cero
python run_parallel_experiments.py
```

### 3. Análisis de Resultados

```bash
# En cualquier carpeta de stage
cd madera
python analyze_results.py  # Genera gráficos y estadísticas
```

## Archivos Generados

### Modelos (entrenamiento_acumulado/)
```
qlearning_model.pkl           # Stage 1 → Stage 2
qlearning_stone_model.pkl     # Stage 2 → Stage 3
qlearning_iron_model.pkl      # Stage 3 → Stage 4
qlearning_diamond_model.pkl   # Stage 4 → Stage 5
qlearning_scratch_model.pkl   # Stage 5 (output)
... (para cada algoritmo)
```

### Métricas (metrics_data/ en cada carpeta)
```
{algorithm}_{AgentName}_{timestamp}.csv   # Datos crudos
{algorithm}_{AgentName}_{timestamp}.png   # Gráficos
```

### Logs (resultados/ en cada carpeta, modo paralelo)
```
{algorithm}_log.txt           # Stage 1
{algorithm}_stone_log.txt     # Stage 2
{algorithm}_iron_log.txt      # Stage 3
{algorithm}_diamond_log.txt   # Stage 4
{algorithm}_scratch_log.txt   # Stage 5
```

## Métricas Recolectadas

Para cada episodio:
- `total_reward`: Recompensa acumulada
- `steps`: Pasos ejecutados
- `epsilon`: Valor de exploración (ε)
- `success`: Si completó el objetivo
- `wood_collected`, `stone_collected`, `iron_collected`, `diamond_collected`
- `max_wood`, `max_stone`, `max_iron`, `max_diamond`
- `action_distribution`: Distribución de acciones (move, turn, attack, craft)

## Verificación de Compatibilidad

Ver documento completo: [`TRANSFER_LEARNING_COMPATIBILITY.md`](./TRANSFER_LEARNING_COMPATIBILITY.md)

### Checklist de Compatibilidad
- ✅ **12 acciones idénticas** en todas las etapas
- ✅ **Q-tables transferibles** (diccionarios dinámicos)
- ✅ **Estados compatibles** (9-10 elementos)
- ✅ **Pipeline secuencial completo** (5 etapas)
- ✅ **Naming convention consistente** para modelos
- ✅ **Comandos de carga verificados**

## Experimentos Recomendados

### Experimento 1: Efectividad del Transfer Learning
```bash
# Con transfer learning
cd madera && python wood_agent.py --algorithm qlearning --episodes 50
cd ../piedra && python stone_agent.py --algorithm qlearning --episodes 50 --load-model ../entrenamiento_acumulado/qlearning_model.pkl

# Sin transfer learning
cd ../piedra && python stone_agent.py --algorithm qlearning --episodes 50
```

**Comparar**: Recompensa promedio, episodios hasta primer éxito, tasa de éxito final.

### Experimento 2: Comparación de Algoritmos
```bash
# Entrenar todos los algoritmos en paralelo
cd madera && python run_parallel_experiments.py
cd ../piedra && python run_parallel_experiments.py
# ... (continuar con todas las etapas)

# Analizar resultados
cd madera && python analyze_results.py
cd ../piedra && python analyze_results.py
# ...
```

**Comparar**: Q-Learning vs SARSA vs Expected SARSA vs Double Q vs Monte Carlo vs Random.

### Experimento 3: Pipeline Completo (From Scratch)
```bash
# Entrenar todo el pipeline secuencialmente
./train_full_pipeline.sh  # (crear script que ejecute todos los stages)

# Ejecutar Stage 5 con modelo cargado
cd desde_cero
python from_scratch_agent.py --algorithm qlearning --episodes 50 \
    --load-model ../entrenamiento_acumulado/qlearning_diamond_model.pkl
```

**Objetivo**: Verificar que un agente puede completar el tech tree completo desde casi cero.

## Requisitos del Sistema

### Software
- Python 3.8+
- Malmo (Minecraft Mod para RL)
- Minecraft Java Edition
- Dependencias Python: `pickle`, `numpy`, `matplotlib`, `pandas`

### Hardware
- **Mínimo**: 8 GB RAM, CPU quad-core
- **Recomendado**: 16 GB RAM, CPU octa-core (para experimentos paralelos)
- **GPU**: No requerida (RL tabular)

### Puertos Minecraft
- **Individual**: 10000 (default)
- **Paralelo**: 10001-10006 (6 instancias simultáneas)

## Troubleshooting

### Error: "MalmoPython no está instalado"
```bash
# Instalar Malmo
cd ~/MalmoPlatform
# Seguir instrucciones de instalación de Malmo
```

### Error: "No se encontró modelo"
```bash
# Verificar que el stage anterior generó el modelo
ls -lh entrenamiento_acumulado/
# Si no existe, entrenar el stage anterior primero
```

### Error: "Puerto ocupado"
```bash
# En modo paralelo, cambiar puertos
python run_parallel_experiments.py  # Usa 10001-10006 por defecto
# O ejecutar secuencialmente con run_experiment.py
```

### Agente no aprende / Recompensa muy negativa
- Verificar que Minecraft está corriendo
- Verificar semilla del entorno (usar `--seed 123456` para reproducibilidad)
- Aumentar número de episodios (`--episodes 100`)
- Verificar que el modelo pre-entrenado se cargó correctamente

## Estructura de Archivos Auxiliares

Cada carpeta de stage contiene:
- **{stage}_agent.py**: Agente principal
- **algorithms.py**: Implementación de algoritmos de RL
- **metrics.py**: Recolección y visualización de métricas
- **run_experiment.py**: Ejecuta todos los algoritmos secuencialmente
- **run_parallel_experiments.py**: Ejecuta todos los algoritmos en paralelo
- **analyze_results.py**: Análisis y gráficos de resultados
- **README.md**: Documentación específica del stage
- **resultados/**: Logs de ejecución (modo paralelo)

## Contribuciones

### Para agregar un nuevo algoritmo:
1. Implementar clase en `algorithms.py` heredando de `Agent`
2. Agregar al diccionario en `{stage}_agent.py`
3. Actualizar `run_experiment.py` y `run_parallel_experiments.py`

### Para agregar un nuevo stage:
1. Copiar estructura de carpeta de un stage existente
2. Modificar XML del mundo (generar_mundo_*_xml)
3. Ajustar inventario inicial
4. Definir objetivo y condición de éxito
5. Actualizar transfer learning path

## Referencias

- **Malmo**: https://github.com/microsoft/malmo
- **Q-Learning**: Watkins & Dayan (1992)
- **SARSA**: Rummery & Niranjan (1994)
- **Double Q-Learning**: van Hasselt (2010)
- **Transfer Learning**: Pan & Yang (2010)

## Autores
- Carlos (madera/, piedra/, hierro/, diamante/, desde_cero/)
- Jonathan (colaborador inicial)

## Licencia
MIT License - Ver archivo LICENSE

## Resumen Ejecutivo

Este proyecto demuestra **transfer learning jerárquico** en un entorno complejo (Minecraft):
- ✅ **5 etapas progresivas** con dificultad creciente
- ✅ **6 algoritmos de RL** implementados y comparables
- ✅ **100% compatible** para transfer learning (verificado)
- ✅ **Pipeline completo** desde Stage 1 hasta Stage 5
- ✅ **Documentación exhaustiva** con READMEs por stage
- ✅ **Experimentos reproducibles** con semillas fijas
- ✅ **Análisis automatizado** de resultados y métricas

El agente final (Stage 5) puede completar un tech tree complejo desde casi cero, demostrando la efectividad del aprendizaje jerárquico con transfer learning.
