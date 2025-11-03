#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de DEBUG - Ver estructura exacta del inventario en Malmo

Este script imprime TODA la observación JSON para ver cómo Malmo
devuelve los datos del inventario.
"""

import sys
sys.path.insert(0, '/home/carlos/MalmoPlatform/Malmo-0.37.0-Linux-Ubuntu-18.04-64bit_withBoost_Python3.6/Python_Examples')

import MalmoPython as Malmo
import json
import time

from mundo_rl import obtener_mision_xml, cargar_configuracion

def main():
    print("🔍 DEBUG - Estructura de Inventario en Malmo")
    print("=" * 60)
    
    # Configuración
    config = cargar_configuracion()
    agent_host = Malmo.AgentHost()
    
    # Crear misión simple
    mision_xml = obtener_mision_xml(seed=config['seed'], spawn_x=0.5, spawn_z=0.5, mundo_plano=True)
    mission = Malmo.MissionSpec(mision_xml, True)
    mission_record = Malmo.MissionRecordSpec()
    
    # Iniciar
    client_pool = Malmo.ClientPool()
    client_pool.add(Malmo.ClientInfo(config['ip'], config['puerto']))
    
    print("📡 Iniciando misión de debug...")
    agent_host.startMission(mission, client_pool, mission_record, 0, "DebugInventory")
    
    # Esperar inicio
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
    
    print("✓ Misión iniciada")
    time.sleep(2)
    
    # Simplemente observar el estado actual (sin dar items)
    # En una misión real, el agente recoge items al picar
    print("\n📦 Observando inventario actual...")
    time.sleep(1)
    
    # Obtener observación
    world_state = agent_host.getWorldState()
    if world_state.number_of_observations_since_last_state > 0:
        obs_text = world_state.observations[-1].text
        obs = json.loads(obs_text)
        
        print("\n" + "=" * 60)
        print("📋 OBSERVACIÓN COMPLETA (filtrada):")
        print("=" * 60)
        
        # Mostrar solo claves relevantes
        print("\n🔑 Claves principales:")
        for key in sorted(obs.keys()):
            if not key.startswith("InventorySlot"):
                value = obs[key]
                if isinstance(value, (int, float, str, bool)):
                    print(f"  {key}: {value}")
                elif isinstance(value, list) and len(value) < 5:
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: <{type(value).__name__} con {len(value) if hasattr(value, '__len__') else '?'} elementos>")
        
        # Buscar TODOS los slots del inventario
        print("\n🎒 SLOTS DE INVENTARIO (todos):")
        print("-" * 60)
        
        for i in range(45):  # 0-44 (inventario + hotbar completo)
            item_key = f"InventorySlot_{i}_item"
            size_key = f"InventorySlot_{i}_size"
            
            if item_key in obs and obs[item_key] != "air":
                item = obs[item_key]
                size = obs.get(size_key, 0)
                
                # Determinar ubicación
                if i < 9:
                    ubicacion = f"HOTBAR[{i}]"
                else:
                    ubicacion = f"INVENTARIO[{i-9}]"
                
                print(f"  Slot {i:2d} ({ubicacion:15s}): {item:20s} x{size}")
        
        # Buscar específicamente madera/wood
        print("\n🌲 BÚSQUEDA ESPECÍFICA DE MADERA:")
        print("-" * 60)
        
        total_wood = 0
        for i in range(45):
            item_key = f"InventorySlot_{i}_item"
            size_key = f"InventorySlot_{i}_size"
            
            if item_key in obs:
                item = obs[item_key].lower()
                size = obs.get(size_key, 0)
                
                if "log" in item or "wood" in item:
                    if "plank" not in item:  # No contar planks
                        total_wood += size
                        print(f"  ✓ Slot {i}: {obs[item_key]} x{size}")
        
        print(f"\n📊 TOTAL MADERA DETECTADA: {total_wood} bloques")
        
        if total_wood >= 2:
            print("  🎉 ¡OBJETIVO CUMPLIDO! (2+ bloques)")
        else:
            print(f"  ⚠️  Faltan {2 - total_wood} bloques para objetivo")
        
        # Verificar si existe 'inventory' o 'Hotbar'
        print("\n🔍 VERIFICACIÓN DE CLAVES LEGACY:")
        print("-" * 60)
        if "inventory" in obs:
            print(f"  'inventory' existe: {obs['inventory']}")
        else:
            print("  'inventory' NO EXISTE")
        
        if "Hotbar" in obs:
            print(f"  'Hotbar' existe: {obs['Hotbar']}")
        else:
            print("  'Hotbar' NO EXISTE")
    
    print("\n" + "=" * 60)
    print("✅ Debug completado")
    print("=" * 60)

if __name__ == "__main__":
    main()
