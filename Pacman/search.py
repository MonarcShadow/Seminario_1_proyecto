from collections import deque
import heapq

def bfs(layout):
    start = find_start(layout)
    frontier = deque([start])
    came_from = {start: None}
    visited = set([start])
    nodos_expandidos = 0
    profundidad_max = 0

    while frontier:
        current = frontier.popleft()
        nodos_expandidos += 1

        if is_goal(layout, current):
            path = reconstruct_path(came_from, current)
            return path, {"nodos_expandidos": nodos_expandidos, "profundidad_max": profundidad_max}

        for next_node in neighbors(layout, current):
            if next_node not in visited:
                visited.add(next_node)
                frontier.append(next_node)
                came_from[next_node] = current
                profundidad_max = max(profundidad_max, len(reconstruct_path(came_from, next_node)))

    return [], {"nodos_expandidos": nodos_expandidos, "profundidad_max": profundidad_max}


def dfs(layout):
    start = find_start(layout)
    frontier = [start]
    came_from = {start: None}
    visited = set([start])
    nodos_expandidos = 0
    profundidad_max = 0

    while frontier:
        current = frontier.pop()
        nodos_expandidos += 1

        if is_goal(layout, current):
            path = reconstruct_path(came_from, current)
            return path, {"nodos_expandidos": nodos_expandidos, "profundidad_max": profundidad_max}

        for next_node in neighbors(layout, current):
            if next_node not in visited:
                visited.add(next_node)
                frontier.append(next_node)
                came_from[next_node] = current
                profundidad_max = max(profundidad_max, len(reconstruct_path(came_from, next_node)))

    return [], {"nodos_expandidos": nodos_expandidos, "profundidad_max": profundidad_max}


def ucs(layout):
    start = find_start(layout)
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    nodos_expandidos = 0
    profundidad_max = 0

    while frontier:
        cost, current = heapq.heappop(frontier)
        nodos_expandidos += 1

        if is_goal(layout, current):
            path = reconstruct_path(came_from, current)
            return path, {"nodos_expandidos": nodos_expandidos, "profundidad_max": profundidad_max}

        for next_node in neighbors(layout, current):
            new_cost = cost_so_far[current] + 1
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                heapq.heappush(frontier, (new_cost, next_node))
                came_from[next_node] = current
                profundidad_max = max(profundidad_max, len(reconstruct_path(came_from, next_node)))

    return [], {"nodos_expandidos": nodos_expandidos, "profundidad_max": profundidad_max}


def greedySearch(layout):
    start = find_start(layout)
    goal = find_goal(layout)
    frontier = [(heuristic(start, goal), start)]
    came_from = {start: None}
    visited = set([start])
    nodos_expandidos = 0
    profundidad_max = 0

    while frontier:
        _, current = heapq.heappop(frontier)
        nodos_expandidos += 1

        if is_goal(layout, current):
            path = reconstruct_path(came_from, current)
            return path, {"nodos_expandidos": nodos_expandidos, "profundidad_max": profundidad_max}

        for next_node in neighbors(layout, current):
            if next_node not in visited:
                visited.add(next_node)
                heapq.heappush(frontier, (heuristic(next_node, goal), next_node))
                came_from[next_node] = current
                profundidad_max = max(profundidad_max, len(reconstruct_path(came_from, next_node)))

    return [], {"nodos_expandidos": nodos_expandidos, "profundidad_max": profundidad_max}


def aStarSearch(layout):
    start = find_start(layout)
    goal = find_goal(layout)
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    nodos_expandidos = 0
    profundidad_max = 0

    while frontier:
        _, current = heapq.heappop(frontier)
        nodos_expandidos += 1

        if is_goal(layout, current):
            path = reconstruct_path(came_from, current)
            return path, {"nodos_expandidos": nodos_expandidos, "profundidad_max": profundidad_max}

        for next_node in neighbors(layout, current):
            new_cost = cost_so_far[current] + 1
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(next_node, goal)
                heapq.heappush(frontier, (priority, next_node))
                came_from[next_node] = current
                profundidad_max = max(profundidad_max, len(reconstruct_path(came_from, next_node)))

    return [], {"nodos_expandidos": nodos_expandidos, "profundidad_max": profundidad_max}


def iddfs(layout, limit=1000):
    start = find_start(layout)
    nodos_expandidos = 0

    def dls(node, depth, came_from):
        nonlocal nodos_expandidos
        nodos_expandidos += 1
        if is_goal(layout, node):
            return reconstruct_path(came_from, node)
        if depth == 0:
            return None
        for next_node in neighbors(layout, node):
            if next_node not in came_from:
                came_from[next_node] = node
                result = dls(next_node, depth-1, came_from)
                if result:
                    return result
        return None

    for depth in range(limit):
        came_from = {start: None}
        path = dls(start, depth, came_from)
        if path:
            return path, {"nodos_expandidos": nodos_expandidos, "profundidad_max": depth}

    return [], {"nodos_expandidos": nodos_expandidos, "profundidad_max": limit}


def find_start(layout):
    for i,row in enumerate(layout):
        for j,cell in enumerate(row):
            if cell == ".":
                return (i,j)
    return (0,0)

def find_goal(layout):
    for i,row in enumerate(layout[::-1]):
        for j,cell in enumerate(row[::-1]):
            if cell == ".":
                return (len(layout)-1-i, len(row)-1-j)
    return (len(layout)-1, len(layout[0])-1)

def is_goal(layout, pos):
    return pos == find_goal(layout)

def neighbors(layout, pos):
    i,j = pos
    moves = [(i-1,j,"Up"), (i+1,j,"Down"), (i,j-1,"Left"), (i,j+1,"Right")]
    valid = []
    for ni,nj,move in moves:
        if 0<=ni<len(layout) and 0<=nj<len(layout[0]) and layout[ni][nj] != "%":
            valid.append((ni,nj))
    return valid

def reconstruct_path(came_from, current):
    path = []
    while came_from[current] is not None:
        pi,pj = came_from[current]
        ci,cj = current
        if ci < pi: path.append("Up")
        elif ci > pi: path.append("Down")
        elif cj < pj: path.append("Left")
        elif cj > pj: path.append("Right")
        current = came_from[current]
    return path[::-1]

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])
