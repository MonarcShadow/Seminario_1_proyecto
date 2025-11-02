"""
Wrapper del Entorno Malmo para recolección de madera
Maneja la comunicación con Minecraft y sistema de recompensas

Autor: Sistema de IA
"""

import json
import time


class EntornoMadera:
    """
    Entorno de Aprendizaje por Refuerzo sobre Malmo
    Especializado en recolección de madera
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
        self.madera_previa = 0
        self.posicion_previa = (0, 0, 0)
        
        # Historial para detectar comportamiento
        self.historial_acciones = []
        self.pasos_sin_movimiento = 0
        self.pasos_picando = 0
        self.ultimo_bloque_mirando = None
        
    def calcular_recompensa(self, obs, accion, recompensa_malmo=0.0):
        """
        Sistema de recompensas diseñado para guiar al agente a recolectar madera
        
        RECOMPENSAS:
        +100   → Conseguir 1 bloque de madera en inventario ¡ÉXITO PARCIAL!
        +500   → Conseguir 3 bloques de madera ¡OBJETIVO COMPLETADO!
        +30    → Estar picando madera (mirando y atacando)
        +20    → Mirar madera directamente (preparar para picar)
        +10    → Detectar madera en campo visual
        +5     → Detectar hojas (indicador de árbol cercano)
        +3     → Moverse exitosamente (exploración)
        -0.5   → Costo por acción (Malmo)
        -5     → Picar sin mirar madera (desperdicio)
        -10    → Colisión/obstáculo
        -20    → Loop detectado (acciones repetitivas sin progreso)
        -30    → Atascado completamente
        
        Parámetros:
        -----------
        obs: dict
            Observaciones actuales
        accion: str
            Comando ejecutado
        recompensa_malmo: float
            Recompensa de Malmo
        
        Retorna:
        --------
        float: Recompensa calculada
        """
        # Recompensa base (incluye costo de acción de Malmo)
        recompensa = recompensa_malmo
        
        # 1. RECOMPENSA POR MADERA EN INVENTARIO (objetivo principal)
        inventario = obs.get("inventory", [])
        madera_actual = 0
        
        tipos_madera = ["log", "log2", "wood"]
        for item in inventario:
            if item.get("type", "") in tipos_madera:
                madera_actual += item.get("quantity", 0)
        
        # Si consiguió nueva madera
        if madera_actual > self.madera_previa:
            nueva_madera = madera_actual - self.madera_previa
            recompensa += 100.0 * nueva_madera
            print(f"   🎉 ¡+{nueva_madera} MADERA CONSEGUIDA! Total: {madera_actual}/3")
            
            # Bonus extra si completó objetivo
            if madera_actual >= 3:
                recompensa += 500.0
                print(f"   🏆 ¡¡¡OBJETIVO COMPLETADO: 3 MADERAS!!!")
        
        self.madera_previa = madera_actual
        
        # 2. RAYCAST - Analizar qué está mirando
        linea_vista = obs.get("LineOfSight", {})
        tipo_mirando = linea_vista.get("type", "air")
        distancia_mirando = linea_vista.get("distance", 10.0)
        
        mirando_madera = tipo_mirando in tipos_madera
        
        # 3. RECOMPENSA POR PICAR MADERA CORRECTAMENTE
        if "attack" in accion:
            self.pasos_picando += 1
            
            if mirando_madera and distancia_mirando < 5.0:
                # ✅ Está picando madera correctamente
                recompensa += 30.0
                
                # Bonus por persistencia (picar el mismo bloque)
                if tipo_mirando == self.ultimo_bloque_mirando:
                    recompensa += 10.0  # Bonus por consistencia
                
            else:
                # ❌ Está picando aire o algo que no es madera
                recompensa -= 5.0
                self.pasos_picando = 0
        else:
            # No está picando
            self.pasos_picando = 0
        
        self.ultimo_bloque_mirando = tipo_mirando if mirando_madera else None
        
        # 4. RECOMPENSA POR MIRAR MADERA (paso previo a picar)
        if mirando_madera and "attack" not in accion:
            if distancia_mirando < 3.0:
                recompensa += 20.0  # Muy cerca, listo para picar
            elif distancia_mirando < 5.0:
                recompensa += 15.0  # A distancia razonable
            else:
                recompensa += 10.0  # Madera visible pero lejos
        
        # 5. ANÁLISIS DEL GRID - Proximidad a madera
        grid = obs.get("near5x5x5", [])
        madera_en_grid = sum(1 for b in grid if b in tipos_madera)
        hojas_en_grid = sum(1 for b in grid if b in ["leaves", "leaves2"])
        
        if madera_en_grid > 0:
            # Madera en campo visual
            recompensa += 10.0
        elif hojas_en_grid > 5:
            # Muchas hojas = árbol cercano
            recompensa += 5.0
        
        # 6. DETECTAR MOVIMIENTO REAL
        x = obs.get("XPos", 0)
        y = obs.get("YPos", 64)
        z = obs.get("ZPos", 0)
        posicion_actual = (round(x, 1), round(y, 1), round(z, 1))
        
        distancia = ((posicion_actual[0] - self.posicion_previa[0])**2 + 
                    (posicion_actual[2] - self.posicion_previa[2])**2)**0.5
        
        if distancia > 0.3 and "move" in accion:
            # ✅ Movimiento exitoso
            recompensa += 3.0
            self.pasos_sin_movimiento = 0
        elif "move" in accion or "strafe" in accion:
            # ❌ Intentó moverse pero no lo logró
            self.pasos_sin_movimiento += 1
            
            if self.pasos_sin_movimiento > 5:
                recompensa -= 10.0  # Penalización por colisión repetida
        
        self.posicion_previa = posicion_actual
        
        # 7. DETECTAR LOOPS (acciones repetitivas inútiles)
        self.historial_acciones.append(accion)
        if len(self.historial_acciones) > 10:
            self.historial_acciones.pop(0)
        
        if len(self.historial_acciones) >= 6:
            ultimas_6 = self.historial_acciones[-6:]
            
            # Loop de giros
            if all("turn" in a for a in ultimas_6):
                recompensa -= 20.0
            
            # Loop de ataques sin mirar madera
            if all("attack" in a for a in ultimas_6) and not mirando_madera:
                recompensa -= 25.0
        
        # 8. ATASCADO COMPLETAMENTE
        if self.pasos_sin_movimiento > 10:
            recompensa -= 30.0
        
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
    
    def ejecutar_accion(self, comando, duracion=0.3):
        """
        Envía comando al agente y espera respuesta
        
        Parámetros:
        -----------
        comando: str
            Comando de Malmo
        duracion: float
            Tiempo de espera después del comando
        """
        self.agent_host.sendCommand(comando)
        
        # Para ataques, mantener presionado más tiempo
        if "attack" in comando:
            time.sleep(0.6)  # Tiempo para picar
        else:
            time.sleep(duracion)
    
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
    
    def verificar_objetivo_completado(self, obs):
        """
        Verifica si se completó el objetivo de recolección
        
        Parámetros:
        -----------
        obs: dict
            Observaciones actuales
        
        Retorna:
        --------
        tuple: (completado: bool, cantidad_madera: int)
        """
        if obs is None:
            return False, 0
        
        inventario = obs.get("inventory", [])
        madera_total = 0
        
        tipos_madera = ["log", "log2", "wood"]
        for item in inventario:
            if item.get("type", "") in tipos_madera:
                madera_total += item.get("quantity", 0)
        
        return madera_total >= 3, madera_total
    
    def obtener_cantidad_madera(self, obs):
        """
        Obtiene la cantidad actual de madera en inventario
        
        Parámetros:
        -----------
        obs: dict
            Observaciones actuales
        
        Retorna:
        --------
        int: Cantidad de madera
        """
        if obs is None:
            return 0
        
        inventario = obs.get("inventory", [])
        madera_total = 0
        
        tipos_madera = ["log", "log2", "wood"]
        for item in inventario:
            if item.get("type", "") in tipos_madera:
                madera_total += item.get("quantity", 0)
        
        return madera_total
    
    def reset(self):
        """
        Resetea el entorno (para nuevos episodios)
        """
        self.madera_previa = 0
        self.posicion_previa = (0, 0, 0)
        self.historial_acciones = []
        self.pasos_sin_movimiento = 0
        self.pasos_picando = 0
        self.ultimo_bloque_mirando = None
