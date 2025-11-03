# Cambios Realizados - Corrección de Movimiento y Configuración

## 🔧 Problemas Identificados y Solucionados

### 1. **Agente Mirando al Suelo**

**Problema**: El agente estaba mirando continuamente hacia abajo.

**Causa**: El pitch estaba configurado en 30° (mirando hacia abajo).

**Solución**:
```python
# ANTES
<Placement x="{spawn_x}" y="64" z="{spawn_z}" pitch="30" yaw="0"/>

# DESPUÉS
<Placement x="{spawn_x}" y="64" z="{spawn_z}" pitch="0" yaw="0"/>
```

- **pitch=0**: Agente mira al frente horizontal
- **pitch=30**: Agente mira 30° hacia abajo
- **pitch=-30**: Agente miraría 30° hacia arriba

### 2. **Comandos de Movimiento No Funcionaban**

**Problemas Múltiples**:

#### a) Conflicto entre tipos de comandos
```xml
<!-- ANTES: Ambos activados (causa conflictos) -->
<DiscreteMovementCommands/>
<ContinuousMovementCommands turnSpeedDegs="180"/>

<!-- DESPUÉS: Solo comandos discretos -->
<DiscreteMovementCommands/>
```

**Explicación**: 
- `DiscreteMovementCommands`: Comandos como "move 1", "turn 1" (un bloque/90°)
- `ContinuousMovementCommands`: Comandos como "move 0.5", "turn 45" (valores continuos)
- Tener ambos activos causa conflictos en la interpretación de comandos

#### b) Tiempo insuficiente para ejecutar comandos

```python
# ANTES
def ejecutar_accion(self, comando, duracion=0.1):
    self.agent_host.sendCommand(comando)
    time.sleep(duracion)  # Solo 0.1 segundos

# DESPUÉS
def ejecutar_accion(self, comando, duracion=0.5):
    self.agent_host.sendCommand(comando)
    time.sleep(duracion)  # 0.5 segundos (5x más tiempo)
```

**Explicación**: Los comandos discretos necesitan tiempo para completarse:
- `move 1`: El agente debe caminar un bloque completo (~0.4-0.5 seg)
- `turn 1`: El agente debe girar 90° (~0.3-0.4 seg)
- Con 0.1 seg, el comando se enviaba pero no se completaba

#### c) Pausa insuficiente entre acciones

```python
# ANTES
time.sleep(0.05)  # Entre iteraciones del bucle

# DESPUÉS
time.sleep(0.1)  # 2x más tiempo
```

### 3. **Configuración Hardcodeada**

**Problema**: IP, puerto y semilla estaban en el código.

**Solución**: Leer desde archivo `.config`

```python
def cargar_configuracion():
    """Carga la configuración desde el archivo .config"""
    config = {
        'ip': '127.0.0.1',
        'puerto': 10001,
        'seed': 123456
    }
    
    # Buscar .config en directorio padre (malmo/)
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        '.config'
    )
    
    with open(config_path, 'r') as f:
        for linea in f:
            if '=' in linea and not linea.startswith('#'):
                clave, valor = linea.split('=', 1)
                clave = clave.strip()
                valor = valor.strip().strip('"')
                
                if clave == 'carlos':
                    config['ip'] = valor
                elif clave == 'seed':
                    config['seed'] = int(valor)
    
    return config
```

**Uso**:
```python
config = cargar_configuracion()
client_pool.add(Malmo.ClientInfo(config['ip'], config['puerto']))
seed = config['seed']
```

### 4. **Semilla No Fija Durante Entrenamiento**

**Problema**: Después de 15 episodios, usaba semilla aleatoria (None).

**Solución**:
```python
# ANTES
if episodio < 15:
    seed = 789123
else:
    seed = None  # Aleatorio

# DESPUÉS
seed = SEED_FIJA  # Siempre la misma del .config
```

**Ventaja**: Mundo consistente para comparar aprendizaje entre entrenamientos.

## 📊 Resumen de Cambios en Archivos

### `mundo_rl.py`

| Línea | Cambio | Razón |
|-------|--------|-------|
| 7-70 | Añadida función `cargar_configuracion()` | Leer .config |
| 35 | `pitch="30"` → `pitch="0"` | Mirar al frente |
| 105-106 | Eliminada línea `ContinuousMovementCommands` | Evitar conflictos |
| 250 | Cargar config al inicio | Usar IP/puerto/seed del .config |
| 289 | `seed = SEED_FIJA` (siempre) | Mundo consistente |
| 242 | `duracion=0.1` → `duracion=0.5` | Más tiempo por comando |
| 273 | `time.sleep(0.05)` → `time.sleep(0.1)` | Más pausa entre iteraciones |

### `entorno_malmo.py`

| Línea | Cambio | Razón |
|-------|--------|-------|
| 244 | `duracion=0.1` → `duracion=0.5` (default) | Más tiempo por defecto |
| 253 | `time.sleep(0.5)` → `time.sleep(0.8)` | Más tiempo para picar |
| 256 | `time.sleep(0.2)` → `time.sleep(0.3)` | Entre ataques |

### Nuevo Archivo: `test_movimiento.py`

Script de prueba para verificar que los movimientos funcionan correctamente.

**Uso**:
```bash
python test_movimiento.py
```

**Qué hace**:
1. Lee configuración de `.config`
2. Inicia misión simple
3. Ejecuta secuencia de comandos: move, turn, jumpmove, attack
4. Muestra posición y orientación después de cada comando

## 🧪 Cómo Verificar que Funciona

### 1. Ejecutar Script de Prueba

```bash
cd "/home/carlos/Seminario_1_proyecto/2_entrega/malmo/carlos/agente madera"
python test_movimiento.py
```

**Verifica**:
- ✅ Agente se mueve hacia adelante con `move 1`
- ✅ Agente gira 90° con `turn 1`
- ✅ Agente salta y avanza con `jumpmove 1`
- ✅ Pitch está en 0° (mirando al frente)
- ✅ Posición X, Y, Z cambia después de mover

### 2. Ejecutar Entrenamiento

```bash
python mundo_rl.py
```

**Observa**:
- La posición (X, Y, Z) debe cambiar entre pasos
- El agente no debe estar saltando en el mismo lugar
- Debe mirar al frente (pitch cercano a 0°)

### 3. En Minecraft

Observa directamente en el juego:
- El agente camina cuando ejecuta `move 1`
- Gira cuando ejecuta `turn 1` o `turn -1`
- Salta y avanza con `jumpmove 1`
- Su cabeza mira al horizonte, no al suelo

## 📝 Formato del Archivo .config

```ini
carlos="127.0.0.1"
jonathan="172.28.224.1"
matias="pendiente"
seed=123456
```

**Notas**:
- `carlos`: IP del servidor Malmo para el usuario carlos
- `seed`: Semilla fija para generación del mundo
- El puerto siempre es 10001 (estándar de Malmo)

## 🔍 Debugging

Si los problemas persisten:

### Verificar logs de Malmo
```bash
# En la terminal donde corre Minecraft
# Busca mensajes como:
# "Received command: move 1"
# "Command executed successfully"
```

### Aumentar verbose en entrenamiento
```python
stats = ejecutar_episodio(
    agent_host, agente, entorno, 
    max_pasos=800, 
    verbose=True  # Cambiar de (episodio % 5 == 0) a True
)
```

### Verificar que DiscreteMovementCommands esté solo
```bash
grep -A2 "COMANDOS" mundo_rl.py
# Debe mostrar solo DiscreteMovementCommands
```

## 🎯 Próximos Pasos

1. **Ejecutar test_movimiento.py** para confirmar que los comandos funcionan
2. **Entrenar 10 episodios** y verificar que las posiciones cambian
3. **Revisar métricas** con `python utils.py resumen`
4. Si funciona bien, continuar entrenamiento completo (50+ episodios)

## 📌 Valores de Timing Recomendados

| Acción | Tiempo (seg) | Razón |
|--------|--------------|-------|
| `move 1` | 0.5 | Caminar 1 bloque |
| `turn 1/turn -1` | 0.5 | Girar 90° |
| `jumpmove 1` | 0.5 | Saltar y avanzar |
| `attack 1` (inicial) | 0.8 | Empezar a picar |
| `attack 1` (repetir) | 0.3 | Continuar picando |
| Entre iteraciones | 0.1 | Procesar observaciones |

**Total por paso**: ~0.6-0.9 segundos (antes era ~0.15 seg)

## ✅ Checklist de Verificación

- [x] pitch=0 en XML
- [x] Solo DiscreteMovementCommands
- [x] duracion=0.5 en ejecutar_accion
- [x] Configuración desde .config
- [x] Semilla fija durante todo el entrenamiento
- [x] Script de prueba test_movimiento.py creado
- [ ] Ejecutar test_movimiento.py y verificar movimiento
- [ ] Entrenar y confirmar que posiciones cambian
- [ ] Validar que el agente no está atascado en un lugar

---

**Fecha**: Noviembre 3, 2025  
**Archivos modificados**: `mundo_rl.py`, `entorno_malmo.py`  
**Archivos creados**: `test_movimiento.py`, `CAMBIOS_MOVIMIENTO.md`
