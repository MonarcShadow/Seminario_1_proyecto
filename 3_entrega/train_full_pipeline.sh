#!/bin/bash
# Script para entrenar el pipeline completo de transfer learning
# Ejecuta las 5 etapas secuencialmente para un algoritmo específico

ALGORITHM=${1:-qlearning}
EPISODES=${2:-50}
SEED=${3:-123456}
PORT=${4:-10000}

echo "=========================================="
echo "Pipeline Completo de Transfer Learning"
echo "=========================================="
echo "Algoritmo: $ALGORITHM"
echo "Episodios: $EPISODES"
echo "Semilla: $SEED"
echo "Puerto: $PORT"
echo "=========================================="

# Stage 1: Wood (sin transfer learning)
echo ""
echo ">>> Stage 1: Wood Agent (madera/)"
cd madera
python wood_agent.py --algorithm $ALGORITHM --episodes $EPISODES --seed $SEED --port $PORT
if [ $? -ne 0 ]; then
    echo "✗ Stage 1 falló"
    exit 1
fi
echo "✓ Stage 1 completado"

# Stage 2: Stone (carga wood_model.pkl)
echo ""
echo ">>> Stage 2: Stone Agent (piedra/)"
cd ../piedra
python stone_agent.py --algorithm $ALGORITHM --episodes $EPISODES --env-seed $SEED --port $PORT \
    --load-model ../entrenamiento_acumulado/${ALGORITHM}_model.pkl
if [ $? -ne 0 ]; then
    echo "✗ Stage 2 falló"
    exit 1
fi
echo "✓ Stage 2 completado"

# Stage 3: Iron (carga stone_model.pkl)
echo ""
echo ">>> Stage 3: Iron Agent (hierro/)"
cd ../hierro
python iron_agent.py --algorithm $ALGORITHM --episodes $EPISODES --env-seed $SEED --port $PORT \
    --load-model ../entrenamiento_acumulado/${ALGORITHM}_stone_model.pkl
if [ $? -ne 0 ]; then
    echo "✗ Stage 3 falló"
    exit 1
fi
echo "✓ Stage 3 completado"

# Stage 4: Diamond (carga iron_model.pkl)
echo ""
echo ">>> Stage 4: Diamond Agent (diamante/)"
cd ../diamante
python diamond_agent.py --algorithm $ALGORITHM --episodes $EPISODES --seed $SEED --port $PORT \
    --load-model ../entrenamiento_acumulado/${ALGORITHM}_iron_model.pkl
if [ $? -ne 0 ]; then
    echo "✗ Stage 4 falló"
    exit 1
fi
echo "✓ Stage 4 completado"

# Stage 5: From Scratch (carga diamond_model.pkl)
echo ""
echo ">>> Stage 5: From Scratch Agent (desde_cero/)"
cd ../desde_cero
python from_scratch_agent.py --algorithm $ALGORITHM --episodes $EPISODES --seed $SEED --port $PORT \
    --load-model ../entrenamiento_acumulado/${ALGORITHM}_diamond_model.pkl
if [ $? -ne 0 ]; then
    echo "✗ Stage 5 falló"
    exit 1
fi
echo "✓ Stage 5 completado"

echo ""
echo "=========================================="
echo "🎉 Pipeline completo exitoso!"
echo "=========================================="
echo "Modelos generados:"
echo "  - ${ALGORITHM}_model.pkl (Stage 1)"
echo "  - ${ALGORITHM}_stone_model.pkl (Stage 2)"
echo "  - ${ALGORITHM}_iron_model.pkl (Stage 3)"
echo "  - ${ALGORITHM}_diamond_model.pkl (Stage 4)"
echo "  - ${ALGORITHM}_scratch_model.pkl (Stage 5)"
echo "=========================================="
