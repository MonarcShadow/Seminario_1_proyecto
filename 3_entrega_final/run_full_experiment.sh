#!/bin/bash

################################################################################
# Script de Experimentación Completa - 4 Algoritmos en Paralelo
#
# Este script:
# 1. Entrena PPO, DQN, A2C en paralelo (puertos distintos)
# 2. Espera a que todos terminen
# 3. Evalúa cada modelo en todos los stages
# 4. Compara algoritmos y genera gráficos
#
# Uso:
#   ./run_full_experiment.sh [fast|full]
#
# Modos:
#   fast - Testing rápido (50 episodios, ~1-2 horas)
#   full - Producción completa (3000 episodios, ~24-48 horas)
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MODE="${1:-fast}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="results/experiment_${TIMESTAMP}"
LOG_DIR="logs/experiment_${TIMESTAMP}"

# Create directories
mkdir -p "$RESULTS_DIR"
mkdir -p "$LOG_DIR"

# Episode configuration based on mode
if [ "$MODE" == "fast" ]; then
    EPISODES=50
    EVAL_EPISODES=5
    echo -e "${YELLOW}[MODE] Fast Testing - ${EPISODES} training episodes${NC}"
elif [ "$MODE" == "full" ]; then
    EPISODES=3000
    EVAL_EPISODES=20
    echo -e "${YELLOW}[MODE] Full Production - ${EPISODES} training episodes${NC}"
else
    echo -e "${RED}[ERROR] Invalid mode: $MODE${NC}"
    echo "Usage: $0 [fast|full]"
    exit 1
fi

# Print header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         MULTI-ALGORITHM TRAINING EXPERIMENT                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Mode: $MODE"
echo "  Episodes: $EPISODES"
echo "  Evaluation episodes: $EVAL_EPISODES"
echo "  Results directory: $RESULTS_DIR"
echo "  Log directory: $LOG_DIR"
echo "  Timestamp: $TIMESTAMP"
echo ""

# Port assignments (to avoid conflicts)
PORT_PPO=10000
PORT_DQN=10001
PORT_A2C=10002
PORT_TRPO=10003

echo -e "${GREEN}Port assignments:${NC}"
echo "  PPO: $PORT_PPO"
echo "  DQN: $PORT_DQN"
echo "  A2C: $PORT_A2C"
echo "  TRPO: $PORT_TRPO"
echo ""

################################################################################
# PHASE 1: PARALLEL TRAINING
################################################################################

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  PHASE 1: TRAINING (Parallel Execution)                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to train algorithm
train_algorithm() {
    local algo=$1
    local port=$2
    local log_file="${LOG_DIR}/${algo}_training.log"
    
    echo -e "${YELLOW}[${algo}] Starting training on port ${port}...${NC}"
    
    python train_${algo}.py \
        --episodes $EPISODES \
        --curriculum \
        --port $port \
        --seed $((RANDOM % 1000000)) \
        > "$log_file" 2>&1
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}[${algo}] ✓ Training completed successfully${NC}"
    else
        echo -e "${RED}[${algo}] ✗ Training failed (exit code: $exit_code)${NC}"
        echo -e "${RED}[${algo}]   Check log: $log_file${NC}"
    fi
    
    return $exit_code
}

# Start training in parallel
echo -e "${YELLOW}[INFO] Starting parallel training...${NC}"
echo ""

train_algorithm "ppo" $PORT_PPO &
PID_PPO=$!

train_algorithm "dqn" $PORT_DQN &
PID_DQN=$!

train_algorithm "a2c" $PORT_A2C &
PID_A2C=$!

train_algorithm "trpo" $PORT_TRPO &
PID_TRPO=$!

# Wait for all training processes
echo -e "${YELLOW}[INFO] Waiting for all training processes to complete...${NC}"
echo "  PPO: PID $PID_PPO"
echo "  DQN: PID $PID_DQN"
echo "  A2C: PID $PID_A2C"
echo "  TRPO: PID $PID_TRPO"
echo ""

# Track failures
FAILED_ALGOS=()

wait $PID_PPO
if [ $? -ne 0 ]; then
    FAILED_ALGOS+=("PPO")
fi

wait $PID_DQN
if [ $? -ne 0 ]; then
    FAILED_ALGOS+=("DQN")
fi

wait $PID_A2C
if [ $? -ne 0 ]; then
    FAILED_ALGOS+=("A2C")
fi

wait $PID_TRPO
if [ $? -ne 0 ]; then
    FAILED_ALGOS+=("TRPO")
fi

echo ""
echo -e "${GREEN}[INFO] All training processes completed!${NC}"
echo ""

# Check for failures
if [ ${#FAILED_ALGOS[@]} -gt 0 ]; then
    echo -e "${RED}[WARNING] Some algorithms failed to train:${NC}"
    for algo in "${FAILED_ALGOS[@]}"; do
        echo -e "${RED}  - $algo${NC}"
    done
    echo ""
    echo -e "${YELLOW}[INFO] Continuing with successful models...${NC}"
    echo ""
fi

################################################################################
# PHASE 2: MODEL EVALUATION
################################################################################

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  PHASE 2: MODEL EVALUATION                                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Find trained models
PPO_MODEL=$(ls -t models/ppo_curriculum_*_final.zip 2>/dev/null | head -1)
DQN_MODEL=$(ls -t models/dqn_curriculum_*_final.zip 2>/dev/null | head -1)
A2C_MODEL=$(ls -t models/a2c_curriculum_*_final.zip 2>/dev/null | head -1)
TRPO_MODEL=$(ls -t models/trpo_curriculum_*_final.zip 2>/dev/null | head -1)

# Evaluate each model
evaluate_model() {
    local algo=$1
    local model=$2
    local port=$3
    
    if [ -z "$model" ]; then
        echo -e "${RED}[${algo}] ✗ No trained model found, skipping evaluation${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}[${algo}] Evaluating model: $model${NC}"
    
    local output_file="${RESULTS_DIR}/${algo}_evaluation.json"
    local log_file="${LOG_DIR}/${algo}_evaluation.log"
    
    python evaluate.py \
        --algorithm $algo \
        --model "$model" \
        --episodes $EVAL_EPISODES \
        --port $port \
        --output "$output_file" \
        --verbose \
        > "$log_file" 2>&1
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}[${algo}] ✓ Evaluation completed${NC}"
        echo -e "${GREEN}[${algo}]   Results: $output_file${NC}"
        return 0
    else
        echo -e "${RED}[${algo}] ✗ Evaluation failed${NC}"
        echo -e "${RED}[${algo}]   Check log: $log_file${NC}"
        return 1
    fi
}

echo -e "${YELLOW}[INFO] Starting model evaluation (sequential)...${NC}"
echo ""

evaluate_model "ppo" "$PPO_MODEL" $PORT_PPO
PPO_EVAL_SUCCESS=$?

evaluate_model "dqn" "$DQN_MODEL" $PORT_DQN
DQN_EVAL_SUCCESS=$?

evaluate_model "a2c" "$A2C_MODEL" $PORT_A2C
A2C_EVAL_SUCCESS=$?

evaluate_model "trpo" "$TRPO_MODEL" $PORT_TRPO
TRPO_EVAL_SUCCESS=$?

echo ""
echo -e "${GREEN}[INFO] Model evaluation completed!${NC}"
echo ""

################################################################################
# PHASE 3: ALGORITHM COMPARISON
################################################################################

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  PHASE 3: ALGORITHM COMPARISON                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Build comparison command with available models
MODELS=()
ALGORITHMS=()

if [ -n "$PPO_MODEL" ]; then
    MODELS+=("$PPO_MODEL")
    ALGORITHMS+=("ppo")
fi

if [ -n "$DQN_MODEL" ]; then
    MODELS+=("$DQN_MODEL")
    ALGORITHMS+=("dqn")
fi

if [ -n "$A2C_MODEL" ]; then
    MODELS+=("$A2C_MODEL")
    ALGORITHMS+=("a2c")
fi

if [ -n "$TRPO_MODEL" ]; then
    MODELS+=("$TRPO_MODEL")
    ALGORITHMS+=("trpo")
fi

if [ ${#MODELS[@]} -lt 2 ]; then
    echo -e "${RED}[ERROR] Need at least 2 models to compare (found ${#MODELS[@]})${NC}"
    echo -e "${YELLOW}[INFO] Skipping comparison...${NC}"
else
    echo -e "${YELLOW}[INFO] Comparing ${#MODELS[@]} algorithms...${NC}"
    echo ""
    
    # Build command
    COMPARE_CMD="python compare_algorithms.py"
    COMPARE_CMD="$COMPARE_CMD --models ${MODELS[@]}"
    COMPARE_CMD="$COMPARE_CMD --algorithms ${ALGORITHMS[@]}"
    COMPARE_CMD="$COMPARE_CMD --episodes $EVAL_EPISODES"
    COMPARE_CMD="$COMPARE_CMD --stages 1 2 3 4"
    COMPARE_CMD="$COMPARE_CMD --output-dir $RESULTS_DIR"
    COMPARE_CMD="$COMPARE_CMD --port $PORT_PPO"
    
    echo -e "${YELLOW}[CMD] $COMPARE_CMD${NC}"
    echo ""
    
    eval $COMPARE_CMD > "${LOG_DIR}/comparison.log" 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[INFO] ✓ Comparison completed successfully${NC}"
        
        # Find generated files
        COMPARISON_JSON=$(ls -t ${RESULTS_DIR}/comparison_results_*.json 2>/dev/null | head -1)
        COMPARISON_PNG=$(ls -t ${RESULTS_DIR}/algorithm_comparison_*.png 2>/dev/null | head -1)
        
        if [ -n "$COMPARISON_JSON" ]; then
            echo -e "${GREEN}[INFO]   Results: $COMPARISON_JSON${NC}"
        fi
        
        if [ -n "$COMPARISON_PNG" ]; then
            echo -e "${GREEN}[INFO]   Plot: $COMPARISON_PNG${NC}"
        fi
    else
        echo -e "${RED}[ERROR] Comparison failed${NC}"
        echo -e "${RED}[ERROR] Check log: ${LOG_DIR}/comparison.log${NC}"
    fi
fi

echo ""

################################################################################
# PHASE 4: SUMMARY
################################################################################

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  EXPERIMENT SUMMARY                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}Training Results:${NC}"
echo "  PPO: $([ -n "$PPO_MODEL" ] && echo "✓ SUCCESS" || echo "✗ FAILED")"
echo "  DQN: $([ -n "$DQN_MODEL" ] && echo "✓ SUCCESS" || echo "✗ FAILED")"
echo "  A2C: $([ -n "$A2C_MODEL" ] && echo "✓ SUCCESS" || echo "✗ FAILED")"
echo "  TRPO: $([ -n "$TRPO_MODEL" ] && echo "✓ SUCCESS" || echo "✗ FAILED")"
echo ""

echo -e "${GREEN}Evaluation Results:${NC}"
echo "  PPO: $([ $PPO_EVAL_SUCCESS -eq 0 ] && echo "✓ SUCCESS" || echo "✗ FAILED")"
echo "  DQN: $([ $DQN_EVAL_SUCCESS -eq 0 ] && echo "✓ SUCCESS" || echo "✗ FAILED")"
echo "  A2C: $([ $A2C_EVAL_SUCCESS -eq 0 ] && echo "✓ SUCCESS" || echo "✗ FAILED")"
echo "  TRPO: $([ $TRPO_EVAL_SUCCESS -eq 0 ] && echo "✓ SUCCESS" || echo "✗ FAILED")"
echo ""

echo -e "${GREEN}Output Files:${NC}"
echo "  Results directory: $RESULTS_DIR"
echo "  Log directory: $LOG_DIR"
echo ""

if [ ${#MODELS[@]} -ge 2 ]; then
    echo -e "${GREEN}Key Files:${NC}"
    ls -lh "$RESULTS_DIR"/*.json 2>/dev/null | awk '{print "  ", $9, "("$5")"}'
    ls -lh "$RESULTS_DIR"/*.png 2>/dev/null | awk '{print "  ", $9, "("$5")"}'
    echo ""
fi

echo -e "${GREEN}Training Logs:${NC}"
ls -lh "$LOG_DIR"/*_training.log 2>/dev/null | awk '{print "  ", $9, "("$5")"}'
echo ""

# Print best algorithm if comparison was successful
COMPARISON_JSON=$(ls -t ${RESULTS_DIR}/comparison_results_*.json 2>/dev/null | head -1)
if [ -n "$COMPARISON_JSON" ]; then
    echo -e "${GREEN}Best Algorithm:${NC}"
    # Extract winner from JSON (simple grep, can be improved)
    grep -o '"success_rate": [0-9.]*' "$COMPARISON_JSON" | head -3 | while read line; do
        echo "  $line"
    done
    echo ""
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  EXPERIMENT COMPLETED                                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Return success if at least one model trained
if [ ${#MODELS[@]} -gt 0 ]; then
    exit 0
else
    exit 1
fi
