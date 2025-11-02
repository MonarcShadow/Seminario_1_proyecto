#!/usr/bin/env python
"""
Script de configuración y verificación rápida
Prepara el entorno para entrenar el agente

Autor: Sistema de IA
"""

import os
import sys

def verificar_instalacion():
    """Verifica que todas las dependencias estén instaladas"""
    print("🔍 Verificando instalación...")
    
    errores = []
    advertencias = []
    
    # Python
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        errores.append("Python 3.7+ requerido")
    else:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    # NumPy
    try:
        import numpy
        print(f"✓ NumPy {numpy.__version__}")
    except ImportError:
        errores.append("NumPy no instalado: pip install numpy")
    
    # Matplotlib
    try:
        import matplotlib
        print(f"✓ Matplotlib {matplotlib.__version__}")
    except ImportError:
        advertencias.append("Matplotlib no instalado (opcional): pip install matplotlib")
    
    # MalmoPython
    try:
        import MalmoPython
        print(f"✓ MalmoPython disponible")
    except ImportError:
        errores.append("MalmoPython no disponible. Ver: https://github.com/microsoft/malmo")
    
    return errores, advertencias


def verificar_archivos():
    """Verifica que los archivos del proyecto existan"""
    print("\n📁 Verificando archivos del proyecto...")
    
    archivos_requeridos = [
        "mundo2v2.py",
        "agente_madera_rl.py",
        "entorno_madera.py",
        "utils_madera.py"
    ]
    
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✓ {archivo}")
        else:
            archivos_faltantes.append(archivo)
            print(f"✗ {archivo} NO ENCONTRADO")
    
    return archivos_faltantes


def crear_script_inicio():
    """Crea un script de inicio rápido"""
    print("\n📝 Creando script de inicio rápido...")
    
    script_content = """#!/bin/bash
# Script de inicio rápido para entrenamiento

echo "🚀 Iniciando entrenamiento de agente de recolección de madera"
echo "============================================================"
echo ""
echo "⚠️  IMPORTANTE: Asegúrate de que Minecraft con Malmo esté corriendo"
echo "    en puerto 10000 antes de continuar."
echo ""
read -p "¿Minecraft está corriendo? (s/n): " respuesta

if [ "$respuesta" != "s" ]; then
    echo "Inicia Minecraft con Malmo primero."
    exit 1
fi

echo ""
echo "Iniciando entrenamiento..."
python mundo2v2.py

echo ""
echo "✓ Entrenamiento completado"
echo ""
echo "Para visualizar resultados:"
echo "  python utils_madera.py graficar"
echo "  python utils_madera.py analizar"
"""
    
    try:
        with open("entrenar.sh", "w") as f:
            f.write(script_content)
        
        # Hacer ejecutable
        os.chmod("entrenar.sh", 0o755)
        print("✓ Script 'entrenar.sh' creado")
        return True
    except Exception as e:
        print(f"✗ Error creando script: {e}")
        return False


def mostrar_instrucciones():
    """Muestra instrucciones de uso"""
    print("\n" + "="*70)
    print("📚 INSTRUCCIONES DE USO")
    print("="*70)
    print("""
🎯 OBJETIVO: Entrenar un agente para recolectar 3 bloques de madera

📋 PASOS:

1. INICIAR MALMO
   - Abre Minecraft 1.11.2 con Malmo
   - Asegúrate que esté escuchando en puerto 10000
   
2. ENTRENAR EL AGENTE
   Opción A (Linux/Mac):
     ./entrenar.sh
   
   Opción B (Manual):
     python mundo2v2.py
   
3. VISUALIZAR RESULTADOS
     python utils_madera.py graficar   # Gráficos de entrenamiento
     python utils_madera.py analizar   # Análisis de tabla Q

4. AJUSTAR PARÁMETROS (opcional)
   Edita mundo2v2.py:
     - NUM_EPISODIOS: número de episodios
     - alpha, gamma, epsilon: hiperparámetros

⚙️  CONFIGURACIÓN AVANZADA:
   - Cambiar mundo: editar 'seed' en obtener_mision_xml()
   - Ajustar recompensas: editar entorno_madera.py
   - Nuevas acciones: editar ACCIONES en agente_madera_rl.py

📊 ARCHIVOS GENERADOS:
   - modelo_agente_madera.pkl: modelo entrenado
   - analisis_entrenamiento_madera.png: gráficos

🐛 SOLUCIÓN DE PROBLEMAS:
   - Error de conexión: Verificar que Minecraft esté en puerto 10000
   - Agente no aprende: Aumentar epsilon (más exploración)
   - Atascado: Revisar sistema de recompensas

📖 MÁS INFO: Ver README_MADERA.md
""")
    print("="*70)


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🛠️  CONFIGURACIÓN - Sistema de Recolección de Madera")
    print("="*70 + "\n")
    
    # Verificar instalación
    errores, advertencias = verificar_instalacion()
    
    # Verificar archivos
    faltantes = verificar_archivos()
    
    # Crear script de inicio
    crear_script_inicio()
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    
    if errores:
        print("\n❌ ERRORES CRÍTICOS:")
        for error in errores:
            print(f"   - {error}")
    
    if advertencias:
        print("\n⚠️  ADVERTENCIAS:")
        for adv in advertencias:
            print(f"   - {adv}")
    
    if faltantes:
        print("\n📁 ARCHIVOS FALTANTES:")
        for archivo in faltantes:
            print(f"   - {archivo}")
    
    if not errores and not faltantes:
        print("\n✅ ¡Todo listo para entrenar!")
        mostrar_instrucciones()
        return 0
    else:
        print("\n⚠️  Corrige los errores antes de continuar")
        return 1


if __name__ == "__main__":
    exit(main())
