"""
Configuración de Conexión al Cliente Minecraft

Este archivo contiene la configuración para conectar al cliente de Minecraft
que está corriendo en Windows (o cualquier otra máquina).

Autor: Sistema de IA
Fecha: Noviembre 2025
"""

# Configuración del cliente Minecraft
MINECRAFT_HOST = "127.0.0.1"  # Dirección IP del cliente Minecraft
MINECRAFT_PORT = 10001         # Puerto del cliente Minecraft

# Si Minecraft está en otra máquina en la red local, cambia la IP:
# Ejemplo: MINECRAFT_HOST = "192.168.1.100"

# Configuración de puertos alternativos si el 10001 está ocupado:
# MINECRAFT_PORT = 10002
# MINECRAFT_PORT = 10003

# Para verificar que el cliente está disponible, ejecuta en Windows:
# netstat -an | findstr :10001

def obtener_cliente_info():
    """
    Retorna la configuración del cliente como tupla
    
    Returns:
    --------
    tuple: (host, port)
    """
    return MINECRAFT_HOST, MINECRAFT_PORT


def crear_client_pool():
    """
    Crea y configura un ClientPool con la configuración actual
    
    Returns:
    --------
    MalmoPython.ClientPool: Pool configurado
    """
    import MalmoPython
    
    client_pool = MalmoPython.ClientPool()
    client_info = MalmoPython.ClientInfo(MINECRAFT_HOST, MINECRAFT_PORT)
    client_pool.add(client_info)
    
    print(f"🔌 Cliente configurado: {MINECRAFT_HOST}:{MINECRAFT_PORT}")
    
    return client_pool


def verificar_conexion():
    """
    Intenta verificar que el cliente está disponible
    (Nota: Esta es una verificación básica, no garantiza que Minecraft esté corriendo)
    """
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((MINECRAFT_HOST, MINECRAFT_PORT))
        sock.close()
        
        if result == 0:
            print(f"✅ Puerto {MINECRAFT_PORT} está abierto en {MINECRAFT_HOST}")
            return True
        else:
            print(f"⚠️  Puerto {MINECRAFT_PORT} no responde en {MINECRAFT_HOST}")
            print(f"   Asegúrate de que Minecraft con Malmo está corriendo")
            return False
    except Exception as e:
        print(f"❌ Error verificando conexión: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("🔍 VERIFICACIÓN DE CONEXIÓN AL CLIENTE")
    print("="*60)
    print(f"\nConfiguración actual:")
    print(f"  Host: {MINECRAFT_HOST}")
    print(f"  Port: {MINECRAFT_PORT}")
    print(f"\nVerificando conexión...")
    
    if verificar_conexion():
        print(f"\n✅ El cliente parece estar disponible")
        print(f"   Puedes ejecutar: python3 mundo_rl.py")
    else:
        print(f"\n⚠️  No se pudo conectar al cliente")
        print(f"\n📋 Pasos para solucionar:")
        print(f"   1. Inicia Minecraft 1.11.2 en Windows")
        print(f"   2. Carga el mod de Malmo")
        print(f"   3. Espera a ver el mensaje 'Malmo server listening'")
        print(f"   4. Vuelve a ejecutar este script")
        print(f"\n💡 Si Minecraft está en otra máquina:")
        print(f"   Edita config.py y cambia MINECRAFT_HOST a la IP correcta")
