#!/bin/bash

# =============================================================================
# Script de Instalación - Cliente Python Malmo para WSL2
# Modo: WSL2 Mirror Networking (localhost)
# Minecraft Server: Windows (Host) - Puerto 10000/10001
# Python Client: Ubuntu WSL2 - Puerto 10000/10001
# Comunicación: localhost (127.0.0.1) bidireccional
# =============================================================================

set -e  # Detener ejecución si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # Sin color

echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Instalación Cliente Python Malmo para WSL2          ║${NC}"
echo -e "${GREEN}║   Modo Mirror Networking (localhost)                  ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Variables de configuración
PYTHON_VERSION="3.6.15"
VENV_NAME="malmoenv"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$HOME/.pyenv/versions/$VENV_NAME"
ALIAS_NAME="malmoenv"

# Malmo se instalará fuera del proyecto
MALMO_BASE_DIR="$HOME/MalmoPlatform"
MALMO_VERSION="0.37.0"
MALMO_PLATFORM="Linux-Ubuntu-18.04-64bit_withBoost_Python3.6"
MALMO_FOLDER="Malmo-${MALMO_VERSION}-${MALMO_PLATFORM}"
MALMO_DIR="$MALMO_BASE_DIR/$MALMO_FOLDER"
MALMO_DOWNLOAD_URL="https://github.com/microsoft/malmo/releases/download/${MALMO_VERSION}/${MALMO_FOLDER}.zip"

MALMO_HOST="127.0.0.1"  # localhost en modo mirror
MALMO_PORT_PRIMARY=10000
MALMO_PORT_SECONDARY=10001

# =============================================================================
# 0. Verificar configuración WSL2 Mirror Mode
# =============================================================================
echo -e "${BLUE}[0/8]${NC} ${YELLOW}Verificando configuración WSL2 Mirror Mode...${NC}"

# Obtener el nombre de usuario de Windows usando la ruta completa
WINDOWS_USER=$(/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command '$env:USERNAME' 2>/dev/null | tr -d '\r')

# Si el método anterior falla, intentar con cmd.exe
if [ -z "$WINDOWS_USER" ]; then
    WINDOWS_USER=$(/mnt/c/Windows/System32/cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r')
fi

# Si aún falla, intentar extraer de USERPROFILE
if [ -z "$WINDOWS_USER" ]; then
    WINDOWS_USER=$(/mnt/c/Windows/System32/cmd.exe /c "echo %USERPROFILE%" 2>/dev/null | sed 's/.*\\//' | tr -d '\r')
fi

# Verificar que obtuvimos el usuario
if [ -z "$WINDOWS_USER" ]; then
    echo -e "${RED}✗ No se pudo detectar el usuario de Windows automáticamente${NC}"
    read -p "$(echo -e ${CYAN}Ingresa tu nombre de usuario de Windows: ${NC})" WINDOWS_USER
fi

# Ruta al archivo .wslconfig en Windows
WSLCONFIG_PATH="/mnt/c/Users/$WINDOWS_USER/.wslconfig"
WSL_MIRROR_CONFIGURED=false

echo -e "${CYAN}Usuario de Windows detectado: ${GREEN}$WINDOWS_USER${NC}"

# Verificar si .wslconfig existe en Windows
if [ -f "$WSLCONFIG_PATH" ]; then
    if grep -qi "networkingMode=mirrored" "$WSLCONFIG_PATH" 2>/dev/null; then
        WSL_MIRROR_CONFIGURED=true
        echo -e "${GREEN}✓ WSL2 Mirror Mode está configurado${NC}"
    else
        echo -e "${YELLOW}⚠ Archivo .wslconfig existe pero Mirror Mode no está habilitado${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Archivo .wslconfig no encontrado en: $WSLCONFIG_PATH${NC}"
fi

if [ "$WSL_MIRROR_CONFIGURED" = false ]; then
    echo -e "${YELLOW}⚠ WSL2 Mirror Mode NO está configurado${NC}"
    echo ""
    echo -e "${CYAN}Para habilitar el modo mirror, puedes crearlo automáticamente o manualmente:${NC}"
    echo ""
    
    # Preguntar si desea crear el archivo automáticamente
    read -p "$(echo -e ${CYAN}¿Deseas crear el archivo .wslconfig automáticamente ahora? [s/N]: ${NC})" CREATE_WSLCONFIG
    
    if [[ "$CREATE_WSLCONFIG" =~ ^[Ss]$ ]]; then
        mkdir -p "/mnt/c/Users/$WINDOWS_USER"
        cat > "$WSLCONFIG_PATH" << 'WSLEOF'
[wsl2]
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoProxy=true
WSLEOF
        echo -e "${GREEN}✓ Archivo .wslconfig creado exitosamente en:${NC}"
        echo -e "  ${BLUE}C:\\Users\\$WINDOWS_USER\\.wslconfig${NC}"
        echo ""
        echo -e "${RED}═══════════════════════════════════════════════════${NC}"
        echo -e "${RED}  IMPORTANTE: Debes reiniciar WSL2 ahora${NC}"
        echo -e "${RED}═══════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}Ejecuta en PowerShell (como Administrador):${NC}"
        echo -e "  ${BLUE}wsl --shutdown${NC}"
        echo -e "${YELLOW}Luego abre WSL2 nuevamente y ejecuta este script otra vez.${NC}"
        echo ""
        exit 0
    else
        echo ""
        echo -e "${CYAN}Instrucciones manuales:${NC}"
        echo -e "1. ${YELLOW}Crea el archivo:${NC} ${BLUE}C:\\Users\\$WINDOWS_USER\\.wslconfig${NC}"
        echo -e "2. ${YELLOW}Con el siguiente contenido:${NC}"
        echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
        echo -e "[wsl2]"
        echo -e "networkingMode=mirrored"
        echo -e "dnsTunneling=true"
        echo -e "firewall=true"
        echo -e "autoProxy=true"
        echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
        echo -e "3. ${YELLOW}Reinicia WSL2 en PowerShell:${NC} ${BLUE}wsl --shutdown${NC}"
        echo ""
        read -p "$(echo -e ${CYAN}Presiona ENTER para continuar con la instalación de todas formas...${NC})"
    fi
fi

# =============================================================================
# 1. Actualizar sistema
# =============================================================================
echo -e "${BLUE}[1/8]${NC} ${YELLOW}Actualizando repositorios del sistema...${NC}"
sudo apt-get update -y

echo -e "${BLUE}[1/8]${NC} ${YELLOW}Actualizando paquetes instalados...${NC}"
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

echo -e "${GREEN}✓ Sistema actualizado${NC}"

# =============================================================================
# 2. Instalar dependencias para Python Client
# =============================================================================
echo -e "${BLUE}[2/8]${NC} ${YELLOW}Instalando dependencias para Python...${NC}"
sudo apt-get install -y \
    build-essential \
    wget \
    unzip \
    git \
    curl \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    llvm \
    make \
    net-tools

echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# =============================================================================
# 3. Verificar conectividad localhost
# =============================================================================
echo -e "${BLUE}[3/8]${NC} ${YELLOW}Verificando configuración de red...${NC}"

echo -e "${CYAN}┌─────────────────────────────────────────────────┐${NC}"
echo -e "${CYAN}│ Modo de Red: ${GREEN}WSL2 Mirror (localhost)${CYAN}           │${NC}"
echo -e "${CYAN}│ Host Malmo:  ${GREEN}127.0.0.1${CYAN}                         │${NC}"
echo -e "${CYAN}│ Puerto 1:    ${GREEN}$MALMO_PORT_PRIMARY${CYAN}                             │${NC}"
echo -e "${CYAN}│ Puerto 2:    ${GREEN}$MALMO_PORT_SECONDARY${CYAN}                             │${NC}"
echo -e "${CYAN}└─────────────────────────────────────────────────┘${NC}"

# Verificar que localhost esté accesible
if ping -c 1 -W 1 127.0.0.1 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ localhost (127.0.0.1) accesible${NC}"
else
    echo -e "${RED}✗ Problema con localhost. Verifica la configuración de red${NC}"
fi

# =============================================================================
# 4. Instalar pyenv
# =============================================================================
if [ ! -d "$HOME/.pyenv" ]; then
    echo -e "${BLUE}[4/8]${NC} ${YELLOW}Instalando pyenv...${NC}"
    curl https://pyenv.run | bash
    
    # Configurar pyenv en .bashrc
    if ! grep -q "pyenv init" ~/.bashrc; then
        cat >> ~/.bashrc << 'EOF'

# Pyenv configuration
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
EOF
    fi
    echo -e "${GREEN}✓ pyenv instalado${NC}"
else
    echo -e "${BLUE}[4/8]${NC} ${GREEN}✓ pyenv ya está instalado${NC}"
fi

# Cargar pyenv en la sesión actual
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# =============================================================================
# 5. Instalar Python 3.6.15 y crear entorno virtual
# =============================================================================
echo -e "${BLUE}[5/8]${NC} ${YELLOW}Instalando Python ${PYTHON_VERSION}...${NC}"
if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    pyenv install $PYTHON_VERSION
    echo -e "${GREEN}✓ Python ${PYTHON_VERSION} instalado${NC}"
else
    echo -e "${GREEN}✓ Python ${PYTHON_VERSION} ya está instalado${NC}"
fi

echo -e "${YELLOW}Creando entorno virtual...${NC}"

# Eliminar entorno virtual anterior si existe
if pyenv virtualenvs | grep -q "$VENV_NAME"; then
    pyenv virtualenv-delete -f $VENV_NAME
fi

pyenv virtualenv $PYTHON_VERSION $VENV_NAME
pyenv activate $VENV_NAME

echo -e "${GREEN}✓ Entorno virtual creado${NC}"

# =============================================================================
# 6. Descargar e instalar Malmo Prebuilt
# =============================================================================
echo -e "${BLUE}[6/8]${NC} ${YELLOW}Descargando Malmo prebuilt (fuera del proyecto)...${NC}"

# Crear directorio para Malmo fuera del proyecto
mkdir -p "$MALMO_BASE_DIR"

if [ ! -d "$MALMO_DIR" ]; then
    echo -e "${CYAN}Descargando Malmo ${MALMO_VERSION} para Ubuntu 18.04 con Python 3.6...${NC}"
    echo -e "${CYAN}URL: ${BLUE}$MALMO_DOWNLOAD_URL${NC}"
    echo -e "${CYAN}Destino: ${BLUE}$MALMO_BASE_DIR${NC}"
    echo ""
    
    cd "$MALMO_BASE_DIR"
    
    # Descargar el archivo zip
    wget -c "$MALMO_DOWNLOAD_URL" -O "${MALMO_FOLDER}.zip"
    
    # Descomprimir
    echo -e "${YELLOW}Descomprimiendo...${NC}"
    unzip -q "${MALMO_FOLDER}.zip"
    
    # Eliminar archivo zip
    rm "${MALMO_FOLDER}.zip"
    
    cd "$PROJECT_DIR"
    
    echo -e "${GREEN}✓ Malmo descargado e instalado en: $MALMO_DIR${NC}"
else
    echo -e "${GREEN}✓ Malmo ya está instalado en: $MALMO_DIR${NC}"
fi

# Verificar que la estructura de Malmo sea correcta
if [ ! -d "$MALMO_DIR/Python_Examples" ]; then
    echo -e "${RED}✗ Error: Estructura de Malmo incorrecta en $MALMO_DIR${NC}"
    echo -e "${YELLOW}Se esperaba encontrar: Python_Examples${NC}"
    exit 1
fi

# =============================================================================
# 7. Configurar Python para usar Malmo
# =============================================================================
echo -e "${BLUE}[7/8]${NC} ${YELLOW}Configurando Python para usar Malmo...${NC}"

pip install --upgrade pip setuptools wheel

# Instalar dependencias básicas
pip install numpy matplotlib pillow lxml future gym

# Agregar Malmo Python al path
MALMO_PYTHON_PATH="$MALMO_DIR/Python_Examples"
echo "$MALMO_PYTHON_PATH" > "$VENV_DIR/lib/python3.6/site-packages/malmo.pth"

# Configurar MALMO_XSD_PATH
export MALMO_XSD_PATH="$MALMO_DIR/Schemas"

echo -e "${GREEN}✓ Malmo configurado correctamente${NC}"

# =============================================================================
# 8. Configurar variables de entorno y alias
# =============================================================================
echo -e "${BLUE}[8/8]${NC} ${YELLOW}Configurando entorno para localhost (mirror mode)...${NC}"

# Agregar configuración a .bashrc
if ! grep -q "MALMO_HOST" ~/.bashrc; then
    cat >> ~/.bashrc << EOF

# Malmo Configuration - WSL2 Mirror Mode (localhost)
export MALMO_HOST="$MALMO_HOST"
export MALMO_PORT_PRIMARY=$MALMO_PORT_PRIMARY
export MALMO_PORT_SECONDARY=$MALMO_PORT_SECONDARY
export MALMO_XSD_PATH="$MALMO_DIR/Schemas"
export MALMO_DIR="$MALMO_DIR"
EOF
fi

# Configurar alias
if ! grep -q "alias $ALIAS_NAME=" ~/.bashrc; then
    cat >> ~/.bashrc << EOF

# Alias para activar entorno Malmo
alias $ALIAS_NAME='pyenv activate $VENV_NAME && echo -e "\033[0;32m✓ Entorno Malmo activado\033[0m" && echo -e "\033[0;36mHost: \$MALMO_HOST (localhost)\033[0m" && echo -e "\033[0;36mPuertos: \$MALMO_PORT_PRIMARY, \$MALMO_PORT_SECONDARY\033[0m" && echo -e "\033[0;36mMalmo Dir: \$MALMO_DIR\033[0m"'
EOF
    echo -e "${GREEN}✓ Alias '$ALIAS_NAME' configurado${NC}"
fi

# Crear script de prueba de conexión
cat > "$PROJECT_DIR/test_connection.py" << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba de conexión Malmo
Conecta al servidor Minecraft en localhost (WSL2 Mirror Mode)
"""
import os
import socket
import sys

# Agregar ruta de Malmo
malmo_dir = os.environ.get('MALMO_DIR', '')
if malmo_dir:
    sys.path.append(os.path.join(malmo_dir, 'Python_Examples'))

def test_malmo_connection(host='127.0.0.1', ports=[10000, 10001]):
    print("═" * 60)
    print("Probando conexión a Minecraft (WSL2 Mirror Mode)")
    print("═" * 60)
    print(f"Host: {host} (localhost)")
    print(f"Puertos: {', '.join(map(str, ports))}")
    print(f"Malmo Dir: {os.environ.get('MALMO_DIR', 'No configurado')}")
    print("-" * 60)
    
    results = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✓ Puerto {port}: Conexión exitosa")
                results.append(True)
            else:
                print(f"✗ Puerto {port}: No disponible")
                results.append(False)
        except Exception as e:
            print(f"✗ Puerto {port}: Error - {e}")
            results.append(False)
    
    print("-" * 60)
    
    # Verificar que MalmoPython esté accesible
    try:
        import MalmoPython
        print("✓ MalmoPython importado correctamente")
        print(f"  Versión: {MalmoPython.__version__ if hasattr(MalmoPython, '__version__') else 'N/A'}")
    except ImportError as e:
        print(f"✗ No se pudo importar MalmoPython: {e}")
        print("  Verifica que MALMO_DIR esté configurado correctamente")
    
    print("-" * 60)
    
    if any(results):
        print("✓ Al menos un puerto está disponible. Minecraft está corriendo.")
        print("\n✓ Configuración correcta para WSL2 Mirror Mode")
    else:
        print("✗ No se pudo conectar a ningún puerto.")
        print("\nVerifica que:")
        print("  1. Minecraft con Malmo esté corriendo en Windows")
        print("  2. WSL2 esté en modo Mirror (networkingMode=mirrored)")
        print("  3. El puerto esté configurado correctamente en launchClient")
    
    print("═" * 60)
    return any(results)

if __name__ == "__main__":
    host = os.environ.get('MALMO_HOST', '127.0.0.1')
    port1 = int(os.environ.get('MALMO_PORT_PRIMARY', 10000))
    port2 = int(os.environ.get('MALMO_PORT_SECONDARY', 10001))
    test_malmo_connection(host, [port1, port2])
EOF
chmod +x "$PROJECT_DIR/test_connection.py"

# Crear ejemplo de conexión
cat > "$PROJECT_DIR/ejemplo_malmo.py" << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ejemplo básico de uso de Malmo en WSL2 Mirror Mode
"""
import os
import sys

# Configurar ruta de Malmo
malmo_dir = os.environ.get('MALMO_DIR', '')
if malmo_dir:
    sys.path.append(os.path.join(malmo_dir, 'Python_Examples'))

try:
    import MalmoPython
    print("✓ MalmoPython importado correctamente")
    
    # Configuración para WSL2 Mirror Mode
    MALMO_HOST = os.environ.get('MALMO_HOST', '127.0.0.1')
    MALMO_PORT = int(os.environ.get('MALMO_PORT_PRIMARY', 10000))
    
    print(f"\nConfiguración:")
    print(f"  Host: {MALMO_HOST}")
    print(f"  Puerto: {MALMO_PORT}")
    print(f"  Malmo Dir: {malmo_dir}")
    
    # Crear AgentHost
    agent_host = MalmoPython.AgentHost()
    print("\n✓ AgentHost creado exitosamente")
    
    # Ejemplo de ClientInfo para conexión localhost
    client_pool = MalmoPython.ClientPool()
    client_pool.add(MalmoPython.ClientInfo(MALMO_HOST, MALMO_PORT))
    
    print(f"✓ ClientPool configurado para {MALMO_HOST}:{MALMO_PORT}")
    print("\nAhora puedes usar agent_host.startMission() con tu misión XML")
    
except ImportError as e:
    print(f"✗ Error al importar MalmoPython: {e}")
    print("\nVerifica que:")
    print("  1. El entorno 'malmoenv' esté activado")
    print("  2. MALMO_DIR esté configurado (ejecuta: echo $MALMO_DIR)")
    print("  3. Malmo esté instalado en: ~/MalmoPlatform/")
except Exception as e:
    print(f"✗ Error: {e}")
EOF
chmod +x "$PROJECT_DIR/ejemplo_malmo.py"

# Crear README
cat > "$PROJECT_DIR/README_MALMO.md" << EOF
# Configuración Malmo para WSL2 Mirror Mode

## Estructura de Directorios

\`\`\`
$HOME/
├── MalmoPlatform/                    # Malmo instalado fuera del proyecto
│   └── $MALMO_FOLDER/
│       ├── Python_Examples/
│       ├── Schemas/
│       ├── Minecraft/
│       └── ...
│
└── $(basename $(dirname $PROJECT_DIR))/
    └── $(basename $PROJECT_DIR)/    # Tu proyecto (repositorio git)
        ├── .env/                     # Entorno virtual Python
        ├── test_connection.py
        ├── ejemplo_malmo.py
        └── README_MALMO.md
\`\`\`

## Instalación de Malmo

Malmo ${MALMO_VERSION} ha sido instalado en:
\`\`\`
$MALMO_DIR
\`\`\`

Esta ubicación está **fuera de tu repositorio** para evitar incluir archivos grandes en git.

## Variables de Entorno

Las siguientes variables están configuradas automáticamente:

- \`MALMO_HOST\`: $MALMO_HOST (localhost)
- \`MALMO_PORT_PRIMARY\`: $MALMO_PORT_PRIMARY
- \`MALMO_PORT_SECONDARY\`: $MALMO_PORT_SECONDARY
- \`MALMO_DIR\`: $MALMO_DIR
- \`MALMO_XSD_PATH\`: $MALMO_DIR/Schemas

## Uso

### 1. Activar entorno virtual

Desde cualquier directorio:
\`\`\`bash
$ALIAS_NAME
\`\`\`

### 2. En Windows: Iniciar Minecraft con Malmo

Descarga Malmo para Windows:
https://github.com/microsoft/malmo/releases/download/${MALMO_VERSION}/Malmo-${MALMO_VERSION}-Windows-64bit_withBoost_Python3.6.zip

Luego ejecuta:
\`\`\`cmd
launchClient.bat -port $MALMO_PORT_PRIMARY
\`\`\`

### 3. Probar conexión

\`\`\`bash
python test_connection.py
\`\`\`

### 4. Ejemplo de código

\`\`\`bash
python ejemplo_malmo.py
\`\`\`

## En tus scripts de Python

\`\`\`python
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
\`\`\`

## WSL2 Mirror Mode

Archivo de configuración: \`C:\\Users\\$WINDOWS_USER\\.wslconfig\`

\`\`\`ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoProxy=true
\`\`\`

Después de modificar .wslconfig, reinicia WSL2:
\`\`\`powershell
wsl --shutdown
wsl
\`\`\`

## Verificar instalación

\`\`\`bash
echo \$MALMO_DIR
ls \$MALMO_DIR/Python_Examples/
python -c "import sys; sys.path.append(os.path.join(os.environ['MALMO_DIR'], 'Python_Examples')); import MalmoPython; print('OK')"
\`\`\`

---
Generado por instalacion.sh - $(date)
EOF

# Configurar VSCode
VSCODE_DIR="$PROJECT_DIR/.vscode"
VSCODE_SETTINGS="$VSCODE_DIR/settings.json"
mkdir -p "$VSCODE_DIR"

cat > "$VSCODE_SETTINGS" << EOF
# Configurar VSCode
VSCODE_DIR="$PROJECT_DIR/.vscode"
VSCODE_SETTINGS="$VSCODE_DIR/settings.json"
mkdir -p "$VSCODE_DIR"

cat > "$VSCODE_SETTINGS" << EOF
{
  // Extensión Python: intérprete del proyecto (pyenv)
  "python.defaultInterpreterPath": "$VENV_DIR/bin/python",
  "python.pythonPath": "$VENV_DIR/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.analysis.extraPaths": [
    "$MALMO_DIR/Python_Examples"
  ],
  "python.envFile": "\${workspaceFolder}/.env_vars",
  "python.terminal.activateEnvInCurrentTerminal": true,

  // Code Runner: forzar a usar el python del entorno
  "code-runner.executorMap": {
    "python": "$VENV_DIR/bin/python"
  },
  "code-runner.runInTerminal": true,
  "code-runner.fileDirectoryAsCwd": true,
  "code-runner.saveFileBeforeRun": true,
  "code-runner.clearPreviousOutput": true,
  "code-runner.respectShebang": false,

  // Asegurar que la terminal cargue ~/.bashrc (pyenv init)
  "terminal.integrated.profiles.linux": {
    "bash-with-pyenv": {
      "path": "/bin/bash",
      "args": ["-l"]
    }
  },
  "terminal.integrated.defaultProfile.linux": "bash-with-pyenv",

  // Limpieza
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  }
}
EOF


EOF

# Crear archivo de variables de entorno para VSCode
cat > "$PROJECT_DIR/.env_vars" << EOF
MALMO_HOST=$MALMO_HOST
MALMO_PORT_PRIMARY=$MALMO_PORT_PRIMARY
MALMO_PORT_SECONDARY=$MALMO_PORT_SECONDARY
MALMO_DIR=$MALMO_DIR
MALMO_XSD_PATH=$MALMO_DIR/Schemas
EOF

# Agregar .env_vars al .gitignore si existe
if [ -f "$PROJECT_DIR/.gitignore" ]; then
    if ! grep -q ".env_vars" "$PROJECT_DIR/.gitignore"; then
        echo ".env_vars" >> "$PROJECT_DIR/.gitignore"
    fi
fi

echo -e "${GREEN}✓ VSCode configurado${NC}"

# =============================================================================
# Resumen de instalación
# =============================================================================
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✓ Instalación Completada                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}═══════════════ Configuración de Red ═══════════════${NC}"
echo -e "  ${BLUE}Modo:${NC}              WSL2 Mirror Networking"
echo -e "  ${BLUE}Host Malmo:${NC}        $MALMO_HOST (localhost)"
echo -e "  ${BLUE}Puerto 1:${NC}          $MALMO_PORT_PRIMARY"
echo -e "  ${BLUE}Puerto 2:${NC}          $MALMO_PORT_SECONDARY"
echo -e "  ${BLUE}Mirror Config:${NC}     $([ "$WSL_MIRROR_CONFIGURED" = true ] && echo '✓ Configurado' || echo '⚠ Requiere configuración')"
echo ""
echo -e "${CYAN}═══════════════ Entorno Python ═══════════════════${NC}"
echo -e "  ${BLUE}Python:${NC}            $(python --version 2>&1)"
echo -e "  ${BLUE}Entorno virtual:${NC}   $VENV_DIR"
echo -e "  ${BLUE}Proyecto:${NC}          $PROJECT_DIR"
echo ""
echo -e "${CYAN}═══════════════ Malmo Platform ═══════════════════${NC}"
echo -e "  ${BLUE}Versión:${NC}           $MALMO_VERSION"
echo -e "  ${BLUE}Ubicación:${NC}         $MALMO_DIR"
echo -e "  ${BLUE}Python Examples:${NC}   $MALMO_DIR/Python_Examples"
echo -e "  ${BLUE}Schemas:${NC}           $MALMO_DIR/Schemas"
echo ""
echo -e "${YELLOW}═══════════════════ Próximos Pasos ════════════════════${NC}"

if [ "$WSL_MIRROR_CONFIGURED" = false ]; then
    echo -e "  ${RED}⚠ IMPORTANTE: Configura WSL2 Mirror Mode primero${NC}"
    echo -e "     Ver instrucciones arriba o en README_MALMO.md"
    echo ""
fi

echo -e "  ${GREEN}1.${NC} ${CYAN}Reinicia tu terminal o ejecuta:${NC}"
echo -e "     ${BLUE}source ~/.bashrc${NC}"
echo ""
echo -e "  ${GREEN}2.${NC} ${CYAN}Activar el entorno:${NC}"
echo -e "     ${BLUE}$ALIAS_NAME${NC}"
echo ""
echo -e "  ${GREEN}3.${NC} ${CYAN}En Windows: Descargar e iniciar Minecraft con Malmo${NC}"
echo -e "     Descarga: ${BLUE}https://github.com/microsoft/malmo/releases${NC}"
echo -e "     Ejecuta: ${BLUE}launchClient.bat -port $MALMO_PORT_PRIMARY${NC}"
echo ""
echo -e "  ${GREEN}4.${NC} ${CYAN}Probar la conexión:${NC}"
echo -e "     ${BLUE}python test_connection.py${NC}"
echo ""
echo -e "  ${GREEN}5.${NC} ${CYAN}Ver ejemplo de uso:${NC}"
echo -e "     ${BLUE}python ejemplo_malmo.py${NC}"
echo -e "     ${BLUE}cat README_MALMO.md${NC}"
echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"

# Guardar información del entorno
cat > "$PROJECT_DIR/.env_info" << EOF
PYTHON_VERSION=$PYTHON_VERSION
VENV_NAME=$VENV_NAME
VENV_DIR=$VENV_DIR
MALMO_VERSION=$MALMO_VERSION
MALMO_DIR=$MALMO_DIR
MALMO_HOST=$MALMO_HOST
MALMO_PORT_PRIMARY=$MALMO_PORT_PRIMARY
MALMO_PORT_SECONDARY=$MALMO_PORT_SECONDARY
WSL_MIRROR_CONFIGURED=$WSL_MIRROR_CONFIGURED
WINDOWS_USER=$WINDOWS_USER
INSTALACION_FECHA=$(date)
EOF

echo -e "${GREEN}✓ Información guardada en:${NC}"
echo -e "  ${BLUE}$PROJECT_DIR/.env_info${NC}"
echo -e "  ${BLUE}$PROJECT_DIR/README_MALMO.md${NC}"
echo ""
