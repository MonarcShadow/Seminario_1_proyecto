#!/bin/bash
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
