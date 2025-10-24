import time
import multiprocessing
import pygame
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
                    # Prepare data for multiprocessing
                    grid_data = [[grid[x][y].wall for y in range(GRID_SIZE_Y)] for x in range(GRID_SIZE_X)]
                    goals_data = [(g.x, g.y) for g in goals]
                    agent_data = [(a["node"].x, a["node"].y) for a in agents]

                    start_time = time.time()
                    with multiprocessing.Pool() as pool:
                        results = pool.map(
                            compute_best_path,
                            [(a, goals_data, grid_data, GRID_SIZE_X, GRID_SIZE_Y) for a in agent_data]
                        )

                    # Assign unique goals after multiprocessing
                    assigned_goals = set()
                    for agent_pos, chosen_goal, path_coords in results:
                        if path_coords:
                            # Skip if goal already taken
                            if chosen_goal in assigned_goals:
                                path_coords = None
                            else:
                                assigned_goals.add(chosen_goal)

                            path_nodes = [grid[x][y] for (x, y) in path_coords] if path_coords else None
                            for a in agents:
                                if a["pos"] == agent_pos:
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

                for a in agents:
                    path = a.get("path")
                    current_pos = tuple(a["pos"])

                    if not path or len(path) == 0:
                        a["path"] = None
                        a["wait"] = 0
                        reserved.add(current_pos)
                        continue

                    next_node = path[0]
                    next_pos = (next_node.x, next_node.y)

                    # Swap / collision detection
                    swap_conflict = False
                    for other in agents:
                        if other is a:
                            continue
                        other_path = other.get("path")
                        other_next = (other_path[0].x, other_path[0].y) if other_path and len(other_path) > 0 else other["pos"]
                        if other_next == current_pos and other["pos"] == next_pos:
                            swap_conflict = True
                            break

                    occupied_block = next_pos in occupied and next_pos not in reserved
                    if next_pos in reserved or occupied_block or swap_conflict:
                        a["wait"] += 1
                        if a["wait"] >= MAX_WAIT:
                            a["wait"] = 0
                            start_node = grid[current_pos[0]][current_pos[1]]
                            goal_node = path[-1]
                            reset_nodes(grid, GRID_SIZE_X, GRID_SIZE_Y)
                            new_path = a_star(grid, start_node, goal_node, GRID_SIZE_X, GRID_SIZE_Y)
                            if new_path:
                                a["path"] = new_path
                        reserved.add(current_pos)
                        continue

                    # Move agent
                    reserved.add(next_pos)
                    occupied.discard(current_pos)
                    occupied.add(next_pos)
                    a["pos"] = next_pos
                    a["node"] = next_node
                    a["wait"] = 0
                    path.pop(0)
                    if len(path) == 0:
                        a["path"] = None

                move_counter = 0

            # Stop moving when all agents done
            if all(a.get("path") is None for a in agents):
                moving = False

        pygame.display.flip()
        clock.tick(CLOCK_RATE)

    pygame.quit()
