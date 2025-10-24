import time
import multiprocessing
from config import *
from node import Node
from astar import a_star, reset_nodes
from renderer import draw_grid, draw_elements, draw_text
from multiprocessing_worker import compute_best_path

def run_simulation():
    move_counter = 0
    grid = [[Node(x, y) for y in range(GRID_SIZE_Y)] for x in range(GRID_SIZE_X)]
    agents = []
    goals = []
    moving = False
    total_time_taken = None
    wall_mode = False
    MAX_WAIT = 10  # ticks before path recalculation

    running = True
    while running:
        screen.fill(WHITE)
        draw_grid(screen, grid)
        draw_elements(screen, agents, goals)
        draw_text(screen, total_time_taken, wall_mode)

        # --- Input handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Mouse inputs
            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE_X, my // CELL_SIZE_Y
                if 0 <= gx < GRID_SIZE_X and 0 <= gy < GRID_SIZE_Y:
                    grid[gx][gy].wall = wall_mode

            if pygame.mouse.get_pressed()[2]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE_X, my // CELL_SIZE_Y
                if 0 <= gx < GRID_SIZE_X and 0 <= gy < GRID_SIZE_Y and not grid[gx][gy].wall:
                    if (gx, gy) not in {a["pos"] for a in agents}:
                        node = grid[gx][gy]
                        agents.append({"node": node, "pos": (node.x, node.y), "path": None, "wait": 0})

            if pygame.mouse.get_pressed()[1]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE_X, my // CELL_SIZE_Y
                if 0 <= gx < GRID_SIZE_X and 0 <= gy < GRID_SIZE_Y and not grid[gx][gy].wall:
                    node = grid[gx][gy]
                    if node not in goals:
                        goals.append(node)

            # Keyboard inputs
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and agents and goals:
                    grid_data = [[grid[x][y].wall for y in range(GRID_SIZE_Y)] for x in range(GRID_SIZE_X)]
                    goals_data = [(g.x, g.y) for g in goals]
                    reached_goals = {(g.x, g.y) for g in goals if any(a["pos"] == (g.x, g.y) for a in agents)}

                    agent_data_to_calc = [
                        (a["node"].x, a["node"].y)
                        for a in agents
                        if a["pos"] not in reached_goals
                    ]

                    start_time = time.time()

                    if agent_data_to_calc:
                        # Reuse the persistent grid for multiprocessing
                        with multiprocessing.Pool() as pool:
                            results = pool.map(
                                compute_best_path,
                                [(a, goals_data, grid, GRID_SIZE_X, GRID_SIZE_Y, reached_goals)
                                for a in agent_data_to_calc]
                            )

                        for agent_pos, path_coords in results:
                            if path_coords:
                                agent_node = grid[agent_pos[0]][agent_pos[1]]
                                path_nodes = [grid[x][y] for (x, y) in path_coords]
                                for a in agents:
                                    if a["pos"] == (agent_node.x, agent_node.y):
                                        a["path"] = path_nodes
                                        break

                    total_time_taken = time.time() - start_time
                    moving = True

                elif event.key == pygame.K_t:
                    wall_mode = not wall_mode

                elif event.key == pygame.K_r:
                    agents.clear()
                    goals.clear()
                    moving = False
                    total_time_taken = None

        # --- Movement logic ---
        if moving:
            move_counter += 1
            if move_counter >= MOVE_DELAY:
                occupied = {tuple(a["pos"]) for a in agents}
                reserved = set()
                reached_goals = {(g.x, g.y) for g in goals if any(a["pos"] == (g.x, g.y) for a in agents)}

                for a in agents:
                    path = a.get("path")
                    current_pos = tuple(a["pos"])

                    if not path or len(path) == 0:
                        a["path"] = None
                        a["wait"] = 0
                        reserved.add(current_pos)
                        continue

                    next_pos = (path[0].x, path[0].y)

                    # Detect swap/collision
                    swap_conflict = any(
                        other is not a and
                        other.get("path") and
                        len(other["path"]) > 0 and
                        other["path"][0].x == current_pos[0] and
                        other["path"][0].y == current_pos[1] and
                        other["pos"] == next_pos
                        for other in agents
                    )

                    # If blocked by anything
                    if next_pos in reserved or next_pos in occupied or next_pos in reached_goals or swap_conflict:
                        a["wait"] += 1
                        if a["wait"] >= MAX_WAIT:
                            # Recalculate path to a completely new goal
                            start_node = grid[current_pos[0]][current_pos[1]]

                            # Build a temporary grid copy
                            temp_grid = [[Node(x, y) for y in range(GRID_SIZE_Y)] for x in range(GRID_SIZE_X)]
                            for x in range(GRID_SIZE_X):
                                for y in range(GRID_SIZE_Y):
                                    temp_grid[x][y].wall = grid[x][y].wall or (x, y) in occupied or (x, y) in reached_goals

                            free_goals = [g for g in goals if (g.x, g.y) not in reached_goals]
                            new_best = None
                            min_len = float('inf')
                            for g in free_goals:
                                reset_nodes(temp_grid, GRID_SIZE_X, GRID_SIZE_Y)
                                path = a_star(temp_grid, temp_grid[current_pos[0]][current_pos[1]],
                                              temp_grid[g.x][g.y], GRID_SIZE_X, GRID_SIZE_Y)
                                if path and len(path) < min_len:
                                    new_best = path
                                    min_len = len(path)

                            a["path"] = new_best
                            a["wait"] = 0
                        reserved.add(current_pos)
                        continue

                    # Normal move
                    reserved.add(next_pos)
                    occupied.discard(current_pos)
                    occupied.add(next_pos)
                    a["pos"] = next_pos
                    a["node"] = path[0]
                    a["wait"] = 0
                    path.pop(0)
                    if len(path) == 0:
                        a["path"] = None

                move_counter = 0

            if all(a.get("path") is None for a in agents):
                moving = False

        pygame.display.flip()
        clock.tick(CLOCK_RATE)

    pygame.quit()
