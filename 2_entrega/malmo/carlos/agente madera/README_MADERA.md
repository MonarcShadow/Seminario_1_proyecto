# 🪓 Agente RL para Recolección de Madera en Minecraft

Sistema de Aprendizaje por Refuerzo (Q-Learning) para entrenar un agente que aprenda a recolectar madera en Minecraft usando Project Malmo.

## 🎯 Objetivo

Entrenar un agente que pueda:
1. **Buscar árboles** en el entorno
2. **Acercarse** a los troncos de madera
3. **Picar** los bloques usando el hacha
4. **Recolectar 3 bloques de madera** en el inventario

Este es el **primer objetivo** de una secuencia de tareas de recolección:
- ✅ **Madera** (actual) - 3 bloques
- 🔜 Piedra
- 🔜 Hierro
- 🔜 Diamante

## 📁 Estructura del Proyecto

```
carlos/
├── mundo2v2.py              # Script principal de entrenamiento
├── agente_madera_rl.py      # Agente Q-Learning
├── entorno_madera.py        # Wrapper del entorno Malmo
├── utils_madera.py          # Utilidades de visualización
├── modelo_agente_madera.pkl # Modelo entrenado (generado)
└── README_MADERA.md         # Este archivo
```

## 🚀 Requisitos

### Software necesario:
- Python 3.7+
- Project Malmo instalado y configurado
- Minecraft 1.11.2 (para Malmo)
- Librerías Python:
  ```bash
  pip install numpy matplotlib pickle
  ```

### Verificar instalación de Malmo:
```bash
# Debe poder importar sin errores
python -c "import MalmoPython; print('Malmo OK')"
```

## 🎮 Uso

### 1. Entrenar el agente

```bash
# Iniciar Minecraft con Malmo en puerto 10000
# Luego ejecutar:
python mundo2v2.py
```

**Parámetros configurables** (editar en `mundo2v2.py`):
```python
NUM_EPISODIOS = 30        # Cantidad de episodios de entrenamiento
MODELO_PATH = "modelo_agente_madera.pkl"  # Ruta del modelo
```

### 2. Visualizar resultados del entrenamiento

```bash
# Generar gráficos
python utils_madera.py graficar

# Analizar tabla Q
python utils_madera.py analizar
```

### 3. Continuar entrenamiento previo

El sistema automáticamente carga el modelo si existe:
```python
# Si encuentra modelo_agente_madera.pkl, continúa desde ahí
# Si no, inicia desde cero
```

## 🧠 Cómo Funciona

### Estado del Agente

El estado se representa como una tupla de 7 elementos:

```python
estado = (
    orientacion,        # 0-3 (N, E, S, O)
    nivel_madera,       # 0=ninguna, 1=poca, 2=mucha visible
    nivel_inventario,   # 0, 1, 2, o 3+ bloques
    mirando_madera,     # 0=no, 1=sí
    dist_categoria,     # 0=muy cerca, 1=cerca, 2=lejos
    obstaculo_frente,   # 0=libre, 1=bloqueado
    indicador_hojas     # 0=sin hojas, 1=algunas, 2=muchas
)
```

### Acciones Disponibles

```python
0: "move 1"        # Avanzar
1: "turn 1"        # Girar derecha 90°
2: "turn -1"       # Girar izquierda 90°
3: "jumpmove 1"    # Saltar y avanzar
4: "attack 1"      # Picar/Atacar
5: "strafe 1"      # Moverse lateral derecha
6: "strafe -1"     # Moverse lateral izquierda
```

### Sistema de Recompensas

| Evento | Recompensa | Descripción |
|--------|-----------|-------------|
| 🎉 Conseguir 3 maderas | **+500** | ¡Objetivo completado! |
| 🪵 Conseguir 1 madera | **+100** | Progreso hacia objetivo |
| 🪓 Picar madera | **+30** | Acción correcta |
| 👁️ Mirar madera | **+20** | Preparación para picar |
| 🌳 Detectar madera | **+10** | Proximidad a objetivo |
| 🍃 Detectar hojas | **+5** | Indicador de árbol |
| 🚶 Moverse | **+3** | Exploración |
| ⚡ Cada acción | **-0.5** | Costo de tiempo |
| ❌ Picar aire | **-5** | Acción ineficiente |
| 🚧 Colisión | **-10** | Obstáculo |
| 🔄 Loop detectado | **-20** | Comportamiento repetitivo |
| 🛑 Atascado | **-30** | Sin progreso |

### Algoritmo Q-Learning

```
Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]

Donde:
- α (alpha) = 0.15   : Tasa de aprendizaje
- γ (gamma) = 0.95   : Factor de descuento
- ε (epsilon) = 0.4  : Exploración inicial (decae a 0.05)
```

## 📊 Métricas y Evaluación

### Durante el entrenamiento se registra:
- ✅ **Tasa de éxito**: % de episodios con 3+ maderas
- 📈 **Recompensa promedio**: Tendencia de aprendizaje
- 📉 **Pasos por episodio**: Eficiencia del agente
- 🪵 **Madera promedio**: Progreso hacia objetivo
- 🔍 **Epsilon (exploración)**: Decaimiento de exploración

### Gráficos generados:
1. **Evolución de recompensas** (con media móvil)
2. **Madera recolectada** (verde = éxito, rojo = fallo)
3. **Eficiencia** (número de pasos)
4. **Decaimiento de exploración** (epsilon)

## 🔧 Configuración Avanzada

### Ajustar hiperparámetros del agente:

Editar en `mundo2v2.py`:

```python
agente = AgenteMaderaQLearning(
    alpha=0.15,         # Mayor = aprende más rápido
    gamma=0.95,         # Mayor = más peso al futuro
    epsilon=0.4,        # Mayor = más exploración
    epsilon_decay=0.995 # Mayor = decae más lento
)
```

### Modificar el mundo (XML):

Editar función `obtener_mision_xml()` en `mundo2v2.py`:

```python
# Cambiar semilla del mundo
seed = 42  # Diferentes valores = diferentes mundos

# Cambiar tiempo límite
timeLimitMs="120000"  # 2 minutos

# Cambiar spawn
<Placement x="0" y="64" z="0" pitch="0" yaw="0"/>
```

## 🐛 Solución de Problemas

### Error: "No module named MalmoPython"
```bash
# Verificar que Malmo esté instalado y en PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/ruta/a/MalmoPlatform/Python_Examples
```

### Error: "Connection refused" al iniciar misión
```bash
# Asegurarse que Minecraft con Malmo esté corriendo
# Verificar que use el puerto 10000
```

### El agente no aprende / Se queda atascado
- Aumentar `epsilon` (más exploración)
- Reducir `alpha` (aprendizaje más conservador)
- Aumentar número de episodios
- Verificar que haya árboles cerca del spawn

### Recompensas muy negativas
- Revisar sistema de recompensas en `entorno_madera.py`
- Aumentar bonificación por detectar madera
- Reducir penalización por atascarse

## 📚 Próximos Pasos

### Para extender el sistema a otros materiales:

1. **Piedra**: 
   - Cambiar `tipos_madera` por `tipos_piedra`
   - Ajustar recompensas para detectar piedra
   - Inventario inicial: pico de madera

2. **Hierro**:
   - Requiere pico de piedra
   - Buscar en cuevas/profundidad
   - Estado debe incluir nivel Y

3. **Diamante**:
   - Requiere pico de hierro
   - Buscar en Y < 16
   - Mayor dificultad de exploración

## 📖 Referencias

- [Project Malmo Documentation](https://microsoft.github.io/malmo/)
- [Q-Learning Algorithm](https://en.wikipedia.org/wiki/Q-learning)
- [Minecraft Wiki - Wood](https://minecraft.gamepedia.com/Wood)

## 👥 Autor

Sistema de IA - Seminario 1 Proyecto

## 📄 Licencia

Proyecto académico - Universidad

---

**¡Buena suerte entrenando tu agente! 🤖🪓🌳**
