# Guía de Troubleshooting

Soluciones a problemas comunes del agente progresivo.

## 🔌 Problemas de Conexión

### Error: "Failed to connect to Minecraft"

**Síntomas:**
```
❌ Error al iniciar misión: Failed to connect
```

**Soluciones:**
1. Verifica que Minecraft 1.11.2 esté corriendo
2. Verifica que el mod Malmo esté cargado (aparece en pantalla principal)
3. Verifica que el puerto 10000 esté disponible:
   ```bash
   netstat -tuln | grep 10000
   ```
4. Reinicia Minecraft y espera 10-15 segundos antes de ejecutar el script

---

### Error: "Mission already running"

**Síntomas:**
```
RuntimeError: Mission already running
```

**Soluciones:**
1. Espera a que termine el episodio anterior (o cierra Minecraft)
2. Añade delay entre episodios (ya está implementado: 2 segundos)
3. Si persiste, reinicia Minecraft

---

## 🐍 Problemas de Python

### Error: "No module named 'MalmoPython'"

**Síntomas:**
```python
ImportError: No module named 'MalmoPython'
```

**Soluciones:**
1. Activa el entorno virtual de Malmo:
   ```bash
   source ~/malmoenv/bin/activate
   ```
2. Verifica la instalación:
   ```bash
   python3 -c "import MalmoPython; print('OK')"
   ```
3. Añade Malmo al PYTHONPATH:
   ```bash
   export PYTHONPATH=$PYTHONPATH:/path/to/Malmo/Python_Examples
   ```

---

### Error: "No module named 'agente_rl'"

**Síntomas:**
```python
ImportError: No module named 'agente_rl'
```

**Soluciones:**
1. Verifica que estás en el directorio correcto:
   ```bash
   cd "agente madera_piedra_hierro_diamante_mundo_plano"
   pwd
   ```
2. Lista los archivos:
   ```bash
   ls -la *.py
   ```
   Deberías ver: `agente_rl.py`, `entorno_malmo.py`, `mundo_rl.py`

---

## 🎮 Problemas de Entrenamiento

### Agente no encuentra materiales

**Síntomas:**
- Episodios timeout sin completar ninguna fase
- Recompensa muy baja (<100)
- Agente gira en círculos

**Diagnóstico:**
```python
# Ejecuta con 1 episodio y observa los mensajes
python3 mundo_rl.py 1
```

Verifica en la salida:
- ¿Se generó el mundo? (debe mostrar cantidad de materiales)
- ¿El agente detecta materiales cerca? (mensajes de proximidad)

**Soluciones:**
1. Aumenta cantidad de materiales en `mundo_rl.py`:
   ```python
   num_madera = random.randint(25, 30)  # Era 15-20
   num_piedra = random.randint(25, 30)
   ```

2. Reduce el área de búsqueda:
   ```python
   radio = 20  # Era 25 (área 40x40 en vez de 50x50)
   ```

3. Aumenta epsilon inicial (más exploración):
   ```python
   agente = AgenteQLearningProgresivo(epsilon=0.6)  # Era 0.4
   ```

---

### Agente se queda atascado

**Síntomas:**
- Mismo mensaje de posición repetido
- "Paso X" no avanza
- Anti-stuck no funciona

**Soluciones:**
1. Reduce umbral anti-stuck en `mundo_rl.py`:
   ```python
   if pasos_sin_movimiento_consecutivos > 10:  # Era 15
   ```

2. Añade más variedad al anti-stuck:
   ```python
   if pasos_sin_movimiento_consecutivos > 10:
       # Giro aleatorio
       angulo = random.choice([1, -1])
       agent_host.sendCommand(f"turn {angulo}")
       time.sleep(0.1)
       agent_host.sendCommand("jumpmove 1")
   ```

3. Verifica que el spawn no esté bloqueado por el muro:
   - Spawn debe estar en (0, 4, 0)
   - Muro debe empezar en ±25, no ±2

---

### Fase 0 nunca se completa

**Síntomas:**
- Agente obtiene 1-2 madera pero no más
- Se queda buscando indefinidamente
- Timeout en todos los episodios

**Diagnóstico:**
Verifica mensajes:
```
🌲 +1 MADERA obtenida! (Total: 1/3) [+200.0]
🌲 +1 MADERA obtenida! (Total: 2/3) [+200.0]
🌲 +1 MADERA obtenida! (Total: 3/3) [+200.0]  # ¿Aparece este?
```

**Soluciones:**
1. Verifica detección de inventario en `entorno_malmo.py`:
   ```python
   def _contar_madera(self, obs):
       count = 0
       for slot in range(45):
           item_key = f'InventorySlot_{slot}_item'
           size_key = f'InventorySlot_{slot}_size'
           if item_key in obs:
               item = obs[item_key]
               size = obs.get(size_key, 1)
               if item in materiales_madera:
                   count += size
                   print(f"DEBUG: Slot {slot} = {item} x{size}")  # DEBUG
       return count
   ```

2. Verifica que el agente está picando (no solo tocando):
   - Debe aparecer "Picando madera exitosamente"
   - Si no aparece, aumenta recompensa por atacar madera

---

### Progresión de fases no funciona

**Síntomas:**
- Agente obtiene 3 madera pero no avanza a fase piedra
- Crafteo simulado no se ejecuta

**Diagnóstico:**
Busca en la salida:
```
============================================================
🌲 FASE MADERA COMPLETADA!
   Madera recolectada: 3/3
   → Avanzando a fase PIEDRA
============================================================
```

Si **NO** aparece, verifica:

1. `entorno_malmo.py`, método `verificar_progresion_fase()`:
   ```python
   if self.fase_actual == 0:
       if self.materiales_recolectados['madera'] >= 3:
           print("\nDEBUG: Entrando en transición fase 0->1")
           print(f"DEBUG: Madera actual = {self.materiales_recolectados['madera']}")
   ```

2. Verifica que se está llamando en `mundo_rl.py`:
   ```python
   cambio_fase = entorno.verificar_progresion_fase(obs_nueva)
   if cambio_fase:
       print("DEBUG: Cambio de fase detectado")
   ```

---

### Herramienta incorrecta no castiga

**Síntomas:**
- Agente intenta picar hierro con pico de madera
- No recibe castigo fuerte
- No aprende a usar herramienta correcta

**Soluciones:**
1. Aumenta castigos en `entorno_malmo.py`:
   ```python
   castigos_herramienta = {
       1: -80.0,   # Era -40
       2: -100.0,  # Era -50
       3: -200.0,  # Era -100
   }
   ```

2. Verifica detección de herramienta:
   ```python
   def _verificar_herramienta_correcta(self, obs, fase):
       # Añadir debug
       for slot in range(9):
           item_key = f'InventorySlot_{slot}_item'
           if item_key in obs:
               print(f"DEBUG: Hotbar slot {slot} = {obs[item_key]}")
       # ... resto del código
   ```

---

## 📊 Problemas de Aprendizaje

### Epsilon no decae

**Síntomas:**
- Después de 50 episodios, epsilon sigue en 0.4
- Agente no mejora (siempre aleatorio)

**Soluciones:**
1. Verifica que se llama `decaer_epsilon()` en `mundo_rl.py`:
   ```python
   agente.decaer_epsilon()  # Después de cada episodio
   ```

2. Verifica decay rate:
   ```python
   # En agente_rl.py
   epsilon_decay=0.995  # Si es 1.0, nunca decae
   ```

3. Monitorea epsilon:
   ```python
   print(f"Epsilon episodio {episodio}: {agente.epsilon:.4f}")
   ```

---

### Q-tables no se guardan

**Síntomas:**
- Modelo no persiste entre ejecuciones
- Siempre empieza desde cero

**Soluciones:**
1. Verifica llamada a `guardar_modelo()`:
   ```python
   if episodio % 10 == 0:
       agente.guardar_modelo('modelo_progresivo.pkl')
   ```

2. Verifica permisos de escritura:
   ```bash
   touch modelo_progresivo.pkl
   ls -la modelo_progresivo.pkl
   ```

3. Añade logging:
   ```python
   import os
   print(f"Guardando en: {os.path.abspath('modelo_progresivo.pkl')}")
   ```

---

### Modelo cargado no mejora rendimiento

**Síntomas:**
- `ejecutar_modelo.py` tiene mismo rendimiento que episodio 1
- Epsilon=0 pero sigue aleatorio

**Diagnóstico:**
```python
python3 -c "
import pickle
with open('modelo_progresivo.pkl', 'rb') as f:
    m = pickle.load(f)
    for fase, qtable in m['q_tables'].items():
        print(f'Fase {fase}: {len(qtable)} estados')
"
```

Si todos muestran 0 estados → modelo vacío

**Soluciones:**
1. Entrena al menos 50 episodios antes de ejecutar
2. Verifica que `actualizar_q()` se llama:
   ```python
   agente.actualizar_q(estado, accion, recompensa, siguiente_estado, fase_actual)
   print(f"DEBUG: Q actualizada para fase {fase_actual}")
   ```

---

## 💾 Problemas de Rendimiento

### Entrenamiento muy lento

**Síntomas:**
- <1 episodio por minuto
- CPU al 100%

**Soluciones:**
1. Reduce `time.sleep()` en el loop principal:
   ```python
   time.sleep(0.05)  # Era 0.1
   ```

2. Reduce max_pasos:
   ```python
   max_pasos = 500  # Era 1000
   ```

3. Reduce timeout XML:
   ```xml
   <ServerQuitFromTimeUp timeLimitMs="180000"/>  <!-- 3 min -->
   ```

---

### Memoria crece sin control

**Síntomas:**
- Uso de RAM aumenta continuamente
- Python crashea por falta de memoria

**Soluciones:**
1. Limita tamaño de Q-tables (implementar poda):
   ```python
   # En actualizar_q()
   if len(q_table) > 10000:  # Máximo 10k estados
       # Eliminar estados viejos/poco usados
       pass
   ```

2. Reduce frecuencia de guardado:
   ```python
   if episodio % 25 == 0:  # Era cada 10
   ```

---

## 🔍 Debugging Avanzado

### Activar modo verbose

En `mundo_rl.py`, añade al inicio de `ejecutar_episodio()`:
```python
DEBUG = True  # Global

if DEBUG:
    print(f"DEBUG: Observación = {obs}")
    print(f"DEBUG: Estado = {estado}")
    print(f"DEBUG: Acción = {accion} ({agente.ACCIONES[accion]})")
    print(f"DEBUG: Recompensa = {recompensa}")
```

### Visualizar Q-values

```python
def debug_q_values(agente, estado, fase):
    q_table = agente.q_tables[fase]
    q_values = q_table[estado]
    print(f"\nQ-values para estado {estado}:")
    for accion, q in q_values.items():
        print(f"  {agente.ACCIONES[accion]:.<15} Q={q:.2f}")
```

### Grabar episodios

En XML de misión:
```python
mission_record = MalmoPython.MissionRecordSpec(f"./grabaciones/episodio_{episodio}.tgz")
mission_record.recordMP4(MalmoPython.FrameType.COLOUR_MAP, 24)
```

---

## 📞 Soporte

Si ninguna solución funciona:

1. Ejecuta el test de sistema:
   ```bash
   python3 test_sistema.py
   ```

2. Revisa los logs de Malmo en la consola de Minecraft

3. Verifica versiones:
   ```bash
   python3 --version  # Debería ser 3.6+
   java -version      # Debería ser Java 8
   ```

4. Prueba con el agente simple de madera primero (más fácil de debuggear)

---

**Última actualización:** Noviembre 2025
