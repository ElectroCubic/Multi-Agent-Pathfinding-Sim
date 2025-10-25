import time
import pygame
from config import *
from astar import a_star, reset_nodes
from renderer import draw_grid, draw_elements, draw_text
from node import Node


def simulate():
    move_counter = 0
    grid = [[Node(x, y) for y in range(GRID_SIZE_Y)] for x in range(GRID_SIZE_X)]

    # Agents are dicts: {"pos": (x,y), "path": [Node,...] or None, "wait": int, "goal": Node or None, "reached_goal": bool}
    agents = []
    goals = []
    moving = False
    total_time_taken = 0.0
    wall_mode = False

    MAX_WAIT = 2

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
                        agents.append({"pos": (gx, gy), "path": None, "wait": 0, "goal": None, "reached_goal": False})

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
                    
                    # Reset agents' paths, wait counters, and goal flags
                    for agent in agents:
                        agent["path"] = None
                        agent["wait"] = 0
                        agent["goal"] = None
                        agent["reached_goal"] = False

                    # Assign goals using greedy assignment
                    assigned_goals = set()
                    unassigned_agents = agents[:]
                    
                    # Sort agents by distance to nearest unassigned goal
                    while unassigned_agents and len(assigned_goals) < len(goals):
                        best_assignment = None
                        best_distance = float("inf")
                        
                        for agent in unassigned_agents:
                            sx, sy = agent["pos"]
                            start_node = grid[sx][sy]
                            
                            for goal in goals:
                                if goal in assigned_goals:
                                    continue
                                    
                                reset_nodes(grid)
                                path = a_star(start_node, goal, grid)
                                if path and len(path) < best_distance:
                                    best_assignment = (agent, goal, path)
                                    best_distance = len(path)
                        
                        if best_assignment:
                            agent, goal, path = best_assignment
                            agent["path"] = path[:]
                            agent["goal"] = goal
                            assigned_goals.add(goal)
                            unassigned_agents.remove(agent)
                        else:
                            break  # No valid paths found

                    total_time_taken = time.time() - start_time
                    moving = True

                elif event.key == pygame.K_t:
                    wall_mode = not wall_mode

                elif event.key == pygame.K_r:
                    agents.clear()
                    goals.clear()
                    moving = False
                    total_time_taken = 0.0

        # --- Movement logic ---
        if moving:
            move_counter += 1
            if move_counter >= MOVE_DELAY:
                # Get positions of agents who have reached their goals (they won't move)
                agents_at_goal = {tuple(agent["pos"]) for agent in agents if agent.get("reached_goal")}
                occupied = {tuple(agent["pos"]) for agent in agents}
                intentions = {}

                # Determine next intended positions
                for agent in agents:
                    if agent.get("reached_goal"):
                        intentions[id(agent)] = agent["pos"]
                        continue
                        
                    path = agent.get("path")
                    if path and len(path) > 0:
                        intentions[id(agent)] = (path[0].x, path[0].y)
                    else:
                        intentions[id(agent)] = agent["pos"]

                reserved = set(agents_at_goal)  # Reserve positions of agents at their goals

                for agent in agents:
                    # Skip agents that have reached their goal
                    if agent.get("reached_goal"):
                        continue
                        
                    pos = agent["pos"]
                    path = agent.get("path")
                    goal = agent.get("goal")
                    current_pos = tuple(pos)

                    # Check if agent reached its goal
                    if goal and current_pos == (goal.x, goal.y):
                        agent["reached_goal"] = True
                        agent["path"] = None
                        agent["wait"] = 0
                        reserved.add(current_pos)
                        continue

                    if not path or len(path) == 0:
                        agent["path"] = None
                        agent["wait"] = 0
                        reserved.add(current_pos)
                        continue

                    next_pos = (path[0].x, path[0].y)

                    # Check if goal is blocked by another agent at goal
                    if goal and (goal.x, goal.y) in agents_at_goal and len(path) == 1:
                        # Goal is permanently blocked, need to find alternative or wait
                        agent["wait"] += 1
                        if agent["wait"] >= MAX_WAIT:
                            # Try to find adjacent free position near goal
                            agent["wait"] = 0
                            adjacent_positions = [
                                (goal.x + dx, goal.y + dy)
                                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
                                if 0 <= goal.x + dx < GRID_SIZE_X and 0 <= goal.y + dy < GRID_SIZE_Y
                                and not grid[goal.x + dx][goal.y + dy].wall
                                and (goal.x + dx, goal.y + dy) not in agents_at_goal
                            ]
                            
                            if adjacent_positions:
                                # Find nearest free adjacent position
                                start_node = grid[current_pos[0]][current_pos[1]]
                                best_alt_path = None
                                min_dist = float("inf")
                                
                                for alt_x, alt_y in adjacent_positions:
                                    reset_nodes(grid)
                                    alt_path = a_star(start_node, grid[alt_x][alt_y], grid)
                                    if alt_path and len(alt_path) < min_dist:
                                        best_alt_path = alt_path
                                        min_dist = len(alt_path)
                                
                                if best_alt_path:
                                    agent["path"] = best_alt_path[:]
                                    agent["goal"] = best_alt_path[-1]
                                    continue
                        
                        reserved.add(current_pos)
                        continue

                    # Swap detection
                    swap_conflict = False
                    for other in agents:
                        if other is agent or other.get("reached_goal"):
                            continue
                        if intentions.get(id(other)) == current_pos and other["pos"] == next_pos:
                            swap_conflict = True
                            break

                    occupied_block = next_pos in reserved
                    
                    if occupied_block or swap_conflict:
                        agent["wait"] += 1
                        if agent["wait"] >= MAX_WAIT and goal:
                            agent["wait"] = 0
                            start_node = grid[current_pos[0]][current_pos[1]]
                            reset_nodes(grid)
                            
                            # Mark currently occupied positions as temporary obstacles
                            temp_occupied = occupied - {current_pos}
                            new_path = a_star(start_node, goal, grid, avoid_positions=temp_occupied)
                            
                            if new_path:
                                agent["path"] = new_path[:]
                            else:
                                # If no path found, try waiting
                                agent["wait"] = 0
                        
                        reserved.add(current_pos)
                        continue

                    # Move agent
                    reserved.add(next_pos)
                    occupied.discard(current_pos)
                    occupied.add(next_pos)
                    agent["pos"] = next_pos
                    agent["wait"] = 0
                    path.pop(0)
                    
                    # Check if reached goal after move
                    if goal and next_pos == (goal.x, goal.y):
                        agent["reached_goal"] = True
                        agent["path"] = None

                move_counter = 0

            # Stop moving when all agents done
            if all(a.get("reached_goal") or a.get("path") is None for a in agents):
                moving = False

        pygame.display.flip()
        clock.tick(CLOCK_RATE)

    pygame.quit()
