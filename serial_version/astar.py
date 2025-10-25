import heapq
from config import GRID_SIZE_X, GRID_SIZE_Y


def heuristic(node_a, node_b):
    return abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)


def get_neighbors(node, grid):
    directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]
    neighbors = []
    for dx, dy in directions:
        nx = node.x + dx
        ny = node.y + dy
        if 0 <= nx < GRID_SIZE_X and 0 <= ny < GRID_SIZE_Y:
            neighbors.append(grid[nx][ny])
    return neighbors


def reset_nodes(grid):
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            grid[x][y].g = float('inf')
            grid[x][y].h = float('inf')
            grid[x][y].parent = None


def a_star(start_node, end_node, grid, avoid_positions=None):
    """
    A* pathfinding algorithm with optional position avoidance.
    
    Args:
        start_node: Starting node
        end_node: Goal node
        grid: 2D grid of nodes
        avoid_positions: Optional set of (x, y) tuples to treat as temporary obstacles
    
    Returns:
        List of nodes representing the path (excluding start_node)
    """
    if avoid_positions is None:
        avoid_positions = set()
    
    open_set = []
    heapq.heappush(open_set, (0, start_node))
    start_node.g = 0
    start_node.h = heuristic(start_node, end_node)
    closed_set = set()

    while len(open_set) > 0:
        _, current = heapq.heappop(open_set)
        
        if current == end_node:
            path = []
            while current.parent is not None:
                path.append(current)
                current = current.parent
            path.reverse()
            return path

        closed_set.add(current)

        for neighbor in get_neighbors(current, grid):
            # Skip if wall, already visited, or in avoid_positions
            if neighbor.wall or neighbor in closed_set:
                continue
            
            # Skip if this position should be avoided (unless it's the goal)
            if (neighbor.x, neighbor.y) in avoid_positions and neighbor != end_node:
                continue

            tentative_g = current.g + 1
            if tentative_g < neighbor.g:
                neighbor.g = tentative_g
                neighbor.h = heuristic(neighbor, end_node)
                neighbor.parent = current
                heapq.heappush(open_set, (neighbor.g + neighbor.h, neighbor))

    return []
