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
