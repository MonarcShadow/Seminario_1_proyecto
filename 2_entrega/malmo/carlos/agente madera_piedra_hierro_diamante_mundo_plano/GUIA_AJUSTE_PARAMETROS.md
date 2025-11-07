# Guía Rápida: Ajuste de Parámetros de Entrenamiento

## 📍 Ubicación de Configuraciones

### Archivo Principal: `configuracion_entrenamiento.py`
**TODO lo que necesitas ajustar está aquí** - No necesitas editar otros archivos.

---

## 🎯 Cómo Modificar las Recompensas

### 1. Recompensas por Obtener Material (las MÁS GRANDES)
```python
# Archivo: configuracion_entrenamiento.py
# Línea: ~60

RECOMPENSA_MATERIAL_OBTENIDO = {
    'madera': 200.0,      # ← Cambia aquí
    'piedra': 250.0,      # ← Cambia aquí
    'hierro': 300.0,      # ← Cambia aquí
    'diamante': 500.0,    # ← Cambia aquí
}
```

**Ejemplo**: Si quieres que el diamante valga MUCHO más:
```python
RECOMPENSA_MATERIAL_OBTENIDO = {
    'madera': 200.0,
    'piedra': 250.0,
    'hierro': 300.0,
    'diamante': 1000.0,  # ¡El doble!
}
```

---

### 2. Recompensas por Picar Correctamente
```python
# Archivo: configuracion_entrenamiento.py
# Línea: ~77

RECOMPENSA_ATAQUE_CORRECTO = {
    0: 30.0,    # Fase 0: Picar madera
    1: 40.0,    # Fase 1: Picar piedra
    2: 50.0,    # Fase 2: Picar hierro
    3: 100.0,   # Fase 3: Picar diamante
}
```

**Incrementa estos valores si quieres que el agente pique más agresivamente.**

---

### 3. Recompensas por Proximidad
```python
# Archivo: configuracion_entrenamiento.py
# Línea: ~110

# MUY CERCA (≤ 2 bloques)
RECOMPENSA_OBJETIVO_MUY_CERCA = {
    0: 20.0,   # Madera muy cerca
    1: 25.0,   # Piedra muy cerca
    2: 30.0,   # Hierro muy cerca
    3: 50.0,   # Diamante muy cerca
}

# CERCA (≤ 4 bloques)
RECOMPENSA_OBJETIVO_CERCA = {
    0: 10.0,   # Madera cerca
    1: 12.0,   # Piedra cerca
    2: 15.0,   # Hierro cerca
    3: 25.0,   # Diamante cerca
}
```

**Incrementa si el agente tiene problemas encontrando materiales.**

---

### 4. Multiplicadores por Fase
```python
# Archivo: configuracion_entrenamiento.py
# Línea: ~161

MULTIPLICADOR_FASE = {
    0: 1.0,    # MADERA: sin multiplicador
    1: 1.2,    # PIEDRA: +20%
    2: 1.5,    # HIERRO: +50%
    3: 2.0,    # DIAMANTE: +100% (todo vale el doble)
}
```

**Esto multiplica TODAS las recompensas. Fase 3 vale el doble!**

---

## 🧠 Parámetros de Aprendizaje

```python
# Archivo: configuracion_entrenamiento.py
# Línea: ~20

PARAMETROS_QLEARNING = {
    'alpha': 0.1,              # ← Velocidad de aprendizaje
    'gamma': 0.95,             # ← Importancia del futuro
    'epsilon_inicial': 0.4,    # ← Exploración inicial
    'epsilon_min': 0.05,       # ← Exploración mínima
    'epsilon_decay': 0.995,    # ← Velocidad de decaimiento
}
```

### Qué hace cada uno:

**Alpha (Tasa de Aprendizaje)**:
- `0.1` = Aprende lento pero estable
- `0.3` = Aprende rápido pero puede ser inestable
- **Recomendado**: 0.1 - 0.15

**Gamma (Factor de Descuento)**:
- `0.9` = Solo importa recompensa cercana
- `0.99` = Planifica a largo plazo
- **Recomendado**: 0.95

**Epsilon Inicial (Exploración)**:
- `0.5` = 50% acciones aleatorias (mucha exploración)
- `0.2` = 20% acciones aleatorias (poca exploración)
- **Recomendado**: 0.3 - 0.4

---

## ⚙️ Configuración del Episodio

```python
# Archivo: configuracion_entrenamiento.py
# Línea: ~175

EPISODIO_CONFIG = {
    'max_pasos': 200,              # ← Pasos por episodio
    'timeout_mision_ms': 120000,   # ← Timeout (2 min)
    'delay_entre_comandos': 0.5,   # ← Velocidad
}
```

**Para entrenamientos más largos**:
```python
'max_pasos': 400,              # 4 minutos por episodio
'timeout_mision_ms': 240000,   # 4 minutos timeout
```

---

## 🗺️ Configuración del Mundo

```python
# Archivo: configuracion_entrenamiento.py
# Línea: ~195

MUNDO_CONFIG = {
    'radio': 25,                      # Área 50x50
    'cantidad_madera': (15, 20),      # ← Más/menos madera
    'cantidad_piedra': (15, 20),      # ← Más/menos piedra
    'cantidad_hierro': (8, 12),       # ← Más/menos hierro
    'cantidad_diamante': (3, 5),      # ← Más/menos diamante
}
```

**Mundo más difícil (menos materiales)**:
```python
'cantidad_madera': (8, 12),
'cantidad_piedra': (8, 12),
'cantidad_hierro': (4, 6),
'cantidad_diamante': (1, 2),
```

---

## 📊 Casos de Uso Comunes

### Caso 1: "El agente no encuentra materiales"
**Solución**: Aumentar recompensas de proximidad
```python
RECOMPENSA_OBJETIVO_MUY_CERCA = {
    0: 40.0,   # Duplicado
    1: 50.0,
    2: 60.0,
    3: 100.0,
}

RECOMPENSA_OBJETIVO_CERCA = {
    0: 20.0,   # Duplicado
    1: 24.0,
    2: 30.0,
    3: 50.0,
}
```

---

### Caso 2: "El agente aprende muy lento"
**Solución**: Aumentar velocidad de aprendizaje
```python
PARAMETROS_QLEARNING = {
    'alpha': 0.2,              # Más rápido
    'epsilon_decay': 0.99,     # Decae más rápido
}
```

---

### Caso 3: "El agente se distrae con materiales incorrectos"
**Solución**: Aumentar castigos por fase incorrecta
```python
CASTIGO_FASE_INCORRECTA = {
    1: -30.0,   # Triplicado
    2: -45.0,
    3: -60.0,
}
```

---

### Caso 4: "El diamante es muy difícil de conseguir"
**Solución**: Aumentar recompensas de fase 3
```python
RECOMPENSA_MATERIAL_OBTENIDO = {
    'diamante': 1000.0,  # ¡Mucho más!
}

MULTIPLICADOR_FASE = {
    3: 3.0,  # Triple multiplicador para fase diamante
}
```

---

## 🚀 Aplicar Cambios

1. **Edita** `configuracion_entrenamiento.py`
2. **Guarda** el archivo
3. **Ejecuta** el entrenamiento:
   ```bash
   malmoenv
   python3 mundo_rl.py 10
   ```
4. Los cambios se aplican automáticamente

---

## 📝 Notas Importantes

- **NO MODIFICAR OTROS ARCHIVOS**: Todo está en `configuracion_entrenamiento.py`
- **Backup**: Guarda una copia antes de cambios grandes
- **Probar primero**: Haz 5-10 episodios de prueba antes de entrenamientos largos
- **Logs**: Observa los mensajes para ver si las recompensas funcionan

---

## 🔍 Dónde Encontrar Qué

| Qué necesitas ajustar | Archivo | Línea aprox. |
|----------------------|---------|--------------|
| Recompensas por material obtenido | `configuracion_entrenamiento.py` | ~60 |
| Recompensas por picar | `configuracion_entrenamiento.py` | ~77 |
| Castigos por herramienta incorrecta | `configuracion_entrenamiento.py` | ~85 |
| Recompensas por proximidad | `configuracion_entrenamiento.py` | ~110 |
| Parámetros de aprendizaje | `configuracion_entrenamiento.py` | ~20 |
| Multiplicadores por fase | `configuracion_entrenamiento.py` | ~161 |
| Configuración de episodio | `configuracion_entrenamiento.py` | ~175 |
| Configuración de mundo | `configuracion_entrenamiento.py` | ~195 |

---

**¿Tienes dudas?** Todas las configuraciones tienen comentarios explicativos en el archivo.
