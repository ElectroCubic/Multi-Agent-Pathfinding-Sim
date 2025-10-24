# multiprocessing_worker.py
from node import Node
from astar import a_star, reset_nodes

def compute_best_path(args):
    """
    Compute the best path for a single agent to any goal.
    Each worker sees all goals, but the main process will assign
    unique goals after collecting results.

    args = (agent_pos, goals_list, grid_data, grid_size_x, grid_size_y)
    agent_pos: (x, y)
    goals_list: [(x1, y1), ...]
    grid_data: [[bool,...], ...]  # wall info
    """
    agent_pos, goals, grid_data, grid_size_x, grid_size_y = args

    # Rebuild the Node grid
    grid = [[Node(x, y) for y in range(grid_size_y)] for x in range(grid_size_x)]
    for x in range(grid_size_x):
        for y in range(grid_size_y):
            grid[x][y].wall = grid_data[x][y]

    start_node = grid[agent_pos[0]][agent_pos[1]]

    # Find closest goal
    best_path = None
    min_len = float('inf')
    best_goal = None
    for gx, gy in goals:
        goal_node = grid[gx][gy]
        reset_nodes(grid, grid_size_x, grid_size_y)
        path = a_star(grid, start_node, goal_node, grid_size_x, grid_size_y)
        if path and len(path) < min_len:
            best_path = path
            best_goal = (gx, gy)
            min_len = len(path)

    # Convert Node path to tuples for safe multiprocessing
    path_tuples = [(n.x, n.y) for n in best_path] if best_path else None

    # Return both the original agent pos and the chosen goal for assignment
    return agent_pos, best_goal, path_tuples
