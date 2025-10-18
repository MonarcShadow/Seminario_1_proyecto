# Configuración Malmo para WSL2 Mirror Mode

## Estructura de Directorios

```
/home/carlos/
├── MalmoPlatform/                    # Malmo instalado fuera del proyecto
│   └── Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6/
│       ├── Python_Examples/
│       ├── Schemas/
│       ├── Minecraft/
│       └── ...
│
└── Seminario_1_proyecto/
    └── 2_entrega/    # Tu proyecto (repositorio git)
        ├── .env/                     # Entorno virtual Python
        ├── test_connection.py
        ├── ejemplo_malmo.py
        └── README_MALMO.md
```

## Instalación de Malmo

Malmo 0.37.0 ha sido instalado en:
```
/home/carlos/MalmoPlatform/Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6
```

Esta ubicación está **fuera de tu repositorio** para evitar incluir archivos grandes en git.

## Variables de Entorno

Las siguientes variables están configuradas automáticamente:

- `MALMO_HOST`: 127.0.0.1 (localhost)
- `MALMO_PORT_PRIMARY`: 10000
- `MALMO_PORT_SECONDARY`: 10001
- `MALMO_DIR`: /home/carlos/MalmoPlatform/Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6
- `MALMO_XSD_PATH`: /home/carlos/MalmoPlatform/Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6/Schemas

## Uso

### 1. Activar entorno virtual

Desde cualquier directorio:
```bash
malmoenv
```

### 2. En Windows: Iniciar Minecraft con Malmo

Descarga Malmo para Windows:
https://github.com/microsoft/malmo/releases/download/0.37.0/Malmo-0.37.0-Windows-64bit_withBoost_Python3.6.zip

Luego ejecuta:
```cmd
launchClient.bat -port 10000
```

### 3. Probar conexión

```bash
python test_connection.py
```

### 4. Ejemplo de código

```bash
python ejemplo_malmo.py
```

## En tus scripts de Python

```python
import os
import sys

# Agregar Malmo al path
malmo_dir = os.environ.get('MALMO_DIR')
sys.path.append(os.path.join(malmo_dir, 'Python_Examples'))

import MalmoPython

# Configuración para localhost (Mirror Mode)
MALMO_HOST = '127.0.0.1'
MALMO_PORT = 10000

# Crear cliente
agent_host = MalmoPython.AgentHost()
client_info = MalmoPython.ClientInfo(MALMO_HOST, MALMO_PORT)
```

## WSL2 Mirror Mode

Archivo de configuración: `C:\Users\carlos\.wslconfig`

```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoProxy=true
```

Después de modificar .wslconfig, reinicia WSL2:
```powershell
wsl --shutdown
wsl
```

## Verificar instalación

```bash
echo $MALMO_DIR
ls $MALMO_DIR/Python_Examples/
python -c "import sys; sys.path.append(os.path.join(os.environ['MALMO_DIR'], 'Python_Examples')); import MalmoPython; print('OK')"
```

---
Generado por instalacion.sh - Sat Oct 18 03:11:57 -03 2025
