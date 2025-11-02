# 🎮 Ejemplos de Uso - Sistema de Recolección de Madera

Este documento contiene ejemplos prácticos de cómo usar el sistema.

---

## 📖 Tabla de Contenidos

1. [Entrenamiento Básico](#1-entrenamiento-básico)
2. [Continuar Entrenamiento](#2-continuar-entrenamiento)
3. [Ajustar Hiperparámetros](#3-ajustar-hiperparámetros)
4. [Visualización de Resultados](#4-visualización-de-resultados)
5. [Evaluación del Agente](#5-evaluación-del-agente)
6. [Debugging y Troubleshooting](#6-debugging-y-troubleshooting)

---

## 1. Entrenamiento Básico

### Setup Inicial

```bash
# 1. Verificar configuración
python configurar.py

# 2. Iniciar Minecraft con Malmo
# (desde directorio de Malmo)
./launchClient.sh -port 10000

# 3. En otra terminal, entrenar el agente
cd /ruta/a/carlos/
python mundo2v2.py
```

### Salida Esperada

```
🚀 INICIANDO ENTRENAMIENTO: RECOLECCIÓN DE MADERA
======================================================================
📋 Objetivo: Entrenar agente para conseguir 3 bloques de madera
🪓 Herramienta inicial: Pico de madera en hotbar
======================================================================

📡 Iniciando misión (episodio 1/30)...
✓ Misión iniciada

==================================================================
🎮 EPISODIO #1
   Epsilon: 0.4000 (exploración)
==================================================================
   Paso   0 | Pos: (  0.5,  64.0,   0.5) | Mirando: air          | Madera: 0/3 | R:  -0.50
   Paso  30 | Pos: (  5.2,  64.0,  -3.1) | Mirando: log          | Madera: 0/3 | R: +15.00
   🎉 ¡+1 MADERA CONSEGUIDA! Total: 1/3
   ...
```

---

## 2. Continuar Entrenamiento

Si ya tienes un modelo entrenado, el sistema automáticamente lo carga:

```python
# En mundo2v2.py, el modelo se carga automáticamente:
agente.cargar_modelo("modelo_agente_madera.pkl")
```

### Entrenar 20 episodios adicionales:

```python
# Editar mundo2v2.py
NUM_EPISODIOS = 20  # En lugar de 30

# Ejecutar
python mundo2v2.py
```

**Salida**:
```
✓ Modelo cargado desde: modelo_agente_madera.pkl
  Episodios previos: 30
  Epsilon actual: 0.1234

📡 Iniciando misión (episodio 31/50)...
```

---

## 3. Ajustar Hiperparámetros

### Escenario: El agente no explora suficiente

**Problema**: Se queda atascado en las mismas estrategias

**Solución**: Aumentar exploración

```python
# En mundo2v2.py, función entrenar()
agente = AgenteMaderaQLearning(
    alpha=0.15,
    gamma=0.95,
    epsilon=0.6,          # ⬆️ Aumentar de 0.4 a 0.6
    epsilon_decay=0.990   # ⬇️ Decaer más lento (de 0.995)
)
```

### Escenario: Aprende muy lento

**Problema**: Muchos episodios sin mejorar

**Solución**: Aumentar tasa de aprendizaje

```python
agente = AgenteMaderaQLearning(
    alpha=0.25,           # ⬆️ Aumentar de 0.15 a 0.25
    gamma=0.95,
    epsilon=0.4,
    epsilon_decay=0.995
)
```

### Escenario: Muy orientado al corto plazo

**Problema**: No planifica, solo reacciona

**Solución**: Aumentar gamma (visión a futuro)

```python
agente = AgenteMaderaQLearning(
    alpha=0.15,
    gamma=0.98,           # ⬆️ Aumentar de 0.95 a 0.98
    epsilon=0.4,
    epsilon_decay=0.995
)
```

---

## 4. Visualización de Resultados

### Generar Gráficos

```bash
python utils_madera.py graficar
```

**Salida**: Crea `analisis_entrenamiento_madera.png` con 4 gráficos:
- Recompensas por episodio
- Madera recolectada (barras verdes/rojas)
- Pasos por episodio
- Decaimiento de epsilon

### Analizar Tabla Q

```bash
python utils_madera.py analizar
```

**Salida Ejemplo**:
```
================================================================================
📊 ANÁLISIS DE LA TABLA Q - RECOLECCIÓN DE MADERA
================================================================================
Total de estados visitados: 347

🏆 Top 15 estados con mayor valor Q:

#    Estado                                            Mejor Acción     Max Q
-------------------------------------------------------------------------------------
1    (1, 2, 1, 1, 0, 0, 2)                            attack 1         245.67
2    (0, 2, 0, 1, 0, 0, 2)                            attack 1         198.34
3    (2, 1, 1, 0, 1, 0, 1)                            move 1            89.21
...

================================================================================
📈 ESTADÍSTICAS DE VALORES Q
================================================================================
Valor Q promedio: 12.4567
Valor Q máximo: 245.6700
Valor Q mínimo: -45.2300
Desviación estándar: 34.5678

================================================================================
🎯 DISTRIBUCIÓN DE ACCIONES PREFERIDAS
================================================================================
move 1         :   125 ( 36.0%) ██████████████████
turn 1         :    78 ( 22.5%) ███████████
turn -1        :    65 ( 18.7%) █████████
jumpmove 1     :    34 (  9.8%) ████
attack 1       :    30 (  8.6%) ████
strafe 1       :    10 (  2.9%) █
strafe -1      :     5 (  1.4%)
```

---

## 5. Evaluación del Agente

### Ejecutar en Modo Greedy (sin exploración)

Crear script `evaluar.py`:

```python
import sys
import time
import MalmoPython as Malmo
from agente_madera_rl import AgenteMaderaQLearning
from entorno_madera import EntornoMadera
from utils_madera import simular_episodio_greedy
from mundo2v2 import obtener_mision_xml

# Cargar agente entrenado
agente = AgenteMaderaQLearning()
agente.cargar_modelo("modelo_agente_madera.pkl")

# Inicializar Malmo
agent_host = Malmo.AgentHost()
entorno = EntornoMadera(agent_host)

# Configurar misión
mision_xml = obtener_mision_xml(seed=42)
mission = Malmo.MissionSpec(mision_xml, True)
mission_record = Malmo.MissionRecordSpec()

client_pool = Malmo.ClientPool()
client_pool.add(Malmo.ClientInfo("127.0.0.1", 10000))

# Iniciar misión
agent_host.startMission(mission, client_pool, mission_record, 0, "Eval")

world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    time.sleep(0.1)
    world_state = agent_host.getWorldState()

# Simular episodio
stats = simular_episodio_greedy(agente, entorno, agent_host, max_pasos=500)

print(f"\n🏆 RESULTADO FINAL:")
print(f"   Madera: {stats['madera']}/3")
print(f"   Éxito: {stats['exito']}")
print(f"   Pasos: {stats['pasos']}")
```

**Ejecutar**:
```bash
python evaluar.py
```

---

## 6. Debugging y Troubleshooting

### Problema: "Connection refused"

```bash
# Verificar que Minecraft esté corriendo
netstat -an | grep 10000

# Debería mostrar:
# tcp4  0  0  *.10000  *.*  LISTEN
```

**Solución**: Reiniciar Minecraft con Malmo

---

### Problema: El agente solo gira

**Verificar tabla Q**:
```bash
python utils_madera.py analizar
```

Si `turn 1` y `turn -1` dominan (>60%), el agente está atascado.

**Solución**:
```python
# Penalizar más los giros consecutivos
# En entorno_madera.py, función calcular_recompensa()

if all("turn" in a for a in ultimas_6):
    recompensa -= 30.0  # Aumentar de 20.0 a 30.0
```

---

### Problema: No encuentra árboles

**Verificar seed del mundo**:
```python
# En mundo2v2.py, función obtener_mision_xml()

def obtener_mision_xml(seed=42):  # Probar seeds: 123, 456, 789
```

**O cambiar spawn**:
```xml
<Placement x="100" y="64" z="-50" pitch="0" yaw="0"/>
```

---

### Problema: Recompensas muy negativas

**Verificar logs del entrenamiento**:
```python
# En mundo2v2.py, ejecutar_episodio()
# Cambiar verbose=True para TODOS los episodios

stats = ejecutar_episodio(..., verbose=True)
```

**Analizar**:
- ¿Se mueve? → Si no, aumentar recompensa por movimiento
- ¿Pica aire? → Penalizar menos al inicio (exploración)
- ¿Loops? → Sistema anti-stuck está funcionando

---

### Problema: Modelo no mejora después de 20 episodios

**Verificar convergencia**:
```bash
python utils_madera.py graficar
```

Si recompensa se estanca:

1. **Reset tabla Q** (empezar de cero):
   ```bash
   rm modelo_agente_madera.pkl
   python mundo2v2.py
   ```

2. **Cambiar estructura de estado**:
   ```python
   # En agente_madera_rl.py, modificar obtener_estado_discretizado()
   # Por ejemplo, agregar más información de hojas
   ```

3. **Ajustar recompensas**:
   ```python
   # En entorno_madera.py
   # Aumentar recompensa por picar madera:
   recompensa += 50.0  # Aumentar de 30.0
   ```

---

## 💡 Tips Avanzados

### Entrenamiento Incremental

```python
# Fase 1: Aprender a navegar (10 episodios)
agente = AgenteMaderaQLearning(epsilon=0.8)  # Mucha exploración

# Fase 2: Aprender a picar (20 episodios)
agente.epsilon = 0.3  # Menos exploración

# Fase 3: Optimizar (20 episodios)
agente.epsilon = 0.1  # Casi pura explotación
```

### Curriculum Learning

```python
# Episodios 1-10: Spawn cerca de árboles
spawn_x, spawn_z = 5, 5

# Episodios 11-20: Spawn aleatorio
spawn_x = random.uniform(-50, 50)
spawn_z = random.uniform(-50, 50)

# Episodios 21-30: Diferentes mundos
seed = random.randint(1, 10000)
```

### Análisis de Trayectorias

```python
from utils_madera import simular_episodio_greedy

stats = simular_episodio_greedy(agente, entorno, agent_host)

# Visualizar trayectoria
import matplotlib.pyplot as plt
trayectoria = stats['trayectoria']
x, y, z = zip(*trayectoria)

plt.figure(figsize=(10, 10))
plt.plot(x, z, 'b-', alpha=0.5)
plt.scatter(x[0], z[0], c='green', s=100, label='Inicio')
plt.scatter(x[-1], z[-1], c='red', s=100, label='Final')
plt.xlabel('X')
plt.ylabel('Z')
plt.title('Trayectoria del Agente')
plt.legend()
plt.grid()
plt.savefig('trayectoria.png')
```

---

## 🎯 Experimentos Sugeridos

### Experimento 1: Comparar estrategias de exploración
```python
# Entrenar 3 agentes con diferentes epsilons
for eps in [0.2, 0.4, 0.6]:
    agente = AgenteMaderaQLearning(epsilon=eps)
    entrenar(modelo_path=f"modelo_eps_{eps}.pkl")
```

### Experimento 2: Impacto del tamaño del grid
```python
# Modificar XML para usar grids de diferente tamaño
# 3×3×3, 5×5×5, 7×7×7
# Comparar velocidad de aprendizaje
```

### Experimento 3: Recompensas sparse vs dense
```python
# Versión A: Solo recompensa final (+500 por 3 maderas)
# Versión B: Recompensas intermedias (sistema actual)
# Comparar convergencia
```

---

**¡Experimenta y diviértete entrenando tu agente! 🤖🪓**
