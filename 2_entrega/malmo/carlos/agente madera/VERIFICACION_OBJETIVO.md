# 📋 Verificación: Flujo de Mensajes al Completar Objetivo

## ✅ SECUENCIA ESPERADA AL COMPLETAR OBJETIVO

### **Contexto**
Cuando el agente recoge 2+ bloques de madera (log/log2/wood) O 8+ tablas (planks), el episodio debe terminar inmediatamente mostrando mensajes claros.

---

## 🎬 FLUJO COMPLETO DE MENSAJES

### **Paso 1: Detección de inventario**
Cuando el agente tiene items de madera en su inventario:

```
🎒 INVENTARIO DETECTADO:
------------------------------------------------------------
  Slot  1 [HOTBAR    ]: log2                      x2
  Slot  3 [HOTBAR    ]: dirt                      x1
------------------------------------------------------------
  📊 TOTAL: 2 logs, 0 planks
------------------------------------------------------------
```

### **Paso 2: Confirmación de objetivo alcanzado**
Inmediatamente después, si tiene 2+ logs o 8+ planks:

```
============================================================
🎉🎉🎉 ¡OBJETIVO ALCANZADO! 🎉🎉🎉
✅ 2 bloques de madera obtenidos (objetivo: 2+)
============================================================
```

O para planks:

```
============================================================
🎉🎉🎉 ¡OBJETIVO ALCANZADO! 🎉🎉🎉
✅ 8 tablas obtenidas (objetivo: 8+)
============================================================
```

### **Paso 3: Confirmación de episodio completado**
Justo después:

```
============================================================
✅ EPISODIO COMPLETADO EXITOSAMENTE
   Pasos totales: 145
   Recompensa acumulada: 347.50
============================================================
```

### **Paso 4: Resumen final del episodio**
Al final, el resumen estándar:

```
📊 Resumen Episodio #5
   Pasos: 145
   Éxito: ✓
   Recompensa total: 347.50
   Tasa de éxito: 1/5 (20.0%)
```

---

## 🔍 VERIFICACIÓN PASO A PASO

### ¿Cómo verificar que funciona correctamente?

Ejecuta:
```bash
python3 entrenar_normal.py 10
```

### **Busca estos indicadores**:

1. **Durante el episodio**:
   - ✅ Aparece "🎒 INVENTARIO DETECTADO" cuando recoge madera
   - ✅ Muestra los slots con items (`Slot 1 [HOTBAR]: log2 x2`)

2. **Al completar objetivo**:
   - ✅ Banner "🎉🎉🎉 ¡OBJETIVO ALCANZADO!" 
   - ✅ Línea "✅ X bloques de madera obtenidos"
   - ✅ Banner "✅ EPISODIO COMPLETADO EXITOSAMENTE"
   - ✅ El episodio **termina inmediatamente** (no llega a 800 pasos)

3. **Resumen del episodio**:
   - ✅ "Éxito: ✓" (no "✗")
   - ✅ Pasos < 800 (generalmente 100-300 si encontró madera)
   - ✅ Tasa de éxito aumenta

---

## ❌ PROBLEMAS COMUNES Y QUÉ BUSCAR

### **Problema 1: No detecta madera en inventario**
**Síntomas**:
- Agente tiene madera visualmente en hotbar
- NO aparece "🎒 INVENTARIO DETECTADO"
- Episodio continúa hasta 800 pasos
- "Éxito: ✗" aunque tenga madera

**Verificación**:
```bash
# Buscar en output si aparece el inventario
python3 entrenar_normal.py 5 2>&1 | grep -A 5 "🎒 INVENTARIO"
```

Si NO aparece nada → el problema está en la lectura del inventario desde Malmo.

---

### **Problema 2: Detecta pero no termina episodio**
**Síntomas**:
- Aparece "🎉 OBJETIVO ALCANZADO"
- Pero el episodio continúa
- Llega a 800 pasos

**Causa**: El `break` no se ejecuta o `madera_obtenida` es False aunque se imprima el mensaje.

**Verificación**: Revisar que `verificar_madera_obtenida()` retorne `True` correctamente.

---

### **Problema 3: Termina pero marca como fallo**
**Síntomas**:
- Aparece "🎉 OBJETIVO ALCANZADO"
- Episodio termina
- Pero "Éxito: ✗" en el resumen

**Causa**: La variable `madera_obtenida` no se guardó correctamente en `stats['exito']`.

---

## 🧪 PRUEBA DE DIAGNÓSTICO

### **Script de prueba rápida**:
```bash
# Ejecutar 10 episodios y buscar éxitos
python3 entrenar_normal.py 10 2>&1 | tee /tmp/test_madera.log

# Contar cuántas veces se alcanzó el objetivo
grep "🎉🎉🎉 ¡OBJETIVO ALCANZADO!" /tmp/test_madera.log | wc -l

# Contar cuántos episodios se marcaron como éxito
grep "Éxito: ✓" /tmp/test_madera.log | wc -l

# Estos dos números DEBEN SER IGUALES
```

---

## 📊 EJEMPLO REAL DE OUTPUT EXITOSO

```
   Paso 125 | Pos: (243.5,  67.0, 245.2) | Acción: attack 1     | R: +30.00 | Inv: 0
   🪓 Picando madera (paso 3) (+30)
   
   Paso 150 | Pos: (243.5,  67.0, 245.2) | Acción: move 1       | R:  +3.00 | Inv: 1

🎒 INVENTARIO DETECTADO:
------------------------------------------------------------
  Slot  1 [HOTBAR    ]: log2                      x2
------------------------------------------------------------
  📊 TOTAL: 2 logs, 0 planks
------------------------------------------------------------

============================================================
🎉🎉🎉 ¡OBJETIVO ALCANZADO! 🎉🎉🎉
✅ 2 bloques de madera obtenidos (objetivo: 2+)
============================================================

============================================================
✅ EPISODIO COMPLETADO EXITOSAMENTE
   Pasos totales: 151
   Recompensa acumulada: 423.50
============================================================

📊 Resumen Episodio #3
   Pasos: 151
   Éxito: ✓              ← IMPORTANTE: Debe ser ✓
   Recompensa total: 423.50
   Tasa de éxito: 1/3 (33.3%)
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

Después de ejecutar `python3 entrenar_normal.py 10`, verifica:

- [ ] Aparece "🎒 INVENTARIO DETECTADO" cuando recoge madera
- [ ] Muestra correctamente los slots y cantidades
- [ ] Aparece "🎉🎉🎉 ¡OBJETIVO ALCANZADO!" cuando tiene 2+ logs o 8+ planks
- [ ] Aparece "✅ EPISODIO COMPLETADO EXITOSAMENTE" inmediatamente después
- [ ] El episodio termina (no continúa a 800 pasos)
- [ ] Resumen muestra "Éxito: ✓" (no "✗")
- [ ] Tasa de éxito es > 0% después de varios episodios
- [ ] Los números de "OBJETIVO ALCANZADO" y "Éxito: ✓" coinciden

Si todos los checks pasan → **Sistema funcionando correctamente** ✅

Si alguno falla → Revisar logs y reportar cuál falla específicamente.
