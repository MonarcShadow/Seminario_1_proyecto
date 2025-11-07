# Agente RL Progresivo - Resumen Ejecutivo

## 🎯 Objetivo

Crear un agente de Aprendizaje por Refuerzo que progrese a través de múltiples objetivos en Minecraft, siguiendo la cadena tecnológica del juego:

**Madera → Piedra → Hierro → Diamante**

## 📋 Características Principales

### Progresión Jerárquica
- **4 Fases secuenciales** que deben completarse en orden
- **Crafteo simulado** de herramientas al completar cada fase
- **Castigos** por intentar saltar fases o usar herramienta incorrecta

### Entorno Controlado
- **Mundo plano 50×50** con materiales distribuidos aleatoriamente
- **Muro de obsidiana** perimetral para limitar exploración
- **Spawn fijo** en el centro (0, 4, 0)
- **Sin mobs, sin hambre** para enfocarse en el objetivo

### Algoritmo: Q-Learning Modular
- **Q-tables separadas por fase** (mejor especialización)
- **Parámetros adaptativos** (α, ε) según complejidad de fase
- **12 dimensiones de estado** (orientación, proximidad, herramienta, etc.)
- **7 acciones** (movimiento + giro + salto + ataque + pitch)

### Sistema de Recompensas Inteligente
- **Recompensas escaladas** según fase (×1.0 a ×2.0)
- **Castigo por herramienta incorrecta** (-40 a -100)
- **Castigo por holgazanería** (cerca sin picar)
- **Bonus por exploración vertical** (pitch)

## 📊 Resultados Esperados

### Métricas de Éxito
- **Tasa de éxito >70%** en últimos 20 episodios
- **Fase 3 (diamante) alcanzada** consistentemente
- **Recompensa media >1000** puntos
- **Pasos medio <500** (eficiencia)

### Curva de Aprendizaje Típica
```
Episodios 1-20:   Exploración, completa fase 0-1
Episodios 20-50:  Aprende fase 2, ocasionalmente fase 3
Episodios 50-100: Consistentemente completa las 4 fases
```

## 🚀 Inicio Rápido

### 1. Verificar Sistema
```bash
python3 test_sistema.py
```

### 2. Entrenar (prueba corta)
```bash
python3 mundo_rl.py 10 123456
```

### 3. Entrenar (completo)
```bash
python3 mundo_rl.py 100 123456
```

### 4. Ejecutar Modelo Entrenado
```bash
python3 ejecutar_modelo.py 5 123456
```

## 📁 Archivos Principales

| Archivo | Descripción |
|---------|-------------|
| `agente_rl.py` | Agente Q-Learning con 4 Q-tables modulares |
| `entorno_malmo.py` | Sistema de recompensas adaptativo |
| `mundo_rl.py` | Generación mundo + loop entrenamiento |
| `ejecutar_modelo.py` | Ejecución sin exploración (ε=0) |
| `test_sistema.py` | Verificación de configuración |
| `README.md` | Documentación completa |
| `SIMPLIFICACIONES.md` | Justificación de decisiones |
| `TROUBLESHOOTING.md` | Solución de problemas |

## 🎓 Simplificaciones Implementadas

Para hacer el problema tratable en tiempo razonable:

1. ✅ **Pico de madera inicial** (dado por comando)
2. ✅ **Crafteo simulado** (comando `/give` automático)
3. ✅ **Hierro → lingote automático** (sin horno)
4. ✅ **Mundo plano controlado** (vs mundo normal aleatorio)
5. ✅ **Sin mobs hostiles** (enfoque en exploración)
6. ✅ **Inventario limpiado** (cada episodio desde cero)

**Todas justificadas académicamente** - ver `SIMPLIFICACIONES.md`

## 🧠 Innovaciones Técnicas

### 1. Q-Tables Modulares
En vez de una sola Q-table gigante, usamos **4 Q-tables especializadas** (una por fase). Ventajas:
- Mejor generalización por fase
- Menos conflictos entre objetivos
- Más rápido de entrenar

### 2. Parámetros Adaptativos
Los parámetros de aprendizaje se ajustan según la fase:
```python
Fase 0 (MADERA):   α=0.10, ε=0.40  # Más fácil
Fase 3 (DIAMANTE): α=0.20, ε=0.25  # Más difícil, menos exploración
```

### 3. Recompensas Escaladas
Las recompensas aumentan en fases avanzadas (×2.0 en diamante) para priorizar completar el objetivo final sobre quedarse en fases tempranas.

### 4. Castigo por Fase Incorrecta
El agente aprende a **no** buscar madera cuando ya está en fase hierro (castigo -15), forzando progresión hacia adelante.

## 📈 Extensiones Futuras

Una vez funciona en mundo plano:

### Corto Plazo
- [ ] Probar en mundo normal (DefaultWorldGenerator)
- [ ] Reducir cantidad de materiales (más realista)
- [ ] Ampliar área a 100×100 bloques

### Mediano Plazo
- [ ] Implementar crafteo real (GUI)
- [ ] Añadir más materiales (carbón, redstone)
- [ ] Sistema de fundición real (hornos)

### Largo Plazo
- [ ] Deep Q-Networks (DQN) para estados continuos
- [ ] Transfer learning a otros objetivos
- [ ] Multi-agente cooperativo

## 💡 Lecciones Aprendidas

### ✅ Qué Funciona Bien
- Q-tables modulares por fase
- Recompensas escaladas según complejidad
- Castigos fuertes por herramienta incorrecta
- Mundo plano para entrenamiento inicial

### ⚠️ Desafíos Identificados
- Agente puede atascarse en spawn (mitigado con anti-stuck)
- Fase 2→3 más difícil (hierro/diamante escasos)
- Requiere ~50+ episodios para convergencia
- Timeout crítico: muy corto → falla, muy largo → entrenamiento lento

### 🎯 Mejores Prácticas
1. Siempre empezar con mundo controlado
2. Entrenar al menos 50 episodios antes de evaluar
3. Monitorear epsilon (debe bajar a <0.1 eventualmente)
4. Guardar modelo frecuentemente (cada 10 episodios)
5. Usar semilla fija para reproducibilidad

## 🔬 Experimentos Sugeridos

### Experimento 1: Ablation Study
Entrenar versiones sin cada componente:
- Sin recompensas escaladas
- Sin Q-tables modulares
- Sin castigo por fase incorrecta
- Sin parámetros adaptativos

**Hipótesis:** Todos son necesarios para buen rendimiento.

### Experimento 2: Sensibilidad a Hiperparámetros
Variar α, γ, ε en rangos:
- α ∈ [0.05, 0.3]
- γ ∈ [0.9, 0.99]
- ε₀ ∈ [0.2, 0.6]

**Hipótesis:** α=0.1-0.15, γ=0.95, ε₀=0.4 son óptimos.

### Experimento 3: Curriculum Learning
Entrenar primero solo fase 0, luego 0-1, luego 0-1-2, finalmente 0-1-2-3.

**Hipótesis:** Converge más rápido que aprender todo a la vez.

### Experimento 4: Transfer a Mundo Normal
1. Entrenar 100 episodios en mundo plano
2. Cargar modelo
3. Ejecutar 50 episodios en mundo normal

**Hipótesis:** Política aprendida se transfiere parcialmente.

## 📚 Referencias y Contexto

### Base Teórica
- **Q-Learning:** Watkins & Dayan (1992)
- **Hierarchical RL:** Sutton et al. (1999)
- **Minecraft RL:** MineRL Competition (NeurIPS 2019-2022)

### Inspiración del Proyecto
Este agente implementa **aprendizaje jerárquico** donde cada fase es un sub-objetivo. Es análogo a:
- Robots aprendiendo tareas complejas por etapas
- Juegos RTS (recolectar → construir → atacar)
- Navegación (buscar puerta → abrir → atravesar)

### Diferencias con MineRL Baseline
- **MineRL:** Usa imitation learning + RL en mundo completo
- **Este proyecto:** Q-learning tabular en mundo simplificado
- **Ventaja aquí:** Más interpretable, más rápido de entrenar
- **Ventaja MineRL:** Más general, escala a tareas complejas

## 🏆 Criterios de Éxito del Proyecto

Para considerar el proyecto **exitoso**:

### Mínimo Viable (60%)
- [ ] Completa fase 0 (madera) en >80% episodios
- [ ] Completa fase 1 (piedra) en >50% episodios
- [ ] Sistema de progresión funciona correctamente

### Objetivo Principal (80%)
- [ ] Completa fase 2 (hierro) en >40% episodios
- [ ] Completa fase 3 (diamante) en >20% episodios
- [ ] Documenta curva de aprendizaje

### Excelente (100%)
- [ ] Completa las 4 fases en >70% últimos 20 episodios
- [ ] Pasos medio <400 en episodios exitosos
- [ ] Funciona también en mundo normal (aunque con menor tasa)

## 📞 Contacto y Contribuciones

**Autor:** Sistema de IA  
**Fecha:** Noviembre 2025  
**Versión:** 1.0  
**Licencia:** MIT (código) / CC-BY (documentación)

### Cómo Contribuir
1. Reporta bugs en issues
2. Sugiere mejoras en discussions
3. Comparte resultados de experimentos
4. Documenta nuevas configuraciones que funcionen

---

## 🎬 Demo Rápido

```bash
# 1. Clonar repositorio
cd "agente madera_piedra_hierro_diamante_mundo_plano"

# 2. Verificar instalación
python3 test_sistema.py

# 3. Entrenar 10 episodios (demo rápido ~15 min)
python3 mundo_rl.py 10

# 4. Ejecutar modelo
python3 ejecutar_modelo.py 3

# 5. Ver estadísticas
python3 -c "
import pickle
with open('modelo_progresivo.pkl', 'rb') as f:
    m = pickle.load(f)
    print(f'Episodios: {m[\"episodios\"]}')
    print(f'Epsilon: {m[\"epsilon\"]:.4f}')
    for fase, qt in m['q_tables'].items():
        print(f'Fase {fase}: {len(qt)} estados')
"
```

**¡Listo para empezar!** 🚀

---

*Este documento es un resumen ejecutivo. Para detalles completos, consulta `README.md`.*
