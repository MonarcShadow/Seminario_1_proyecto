# 🪓 Sistema de Recolección de Madera - Índice de Archivos

## 📚 Documentación Completa del Proyecto

Este directorio contiene un sistema completo de **Aprendizaje por Refuerzo (Q-Learning)** para entrenar un agente que recolecte madera en Minecraft usando Project Malmo.

---

## 📁 Estructura de Archivos

### 🎯 Archivos Principales (Código)

| Archivo | Descripción | Líneas | Uso |
|---------|-------------|--------|-----|
| **mundo2v2.py** | 🚀 Script principal de entrenamiento | ~380 | `python mundo2v2.py` |
| **agente_madera_rl.py** | 🧠 Implementación del agente Q-Learning | ~300 | Importado automáticamente |
| **entorno_madera.py** | 🌍 Wrapper del entorno + sistema de recompensas | ~310 | Importado automáticamente |
| **utils_madera.py** | 📊 Utilidades de visualización y análisis | ~450 | `python utils_madera.py graficar` |

### 🧪 Archivos de Prueba y Configuración

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| **configurar.py** | ⚙️ Script de verificación del sistema | `python configurar.py` |
| **test_sistema_madera.py** | 🧪 Tests unitarios del sistema | `python test_sistema_madera.py` |

### 📖 Documentación

| Archivo | Contenido | Para quién |
|---------|-----------|-----------|
| **README_MADERA.md** | 📘 Guía completa del usuario | Usuarios nuevos |
| **RESUMEN_TECNICO.md** | 🔬 Detalles técnicos y arquitectura | Desarrolladores |
| **EJEMPLOS_USO.md** | 💡 Ejemplos prácticos y troubleshooting | Todos |
| **INDICE.md** | 📋 Este archivo (índice del proyecto) | Navegación |

### 📦 Archivos Generados (durante entrenamiento)

| Archivo | Descripción | Cuándo se crea |
|---------|-------------|----------------|
| `modelo_agente_madera.pkl` | Tabla Q entrenada + estadísticas | Al entrenar |
| `analisis_entrenamiento_madera.png` | Gráficos de aprendizaje | Al ejecutar `graficar` |
| `entrenar.sh` | Script de inicio rápido (Linux/Mac) | Al ejecutar `configurar.py` |

---

## 🚀 Inicio Rápido

### 1️⃣ Primera Vez

```bash
# Verificar instalación
python configurar.py

# Ver instrucciones completas
cat README_MADERA.md
```

### 2️⃣ Entrenar Agente

```bash
# Opción A: Script automático (Linux/Mac)
./entrenar.sh

# Opción B: Manual
python mundo2v2.py
```

### 3️⃣ Ver Resultados

```bash
# Generar gráficos
python utils_madera.py graficar

# Analizar tabla Q
python utils_madera.py analizar
```

---

## 📖 Rutas de Lectura Recomendadas

### Para Usuarios Nuevos

1. **README_MADERA.md** → Visión general del proyecto
2. **configurar.py** → Verificar que todo funciona
3. **mundo2v2.py** → Entrenar tu primer agente
4. **EJEMPLOS_USO.md** → Ver ejemplos prácticos

### Para Desarrolladores

1. **RESUMEN_TECNICO.md** → Arquitectura del sistema
2. **agente_madera_rl.py** → Algoritmo Q-Learning
3. **entorno_madera.py** → Sistema de recompensas
4. **utils_madera.py** → Análisis y visualización

### Para Debugging

1. **EJEMPLOS_USO.md** → Sección "Troubleshooting"
2. **test_sistema_madera.py** → Tests unitarios
3. **configurar.py** → Verificar configuración

---

## 🎯 Objetivos del Sistema

### Objetivo Principal
**Recolectar 3 bloques de madera** picando árboles en Minecraft.

### Características Clave
- ✅ **Q-Learning** con tabla de estados discretos
- ✅ **7 acciones** disponibles (incluye picar y strafe)
- ✅ **Sistema de recompensas** detallado
- ✅ **Anti-stuck** mechanisms
- ✅ **Tracking de inventario** en tiempo real
- ✅ **Visualización** de métricas y tabla Q
- ✅ **Guardado/carga** de modelos entrenados

---

## 🔑 Componentes del Sistema

### 1. Agente (agente_madera_rl.py)

```python
class AgenteMaderaQLearning:
    """
    Algoritmo Q-Learning para recolección de madera
    
    - Estado: tupla de 7 dimensiones
    - Acciones: 7 comandos de Minecraft
    - Q-table: defaultdict con valores Q
    """
```

**Métodos principales**:
- `obtener_estado_discretizado()` → Observaciones → Estado
- `elegir_accion()` → ε-greedy policy
- `actualizar_q()` → Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
- `guardar_modelo()` / `cargar_modelo()` → Persistencia

### 2. Entorno (entorno_madera.py)

```python
class EntornoMadera:
    """
    Wrapper de Malmo con sistema de recompensas
    
    - Comunicación con Minecraft
    - Cálculo de recompensas
    - Detección de loops y colisiones
    """
```

**Métodos principales**:
- `calcular_recompensa()` → Recompensa total por acción
- `obtener_observacion()` → Parse de JSON de Malmo
- `ejecutar_accion()` → Enviar comando al agente
- `verificar_objetivo_completado()` → Check inventario ≥ 3

### 3. Script Principal (mundo2v2.py)

**Funciones clave**:
- `obtener_mision_xml()` → Genera XML de Malmo
- `ejecutar_episodio()` → Loop de decisión del agente
- `entrenar()` → Bucle de entrenamiento completo

### 4. Utilidades (utils_madera.py)

**Funciones principales**:
- `graficar_aprendizaje()` → 4 gráficos de análisis
- `analizar_tabla_q()` → Estadísticas de la tabla Q
- `simular_episodio_greedy()` → Evaluación sin exploración

---

## 📊 Métricas y Evaluación

### Métricas Registradas

- **Recompensa total** por episodio
- **Pasos** necesarios para completar
- **Madera recolectada** (0-3+)
- **Epsilon** (tasa de exploración)
- **Estados visitados** en tabla Q
- **Distribución de acciones** preferidas

### Criterio de Éxito

Un episodio es **exitoso** si:
- Madera en inventario ≥ 3 bloques
- O recompensa total > 250

---

## 🔧 Configuración

### Hiperparámetros (agente_madera_rl.py)

```python
alpha = 0.15          # Tasa de aprendizaje
gamma = 0.95          # Factor de descuento
epsilon = 0.4         # Exploración inicial
epsilon_min = 0.05    # Mínimo epsilon
epsilon_decay = 0.995 # Decaimiento por episodio
```

### Configuración de Misión (mundo2v2.py)

```python
NUM_EPISODIOS = 30                      # Episodios de entrenamiento
MODELO_PATH = "modelo_agente_madera.pkl"  # Ruta del modelo
seed = 42                               # Semilla del mundo
max_pasos = 800                         # Pasos por episodio
```

---

## 🐛 Troubleshooting

### Problemas Comunes

| Problema | Archivo | Solución |
|----------|---------|----------|
| Error de importación | configurar.py | Verificar instalación |
| Conexión rechazada | README_MADERA.md | Verificar puerto 10000 |
| Agente atascado | EJEMPLOS_USO.md | Ajustar epsilon |
| No encuentra árboles | mundo2v2.py | Cambiar seed/spawn |
| No aprende | entorno_madera.py | Revisar recompensas |

---

## 🎓 Referencias y Créditos

### Basado en
- **Sistema de agua** de Jonathan (`jonathan/mundo_rl.py`)
- **Project Malmo** (Microsoft Research)
- **Q-Learning** (Watkins & Dayan, 1992)

### Diferencias Clave
- ➕ Acción de picar (`attack`)
- ➕ Tracking de inventario
- ➕ Raycast para distancia
- ➕ Grid 5×5×5 (vs 5×3×5)
- ➕ Sistema anti-stuck mejorado

---

## 📝 Changelog

### v1.0 (2 nov 2025)
- ✅ Sistema completo de recolección de madera
- ✅ Q-Learning con 7 acciones
- ✅ Sistema de recompensas detallado
- ✅ Visualización y análisis
- ✅ Documentación completa
- ✅ Scripts de configuración y prueba

### Próximas Versiones
- 🔜 Recolección de piedra
- 🔜 Recolección de hierro
- 🔜 Recolección de diamante
- 🔜 Secuencia completa de recursos

---

## 👥 Equipo

- **Sistema de IA**: Desarrollo del código
- **Carlos**: Integración y pruebas
- **Jonathan**: Sistema base (agua)
- **Seminario 1**: Proyecto académico

---

## 📄 Licencia

Proyecto académico - Universidad

---

## 🆘 Ayuda

### Necesitas ayuda con...

| Tópico | Archivo a Consultar |
|--------|-------------------|
| Instalación | README_MADERA.md |
| Conceptos técnicos | RESUMEN_TECNICO.md |
| Ejemplos de código | EJEMPLOS_USO.md |
| Errores comunes | EJEMPLOS_USO.md → Troubleshooting |
| Modificar recompensas | entorno_madera.py + comentarios |
| Cambiar acciones | agente_madera_rl.py → ACCIONES |
| Ajustar mundo | mundo2v2.py → obtener_mision_xml() |

### Comandos Útiles

```bash
# Información del sistema
python configurar.py

# Tests
python test_sistema_madera.py

# Entrenamiento
python mundo2v2.py

# Análisis
python utils_madera.py graficar
python utils_madera.py analizar

# Ayuda
cat README_MADERA.md
cat EJEMPLOS_USO.md
```

---

## 🎯 Navegación Rápida

- **[README Principal](README_MADERA.md)** - Empieza aquí
- **[Resumen Técnico](RESUMEN_TECNICO.md)** - Arquitectura detallada
- **[Ejemplos de Uso](EJEMPLOS_USO.md)** - Guías prácticas
- **[Código: Agente](agente_madera_rl.py)** - Q-Learning
- **[Código: Entorno](entorno_madera.py)** - Recompensas
- **[Código: Principal](mundo2v2.py)** - Entrenamiento
- **[Código: Utils](utils_madera.py)** - Visualización

---

**Última actualización**: 2 de noviembre de 2025  
**Versión**: 1.0  
**Estado**: ✅ Completamente funcional

🤖🪓🌳 **¡Feliz entrenamiento!**
