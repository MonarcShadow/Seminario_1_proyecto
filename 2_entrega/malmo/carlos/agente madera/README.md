# Agente RL - Recolección de Madera en Minecraft

Este agente de Aprendizaje por Refuerzo (Q-Learning) aprende a buscar, picar y recolectar madera en Minecraft usando Malmo.

## 🎯 Objetivo

El agente debe:
1. **Buscar** árboles en el mundo
2. **Acercarse** a los bloques de madera
3. **Picar** el bloque hasta romperlo
4. **Recoger** el drop acercándose al item para agregarlo al inventario

## 📋 Requisitos

- Minecraft 1.11.2
- Malmo instalado y configurado
- Python 3.x
- Bibliotecas: numpy, matplotlib, pickle

## 🚀 Uso

### Entrenar el agente

```bash
python mundo_rl.py
```

El entrenamiento ejecutará 50 episodios por defecto. Cada episodio:
- Dura máximo 120 segundos o 800 pasos
- El agente spawn en posiciones aleatorias
- Termina cuando obtiene madera o se acaba el tiempo

### Parámetros configurables

En `mundo_rl.py` puedes modificar:

```python
NUM_EPISODIOS = 50        # Cantidad de episodios
MODELO_PATH = "modelo_agente_madera.pkl"  # Archivo del modelo
```

En `agente_rl.py` puedes ajustar hiperparámetros:

```python
agente = AgenteQLearning(
    alpha=0.1,           # Tasa de aprendizaje
    gamma=0.95,          # Factor de descuento
    epsilon=0.4,         # Exploración inicial
    epsilon_decay=0.995  # Decaimiento de exploración
)
```

## 📊 Análisis de Resultados

El archivo `utils.py` proporciona herramientas para analizar el entrenamiento:

```bash
# Ver resumen del entrenamiento
python utils.py resumen

# Graficar evolución del aprendizaje
python utils.py graficar

# Analizar tabla Q aprendida
python utils.py analizar

# Exportar política a archivo de texto
python utils.py exportar

# Ejecutar todos los análisis
python utils.py todo
```

## 🎮 Acciones Disponibles

El agente puede ejecutar 5 acciones:

1. `move 1` - Avanzar hacia adelante
2. `turn 1` - Girar 90° a la derecha
3. `turn -1` - Girar 90° a la izquierda
4. `jumpmove 1` - Saltar y avanzar (para superar obstáculos)
5. `attack 1` - Picar bloque (mantiene presionado para romper)

## 🧠 Representación del Estado

El estado se discretiza en una tupla de 9 elementos:

```python
(orientación, madera_cerca, madera_frente, distancia_madera,
 obstaculo_frente, aire_frente, tiene_madera, altura, mirando_madera)
```

Donde:
- **orientación**: 0=Norte, 1=Este, 2=Sur, 3=Oeste
- **madera_cerca**: 1 si detecta madera en rejilla 5x3x5, 0 si no
- **madera_frente**: 1 si hay madera justo enfrente, 0 si no
- **distancia_madera**: 0=muy cerca (puede picar), 1=cerca, 2=lejos, 3=no visible
- **obstaculo_frente**: 1 si hay obstáculo sólido, 0 si no
- **aire_frente**: 1 si hay aire enfrente, 0 si no
- **tiene_madera**: 1 si ya tiene madera en inventario, 0 si no
- **altura**: 0=bajo (<60), 1=medio (60-70), 2=alto (>70)
- **mirando_madera**: 1 si LineOfSight apunta a madera, 0 si no

## 💰 Sistema de Recompensas

### Recompensas Positivas
- **+200**: Obtener madera en inventario (OBJETIVO)
- **+50**: Picar bloque exitosamente (de Malmo)
- **+30**: Picar cuando hay madera enfrente
- **+20**: Detectar madera muy cerca
- **+15**: Acercarse a madera visible
- **+5**: Intentar moverse después de girar
- **+3**: Movimiento exitoso
- **+2**: Mirar hacia madera

### Penalizaciones
- **-0.5**: Costo por cada acción
- **-5**: Colisión con obstáculo
- **-10**: Picar sin madera enfrente
- **-15**: Alejarse de madera una vez detectada
- **-20**: Loop de giros detectado
- **-30**: Atascado completamente (>8 pasos sin movimiento)

## 🔧 Características Especiales

### Sistema Anti-Stuck
Si el agente se queda atascado sin moverse por más de 12 pasos:
- Ejecuta secuencia de escape: girar y saltar
- Resetea contador después de la secuencia

### Heurística de Picado
Si el agente ve madera enfrente y está mirándola:
- Automáticamente ejecuta `attack` para picar
- Mantiene el comando por 0.5 segundos
- Realiza 3 ataques consecutivos (necesario en Minecraft 1.11.2)

### Tipos de Madera Detectados
El agente reconoce todas las variantes de madera:
- `log` - Roble, abedul, abeto, jungla
- `log2` - Acacia, roble oscuro
- `planks` - Tablas (por si acaso)

## 📈 Progreso Esperado

### Primeros 10 episodios
- Alta exploración (epsilon ~0.4)
- Aprendiendo movimientos básicos
- Descubriendo el entorno

### Episodios 10-30
- Reducción de exploración
- Comenzando a reconocer árboles
- Primeros intentos de picar

### Episodios 30-50
- Comportamiento más dirigido
- Mayor tasa de éxito
- Optimización de pasos

## 🔄 Próximos Pasos

Este agente es el primer paso de una secuencia progresiva:

1. **Madera** ✅ (actual)
2. **Piedra** (siguiente)
3. **Hierro** (futuro)
4. **Diamante** (objetivo final)

Cada etapa construye sobre la anterior, incrementando la complejidad de la tarea.

## 🐛 Troubleshooting

### El agente no encuentra árboles
- Asegúrate de que el mundo generado tenga árboles (bioma adecuado)
- Aumenta el número de episodios para mejor exploración
- Ajusta `spawn_x` y `spawn_z` para aparecer cerca de bosques

### El agente pica pero no recoge la madera
- Verifica que los items droppeados no desaparezcan (check game rules)
- El agente debe estar cerca del item para recogerlo automáticamente
- Revisa que no haya obstáculos entre el agente y el drop

### Bajo rendimiento de aprendizaje
- Aumenta `alpha` (tasa de aprendizaje) a 0.15-0.2
- Reduce `epsilon_decay` para mantener más exploración
- Incrementa `NUM_EPISODIOS` a 100+

### Errores de conexión con Malmo
- Verifica que Minecraft esté corriendo con Malmo en puerto 10001
- Comprueba que no haya otras instancias del agente corriendo
- Reinicia Minecraft si hay problemas persistentes

## 📝 Notas

- El modelo se guarda automáticamente cada 10 episodios
- Puedes interrumpir el entrenamiento con Ctrl+C y el progreso se guardará
- La tabla Q se carga automáticamente al reiniciar el entrenamiento
- Los archivos generados: `modelo_agente_madera.pkl`, `analisis_entrenamiento_madera.png`

## 👨‍💻 Autor

Sistema de IA - Seminario 1 Proyecto
