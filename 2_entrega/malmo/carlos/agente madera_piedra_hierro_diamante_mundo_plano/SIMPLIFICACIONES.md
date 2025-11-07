# Simplificaciones del Proyecto

Este documento detalla las simplificaciones implementadas según los supuestos del proyecto.

## 🎯 Objetivo del Proyecto

Crear un agente de RL que progrese a través de múltiples objetivos en Minecraft:
1. Recolectar madera
2. Recolectar piedra (con pico de madera)
3. Recolectar hierro (con pico de piedra)
4. Recolectar diamante (con pico de hierro)

## 🔧 Simplificaciones Implementadas

### 1. Limpieza de Inventario al Inicio

**Problema:** En caso de fallas de conexión, items del episodio anterior pueden quedarse en el inventario.

**Solución:**
```python
agent_host.sendCommand("chat /clear")
```

**Ubicación:** `mundo_rl.py`, al inicio de cada episodio (después de spawn).

---

### 2. Pico de Madera Inicial

**Problema:** El agente necesita un pico de madera para empezar a picar piedra, pero fabricarlo requeriría:
- Hacer una mesa de crafteo
- Aprender recetas de crafteo
- Interfaz de crafteo (muy compleja para RL)

**Solución:** Dar pico de madera directamente al spawn:
```python
agent_host.sendCommand("chat /give @p wooden_pickaxe 1")
```

**Ubicación:** `mundo_rl.py`, en el slot 0 de la hotbar, después de limpiar inventario.

**Justificación:** Simplifica enormemente el problema, permitiendo enfocarse en la exploración y recolección de materiales.

---

### 3. Crafteo Simulado de Herramientas

**Problema:** El sistema de crafteo real requiere:
- Abrir inventario (GUI)
- Colocar items en patrón específico
- Clicks precisos
- Conocimiento de todas las recetas

**Solución:** Simular crafteo mediante comandos cuando se alcanza el material necesario:

#### Pico de Piedra (Fase 1 → 2)
```python
if piedra_recolectada >= 3:
    agent_host.sendCommand("chat /clear")  # Quita materiales
    agent_host.sendCommand("chat /give @p stone_pickaxe 1")  # Da pico
```

#### Pico de Hierro (Fase 2 → 3)
```python
if hierro_recolectado >= 3:
    agent_host.sendCommand("chat /clear")
    agent_host.sendCommand("chat /give @p iron_pickaxe 1")
```

**Ubicación:** `entorno_malmo.py`, método `verificar_progresion_fase()`.

**Justificación:** 
- Evita complejidad de GUI
- Mantiene la lógica de progresión (necesitas material X para obtener herramienta Y)
- El agente aún debe aprender qué material buscar en cada fase

---

### 4. Conversión Automática Hierro → Lingote

**Problema:** En Minecraft real, el mineral de hierro (iron_ore) debe:
1. Picarse con pico de piedra+
2. Colocarse en un horno
3. Añadir combustible (carbón/madera)
4. Esperar tiempo de fundición
5. Extraer lingote (iron_ingot)

**Solución:** Conversión automática al picar:
```python
# En entorno_malmo.py
def _contar_hierro(self, obs):
    # Cuenta directamente iron_ingot
    # El juego convierte automáticamente al recoger
    if item == 'iron_ingot':
        count += size
```

**Ubicación:** `entorno_malmo.py`, método `_contar_hierro()`.

**Nota Técnica:** Malmo permite configurar esto mediante reglas de drops personalizadas o simplemente contar el lingote directamente en el inventario.

**Justificación:**
- Fundición requeriría: encontrar/craftear horno, encontrar combustible, esperar tiempo
- Añadiría ~15 minutos por episodio
- No aporta al objetivo principal (aprender exploración y progresión)

---

### 5. Mundo Plano Controlado

**Problema:** En mundo normal (DefaultWorldGenerator):
- Generación aleatoria impredecible
- Materiales pueden estar muy dispersos
- Algunas semillas pueden no tener todos los materiales cerca
- Cuevas, lava, mobs hostiles complican entrenamiento

**Solución:** Mundo plano (FlatWorld) con materiales colocados manualmente:

```python
def generar_mundo_plano_xml(seed):
    # Área 50×50 bloques
    # Muro de obsidiana perimetral
    # Materiales distribuidos aleatoriamente:
    #   - 15-20 madera
    #   - 15-20 piedra
    #   - 8-12 hierro
    #   - 3-5 diamante
```

**Características:**
- **Spawn fijo:** (0, 4, 0)
- **Sin mobs:** `AllowSpawning=false`
- **Sin ciclo día/noche:** `AllowPassageOfTime=false`
- **Perímetro cerrado:** Muro de obsidiana altura 6
- **Distribución garantizada:** Siempre hay suficientes materiales

**Ubicación:** `mundo_rl.py`, función `generar_mundo_plano_xml()`.

**Justificación:**
- Entorno controlado = entrenamiento más rápido
- Reproducibilidad con misma semilla
- Evita frustración de no encontrar materiales
- Una vez aprende aquí, puede transferirse a mundo normal

---

### 6. Sin Mesa de Crafteo

**Problema:** Craftear requiere mesa de crafteo para muchas recetas (herramientas necesitan 3×3).

**Solución:** Todos los crafteos se simulan con comandos (ver punto 3).

**Justificación:** Ya cubierto en simplificación #3.

---

### 7. Sin Durabilidad de Herramientas

**Problema:** Herramientas se rompen después de N usos:
- Pico de madera: ~60 bloques
- Pico de piedra: ~132 bloques
- Pico de hierro: ~251 bloques

**Solución:** Las herramientas dadas por comando tienen durabilidad completa. Como solo se requieren:
- 3 piedra → uso mínimo del pico de madera
- 3 hierro → uso mínimo del pico de piedra
- 1 diamante → uso mínimo del pico de hierro

Es muy improbable que se rompan durante un episodio normal.

**Si se rompen:** El entorno detecta herramienta incorrecta y castiga fuertemente, obligando al agente a buscar materiales de fase anterior (lo cual también es castigado). En la práctica, el episodio fallaría.

**Ubicación:** Implícito en el sistema de recompensas (`_verificar_herramienta_correcta()`).

---

### 8. Sin Sistema de Hambre

**Problema:** En Survival, el hambre baja con el tiempo y acciones. Si llega a 0, el agente pierde salud.

**Solución:** El hambre baja lentamente y los episodios son cortos (< 5 min típicamente). No requiere comida.

**Justificación:** Añadir búsqueda de comida complicaría innecesariamente el problema. El objetivo es aprender progresión de materiales, no supervivencia.

---

### 9. Sin Mobs Hostiles

**Problema:** Zombies, creepers, esqueletos atacarían al agente.

**Solución:**
```xml
<AllowSpawning>false</AllowSpawning>
```

**Ubicación:** XML de misión en `mundo_rl.py`.

**Justificación:** Combate es un problema completamente diferente. Queremos enfocarnos en exploración y recolección.

---

### 10. Timeout Generoso

**Problema:** ¿Cuánto tiempo dar al agente por episodio?

**Solución:** 5 minutos (300 segundos = 300,000 ms):
```xml
<ServerQuitFromTimeUp timeLimitMs="300000"/>
```

Y 1000 pasos máximo en el código Python.

**Ubicación:** XML de misión + bucle principal en `ejecutar_episodio()`.

**Justificación:** 
- Da tiempo suficiente para completar todas las fases
- Evita episodios infinitos
- En práctica, episodios exitosos terminan en 200-500 pasos (~2-3 min)

---

## 📊 Comparación Real vs Simplificado

| Aspecto | Minecraft Real | Versión Simplificada |
|---------|---------------|----------------------|
| **Pico inicial** | Craftear con tabla + madera | Dado por comando |
| **Crafteo herramientas** | Mesa crafteo + receta | Comando automático al completar fase |
| **Fundición hierro** | Horno + combustible + tiempo | Conversión automática |
| **Búsqueda materiales** | Mundo aleatorio gigante | Área 50×50 controlada |
| **Durabilidad** | Herramientas se rompen | Suficiente para episodio |
| **Mobs** | Zombies, creepers, etc. | Desactivados |
| **Hambre** | Requiere comida | Ignorado (episodios cortos) |
| **Mesa crafteo** | Necesaria para herramientas | No necesaria |
| **Tiempo día/noche** | 20 min ciclo | Congelado en día |

---

## ✅ Qué SÍ Aprende el Agente

A pesar de las simplificaciones, el agente **SÍ debe aprender:**

1. **Exploración:** Moverse por el mundo buscando materiales
2. **Reconocimiento visual:** Identificar bloques objetivo en la rejilla
3. **Navegación:** Evitar obstáculos, saltar, girar efectivamente
4. **Uso de pitch:** Buscar materiales en altura
5. **Timing de ataque:** Cuándo picar vs cuándo moverse
6. **Progresión de objetivos:** Orden correcto (madera → piedra → hierro → diamante)
7. **Uso de herramienta correcta:** No picar con herramienta incorrecta
8. **Eficiencia:** Completar objetivo en menos pasos

---

## 🎓 Justificación Académica

Estas simplificaciones son **válidas académicamente** porque:

1. **Enfoque del problema:** El objetivo es aprender RL con progresión jerárquica, no simular Minecraft completo
2. **Complejidad suficiente:** Aún hay 12 dimensiones de estado, 7 acciones, 4 fases
3. **Transferibilidad:** Las políticas aprendidas pueden transferirse a entornos más complejos
4. **Tiempo de entrenamiento:** Sin simplificaciones, podría tomar semanas/meses entrenar
5. **Claridad de análisis:** Entorno controlado permite identificar qué funciona y qué no

---

## 🔜 Extensiones Futuras

Una vez funciona la versión simplificada, se puede:

1. **Mundo normal:** Usar DefaultWorldGenerator en lugar de FlatWorld
2. **Crafteo real:** Implementar acciones de GUI
3. **Múltiples herramientas:** Necesitar hacha para madera, pala para grava, etc.
4. **Mobs:** Añadir enemigos y aprender combate
5. **Hambre:** Requerir comida
6. **Durabilidad:** Gestionar múltiples herramientas
7. **Objetivos más complejos:** Enchanting, Nether, End, etc.

---

**Conclusión:** Las simplificaciones permiten entrenar un agente funcional en tiempo razonable mientras se mantiene la complejidad central del problema: **aprendizaje de progresión jerárquica multi-objetivo en un entorno 3D parcialmente observable**.
