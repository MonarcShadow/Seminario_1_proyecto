# Agente RL - Búsqueda y Recolección de Madera

## 🎯 Objetivo
Agente de aprendizaje por refuerzo (Q-Learning) que aprende a buscar, encontrar y recolectar madera en Minecraft usando Malmo.

## 📁 Archivos principales

### Scripts de entrenamiento
- **`entrenar_normal.py`**: Entrenamiento en mundo normal (DefaultWorldGenerator)
- **`entrenar_plano.py`**: Entrenamiento en mundo plano (para pruebas)
- **`test_movimiento.py`**: Verificación básica de comandos de movimiento
- **`debug_movimiento.py`**: Debug detallado del sistema de movimiento

### Módulos principales
- **`agente_rl.py`**: Implementación del agente Q-Learning
- **`entorno_malmo.py`**: Wrapper del entorno de Malmo, sistema de recompensas
- **`mundo_rl.py`**: Configuración del mundo XML y loop de entrenamiento
- **`utils.py`**: Utilidades para análisis y visualización

## 🚀 Uso

### Entrenamiento en mundo normal (recomendado)
```bash
malmoenv  # Activar entorno virtual
cd "agente madera"
python3 entrenar_normal.py 50  # 50 episodios
```

### Pruebas en mundo plano
```bash
python3 entrenar_plano.py 10  # 10 episodios de prueba
```

### Verificar movimiento básico
```bash
python3 test_movimiento.py
```

## 🔧 Correcciones aplicadas (Nov 2025)

### Problema: Agente no se movía
**Síntomas**: Posición fija, sistema anti-stuck activándose constantemente

**Causas identificadas**:
1. ✅ Duración de comandos muy lenta (0.5s → 0.1s)
2. ✅ Cálculo de distancia en 3D incluía Y (saltos contaban como no-movimiento)
3. ✅ Thresholds anti-stuck muy altos (18 → 10)
4. ✅ Lógica de penalizaciones incorrecta (aplicaba siempre en vez de solo cuando no se movía)
5. ✅ Spawn aleatorio colocaba agente en posiciones inválidas
6. ✅ Condición `AgentQuitFromReachingPosition` terminaba misión inmediatamente

**Soluciones aplicadas**:

#### 1. Duración de comandos (entorno_malmo.py)
```python
# Antes: duracion=0.5 (muy lento)
def ejecutar_accion(self, comando, duracion=0.5):

# Después: duracion=0.1 (igual que agente agua)
def ejecutar_accion(self, comando, duracion=0.1):
```

#### 2. Distancia en 2D (entorno_malmo.py)
```python
# Antes: Distancia 3D (incluía Y)
distancia = ((dx)**2 + (dy)**2 + (dz)**2)**0.5

# Después: Distancia 2D (solo X,Z - ignora saltos)
distancia = ((posicion_actual[0] - self.posicion_previa[0])**2 + 
            (posicion_actual[2] - self.posicion_previa[2])**2)**0.5
```

#### 3. Thresholds anti-stuck (mundo_rl.py)
```python
# Antes: Muy tolerante, permitía demasiado tiempo sin movimiento
if entorno.pasos_sin_movimiento > 18:

# Después: Más estricto, igual que agente agua
if entorno.pasos_sin_movimiento > 10:
```

#### 4. Lógica de penalizaciones (entorno_malmo.py)
```python
# Antes: Historial y penalizaciones SIEMPRE
if distancia > 0.3:
    recompensa += 3.0
else:
    self.pasos_sin_movimiento += 1

self.historial_acciones.append(accion)  # ❌ Siempre
if self.pasos_sin_movimiento > 3:      # ❌ Penaliza incluso si se movió
    recompensa -= ...

# Después: Historial y penalizaciones SOLO cuando NO se mueve
if distancia > 0.3:
    recompensa += 3.0
    self.pasos_sin_movimiento = 0
else:
    self.pasos_sin_movimiento += 1
    self.historial_acciones.append(accion)  # ✅ Solo si no se movió
    if self.pasos_sin_movimiento > 3:       # ✅ Solo penaliza sin movimiento
        recompensa -= ...
```

#### 5. Spawn fijo (mundo_rl.py, entrenar_plano.py)
```python
# Antes: Spawn aleatorio (mundo plano puede tener agua/bloques)
spawn_x = random.uniform(-150, 150)
spawn_z = random.uniform(-150, 150)

# Después: Spawn natural del mundo (seguro)
spawn_x = None  # Mundo normal: spawn natural
spawn_z = None

# O spawn fijo para mundo plano:
spawn_x = 0.5
spawn_z = 0.5
```

#### 6. Condiciones de salida (mundo_rl.py)
```python
# Removido: Condición problemática que terminaba misión inmediatamente
# <AgentQuitFromReachingPosition>
#   <Marker x="0" y="20" z="0" tolerance="50.0"/>
# </AgentQuitFromReachingPosition>

# Mantenido: Solo terminar al colectar madera
<AgentQuitFromCollectingItem>
  <Item type="log" />
  <Item type="log2" />
</AgentQuitFromCollectingItem>
```

## 📊 Resultados después de correcciones

### Antes
- Pasos: 0-108
- Posición: **FIJA** (46.0, 4.0, 23.6)
- Comportamiento: Solo saltaba en el mismo lugar
- Recompensa: -3527.00

### Después
- Pasos: 106+
- Posición: **CAMBIANDO** (0.5→22.5→54.5→84.5→114.5)
- Comportamiento: Se mueve correctamente, explora
- Recompensa: +35.00

## 🎮 Acciones disponibles

1. **`move 1`**: Avanzar 1 bloque
2. **`turn 1`**: Girar 90° a la derecha
3. **`turn -1`**: Girar 90° a la izquierda
4. **`jumpmove 1`**: Saltar y avanzar
5. **`attack 1`**: Picar bloque (mantiene presionado)

## 🧠 Estado discretizado (9 dimensiones)

1. **orientacion**: 0-3 (N, E, S, O)
2. **madera_cerca**: 0-1 (hay madera en grid 5x3x5)
3. **madera_frente**: 0-1 (hay madera justo enfrente)
4. **distancia_madera**: 0-3 (muy cerca, cerca, lejos, no visible)
5. **obstaculo_frente**: 0-1 (bloque sólido enfrente)
6. **tiene_madera**: 0-1 (madera en inventario)
7. **altura_relativa**: 0-2 (bajo, medio, alto)
8. **aire_frente**: 0-1 (aire enfrente)
9. **mirando_madera**: 0-1 (LineOfSight ve madera)

## 🎁 Sistema de recompensas

| Evento | Recompensa |
|--------|-----------|
| Colectar madera (Malmo) | +50.0 |
| Moverse exitosamente | +3.0 |
| Comando enviado | -0.5 |
| Sin movimiento (progresiva) | -2.0 * pasos |
| Loop de giros | -20.0 |
| Completamente atascado (>8 pasos) | -30.0 |
| Picar sin madera enfrente | -10.0 |

## 🔍 Debugging

Si el agente no se mueve:
1. Ejecutar `python3 debug_movimiento.py` para verificar comandos
2. Revisar que `duracion=0.1` en `ejecutar_accion()`
3. Verificar que distancia se calcula solo en 2D (X,Z)
4. Confirmar que spawn no es aleatorio problemático
5. Revisar logs de Malmo para errores

## 📈 Comparación con agente de agua

El agente de madera está basado en el agente de agua (que funciona correctamente).
Diferencias principales:
- ✅ **Acciones**: Madera tiene 5 (incluye `attack`), Agua tiene 4
- ✅ **Estado**: Madera 9D, Agua 5D
- ✅ **Duración**: Ambos usan 0.1s
- ✅ **Distancia**: Ambos usan 2D (X,Z)
- ✅ **Thresholds**: Ambos usan 3 y 8 pasos
- ✅ **Penalizaciones**: Misma lógica (solo cuando no se mueve)

## 🚧 Próximos pasos

1. ✅ Agente se mueve correctamente
2. 🔄 Entrenar en mundo normal con árboles
3. 🔄 Optimizar heurística de picar madera
4. 🔄 Ajustar parámetros de aprendizaje (alpha, gamma, epsilon)
5. 📋 Implementar agente de piedra
6. 📋 Implementar agente de hierro
7. 📋 Implementar agente de diamante

## 📝 Notas técnicas

- Minecraft versión: 1.11.2
- Malmo: 0.37.0
- Python: 3.6.15
- Puerto: 10001 (hardcoded)
- Semilla por defecto: 123456
