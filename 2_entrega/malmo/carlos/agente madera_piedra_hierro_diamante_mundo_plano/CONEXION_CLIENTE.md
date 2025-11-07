# Configuración de Conexión Cliente-Servidor

Este documento explica cómo configurar la conexión entre el código Python (servidor) y Minecraft (cliente).

## 🔌 Arquitectura de Conexión

```
┌─────────────────────┐         Red Local          ┌──────────────────────┐
│  LINUX (Python)     │◄─────────────────────────►│  WINDOWS (Minecraft) │
│                     │   IP: 127.0.0.1 / LAN IP   │                      │
│  - mundo_rl.py      │   Puerto: 10001            │  - Minecraft 1.11.2  │
│  - agente_rl.py     │                            │  - Mod Malmo         │
│  - entorno_malmo.py │                            │                      │
└─────────────────────┘                            └──────────────────────┘
```

## ⚙️ Configuración Actual

El archivo `config.py` contiene la configuración de conexión:

```python
MINECRAFT_HOST = "127.0.0.1"  # Dirección IP del cliente Minecraft
MINECRAFT_PORT = 10001         # Puerto del cliente Minecraft
```

### Escenarios Comunes:

### 1️⃣ **Mismo Equipo (Localhost)**
Si Python y Minecraft están en la misma máquina:
```python
MINECRAFT_HOST = "127.0.0.1"
MINECRAFT_PORT = 10001
```

### 2️⃣ **Máquinas Diferentes en Red Local**
Si Python está en Linux y Minecraft en Windows (tu caso):

**Paso 1:** Encuentra la IP de Windows
- Abre CMD en Windows
- Ejecuta: `ipconfig`
- Busca "Dirección IPv4" (ejemplo: `192.168.1.100`)

**Paso 2:** Edita `config.py`:
```python
MINECRAFT_HOST = "192.168.1.100"  # Reemplaza con la IP de Windows
MINECRAFT_PORT = 10001
```

**Paso 3:** Verifica que el firewall de Windows permita el puerto 10001

### 3️⃣ **Puerto Alternativo**
Si el puerto 10001 está ocupado:
```python
MINECRAFT_HOST = "127.0.0.1"
MINECRAFT_PORT = 10002  # o 10003, 10004, etc.
```

## 🔍 Verificar Conexión

### Desde Python (Linux):

```bash
# Opción 1: Usar el script de configuración
python3 config.py

# Opción 2: Usar el test de sistema
python3 test_sistema.py
```

### Desde Windows:

```cmd
# Ver puertos abiertos
netstat -an | findstr :10001

# Deberías ver algo como:
# TCP    0.0.0.0:10001    0.0.0.0:0    LISTENING
```

### Desde Linux:

```bash
# Probar conexión al puerto (si Minecraft está en Windows)
nc -zv 192.168.1.100 10001

# O usando telnet
telnet 192.168.1.100 10001
```

## 🐛 Problemas Comunes

### ❌ "Connection refused"

**Causa:** Minecraft no está escuchando en el puerto

**Solución:**
1. Inicia Minecraft 1.11.2
2. Carga el mod de Malmo
3. Espera a ver "Malmo server listening on port 10001"

---

### ❌ "No route to host"

**Causa:** IP incorrecta o firewall bloqueando

**Solución:**
1. Verifica la IP de Windows con `ipconfig`
2. Verifica que ambas máquinas estén en la misma red
3. Desactiva temporalmente el firewall de Windows para probar

---

### ❌ "Connection timeout"

**Causa:** Firewall bloqueando el puerto

**Solución en Windows:**
1. Panel de Control → Sistema y Seguridad → Firewall de Windows
2. Configuración avanzada
3. Reglas de entrada → Nueva regla
4. Puerto → TCP → 10001
5. Permitir la conexión

---

### ❌ "Port already in use"

**Causa:** Otra aplicación usa el puerto 10001

**Solución:**
1. Cambia el puerto en `config.py` (ejemplo: 10002)
2. O cierra la aplicación que usa el puerto:
   ```cmd
   netstat -ano | findstr :10001
   taskkill /PID <PID> /F
   ```

---

## 📝 Cambiar Configuración

### Opción 1: Editar config.py directamente

```python
# config.py
MINECRAFT_HOST = "192.168.1.100"  # Tu IP de Windows
MINECRAFT_PORT = 10001
```

### Opción 2: Variables de entorno

```bash
export MINECRAFT_HOST="192.168.1.100"
export MINECRAFT_PORT="10001"
python3 mundo_rl.py
```

Luego modifica `config.py`:
```python
import os
MINECRAFT_HOST = os.getenv("MINECRAFT_HOST", "127.0.0.1")
MINECRAFT_PORT = int(os.getenv("MINECRAFT_PORT", "10001"))
```

## 🔒 Seguridad

### Recomendaciones:

1. **Red local:** Usa solo en redes confiables (casa, laboratorio)
2. **Firewall:** Abre solo el puerto específico (10001)
3. **No expongas a Internet:** Malmo no tiene autenticación

### Si necesitas acceso remoto:

Usa túnel SSH:
```bash
# Desde Linux, crear túnel a Windows
ssh -L 10001:localhost:10001 usuario@windows-ip

# Luego en config.py:
MINECRAFT_HOST = "127.0.0.1"
MINECRAFT_PORT = 10001
```

## 🧪 Prueba de Conexión Completa

```bash
# 1. Inicia Minecraft en Windows
# 2. Verifica puerto en Windows
netstat -an | findstr :10001

# 3. Verifica desde Linux
python3 config.py

# 4. Ejecuta test completo
python3 test_sistema.py

# 5. Si todo OK, entrena
python3 mundo_rl.py 1
```

## 📊 Ejemplo de Salida Correcta

```
🔌 Cliente configurado: 192.168.1.100:10001
✅ Puerto 10001 está abierto en 192.168.1.100
✓ Misión iniciada (mundo plano)
🎮 Comenzando episodio...
```

## 🆘 Soporte Adicional

Si los problemas persisten:

1. **Logs de Malmo:** Revisa la consola de Minecraft
2. **Versiones:** Verifica Minecraft 1.11.2 y Malmo 0.37.0
3. **Python:** Verifica que MalmoPython está instalado correctamente
4. **Red:** Ping entre las máquinas
   ```bash
   # Desde Linux
   ping 192.168.1.100
   ```

---

## 📌 Resumen Rápido

Para tu caso específico (Python en Linux, Minecraft en Windows):

1. ✅ Encuentra IP de Windows: `ipconfig` → ejemplo `192.168.1.100`
2. ✅ Edita `config.py`:
   ```python
   MINECRAFT_HOST = "192.168.1.100"
   MINECRAFT_PORT = 10001
   ```
3. ✅ Inicia Minecraft con Malmo en Windows
4. ✅ Verifica conexión: `python3 config.py`
5. ✅ Entrena: `python3 mundo_rl.py 10`

---

**Última actualización:** Noviembre 2025  
**Autor:** Sistema de IA
