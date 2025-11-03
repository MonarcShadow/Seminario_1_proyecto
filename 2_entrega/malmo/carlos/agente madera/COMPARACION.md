# Comparación: Agente Agua vs Agente Madera

## 📊 Diferencias Principales

### 1. **Objetivo de la Tarea**

| Aspecto | Agente Agua | Agente Madera |
|---------|-------------|---------------|
| **Objetivo** | Tocar agua | Picar y recolectar madera |
| **Complejidad** | Baja (1 acción: llegar) | Alta (3 acciones: buscar, picar, recoger) |
| **Criterio de éxito** | Tocar bloque de agua | Tener madera en inventario |
| **Tiempo límite** | 60 segundos | 120 segundos |
| **Pasos máximos** | 500 | 800 |

### 2. **Acciones Disponibles**

| Acción | Agente Agua | Agente Madera | Diferencia |
|--------|-------------|---------------|------------|
| `move 1` | ✅ | ✅ | - |
| `turn 1` | ✅ | ✅ | - |
| `turn -1` | ✅ | ✅ | - |
| `jumpmove 1` | ✅ | ✅ | - |
| `attack 1` | ❌ | ✅ | **NUEVO**: Necesario para picar |

**Total acciones**: Agua = 4, Madera = 5

### 3. **Representación del Estado**

#### Agente Agua (6 dimensiones)
```python
(orientación, agua_cerca, nivel_arena, obstaculo_frente, aire_frente, altura)
```

#### Agente Madera (9 dimensiones)
```python
(orientación, madera_cerca, madera_frente, distancia_madera,
 obstaculo_frente, aire_frente, tiene_madera, altura, mirando_madera)
```

**Diferencias clave**:
- ✨ `madera_frente`: Necesario para saber cuándo picar
- ✨ `distancia_madera`: 4 niveles (muy cerca/cerca/lejos/no visible)
- ✨ `tiene_madera`: Para saber si ya completó el objetivo
- ✨ `mirando_madera`: LineOfSight para picar con precisión
- ❌ `nivel_arena`: Solo relevante para agua

**Complejidad del espacio de estados**: 
- Agua: 4 × 2 × 3 × 2 × 2 × 3 = **288 estados** (aprox.)
- Madera: 4 × 2 × 2 × 4 × 2 × 2 × 2 × 3 × 2 = **3,072 estados** (aprox.)

### 4. **Sistema de Recompensas**

#### Recompensas Principales

| Evento | Agente Agua | Agente Madera |
|--------|-------------|---------------|
| **Objetivo logrado** | +100 (tocar agua) | +200 (madera en inventario) |
| **Progreso hacia objetivo** | +10 (más arena) | +50 (picar bloque) |
| | | +30 (picar con madera enfrente) |
| **Proximidad** | +10 (acercarse a arena) | +20 (madera muy cerca) |
| | | +15 (acercarse a madera) |
| | | +2 (mirar madera) |
| **Movimiento exitoso** | +3 | +3 |
| **Exploración** | +5 (área nueva) | +5 (intentar moverse tras girar) |
| | | +2 (variedad de bloques) |

#### Penalizaciones

| Situación | Agente Agua | Agente Madera |
|-----------|-------------|---------------|
| **Costo por acción** | -0.5 | -0.5 |
| **Alejarse de objetivo** | -15 (alejarse de arena) | -15 (alejarse de madera) |
| **Colisión** | -5 | -5 |
| **Loop detectado** | -20 | -20 |
| **Atascado** | -30 | -30 |
| **Acción incorrecta** | - | -10 (picar sin madera) |

**Observación**: El agente de madera tiene más oportunidades de recompensa debido a la naturaleza secuencial de la tarea.

### 5. **Observaciones de Malmo**

| Observación | Agente Agua | Agente Madera | Uso |
|-------------|-------------|---------------|-----|
| `ObservationFromFullStats` | ✅ | ✅ | Posición, salud, etc. |
| `ObservationFromGrid` (5×3×5) | ✅ | ✅ | Bloques cercanos |
| `ObservationFromRay` | ✅ | ✅ | LineOfSight |
| `ObservationFromNearbyEntities` | ✅ | ✅ | Entities cercanas |
| `ObservationFromFullInventory` | ❌ | ✅ | **NUEVO**: Para verificar madera |

### 6. **Recompensas de Malmo (XML)**

#### Agente Agua
```xml
<RewardForTouchingBlockType>
  <Block reward="100.0" type="water" behaviour="onceOnly"/>
  <Block reward="100.0" type="flowing_water" behaviour="onceOnly"/>
</RewardForTouchingBlockType>
```

#### Agente Madera
```xml
<RewardForCollectingItem>
  <Item type="log" reward="50.0"/>
  <Item type="log2" reward="50.0"/>
</RewardForCollectingItem>
```

**Diferencia**: `TouchingBlockType` vs `CollectingItem` - el segundo requiere que el item entre al inventario.

### 7. **Condiciones de Salida (AgentQuit)**

#### Agente Agua
```xml
<AgentQuitFromTouchingBlockType>
  <Block type="water"/>
  <Block type="flowing_water"/>
</AgentQuitFromTouchingBlockType>
```

#### Agente Madera
```xml
<AgentQuitFromCollectingItem>
  <Item type="log" />
  <Item type="log2" />
</AgentQuitFromCollectingItem>
```

### 8. **Mecánicas de Acción**

#### Ejecución del comando `attack`

**Agente Agua**: No aplicable

**Agente Madera**: 
```python
if "attack" in comando:
    time.sleep(0.5)  # Mantener picando
    for _ in range(3):  # Picar 3 veces
        self.agent_host.sendCommand(comando)
        time.sleep(0.2)
```

**Razón**: En Minecraft 1.11.2, romper un bloque requiere múltiples ataques consecutivos.

### 9. **Heurísticas Integradas**

#### Agente Agua
- Sistema anti-stuck (girar 180° si atascado >10 pasos)
- Incentivo para moverse después de girar

#### Agente Madera
- Sistema anti-stuck mejorado (alterna giros y saltos)
- **Heurística de picado**: Si ve madera enfrente Y está mirándola → automáticamente picar
  ```python
  if estado[2] == 1 and estado[8] == 1:  # madera_frente y mirando_madera
      if entorno.pasos_picando < 10:
          comando = "attack 1"
  ```
- Contador de pasos picando para mantener la acción

### 10. **Hiperparámetros Iniciales**

| Parámetro | Agente Agua | Agente Madera | Razón |
|-----------|-------------|---------------|-------|
| `alpha` | 0.1 | 0.1 | - |
| `gamma` | 0.95 | 0.95 | - |
| `epsilon` inicial | 0.3 | 0.4 | Más exploración para madera |
| `epsilon_min` | 0.05 | 0.05 | - |
| `epsilon_decay` | 0.995 | 0.995 | - |

### 11. **Generación del Mundo**

#### Agente Agua
```python
seed = 123456  # Primeros 10 episodios
spawn_radius = 100  # bloques
```

#### Agente Madera
```python
seed = 789123  # Primeros 15 episodios (más tiempo para aprender)
spawn_radius = 150  # bloques (área más grande)
```

**Diferencia**: El agente de madera necesita más tiempo para aprender la secuencia completa (buscar → picar → recoger).

### 12. **Detección de Bloques Objetivo**

#### Agente Agua
```python
BLOQUES_AGUA = ["water", "flowing_water", "stationary_water"]
```

#### Agente Madera
```python
TIPOS_MADERA_BLOQUES = ["log", "log2"]  # Para detectar
TIPOS_MADERA = ["log", "log2", "planks"]  # Para inventario
```

**Nota**: Acepta cualquier variante de madera (roble, abedul, abeto, jungla, acacia, roble oscuro).

### 13. **Verificación de Éxito**

#### Agente Agua
```python
def verificar_agua_encontrada(self, obs, recompensa_malmo=0.0):
    if recompensa_malmo >= 100.0:  # Tocó agua
        return True
```

#### Agente Madera
```python
def verificar_madera_obtenida(self, obs):
    inventario = obs.get("inventory", [])
    for item in inventario:
        if "log" in item.get("type", ""):
            return True  # Tiene madera en inventario
```

**Diferencia clave**: Agua usa recompensa de Malmo, Madera verifica inventario directamente.

### 14. **Tracking de Progreso**

#### Agente Agua
```python
self.arena_previa = 0  # Cantidad de arena visible
```

#### Agente Madera
```python
self.madera_previa = 0  # Bloques de madera visibles
self.madera_inventario_previa = 0  # Cantidad en inventario
self.picando_actualmente = False
self.pasos_picando = 0  # Contador de pasos picando
```

**Observación**: El agente de madera necesita más variables de estado para rastrear la tarea multi-paso.

## 🎯 Conclusión

### Complejidad Incrementada

| Aspecto | Multiplicador |
|---------|---------------|
| Espacio de estados | ×10.7 |
| Acciones | ×1.25 |
| Pasos necesarios | ×1.6 |
| Tiempo límite | ×2 |
| Mecánicas | ×3 (buscar, picar, recoger) |

### Progresión de Dificultad

```
Agua (Simple) → Madera (Intermedio) → Piedra → Hierro → Diamante (Complejo)
```

Cada etapa añade:
- ✅ Más pasos en la secuencia
- ✅ Mayor espacio de estados
- ✅ Requisitos de herramientas (en futuras etapas)
- ✅ Dependencias entre tareas

### Aprendizajes Transferibles

El agente de madera hereda y mejora:
1. ✨ Sistema de navegación (de agua)
2. ✨ Detección de obstáculos (de agua)
3. ✨ Anti-stuck (mejorado)
4. ✨ **NUEVO**: Mecánica de ataque/picado
5. ✨ **NUEVO**: Verificación de inventario
6. ✨ **NUEVO**: Seguimiento de objetivo con LineOfSight

Estos componentes serán reutilizables para piedra, hierro y diamante.

---

**Autor**: Sistema de IA  
**Fecha**: Noviembre 2025  
**Versión Minecraft**: 1.11.2
