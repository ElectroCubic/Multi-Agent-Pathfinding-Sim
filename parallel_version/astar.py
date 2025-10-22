
import heapq
from node import Node

def heuristic(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

def get_neighbors(node, grid, grid_size):
    dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
    neighbors = []
    for dx, dy in dirs:
        nx, ny = node.x + dx, node.y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            neighbors.append(grid[nx][ny])
    return neighbors

def reset_nodes(grid, grid_size):
    for x in range(grid_size):
        for y in range(grid_size):
            grid[x][y].g, grid[x][y].h = float('inf'), float('inf')
            grid[x][y].parent = None

def a_star(grid, start, end, grid_size):
    open_set = []
    heapq.heappush(open_set, (0, start))
    start.g, start.h = 0, heuristic(start, end)
    closed_set = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == end:
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            return path[::-1]

        closed_set.add(current)
        for neighbor in get_neighbors(current, grid, grid_size):
            if neighbor.wall or neighbor in closed_set:
                continue
            tentative_g = current.g + 1
            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g, neighbor.h = tentative_g, heuristic(neighbor, end)
                heapq.heappush(open_set, (neighbor.g + neighbor.h, neighbor))
    return []
