import time
import pygame
from config import *
from node import Node
from astar import astar, build_wall_map
from renderer import draw_grid, draw_elements, draw_text

def simulate():
    move_counter = 0
    grid = [[Node(x, y) for y in range(GRID_SIZE_Y)] for x in range(GRID_SIZE_X)]
    agents = []
    goals = []
    moving = False
    total_time_taken = 0.0
    wall_mode = True

    running = True
    while running:
        screen.fill(WHITE)
        draw_grid(screen, grid)
        draw_elements(screen, agents, goals)
        draw_text(screen, total_time_taken, wall_mode, agents, goals)

        # --- Input Handling ---
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
                        agents.append({"pos": (gx, gy), "path": None, "wait": 0, "goal": None, "reached_goal": False})

            if pygame.mouse.get_pressed()[1]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE_X, my // CELL_SIZE_Y
                if 0 <= gx < GRID_SIZE_X and 0 <= gy < GRID_SIZE_Y and not grid[gx][gy].wall:
                    node = grid[gx][gy]
                    if node not in goals:
                        goals.append(node)

            # Keyboard inputs
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start_time = time.time()

                    # Reset agents
                    for agent in agents:
                        agent["path"] = None
                        agent["wait"] = 0
                        agent["goal"] = None
                        agent["reached_goal"] = False

                    walls = build_wall_map(grid)
                    assigned_goals = set()
                    unassigned_agents = agents[:]

                    while unassigned_agents and len(assigned_goals) < len(goals):
                        best_assignment = None
                        best_distance = float("inf")

                        for agent in unassigned_agents:
                            sx, sy = agent["pos"]
                            start = (sx, sy)

                            for goal in goals:
                                if goal in assigned_goals:
                                    continue
                                g_pos = (goal.x, goal.y)
                                path_coords = astar(walls, start, g_pos)
                                if path_coords and len(path_coords) < best_distance:
                                    best_assignment = (agent, goal, path_coords)
                                    best_distance = len(path_coords)

                        if best_assignment:
                            agent, goal, path_coords = best_assignment
                            agent["path"] = [grid[x][y] for x, y in path_coords]
                            agent["goal"] = goal
                            assigned_goals.add(goal)
                            unassigned_agents.remove(agent)
                        else:
                            break

                    total_time_taken = time.time() - start_time
                    moving = True

                elif event.key == pygame.K_t:
                    wall_mode = not wall_mode

                elif event.key == pygame.K_r:
                    agents.clear()
                    goals.clear()
                    moving = False
                    total_time_taken = 0.0

        # --- Movement Logic ---
        if moving:
            move_counter += 1
            if move_counter >= MOVE_DELAY:
                occupied = {tuple(a["pos"]) for a in agents}
                reserved = set()
                agents_at_goal = {tuple(a["pos"]) for a in agents if a.get("reached_goal")}

                stuck_agents = []

                for agent in agents:
                    if agent.get("reached_goal"):
                        reserved.add(agent["pos"])
                        continue

                    path = agent.get("path")
                    current_pos = tuple(agent["pos"])

                    if not path or len(path) == 0:
                        agent["path"] = None
                        agent["wait"] = 0
                        reserved.add(current_pos)
                        continue

                    next_pos = (path[0].x, path[0].y)

                    # Swap conflict
                    swap_conflict = any(
                        other is not agent and
                        other.get("path") and len(other["path"]) > 0 and
                        other["path"][0].x == current_pos[0] and
                        other["path"][0].y == current_pos[1] and
                        other["pos"] == next_pos
                        for other in agents
                    )

                    occupied_block = next_pos in reserved or next_pos in occupied or next_pos in agents_at_goal

                    if occupied_block or swap_conflict:
                        agent["wait"] += 1
                        if agent["wait"] >= MAX_WAIT:
                            agent["wait"] = 0
                            stuck_agents.append(agent)
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

                    # Check if reached goal
                    goal = agent.get("goal")
                    if goal and agent["pos"] == (goal.x, goal.y):
                        agent["reached_goal"] = True
                        agent["path"] = None

                # Dynamic replanning for stuck agents
                if stuck_agents:
                    walls = build_wall_map(grid)
                    for agent in stuck_agents:
                        goal = agent.get("goal")
                        if goal:
                            start = agent["pos"]
                            temp_avoid = occupied - {start}
                            path_coords = astar(walls, start, (goal.x, goal.y), avoid_positions=temp_avoid)
                            if path_coords:
                                agent["path"] = [grid[x][y] for x, y in path_coords]

                move_counter = 0

            # Stop moving if all agents finished
            if all(a.get("reached_goal") or a.get("path") is None for a in agents):
                moving = False

        pygame.display.flip()
        clock.tick(CLOCK_RATE)

    pygame.quit()
