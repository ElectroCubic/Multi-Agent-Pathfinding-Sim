
import heapq

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(walls, start, goal, grid_w, grid_h):
    """
    walls: 2D array-like truthy for blocked cells. Indexing: walls[x][y]
    start/goal: (x, y)
    returns: list of (x,y) from start's next step ... goal (does NOT include start)
    """
    if start == goal:
        return []

    sx, sy = start
    gx, gy = goal
    if walls[gx][gy] or walls[sx][sy]:
        return []

    open_heap = []
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    heapq.heappush(open_heap, (fscore[start], start))
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
            return path  # list of (x,y)

        closed.add(current)
        cx, cy = current
        for dx, dy in ((0,1),(1,0),(-1,0),(0,-1)):
            nx, ny = cx + dx, cy + dy
            if not (0 <= nx < grid_w and 0 <= ny < grid_h):
                continue
            if walls[nx][ny]:
                continue
            neigh = (nx, ny)
            tentative_g = gscore[current] + 1
            if tentative_g < gscore.get(neigh, float('inf')):
                came_from[neigh] = current
                gscore[neigh] = tentative_g
                f = tentative_g + heuristic(neigh, goal)
                heapq.heappush(open_heap, (f, neigh))

    return []  # no path found
