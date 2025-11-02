"""
Agente de Aprendizaje por Refuerzo (Q-Learning)
Para recolección de madera en Minecraft usando Malmo

Objetivo: Conseguir 3 bloques de madera (log) picando árboles

Autor: Sistema de IA
"""

import numpy as np
import random
import pickle
from collections import defaultdict


class AgenteMaderaQLearning:
    """
    Agente que aprende mediante Q-Learning a recolectar madera
    usando información de la rejilla de bloques e inventario
    """
    
    # Acciones disponibles (índices)
    ACCIONES = {
        0: "move 1",           # Avanzar
        1: "turn 1",           # Girar derecha 90°
        2: "turn -1",          # Girar izquierda 90°
        3: "jumpmove 1",       # Saltar y avanzar
        4: "attack 1",         # Atacar/Picar (mantener)
        5: "strafe 1",         # Moverse a la derecha
        6: "strafe -1",        # Moverse a la izquierda
    }
    
    def __init__(self, 
                 alpha=0.15,      # Tasa de aprendizaje
                 gamma=0.95,      # Factor de descuento
                 epsilon=0.4,     # Tasa de exploración inicial
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
        self.historial_madera_recolectada = []
    
    def obtener_estado_discretizado(self, obs):
        """
        Convierte las observaciones crudas en un estado discreto
        
        Estado = (orientación, madera_visible, madera_en_inventario, 
                  mirando_madera, distancia_a_madera, obstaculo_frente)
        
        Parámetros:
        -----------
        obs: dict
            Observaciones de Malmo (incluye grid, raycast, inventario)
        
        Retorna:
        --------
        tuple: Estado discretizado
        """
        # 1. Orientación (discretizada en 4 direcciones)
        yaw = obs.get("Yaw", 0)
        orientacion = round(yaw / 90) % 4  # 0=Norte, 1=Este, 2=Sur, 3=Oeste
        
        # 2. Analizar rejilla 5x5x5 para detectar madera
        grid = obs.get("near5x5x5", [])
        
        tipos_madera = ["log", "log2", "wood"]  # Diferentes tipos de troncos
        
        madera_visible = 0
        madera_cerca = 0
        hojas_visibles = 0
        
        if len(grid) >= 75:  # Al menos 5x3x5
            for bloque in grid:
                if bloque in tipos_madera:
                    madera_visible = 1
                    madera_cerca += 1
                elif bloque in ["leaves", "leaves2"]:
                    hojas_visibles += 1
        
        # Discretizar cantidad de madera visible
        if madera_cerca == 0:
            nivel_madera = 0
        elif madera_cerca <= 2:
            nivel_madera = 1  # Poca madera
        else:
            nivel_madera = 2  # Mucha madera (árbol completo)
        
        # 3. Inventario - Contar madera recolectada
        inventario = obs.get("inventory", [])
        madera_en_inventario = 0
        
        for item in inventario:
            tipo = item.get("type", "")
            if tipo in tipos_madera:
                madera_en_inventario += item.get("quantity", 0)
        
        # Discretizar inventario (0, 1, 2, 3+)
        if madera_en_inventario == 0:
            nivel_inventario = 0
        elif madera_en_inventario == 1:
            nivel_inventario = 1
        elif madera_en_inventario == 2:
            nivel_inventario = 2
        else:
            nivel_inventario = 3  # 3 o más (objetivo alcanzado)
        
        # 4. Raycast - ¿Está mirando directamente a madera?
        linea_vista = obs.get("LineOfSight", {})
        tipo_mirando = linea_vista.get("type", "air")
        
        mirando_madera = 1 if tipo_mirando in tipos_madera else 0
        
        # 5. Distancia a bloque que mira
        distancia = linea_vista.get("distance", 10.0)
        if distancia < 2.0:
            dist_categoria = 0  # Muy cerca (puede picar)
        elif distancia < 4.0:
            dist_categoria = 1  # Cerca
        else:
            dist_categoria = 2  # Lejos
        
        # 6. Obstáculo al frente (para navegación)
        obstaculo_frente = 0
        if len(grid) >= 38:
            # Bloque justo enfrente
            bloque_frente = grid[37]  # Centro aproximado
            if bloque_frente not in ["air", "tallgrass", "leaves", "leaves2"]:
                obstaculo_frente = 1
        
        # 7. Indicador de hojas (señal de árbol cercano)
        if hojas_visibles > 5:
            indicador_hojas = 2  # Muchas hojas
        elif hojas_visibles > 0:
            indicador_hojas = 1  # Algunas hojas
        else:
            indicador_hojas = 0  # Sin hojas
        
        # Estado final: tupla inmutable
        estado = (
            orientacion,
            nivel_madera,
            nivel_inventario,
            mirando_madera,
            dist_categoria,
            obstaculo_frente,
            indicador_hojas
        )
        
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
            q_siguiente_max = 0
        else:
            q_siguiente_max = np.max(self.Q[siguiente_estado])
        
        # Ecuación de actualización Q-Learning
        nuevo_q = q_actual + self.alpha * (recompensa + self.gamma * q_siguiente_max - q_actual)
        
        self.Q[estado][accion] = nuevo_q
        
        # Acumular estadísticas
        self.recompensa_total_episodio += recompensa
        self.pasos_episodio += 1
    
    def finalizar_episodio(self, madera_recolectada):
        """
        Actualiza estadísticas y decae epsilon al final de un episodio
        
        Parámetros:
        -----------
        madera_recolectada: int
            Cantidad de madera conseguida en el episodio
        """
        self.episodios_completados += 1
        
        # Guardar historial
        self.historial_recompensas.append(self.recompensa_total_episodio)
        self.historial_pasos.append(self.pasos_episodio)
        self.historial_epsilon.append(self.epsilon)
        self.historial_madera_recolectada.append(madera_recolectada)
        
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
            'Q': dict(self.Q),
            'episodios': self.episodios_completados,
            'epsilon': self.epsilon,
            'historial_recompensas': self.historial_recompensas,
            'historial_pasos': self.historial_pasos,
            'historial_epsilon': self.historial_epsilon,
            'historial_madera': self.historial_madera_recolectada
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
            self.historial_madera_recolectada = datos.get('historial_madera', [])
            
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
        
        if len(self.historial_madera_recolectada) > 0:
            print(f"  Madera promedio: {np.mean(self.historial_madera_recolectada[-10:]):.2f}")
        
        print(f"\nMejor episodio:")
        if self.historial_recompensas:
            mejor_idx = np.argmax(self.historial_recompensas)
            print(f"  Episodio #{mejor_idx + 1}")
            print(f"  Recompensa: {self.historial_recompensas[mejor_idx]:.2f}")
            print(f"  Pasos: {self.historial_pasos[mejor_idx]}")
            if len(self.historial_madera_recolectada) > mejor_idx:
                print(f"  Madera recolectada: {self.historial_madera_recolectada[mejor_idx]}")
        
        # Tasa de éxito (3 o más maderas)
        if len(self.historial_madera_recolectada) > 0:
            exitos = sum(1 for m in self.historial_madera_recolectada if m >= 3)
            tasa = 100 * exitos / len(self.historial_madera_recolectada)
            print(f"\nTasa de éxito (3+ maderas): {exitos}/{len(self.historial_madera_recolectada)} ({tasa:.1f}%)")
        
        print("="*60 + "\n")
