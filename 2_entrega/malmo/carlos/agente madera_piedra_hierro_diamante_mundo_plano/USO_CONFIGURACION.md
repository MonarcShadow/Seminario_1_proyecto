# 🚀 Guía Rápida: Uso de configuracion_entrenamiento.py

## ¿Qué hace este archivo?

`configuracion_entrenamiento.py` es tu **panel de control central** para ajustar TODO el comportamiento del agente sin tocar otros archivos.

---

## 📋 Uso Básico

### 1. Ver la configuración actual (sin cambios)
```bash
python3 configuracion_entrenamiento.py --resumen
```

Esto te muestra:
- ✅ Parámetros Q-Learning actuales
- ✅ Todas las recompensas configuradas
- ✅ Multiplicadores por fase
- ✅ Configuración de episodio y mundo

**No hace cambios**, solo muestra la configuración.

---

### 2. Aplicar configuración a los archivos
```bash
python3 configuracion_entrenamiento.py
```

Esto:
1. Te muestra el resumen de configuración
2. Te pregunta: `¿Deseas aplicar esta configuración? (s/n):`
3. Si dices **s**, actualiza automáticamente:
   - `agente_rl.py`
   - `entorno_malmo.py`
   - `mundo_rl.py`

---

## 🎯 Flujo de Trabajo Recomendado

### Paso 1: Ajustar valores
Edita `configuracion_entrenamiento.py` con tus valores deseados:

```python
# Ejemplo: Hacer que el diamante valga más
RECOMPENSA_MATERIAL_OBTENIDO = {
    'madera': 200.0,
    'piedra': 250.0,
    'hierro': 300.0,
    'diamante': 1000.0,  # ← Cambié de 500 a 1000
}
```

### Paso 2: Ver el resumen
```bash
python3 configuracion_entrenamiento.py --resumen
```

Verifica que los valores sean correctos.

### Paso 3: Aplicar cambios
```bash
python3 configuracion_entrenamiento.py
```

Responde **s** cuando pregunte.

### Paso 4: Entrenar
```bash
malmoenv
python3 mundo_rl.py 10
```

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Aumentar velocidad de aprendizaje

**Editar:**
```python
PARAMETROS_QLEARNING = {
    'alpha': 0.2,  # Cambiar de 0.1 a 0.2
    # ... resto igual
}
```

**Aplicar:**
```bash
python3 configuracion_entrenamiento.py
# Responder: s
```

---

### Ejemplo 2: Hacer episodios más largos

**Editar:**
```python
EPISODIO_CONFIG = {
    'max_pasos': 400,              # Cambiar de 200 a 400
    'timeout_mision_ms': 240000,   # 4 minutos
    # ... resto igual
}
```

**Aplicar:**
```bash
python3 configuracion_entrenamiento.py
```

---

### Ejemplo 3: Mundo con menos materiales (más difícil)

**Editar:**
```python
MUNDO_CONFIG = {
    'cantidad_madera': (8, 12),    # Antes (15, 20)
    'cantidad_piedra': (8, 12),    # Antes (15, 20)
    'cantidad_hierro': (4, 6),     # Antes (8, 12)
    'cantidad_diamante': (1, 2),   # Antes (3, 5)
    # ... resto igual
}
```

**Aplicar:**
```bash
python3 configuracion_entrenamiento.py
```

---

## ⚠️ Advertencias

### ❌ NO EDITAR ESTOS ARCHIVOS MANUALMENTE:
- `agente_rl.py`
- `entorno_malmo.py`
- `mundo_rl.py`

Si los editas manualmente, `configuracion_entrenamiento.py` sobrescribirá tus cambios.

### ✅ SIEMPRE EDITAR:
- `configuracion_entrenamiento.py`

Todos los valores están aquí.

---

## 🔄 Revertir Cambios

Si quieres volver a los valores por defecto:

1. **Opción 1**: Restaurar desde git
```bash
git checkout configuracion_entrenamiento.py
python3 configuracion_entrenamiento.py
```

2. **Opción 2**: Editar manualmente los valores a los originales
```python
PARAMETROS_QLEARNING = {
    'alpha': 0.1,
    'gamma': 0.95,
    'epsilon_inicial': 0.4,
    'epsilon_min': 0.05,
    'epsilon_decay': 0.995,
}
# etc...
```

---

## 📊 Verificar que se aplicó correctamente

Después de aplicar cambios, puedes verificar manualmente:

```bash
# Ver alpha en agente_rl.py
grep "alpha=" agente_rl.py | head -1

# Ver recompensa madera en entorno_malmo.py
grep "200.0 \* diff" entorno_malmo.py

# Ver max_pasos en mundo_rl.py
grep "max_pasos =" mundo_rl.py
```

---

## 🆘 Solución de Problemas

### "No se aplicaron los cambios"

**Causa**: Respondiste 'n' cuando preguntó.

**Solución**: Ejecuta de nuevo y responde 's'.

---

### "Los valores no coinciden"

**Causa**: Editaste manualmente los archivos después de aplicar.

**Solución**: 
1. Edita SOLO `configuracion_entrenamiento.py`
2. Ejecuta: `python3 configuracion_entrenamiento.py`
3. Responde: `s`

---

### "Error al aplicar"

**Causa**: Archivos movidos o renombrados.

**Solución**: Verifica que estos archivos existan en el mismo directorio:
- `agente_rl.py`
- `entorno_malmo.py`
- `mundo_rl.py`
- `configuracion_entrenamiento.py`

---

## 💡 Tips

1. **Backup antes de cambios grandes**: 
   ```bash
   cp configuracion_entrenamiento.py configuracion_entrenamiento.py.backup
   ```

2. **Ver solo resumen sin aplicar**:
   ```bash
   python3 configuracion_entrenamiento.py --resumen
   ```

3. **Probar con pocos episodios primero**:
   ```bash
   python3 mundo_rl.py 3  # Solo 3 episodios de prueba
   ```

4. **Cambiar un valor a la vez**: Más fácil identificar qué funciona.

---

## 📚 Más Información

- **Guía detallada**: `GUIA_AJUSTE_PARAMETROS.md`
- **Documentación completa**: `README.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`

---

## ✨ Resumen

```bash
# 1. Editar valores
nano configuracion_entrenamiento.py

# 2. Ver resumen (opcional)
python3 configuracion_entrenamiento.py --resumen

# 3. Aplicar cambios
python3 configuracion_entrenamiento.py
# Responder: s

# 4. Entrenar
malmoenv && python3 mundo_rl.py 10
```

¡Así de simple! 🎉
