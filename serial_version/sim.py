import time
import pygame
from config import *
from astar import a_star, reset_nodes
from renderer import draw_grid, draw_elements, draw_text
from node import Node

def simulate():
    move_counter = 0
    grid = [[Node(x, y) for y in range(GRID_SIZE_Y)] for x in range(GRID_SIZE_X)]

    # Agents are dicts: {"pos": (x,y), "path": [Node,...] or None, "wait": int}
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

            # Mouse: place walls, add agents, add goals
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
                        agents.append({"pos": (gx, gy), "path": None, "wait": 0})

            if pygame.mouse.get_pressed()[1]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE_X, my // CELL_SIZE_Y
                if 0 <= gx < GRID_SIZE_X and 0 <= gy < GRID_SIZE_Y and not grid[gx][gy].wall:
                    node = grid[gx][gy]
                    if node not in goals:
                        goals.append(node)

            # Keyboard: start simulation, toggle wall mode, reset
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start_time = time.time()
                    assigned_goals = set()

                    # Reset agents' paths and wait counters
                    for agent in agents:
                        agent["path"] = None
                        agent["wait"] = 0

                    # Assign unique goals
                    for agent in agents:
                        best_goal = None
                        best_path = None
                        min_len = float("inf")
                        sx, sy = agent["pos"]
                        start_node = grid[sx][sy]

                        for goal in goals:
                            if goal in assigned_goals:
                                continue
                            reset_nodes(grid)
                            path = a_star(start_node, goal, grid)
                            if path and len(path) < min_len:
                                best_goal = goal
                                best_path = path
                                min_len = len(path)

                        if best_path:
                            agent["path"] = best_path[:]  # copy
                            assigned_goals.add(best_goal)
                        else:
                            agent["path"] = None

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
                occupied = {tuple(agent["pos"]) for agent in agents}
                intentions = {}

                # Determine next intended positions
                for agent in agents:
                    path = agent.get("path")
                    if path and len(path) > 0:
                        intentions[id(agent)] = (path[0].x, path[0].y)
                    else:
                        intentions[id(agent)] = agent["pos"]

                reserved = set()

                for agent in agents:
                    pos = agent["pos"]
                    path = agent.get("path")
                    current_pos = tuple(pos)

                    if not path or len(path) == 0:
                        agent["path"] = None
                        agent["wait"] = 0
                        reserved.add(current_pos)
                        continue

                    next_pos = (path[0].x, path[0].y)

                    # Swap detection
                    swap_conflict = False
                    for other in agents:
                        if other is agent:
                            continue
                        if intentions.get(id(other)) == current_pos and other["pos"] == next_pos:
                            swap_conflict = True
                            break

                    occupied_block = next_pos in occupied and next_pos not in {intentions[id(a)] for a in agents if a is not agent}
                    if next_pos in reserved or occupied_block or swap_conflict:
                        agent["wait"] += 1
                        if agent["wait"] >= MAX_WAIT:
                            agent["wait"] = 0
                            start_node = grid[current_pos[0]][current_pos[1]]
                            goal_node = path[-1]
                            reset_nodes(grid)
                            new_path = a_star(start_node, goal_node, grid)
                            if new_path:
                                agent["path"] = new_path[:]
                        reserved.add(current_pos)
                        continue

                    # Move agent
                    reserved.add(next_pos)
                    occupied.discard(current_pos)
                    occupied.add(next_pos)
                    agent["pos"] = next_pos
                    agent["wait"] = 0
                    path.pop(0)
                    if len(path) == 0:
                        agent["path"] = None

                move_counter = 0

            # Stop moving when all agents done
            if all(a.get("path") is None for a in agents):
                moving = False

        pygame.display.flip()
        clock.tick(CLOCK_RATE)

    pygame.quit()
