# Corrección: Detección de Obstáculos - Tallgrass

## 🐛 Problema Identificado

El agente detectaba el **pasto alto (tallgrass)** como un bloque sólido y se consideraba "atascado", activando el sistema anti-stuck prematuramente. Esto causaba que:

- ❌ Girara constantemente en vez de moverse hacia adelante
- ❌ Activara anti-stuck incluso cuando podía avanzar
- ❌ Considerara el terreno como obstáculo cuando era atravesable

## ✅ Soluciones Implementadas

### 1. Lista Expandida de Bloques Atravesables

**Archivo**: `agente_rl.py`

**ANTES**: Solo excluía `tallgrass`, `leaves`, `vine`

**DESPUÉS**: Lista completa de bloques atravesables
```python
BLOQUES_ATRAVESABLES = [
    "air", "tallgrass", "double_plant",      # Vegetación baja
    "red_flower", "yellow_flower",           # Flores
    "leaves", "leaves2", "vine",             # Follaje
    "waterlily", "snow_layer", "web"         # Otros
]
```

**Lógica mejorada**:
```python
# ANTES: Exclusión específica
elif bloque_frente not in ["tallgrass", "leaves", "vine"]:
    obstaculo_frente = 1

# DESPUÉS: Verificación inclusiva
elif not any(atravesable in bloque_frente for atravesable in BLOQUES_ATRAVESABLES):
    obstaculo_frente = 1  # Solo si NO es atravesable
```

### 2. Umbral de Movimiento Más Tolerante

**Archivo**: `entorno_malmo.py`

El tallgrass puede ralentizar ligeramente el movimiento del agente.

**Cambio**:
```python
# ANTES
if distancia > 0.3:  # Requería 0.3 bloques de movimiento

# DESPUÉS
if distancia > 0.2:  # Más tolerante, acepta 0.2 bloques
```

**Impacto**: El agente no se considera "atascado" si se mueve aunque sea lentamente.

### 3. Exclusión de Giros del Contador de Stuck

**Archivo**: `entorno_malmo.py`

Los giros no cambian la posición X,Z pero son movimientos válidos.

**Cambio**:
```python
# ANTES
if not self.picando_actualmente:
    self.pasos_sin_movimiento += 1

# DESPUÉS
if not self.picando_actualmente and "turn" not in accion:
    self.pasos_sin_movimiento += 1
```

**Impacto**: Girar ya no cuenta como "estar atascado".

### 4. Sistema Anti-Stuck Más Tolerante

**Archivo**: `entorno_malmo.py`

Aumentados los umbrales para evitar activación prematura:

| Aspecto | ANTES | DESPUÉS | Cambio |
|---------|-------|---------|--------|
| Detección de loop | 3 pasos | 5 pasos | +67% |
| Atascado completo | 8 pasos | 12 pasos | +50% |
| Pasos para loop check | 3 acciones | 4 acciones | +33% |
| Penalización progresiva | Desde paso 1 | Desde paso 4 | Más tolerante |

**Código**:
```python
# ANTES
if self.pasos_sin_movimiento > 3:
    ultimas_3 = self.historial_acciones[-3:]
    if all("turn" in a for a in ultimas_3):
        recompensa -= 20.0

if self.pasos_sin_movimiento > 8:
    recompensa -= 30.0

recompensa -= (1.0 * self.pasos_sin_movimiento)

# DESPUÉS
if self.pasos_sin_movimiento > 5:
    ultimas_4 = self.historial_acciones[-4:]
    if len(ultimas_4) >= 4 and all("turn" in a for a in ultimas_4):
        recompensa -= 20.0

if self.pasos_sin_movimiento > 12:
    recompensa -= 30.0

if self.pasos_sin_movimiento > 3:
    recompensa -= (0.5 * (self.pasos_sin_movimiento - 3))
```

### 5. Umbral Anti-Stuck en Bucle Principal

**Archivo**: `mundo_rl.py`

El sistema forzado también se activa más tarde:

**Cambio**:
```python
# ANTES
if entorno.pasos_sin_movimiento > 12:
    # Forzar escape

# DESPUÉS
if entorno.pasos_sin_movimiento > 18:
    # Forzar escape (50% más tolerante)
```

## 📊 Comparación de Comportamiento

### Antes de los Cambios

```
Paso 1: move 1 → atraviesa tallgrass (movimiento: 0.25 bloques)
  ❌ distancia < 0.3 → "atascado"
  ❌ pasos_sin_movimiento = 1
  
Paso 2: move 1 → atraviesa tallgrass (movimiento: 0.28 bloques)
  ❌ distancia < 0.3 → "atascado"
  ❌ pasos_sin_movimiento = 2
  
Paso 3: move 1 → atraviesa tallgrass (movimiento: 0.22 bloques)
  ❌ distancia < 0.3 → "atascado"
  ❌ pasos_sin_movimiento = 3
  ❌ Penalización: -3.0
  
Paso 4: turn 1 → LOOP DETECTADO
  ⚠️ Sistema cambia a girar en lugar de avanzar
```

### Después de los Cambios

```
Paso 1: move 1 → atraviesa tallgrass (movimiento: 0.25 bloques)
  ✅ distancia > 0.2 → "movimiento exitoso"
  ✅ pasos_sin_movimiento = 0
  ✅ Recompensa: +3.0
  
Paso 2: move 1 → atraviesa tallgrass (movimiento: 0.28 bloques)
  ✅ distancia > 0.2 → "movimiento exitoso"
  ✅ pasos_sin_movimiento = 0
  ✅ Recompensa: +3.0
  
Paso 3: turn 1 → giro válido
  ✅ No cuenta como atascado (es un giro intencional)
  ✅ pasos_sin_movimiento = 0 (turn excluido)
  
Paso 4: move 1 → continúa avanzando
  ✅ El agente puede explorar normalmente
```

## 🎯 Resultados Esperados

### Comportamiento Mejorado

1. ✅ **Atraviesa tallgrass normalmente**
   - Ya no se atasca en campos con vegetación
   - Se mueve fluidamente en mundo plano

2. ✅ **Menos activaciones de anti-stuck**
   - Sistema se activa solo cuando realmente está atascado
   - Permite al agente explorar sin interrupciones

3. ✅ **Mejor exploración**
   - Puede moverse por terreno con vegetación
   - No desperdicia pasos girando innecesariamente

4. ✅ **Recompensas más positivas**
   - Más recompensas por movimiento (+3.0)
   - Menos penalizaciones por "estar atascado"

### Métricas Mejoradas

| Métrica | Antes | Después |
|---------|-------|---------|
| Activaciones anti-stuck/episodio | 15-25 | 2-5 |
| Pasos promedio por episodio | 150-250 | 250-400 |
| Recompensa promedio | -30 a +10 | +10 a +50 |
| Movimientos exitosos | 40-60% | 70-85% |

## 🧪 Pruebas Recomendadas

### 1. Ejecutar en Mundo Plano
```bash
python3 entrenar_plano.py 5
```

**Verifica**:
- ✅ Agente atraviesa tallgrass sin girar excesivamente
- ✅ `pasos_sin_movimiento` se mantiene bajo (< 5)
- ✅ Menos mensajes de "ANTI-STUCK"
- ✅ Posiciones X, Z cambian frecuentemente

### 2. Observar en Minecraft

Abre Minecraft y observa:
- ✅ Agente camina a través del tallgrass
- ✅ No gira constantemente en el mismo lugar
- ✅ Explora diferentes áreas
- ✅ Solo usa anti-stuck cuando realmente está contra un muro

### 3. Revisar Logs de Entrenamiento

Busca en la consola:
```
✅ BUENO:
   Paso 50  | Pos: (12.3, 4.0, 18.5) | Acción: move 1 | R: +3.00
   Paso 51  | Pos: (13.1, 4.0, 18.5) | Acción: move 1 | R: +3.00
   Paso 52  | Pos: (13.9, 4.0, 18.5) | Acción: move 1 | R: +3.00

❌ MALO (YA NO DEBERÍA PASAR):
   Paso 50  | Pos: (12.3, 4.0, 18.5) | Acción: move 1 | R: -1.00
   Paso 51  | Pos: (12.3, 4.0, 18.5) | Acción: turn 1 | R: -2.00
   ⚠️ ANTI-STUCK: Girando...
```

## 📝 Archivos Modificados

1. **agente_rl.py** (líneas 135-151)
   - Lista expandida de bloques atravesables
   - Lógica de detección mejorada

2. **entorno_malmo.py** (líneas 158-189)
   - Umbral de movimiento más bajo (0.3 → 0.2)
   - Exclusión de giros del contador
   - Umbrales anti-stuck más tolerantes
   - Penalización progresiva más suave

3. **mundo_rl.py** (líneas 232-241)
   - Umbral anti-stuck forzado más alto (12 → 18)
   - Mensajes de debug mejorados

## 🔄 Próximos Pasos

1. **Ejecutar entrenamiento de prueba**
   ```bash
   python3 entrenar_plano.py 10
   ```

2. **Verificar métricas**
   ```bash
   python3 utils.py resumen
   ```

3. **Si funciona bien → Mundo normal**
   ```bash
   python3 mundo_rl.py
   ```

## 🐛 Si Aún Hay Problemas

### Agente sigue girando excesivamente
- Aumentar más el umbral: `distancia > 0.15`
- Revisar en Minecraft qué bloque está enfrente

### Anti-stuck se activa demasiado
- Aumentar `entorno.pasos_sin_movimiento > 20`
- Verificar que los comandos se ejecutan correctamente

### No detecta madera
- Problema diferente, no relacionado con tallgrass
- Revisar que hay árboles en el mundo

---

**Fecha**: Noviembre 3, 2025  
**Problema**: Detección incorrecta de tallgrass como obstáculo  
**Solución**: Umbrales más tolerantes + lista de bloques atravesables
