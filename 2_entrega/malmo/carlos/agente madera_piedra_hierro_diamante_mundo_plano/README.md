# Agente RL Progresivo Multi-Material

Agente de Aprendizaje por Refuerzo que progresa a través de múltiples objetivos en Minecraft:
**Madera → Piedra → Hierro → Diamante**

## 🎯 Objetivos del Agente

El agente debe completar las siguientes fases en orden:

### Fase 0: 🌲 MADERA
- **Objetivo:** Recolectar 3 bloques de madera
- **Herramienta:** Ninguna (mano)
- **Método:** Picar troncos de árboles

### Fase 1: 🪨 PIEDRA  
- **Objetivo:** Recolectar 3 bloques de piedra
- **Herramienta:** Pico de madera (proporcionado al inicio)
- **Método:** Picar bloques de piedra/cobblestone
- **Crafteo simulado:** Al completar, recibe pico de piedra

### Fase 2: ⚙️ HIERRO
- **Objetivo:** Recolectar 3 lingotes de hierro
- **Herramienta:** Pico de piedra
- **Método:** Picar menas de hierro (conversión automática a lingote)
- **Crafteo simulado:** Al completar, recibe pico de hierro

### Fase 3: 💎 DIAMANTE (Final)
- **Objetivo:** Recolectar 1 diamante
- **Herramienta:** Pico de hierro
- **Método:** Picar mena de diamante
- **¡Éxito!** Objetivo final completado

## 🗺️ Entorno Controlado

### Características del Mundo Plano

- **Tamaño:** 50×50 bloques
- **Spawn:** Centro (0, 4, 0)
- **Perímetro:** Muro de obsidiana (altura 6 bloques)
- **Suelo:** Piedra

### Distribución de Materiales

Todos los materiales se generan aleatoriamente dentro del área:

- **🌲 Madera:** 15-20 ubicaciones (troncos oak/spruce)
- **🪨 Piedra:** 15-20 ubicaciones (stone/cobblestone)
- **⚙️ Hierro:** 8-12 ubicaciones (iron_ore)
- **💎 Diamante:** 3-5 ubicaciones (diamond_ore)

Algunos materiales se colocan en torres de 1-3 bloques de altura para requerir cambios de pitch.

## 🧠 Sistema de Aprendizaje

### Algoritmo: Q-Learning Modular

- **Q-tables separadas por fase** (mejor especialización)
- **Parámetros adaptativos** según complejidad de fase
- **Estado:** 12 dimensiones
  - Orientación (0-3: N, E, S, O)
  - Material cerca (bool)
  - Material frente (bool)
  - Distancia a material (0-2)
  - Obstáculo frente (bool)
  - Aire frente (bool)
  - Tiene suficiente material (bool)
  - Altura relativa (0-2)
  - Mirando material (bool)
  - Ángulo vertical (0-2: abajo, frente, arriba)
  - Fase actual (0-3)
  - Herramienta correcta (bool)

### Acciones (7 total)

```python
0: move 1        # Avanzar
1: turn 1        # Girar derecha
2: turn -1       # Girar izquierda
3: jumpmove 1    # Saltar + avanzar
4: attack 1      # Picar
5: pitch 1       # Mirar arriba
6: pitch -1      # Mirar abajo
```

### Sistema de Recompensas

Las recompensas escalan según la fase (más difícil = mayor recompensa):

#### Recompensas Positivas
- **+200-500:** Obtener material objetivo (×fase)
- **+30-100:** Picar material correcto
- **+20-50:** Estar muy cerca del objetivo
- **+10-25:** Estar cerca del objetivo
- **+5-10:** Movimiento efectivo hacia objetivo
- **+8-15:** Usar pitch cerca de objetivo

#### Castigos Negativos
- **-30 a -100:** Atacar sin herramienta correcta (no drop)
- **-30 a -50:** Atacar sin objetivo frente
- **-10 a -20:** Buscar material de fase anterior
- **-5×N:** Holgazanear cerca sin picar (N pasos - 8)
- **-1:** Quedarse atascado sin movimiento

### Parámetros Adaptativos por Fase

```python
Fase 0 (MADERA):   α=0.10, ε=0.40, mult=1.0
Fase 1 (PIEDRA):   α=0.12, ε=0.35, mult=1.2
Fase 2 (HIERRO):   α=0.15, ε=0.30, mult=1.5
Fase 3 (DIAMANTE): α=0.20, ε=0.25, mult=2.0
```

## 📦 Estructura del Proyecto

```
agente madera_piedra_hierro_diamante_mundo_plano/
├── agente_rl.py          # Agente Q-Learning modular
├── entorno_malmo.py      # Entorno con recompensas por fase
├── mundo_rl.py           # Generador de mundo + loop entrenamiento
├── utils.py              # Utilidades
├── README.md             # Este archivo
└── modelo_progresivo.pkl # Modelo entrenado (se genera)
```

## 🚀 Uso

### Requisitos Previos

1. **Minecraft 1.11.2** corriendo con Malmo
2. **Malmo 0.37.0** instalado
3. **Python 3.6+** con MalmoPython

### ⚠️ IMPORTANTE: Configuración del Cliente

Si Minecraft está en otra máquina (ejemplo: Windows), edita `config.py`:

```python
MINECRAFT_HOST = "192.168.1.100"  # IP de la máquina con Minecraft
MINECRAFT_PORT = 10001
```

Para encontrar la IP en Windows: `ipconfig` en CMD

Ver guía completa en: **[CONEXION_CLIENTE.md](CONEXION_CLIENTE.md)**

### Verificar Conexión

```bash
# Probar que el cliente está disponible
python3 config.py

# O usar test completo
python3 test_sistema.py
```

### Entrenamiento

```bash
# Entrenar 100 episodios con semilla fija
python3 mundo_rl.py 100 123456

# Entrenar 50 episodios con otra semilla
python3 mundo_rl.py 50 999888

# Por defecto (100 episodios, semilla 123456)
python3 mundo_rl.py
```

### Parámetros

- **Argumento 1:** Número de episodios (default: 100)
- **Argumento 2:** Semilla para mundo (default: 123456)

### Durante el Entrenamiento

El programa muestra:
- 🗺️ Generación del mundo (cantidad de materiales)
- 🎮 Progreso en tiempo real cada 50 pasos
- 📊 Resumen al final de cada episodio
- 💾 Guardado de modelo cada 10 episodios

### Ejemplo de Salida

```
================================================================
🗺️  MUNDO PLANO GENERADO
================================================================
Área: 50x50 bloques
Spawn: (0, 4, 0)

Materiales colocados:
  🌲 Madera:   18 ubicaciones (23 bloques)
  🪨 Piedra:   17 ubicaciones (21 bloques)
  ⚙️  Hierro:   10 ubicaciones (14 bloques)
  💎 Diamante: 4 ubicaciones (5 bloques)

Semilla: 123456
================================================================

🌲 +1 MADERA obtenida! (Total: 1/3) [+200.0]
🌲 +1 MADERA obtenida! (Total: 2/3) [+200.0]
🌲 +1 MADERA obtenida! (Total: 3/3) [+200.0]

============================================================
🌲 FASE MADERA COMPLETADA!
   Madera recolectada: 3/3
   → Avanzando a fase PIEDRA
============================================================

🪨 +1 PIEDRA obtenida! (Total: 1/3) [+250.0]
...
```

## 🎓 Simplificaciones del Proyecto

Para facilitar el entrenamiento, se implementaron estas simplificaciones:

1. **Inventario limpiado** al inicio (evitar items de episodios anteriores)
2. **Pico de madera inicial** dado por comando `/give`
3. **Crafteo simulado:** Al completar fase, se da herramienta siguiente automáticamente
4. **Conversión hierro:** Iron_ore → iron_ingot automática (sin horno)
5. **Mundo plano controlado:** Todos los materiales cerca (50×50 área)

## ⚠️ Consideraciones

### Castigos por Herramienta Incorrecta

El agente aprende que:
- Picar piedra sin pico de madera → no drop → castigo
- Picar hierro sin pico de piedra → no drop → castigo  
- Picar diamante sin pico de hierro → no drop → castigo

### Progresión Obligatoria

El agente **debe** completar las fases en orden:
- No puede saltar fases
- Atacar materiales de fase anterior da castigo
- Cada fase desbloquea la siguiente

### Timeout

- Máximo 1000 pasos por episodio (~5 minutos)
- Si no completa, episodio falla

## 📊 Métricas de Éxito

Para considerar el entrenamiento exitoso:

- **Tasa de éxito >70%** en últimos 20 episodios
- **Fase 3 alcanzada** consistentemente
- **Recompensa media >1000** en últimos episodios
- **Pasos medio <500** (eficiencia)

## 🔧 Ajuste de Hiperparámetros

Si el agente no aprende bien, ajustar en `agente_rl.py`:

```python
# Aumentar exploración inicial
epsilon=0.5  # default: 0.4

# Reducir decaimiento (explorar más tiempo)
epsilon_decay=0.998  # default: 0.995

# Aumentar aprendizaje
alpha=0.15  # default: 0.1

# Ajustar descuento (balance inmediato vs futuro)
gamma=0.98  # default: 0.95
```

## 📝 Archivos Generados

- `modelo_progresivo.pkl` - Modelo entrenado (Q-tables + parámetros)
- Logs en consola con progreso detallado

## 🐛 Troubleshooting

### Agente se queda atascado
- Sistema anti-stuck a los 15 pasos sin movimiento
- Fuerza turn + jumpmove para escapar

### No encuentra materiales
- Verificar que el mundo se generó correctamente
- Probar con diferente semilla
- Aumentar número de materiales en `generar_mundo_plano_xml()`

### Ataca sin herramienta correcta
- Normal en primeros episodios (exploración)
- Debe aprender con el castigo fuerte
- Si persiste, aumentar castigo en `entorno_malmo.py`

## 🎯 Próximos Pasos

Una vez funcionando en mundo plano:
1. Probar en mundo normal (DefaultWorldGenerator)
2. Reducir cantidad de materiales (más realista)
3. Ampliar área de búsqueda
4. Agregar más objetivos (carbón, redstone, etc.)

---

**Autor:** Sistema de IA  
**Fecha:** Noviembre 2025  
**Versión:** 1.0
