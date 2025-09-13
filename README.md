Proyecto seminario 1 2025-2

# 1. ¿Qué ambiente va a elegir? ¿Es suficientemente complejo para el proyecto complejo?

El ambiente elegido para el proyecto es **Minecraft Java Edition**, ejecutado en un servidor **Spigot** con el plugin **RaspberryJuice**, lo que permite el control mediante scripts en **Python** a través de la librería `mcpi`.  

Este entorno nos proporciona un mundo tridimensional interactivo donde es posible colocar y quitar bloques, mover agentes, y diseñar escenarios experimentales como laberintos controlados. Además, se complementa con herramientas de análisis y visualización en Python, tales como `matplotlib` y `numpy`, que facilitan la medición de métricas de rendimiento de los algoritmos.

## Componentes del ambiente
- Cliente de **Minecraft Java Edition**  
- Servidor **Spigot** con el plugin **RaspberryJuice**  
- Scripts de **Python 3** para el control del agente (`mcpi`)  
- Librerías auxiliares: `matplotlib`, `numpy`, `csv`  

## Complejidad del ambiente
El ambiente resulta suficientemente complejo para el desarrollo del proyecto, debido a las siguientes características:

- Permite implementar y probar algoritmos de búsqueda clásicos (BFS, DFS, A*, Greedy).  
- Proporciona un entorno gráfico interactivo donde el agente ejecuta los recorridos y las soluciones pueden observarse directamente.  
- Facilita la recolección de métricas relacionadas con la eficiencia de los algoritmos y la comparación entre distintas estrategias.  
- Ofrece flexibilidad para diseñar problemas de navegación de distinta dificultad, como laberintos de diferentes tamaños y configuraciones.  

**Conclusión:** este entorno ofrece la complejidad necesaria para aplicar, comparar y analizar algoritmos de búsqueda en un contexto visual y dinámico, lo que lo hace adecuado para el proyecto.  

---

# 2. Preparación y Configuración del Entorno

Para el desarrollo del proyecto se trabajó con la **versión de Minecraft 1.11**, asegurando compatibilidad entre el servidor Spigot, el plugin RaspberryJuice y la API de Python `mcpi`.  

El repositorio del proyecto mantiene la siguiente organización:

- **servidor**: contiene los archivos necesarios para ejecutar Minecraft (`BuildTools`, `spigot-1.11.jar`, el plugin RaspberryJuice, configuración del servidor).  
- **src**: código fuente en Python que implementa el agente, estrategias de búsqueda y generación de métricas.  

📂 **Repositorio del proyecto:** [enlace-al-repositorio]  
☁️ **OneDrive con dependencias y versiones utilizadas:** [Google Drive](https://drive.google.com/drive/folders/1k0YW0Tz8DlNd0vtrD2Yc2JMkU5tlLdX1?usp=drive_link)

---

## Instalación de dependencias

### Java
Spigot 1.11 requiere **Java JDK 1.8**. Para instalarlo en Windows:

```bash
winget install --id EclipseAdoptium.Temurin.8.JDK
````

Verificar la instalación con:

```bash
java -version
# Resultado esperado:
# openjdk version "1.8.0_xxx"
# OpenJDK Runtime Environment (Temurin) 
# OpenJDK 64-Bit Server VM (Temurin)
```

### Construcción de Spigot

Ubicar `BuildTools.jar` en la carpeta del servidor (`C:\MinecraftAgente\servidor\`) y compilar la versión requerida:

```bash
java -jar BuildTools.jar --rev 1.11
```

Esto generará el archivo `spigot-1.11.jar`, que será utilizado para ejecutar el servidor.

### Python y entorno virtual

Instalar Python 3 en el sistema (si no está disponible). Luego, crear y activar un entorno virtual en la carpeta del proyecto:

```bash
python -m venv venv
venv\Scripts\activate
```

Dentro del entorno virtual, instalar las librerías necesarias:

```bash
pip install mcpi matplotlib numpy
```

---

## Configuración del servidor

### Aceptar el EULA

Antes de la primera ejecución del servidor, editar (o crear) el archivo:

```
C:\MinecraftAgente\servidor\eula.txt
```

con el contenido:

```
eula=true
```

### Plugin RaspberryJuice

El plugin **RaspberryJuice.jar** debe copiarse en:

```
C:\MinecraftAgente\servidor\plugins\
```

Al iniciar el servidor, debe confirmarse en la consola que el plugin fue cargado correctamente.

### server.properties

Para simplificar el escenario de pruebas, modificar el archivo:

```
C:\MinecraftAgente\servidor\server.properties
```

con los siguientes parámetros recomendados:

```
level-type=flat
spawn-monsters=false
spawn-animals=false
difficulty=0
gamemode=1
level-name=laberinto
```

Esto asegura un mundo plano, en creativo, sin mobs ni animales.

---

## Ejecución del servidor

Desde la carpeta del servidor, iniciar con parámetros de memoria:

```bash
java -Xmx1024M -Xms1024M -jar spigot-1.11.jar nogui
```

---

## Conexión desde el cliente Minecraft

Para conectarse al servidor:

1. Abrir **Minecraft Launcher** y seleccionar la versión **1.11**.

2. Ir a **Multijugador** → **Agregar servidor**.

3. Dirección del servidor:

   ```
   localhost:25565
   ```

4. Ingresar al mundo y asegurarse de tener permisos en **modo creativo**.

---

## Ejecución del agente en Python

Con el servidor en ejecución y el jugador conectado, abrir una terminal en la carpeta:

```
C:\MinecraftAgente\src
```

y ejecutar:

```bash
python .\main.py
```

Esto iniciará el agente y permitirá su interacción con el servidor a través del plugin RaspberryJuice.

---

## Estructura de carpetas del proyecto

```plaintext
C:/MinecraftAgente/
├── servidor/
│   ├── BuildTools.jar
│   ├── spigot-1.11.jar
│   ├── plugins/
│   │   └── RaspberryJuice.jar
│   ├── eula.txt
│   └── server.properties
└── src/
    └── main.py
```

```

---

¿Quieres que también le agregue un **índice al inicio con enlaces internos** a cada sección (como suelen tener los README grandes en GitHub)?
```
