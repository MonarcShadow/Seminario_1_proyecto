"""
Script de Entrenamiento en MUNDO PLANO
Para pruebas iniciales sin problemas de terreno

Uso:
    python entrenar_plano.py [episodios]
    
Ejemplo:
    python entrenar_plano.py 10
"""

import sys
sys.path.insert(0, '/home/carlos/MalmoPlatform/Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6/Python_Examples')

from mundo_rl import entrenar

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print("MalmoPython importado correctamente")
    
    # Parámetros desde línea de comandos
    num_episodios = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    print("\n🎯 Configuración:")
    print(f"   Episodios: {num_episodios}")
    print(f"   Modo: MUNDO PLANO (pruebas)")
    print(f"   Modelo: modelo_agente_madera_plano.pkl")
    
    print("\n" + "="*60)
    print("🚀 ENTRENAMIENTO EN MUNDO PLANO - MODO PRUEBA")
    print("="*60)
    print("⚠️  Este modo usa mundo plano para evitar problemas de terreno")
    print("    Úsalo para verificar que el agente funciona correctamente")
    print("="*60)
    
    try:
        entrenar(
            num_episodios=num_episodios,
            guardar_cada=5,
            modelo_path="modelo_agente_madera_plano.pkl",
            mundo_plano=True,
            mostrar_cada=1  # Mostrar todos en mundo plano
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Entrenamiento interrumpido por el usuario")
        print("✓ El progreso se guardó automáticamente")
    except Exception as e:
        print(f"\n❌ Error durante entrenamiento: {e}")
        import traceback
        traceback.print_exc()
