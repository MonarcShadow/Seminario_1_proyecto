"""
Entorno Malmo Multi-Objetivo con Progresión de Fases
Madera → Piedra → Hierro → Diamante

Autor: Sistema de IA
Fecha: Noviembre 2025
"""

import json
import time


class EntornoMalmoProgresivo:
    """
    Entorno que maneja la progresión a través de múltiples objetivos
    con sistema de recompensas adaptativo por fase
    """
    
    # Constantes de fase
    FASES = {
        0: 'MADERA',
        1: 'PIEDRA',
        2: 'HIERRO',
        3: 'DIAMANTE'
    }
    
    def __init__(self, agent_host):
        """
        Parámetros:
        -----------
        agent_host: MalmoPython.AgentHost
        """
        self.agent_host = agent_host
        self.world_state = None
        self.fase_actual = 0  # 0: MADERA, 1: PIEDRA, 2: HIERRO, 3: DIAMANTE
        
        # Progreso de materiales recolectados
        self.materiales_recolectados = {
            'madera': 0,
            'piedra': 0,
            'hierro': 0,
            'diamante': 0,
        }
        
        # Flags de crafteo simulado
        self.pico_piedra_dado = False
        self.pico_hierro_dado = False
        
        # Tracking de estado previo
        self.estado_previo = None
        self.posicion_previa = (0, 0, 0)
        self.pasos_sin_movimiento = 0
        
        # Anti-holgazanería por fase
        self.pasos_cerca_objetivo_sin_picar = 0
        self.objetivo_detectado_previamente = False
        
        # Tracking de herramienta incorrecta
        self.ataques_herramienta_incorrecta = 0
        
    def calcular_recompensa(self, obs, accion, fase_actual):
        """
        Sistema de recompensas adaptativo según la fase actual
        
        RECOMPENSAS POR FASE:
        
        FASE 0 - MADERA (sin herramienta):
        +200  → Obtener madera en inventario
        +30   → Picar madera exitosamente
        +20   → Madera muy cerca
        +10   → Madera cerca
        +5    → Movimiento hacia madera
        -5×N  → Holgazanear cerca de madera sin picar (N = pasos - 8)
        -30   → Atacar sin madera frente
        
        FASE 1 - PIEDRA (con pico de madera):
        +250  → Obtener piedra en inventario
        +40   → Picar piedra exitosamente
        +25   → Piedra muy cerca
        +12   → Piedra cerca
        +6    → Movimiento hacia piedra
        -40   → Atacar piedra sin pico de madera (herramienta incorrecta)
        -35   → Atacar sin piedra frente
        -10   → Seguir buscando madera (fase incorrecta)
        
        FASE 2 - HIERRO (con pico de piedra):
        +300  → Obtener hierro en inventario
        +50   → Picar hierro exitosamente
        +30   → Hierro muy cerca
        +15   → Hierro cerca
        +8    → Movimiento hacia hierro
        -50   → Atacar hierro sin pico de piedra
        -40   → Atacar sin hierro frente
        -15   → Buscar material de fase anterior
        
        FASE 3 - DIAMANTE (con pico de hierro):
        +500  → Obtener diamante (¡OBJETIVO FINAL!)
        +100  → Picar diamante exitosamente
        +50   → Diamante muy cerca
        +25   → Diamante cerca
        +10   → Movimiento hacia diamante
        -100  → Atacar diamante sin pico de hierro
        -50   → Atacar sin diamante frente
        -20   → Buscar material de fase anterior
        
        GENERALES (todas las fases):
        +8    → Cambiar pitch cerca de objetivo
        +15   → Encontrar objetivo al cambiar pitch
        -1    → Movimiento sin cambio de posición
        -5    → Repetir misma acción muchas veces
        """
        
        recompensa = 0.0
        
        # Multiplicador según fase (fases más avanzadas son más importantes)
        multiplicador_fase = {
            0: 1.0,   # MADERA
            1: 1.2,   # PIEDRA
            2: 1.5,   # HIERRO
            3: 2.0,   # DIAMANTE
        }
        mult = multiplicador_fase.get(fase_actual, 1.0)
        
        # 1. RECOMPENSA POR OBTENER MATERIAL EN INVENTARIO
        recompensa_inventario = self._recompensa_por_inventario(obs, fase_actual)
        recompensa += recompensa_inventario * mult
        
        # 2. RECOMPENSA/CASTIGO POR ATACAR
        if accion == 4:  # attack
            recompensa_ataque = self._recompensa_por_ataque(obs, fase_actual)
            recompensa += recompensa_ataque * mult
        
        # 3. RECOMPENSA POR PROXIMIDAD AL OBJETIVO
        recompensa_proximidad = self._recompensa_por_proximidad(obs, fase_actual)
        recompensa += recompensa_proximidad * mult
        
        # 4. RECOMPENSA POR MOVIMIENTO EFECTIVO
        recompensa_movimiento = self._recompensa_por_movimiento(obs, accion)
        recompensa += recompensa_movimiento
        
        # 5. CASTIGO POR HOLGAZANERÍA
        castigo_holgazan = self._castigo_holgazaneria(obs, accion, fase_actual)
        recompensa += castigo_holgazan * mult
        
        # 6. RECOMPENSA POR USAR PITCH (buscar en altura) - SOLO SI ES ÚTIL
        if accion in [7, 8]:  # pitch up/down (ahora son acciones 7 y 8)
            recompensa_pitch = self._recompensa_por_pitch(obs, fase_actual)
            recompensa += recompensa_pitch * mult
        
        # 7. CASTIGO POR BUSCAR MATERIAL DE FASE INCORRECTA
        castigo_fase_incorrecta = self._castigo_fase_incorrecta(obs, accion, fase_actual)
        recompensa += castigo_fase_incorrecta * mult
        
        return recompensa
    
    def _recompensa_por_inventario(self, obs, fase):
        """Detecta si se obtuvo material objetivo en inventario"""
        recompensa = 0.0
        
        # Contar material actual en inventario
        if fase == 0:  # MADERA
            nuevo_count = self._contar_madera(obs)
            if nuevo_count > self.materiales_recolectados['madera']:
                diff = nuevo_count - self.materiales_recolectados['madera']
                recompensa = 200.0 * diff
                print(f"🌲 +{diff} MADERA obtenida! (Total: {nuevo_count}/3) [+{recompensa}]")
                self.materiales_recolectados['madera'] = nuevo_count
        
        elif fase == 1:  # PIEDRA
            nuevo_count = self._contar_piedra(obs)
            if nuevo_count > self.materiales_recolectados['piedra']:
                diff = nuevo_count - self.materiales_recolectados['piedra']
                recompensa = 250.0 * diff
                print(f"🪨 +{diff} PIEDRA obtenida! (Total: {nuevo_count}/3) [+{recompensa}]")
                self.materiales_recolectados['piedra'] = nuevo_count
        
        elif fase == 2:  # HIERRO
            nuevo_count = self._contar_hierro(obs)
            if nuevo_count > self.materiales_recolectados['hierro']:
                diff = nuevo_count - self.materiales_recolectados['hierro']
                recompensa = 300.0 * diff
                print(f"⚙️ +{diff} HIERRO obtenido! (Total: {nuevo_count}/3) [+{recompensa}]")
                self.materiales_recolectados['hierro'] = nuevo_count
        
        elif fase == 3:  # DIAMANTE
            nuevo_count = self._contar_diamante(obs)
            if nuevo_count > self.materiales_recolectados['diamante']:
                diff = nuevo_count - self.materiales_recolectados['diamante']
                recompensa = 500.0 * diff
                print(f"💎 ¡¡¡DIAMANTE OBTENIDO!!! [+{recompensa}]")
                self.materiales_recolectados['diamante'] = nuevo_count
        
        return recompensa
    
    def _recompensa_por_ataque(self, obs, fase):
        """Calcula recompensa/castigo por atacar según contexto"""
        recompensa = 0.0
        
        # Verificar si hay objetivo frente
        tiene_objetivo_frente = self._verificar_objetivo_frente(obs, fase)
        tiene_herramienta_correcta = self._verificar_herramienta_correcta(obs, fase)
        
        if tiene_objetivo_frente:
            if tiene_herramienta_correcta or fase == 0:  # Fase 0 no requiere herramienta
                # Ataque correcto
                recompensas_ataque = {
                    0: 30.0,   # Picar madera
                    1: 40.0,   # Picar piedra
                    2: 50.0,   # Picar hierro
                    3: 100.0,  # Picar diamante
                }
                recompensa = recompensas_ataque.get(fase, 30.0)
            else:
                # Atacar con herramienta incorrecta (no obtendrá el drop)
                castigos_herramienta = {
                    1: -40.0,  # Piedra sin pico de madera
                    2: -50.0,  # Hierro sin pico de piedra
                    3: -100.0, # Diamante sin pico de hierro
                }
                recompensa = castigos_herramienta.get(fase, -30.0)
                self.ataques_herramienta_incorrecta += 1
                
                if self.ataques_herramienta_incorrecta % 5 == 0:
                    print(f"⚠️ Atacando con herramienta incorrecta! (fase {fase})")
        else:
            # Atacar sin objetivo frente
            castigos_ataque_vacio = {
                0: -30.0,
                1: -35.0,
                2: -40.0,
                3: -50.0,
            }
            recompensa = castigos_ataque_vacio.get(fase, -30.0)
        
        return recompensa
    
    def _recompensa_por_proximidad(self, obs, fase):
        """Recompensa por estar cerca del objetivo"""
        recompensa = 0.0
        
        # Analizar grid para detectar objetivo
        materiales_objetivo = self._obtener_materiales_objetivo(fase)
        grid = obs.get('floor3x3', [])
        
        if len(grid) < 125:
            return 0.0
        
        # Buscar objetivo en el grid
        objetivo_muy_cerca = False  # Distancia <= 2
        objetivo_cerca = False      # Distancia <= 4
        
        for y_offset in range(5):
            for x in range(5):
                for z in range(5):
                    idx = y_offset * 25 + z * 5 + x
                    if idx >= len(grid):
                        continue
                    
                    bloque = grid[idx]
                    if bloque in materiales_objetivo:
                        dist = abs(x - 2) + abs(y_offset - 2) + abs(z - 2)
                        
                        if dist <= 2:
                            objetivo_muy_cerca = True
                        elif dist <= 4:
                            objetivo_cerca = True
        
        # Asignar recompensas según distancia
        if objetivo_muy_cerca:
            recompensas_muy_cerca = {
                0: 20.0,  # Madera muy cerca
                1: 25.0,  # Piedra muy cerca
                2: 30.0,  # Hierro muy cerca
                3: 50.0,  # Diamante muy cerca
            }
            recompensa = recompensas_muy_cerca.get(fase, 20.0)
        elif objetivo_cerca:
            recompensas_cerca = {
                0: 10.0,
                1: 12.0,
                2: 15.0,
                3: 25.0,
            }
            recompensa = recompensas_cerca.get(fase, 10.0)
        
        return recompensa
    
    def _recompensa_por_movimiento(self, obs, accion):
        """Recompensa por moverse efectivamente (SOLO SI NO ESTÁ CERCA DEL OBJETIVO)"""
        recompensa = 0.0
        
        # Solo evaluar en acciones de movimiento
        if accion not in [0, 3]:  # move, jumpmove
            return 0.0
        
        xpos = obs.get('XPos', 0)
        zpos = obs.get('ZPos', 0)
        ypos = obs.get('YPos', 0)
        
        pos_actual = (xpos, ypos, zpos)
        
        if self.posicion_previa != (0, 0, 0):
            # Calcular distancia 2D (X, Z)
            dist = ((xpos - self.posicion_previa[0])**2 + 
                    (zpos - self.posicion_previa[2])**2)**0.5
            
            if dist < 0.3:  # No se movió significativamente
                self.pasos_sin_movimiento += 1
                if self.pasos_sin_movimiento > 5:
                    recompensa = -2.0  # Castigo aumentado por quedarse atascado
            else:
                self.pasos_sin_movimiento = 0
                # NO dar recompensa por movimiento genérico
                # Solo la proximidad al objetivo da recompensa
                recompensa = 0.0
        
        self.posicion_previa = pos_actual
        return recompensa
    
    def _castigo_holgazaneria(self, obs, accion, fase):
        """Castigo por estar cerca del objetivo sin atacar"""
        castigo = 0.0
        
        # Detectar si hay objetivo cerca
        materiales_objetivo = self._obtener_materiales_objetivo(fase)
        grid = obs.get('floor3x3', [])
        
        objetivo_cerca = False
        if len(grid) >= 125:
            for y_offset in range(5):
                for x in range(5):
                    for z in range(5):
                        idx = y_offset * 25 + z * 5 + x
                        if idx >= len(grid):
                            continue
                        
                        bloque = grid[idx]
                        if bloque in materiales_objetivo:
                            dist = abs(x - 2) + abs(y_offset - 2) + abs(z - 2)
                            if dist <= 3:
                                objetivo_cerca = True
                                break
        
        # Contar pasos cerca sin atacar
        if objetivo_cerca:
            if accion != 4:  # No está atacando
                self.pasos_cerca_objetivo_sin_picar += 1
            else:
                self.pasos_cerca_objetivo_sin_picar = 0
            
            self.objetivo_detectado_previamente = True
        else:
            self.pasos_cerca_objetivo_sin_picar = 0
            self.objetivo_detectado_previamente = False
        
        # Aplicar castigo progresivo después de 8 pasos
        if self.pasos_cerca_objetivo_sin_picar > 8:
            pasos_extra = self.pasos_cerca_objetivo_sin_picar - 8
            castigo = -5.0 * pasos_extra
        
        return castigo
    
    def _recompensa_por_pitch(self, obs, fase):
        """Recompensa por usar pitch SOLO cuando hay objetivo en altura cerca"""
        recompensa = 0.0
        
        # Verificar si hay objetivo cerca VERTICALMENTE
        materiales_objetivo = self._obtener_materiales_objetivo(fase)
        grid = obs.get('floor3x3', [])
        
        objetivo_encontrado_vertical = False
        
        if len(grid) >= 125:
            # Verificar SOLO capas verticales (no la capa central horizontal)
            for y_offset in [0, 1, 3, 4]:  # Capas arriba y abajo del centro (excluye 2)
                for x in range(5):
                    for z in range(5):
                        idx = y_offset * 25 + z * 5 + x
                        if idx >= len(grid):
                            continue
                        
                        bloque = grid[idx]
                        if bloque in materiales_objetivo:
                            # Solo recompensar si está MUY cerca horizontalmente
                            dist_horizontal = abs(x - 2) + abs(z - 2)
                            if dist_horizontal <= 1:  # Más estricto: solo 1 bloque
                                objetivo_encontrado_vertical = True
                                break
        
        # SOLO recompensa si realmente hay un objetivo vertical cerca
        if objetivo_encontrado_vertical:
            recompensa = 10.0  # Recompensa moderada solo cuando es útil
        else:
            recompensa = 0.0  # NO recompensar pitch sin razón
        
        return recompensa
    
    def _castigo_fase_incorrecta(self, obs, accion, fase):
        """Castigo por buscar material de fase anterior"""
        castigo = 0.0
        
        if fase == 0:
            return 0.0  # Primera fase, no hay fase anterior
        
        # Si está atacando, verificar qué está atacando
        if accion == 4:
            # Verificar si está atacando material de fase anterior
            materiales_anteriores = []
            if fase >= 1:
                materiales_anteriores.extend(['log', 'log2', 'oak_wood', 'spruce_wood'])
            if fase >= 2:
                materiales_anteriores.extend(['stone', 'cobblestone'])
            if fase >= 3:
                materiales_anteriores.extend(['iron_ore'])
            
            # Verificar qué hay frente
            grid = obs.get('floor3x3', [])
            if len(grid) >= 66:
                bloque_frente = grid[65]
                if bloque_frente in materiales_anteriores:
                    castigos = {
                        1: -10.0,  # Buscar madera en fase piedra
                        2: -15.0,  # Buscar madera/piedra en fase hierro
                        3: -20.0,  # Buscar cualquier cosa anterior en fase diamante
                    }
                    castigo = castigos.get(fase, -10.0)
                    
                    if castigo < 0:
                        print(f"⚠️ Atacando material de fase anterior en fase {fase}")
        
        return castigo
    
    def _obtener_materiales_objetivo(self, fase):
        """Retorna lista de materiales objetivo según fase"""
        if fase == 0:
            return ['log', 'log2', 'oak_wood', 'spruce_wood', 'birch_wood', 
                    'jungle_wood', 'acacia_wood', 'dark_oak_wood']
        elif fase == 1:
            return ['stone', 'cobblestone']
        elif fase == 2:
            return ['iron_ore']
        elif fase == 3:
            return ['diamond_ore']
        return []
    
    def _verificar_objetivo_frente(self, obs, fase):
        """Verifica si hay objetivo frente al agente"""
        materiales_objetivo = self._obtener_materiales_objetivo(fase)
        grid = obs.get('floor3x3', [])
        
        if len(grid) < 66:
            return False
        
        # Índice 65 = bloque justo frente en capa central
        bloque_frente = grid[65]
        return bloque_frente in materiales_objetivo
    
    def _verificar_herramienta_correcta(self, obs, fase):
        """Verifica si tiene herramienta correcta equipada"""
        herramientas_req = {
            0: None,  # Madera: mano
            1: 'wooden_pickaxe',
            2: 'stone_pickaxe',
            3: 'iron_pickaxe',
        }
        
        herramienta = herramientas_req.get(fase)
        if herramienta is None:
            return True
        
        # Buscar en hotbar (slots 0-8)
        for slot in range(9):
            item_key = f'InventorySlot_{slot}_item'
            if item_key in obs:
                if obs[item_key] == herramienta:
                    return True
        
        return False
    
    def _contar_madera(self, obs):
        """Cuenta bloques de madera en inventario"""
        count = 0
        materiales = ['log', 'log2', 'oak_wood', 'spruce_wood', 'birch_wood',
                      'jungle_wood', 'acacia_wood', 'dark_oak_wood']
        
        for slot in range(45):
            item_key = f'InventorySlot_{slot}_item'
            size_key = f'InventorySlot_{slot}_size'
            
            if item_key in obs:
                item = obs[item_key]
                size = obs.get(size_key, 1)
                if item in materiales:
                    count += size
        
        return count
    
    def _contar_piedra(self, obs):
        """Cuenta bloques de piedra en inventario"""
        count = 0
        materiales = ['stone', 'cobblestone']
        
        for slot in range(45):
            item_key = f'InventorySlot_{slot}_item'
            size_key = f'InventorySlot_{slot}_size'
            
            if item_key in obs:
                item = obs[item_key]
                size = obs.get(size_key, 1)
                if item in materiales:
                    count += size
        
        return count
    
    def _contar_hierro(self, obs):
        """Cuenta lingotes de hierro en inventario (mineral convertido)"""
        count = 0
        
        for slot in range(45):
            item_key = f'InventorySlot_{slot}_item'
            size_key = f'InventorySlot_{slot}_size'
            
            if item_key in obs:
                item = obs[item_key]
                size = obs.get(size_key, 1)
                # Mineral de hierro se convierte automáticamente a lingote
                if item == 'iron_ingot':
                    count += size
        
        return count
    
    def _contar_diamante(self, obs):
        """Cuenta diamantes en inventario"""
        count = 0
        
        for slot in range(45):
            item_key = f'InventorySlot_{slot}_item'
            size_key = f'InventorySlot_{slot}_size'
            
            if item_key in obs:
                item = obs[item_key]
                size = obs.get(size_key, 1)
                if item == 'diamond':
                    count += size
        
        return count
    
    def verificar_progresion_fase(self, obs):
        """
        Verifica si se debe avanzar a la siguiente fase
        Maneja el "crafteo" simulado de herramientas
        
        Returns:
        --------
        bool: True si cambió de fase
        """
        cambio = False
        
        if self.fase_actual == 0:  # MADERA → PIEDRA
            if self.materiales_recolectados['madera'] >= 3:
                print("\n" + "="*60)
                print("🌲 FASE MADERA COMPLETADA!")
                print(f"   Madera recolectada: {self.materiales_recolectados['madera']}/3")
                print("   → Avanzando a fase PIEDRA")
                print("="*60 + "\n")
                self.fase_actual = 1
                self.pasos_cerca_objetivo_sin_picar = 0
                cambio = True
        
        elif self.fase_actual == 1:  # PIEDRA → HIERRO
            if self.materiales_recolectados['piedra'] >= 3:
                if not self.pico_piedra_dado:
                    print("\n" + "="*60)
                    print("🪨 FASE PIEDRA COMPLETADA!")
                    print(f"   Piedra recolectada: {self.materiales_recolectados['piedra']}/3")
                    print("   ⚒️  CRAFTEANDO pico de piedra...")
                    print("   (Simulando: -3 piedra, +1 pico de piedra)")
                    print("="*60 + "\n")
                    
                    # Simular crafteo: quitar piedra, dar pico
                    time.sleep(0.5)
                    self.agent_host.sendCommand("chat /clear")
                    time.sleep(0.3)
                    self.agent_host.sendCommand("chat /give @p stone_pickaxe 1")
                    time.sleep(0.3)
                    
                    self.pico_piedra_dado = True
                    self.fase_actual = 2
                    self.pasos_cerca_objetivo_sin_picar = 0
                    cambio = True
                    
                    print("✓ Fase HIERRO iniciada")
        
        elif self.fase_actual == 2:  # HIERRO → DIAMANTE
            if self.materiales_recolectados['hierro'] >= 3:
                if not self.pico_hierro_dado:
                    print("\n" + "="*60)
                    print("⚙️ FASE HIERRO COMPLETADA!")
                    print(f"   Hierro recolectado: {self.materiales_recolectados['hierro']}/3")
                    print("   ⚒️  CRAFTEANDO pico de hierro...")
                    print("   (Simulando: -3 hierro, +1 pico de hierro)")
                    print("="*60 + "\n")
                    
                    # Simular crafteo: quitar hierro, dar pico
                    time.sleep(0.5)
                    self.agent_host.sendCommand("chat /clear")
                    time.sleep(0.3)
                    self.agent_host.sendCommand("chat /give @p iron_pickaxe 1")
                    time.sleep(0.3)
                    
                    self.pico_hierro_dado = True
                    self.fase_actual = 3
                    self.pasos_cerca_objetivo_sin_picar = 0
                    cambio = True
                    
                    print("✓ Fase DIAMANTE iniciada (¡OBJETIVO FINAL!)")
        
        elif self.fase_actual == 3:  # DIAMANTE (objetivo final)
            if self.materiales_recolectados['diamante'] >= 1:
                print("\n" + "="*70)
                print("💎💎💎 ¡¡¡OBJETIVO FINAL COMPLETADO!!! 💎💎💎")
                print(f"   DIAMANTE OBTENIDO!")
                print("   🏆 EL AGENTE HA COMPLETADO TODA LA PROGRESIÓN 🏆")
                print("="*70 + "\n")
                return True  # Episodio terminado exitosamente
        
        return cambio
    
    def reset_episodio(self):
        """Resetea el estado del entorno para nuevo episodio"""
        self.fase_actual = 0
        self.materiales_recolectados = {
            'madera': 0,
            'piedra': 0,
            'hierro': 0,
            'diamante': 0,
        }
        self.pico_piedra_dado = False
        self.pico_hierro_dado = False
        self.posicion_previa = (0, 0, 0)
        self.pasos_sin_movimiento = 0
        self.pasos_cerca_objetivo_sin_picar = 0
        self.objetivo_detectado_previamente = False
        self.ataques_herramienta_incorrecta = 0
    
    def obtener_fase_actual(self):
        """Retorna la fase actual y nombre"""
        nombres = {
            0: "MADERA",
            1: "PIEDRA",
            2: "HIERRO",
            3: "DIAMANTE"
        }
        return self.fase_actual, nombres.get(self.fase_actual, "DESCONOCIDO")
    
    def obtener_progreso(self):
        """Retorna diccionario con progreso de cada fase"""
        return {
            'fase_actual': self.fase_actual,
            'madera': f"{self.materiales_recolectados['madera']}/3",
            'piedra': f"{self.materiales_recolectados['piedra']}/3",
            'hierro': f"{self.materiales_recolectados['hierro']}/3",
            'diamante': f"{self.materiales_recolectados['diamante']}/1",
            'pico_piedra': self.pico_piedra_dado,
            'pico_hierro': self.pico_hierro_dado,
        }
