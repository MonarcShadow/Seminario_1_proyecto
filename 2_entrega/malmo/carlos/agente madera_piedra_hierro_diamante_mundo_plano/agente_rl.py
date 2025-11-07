"""
Agente de Aprendizaje por Refuerzo Multi-Objetivo
Progresión: Madera → Piedra → Hierro → Diamante

Autor: Sistema de IA
Fecha: Noviembre 2025
"""

import numpy as np
import random
import json
import pickle
from collections import defaultdict


class AgenteQLearningProgresivo:
    """
    Agente Q-Learning que progresa a través de múltiples objetivos jerárquicos:
    1. Recolectar 3 madera
    2. Recolectar 3 piedra (con pico de madera)
    3. Recolectar 3 hierro (con pico de piedra)
    4. Recolectar 1 diamante (con pico de hierro)
    """
    
    # Acciones disponibles (balanceadas para mejor exploración)
    ACCIONES = {
        0: "move 1",      # Avanzar
        1: "move 1",      # Avanzar (duplicado para favorecer movimiento)
        2: "turn 0.5",    # Girar derecha 45° (más suave)
        3: "turn -0.5",   # Girar izquierda 45° (más suave)
        4: "jumpmove 1",  # Saltar y avanzar
        5: "attack 1",    # Picar bloque
        6: "attack 1",    # Picar (duplicado para favorecer ataque)
        7: "pitch 0.3",   # Mirar poco arriba (para bloques elevados)
        8: "pitch -0.3",  # Mirar poco abajo (para bloques bajos)
    }
    
    # Fases del objetivo
    FASES = {
        0: "MADERA",      # Recolectar 3 madera
        1: "PIEDRA",      # Recolectar 3 piedra
        2: "HIERRO",      # Recolectar 3 hierro
        3: "DIAMANTE",    # Recolectar 1 diamante
    }
    
    def __init__(self, 
                 alpha=0.1,
                 gamma=0.95,
                 epsilon=0.4,
                 epsilon_min=0.05,
                 epsilon_decay=0.995):
        """
        Parámetros:
        -----------
        alpha: float - Tasa de aprendizaje
        gamma: float - Factor de descuento
        epsilon: float - Exploración inicial
        epsilon_min: float - Mínimo epsilon
        epsilon_decay: float - Decaimiento de epsilon
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Tabla Q separada por fase (para mejor aprendizaje modular)
        self.q_tables = {
            0: defaultdict(lambda: defaultdict(float)),  # Q-table para MADERA
            1: defaultdict(lambda: defaultdict(float)),  # Q-table para PIEDRA
            2: defaultdict(lambda: defaultdict(float)),  # Q-table para HIERRO
            3: defaultdict(lambda: defaultdict(float)),  # Q-table para DIAMANTE
        }
        
        self.episodios_completados = 0
        
        # Parámetros adaptativos por fase
        self.parametros_fase = {
            0: {"alpha": 0.1, "epsilon": 0.4, "recompensa_mult": 1.0},
            1: {"alpha": 0.12, "epsilon": 0.35, "recompensa_mult": 1.2},
            2: {"alpha": 0.15, "epsilon": 0.3, "recompensa_mult": 1.5},
            3: {"alpha": 0.2, "epsilon": 0.25, "recompensa_mult": 2.0},
        }
    
    def obtener_estado_discretizado(self, obs, fase_actual):
        """
        Crea un estado discretizado a partir de las observaciones
        
        Estado incluye:
        - Orientación del agente (0-3: N, E, S, O)
        - Material objetivo cerca (bool)
        - Material objetivo frente (bool)
        - Distancia al objetivo (0: lejos, 1: medio, 2: cerca)
        - Obstáculo frente (bool)
        - Aire frente (bool)
        - Tiene suficiente material (bool)
        - Altura relativa (0: bajo, 1: nivel, 2: alto)
        - Mirando objetivo (bool)
        - Ángulo vertical (0: abajo, 1: frente, 2: arriba)
        - Fase actual (0-3)
        - Herramienta correcta (bool)
        
        Returns:
        --------
        tuple: Estado discretizado (12 dimensiones)
        """
        
        # Extraer datos de observación
        yaw = obs.get('Yaw', 0)
        pitch = obs.get('Pitch', 0)
        xpos = obs.get('XPos', 0)
        ypos = obs.get('YPos', 0)
        zpos = obs.get('ZPos', 0)
        
        # 1. Orientación (0-3: Norte, Este, Sur, Oeste)
        orientacion = int((yaw + 45) / 90) % 4
        
        # 2. Ángulo vertical (0: abajo >30°, 1: frente -30 a 30°, 2: arriba <-30°)
        if pitch > 30:
            angulo_vertical = 0  # Mirando abajo
        elif pitch < -30:
            angulo_vertical = 2  # Mirando arriba
        else:
            angulo_vertical = 1  # Mirando al frente
        
        # Determinar qué material buscar según la fase
        materiales_objetivo = self._obtener_materiales_objetivo(fase_actual)
        
        # 3-5. Detección de material objetivo
        material_cerca = False
        material_frente = False
        distancia_material = 0
        mirando_material = False
        
        # Analizar rejilla 5x5x5 (125 bloques)
        grid = obs.get('floor3x3', [])
        if len(grid) == 125:
            material_cerca, material_frente, distancia_material, mirando_material = \
                self._analizar_grid_material(grid, orientacion, materiales_objetivo)
        
        # 6-7. Obstáculos y aire frente
        obstaculo_frente = False
        aire_frente = False
        if len(grid) >= 66:  # Centro de la capa media
            bloque_frente_centro = grid[65]  # Índice del bloque justo frente
            if bloque_frente_centro in materiales_objetivo:
                pass  # No es obstáculo, es objetivo
            elif bloque_frente_centro == 'air':
                aire_frente = True
            else:
                obstaculo_frente = True
        
        # 8. Verificar si tiene suficiente material
        tiene_suficiente = self._verificar_inventario_suficiente(obs, fase_actual)
        
        # 9. Altura relativa (comparar con spawn ~64)
        altura_spawn = 64
        if ypos < altura_spawn - 2:
            altura = 0  # Bajo
        elif ypos > altura_spawn + 2:
            altura = 2  # Alto
        else:
            altura = 1  # Nivel
        
        # 10. Herramienta correcta equipada
        herramienta_correcta = self._verificar_herramienta_correcta(obs, fase_actual)
        
        # Construir tupla de estado (12 dimensiones)
        estado = (
            orientacion,           # 0-3
            int(material_cerca),   # 0-1
            int(material_frente),  # 0-1
            distancia_material,    # 0-2
            int(obstaculo_frente), # 0-1
            int(aire_frente),      # 0-1
            int(tiene_suficiente), # 0-1
            altura,                # 0-2
            int(mirando_material), # 0-1
            angulo_vertical,       # 0-2
            fase_actual,           # 0-3
            int(herramienta_correcta), # 0-1
        )
        
        return estado
    
    def _obtener_materiales_objetivo(self, fase):
        """Retorna lista de materiales a buscar según la fase"""
        if fase == 0:  # MADERA
            return ['log', 'log2', 'oak_wood', 'spruce_wood', 'birch_wood', 
                    'jungle_wood', 'acacia_wood', 'dark_oak_wood']
        elif fase == 1:  # PIEDRA
            return ['stone', 'cobblestone']
        elif fase == 2:  # HIERRO
            return ['iron_ore']
        elif fase == 3:  # DIAMANTE
            return ['diamond_ore']
        return []
    
    def _analizar_grid_material(self, grid, orientacion, materiales_objetivo):
        """
        Analiza la rejilla 5x5x5 buscando materiales objetivo
        
        Returns:
        --------
        tuple: (material_cerca, material_frente, distancia, mirando_material)
        """
        material_cerca = False
        material_frente = False
        distancia_material = 0  # 0: lejos, 1: medio, 2: cerca
        mirando_material = False
        
        # Mapeo de orientación a dirección de búsqueda
        # 0: Norte (-Z), 1: Este (+X), 2: Sur (+Z), 3: Oeste (-X)
        
        # Índices de la rejilla (5x5x5 = 125 bloques)
        # Centro: (2, 2, 2) = índice 62
        # Capa Y=0 (inferior): 0-24
        # Capa Y=1 (media inferior): 25-49
        # Capa Y=2 (centro): 50-74
        # Capa Y=3 (media superior): 75-99
        # Capa Y=4 (superior): 100-124
        
        # Buscar en capa central y adyacentes
        for y_offset in range(5):
            for x in range(5):
                for z in range(5):
                    idx = y_offset * 25 + z * 5 + x
                    if idx >= len(grid):
                        continue
                    
                    bloque = grid[idx]
                    if bloque in materiales_objetivo:
                        material_cerca = True
                        
                        # Calcular distancia Manhattan desde centro (2,2,2)
                        dist = abs(x - 2) + abs(y_offset - 2) + abs(z - 2)
                        
                        if dist <= 2:
                            distancia_material = 2  # Muy cerca
                        elif dist <= 4:
                            distancia_material = max(distancia_material, 1)  # Medio
                        
                        # Verificar si está frente según orientación
                        if orientacion == 0 and z < 2 and abs(x - 2) <= 1:  # Norte
                            material_frente = True
                            if x == 2 and z == 1:
                                mirando_material = True
                        elif orientacion == 1 and x > 2 and abs(z - 2) <= 1:  # Este
                            material_frente = True
                            if z == 2 and x == 3:
                                mirando_material = True
                        elif orientacion == 2 and z > 2 and abs(x - 2) <= 1:  # Sur
                            material_frente = True
                            if x == 2 and z == 3:
                                mirando_material = True
                        elif orientacion == 3 and x < 2 and abs(z - 2) <= 1:  # Oeste
                            material_frente = True
                            if z == 2 and x == 1:
                                mirando_material = True
        
        return material_cerca, material_frente, distancia_material, mirando_material
    
    def _verificar_inventario_suficiente(self, obs, fase):
        """Verifica si tiene suficiente material para la fase actual"""
        cantidad_requerida = {
            0: 3,  # 3 madera
            1: 3,  # 3 piedra
            2: 3,  # 3 hierro
            3: 1,  # 1 diamante
        }
        
        materiales = self._obtener_materiales_objetivo(fase)
        count = 0
        
        # Contar en inventario (slots 0-44)
        for slot in range(45):
            item_key = f'InventorySlot_{slot}_item'
            size_key = f'InventorySlot_{slot}_size'
            
            if item_key in obs:
                item = obs[item_key]
                size = obs.get(size_key, 1)
                
                # Caso especial: hierro se convierte a lingote
                if fase == 2 and item == 'iron_ingot':
                    count += size
                elif item in materiales:
                    count += size
        
        return count >= cantidad_requerida.get(fase, 999)
    
    def _verificar_herramienta_correcta(self, obs, fase):
        """Verifica si tiene la herramienta correcta equipada en hotbar"""
        herramientas_requeridas = {
            0: None,  # Madera: no requiere herramienta (mano)
            1: 'wooden_pickaxe',  # Piedra: pico de madera
            2: 'stone_pickaxe',   # Hierro: pico de piedra
            3: 'iron_pickaxe',    # Diamante: pico de hierro
        }
        
        herramienta_req = herramientas_requeridas.get(fase)
        if herramienta_req is None:
            return True  # No requiere herramienta
        
        # Buscar en hotbar (slots 0-8)
        for slot in range(9):
            item_key = f'InventorySlot_{slot}_item'
            if item_key in obs:
                if obs[item_key] == herramienta_req:
                    return True
        
        return False
    
    def elegir_accion(self, estado, fase_actual, epsilon_override=None):
        """
        Epsilon-greedy: explora o explota según epsilon
        Usa parámetros adaptativos según la fase
        """
        epsilon = epsilon_override if epsilon_override is not None else self.epsilon
        
        # Ajustar epsilon según la fase
        epsilon_fase = self.parametros_fase[fase_actual]["epsilon"]
        epsilon_ajustado = min(epsilon, epsilon_fase)
        
        if random.random() < epsilon_ajustado:
            # Exploración: acción aleatoria
            return random.randint(0, len(self.ACCIONES) - 1)
        else:
            # Explotación: mejor acción conocida
            q_table = self.q_tables[fase_actual]
            q_values = q_table[estado]
            
            if not q_values:
                return random.randint(0, len(self.ACCIONES) - 1)
            
            # Elegir acción con mayor Q-value
            max_q = max(q_values.values())
            mejores_acciones = [a for a, q in q_values.items() if q == max_q]
            return random.choice(mejores_acciones)
    
    def actualizar_q(self, estado, accion, recompensa, siguiente_estado, fase_actual, done=False):
        """
        Actualiza Q-value usando la ecuación de Q-Learning
        Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
        """
        q_table = self.q_tables[fase_actual]
        
        # Ajustar alpha según la fase
        alpha = self.parametros_fase[fase_actual]["alpha"]
        
        # Q-value actual
        q_actual = q_table[estado][accion]
        
        # Máximo Q-value del siguiente estado
        if done:
            max_q_siguiente = 0
        else:
            q_siguiente = q_table[siguiente_estado]
            max_q_siguiente = max(q_siguiente.values()) if q_siguiente else 0
        
        # Actualización Q-Learning
        nuevo_q = q_actual + alpha * (recompensa + self.gamma * max_q_siguiente - q_actual)
        q_table[estado][accion] = nuevo_q
    
    def decaer_epsilon(self):
        """Reduce epsilon después de cada episodio"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.episodios_completados += 1
    
    def guardar_modelo(self, ruta):
        """Guarda las Q-tables y parámetros"""
        modelo = {
            'q_tables': {k: dict(v) for k, v in self.q_tables.items()},
            'epsilon': self.epsilon,
            'episodios': self.episodios_completados,
            'parametros_fase': self.parametros_fase,
        }
        
        with open(ruta, 'wb') as f:
            pickle.dump(modelo, f)
        
        print(f"✓ Modelo guardado en {ruta}")
    
    def cargar_modelo(self, ruta):
        """Carga Q-tables y parámetros desde archivo"""
        try:
            with open(ruta, 'rb') as f:
                modelo = pickle.load(f)
            
            # Convertir de vuelta a defaultdict
            self.q_tables = {
                k: defaultdict(lambda: defaultdict(float), v)
                for k, v in modelo['q_tables'].items()
            }
            self.epsilon = modelo['epsilon']
            self.episodios_completados = modelo['episodios']
            self.parametros_fase = modelo.get('parametros_fase', self.parametros_fase)
            
            print(f"✓ Modelo cargado desde {ruta}")
            print(f"  Episodios completados: {self.episodios_completados}")
            print(f"  Epsilon actual: {self.epsilon:.4f}")
            return True
        except FileNotFoundError:
            print(f"⚠ No se encontró modelo en {ruta}")
            return False
    
    def obtener_estadisticas(self):
        """Retorna estadísticas de las Q-tables"""
        stats = {}
        for fase, q_table in self.q_tables.items():
            fase_nombre = self.FASES[fase]
            num_estados = len(q_table)
            num_pares = sum(len(acciones) for acciones in q_table.values())
            stats[fase_nombre] = {
                'estados': num_estados,
                'pares_estado_accion': num_pares
            }
        
        return stats
