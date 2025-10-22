
from node import Node
from astar import a_star, reset_nodes

def compute_best_path(args):
    agent_pos, goals, grid_data, grid_size = args
    grid = [[Node(x, y) for y in range(grid_size)] for x in range(grid_size)]
    for x in range(grid_size):
        for y in range(grid_size):
            grid[x][y].wall = grid_data[x][y]

    agent = grid[agent_pos[0]][agent_pos[1]]
    best_path, min_len = None, float("inf")

    for gx, gy in goals:
        goal = grid[gx][gy]
        reset_nodes(grid, grid_size)
        path = a_star(grid, agent, goal, grid_size)
        if path and len(path) < min_len:
            best_path, min_len = path, len(path)

    return (agent_pos, [(n.x, n.y) for n in best_path] if best_path else None)
