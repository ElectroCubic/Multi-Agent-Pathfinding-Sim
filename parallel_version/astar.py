import heapq
from config import GRID_SIZE_X, GRID_SIZE_Y

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan Distance

def astar(walls, start, goal):
    """
    walls: 2D array. Indexing: walls[x][y]
    start/goal: (x, y)
    returns: list of (x,y) from start's next step till goal
    """
    if start == goal:
        return []

    sx, sy = start
    gx, gy = goal
    if walls[gx][gy] or walls[sx][sy]:
        return []

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
            if walls[nx][ny]:
                continue
            neigh = (nx, ny)
            tentative_g = g_val[current] + 1
            if tentative_g < g_val.get(neigh, float('inf')):
                came_from[neigh] = current
                g_val[neigh] = tentative_g
                heapq.heappush(open_heap, (tentative_g + heuristic(neigh, goal), neigh))

    return []  # no path found
