import time
from search import bfs, aStarSearch, dfs, ucs, greedySearch, iddfs
from search_food import bfs_food, dfs_food, ucs_food, greedy_food, astar_food, iddfs_food

class SearchAgent:
    def __init__(self, layout):
        self.layout = layout
        self.path = []
        self.metrics = {}

    def run(self, search_fn):
        start_time = time.time()
        self.path, stats = search_fn(self.layout)
        end_time = time.time()

        self.metrics = {
            "tiempo": round(end_time - start_time, 4),
            "pasos": len(self.path),
            "nodos_expandidos": stats.get("nodos_expandidos", 0) if isinstance(stats, dict) else 0,
            "profundidad_max": stats.get("profundidad_max", 0) if isinstance(stats, dict) else 0
        }

    def report(self, name):
        print(f"=== {name} ===")
        print(f"Tiempo: {self.metrics['tiempo']} segundos")
        print(f"Pasos en la ruta: {self.metrics['pasos']}")
        print(f"Nodos expandidos: {self.metrics['nodos_expandidos']}")
        print(f"Profundidad máxima: {self.metrics['profundidad_max']}")
        print("-"*40)

# ===========================
# Agentes clásicos
# ===========================
class MyBFSAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        self.run(bfs)

class MyDFSAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        self.run(dfs)

class MyUCSAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        self.run(ucs)

class MyGreedyAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        self.run(greedySearch)

class MyIDDFSAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        self.run(iddfs)

class MyAStarAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        self.run(aStarSearch)

# ===========================
# Agentes Food Problem
# ===========================
class MyFoodBFSAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        path, tiempo, nodos_expandidos, profundidad_max = bfs_food(layout)
        self.path = path
        self.metrics = {
            "tiempo": round(tiempo, 4),
            "pasos": len(path),
            "nodos_expandidos": nodos_expandidos,
            "profundidad_max": profundidad_max
        }

class MyFoodDFSAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        path, tiempo, nodos_expandidos, profundidad_max = dfs_food(layout)
        self.path = path
        self.metrics = {
            "tiempo": round(tiempo, 4),
            "pasos": len(path),
            "nodos_expandidos": nodos_expandidos,
            "profundidad_max": profundidad_max
        }

class MyFoodUCSAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        path, tiempo, nodos_expandidos, profundidad_max = ucs_food(layout)
        self.path = path
        self.metrics = {
            "tiempo": round(tiempo, 4),
            "pasos": len(path),
            "nodos_expandidos": nodos_expandidos,
            "profundidad_max": profundidad_max
        }

class MyFoodGreedyAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        path, tiempo, nodos_expandidos, profundidad_max = greedy_food(layout)
        self.path = path
        self.metrics = {
            "tiempo": round(tiempo, 4),
            "pasos": len(path),
            "nodos_expandidos": nodos_expandidos,
            "profundidad_max": profundidad_max
        }

class MyFoodAStarAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        path, tiempo, nodos_expandidos, profundidad_max = astar_food(layout)
        self.path = path
        self.metrics = {
            "tiempo": round(tiempo, 4),
            "pasos": len(path),
            "nodos_expandidos": nodos_expandidos,
            "profundidad_max": profundidad_max
        }

class MyFoodIDDFSAgent(SearchAgent):
    def __init__(self, layout):
        super().__init__(layout)
        path, tiempo, nodos_expandidos, profundidad_max = iddfs_food(layout)
        self.path = path
        self.metrics = {
            "tiempo": round(tiempo, 4),
            "pasos": len(path),
            "nodos_expandidos": nodos_expandidos,
            "profundidad_max": profundidad_max
        }
