#!/bin/bash

# =============================================================================
# Script de Instalación - Cliente Python Malmo para WSL2
# Modo: WSL2 Mirror Networking (localhost 127.0.0.1)
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
echo -e "${GREEN}║   Instalación Cliente Python Malmo para WSL2         ║${NC}"
echo -e "${GREEN}║   Modo Mirror Networking (localhost)                  ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Variables de configuración
PYTHON_VERSION="3.6.15"
VENV_NAME="malmoenv"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.env"
ALIAS_NAME="malmoenv"
MALMO_DIR="$PROJECT_DIR/entrega_2/malmo"
MALMO_HOST="127.0.0.1"  # localhost en modo mirror
MALMO_PORT_PRIMARY=10000
MALMO_PORT_SECONDARY=10001

# =============================================================================
# 0. Verificar configuración WSL2 Mirror Mode
# =============================================================================
echo -e "${BLUE}[0/7]${NC} ${YELLOW}Verificando configuración WSL2 Mirror Mode...${NC}"

WSLCONFIG_PATH=$(wslpath "$(cmd.exe /C "echo %UserProfile%" 2>/dev/null | tr -d '\r')")/.wslconfig
WSL_MIRROR_CONFIGURED=false

# Verificar si .wslconfig existe en Windows
if [ -f "$WSLCONFIG_PATH" ]; then
    if grep -q "networkingMode=mirrored" "$WSLCONFIG_PATH" 2>/dev/null; then
        WSL_MIRROR_CONFIGURED=true
        echo -e "${GREEN}✓ WSL2 Mirror Mode está configurado${NC}"
    fi
fi

if [ "$WSL_MIRROR_CONFIGURED" = false ]; then
    echo -e "${YELLOW}⚠ WSL2 Mirror Mode NO está configurado${NC}"
    echo -e "${CYAN}Para habilitar el modo mirror, crea/edita el archivo:${NC}"
    echo -e "  ${MAGENTA}C:\\Users\\$USER\\.wslconfig${NC}"
    echo ""
    echo -e "${CYAN}Y agrega el siguiente contenido:${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "[wsl2]"
    echo -e "networkingMode=mirrored"
    echo -e "dnsTunneling=true"
    echo -e "firewall=true"
    echo -e "autoProxy=true"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Después ejecuta en PowerShell (como Administrador):${NC}"
    echo -e "  ${BLUE}wsl --shutdown${NC}"
    echo -e "  ${BLUE}wsl${NC}"
    echo ""
    read -p "$(echo -e ${CYAN}Presiona ENTER para continuar con la instalación...${NC})"
fi

# =============================================================================
# 1. Actualizar sistema
# =============================================================================
echo -e "${BLUE}[1/7]${NC} ${YELLOW}Actualizando repositorios del sistema...${NC}"
sudo apt-get update -y

echo -e "${BLUE}[1/7]${NC} ${YELLOW}Actualizando paquetes instalados...${NC}"
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

echo -e "${GREEN}✓ Sistema actualizado${NC}"

# =============================================================================
# 2. Instalar dependencias para Python Client
# =============================================================================
echo -e "${BLUE}[2/7]${NC} ${YELLOW}Instalando dependencias para Python...${NC}"
sudo apt-get install -y \
    build-essential \
    wget \
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
echo -e "${BLUE}[3/7]${NC} ${YELLOW}Verificando configuración de red...${NC}"

echo -e "${CYAN}┌─────────────────────────────────────────────────┐${NC}"
echo -e "${CYAN}│ Modo de Red: ${GREEN}WSL2 Mirror (localhost)${CYAN}          │${NC}"
echo -e "${CYAN}│ Host Malmo:  ${GREEN}127.0.0.1${CYAN}                        │${NC}"
echo -e "${CYAN}│ Puerto 1:    ${GREEN}$MALMO_PORT_PRIMARY${CYAN}                            │${NC}"
echo -e "${CYAN}│ Puerto 2:    ${GREEN}$MALMO_PORT_SECONDARY${CYAN}                            │${NC}"
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
    echo -e "${BLUE}[4/7]${NC} ${YELLOW}Instalando pyenv...${NC}"
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
    echo -e "${BLUE}[4/7]${NC} ${GREEN}✓ pyenv ya está instalado${NC}"
fi

# Cargar pyenv en la sesión actual
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# =============================================================================
# 5. Instalar Python 3.6.15 y crear entorno virtual
# =============================================================================
echo -e "${BLUE}[5/7]${NC} ${YELLOW}Instalando Python ${PYTHON_VERSION}...${NC}"
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
ln -sf $HOME/.pyenv/versions/$VENV_NAME $VENV_DIR
pyenv activate $VENV_NAME

echo -e "${GREEN}✓ Entorno virtual creado${NC}"

# =============================================================================
# 6. Instalar Malmo Python Client
# =============================================================================
echo -e "${BLUE}[6/7]${NC} ${YELLOW}Instalando Malmo Python Client...${NC}"

pip install --upgrade pip setuptools wheel

# Instalar dependencias
pip install numpy matplotlib pillow lxml future

# Intentar instalar malmo con pip
echo -e "${YELLOW}Intentando instalar Malmo con pip...${NC}"
if pip install malmo 2>/dev/null; then
    echo -e "${GREEN}✓ Malmo instalado con pip${NC}"
    MALMO_INSTALLED_VIA_PIP=true
else
    echo -e "${YELLOW}⚠ Pip falló. Clonando repositorio Malmo...${NC}"
    MALMO_INSTALLED_VIA_PIP=false
    
    # Clonar repositorio de Malmo
    if [ ! -d "$MALMO_DIR/.git" ]; then
        mkdir -p "$(dirname "$MALMO_DIR")"
        git clone https://github.com/microsoft/malmo.git "$MALMO_DIR"
    fi
    
    # Configurar MALMO_XSD_PATH
    export MALMO_XSD_PATH=$MALMO_DIR/Schemas
    
    # Agregar MalmoEnv al Python path (recomendado para cliente sin código nativo)
    if [ -d "$MALMO_DIR/MalmoEnv" ]; then
        echo "$MALMO_DIR/MalmoEnv" > "$VENV_DIR/lib/python3.6/site-packages/malmoenv.pth"
        
        # Instalar MalmoEnv en modo editable
        if [ -f "$MALMO_DIR/MalmoEnv/setup.py" ]; then
            cd "$MALMO_DIR/MalmoEnv"
            pip install -e .
            cd "$PROJECT_DIR"
        fi
        
        echo -e "${GREEN}✓ MalmoEnv instalado desde repositorio${NC}"
    fi
    
    # Agregar Python samples al path
    if [ -d "$MALMO_DIR/Malmo/samples/Python_examples" ]; then
        echo "$MALMO_DIR/Malmo/samples/Python_examples" > "$VENV_DIR/lib/python3.6/site-packages/malmo_samples.pth"
    fi
fi

# Instalar gym para entornos de RL
pip install gym

echo -e "${GREEN}✓ Instalación de Malmo completada${NC}"

# =============================================================================
# 7. Configurar variables de entorno y alias
# =============================================================================
echo -e "${BLUE}[7/7]${NC} ${YELLOW}Configurando entorno para localhost (mirror mode)...${NC}"

# Agregar configuración a .bashrc
if ! grep -q "MALMO_HOST" ~/.bashrc; then
    cat >> ~/.bashrc << EOF

# Malmo Configuration - WSL2 Mirror Mode (localhost)
export MALMO_HOST="$MALMO_HOST"
export MALMO_PORT_PRIMARY=$MALMO_PORT_PRIMARY
export MALMO_PORT_SECONDARY=$MALMO_PORT_SECONDARY
EOF
fi

if [ "$MALMO_INSTALLED_VIA_PIP" = false ]; then
    if ! grep -q "MALMO_XSD_PATH" ~/.bashrc; then
        echo "export MALMO_XSD_PATH=$MALMO_DIR/Schemas" >> ~/.bashrc
    fi
fi

# Configurar alias
if ! grep -q "alias $ALIAS_NAME=" ~/.bashrc; then
    cat >> ~/.bashrc << EOF

# Alias para activar entorno Malmo
alias $ALIAS_NAME='cd $PROJECT_DIR && pyenv activate $VENV_NAME && echo -e "\033[0;32m✓ Entorno Malmo activado\033[0m" && echo -e "\033[0;36mHost: \$MALMO_HOST (localhost)\033[0m" && echo -e "\033[0;36mPuertos: \$MALMO_PORT_PRIMARY, \$MALMO_PORT_SECONDARY\033[0m"'
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

def test_malmo_connection(host='127.0.0.1', ports=[10000, 10001]):
    print("═" * 60)
    print("Probando conexión a Minecraft (WSL2 Mirror Mode)")
    print("═" * 60)
    print(f"Host: {host} (localhost)")
    print(f"Puertos: {', '.join(map(str, ports))}")
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

# Crear ejemplo de conexión para scripts de Malmo
cat > "$PROJECT_DIR/ejemplo_conexion.py" << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ejemplo de conexión a Malmo en WSL2 Mirror Mode
Usar en tus scripts de Malmo
"""
import os

# Configuración para WSL2 Mirror Mode
MALMO_HOST = os.environ.get('MALMO_HOST', '127.0.0.1')
MALMO_PORT = int(os.environ.get('MALMO_PORT_PRIMARY', 10000))

print(f"Conectando a Malmo en {MALMO_HOST}:{MALMO_PORT}")

# Ejemplo de uso con MalmoEnv
try:
    import malmoenv
    
    env = malmoenv.make()
    # La conexión se hace automáticamente a localhost
    env.init(
        '<MissionXML>...</MissionXML>',
        port=MALMO_PORT,
        server=MALMO_HOST,
        server2=MALMO_HOST
    )
    print("✓ Conexión exitosa con MalmoEnv")
except ImportError:
    print("MalmoEnv no instalado, usando MalmoPython...")
    
    # Ejemplo con MalmoPython (si usas el repositorio clonado)
    try:
        import MalmoPython
        
        agent_host = MalmoPython.AgentHost()
        client_info = MalmoPython.ClientInfo(MALMO_HOST, MALMO_PORT)
        print(f"✓ ClientInfo configurado para {MALMO_HOST}:{MALMO_PORT}")
    except ImportError:
        print("✗ No se encontró MalmoPython. Verifica la instalación.")

print("\nUsa siempre:")
print(f"  Host: {MALMO_HOST}")
print(f"  Puerto: {MALMO_PORT}")
EOF
chmod +x "$PROJECT_DIR/ejemplo_conexion.py"

# Crear archivo README para configuración
cat > "$PROJECT_DIR/README_MIRROR_MODE.md" << EOF
# Configuración WSL2 Mirror Mode para Malmo

## ¿Qué es Mirror Mode?

Mirror Mode es una característica de WSL2 que permite que Windows y WSL2 compartan la misma interfaz de red, permitiendo comunicación bidireccional usando \`localhost\` (127.0.0.1).

## Requisitos

- Windows 11 22H2 o superior
- WSL 2 versión 2.0.4 o superior

## Configuración

### 1. Habilitar Mirror Mode en WSL2

Crea o edita el archivo \`.wslconfig\` en Windows:

\`\`\`
C:\\Users\\$USER\\.wslconfig
\`\`\`

Contenido:

\`\`\`ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoProxy=true
\`\`\`

### 2. Reiniciar WSL2

En PowerShell (como Administrador):

\`\`\`powershell
wsl --shutdown
wsl
\`\`\`

### 3. Configurar Firewall de Windows (Opcional)

Si tienes problemas de conexión, ejecuta en PowerShell (Admin):

\`\`\`powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
\`\`\`

O para puertos específicos:

\`\`\`powershell
New-NetFirewallHyperVRule -Name "Malmo" -DisplayName "Malmo Minecraft" -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Protocol TCP -LocalPorts 10000,10001
\`\`\`

## Uso con Malmo

### En Windows (Minecraft Server)

1. Descarga Malmo para Windows
2. Ejecuta: \`launchClient.bat -port 10000\`

### En WSL2 (Python Client)

En tus scripts de Python, usa:

\`\`\`python
MALMO_HOST = "127.0.0.1"  # localhost
MALMO_PORT = 10000
\`\`\`

### Prueba de Conexión

\`\`\`bash
python test_connection.py
\`\`\`

## Beneficios del Mirror Mode

✓ Comunicación bidireccional simple con localhost
✓ No necesitas conocer la IP de Windows
✓ Soporte para IPv6
✓ Mejor compatibilidad con VPNs
✓ Conexión desde LAN

## Verificar Configuración

Para verificar que Mirror Mode está activo:

\`\`\`bash
ip addr show
\`\`\`

Deberías ver las mismas interfaces de red que en Windows.

---
Generado por instalacion.sh
EOF

# Configurar VSCode
VSCODE_DIR="$PROJECT_DIR/.vscode"
VSCODE_SETTINGS="$VSCODE_DIR/settings.json"
mkdir -p "$VSCODE_DIR"

cat > "$VSCODE_SETTINGS" << EOF
{
    "python.defaultInterpreterPath": "$VENV_DIR/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.pythonPath": "$VENV_DIR/bin/python",
    "python.analysis.extraPaths": [
        "$MALMO_DIR/MalmoEnv",
        "$MALMO_DIR/Malmo/samples/Python_examples"
    ],
    "python.envFile": "\${workspaceFolder}/.env_vars",
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true
    },
    "python.terminal.activateEnvInCurrentTerminal": true
}
EOF

# Crear archivo de variables de entorno para VSCode
cat > "$PROJECT_DIR/.env_vars" << EOF
MALMO_HOST=$MALMO_HOST
MALMO_PORT_PRIMARY=$MALMO_PORT_PRIMARY
MALMO_PORT_SECONDARY=$MALMO_PORT_SECONDARY
MALMO_XSD_PATH=$MALMO_DIR/Schemas
EOF

echo -e "${GREEN}✓ VSCode configurado${NC}"

# =============================================================================
# Resumen de instalación
# =============================================================================
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✓ Instalación Completada                    ║${NC}"
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
if [ "$MALMO_INSTALLED_VIA_PIP" = false ]; then
    echo -e "  ${BLUE}Malmo:${NC}             $MALMO_DIR"
fi
echo ""
echo -e "${YELLOW}═══════════════════ Próximos Pasos ════════════════════${NC}"

if [ "$WSL_MIRROR_CONFIGURED" = false ]; then
    echo -e "  ${RED}⚠ IMPORTANTE: Configura WSL2 Mirror Mode${NC}"
    echo -e ""
    echo -e "  ${GREEN}1.${NC} ${CYAN}Crea/edita en Windows:${NC}"
    echo -e "     ${BLUE}C:\\Users\\$USER\\.wslconfig${NC}"
    echo -e ""
    echo -e "     ${YELLOW}Contenido:${NC}"
    echo -e "     ${BLUE}[wsl2]${NC}"
    echo -e "     ${BLUE}networkingMode=mirrored${NC}"
    echo -e ""
    echo -e "  ${GREEN}2.${NC} ${CYAN}Reinicia WSL2 en PowerShell (Admin):${NC}"
    echo -e "     ${BLUE}wsl --shutdown${NC}"
    echo -e "     ${BLUE}wsl${NC}"
    echo -e ""
    echo -e "  ${GREEN}3.${NC} ${CYAN}Continúa con los siguientes pasos${NC}"
    echo ""
fi

echo -e "  ${GREEN}A.${NC} ${CYAN}En Windows: Iniciar Minecraft con Malmo${NC}"
echo -e "     Descarga: ${BLUE}https://github.com/microsoft/malmo/releases${NC}"
echo -e "     Ejecuta: ${BLUE}launchClient.bat -port $MALMO_PORT_PRIMARY${NC}"
echo ""
echo -e "  ${GREEN}B.${NC} ${CYAN}En WSL2: Reinicia terminal o ejecuta:${NC}"
echo -e "     ${BLUE}source ~/.bashrc${NC}"
echo ""
echo -e "  ${GREEN}C.${NC} ${CYAN}Activar el entorno:${NC}"
echo -e "     ${BLUE}malmoenv${NC}"
echo ""
echo -e "  ${GREEN}D.${NC} ${CYAN}Probar la conexión:${NC}"
echo -e "     ${BLUE}python test_connection.py${NC}"
echo ""
echo -e "  ${GREEN}E.${NC} ${CYAN}Ver ejemplo de uso:${NC}"
echo -e "     ${BLUE}python ejemplo_conexion.py${NC}"
echo -e "     ${BLUE}cat README_MIRROR_MODE.md${NC}"
echo ""
echo -e "${YELLOW}═══════════════════ Configuración en Scripts ═══════════════${NC}"
echo -e "  ${CYAN}En tus scripts de Python, usa siempre:${NC}"
echo -e "     ${BLUE}MALMO_HOST = '127.0.0.1'  # localhost${NC}"
echo -e "     ${BLUE}MALMO_PORT = 10000  # o 10001${NC}"
echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"

# Guardar información del entorno
cat > "$PROJECT_DIR/.env_info" << EOF
PYTHON_VERSION=$PYTHON_VERSION
VENV_NAME=$VENV_NAME
VENV_DIR=$VENV_DIR
MALMO_DIR=$MALMO_DIR
MALMO_HOST=$MALMO_HOST
MALMO_PORT_PRIMARY=$MALMO_PORT_PRIMARY
MALMO_PORT_SECONDARY=$MALMO_PORT_SECONDARY
WSL_MIRROR_CONFIGURED=$WSL_MIRROR_CONFIGURED
INSTALACION_FECHA=$(date)
MALMO_INSTALLED_VIA_PIP=$MALMO_INSTALLED_VIA_PIP
EOF

echo -e "${GREEN}✓ Información guardada en $PROJECT_DIR/.env_info${NC}"
echo ""
