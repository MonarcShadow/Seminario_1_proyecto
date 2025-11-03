# Correcciones Finales - Agente de Madera

## Cambios aplicados (Nov 2025)

### 1. ✅ Agregado `planks` (tablas) como objetivo válido

**Problema**: El agente recogía tablas de madera (`planks`) pero recibía penalización en lugar de recompensa.

**Solución**: Agregado `planks` en recompensas y condiciones de salida.

#### En `mundo_rl.py`:
```xml
<!-- Antes -->
<RewardForCollectingItem>
  <Item type="log" reward="50.0"/>
  <Item type="log2" reward="50.0"/>
</RewardForCollectingItem>

<AgentQuitFromCollectingItem>
  <Item type="log" />
  <Item type="log2" />
</AgentQuitFromCollectingItem>

<!-- Después -->
<RewardForCollectingItem>
  <Item type="log" reward="50.0"/>
  <Item type="log2" reward="50.0"/>
  <Item type="planks" reward="50.0"/>
</RewardForCollectingItem>

<AgentQuitFromCollectingItem>
  <Item type="log" />
  <Item type="log2" />
  <Item type="planks" />
</AgentQuitFromCollectingItem>
```

### 2. ✅ Sistema de detección de items droppeados

**Problema**: Después de picar un bloque, el item cae al suelo pero el agente no se acerca para recogerlo.

**Solución**: Sistema de detección de items cercanos y recompensas por acercarse a ellos.

#### En `entorno_malmo.py`:
```python
# 4.5. DETECTAR ITEMS DROPPEADOS (madera en el suelo)
entities = obs.get("entities", [])
item_madera_cerca = None
distancia_item_min = float('inf')

for entity in entities:
    if entity.get("name", "") == "item":
        # Calcular distancia al item
        dist = ((item_x - agent_x)**2 + (item_z - agent_z)**2)**0.5
        
        if dist < distancia_item_min:
            distancia_item_min = dist
            item_madera_cerca = entity

# Recompensas por proximidad
if item_madera_cerca and distancia_item_min < 5.0:
    if distancia_item_min < 1.5:
        recompensa += 40.0  # Muy cerca
    elif distancia_item_min < 3.0:
        recompensa += 25.0  # Cerca
    else:
        recompensa += 10.0  # Detectado
```

### 3. ✅ Heurística de recolección post-picado

**Problema**: El agente picaba pero no se movía hacia el drop.

**Solución**: Después de terminar de picar, forzar movimiento hacia adelante si hay items cerca.

#### En `mundo_rl.py`:
```python
# Si acaba de terminar de picar
elif entorno.pasos_picando == 0 and entorno.picando_actualmente == False:
    # Detectar si hay items cerca
    entities = obs.get("entities", [])
    hay_items_cerca = any(e.get("name") == "item" for e in entities)
    if hay_items_cerca:
        comando = "move 1"  # Avanzar para recoger
```

### 4. ✅ Mejoras en detección

- `planks` incluido en `TIPOS_MADERA` en `agente_rl.py`
- `planks` incluido en verificación de inventario en `entorno_malmo.py`
- Detección de entidades cercanas en XML (`ObservationFromNearbyEntities`)

## Sistema de recompensas actualizado

| Evento | Recompensa |
|--------|-----------|
| Colectar madera/planks (Malmo) | +50.0 |
| Madera en inventario | +200.0 |
| Item droppeado muy cerca (<1.5m) | +40.0 |
| Item droppeado cerca (<3m) | +25.0 |
| Item droppeado detectado (<5m) | +10.0 |
| Madera muy cerca en grid | +20.0 |
| Madera detectada más cerca | +15.0 |
| Picando madera correctamente | +30.0 |
| Moverse exitosamente | +3.0 |
| Alejándose de madera | -15.0 |
| Picando sin madera enfrente | -10.0 |
| Sin movimiento (progresiva) | -2.0 * pasos |
| Loop de giros | -20.0 |
| Atascado (>8 pasos) | -30.0 |
| Comando enviado | -0.5 |

## Próximos pasos

1. ✅ Agente se mueve correctamente en mundo normal
2. ✅ Detecta y se acerca a árboles
3. ✅ Pica madera
4. ✅ Detecta items droppeados
5. 🔄 Recolecta items exitosamente (requiere más entrenamiento)
6. 📋 Optimizar hiperparámetros
7. 📋 Entrenar por más episodios (50+)

## Comandos para entrenamiento

```bash
# Activar entorno
malmoenv

# Entrenar en mundo normal (recomendado)
cd "agente madera"
python3 entrenar_normal.py 50

# Pruebas en mundo plano
python3 entrenar_plano.py 10
```

## Notas

- El agente necesita estar **muy cerca** del item (< 1.5 bloques) para recogerlo automáticamente
- Después de picar, el agente debe moverse hacia adelante 1-2 bloques
- Los drops pueden caer en direcciones aleatorias, el agente aprenderá con más entrenamiento
- `planks` aparecen naturalmente en aldeas o cuando se destruyen estructuras de madera
