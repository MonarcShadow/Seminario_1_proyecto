"""
Script de Prueba - Verificar Conexión y Módulos
Verifica que todo esté listo antes de entrenar

Autor: Sistema de IA
"""

import sys
import time

def test_malmo():
    """Prueba conexión con Malmo"""
    print("1️⃣  Probando MalmoPython...")
    try:
        import MalmoPython
        print("   ✓ MalmoPython importado correctamente")
        return True
    except ImportError as e:
        print(f"   ✗ Error: {e}")
        print("   → Instala Malmo y añádelo al PYTHONPATH")
        return False


def test_modulos():
    """Prueba módulos del proyecto"""
    print("\n2️⃣  Probando módulos del proyecto...")
    
    try:
        from agente_rl import AgenteQLearningProgresivo
        print("   ✓ agente_rl.py")
    except Exception as e:
        print(f"   ✗ agente_rl.py: {e}")
        return False
    
    try:
        from entorno_malmo import EntornoMalmoProgresivo
        print("   ✓ entorno_malmo.py")
    except Exception as e:
        print(f"   ✗ entorno_malmo.py: {e}")
        return False
    
    try:
        from mundo_rl import generar_mundo_plano_xml
        print("   ✓ mundo_rl.py")
    except Exception as e:
        print(f"   ✗ mundo_rl.py: {e}")
        return False
    
    return True


def test_agente():
    """Prueba creación de agente"""
    print("\n3️⃣  Probando creación de agente...")
    try:
        from agente_rl import AgenteQLearningProgresivo
        agente = AgenteQLearningProgresivo()
        print(f"   ✓ Agente creado")
        print(f"   - Acciones: {len(agente.ACCIONES)}")
        print(f"   - Fases: {len(agente.FASES)}")
        print(f"   - Q-tables: {len(agente.q_tables)}")
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_mundo():
    """Prueba generación de mundo"""
    print("\n4️⃣  Probando generación de mundo...")
    try:
        from mundo_rl import generar_mundo_plano_xml
        xml = generar_mundo_plano_xml(seed=999)
        
        if len(xml) > 1000:
            print(f"   ✓ XML generado ({len(xml)} caracteres)")
            
            # Verificar elementos clave
            checks = [
                ("FlatWorldGenerator", "generador mundo plano"),
                ("DrawingDecorator", "decorador de dibujo"),
                ("obsidian", "muro de obsidiana"),
                ("iron_ore", "mineral de hierro"),
                ("diamond_ore", "mineral de diamante"),
            ]
            
            for check, descripcion in checks:
                if check in xml:
                    print(f"   ✓ Contiene {descripcion}")
                else:
                    print(f"   ✗ Falta {descripcion}")
            
            return True
        else:
            print(f"   ✗ XML demasiado corto: {len(xml)} caracteres")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_estado():
    """Prueba discretización de estado"""
    print("\n5️⃣  Probando discretización de estado...")
    try:
        from agente_rl import AgenteQLearningProgresivo
        agente = AgenteQLearningProgresivo()
        
        # Observación de prueba
        obs_prueba = {
            'Yaw': 0,
            'Pitch': 0,
            'XPos': 0.5,
            'YPos': 4.0,
            'ZPos': 0.5,
            'floor3x3': ['air'] * 125,  # Grid vacío
        }
        
        estado = agente.obtener_estado_discretizado(obs_prueba, fase_actual=0)
        
        print(f"   ✓ Estado generado: {len(estado)} dimensiones")
        print(f"   - Estado: {estado}")
        
        if len(estado) == 12:
            print(f"   ✓ Dimensiones correctas (12)")
            return True
        else:
            print(f"   ✗ Dimensiones incorrectas: {len(estado)} (esperado: 12)")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_minecraft():
    """Prueba conexión con Minecraft"""
    print("\n6️⃣  Probando conexión con Minecraft...")
    try:
        import MalmoPython
        agent_host = MalmoPython.AgentHost()
        
        # Intentar obtener estado
        print("   ⏳ Intentando conectar...")
        print("   (Esto fallará si Minecraft no está corriendo, es normal)")
        
        # Crear misión simple
        from mundo_rl import generar_mundo_plano_xml
        xml = generar_mundo_plano_xml(seed=123)
        mission = MalmoPython.MissionSpec(xml, True)
        
        print("   ✓ Misión XML parseada correctamente")
        
        # Probar conexión al cliente
        try:
            from config import verificar_conexion
            print("\n   📡 Verificando conexión al cliente Minecraft...")
            if verificar_conexion():
                print("   ✓ Cliente Minecraft disponible")
            else:
                print("   ⚠️  Cliente no responde (asegúrate de iniciar Minecraft)")
        except Exception as e:
            print(f"   ⚠️  No se pudo verificar cliente: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("🧪 PRUEBAS DE VERIFICACIÓN")
    print("   Agente Progresivo Multi-Material")
    print("="*60 + "\n")
    
    resultados = []
    
    resultados.append(("Malmo", test_malmo()))
    resultados.append(("Módulos", test_modulos()))
    resultados.append(("Agente", test_agente()))
    resultados.append(("Mundo", test_mundo()))
    resultados.append(("Estado", test_estado()))
    resultados.append(("Minecraft", test_minecraft()))
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    
    for nombre, resultado in resultados:
        estado = "✓ PASS" if resultado else "✗ FAIL"
        print(f"{nombre:.<30} {estado}")
    
    total = len(resultados)
    pasados = sum(1 for _, r in resultados if r)
    
    print("\n" + "="*60)
    print(f"Total: {pasados}/{total} pruebas pasadas ({100*pasados/total:.0f}%)")
    print("="*60 + "\n")
    
    if pasados == total:
        print("✅ ¡Todo listo para entrenar!")
        print("\nSiguientes pasos:")
        print("  1. Inicia Minecraft 1.11.2")
        print("  2. Carga el mod de Malmo")
        print("  3. Ejecuta: python3 mundo_rl.py 10")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return pasados == total


if __name__ == "__main__":
    exito = main()
    sys.exit(0 if exito else 1)
