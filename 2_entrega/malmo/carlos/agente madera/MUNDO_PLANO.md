# Solución: Mundo Plano para Pruebas

## 🔴 Problemas Identificados

### 1. Mundo Generado Inconsistente
- Misma semilla NO genera mismo mundo si spawn cambia
- Terreno puede tener agujeros, cuevas, lagos
- Agente puede aparecer en agua, lava, o bloques sólidos

### 2. Muerte del Agente
- **Sofocación**: Spawn dentro de bloques sólidos
- **Caídas**: Spawn en acantilados o cuevas
- **Ahogamiento**: Spawn en agua profunda

### 3. Dificultad para Probar
- Imposible verificar si comandos funcionan
- Agente muere antes de moverse
- Comportamiento inconsistente entre ejecuciones

## ✅ Solución Implementada

### Mundo Plano para Pruebas

He modificado el código para soportar **dos modos**:

#### Modo 1: Mundo Plano (Pruebas) 🧪
```python
mundo_plano=True
```
- Terreno completamente plano
- Sin caídas ni cuevas
- Spawn seguro en Y=4
- Ideal para verificar movimientos

#### Modo 2: Mundo Normal (Entrenamiento) 🎮
```python
mundo_plano=False
```
- Mundo generado con semilla
- Terreno realista con árboles
- Para entrenamiento real

## 📝 Cambios Realizados

### 1. `test_movimiento.py` - Reescrito Completamente

**ANTES**: Mundo generado (peligroso)
```python
<DefaultWorldGenerator seed="{seed}" forceReset="true"/>
<Placement x="0" y="64" z="0" pitch="0" yaw="0"/>
```

**DESPUÉS**: Mundo plano (seguro)
```python
<FlatWorldGenerator generatorString="3;7,2*3,2;1;village"/>
<Placement x="0.5" y="4" z="0.5" pitch="0" yaw="0"/>
```

**Ventajas**:
- ✅ Terreno predecible
- ✅ Sin sofocación (Y=4 está sobre el pasto)
- ✅ Sin caídas posibles
- ✅ Pruebas reproducibles

### 2. `mundo_rl.py` - Añadido Parámetro `mundo_plano`

```python
def obtener_mision_xml(seed=None, spawn_x=None, spawn_z=None, mundo_plano=False):
    if mundo_plano:
        world_generator = '<FlatWorldGenerator generatorString="3;7,2*3,2;1;village,biome_1,decoration"/>'
        spawn_y = 4  # Altura del mundo plano
    else:
        world_generator = f'<DefaultWorldGenerator {seed_attr}/>'
        spawn_y = 64
```

**Flexibilidad**: Ahora puedes elegir el tipo de mundo según necesidad.

### 3. `entrenar_plano.py` - Script Nuevo

Script específico para entrenamiento en mundo plano:

```bash
python entrenar_plano.py 10  # 10 episodios de prueba
```

**Características**:
- 🎯 Configurado para mundo plano
- 🎯 Más epsilon (exploración)
- 🎯 Menos pasos por episodio (600 vs 800)
- 🎯 Siempre verbose (para debugging)

## 🧪 Flujo de Trabajo Recomendado

### Paso 1: Verificar Movimientos (30 segundos)
```bash
python test_movimiento.py
```

**Verifica**:
- ✅ Agente aparece en terreno plano
- ✅ Comandos `move 1` mueven al agente
- ✅ Comandos `turn 1` lo giran
- ✅ `jumpmove 1` lo hace saltar
- ✅ Pitch está en 0° (mirando al frente)

### Paso 2: Entrenamiento de Prueba (5-10 minutos)
```bash
python entrenar_plano.py 10
```

**Verifica**:
- ✅ Agente se mueve correctamente
- ✅ No muere ni se atasca
- ✅ Tabla Q se construye
- ✅ Recompensas aumentan con el tiempo

### Paso 3: Entrenamiento Real (40-60 minutos)
```bash
python mundo_rl.py
```

**Solo si Paso 1 y 2 funcionan correctamente**

## 📊 Comparación de Modos

| Aspecto | Mundo Plano 🧪 | Mundo Normal 🎮 |
|---------|---------------|----------------|
| **Terreno** | Perfectamente plano | Irregular, realista |
| **Spawn seguro** | ✅ 100% | ⚠️ Depende de semilla |
| **Árboles** | Limitados | Abundantes |
| **Ideal para** | Pruebas, debugging | Entrenamiento real |
| **Muerte del agente** | ❌ Muy rara | ⚠️ Posible |
| **Reproducibilidad** | ✅ 100% | ⚠️ Depende de spawn |

## 🔧 Configuración del Mundo Plano

### FlatWorldGenerator String
```
3;7,2*3,2;1;village,biome_1,decoration
```

**Decodificado**:
- `3`: Versión del formato
- `7,2*3,2`: Capas de bloques:
  - 1 capa de bedrock (7)
  - 2 capas de dirt (2*3)
  - 1 capa de grass (2)
- `1`: Bioma (plains)
- `village,biome_1,decoration`: Decoraciones (árboles, estructuras)

**Resultado**: Mundo plano con pasto y algunos árboles

## 🐛 Resolución de Problemas

### El agente sigue muriendo en mundo plano
- **Causa**: Raro, pero puede spawnearse en una estructura
- **Solución**: Cambiar el spawn_x/spawn_z ligeramente

### No hay árboles en mundo plano
- **Causa**: La decoración es aleatoria
- **Solución 1**: Ejecutar varias veces hasta que aparezcan
- **Solución 2**: Usar mundo normal una vez verificado que funciona

### Comandos no funcionan en mundo plano
- **Causa**: Problema NO relacionado con el tipo de mundo
- **Solución**: Revisar `CAMBIOS_MOVIMIENTO.md`

## 📈 Resultados Esperados

### Test de Movimiento (test_movimiento.py)
```
✓ Pos cambia con move 1
✓ Yaw cambia con turn 1
✓ Y aumenta con jumpmove 1
✓ Pitch ≈ 0°
```

### Entrenamiento Plano (10 episodios)
```
Episodios exitosos: 1-3 / 10 (10-30%)
Estados en tabla Q: 50-150
Pasos promedio: 200-400
```

### Entrenamiento Normal (50 episodios)
```
Episodios exitosos: 10-25 / 50 (20-50%)
Estados en tabla Q: 300-800
Pasos promedio: 150-300
```

## 🎯 Próximos Pasos

1. ✅ Ejecutar `python test_movimiento.py`
   - Verificar que agente no muere
   - Verificar que se mueve correctamente

2. ✅ Ejecutar `python entrenar_plano.py 10`
   - Verificar que tabla Q se construye
   - Verificar que recompensas aumentan

3. ✅ Si ambos funcionan → `python mundo_rl.py`
   - Entrenamiento completo en mundo normal

4. ⚠️ Si falla algún paso → revisar:
   - Configuración de Malmo
   - Versión de Minecraft (1.11.2)
   - Puerto disponible (10001)
   - IP correcta en `.config`

## 📚 Archivos Relacionados

- `test_movimiento.py` - Prueba rápida en mundo plano
- `entrenar_plano.py` - Entrenamiento de prueba en mundo plano
- `mundo_rl.py` - Entrenamiento normal (mundo generado)
- `CAMBIOS_MOVIMIENTO.md` - Correcciones de comandos

---

**Creado**: Noviembre 3, 2025  
**Propósito**: Solucionar problemas de spawn y muerte del agente  
**Método**: Mundo plano para pruebas, mundo normal para entrenamiento
