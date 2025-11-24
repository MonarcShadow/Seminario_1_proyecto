#!/usr/bin/env python3
"""
Test de compatibilidad de estados entre todos los stages
"""
import sys
import os
import json

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'madera'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'piedra'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'hierro'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'diamante'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'desde_cero'))

# Mock world state for testing
class MockObservation:
    def __init__(self, text):
        self.text = text

class MockWorldState:
    def __init__(self):
        self.number_of_observations_since_last_state = 1
        # Create proper JSON with 25 zeros for 5x5 grid
        surroundings = [0] * 25
        obs_dict = {
            "surroundings5x5": surroundings,
            "InventorySlot_0_item": "stone_pickaxe",
            "InventorySlot_0_size": 1
        }
        self.observations = [MockObservation(json.dumps(obs_dict))]

def test_stage(stage_name, module_name):
    """Test que un stage tenga el formato correcto"""
    try:
        mod = __import__(module_name, fromlist=['get_state'])
        get_state = getattr(mod, 'get_state')
        state = get_state(MockWorldState())
        
        if len(state) == 10:
            print(f"   ✓ {stage_name:15} -> 10 elementos")
            return (True, 10)
        else:
            print(f"   ✗ {stage_name:15} -> {len(state)} elementos (INCORRECTO)")
            return (False, len(state))
    except Exception as e:
        print(f"   ✗ {stage_name:15} -> ERROR: {e}")
        return (False, 0)

def main():
    print("="*60)
    print("Test de Compatibilidad de Estados - Tech Tree Completo")
    print("="*60)
    print("\nTodos los stages deben retornar 10 elementos:")
    print("  (surroundings, wood, stone, iron, diamond,")
    print("   planks, sticks, has_wood_pick, has_stone_pick, has_iron_pick)")
    print("\n" + "="*60)
    
    stages = [
        ("Stage 1 (Wood)", "wood_agent"),
        ("Stage 2 (Stone)", "stone_agent"),
        ("Stage 3 (Iron)", "iron_agent"),
        ("Stage 4 (Diamond)", "diamond_agent"),
        ("Stage 5 (Scratch)", "from_scratch_agent")
    ]
    
    results = []
    for stage_name, module_name in stages:
        success, size = test_stage(stage_name, module_name)
        results.append((stage_name, success, size))
    
    print("\n" + "="*60)
    
    all_success = all(success for _, success, _ in results)
    all_same_size = len(set(size for _, _, size in results)) == 1
    
    if all_success and all_same_size:
        print("✓✓✓ ÉXITO TOTAL")
        print(f"✓ Todos los stages tienen 10 elementos")
        print("✓ Compatible para transfer learning")
        print("✓ Los .pkl se pueden pasar entre stages")
        return 0
    else:
        print("✗✗✗ INCOMPATIBILIDAD DETECTADA")
        for stage_name, success, size in results:
            if not success or size != 10:
                print(f"✗ {stage_name} tiene {size} elementos (debería ser 10)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
