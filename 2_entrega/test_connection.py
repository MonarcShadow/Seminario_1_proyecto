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
