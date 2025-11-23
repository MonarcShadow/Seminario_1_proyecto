#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EJECUTAR MODELO ENTRENADO - Agente de Recolección de Madera

Este script ejecuta el modelo YA ENTRENADO sin exploración aleatoria.
Usa epsilon=0 para que el agente solo tome decisiones basadas en lo aprendido.

Uso:
    python3 ejecutar_modelo.py [num_episodios] [mundo_tipo]
    
    num_episodios: Cantidad de episodios a ejecutar (default: 5)
    mundo_tipo: "normal" o "plano" (default: "normal")

Ejemplos:
    python3 ejecutar_modelo.py           # 5 episodios en mundo normal
    python3 ejecutar_modelo.py 10        # 10 episodios en mundo normal
    python3 ejecutar_modelo.py 3 plano   # 3 episodios en mundo plano
"""

import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mundo_rl import entrenar

def main():
    # Parsear argumentos
    num_episodios = 5  # Default
    mundo_tipo = "normal"  # Default
    
    if len(sys.argv) > 1:
        try:
            num_episodios = int(sys.argv[1])
        except ValueError:
            print(f"❌ Error: '{sys.argv[1]}' no es un número válido")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        mundo_tipo = sys.argv[2].lower()
        if mundo_tipo not in ["normal", "plano"]:
            print(f"❌ Error: mundo_tipo debe ser 'normal' o 'plano', no '{mundo_tipo}'")
            sys.exit(1)
    
    # Configuración
    mundo_plano = (mundo_tipo == "plano")
    nombre_modelo = "modelo_agente_madera_plano.pkl" if mundo_plano else "modelo_agente_madera.pkl"
    
    print("=" * 60)
    print("🎮 EJECUCIÓN DE MODELO ENTRENADO - AGENTE DE MADERA")
    print("=" * 60)
    print(f"📊 Configuración:")
    print(f"   Episodios: {num_episodios}")
    print(f"   Mundo: {'PLANO (pruebas)' if mundo_plano else 'NORMAL (terreno natural)'}")
    print(f"   Modelo: {nombre_modelo}")
    print(f"   Modo: EXPLOTACIÓN (epsilon=0, sin exploración)")
    print("=" * 60)
    print()
    
    # Verificar que existe el modelo
    if not os.path.exists(nombre_modelo):
        print(f"❌ Error: No se encontró el modelo '{nombre_modelo}'")
        print(f"   Primero debes entrenar el modelo con:")
        if mundo_plano:
            print(f"   python3 entrenar_plano.py 50")
        else:
            print(f"   python3 entrenar_normal.py 50")
        sys.exit(1)
    
    # EJECUTAR con epsilon=0 (sin exploración, solo explotación)
    entrenar(
        num_episodios=num_episodios,
        nombre_modelo=nombre_modelo,
        mundo_plano=mundo_plano,
        epsilon_override=0.0,  # ¡CLAVE! Sin exploración aleatoria
        mostrar_cada=1  # Mostrar todos los episodios
    )
    
    print()
    print("=" * 60)
    print("✅ EJECUCIÓN COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    main()
