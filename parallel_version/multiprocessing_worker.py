from node import Node
from astar import a_star, reset_nodes

def compute_best_path(args):
    """
    args = (agent_pos, goals_list, grid, grid_size_x, grid_size_y, reached_goals)
    agent_pos: (x, y)
    goals_list: [(x1, y1), ...]
    grid: pre-built Node grid (persistent)
    reached_goals: set of (x,y) that should be treated as walls
    """
    agent_pos, goals, grid, grid_size_x, grid_size_y, reached_goals = args

    start_node = grid[agent_pos[0]][agent_pos[1]]

    best_path = None
    min_len = float('inf')
    for gx, gy in goals:
        if (gx, gy) in reached_goals:
            continue  # skip goals that are already taken

        goal_node = grid[gx][gy]

        # Mark reached goals as temp walls
        for x, y in reached_goals:
            grid[x][y].temp_wall = True

        reset_nodes(grid, grid_size_x, grid_size_y)
        path = a_star(grid, start_node, goal_node, grid_size_x, grid_size_y)

        # Clear temp walls
        for x, y in reached_goals:
            grid[x][y].temp_wall = False

        if path and len(path) < min_len:
            best_path = path
            min_len = len(path)

    path_tuples = [(n.x, n.y) for n in best_path] if best_path else None
    return agent_pos, path_tuples
