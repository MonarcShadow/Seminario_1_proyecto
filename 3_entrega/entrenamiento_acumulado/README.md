# Entrenamiento Acumulado

Esta carpeta contiene los modelos entrenados (archivos `.pkl`) de todos los agentes del proyecto.

## Estructura de Archivos

### Agente de Madera (Stage 1)
- `qlearning_model.pkl` - Modelo Q-Learning para recolección de madera
- `sarsa_model.pkl` - Modelo SARSA para recolección de madera
- `expected_sarsa_model.pkl` - Modelo Expected SARSA para recolección de madera
- `double_q_model.pkl` - Modelo Double Q-Learning para recolección de madera
- `monte_carlo_model.pkl` - Modelo Monte Carlo para recolección de madera
- `random_model.pkl` - Modelo Random (baseline) para recolección de madera

### Agente de Piedra (Stage 2)
- `qlearning_stone_model.pkl` - Modelo Q-Learning para recolección de piedra
- `sarsa_stone_model.pkl` - Modelo SARSA para recolección de piedra
- `expected_sarsa_stone_model.pkl` - Modelo Expected SARSA para recolección de piedra
- `double_q_stone_model.pkl` - Modelo Double Q-Learning para recolección de piedra
- `monte_carlo_stone_model.pkl` - Modelo Monte Carlo para recolección de piedra
- `random_stone_model.pkl` - Modelo Random (baseline) para recolección de piedra

## Uso

Los modelos se guardan automáticamente al finalizar cada episodio de entrenamiento y al finalizar el entrenamiento completo.

Para cargar un modelo pre-entrenado del agente de madera en el agente de piedra:

```bash
cd piedra
python stone_agent.py --algorithm qlearning --episodes 50 --load-model ../entrenamiento_acumulado/qlearning_model.pkl
```

## Notas

- Los archivos `.pkl` contienen las Q-tables entrenadas (para algoritmos basados en valor) o información mínima del agente (para Random Agent)
- Los modelos se sobrescriben en cada ejecución de entrenamiento
- Para aprendizaje jerárquico, el agente de piedra puede cargar modelos pre-entrenados del agente de madera


```bash
cd madera
python wood_agent.py --algorithm qlearning --episodes 50
```

```bash
cd piedra
python stone_agent.py --algorithm qlearning --episodes 50
```
```bash
cd piedra
python stone_agent.py --algorithm qlearning --episodes 50 --load-model ../entrenamiento_acumulado/qlearning_model.pkl
```