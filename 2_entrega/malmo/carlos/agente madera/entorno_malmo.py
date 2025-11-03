"""
Wrapper del Entorno Malmo para RL - Búsqueda y Recolección de Madera
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
        self.madera_previa = 0
        self.madera_inventario_previa = 0
        self.posicion_previa = (0, 0, 0)
        self.picando_actualmente = False
        self.pasos_picando = 0
        
        # Historial para detectar loops
        self.historial_acciones = []  # Últimas N acciones
        self.pasos_sin_movimiento = 0  # Contador de pasos sin cambio de posición
        
        # Contador de holgazanería (tiempo cerca de madera sin intentar picar)
        self.pasos_cerca_madera_sin_picar = 0
        self.madera_detectada_previamente = False
        
    def calcular_recompensa(self, obs, accion, recompensa_malmo=0.0):
        """
        Sistema de recompensas diseñado para guiar al agente a encontrar y recolectar madera
        
        RECOMPENSAS:
        +200  → Obtener madera en inventario (OBJETIVO PRINCIPAL)
        +50   → Picar bloque de madera exitosamente (recompensa de Malmo)
        +30   → Picar cuando hay madera frente (acción correcta)
        +20   → Detectar madera muy cerca (puede picar)
        +15   → Acercarse a madera visible
        +5    → Descubrir área nueva con árboles
        +3    → Moverse exitosamente
        +2    → Mirar hacia madera
        -0.5  → Costo por acción
        -5    → Colisión/obstáculo
        -10   → Picar sin madera enfrente (desperdicio)
        -15   → Alejarse de madera una vez detectada
        -20   → Loop detectado (giros repetidos sin movimiento)
        -30   → Atascado completamente
        
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
        # 1. VERIFICAR SI OBTUVO MADERA EN INVENTARIO (OBJETIVO PRINCIPAL)
        inventario = obs.get("inventory", [])
        madera_actual = 0
        
        for item in inventario:
            item_type = item.get("type", "").lower()
            # Contar cualquier tipo de madera (log, log2, planks, oak_wood, etc.)
            if ("log" in item_type or "wood" in item_type or "plank" in item_type):
                madera_actual += item.get("quantity", 0)
        
        # ¡ÉXITO! Incrementó madera en inventario
        if madera_actual > self.madera_inventario_previa:
            incremento = madera_actual - self.madera_inventario_previa
            recompensa_obtenida = 200.0 * incremento
            print(f"🎉 ¡MADERA OBTENIDA! +{incremento} en inventario (Recompensa: +{recompensa_obtenida})")
            self.madera_inventario_previa = madera_actual
            return recompensa_obtenida
        
        self.madera_inventario_previa = madera_actual
        
        # 2. USAR RECOMPENSA DE MALMO (picar bloques)
        # Si Malmo da recompensa positiva alta, es porque picó madera exitosamente
        if recompensa_malmo >= 20.0:
            print(f"🪓 Bloque picado exitosamente (Recompensa Malmo: +{recompensa_malmo})")
            return recompensa_malmo
        
        # Recompensa base incluye el costo por acción de Malmo (-0.5)
        recompensa = recompensa_malmo
        
        # 3. SEÑAL DE PROXIMIDAD: Detectar madera y hojas en grid
        grid = obs.get("near5x3x5", [])
        madera_en_grid = 0
        hojas_en_grid = 0
        madera_muy_cerca = False
        
        TIPOS_MADERA_BLOQUES = ["log", "log2"]
        TIPOS_HOJAS = ["leaves", "leaves2"]
        
        for i, bloque in enumerate(grid):
            if any(madera in bloque for madera in TIPOS_MADERA_BLOQUES):
                madera_en_grid += 1
                
                # Calcular distancia al bloque
                x = (i % 5) - 2
                y = ((i // 5) % 3) - 1
                z = (i // 15) - 2
                dist = abs(x) + abs(y) + abs(z)
                
                if dist <= 2:
                    madera_muy_cerca = True
            
            # Detectar hojas como indicador de árbol cerca
            elif any(hoja in bloque for hoja in TIPOS_HOJAS):
                hojas_en_grid += 1
        
        # Recompensar acercarse a madera
        if madera_en_grid > self.madera_previa:
            recompensa += 15.0
            print(f"   🌳 Madera detectada más cerca (+15)")
        elif madera_en_grid < self.madera_previa and self.madera_previa > 0:
            recompensa -= 15.0
            print(f"   ⚠️ Alejándose de madera (-15)")
        elif madera_muy_cerca:
            recompensa += 20.0
            print(f"   🎯 Madera muy cerca, listo para picar (+20)")
        
        # Recompensar detectar hojas (indicador de árbol)
        if hojas_en_grid > 0 and madera_en_grid == 0:
            recompensa += 5.0
            print(f"   🍃 Hojas detectadas, árbol cerca (+5)")
        
        self.madera_previa = madera_en_grid
        
        # 3.5. PENALIZAR HOLGAZANERÍA: Estar cerca de madera/hojas sin intentar picar
        # Si detecta madera o muchas hojas pero no está picando, es holgazanería
        tiene_arbol_cerca = (madera_en_grid > 0 or hojas_en_grid > 3)
        
        if tiene_arbol_cerca:
            self.madera_detectada_previamente = True
            if "attack" not in accion:
                # Está cerca de madera pero NO está picando
                self.pasos_cerca_madera_sin_picar += 1
                
                # Penalización progresiva por holgazanear
                if self.pasos_cerca_madera_sin_picar > 8:
                    penalizacion = -5.0 * (self.pasos_cerca_madera_sin_picar - 8)
                    recompensa += penalizacion
                    print(f"   😴 ¡HOLGAZANEANDO! {self.pasos_cerca_madera_sin_picar} pasos cerca sin picar ({penalizacion:.1f})")
            else:
                # Está picando, resetear contador
                self.pasos_cerca_madera_sin_picar = 0
        else:
            # No hay madera cerca, resetear
            self.pasos_cerca_madera_sin_picar = 0
            self.madera_detectada_previamente = False
        
        # 4. RECOMPENSAR/PENALIZAR ACCIÓN DE PICAR
        if "attack" in accion:
            # Verificar si está mirando madera o hojas
            line_of_sight = obs.get("LineOfSight", {})
            mirando_madera = False
            mirando_hojas = False
            
            if isinstance(line_of_sight, dict):
                tipo_bloque = line_of_sight.get("type", "")
                if any(madera in tipo_bloque for madera in TIPOS_MADERA_BLOQUES):
                    mirando_madera = True
                elif any(hoja in tipo_bloque for hoja in TIPOS_HOJAS):
                    mirando_hojas = True
            
            if mirando_madera:
                # ¡Bien! Está picando madera
                recompensa += 30.0
                self.picando_actualmente = True
                self.pasos_picando += 1
                print(f"   🪓 Picando madera (paso {self.pasos_picando}) (+30)")
            elif mirando_hojas:
                # Bien, está despejando hojas para acceder al tronco
                recompensa += 1.0
                self.picando_actualmente = False
                self.pasos_picando = 0
                print(f"   🍃 Despejando hojas (+1)")
            else:
                # Mal, está picando aire o bloque incorrecto
                recompensa -= 10.0
                self.picando_actualmente = False
                self.pasos_picando = 0
                print(f"   ❌ Picando sin madera enfrente (-10)")
        else:
            self.picando_actualmente = False
            self.pasos_picando = 0
        
        # 4.5. DETECTAR ITEMS DROPPEADOS (madera en el suelo)
        # Incentivar moverse hacia items después de picar
        entities = obs.get("entities", [])
        item_madera_cerca = None
        distancia_item_min = float('inf')
        
        for entity in entities:
            if entity.get("name", "") == "item":
                # Obtener posición del item
                item_x = entity.get("x", 0)
                item_y = entity.get("y", 0)
                item_z = entity.get("z", 0)
                
                # Posición del agente
                agent_x = obs.get("XPos", 0)
                agent_y = obs.get("YPos", 0)
                agent_z = obs.get("ZPos", 0)
                
                # Calcular distancia 2D (X, Z)
                dist = ((item_x - agent_x)**2 + (item_z - agent_z)**2)**0.5
                
                if dist < distancia_item_min:
                    distancia_item_min = dist
                    item_madera_cerca = entity
        
        # Recompensar acercarse a items droppeados
        if item_madera_cerca and distancia_item_min < 5.0:
            if distancia_item_min < 1.5:
                # Muy cerca, debería recogerlo automáticamente
                recompensa += 40.0
                print(f"   📦 Muy cerca de item droppeado (+40)")
            elif distancia_item_min < 3.0:
                # Cerca, acercándose
                recompensa += 25.0
                print(f"   📦 Acercándose a item droppeado (+25)")
            else:
                # Detectado, pero lejos
                recompensa += 10.0
                print(f"   📦 Item droppeado detectado (+10)")
        
        # 5. DETECTAR MOVIMIENTO REAL
        x = obs.get("XPos", 0)
        y = obs.get("YPos", 64)
        z = obs.get("ZPos", 0)
        posicion_actual = (round(x, 1), round(y, 1), round(z, 1))
        
        # Calcular distancia SOLO en 2D (X, Z) como en agente agua
        # Ignorar Y porque saltar/caer no debería contar como "moverse"
        distancia = ((posicion_actual[0] - self.posicion_previa[0])**2 + 
                    (posicion_actual[2] - self.posicion_previa[2])**2)**0.5
        
        if distancia > 0.3:  # Se movió al menos 0.3 bloques (mismo que agente agua)
            # ✅ MOVIMIENTO EXITOSO
            recompensa += 3.0
            self.pasos_sin_movimiento = 0
        else:
            # ❌ NO SE MOVIÓ
            self.pasos_sin_movimiento += 1
            
            # Agregar acción al historial
            self.historial_acciones.append(accion)
            if len(self.historial_acciones) > 10:
                self.historial_acciones.pop(0)
            
            # DETECTAR LOOP: Si lleva muchos giros consecutivos (igual que agua)
            if self.pasos_sin_movimiento > 3:
                # Revisar si está alternando entre giros
                ultimas_3 = self.historial_acciones[-3:]
                if all("turn" in a for a in ultimas_3):
                    recompensa -= 20.0  # CASTIGO FUERTE por loop de giros
            
            # ATASCADO COMPLETAMENTE (mismo threshold que agua)
            if self.pasos_sin_movimiento > 8:
                recompensa -= 30.0  # CASTIGO MUY FUERTE
                
            # Penalización progresiva por quedarse quieto (igual que agua)
            recompensa -= (2.0 * self.pasos_sin_movimiento)
        
        self.posicion_previa = posicion_actual
        
        # 6. RECOMPENSAR MIRAR HACIA MADERA
        line_of_sight = obs.get("LineOfSight", {})
        if isinstance(line_of_sight, dict):
            tipo_bloque = line_of_sight.get("type", "")
            if any(madera in tipo_bloque for madera in TIPOS_MADERA_BLOQUES):
                recompensa += 2.0
        
        # 7. INCENTIVAR INTENTOS DE MOVIMIENTO después de giros
        if len(self.historial_acciones) >= 2:
            ultima = self.historial_acciones[-1] if len(self.historial_acciones) > 0 else ""
            penultima = self.historial_acciones[-2] if len(self.historial_acciones) > 1 else ""
            
            if "turn" in penultima and ("move" in accion or "jumpmove" in accion):
                recompensa += 5.0
        
        # 8. PENALIZACIÓN POR OBSTÁCULOS
        if ("move" in accion or "jumpmove" in accion) and distancia < 0.1:
            recompensa -= 5.0
        
        # 9. RECOMPENSA POR VARIEDAD DE BLOQUES (exploración)
        tipos_unicos = len(set(grid))
        if tipos_unicos > 5:
            recompensa += 2.0
        
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
    
    def ejecutar_accion(self, comando, duracion=0.1):
        """
        Envía comando al agente y espera respuesta
        
        Parámetros:
        -----------
        comando: str
            Comando de Malmo (ej: "move 1", "turn 1", "attack 1")
        duracion: float
            Tiempo de espera después del comando
        """
        self.agent_host.sendCommand(comando)
        time.sleep(duracion)
        
        # Para picar, necesita mantener el comando más tiempo
        if "attack" in comando:
            # En Minecraft 1.11.2, necesita múltiples ataques para romper bloque
            for _ in range(3):  # Picar 3 veces adicionales
                time.sleep(0.2)
                self.agent_host.sendCommand(comando)
                time.sleep(0.2)
        elif "move" in comando:
            # Tiempo adicional para comandos de movimiento (igual que agente agua)
            time.sleep(0.1)
    
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
    
    def verificar_madera_obtenida(self, obs):
        """
        Verifica si el agente obtuvo suficiente madera en su inventario
        
        Objetivo: 2+ bloques de madera (log/log2) O 8+ tablas (planks)
        
        Parámetros:
        -----------
        obs: dict
            Observaciones actuales
        
        Retorna:
        --------
        bool: True si alcanzó el objetivo (2+ logs o 8+ planks)
        """
        if obs is None:
            return False
        
        inventario = obs.get("inventory", [])
        
        total_logs = 0
        total_planks = 0
        
        # Debug: mostrar todos los items del inventario
        if len(inventario) > 0:
            print(f"🎒 Inventario actual:")
            for item in inventario:
                item_type = item.get("type", "")
                cantidad = item.get("quantity", 0)
                print(f"   - {item_type}: {cantidad}")
        
        for item in inventario:
            item_type = item.get("type", "").lower()  # Convertir a minúsculas para comparar
            cantidad = item.get("quantity", 0)
            
            # Buscar cualquier tipo de tronco (log, log2, oak_wood, etc.)
            if "log" in item_type or "wood" in item_type:
                # Pero no contar planks/tablas como logs
                if "plank" not in item_type:
                    total_logs += cantidad
            elif "plank" in item_type:
                total_planks += cantidad
        
        # Verificar si alcanzó el objetivo
        if total_logs >= 2:
            print(f"🎉 ¡OBJETIVO ALCANZADO! {total_logs} bloques de madera")
            return True
        elif total_planks >= 8:
            print(f"🎉 ¡OBJETIVO ALCANZADO! {total_planks} tablas (planks)")
            return True
        
        # Mostrar progreso si tiene algo
        if total_logs > 0 or total_planks > 0:
            print(f"📊 Progreso: {total_logs}/2 logs, {total_planks}/8 planks")
        
        return False
    
    def reset(self):
        """
        Resetea el entorno (para nuevos episodios)
        """
        self.estado_previo = None
        self.madera_previa = 0
        self.madera_inventario_previa = 0
        self.posicion_previa = (0, 0, 0)
        self.historial_acciones = []
        self.pasos_sin_movimiento = 0
        self.picando_actualmente = False
        self.pasos_picando = 0
        # Resetear contadores de holgazanería
        self.pasos_cerca_madera_sin_picar = 0
        self.madera_detectada_previamente = False
