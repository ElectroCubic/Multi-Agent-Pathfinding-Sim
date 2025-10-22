
import pygame
import time
import multiprocessing
from config import *
from node import Node
from astar import a_star
from multiprocessing_worker import compute_best_path

def run_simulation():
    move_counter = 0
    grid = [[Node(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
    agents, goals = [], []
    paths = {}
    moving = False
    total_time_taken = None
    wait_timer = {}

    running = True
    while running:
        screen.fill(WHITE)

        # Draw grid
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = BLACK if grid[x][y].wall else WHITE
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

        # Draw goals
        for g in goals:
            pygame.draw.rect(screen, GREEN, pygame.Rect(g.x*CELL_SIZE, g.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw paths
        for path in paths.values():
            for node in path:
                if node not in goals and node not in agents:
                    pygame.draw.rect(screen, BLUE, pygame.Rect(node.x*CELL_SIZE, node.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw agents
        for a in agents:
            pygame.draw.rect(screen, RED, pygame.Rect(a.x*CELL_SIZE, a.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Timer display
        if total_time_taken is not None:
            text = font.render(f"Total Time: {total_time_taken:.2f} sec", True, (0, 0, 0))
            screen.blit(text, (10, 10))

        # Names
        name1 = font.render("Anush Bundel 2023BCS0005", True, BLACK)
        name2 = font.render("Ankush 2023BCS0131", True, BLACK)
        screen.blit(name1, (10, HEIGHT - 45))
        screen.blit(name2, (10, HEIGHT - 25))

        # --- Handle Input ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                if gx < GRID_SIZE and gy < GRID_SIZE:
                    grid[gx][gy].wall = not grid[gx][gy].wall

            if pygame.mouse.get_pressed()[2]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                if gx < GRID_SIZE and gy < GRID_SIZE and not grid[gx][gy].wall and grid[gx][gy] not in agents:
                    agents.append(grid[gx][gy])
                    wait_timer[grid[gx][gy]] = 0

            if pygame.mouse.get_pressed()[1]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                if gx < GRID_SIZE and gy < GRID_SIZE and not grid[gx][gy].wall and grid[gx][gy] not in goals:
                    goals.append(grid[gx][gy])

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paths.clear()
                    grid_data = [[grid[x][y].wall for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
                    goals_data = [(g.x, g.y) for g in goals]
                    agent_data = [(a.x, a.y) for a in agents]

                    start_time = time.time()
                    with multiprocessing.Pool() as pool:
                        results = pool.map(
                            compute_best_path,
                            [(a, goals_data, grid_data, GRID_SIZE) for a in agent_data]
                        )

                    for agent_pos, path_coords in results:
                        if path_coords:
                            agent_node = grid[agent_pos[0]][agent_pos[1]]
                            path_nodes = [grid[x][y] for (x, y) in path_coords]
                            paths[agent_node] = path_nodes

                    total_time_taken = time.time() - start_time
                    moving = True

                if event.key == pygame.K_r:
                    agents.clear()
                    goals.clear()
                    paths.clear()
                    moving = False
                    total_time_taken = None
                    wait_timer.clear()

        # --- Movement ---
        MAX_WAIT = 10
        if moving:
            move_counter += 1
            if move_counter >= MOVE_DELAY:
                new_paths = {}
                occupied = {(a.x, a.y) for a in agents}
                reserved = set()

                for agent, path in list(paths.items()):
                    if not path:
                        wait_timer[agent] = 0
                        continue

                    next_node = path[0]
                    next_pos = (next_node.x, next_node.y)

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
                            new_path = a_star(grid, start, goal, GRID_SIZE)
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
