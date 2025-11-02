# 📋 Resumen Técnico - Sistema de Recolección de Madera

## 🎯 Objetivo del Sistema

Entrenar un agente de aprendizaje por refuerzo (Q-Learning) para **recolectar 3 bloques de madera** picando árboles en Minecraft usando Project Malmo.

---

## 🔑 Diferencias Clave con el Sistema de Búsqueda de Agua

| Característica | Sistema Agua (Jonathan) | Sistema Madera (Carlos) |
|---------------|------------------------|-------------------------|
| **Objetivo** | Tocar agua | Picar y recolectar 3 maderas |
| **Acciones** | 4 (move, turn×2, jumpmove) | 7 (+attack, strafe×2) |
| **Estado** | 6 dimensiones | 7 dimensiones |
| **Grid** | 5×3×5 (75 bloques) | 5×5×5 (125 bloques) |
| **Inventario** | No usado | ✓ Tracking activo |
| **Raycast** | Básico | ✓ Detección de distancia |
| **Recompensa máxima** | +100 (tocar agua) | +500 (3 maderas) |
| **Criterio éxito** | RewardForTouchingBlock | Inventario ≥ 3 |
| **Tiempo límite** | 60 seg | 120 seg |
| **Epsilon inicial** | 0.3 | 0.4 |

---

## 🧠 Arquitectura del Estado

### Estado del Agente (7 dimensiones)

```python
estado = (
    orientacion,        # int [0-3]: Norte, Este, Sur, Oeste
    nivel_madera,       # int [0-2]: Cantidad de madera visible
    nivel_inventario,   # int [0-3]: Maderas en inventario (0, 1, 2, 3+)
    mirando_madera,     # bool [0-1]: ¿Mira directamente a madera?
    dist_categoria,     # int [0-2]: Distancia al bloque (cerca/medio/lejos)
    obstaculo_frente,   # bool [0-1]: ¿Hay obstáculo?
    indicador_hojas     # int [0-2]: Nivel de hojas (señal de árbol)
)
```

**Tamaño del espacio de estados**: 4 × 3 × 4 × 2 × 3 × 2 × 3 = **864 estados posibles**

---

## ⚙️ Acciones Disponibles

```python
ACCIONES = {
    0: "move 1",        # Avanzar 1 bloque
    1: "turn 1",        # Girar derecha 90°
    2: "turn -1",       # Girar izquierda 90°
    3: "jumpmove 1",    # Saltar + avanzar
    4: "attack 1",      # 🆕 Picar/Atacar (mantener)
    5: "strafe 1",      # 🆕 Moverse lateral derecha
    6: "strafe -1",     # 🆕 Moverse lateral izquierda
}
```

### Nueva acción clave: `attack 1`
- **Duración**: 0.6 segundos (tiempo de picado)
- **Uso**: Romper bloques de madera
- **Recompensa condicionada**: +30 si mira madera, -5 si no

---

## 💰 Sistema de Recompensas

### Recompensas Positivas

| Evento | Valor | Trigger |
|--------|-------|---------|
| 🏆 **Completar objetivo** | **+500** | Inventario ≥ 3 maderas |
| 🪵 **Conseguir 1 madera** | **+100** | Item en inventario (Malmo) |
| 🪓 **Picar madera** | **+30** | attack + mirando madera |
| 🔁 **Picar consistente** | **+10** | Picar mismo bloque |
| 👁️ **Mirar madera cerca** | **+20** | Raycast madera < 3m |
| 👁️ **Mirar madera lejos** | **+10** | Raycast madera 3-5m |
| 🌳 **Madera en grid** | **+10** | Detectada en percepción |
| 🍃 **Hojas abundantes** | **+5** | >5 hojas = árbol cerca |
| 🚶 **Moverse exitoso** | **+3** | Cambio de posición real |

### Recompensas Negativas

| Evento | Valor | Trigger |
|--------|-------|---------|
| ⚡ **Costo acción** | **-0.5** | Cada comando (Malmo) |
| ❌ **Picar aire** | **-5** | attack sin mirar madera |
| 🚧 **Colisión repetida** | **-10** | 5+ pasos sin movimiento |
| 🔄 **Loop de giros** | **-20** | 6 giros consecutivos |
| 🔄 **Loop de ataques** | **-25** | 6 ataques sin madera |
| 🛑 **Atascado total** | **-30** | >10 pasos sin movimiento |

---

## 📊 Observaciones del Entorno

### ObservationFromGrid (5×5×5)
```xml
<Grid name="near5x5x5">
  <min x="-2" y="-2" z="-2"/>
  <max x="2" y="2" z="2"/>
</Grid>
```
- **Total**: 125 bloques
- **Uso**: Detección de madera, hojas, obstáculos

### ObservationFromRay
```json
{
  "type": "log",        // Tipo de bloque mirando
  "distance": 2.5       // Distancia en bloques
}
```
- **Uso**: Precisión para picar

### ObservationFromFullInventory
```json
{
  "inventory": [
    {"type": "wooden_axe", "quantity": 1, "slot": 0},
    {"type": "log", "quantity": 2}
  ]
}
```
- **Uso**: Tracking de madera recolectada

---

## 🔧 Hiperparámetros Q-Learning

```python
alpha = 0.15          # Tasa de aprendizaje (↑ del 0.1)
gamma = 0.95          # Factor de descuento
epsilon = 0.4         # Exploración inicial (↑ del 0.3)
epsilon_min = 0.05    # Mínimo epsilon
epsilon_decay = 0.995 # Decaimiento por episodio
```

### Justificación de cambios:
- **Alpha más alto**: Entorno más complejo (picar vs tocar)
- **Epsilon más alto**: Más exploración necesaria (buscar Y picar)

---

## 🎮 Configuración XML Malmo

### Mundo
```xml
<DefaultWorldGenerator seed="42" forceReset="false"/>
```
- **Seed fija (42)**: Reproducibilidad
- **forceReset=false**: Reutilizar mundo (más rápido)

### Inventario Inicial
```xml
<Inventory>
  <InventoryItem slot="0" type="wooden_axe"/>
</Inventory>
```
- **Hacha de madera** en primer slot de hotbar
- Permite picar madera

### Límites de Tiempo
```xml
<ServerQuitFromTimeUp timeLimitMs="120000"/>
```
- **2 minutos** por episodio (vs 1 minuto en agua)
- Más tiempo para buscar + picar

### Condición de Salida
```xml
<AgentQuitFromCollectingItem>
  <Item type="log" amount="3"/>
</AgentQuitFromCollectingItem>
```
- Termina automáticamente al conseguir 3 maderas

---

## 📈 Métricas de Evaluación

### Durante Entrenamiento
- **Tasa de éxito**: % episodios con 3+ maderas
- **Madera promedio**: Maderas por episodio
- **Pasos promedio**: Eficiencia temporal
- **Recompensa acumulada**: Tendencia de aprendizaje

### Gráficos Generados (utils_madera.py)
1. **Recompensas** + media móvil (ventana 5)
2. **Madera recolectada** (barra: verde=éxito, rojo=fallo)
3. **Pasos por episodio** + eficiencia
4. **Epsilon decay** (exploración vs explotación)

---

## 🔄 Flujo de Entrenamiento

```
┌─────────────────────────────────────────────────┐
│  1. INICIAR EPISODIO                            │
│     - Reset entorno                             │
│     - Spawn con hacha                           │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│  2. BUCLE DE DECISIÓN (max 800 pasos)           │
│     ┌───────────────────────────────────────┐   │
│     │ a) Observar: grid + raycast + inv    │   │
│     │ b) Discretizar estado                │   │
│     │ c) Elegir acción (ε-greedy)          │   │
│     │ d) Ejecutar comando                  │   │
│     │ e) Capturar recompensa Malmo         │   │
│     │ f) Calcular recompensa total         │   │
│     │ g) Actualizar Q(s,a)                 │   │
│     │ h) Verificar inventario ≥ 3          │   │
│     └───────────────────────────────────────┘   │
│            ↓ (si no completado)                 │
│            └─────────────────┐                  │
└──────────────────────────────┼──────────────────┘
                               ↓
┌─────────────────────────────────────────────────┐
│  3. FINALIZAR EPISODIO                          │
│     - Guardar estadísticas                      │
│     - Decaer epsilon                            │
│     - Guardar modelo (cada 5 episodios)         │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Extensión a Otros Materiales

### Piedra (Siguiente Fase)
```python
# Cambios necesarios:
TIPOS_OBJETIVO = ["stone", "cobblestone"]
HERRAMIENTA_INICIAL = "wooden_pickaxe"
CANTIDAD_OBJETIVO = 5  # bloques
```

### Hierro
```python
TIPOS_OBJETIVO = ["iron_ore"]
HERRAMIENTA_INICIAL = "stone_pickaxe"
ESTADO += (nivel_y_categoria,)  # Buscar en profundidad
```

### Diamante
```python
TIPOS_OBJETIVO = ["diamond_ore"]
HERRAMIENTA_INICIAL = "iron_pickaxe"
RESTRICCION_Y = "y < 16"  # Solo capas profundas
```

---

## 🐛 Mecanismos Anti-Stuck

### Detección de Loops
```python
# Loop de giros (sin moverse)
if ultimas_6_acciones.todas("turn") and sin_movimiento > 3:
    recompensa -= 20
```

### Sistema de Escape
```python
if pasos_sin_movimiento > 10:
    forzar_secuencia([
        "turn 1",      # Girar 90°
        "turn 1",      # Girar 90° más (180° total)
        "jumpmove 1"   # Saltar hacia adelante
    ])
```

---

## 📦 Archivos del Proyecto

```
carlos/
├── mundo2v2.py                 # ⭐ Script principal
├── agente_madera_rl.py         # Algoritmo Q-Learning
├── entorno_madera.py           # Wrapper Malmo + recompensas
├── utils_madera.py             # Visualización y análisis
├── configurar.py               # Setup automático
├── test_sistema_madera.py      # Tests unitarios
├── README_MADERA.md            # Documentación completa
├── RESUMEN_TECNICO.md          # Este archivo
└── modelo_agente_madera.pkl    # (generado al entrenar)
```

---

## 🎓 Referencias Técnicas

- **Algoritmo**: Q-Learning (Watkins & Dayan, 1992)
- **Entorno**: Project Malmo (Microsoft Research)
- **Juego**: Minecraft 1.11.2
- **Python**: 3.7+
- **Librerías**: NumPy, Matplotlib, Pickle

---

## ✅ Checklist de Uso

- [ ] Malmo instalado y configurado
- [ ] Minecraft 1.11.2 corriendo (puerto 10000)
- [ ] Dependencias Python instaladas
- [ ] Verificar con: `python configurar.py`
- [ ] Entrenar: `python mundo2v2.py`
- [ ] Visualizar: `python utils_madera.py graficar`
- [ ] Analizar: `python utils_madera.py analizar`

---

**Última actualización**: 2 de noviembre de 2025  
**Autor**: Sistema de IA  
**Proyecto**: Seminario 1 - Aprendizaje por Refuerzo en Minecraft
