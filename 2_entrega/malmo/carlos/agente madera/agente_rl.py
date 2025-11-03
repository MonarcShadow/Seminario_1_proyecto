"""
Agente de Aprendizaje por Refuerzo (Q-Learning)
Para búsqueda y recolección de madera en Minecraft usando Malmo

Autor: Sistema de IA
"""

import numpy as np
import random
import json
import pickle
from collections import defaultdict


class AgenteQLearning:
    """
    Agente que aprende mediante Q-Learning a encontrar y recolectar madera
    usando información de la rejilla 5x3x5 de bloques
    """
    
    # Acciones disponibles (índices)
    ACCIONES = {
        0: "move 1",      # Avanzar
        1: "turn 1",      # Girar derecha 90°
        2: "turn -1",     # Girar izquierda 90°
        3: "jumpmove 1",  # Saltar y avanzar
        4: "attack 1",    # Picar bloque (mantener presionado)
    }
    
    def __init__(self, 
                 alpha=0.1,      # Tasa de aprendizaje
                 gamma=0.95,     # Factor de descuento
                 epsilon=0.3,    # Tasa de exploración inicial
                 epsilon_min=0.05,
                 epsilon_decay=0.995):
        """
        Parámetros:
        -----------
        alpha: float
            Tasa de aprendizaje (learning rate)
        gamma: float
            Factor de descuento (discount factor)
        epsilon: float
            Tasa de exploración (exploration rate)
        epsilon_min: float
            Mínimo valor de epsilon
        epsilon_decay: float
            Tasa de decaimiento de epsilon por episodio
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Tabla Q: Q[estado][acción] = valor
        self.Q = defaultdict(lambda: np.zeros(len(self.ACCIONES)))
        
        # Estadísticas
        self.episodios_completados = 0
        self.recompensa_total_episodio = 0
        self.pasos_episodio = 0
        
        # Historial
        self.historial_recompensas = []
        self.historial_pasos = []
        self.historial_epsilon = []
    
    def obtener_estado_discretizado(self, obs):
        """
        Convierte las observaciones crudas en un estado discreto
        
        Estado = (orientación, madera_cerca, madera_frente, distancia_madera, 
                  obstaculo_frente, tiene_madera_inventario, altura_relativa)
        
        Parámetros:
        -----------
        obs: dict
            Observaciones de Malmo (incluye grid, posición, inventario, etc.)
        
        Retorna:
        --------
        tuple: Estado discretizado
        """
        # 1. Orientación (discretizada en 4 direcciones)
        yaw = obs.get("Yaw", 0)
        orientacion = round(yaw / 90) % 4  # 0=Norte, 1=Este, 2=Sur, 3=Oeste
        
        # 2. Analizar rejilla 5x3x5
        grid = obs.get("near5x3x5", [])
        
        # Tipos de madera en Minecraft 1.11.2
        TIPOS_MADERA = [
            "log", "log2",  # Troncos
            "planks",       # Tablas (por si acaso)
        ]
        
        # Contar tipos de bloques relevantes
        madera_cerca = 0
        madera_frente = 0
        obstaculo_frente = 0
        aire_frente = 0
        distancia_madera = 3  # 0=muy cerca, 1=cerca, 2=lejos, 3=no visible
        
        if len(grid) == 75:  # 5x3x5 = 75 bloques
            # Centro del grid es el agente (índice 37)
            
            # Detectar madera en el grid
            for i, bloque in enumerate(grid):
                if any(madera in bloque for madera in TIPOS_MADERA):
                    madera_cerca = 1
                    
                    # Calcular distancia aproximada al bloque de madera
                    # Convertir índice a coordenadas 3D en el grid
                    x = (i % 5) - 2  # -2 a 2
                    y = ((i // 5) % 3) - 1  # -1 a 1
                    z = (i // 15) - 2  # -2 a 2
                    dist = abs(x) + abs(y) + abs(z)  # Distancia Manhattan
                    
                    if dist <= 2:
                        distancia_madera = 0  # Muy cerca (puede picar)
                    elif dist <= 4:
                        distancia_madera = 1  # Cerca (acercarse)
                    else:
                        distancia_madera = 2  # Lejos
            
            # Detectar madera justo al frente (según orientación)
            # Para poder picar, necesita estar mirando al bloque
            if orientacion == 0:  # Norte (Z-)
                indices_frente = [32, 27, 22]  # Frente en diferentes alturas
            elif orientacion == 1:  # Este (X+)
                indices_frente = [38, 33, 28]
            elif orientacion == 2:  # Sur (Z+)
                indices_frente = [42, 47, 52]
            else:  # Oeste (X-)
                indices_frente = [36, 31, 26]
            
            # Bloques que NO son obstáculos (se pueden atravesar)
            BLOQUES_ATRAVESABLES = [
                "air", "tallgrass", "double_plant", "red_flower", "yellow_flower",
                "leaves", "leaves2", "vine", "waterlily", "snow_layer", "web"
            ]
            
            for idx in indices_frente:
                if idx < len(grid):
                    bloque_frente = grid[idx]
                    if any(madera in bloque_frente for madera in TIPOS_MADERA):
                        madera_frente = 1
                        distancia_madera = 0  # Puede picar
                        break
                    elif bloque_frente == "air":
                        aire_frente = 1
                    elif not any(atravesable in bloque_frente for atravesable in BLOQUES_ATRAVESABLES):
                        # Solo es obstáculo si NO está en la lista de atravesables
                        obstaculo_frente = 1
        
        # 3. Verificar inventario (si ya recogió madera)
        inventario = obs.get("inventory", [])
        tiene_madera = 0
        for item in inventario:
            item_type = item.get("type", "").lower()
            # Detectar log, log2, planks, oak_wood, etc.
            if "log" in item_type or "wood" in item_type or "plank" in item_type:
                tiene_madera = 1
                break
        
        # 4. Altura relativa (útil para navegación)
        y_pos = obs.get("YPos", 64)
        if y_pos < 60:
            altura = 0  # Bajo
        elif y_pos < 70:
            altura = 1  # Medio
        else:
            altura = 2  # Alto
        
        # 5. Detectar si está mirando un bloque de madera (LineOfSight)
        line_of_sight = obs.get("LineOfSight", {})
        mirando_madera = 0
        if isinstance(line_of_sight, dict):
            tipo_bloque = line_of_sight.get("type", "")
            if any(madera in tipo_bloque for madera in TIPOS_MADERA):
                mirando_madera = 1
        
        # Estado final: tupla inmutable para usar como clave
        estado = (orientacion, madera_cerca, madera_frente, distancia_madera, 
                  obstaculo_frente, aire_frente, tiene_madera, altura, mirando_madera)
        
        return estado
    
    def elegir_accion(self, estado):
        """
        Política ε-greedy: exploración vs explotación
        
        Parámetros:
        -----------
        estado: tuple
            Estado actual discretizado
        
        Retorna:
        --------
        int: Índice de la acción elegida
        """
        # Exploración: acción aleatoria
        if random.random() < self.epsilon:
            return random.randint(0, len(self.ACCIONES) - 1)
        
        # Explotación: mejor acción conocida
        valores_q = self.Q[estado]
        max_q = np.max(valores_q)
        
        # Si hay empate, elegir aleatoriamente entre las mejores
        mejores_acciones = np.where(valores_q == max_q)[0]
        return np.random.choice(mejores_acciones)
    
    def actualizar_q(self, estado, accion, recompensa, siguiente_estado, terminado):
        """
        Actualiza la tabla Q usando la ecuación de Q-Learning
        
        Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]
        
        Parámetros:
        -----------
        estado: tuple
            Estado actual
        accion: int
            Acción tomada
        recompensa: float
            Recompensa recibida
        siguiente_estado: tuple
            Estado resultante
        terminado: bool
            Si el episodio terminó
        """
        q_actual = self.Q[estado][accion]
        
        if terminado:
            # Si terminó, no hay siguiente estado
            q_siguiente_max = 0
        else:
            q_siguiente_max = np.max(self.Q[siguiente_estado])
        
        # Ecuación de actualización Q-Learning
        nuevo_q = q_actual + self.alpha * (recompensa + self.gamma * q_siguiente_max - q_actual)
        
        self.Q[estado][accion] = nuevo_q
        
        # Acumular estadísticas
        self.recompensa_total_episodio += recompensa
        self.pasos_episodio += 1
    
    def finalizar_episodio(self):
        """
        Actualiza estadísticas y decae epsilon al final de un episodio
        """
        self.episodios_completados += 1
        
        # Guardar historial
        self.historial_recompensas.append(self.recompensa_total_episodio)
        self.historial_pasos.append(self.pasos_episodio)
        self.historial_epsilon.append(self.epsilon)
        
        # Decaer epsilon (menos exploración con el tiempo)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        # Resetear contadores
        self.recompensa_total_episodio = 0
        self.pasos_episodio = 0
    
    def obtener_comando(self, accion_idx):
        """
        Convierte índice de acción a comando de Malmo
        
        Parámetros:
        -----------
        accion_idx: int
            Índice de la acción
        
        Retorna:
        --------
        str: Comando para Malmo
        """
        return self.ACCIONES[accion_idx]
    
    def guardar_modelo(self, filepath):
        """Guarda la tabla Q y parámetros del agente"""
        datos = {
            'Q': dict(self.Q),  # Convertir defaultdict a dict
            'episodios': self.episodios_completados,
            'epsilon': self.epsilon,
            'historial_recompensas': self.historial_recompensas,
            'historial_pasos': self.historial_pasos,
            'historial_epsilon': self.historial_epsilon
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(datos, f)
        
        print(f"✓ Modelo guardado en: {filepath}")
    
    def cargar_modelo(self, filepath):
        """Carga tabla Q y parámetros previamente guardados"""
        try:
            with open(filepath, 'rb') as f:
                datos = pickle.load(f)
            
            self.Q = defaultdict(lambda: np.zeros(len(self.ACCIONES)), datos['Q'])
            self.episodios_completados = datos['episodios']
            self.epsilon = datos['epsilon']
            self.historial_recompensas = datos['historial_recompensas']
            self.historial_pasos = datos['historial_pasos']
            self.historial_epsilon = datos['historial_epsilon']
            
            print(f"✓ Modelo cargado desde: {filepath}")
            print(f"  Episodios previos: {self.episodios_completados}")
            print(f"  Epsilon actual: {self.epsilon:.4f}")
            
        except FileNotFoundError:
            print(f"⚠ No se encontró archivo: {filepath}")
            print("  Iniciando con tabla Q vacía")
    
    def imprimir_estadisticas(self):
        """Muestra estadísticas del entrenamiento"""
        if len(self.historial_recompensas) == 0:
            print("Sin estadísticas aún")
            return
        
        print("\n" + "="*60)
        print(f"📊 ESTADÍSTICAS DE ENTRENAMIENTO")
        print("="*60)
        print(f"Episodios completados: {self.episodios_completados}")
        print(f"Estados en tabla Q: {len(self.Q)}")
        print(f"Epsilon actual: {self.epsilon:.4f}")
        print(f"\nÚltimos 10 episodios:")
        print(f"  Recompensa promedio: {np.mean(self.historial_recompensas[-10:]):.2f}")
        print(f"  Pasos promedio: {np.mean(self.historial_pasos[-10:]):.2f}")
        print(f"\nMejor episodio:")
        if self.historial_recompensas:
            mejor_idx = np.argmax(self.historial_recompensas)
            print(f"  Episodio #{mejor_idx + 1}")
            print(f"  Recompensa: {self.historial_recompensas[mejor_idx]:.2f}")
            print(f"  Pasos: {self.historial_pasos[mejor_idx]}")
        print("="*60 + "\n")
