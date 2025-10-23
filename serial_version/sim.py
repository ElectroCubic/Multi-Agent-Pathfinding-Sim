import time
import pygame
from config import *
from astar import a_star, reset_nodes
from renderer import draw_grid, draw_elements, draw_text
from node import Node

def simulate():
    move_counter = 0
    grid = [[Node(x, y) for y in range(GRID_SIZE_Y)] for x in range(GRID_SIZE_X)]

    agents, goals = [], []
    paths = {}
    moving = False
    total_time_taken = None
    wait_timer = {}
    wall_mode = False

    running = True
    while running:
        screen.fill(WHITE)
        draw_grid(screen, grid)
        draw_elements(screen, agents, goals, paths)
        draw_text(screen, total_time_taken)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if pygame.mouse.get_pressed()[0]:  # Place/Remove walls
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE_X, my // CELL_SIZE_Y
                if gx < GRID_SIZE_X and gy < GRID_SIZE_Y:
                    if wall_mode:
                        grid[gx][gy].wall = True
                    else:
                        grid[gx][gy].wall = False

            if pygame.mouse.get_pressed()[2]:  # Add agent
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE_X, my // CELL_SIZE_Y
                if gx < GRID_SIZE_X and gy < GRID_SIZE_Y and not grid[gx][gy].wall:
                    node = grid[gx][gy]
                    if node not in agents:
                        agents.append(node)
                        wait_timer[node] = 0

            if pygame.mouse.get_pressed()[1]:  # Add goal
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE_X, my // CELL_SIZE_Y
                if gx < GRID_SIZE_X and gy < GRID_SIZE_Y and not grid[gx][gy].wall:
                    node = grid[gx][gy]
                    if node not in goals:
                        goals.append(node)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paths.clear()
                    start_time = time.time()
                    for agent in agents:
                        best_path, min_len = None, float("inf")
                        for goal in goals:
                            reset_nodes(grid)
                            path = a_star(agent, goal, grid)
                            if path and len(path) < min_len:
                                best_path, min_len = path, len(path)
                        if best_path:
                            paths[agent] = best_path
                    total_time_taken = time.time() - start_time
                    moving = True

                elif event.key == pygame.K_t:
                    wall_mode = not wall_mode

                elif event.key == pygame.K_r:
                    agents.clear()
                    goals.clear()
                    paths.clear()
                    wait_timer.clear()
                    moving = False
                    total_time_taken = None

        # --- COLLISION AVOIDANCE ---
        MAX_WAIT = 10
        if moving:
            move_counter += 1
            if move_counter >= MOVE_DELAY:
                occupied = {(a.x, a.y) for a in agents}
                reserved = set()
                new_paths = {}

                for agent, path in list(paths.items()):
                    if not path:
                        wait_timer[agent] = 0
                        continue

                    next_node = path[0]
                    next_pos = (next_node.x, next_node.y)

                    # Check if space is free
                    if next_pos not in occupied and next_pos not in reserved:
                        reserved.add(next_pos)
                        occupied.remove((agent.x, agent.y))
                        occupied.add(next_pos)

                        agents[agents.index(agent)] = next_node
                        path.pop(0)
                        wait_timer[next_node] = 0
                        if path:
                            new_paths[next_node] = path
                    else:
                        wait_timer[agent] = wait_timer.get(agent, 0) + 1
                        if wait_timer[agent] >= MAX_WAIT:
                            wait_timer[agent] = 0
                            start = agent
                            goal = path[-1]
                            new_path = a_star(start, goal, grid)
                            new_paths[agent] = new_path if new_path else path
                        else:
                            new_paths[agent] = path

                paths = new_paths
                move_counter = 0

            if not any(paths.values()):
                moving = False

        pygame.display.flip()
        clock.tick(CLOCK_RATE)

    pygame.quit()
