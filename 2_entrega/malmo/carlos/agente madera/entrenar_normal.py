"""
Script de Entrenamiento en MUNDO NORMAL
Para entrenamiento real del agente

Uso:
    python entrenar_normal.py [episodios]
    
Ejemplo:
    python entrenar_normal.py 50
"""

import sys
sys.path.insert(0, '/home/carlos/MalmoPlatform/Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6/Python_Examples')

from mundo_rl import entrenar

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print("MalmoPython importado correctamente")
    
    # Parámetros desde línea de comandos
    num_episodios = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    
    print("\n" + "="*60)
    print("🌲 ENTRENAMIENTO EN MUNDO NORMAL - BÚSQUEDA DE MADERA")
    print("="*60)
    print(f"📊 Configuración:")
    print(f"   Episodios: {num_episodios}")
    print(f"   Mundo: NORMAL (DefaultWorldGenerator)")
    print(f"   Modelo: modelo_agente_madera.pkl")
    print("="*60)
    
    try:
        entrenar(
            num_episodios=num_episodios,
            guardar_cada=10,
            modelo_path="modelo_agente_madera.pkl"
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Entrenamiento interrumpido por el usuario")
        print("✓ El progreso se guardó automáticamente")
    except Exception as e:
        print(f"\n❌ Error durante entrenamiento: {e}")
        import traceback
        traceback.print_exc()
