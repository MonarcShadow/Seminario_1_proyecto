# Guía Completa de Agentes - Transfer Learning Pipeline

## 🎯 Resumen del Sistema

El sistema implementa **transfer learning escalonado** donde cada agente aprende una tarea específica y transfiere su conocimiento al siguiente:

```
Madera → Piedra → Hierro → Diamante → Desde Cero (Completo)
```

---

## 📊 Stage 1: Wood Agent (Agente de Madera)

**Archivo**: `madera/wood_agent.py`

### Objetivo
Recolectar **3 logs** y craftear un **wooden pickaxe**

### Inventario Inicial
- Manos vacías (puede romper wood directamente)

### Condición de Término
- ✅ **Éxito**: Tiene `wooden_pickaxe` en inventario
- ⏱️ **Timeout**: 6000 pasos

### Modelo Guardado
- **Ubicación**: `entrenamiento_acumulado/{algorithm}_model.pkl`
- **Ejemplos**: `qlearning_model.pkl`, `sarsa_model.pkl`, etc.

### CSV Generado
- **Ubicación**: `madera/metrics_data/{algorithm}_WoodAgent_{timestamp}.csv`
- **Columnas**: Episode, Steps, WoodCollected, TotalReward, AvgReward, Epsilon, Actions

### Recompensas
- `+1000` por cada log recolectado
- `+10000` por craftear wooden pickaxe (éxito)
- `-100` por acción inútil (moverse sin propósito)

---

## 📊 Stage 2: Stone Agent (Agente de Piedra)

**Archivo**: `piedra/stone_agent.py`

### Objetivo
Recolectar **3 cobblestone** y craftear un **stone pickaxe**

### Inventario Inicial
- `wooden_pickaxe` (para minar cobblestone)
- `sticks` (necesarios para craftear)
- `planks` (para craftear sticks si se necesitan)

### Condición de Término
- ✅ **Éxito**: Tiene `stone_pickaxe` en inventario
- ⏱️ **Timeout**: 6000 pasos

### Modelo Cargado (Transfer Learning)
- **Desde**: `entrenamiento_acumulado/{algorithm}_model.pkl` (Stage 1)
- **Ejemplo**: Carga `qlearning_model.pkl` si el algoritmo es Q-Learning

### Modelo Guardado
- **Ubicación**: `entrenamiento_acumulado/{algorithm}_stone_model.pkl`
- **Contenido**: Q-table de Stage 1 + aprendizaje de Stage 2

### CSV Generado
- **Ubicación**: `piedra/metrics_data/{algorithm}_StoneAgent_{timestamp}.csv`

### Recompensas
- `+1000` por cada cobblestone recolectado
- `+10000` por craftear stone pickaxe (éxito)
- `-100` por acción inútil

---

## 📊 Stage 3: Iron Agent (Agente de Hierro)

**Archivo**: `hierro/iron_agent.py`

### Objetivo
Recolectar **3 iron ingots** y craftear un **iron pickaxe**

### Inventario Inicial
- `stone_pickaxe` (para minar iron_ore → iron_block)
- `sticks` (para craftear)
- `planks` (backup para sticks)

### Simplificación Implementada
- `iron_block` dropea `iron_ingot` directamente (sin necesidad de furnace)

### Condición de Término
- ✅ **Éxito**: Tiene `iron_pickaxe` en inventario
- ⏱️ **Timeout**: 6000 pasos

### Modelo Cargado (Transfer Learning)
- **Desde**: `entrenamiento_acumulado/{algorithm}_stone_model.pkl` (Stage 2)
- **Contenido**: Conocimiento acumulado de Stage 1 + Stage 2

### Modelo Guardado
- **Ubicación**: `entrenamiento_acumulado/{algorithm}_iron_model.pkl`
- **Contenido**: Q-table de Stage 1 + Stage 2 + Stage 3

### CSV Generado
- **Ubicación**: `hierro/metrics_data/{algorithm}_IronAgent_{timestamp}.csv`

### Recompensas
- `+1000` por cada iron_ingot recolectado
- `+10000` por craftear iron pickaxe (éxito)
- `-100` por acción inútil

---

## 📊 Stage 4: Diamond Agent (Agente de Diamante)

**Archivo**: `diamante/diamond_agent.py`

### Objetivo
Recolectar **diamantes** (cantidad no fija, maximizar)

### Inventario Inicial
- `iron_pickaxe` (necesario para minar diamond_ore)

### Condición de Término
- ✅ **Éxito**: Tiene al menos `1 diamond` en inventario
- ⏱️ **Timeout**: 6000 pasos

### Modelo Cargado (Transfer Learning)
- **Desde**: `entrenamiento_acumulado/{algorithm}_iron_model.pkl` (Stage 3)
- **Contenido**: Conocimiento acumulado de Stage 1 + Stage 2 + Stage 3

### Modelo Guardado
- **Ubicación**: `entrenamiento_acumulado/{algorithm}_diamond_model.pkl`
- **Contenido**: Q-table completa de todos los stages hasta aquí

### CSV Generado
- **Ubicación**: `diamante/metrics_data/{algorithm}_DiamondAgent_{timestamp}.csv`

### Recompensas
- `+1000` por cada diamond recolectado
- `+10000` si recolecta al menos 1 diamond (éxito)
- `-100` por acción inútil

---

## 📊 Stage 5: From Scratch Agent (Desde Cero - Completo)

**Archivo**: `desde_cero/from_scratch_agent.py`

### Objetivo Completo
Completar el **tech tree completo** desde cero:
1. Recolectar 3 wood → Craftear wooden pickaxe
2. Recolectar 3 cobblestone → Craftear stone pickaxe
3. Recolectar 3 iron → Craftear iron pickaxe
4. Recolectar diamantes

### Inventario Inicial
- `diamond_axe` (para optimizar recolección de wood)

### Condición de Término
- ✅ **Éxito**: Tiene `iron_pickaxe` Y al menos `1 diamond`
- ⏱️ **Timeout**: 6000 pasos

### Modelo Cargado (Transfer Learning)
- **Desde**: `entrenamiento_acumulado/{algorithm}_diamond_model.pkl` (Stage 4)
- **Contenido**: **TODO** el conocimiento acumulado de los 4 stages anteriores

### Modelo Guardado
- **Ubicación**: `entrenamiento_acumulado/{algorithm}_scratch_model.pkl`
- **Contenido**: **MODELO FINAL** - Q-table con todo el aprendizaje del pipeline

### CSV Generado
- **Ubicación**: `desde_cero/metrics_data/{algorithm}_FromScratchAgent_{timestamp}.csv`

### Recompensas
- `+1000` por cada material recolectado (wood, stone, iron, diamond)
- `+10000` por cada pickaxe crafteado
- `+50000` por completar todo el tech tree
- `-100` por acción inútil

---

## 🔄 Pipeline de Transfer Learning

### Flujo de Entrenamiento

```
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: WOOD                                              │
│  Entrena: 50 episodios                                      │
│  Guarda: qlearning_model.pkl                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: STONE                                             │
│  Carga: qlearning_model.pkl                                 │
│  Entrena: 50 episodios (continúa desde Stage 1)            │
│  Guarda: qlearning_stone_model.pkl                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: IRON                                              │
│  Carga: qlearning_stone_model.pkl                           │
│  Entrena: 50 episodios (continúa desde Stage 1+2)          │
│  Guarda: qlearning_iron_model.pkl                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 4: DIAMOND                                           │
│  Carga: qlearning_iron_model.pkl                            │
│  Entrena: 50 episodios (continúa desde Stage 1+2+3)        │
│  Guarda: qlearning_diamond_model.pkl                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 5: FROM SCRATCH (COMPLETO)                           │
│  Carga: qlearning_diamond_model.pkl                         │
│  Entrena: 50 episodios (todo el conocimiento acumulado)    │
│  Guarda: qlearning_scratch_model.pkl ← MODELO FINAL         │
└─────────────────────────────────────────────────────────────┘
```

### Comando de Entrenamiento

```bash
# Entrenar pipeline completo con transfer learning
python train_parallel_pipeline.py --episodes 50 --continuar si

# Entrenar solo stages 1-3
python train_parallel_pipeline.py --episodes 50 --inicio 1 --final 3

# Entrenar desde cero sin transfer learning
python train_parallel_pipeline.py --episodes 50 --continuar no
```

---

## 📁 Estructura de Archivos Generados

```
3_entrega/
├── entrenamiento_acumulado/
│   ├── qlearning_model.pkl              ← Stage 1
│   ├── qlearning_stone_model.pkl        ← Stage 1+2
│   ├── qlearning_iron_model.pkl         ← Stage 1+2+3
│   ├── qlearning_diamond_model.pkl      ← Stage 1+2+3+4
│   ├── qlearning_scratch_model.pkl      ← FINAL (todos los stages)
│   ├── sarsa_model.pkl
│   ├── sarsa_stone_model.pkl
│   └── ... (mismo patrón para cada algoritmo)
│
├── madera/
│   └── metrics_data/
│       ├── qlearning_WoodAgent_1763954849.csv
│       ├── qlearning_WoodAgent_1763954849.png
│       └── ... (6 algoritmos × 2 archivos)
│
├── piedra/
│   └── metrics_data/
│       ├── qlearning_StoneAgent_1763955000.csv
│       └── ... 
│
├── hierro/
│   └── metrics_data/
│       └── ...
│
├── diamante/
│   └── metrics_data/
│       └── ...
│
└── desde_cero/
    └── metrics_data/
        └── ...
```

---

## ⚙️ Parámetros de Configuración

### Todos los Agentes Comparten

```python
# Dimensiones del mundo
radio = 10  # Radio del área de generación

# Límites de pasos
max_steps = 6000

# Generación de bloques
wood: ~8-12 bloques
cobblestone: ~8-12 bloques  
iron_block: ~8-12 bloques
diamond_ore: ~8-12 bloques

# Seed fijo
env_seed = 123456  # Mismo layout de bloques en todos los episodios
```

### Algoritmos Soportados

1. **Q-Learning** - Puerto 10001
2. **SARSA** - Puerto 10002
3. **Expected SARSA** - Puerto 10003
4. **Double Q-Learning** - Puerto 10004
5. **Monte Carlo** - Puerto 10005
6. **Random** (baseline) - Puerto 10006

---

## 🐛 Troubleshooting

### Problema: "Modelo no existe"
**Causa**: El stage anterior no guardó el modelo
**Solución**: Ejecutar el stage anterior primero o usar `--continuar no`

### Problema: "Episode no termina"
**Causa**: El agente alcanzó max_steps sin completar objetivo
**Solución**: Normal en entrenamiento temprano, mejora con más episodios

### Problema: "CSV no se genera"
**Causa**: Error en MetricsLogger o permisos de escritura
**Solución**: Verificar que `metrics_data/` existe y tiene permisos

### Problema: "Puerto ocupado"
**Causa**: Minecraft no está corriendo en ese puerto
**Solución**: Abrir 6 clientes de Minecraft en puertos 10001-10006

---

## 📈 Interpretación de Resultados

### Métricas Clave

- **Steps**: Menor es mejor (más eficiente)
- **TotalReward**: Mayor es mejor
- **AvgReward**: Eficiencia por paso
- **Epsilon**: Disminuye con episodios (menos exploración)
- **Success**: Porcentaje de episodios exitosos

### Esperado con Transfer Learning

- Stage 2 debería completarse más rápido que Stage 1 entrenado desde cero
- Stage 3 más rápido que Stage 2
- Stage 4 y 5 se benefician de todo el conocimiento acumulado

---

## ✅ Checklist de Ejecución

Antes de entrenar:
- [ ] 6 clientes de Minecraft abiertos (puertos 10001-10006)
- [ ] Carpeta `entrenamiento_acumulado/` existe
- [ ] Carpetas `metrics_data/` en cada stage
- [ ] MALMO_DIR configurado correctamente

Durante entrenamiento:
- [ ] Verificar que CSV se va actualizando
- [ ] Verificar que .pkl se guarda después de cada episodio
- [ ] Monitorear que episodes terminan (no se quedan esperando)

Después de entrenar:
- [ ] Revisar CSV generados en cada `metrics_data/`
- [ ] Verificar PNG con gráficas
- [ ] Confirmar que modelos .pkl existen en `entrenamiento_acumulado/`
- [ ] Ejecutar `analyze_results.py` en cada carpeta para comparar algoritmos
