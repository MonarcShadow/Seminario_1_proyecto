from collections import deque
import heapq
import time

# =====================================================
# Food Problem: estado = (posicion, frozenset(comidas_restantes))
# =====================================================

def get_start_and_food(layout):
    start = None
    food = set()
    for i,row in enumerate(layout):
        for j,cell in enumerate(row):
            if cell == ".":
                food.add((i,j))
                if start is None:
                    start = (i,j)
    return start, food

def get_neighbors(pos, layout):
    i,j = pos
    moves = [("Up",(i-1,j)), ("Down",(i+1,j)), ("Left",(i,j-1)), ("Right",(i,j+1))]
    rows, cols = len(layout), len(layout[0])
    valid = []
    for action,(ni,nj) in moves:
        if 0<=ni<rows and 0<=nj<cols and layout[ni][nj] != "%":
            valid.append((action,(ni,nj)))
    return valid

def manhattan(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# =====================================================
# BFS
# =====================================================

def bfs_food(layout, start=None):
    start_time = time.time()
    
    rows, cols = len(layout), len(layout[0])
    if start is None:
        for i, row in enumerate(layout):
            for j, cell in enumerate(row):
                if cell == ".":
                    start = (i,j)
                    break
            if start: break

    food_positions = {(i,j) for i in range(rows) for j in range(cols) if layout[i][j] == "."}
    path = []
    current = start
    eaten = set()

    nodes_expanded = 0
    max_depth = 0

    while food_positions - eaten:
        queue = deque([(current, [])])
        visited = set()
        found = False
        while queue and not found:
            pos, moves = queue.popleft()
            if pos in visited: 
                continue
            visited.add(pos)
            nodes_expanded += 1
            max_depth = max(max_depth, len(moves))
            
            if pos in food_positions and pos not in eaten:
                path.extend(moves)
                current = pos
                eaten.add(pos)
                found = True
                break

            i,j = pos
            for direction, (di,dj) in [("Up",(-1,0)),("Down",(1,0)),("Left",(0,-1)),("Right",(0,1))]:
                ni, nj = i+di, j+dj
                if 0<=ni<rows and 0<=nj<cols and layout[ni][nj] != "%":
                    queue.append(((ni,nj), moves+[direction]))

    elapsed_time = time.time() - start_time
    return path, elapsed_time, nodes_expanded, max_depth



# =====================================================
# DFS
# =====================================================
def dfs_food(layout):
    start_pos, food = get_start_and_food(layout)
    start_state = (start_pos, frozenset(food))
    goal_test = lambda state: len(state[1]) == 0

    frontier = [(start_state, [])]
    explored = set()
    nodes_expanded = 0
    max_depth = 0
    t0 = time.time()

    while frontier:
        state, path = frontier.pop()
        if state in explored:
            continue
        explored.add(state)
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))

        if goal_test(state):
            return path, time.time()-t0, nodes_expanded, max_depth

        pos, foods = state
        for action, new_pos in get_neighbors(pos, layout):
            new_foods = set(foods)
            if new_pos in new_foods:
                new_foods.remove(new_pos)
            frontier.append(((new_pos, frozenset(new_foods)), path+[action]))

    return [], time.time()-t0, nodes_expanded, max_depth

# =====================================================
# UCS
# =====================================================
def ucs_food(layout):
    start_pos, food = get_start_and_food(layout)
    start_state = (start_pos, frozenset(food))
    goal_test = lambda state: len(state[1]) == 0

    frontier = [(0, start_state, [])]  # (cost, state, path)
    explored = {}
    nodes_expanded = 0
    max_depth = 0
    t0 = time.time()

    while frontier:
        cost, state, path = heapq.heappop(frontier)
        if state in explored and explored[state] <= cost:
            continue
        explored[state] = cost
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))

        if goal_test(state):
            return path, time.time()-t0, nodes_expanded, max_depth

        pos, foods = state
        for action, new_pos in get_neighbors(pos, layout):
            new_foods = set(foods)
            if new_pos in new_foods:
                new_foods.remove(new_pos)
            heapq.heappush(frontier, (cost+1, (new_pos, frozenset(new_foods)), path+[action]))

    return [], time.time()-t0, nodes_expanded, max_depth

# =====================================================
# Greedy
# =====================================================
def greedy_food(layout):
    start_pos, food = get_start_and_food(layout)
    start_state = (start_pos, frozenset(food))
    goal_test = lambda state: len(state[1]) == 0

    frontier = [(0, start_state, [])]
    explored = set()
    nodes_expanded = 0
    max_depth = 0
    t0 = time.time()

    while frontier:
        h, state, path = heapq.heappop(frontier)
        if state in explored:
            continue
        explored.add(state)
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))

        if goal_test(state):
            return path, time.time()-t0, nodes_expanded, max_depth

        pos, foods = state
        for action, new_pos in get_neighbors(pos, layout):
            new_foods = set(foods)
            if new_pos in new_foods:
                new_foods.remove(new_pos)
            h2 = min([manhattan(new_pos,f) for f in new_foods]) if new_foods else 0
            heapq.heappush(frontier, (h2, (new_pos, frozenset(new_foods)), path+[action]))

    return [], time.time()-t0, nodes_expanded, max_depth

# =====================================================
# A*
# =====================================================
def astar_food(layout):
    start_pos, food = get_start_and_food(layout)
    start_state = (start_pos, frozenset(food))
    goal_test = lambda state: len(state[1]) == 0

    frontier = [(0, 0, start_state, [])]  # (f, g, state, path)
    explored = {}
    nodes_expanded = 0
    max_depth = 0
    t0 = time.time()

    while frontier:
        f, g, state, path = heapq.heappop(frontier)
        if state in explored and explored[state] <= g:
            continue
        explored[state] = g
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))

        if goal_test(state):
            return path, time.time()-t0, nodes_expanded, max_depth

        pos, foods = state
        for action, new_pos in get_neighbors(pos, layout):
            new_foods = set(foods)
            if new_pos in new_foods:
                new_foods.remove(new_pos)
            g2 = g+1
            h2 = min([manhattan(new_pos,f) for f in new_foods]) if new_foods else 0
            heapq.heappush(frontier, (g2+h2, g2, (new_pos,frozenset(new_foods)), path+[action]))

    return [], time.time()-t0, nodes_expanded, max_depth

# =====================================================
# IDDFS
# =====================================================

def iddfs_food(layout, limit=1000):
    start_time = time.time()
    max_depth_reached = 0
    nodes_expanded = 0
    path = []

    def dls(state, depth, current_path, visited):
        nonlocal nodes_expanded, max_depth_reached
        nodes_expanded += 1
        max_depth_reached = max(max_depth_reached, depth)

        pacman_pos, food_left = state
        if not food_left:
            return current_path

        if depth == 0:
            return None

        moves = ["Up", "Down", "Left", "Right"]
        for move in moves:
            ni, nj = pacman_pos
            if move == "Up": ni -= 1
            elif move == "Down": ni += 1
            elif move == "Left": nj -= 1
            elif move == "Right": nj += 1

            if (0 <= ni < len(layout) and 0 <= nj < len(layout[0]) 
                and layout[ni][nj] != "%"):
                new_food = set(food_left)
                if (ni, nj) in new_food:
                    new_food.remove((ni, nj))
                new_state = ((ni, nj), frozenset(new_food))

                if new_state not in visited:
                    visited.add(new_state)
                    result = dls(new_state, depth-1, current_path+[move], visited)
                    if result is not None:
                        return result
        return None

    # posiciones iniciales
    food_positions = {(i,j) for i,row in enumerate(layout) for j,cell in enumerate(row) if cell == "."}
    start_pos = next((i,j) for i,row in enumerate(layout) for j,cell in enumerate(row) if cell == ".")

    solution = None
    for depth in range(1, limit+1):
        visited = set()
        solution = dls((start_pos, frozenset(food_positions)), depth, [], visited)
        if solution is not None:
            elapsed_time = time.time() - start_time
            return solution, elapsed_time, nodes_expanded, depth

    # si no encontró nada en el límite
    elapsed_time = time.time() - start_time
    return [], elapsed_time, nodes_expanded, limit
