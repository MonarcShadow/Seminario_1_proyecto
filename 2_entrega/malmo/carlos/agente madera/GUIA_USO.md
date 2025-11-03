# 🪓 Agente de Recolección de Madera - Guía de Uso

## 📋 Descripción
Agente de Q-Learning que aprende a recolectar madera en Minecraft usando Malmo.

**Objetivo**: Obtener 2+ bloques de madera (log/oak_wood) O 8+ tablas de madera (planks)

---

## 🚀 ENTRENAMIENTO EXHAUSTIVO

### 1️⃣ Entrenamiento en Mundo Normal (Recomendado)

```bash
# Entrenamiento exhaustivo (50+ episodios)
python3 entrenar_normal.py 50

# Entrenamiento largo (100 episodios)
python3 entrenar_normal.py 100

# Continuar entrenamiento (añade 30 episodios más)
python3 entrenar_normal.py 30
```

**Características**:
- Mundo natural con terreno generado proceduralmente
- Árboles distribuidos naturalmente
- El modelo se guarda cada 10 episodios
- Archivo generado: `modelo_agente_madera.pkl`

### 2️⃣ Entrenamiento en Mundo Plano (Solo para pruebas)

```bash
# Pruebas rápidas (10 episodios)
python3 entrenar_plano.py 10

# Más episodios de prueba
python3 entrenar_plano.py 25
```

**Características**:
- Mundo plano sin obstáculos naturales
- Útil para verificar que el agente se mueve correctamente
- Archivo generado: `modelo_agente_madera_plano.pkl`

---

## 🎮 EJECUTAR MODELO ENTRENADO

Una vez completado el entrenamiento, ejecuta el modelo sin exploración aleatoria:

### Ejecución en Mundo Normal

```bash
# 5 episodios (default)
python3 ejecutar_modelo.py

# 10 episodios
python3 ejecutar_modelo.py 10

# 20 episodios
python3 ejecutar_modelo.py 20
```

### Ejecución en Mundo Plano

```bash
# 3 episodios en mundo plano
python3 ejecutar_modelo.py 3 plano

# 5 episodios en mundo plano
python3 ejecutar_modelo.py 5 plano
```

**Diferencia con entrenamiento**:
- ✅ `epsilon = 0` (sin exploración aleatoria)
- ✅ El agente solo usa lo que aprendió
- ✅ Permite evaluar el rendimiento real del modelo

---

## 📊 Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `modelo_agente_madera.pkl` | Modelo entrenado en mundo normal |
| `modelo_agente_madera_plano.pkl` | Modelo entrenado en mundo plano |

---

## 🔄 Flujo de Trabajo Recomendado

### Paso 1: Verificar que funciona
```bash
python3 entrenar_plano.py 5
```
Verifica que el agente se mueve y no hay errores.

### Paso 2: Entrenamiento exhaustivo
```bash
python3 entrenar_normal.py 50
```
Deja que entrene 50+ episodios (puede tomar tiempo).

### Paso 3: Evaluar el modelo
```bash
python3 ejecutar_modelo.py 10
```
Observa cuántos episodios completa exitosamente.

### Paso 4 (Opcional): Más entrenamiento
Si la tasa de éxito es baja (<20%), entrena más:
```bash
python3 entrenar_normal.py 50  # Añade 50 episodios más
```

---

## 🎯 Sistema de Recompensas

El agente aprende mediante:

| Acción | Recompensa |
|--------|-----------|
| 🌲 Picar madera | +30 |
| 🍃 Picar hojas | +1 |
| 📦 Recoger item droppeado | +10 a +40 |
| 🎯 Madera muy cerca | +20 |
| 🔍 Madera detectada | +5 |
| 🍃 Hojas detectadas | +5 |
| 🚶 Moverse correctamente | +3 |
| 👀 Mirar hacia madera | +2 |
| ❌ Picar sin madera | -10 |
| ⚠️ Alejarse de madera | -15 |
| 😴 Holgazanear cerca de árboles | -5 × pasos |
| 🔄 Loop de giros | -20 |
| 🚫 Atascado | -30 |

---

## 📈 Interpretación de Resultados

Durante el entrenamiento verás:

```
📊 Resumen Episodio #1
   Pasos: 291
   Éxito: ✗
   Recompensa total: -132.00
   Tasa de éxito: 0/1 (0.0%)
```

**Indicadores de progreso**:
- ✅ Recompensa total aumenta con el tiempo
- ✅ Tasa de éxito mejora gradualmente
- ✅ El agente pica madera más frecuentemente
- ⚠️ Si la recompensa se mantiene negativa, puede necesitar más entrenamiento

---

## 🛠️ Solución de Problemas

### El agente no se mueve
```bash
# Verifica manualmente que funciona
python3 test_movimiento.py
```

### Errores de Malmo
- Asegúrate de que Minecraft con Malmo esté ejecutándose
- Verifica el archivo `.config` con IP y puerto correctos
- Puerto default: 10001

### Entrenamiento muy lento
- Normal: cada episodio toma 1-3 minutos
- Puedes interrumpir con `Ctrl+C`, el progreso se guarda automáticamente

---

## 💡 Tips

1. **Paciencia**: Los primeros 10-20 episodios suelen ser exploratorios
2. **Guardado automático**: El modelo se guarda cada 10 episodios
3. **Continuación**: Puedes ejecutar `entrenar_normal.py` múltiples veces, continúa desde donde quedó
4. **Epsilon decay**: La exploración disminuye automáticamente con el tiempo

---

## 📞 Comandos Rápidos

```bash
# Entrenamiento exhaustivo
python3 entrenar_normal.py 50

# Ejecutar modelo entrenado
python3 ejecutar_modelo.py 10

# Verificar funcionamiento
python3 entrenar_plano.py 5
```

¡Buena suerte entrenando tu agente! 🚀🪓
