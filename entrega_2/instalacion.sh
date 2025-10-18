#!/bin/bash

# =============================================================================
# Script de Instalación - Cliente Python Malmo para WSL2
# Minecraft Server: Windows (Host)
# Python Client: Ubuntu WSL2
# Comunicación: Puerto TCP via IP routing
# =============================================================================

set -e  # Detener ejecución si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # Sin color

echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Instalación Cliente Python Malmo para WSL2      ║${NC}"
echo -e "${GREEN}║   Minecraft corriendo en Windows (Host)           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Variables de configuración
PYTHON_VERSION="3.6.15"
VENV_NAME="malmoenv"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.env"
ALIAS_NAME="malmoenv"
MALMO_DIR="$PROJECT_DIR/entrega_2/malmo"
MALMO_PORT=10000  # Puerto por defecto de Malmo

# =============================================================================
# 1. Actualizar sistema
# =============================================================================
echo -e "${BLUE}[1/7]${NC} ${YELLOW}Actualizando repositorios del sistema...${NC}"
sudo apt-get update -y

echo -e "${BLUE}[1/7]${NC} ${YELLOW}Actualizando paquetes instalados...${NC}"
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

echo -e "${GREEN}✓ Sistema actualizado${NC}"

# =============================================================================
# 2. Instalar dependencias mínimas para Python Client
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
    net-tools \
    iputils-ping

echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# =============================================================================
# 3. Obtener IP del host Windows
# =============================================================================
echo -e "${BLUE}[3/7]${NC} ${YELLOW}Detectando IP del host Windows...${NC}"

# Obtener IP de Windows desde WSL2
WINDOWS_IP=$(ip route show | grep -i default | awk '{ print $3}')

echo -e "${CYAN}┌────────────────────────────────────────────┐${NC}"
echo -e "${CYAN}│ IP del Host Windows: ${GREEN}$WINDOWS_IP${CYAN}       │${NC}"
echo -e "${CYAN}└────────────────────────────────────────────┘${NC}"

# Verificar conectividad con Windows
echo -e "${YELLOW}Verificando conectividad con Windows...${NC}"
if ping -c 1 -W 2 $WINDOWS_IP > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Conexión con Windows exitosa${NC}"
else
    echo -e "${RED}⚠ No se puede conectar a Windows. Verifica tu configuración de red${NC}"
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
        pip install --editable "$MALMO_DIR/MalmoEnv"
        echo -e "${GREEN}✓ MalmoEnv instalado desde repositorio${NC}"
    fi
    
    # Agregar Python samples al path
    if [ -d "$MALMO_DIR/Malmo/samples/Python_examples" ]; then
        echo "$MALMO_DIR/Malmo/samples/Python_examples" > "$VENV_DIR/lib/python3.6/site-packages/malmo_samples.pth"
    fi
fi

# Instalar otras dependencias útiles
pip install gym

echo -e "${GREEN}✓ Instalación de Malmo completada${NC}"

# =============================================================================
# 7. Configurar conexión con Windows y alias
# =============================================================================
echo -e "${BLUE}[7/7]${NC} ${YELLOW}Configurando conexión con Minecraft en Windows...${NC}"

# Crear script helper para obtener IP de Windows
cat > "$PROJECT_DIR/get_windows_ip.sh" << 'EOF'
#!/bin/bash
ip route show | grep -i default | awk '{ print $3}'
EOF
chmod +x "$PROJECT_DIR/get_windows_ip.sh"

# Agregar configuración a .bashrc
if ! grep -q "MALMO_WINDOWS_IP" ~/.bashrc; then
    cat >> ~/.bashrc << EOF

# Malmo Configuration - Windows Host IP
export MALMO_WINDOWS_IP=\$(ip route show | grep -i default | awk '{ print \$3}')
export MALMO_PORT=$MALMO_PORT
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
alias $ALIAS_NAME='cd $PROJECT_DIR && pyenv activate $VENV_NAME && echo -e "\033[0;32m✓ Entorno Malmo activado\033[0m" && echo -e "\033[0;36mWindows Host IP: \$MALMO_WINDOWS_IP\033[0m" && echo -e "\033[0;36mPuerto Malmo: \$MALMO_PORT\033[0m"'
EOF
    echo -e "${GREEN}✓ Alias '$ALIAS_NAME' configurado${NC}"
fi

# Crear archivo de ejemplo para conectar a Windows
cat > "$PROJECT_DIR/test_connection.py" << EOF
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba de conexión Malmo
Conecta al servidor Minecraft corriendo en Windows
"""
import os
import socket

def test_malmo_connection():
    windows_ip = os.environ.get('MALMO_WINDOWS_IP', '$WINDOWS_IP')
    malmo_port = int(os.environ.get('MALMO_PORT', $MALMO_PORT))
    
    print(f"Probando conexión a Minecraft en Windows...")
    print(f"IP: {windows_ip}")
    print(f"Puerto: {malmo_port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((windows_ip, malmo_port))
        sock.close()
        
        if result == 0:
            print("✓ Conexión exitosa! Minecraft está corriendo.")
            return True
        else:
            print("✗ No se pudo conectar. Verifica que Minecraft esté corriendo en Windows.")
            print(f"  Asegúrate de que el puerto {malmo_port} esté abierto en Windows.")
            return False
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    test_malmo_connection()
EOF
chmod +x "$PROJECT_DIR/test_connection.py"

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
    }
}
EOF

# Crear archivo de variables de entorno para VSCode
cat > "$PROJECT_DIR/.env_vars" << EOF
MALMO_WINDOWS_IP=$WINDOWS_IP
MALMO_PORT=$MALMO_PORT
MALMO_XSD_PATH=$MALMO_DIR/Schemas
EOF

echo -e "${GREEN}✓ VSCode configurado${NC}"

# =============================================================================
# Resumen de instalación
# =============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✓ Instalación Completada                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}═══════════════ Configuración de Red ═══════════════${NC}"
echo -e "  ${BLUE}IP Windows (Host):${NC}    $WINDOWS_IP"
echo -e "  ${BLUE}Puerto Malmo:${NC}         $MALMO_PORT"
echo -e "  ${BLUE}Conectividad:${NC}         $(ping -c 1 -W 2 $WINDOWS_IP > /dev/null 2>&1 && echo '✓ OK' || echo '✗ Sin conexión')"
echo ""
echo -e "${CYAN}═══════════════ Entorno Python ═══════════════════${NC}"
echo -e "  ${BLUE}Python:${NC}               $(python --version 2>&1)"
echo -e "  ${BLUE}Entorno virtual:${NC}      $VENV_DIR"
echo -e "  ${BLUE}Proyecto:${NC}             $PROJECT_DIR"
if [ "$MALMO_INSTALLED_VIA_PIP" = false ]; then
    echo -e "  ${BLUE}Malmo:${NC}                $MALMO_DIR"
fi
echo ""
echo -e "${YELLOW}═══════════════════ Próximos Pasos ════════════════════${NC}"
echo -e "  ${GREEN}1.${NC} ${CYAN}En Windows:${NC} Iniciar Minecraft con Malmo"
echo -e "     - Descarga Malmo para Windows desde:"
echo -e "       ${BLUE}https://github.com/microsoft/malmo/releases${NC}"
echo -e "     - Ejecuta: ${BLUE}launchClient.bat -port $MALMO_PORT${NC}"
echo -e "     - Asegúrate de que el puerto $MALMO_PORT esté abierto en el firewall"
echo ""
echo -e "  ${GREEN}2.${NC} ${CYAN}En WSL2:${NC} Reinicia tu terminal o ejecuta:"
echo -e "     ${BLUE}source ~/.bashrc${NC}"
echo ""
echo -e "  ${GREEN}3.${NC} ${CYAN}Activar el entorno desde cualquier directorio:${NC}"
echo -e "     ${BLUE}malmoenv${NC}"
echo ""
echo -e "  ${GREEN}4.${NC} ${CYAN}Probar la conexión:${NC}"
echo -e "     ${BLUE}python test_connection.py${NC}"
echo ""
echo -e "  ${GREEN}5.${NC} ${CYAN}Ejecutar tus scripts de Malmo:${NC}"
echo -e "     Modifica la IP de conexión a: ${BLUE}$WINDOWS_IP${NC}"
echo -e "     Ejemplo en Python:"
echo -e "     ${BLUE}client_info = MalmoPython.ClientInfo('$WINDOWS_IP', $MALMO_PORT)${NC}"
echo ""
echo -e "${YELLOW}═════════════════ Firewall Windows ════════════════════${NC}"
echo -e "  Si no puedes conectar, ejecuta en ${CYAN}PowerShell (Admin)${NC} en Windows:"
echo -e "  ${BLUE}New-NetFirewallRule -DisplayName \"Malmo\" -Direction Inbound \\${NC}"
echo -e "  ${BLUE}  -InterfaceAlias \"vEthernet (WSL)\" -Protocol TCP \\${NC}"
echo -e "  ${BLUE}  -LocalPort $MALMO_PORT -Action Allow${NC}"
echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"

# Guardar información del entorno
cat > "$PROJECT_DIR/.env_info" << EOF
PYTHON_VERSION=$PYTHON_VERSION
VENV_NAME=$VENV_NAME
VENV_DIR=$VENV_DIR
MALMO_DIR=$MALMO_DIR
WINDOWS_IP=$WINDOWS_IP
MALMO_PORT=$MALMO_PORT
INSTALACION_FECHA=$(date)
MALMO_INSTALLED_VIA_PIP=$MALMO_INSTALLED_VIA_PIP
EOF

echo -e "${GREEN}✓ Información guardada en $PROJECT_DIR/.env_info${NC}"
echo ""
