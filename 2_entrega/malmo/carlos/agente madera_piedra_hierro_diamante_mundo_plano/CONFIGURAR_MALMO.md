# Configuración de MalmoPython

## Problema Actual
```
ModuleNotFoundError: No module named 'MalmoPython'
```

## Solución

### Opción 1: Agregar MalmoPython al PYTHONPATH (Recomendado)

```bash
# Encuentra la ruta de MalmoPython en tu instalación de Malmo
# Por defecto debería estar en:
export MALMO_PATH="/path/to/Malmo-0.37.0"
export PYTHONPATH="$PYTHONPATH:$MALMO_PATH/Python_Examples"

# Ejemplo (ajusta la ruta según tu instalación):
export PYTHONPATH="$PYTHONPATH:/home/carlos/Malmo-0.37.0/Python_Examples"
```

### Opción 2: Agregar al script de Python

Agrega esto al inicio de `mundo_rl.py`:

```python
import sys
import os

# Agregar ruta de MalmoPython
malmo_path = os.path.expanduser("~/Malmo-0.37.0/Python_Examples")
if os.path.exists(malmo_path):
    sys.path.append(malmo_path)
else:
    print(f"⚠️  Advertencia: No se encontró Malmo en {malmo_path}")
    print("   Ajusta la ruta en mundo_rl.py")
```

### Opción 3: Crear enlace simbólico

```bash
# En el directorio actual, crea enlace a MalmoPython
ln -s ~/Malmo-0.37.0/Python_Examples/MalmoPython.py MalmoPython.py
```

## Verificación

Para verificar que MalmoPython está accesible:

```bash
python3 -c "import sys; sys.path.append('/home/carlos/Malmo-0.37.0/Python_Examples'); import MalmoPython; print('✓ MalmoPython OK')"
```

## Ejecutar Después de Configurar

Una vez configurado:

```bash
# Con PYTHONPATH
export PYTHONPATH="$PYTHONPATH:/home/carlos/Malmo-0.37.0/Python_Examples"
python3 mundo_rl.py 10

# O en una línea
PYTHONPATH="/home/carlos/Malmo-0.37.0/Python_Examples:$PYTHONPATH" python3 mundo_rl.py 10
```

## Configuración Permanente

Para que persista entre sesiones, agrega al `~/.bashrc`:

```bash
echo 'export PYTHONPATH="$PYTHONPATH:/home/carlos/Malmo-0.37.0/Python_Examples"' >> ~/.bashrc
source ~/.bashrc
```

## Notas

- Ajusta `/home/carlos/Malmo-0.37.0` según tu instalación real de Malmo
- Verifica que existe el archivo `MalmoPython.py` en esa ruta
- El cliente de Minecraft debe estar corriendo antes de ejecutar el script
