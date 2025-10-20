"""
Wrapper del Entorno Malmo para RL
Maneja la comunicación con Minecraft y sistema de recompensas

Autor: Sistema de IA
"""

import json
import time


class EntornoMalmo:
    """
    Entorno de Aprendizaje por Refuerzo sobre Malmo
    Proporciona interfaz similar a OpenAI Gym
    """
    
    def __init__(self, agent_host):
        """
        Parámetros:
        -----------
        agent_host: MalmoPython.AgentHost
            Instancia del agente de Malmo
        """
        self.agent_host = agent_host
        self.world_state = None
        self.estado_previo = None
        self.arena_previa = 0
        self.posicion_previa = (0, 0, 0)
        
        # Historial para detectar loops
        self.historial_acciones = []  # Últimas N acciones
        self.pasos_sin_movimiento = 0  # Contador de pasos sin cambio de posición
        
    def calcular_recompensa(self, obs, accion, recompensa_malmo=0.0):
        """
        Sistema de recompensas diseñado para guiar al agente hacia el agua
        
        RECOMPENSAS:
        +100  → Tocar agua (de Malmo - RewardForTouchingBlockType) ¡ÉXITO!
        +10   → Acercarse a arena (indicador de agua)
        +5    → Descubrir área nueva
        +3    → Moverse exitosamente (cambio de posición)
        +2    → Moverse hacia zona más baja (agua suele estar abajo)
        -0.5  → Costo por acción (de Malmo)
        +100  → Tocar agua (de Malmo - RewardForTouchingBlockType)
        -5    → Colisión/obstáculo
        -20   → Loop detectado (giros repetidos sin movimiento)
        -30   → Atascado completamente (muchos pasos sin movimiento)
        -15   → Alejarse de arena una vez detectada
        
        Parámetros:
        -----------
        obs: dict
            Observaciones actuales
        accion: str
            Comando ejecutado
        recompensa_malmo: float
            Recompensa acumulada de Malmo en este paso
        
        Retorna:
        --------
        float: Recompensa calculada
        """
        # 1. USAR RECOMPENSA DE MALMO (prioridad máxima)
        # Si Malmo da +100, es porque tocó agua → ¡ÉXITO!
        if recompensa_malmo >= 100.0:
            print("🎉 ¡AGUA TOCADA! Recompensa de Malmo detectada")
            return recompensa_malmo
        
        # Recompensa base incluye el costo por acción de Malmo (-0.5)
        recompensa = recompensa_malmo  # Ya incluye -0.5 por comando
        
        # 2. SEÑAL DE PROXIMIDAD: Arena indica cercanía a agua
        grid = obs.get("near5x3x5", [])
        arena_actual = sum(1 for bloque in grid if bloque == "sand")
        
        # Eliminar detección manual de agua (ahora Malmo lo maneja)
        # 3. SEÑAL DE PROXIMIDAD: Arena indica cercanía a agua
        
        if arena_actual > self.arena_previa:
            # Encontramos MÁS arena → vamos bien
            recompensa += 10.0
        elif arena_actual > 0 and arena_actual < self.arena_previa:
            # Nos ALEJAMOS de arena → penalización
            recompensa -= 15.0
        elif arena_actual > 0:
            # Mantenemos arena visible → pequeño bonus
            recompensa += 2.0
        
        self.arena_previa = arena_actual
        
        # 3. DETECTAR MOVIMIENTO REAL
        x = obs.get("XPos", 0)
        y = obs.get("YPos", 64)
        z = obs.get("ZPos", 0)
        posicion_actual = (round(x, 1), round(y, 1), round(z, 1))
        
        # Calcular si hubo movimiento significativo
        distancia = ((posicion_actual[0] - self.posicion_previa[0])**2 + 
                    (posicion_actual[2] - self.posicion_previa[2])**2)**0.5
        
        if distancia > 0.3:  # Se movió al menos 0.3 bloques
            # ✅ MOVIMIENTO EXITOSO
            recompensa += 3.0
            self.pasos_sin_movimiento = 0
            
            # Bonus por explorar hacia abajo (agua suele estar en Y bajo)
            if y < self.posicion_previa[1]:
                recompensa += 2.0
        else:
            # ❌ NO SE MOVIÓ
            self.pasos_sin_movimiento += 1
            
            # Agregar acción al historial
            self.historial_acciones.append(accion)
            if len(self.historial_acciones) > 10:
                self.historial_acciones.pop(0)
            
            # DETECTAR LOOP: Si lleva muchos giros consecutivos
            if self.pasos_sin_movimiento > 3:
                # Revisar si está alternando entre giros
                ultimas_3 = self.historial_acciones[-3:]
                if all("turn" in a for a in ultimas_3):
                    recompensa -= 20.0  # CASTIGO FUERTE por loop de giros
            
            # ATASCADO COMPLETAMENTE
            if self.pasos_sin_movimiento > 8:
                recompensa -= 30.0  # CASTIGO MUY FUERTE
                
            # Penalización progresiva por quedarse quieto
            recompensa -= (2.0 * self.pasos_sin_movimiento)
        
        self.posicion_previa = posicion_actual
        
        # 4. INCENTIVAR INTENTOS DE MOVIMIENTO después de giros
        # Si acaba de girar, la siguiente acción DEBE ser move o jumpmove
        if len(self.historial_acciones) >= 2:
            ultima = self.historial_acciones[-1] if len(self.historial_acciones) > 0 else ""
            penultima = self.historial_acciones[-2] if len(self.historial_acciones) > 1 else ""
            
            # Si giró en la acción anterior y ahora intenta moverse → BONUS
            if "turn" in penultima and ("move" in accion or "jumpmove" in accion):
                recompensa += 5.0  # Recompensar intentar avanzar después de girar
        
        # 5. PENALIZACIÓN POR OBSTÁCULOS (solo si intentó moverse y no lo logró)
        if ("move" in accion or "jumpmove" in accion) and distancia < 0.1:
            # Intentó moverse pero no se movió → hay obstáculo
            recompensa -= 5.0
        
        # 6. RECOMPENSA POR VARIEDAD DE BLOQUES (exploración)
        tipos_unicos = len(set(grid))
        if tipos_unicos > 3:
            recompensa += 1.0  # Bonus por descubrir área diversa
        
        return recompensa
    
    def obtener_observacion(self):
        """
        Extrae observaciones del world_state actual
        
        Retorna:
        --------
        dict: Observaciones parseadas o None si no hay datos
        """
        if self.world_state is None:
            return None
        
        if self.world_state.number_of_observations_since_last_state > 0:
            obs_text = self.world_state.observations[-1].text
            obs = json.loads(obs_text)
            return obs
        
        return None
    
    def ejecutar_accion(self, comando, duracion=0.5):
        """
        Envía comando al agente y espera respuesta
        
        Parámetros:
        -----------
        comando: str
            Comando de Malmo (ej: "move 1", "turn 1")
        duracion: float
            Tiempo de espera después del comando
        """
        self.agent_host.sendCommand(comando)
        time.sleep(duracion)
        
        # Detener movimiento continuo
        if "move" in comando:
            time.sleep(0.1)
            # No detener explícitamente para comandos discretos
    
    def actualizar_world_state(self):
        """
        Actualiza el world_state obteniendo el estado actual de Malmo
        
        Retorna:
        --------
        bool: True si la misión sigue corriendo, False si terminó
        """
        self.world_state = self.agent_host.getWorldState()
        
        # Verificar errores
        for error in self.world_state.errors:
            print(f"❌ Error Malmo: {error.text}")
        
        return self.world_state.is_mission_running
    
    def verificar_agua_encontrada(self, obs, recompensa_malmo=0.0):
        """
        Verifica si el agente encontró agua usando recompensas de Malmo
        
        Parámetros:
        -----------
        obs: dict
            Observaciones actuales
        recompensa_malmo: float
            Recompensa de Malmo (si es >= 100, tocó agua)
        
        Retorna:
        --------
        bool: True si tocó agua (recompensa de Malmo >= 100)
        """
        # MÉTODO PRINCIPAL: Usar recompensa de Malmo (más confiable)
        if recompensa_malmo >= 100.0:
            print("💧 ¡AGUA TOCADA! (confirmado por RewardForTouchingBlockType)")
            return True
        
        # MÉTODO ALTERNATIVO: Revisar grid (solo para monitoreo, no decisión)
        if obs is None:
            return False
        
        grid = obs.get("near5x3x5", [])
        agua_en_grid = any(
            bloque in ["water", "flowing_water", "stationary_water"]
            for bloque in grid
        )
        
        if agua_en_grid:
            print("👀 Agua visible en grid (cerca pero no tocada aún)")
        
        return False  # Solo retorna True si TOCÓ agua (recompensa de Malmo)
    
    def reset(self):
        """
        Resetea el entorno (para nuevos episodios)
        """
        self.estado_previo = None
        self.arena_previa = 0
        self.posicion_previa = (0, 0, 0)
        self.historial_acciones = []
        self.pasos_sin_movimiento = 0
