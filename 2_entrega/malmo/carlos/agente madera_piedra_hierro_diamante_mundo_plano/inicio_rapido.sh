#!/bin/bash

# Script de Inicio Rápido - Agente Progresivo
# Autor: Sistema de IA

echo "=========================================="
echo "🚀 AGENTE PROGRESIVO MULTI-MATERIAL"
echo "   Madera → Piedra → Hierro → Diamante"
echo "=========================================="
echo ""

# Verificar que Minecraft está corriendo
echo "⚠️  IMPORTANTE:"
echo "   1. Minecraft 1.11.2 debe estar corriendo"
echo "   2. Malmo debe estar activo"
echo "   3. Puerto 10000 disponible"
echo ""

# Menú
echo "Selecciona una opción:"
echo ""
echo "  1) Entrenar modelo (10 episodios - prueba rápida)"
echo "  2) Entrenar modelo (50 episodios - entrenamiento corto)"
echo "  3) Entrenar modelo (100 episodios - entrenamiento completo)"
echo "  4) Ejecutar modelo entrenado (5 episodios)"
echo "  5) Ver estadísticas del modelo"
echo "  6) Salir"
echo ""

read -p "Opción: " opcion

case $opcion in
    1)
        echo ""
        echo "🎓 Entrenando 10 episodios..."
        python3 mundo_rl.py 10 123456
        ;;
    2)
        echo ""
        echo "🎓 Entrenando 50 episodios..."
        python3 mundo_rl.py 50 123456
        ;;
    3)
        echo ""
        echo "🎓 Entrenando 100 episodios..."
        python3 mundo_rl.py 100 123456
        ;;
    4)
        echo ""
        echo "🎮 Ejecutando modelo entrenado..."
        python3 ejecutar_modelo.py 5 123456
        ;;
    5)
        echo ""
        if [ -f "modelo_progresivo.pkl" ]; then
            echo "📊 Modelo encontrado: modelo_progresivo.pkl"
            python3 -c "
import pickle
with open('modelo_progresivo.pkl', 'rb') as f:
    modelo = pickle.load(f)
print(f\"Episodios completados: {modelo['episodios']}\")
print(f\"Epsilon actual: {modelo['epsilon']:.4f}\")
print(f\"\nEstados aprendidos por fase:\")
for fase, qtable in modelo['q_tables'].items():
    print(f\"  Fase {fase}: {len(qtable)} estados\")
"
        else
            echo "❌ No se encontró modelo entrenado."
            echo "   Entrena primero con la opción 1, 2 o 3."
        fi
        ;;
    6)
        echo ""
        echo "👋 ¡Hasta luego!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Opción inválida"
        ;;
esac

echo ""
echo "=========================================="
echo "✓ Proceso completado"
echo "=========================================="
