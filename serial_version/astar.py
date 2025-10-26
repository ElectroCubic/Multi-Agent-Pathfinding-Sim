import heapq
from config import GRID_SIZE_X, GRID_SIZE_Y

def heuristic(a, b):
    """Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(walls, start, goal, avoid_positions=None):
    """
    A* pathfinding using wall map and tuple coordinates.

    Args:
        walls: 2D array of bools (True = wall, False = free)
        start: (x, y)
        goal: (x, y)
        avoid_positions: optional set of (x, y) to treat as temporary obstacles

    Returns:
        list of (x,y) coordinates from start's next step to goal
    """
    if start == goal:
        return []

    if walls[start[0]][start[1]] or walls[goal[0]][goal[1]]:
        return []

    if avoid_positions is None:
        avoid_positions = set()

    open_heap = []
    g_val = {start: 0}
    f_val = {start: heuristic(start, goal)}
    heapq.heappush(open_heap, (f_val[start], start))
    came_from = {}
    closed = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in closed:
            continue

        if current == goal:
            path = []
            cur = current
            while cur in came_from:
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
            return path

        closed.add(current)
        cx, cy = current
        for dx, dy in ((0,1),(1,0),(-1,0),(0,-1)):
            nx, ny = cx + dx, cy + dy
            if not (0 <= nx < GRID_SIZE_X and 0 <= ny < GRID_SIZE_Y):
                continue
            neigh = (nx, ny)
            if walls[nx][ny] or neigh in avoid_positions:
                continue
            tentative_g = g_val[current] + 1
            if tentative_g < g_val.get(neigh, float('inf')):
                g_val[neigh] = tentative_g
                f_val[neigh] = tentative_g + heuristic(neigh, goal)
                came_from[neigh] = current
                heapq.heappush(open_heap, (f_val[neigh], neigh))

    return []  # no path found

def build_wall_map(grid):
    """Convert Node grid to walls array compatible with parallel astar."""
    walls = [[False for _ in range(GRID_SIZE_Y)] for _ in range(GRID_SIZE_X)]
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            walls[x][y] = grid[x][y].wall
    return walls
