import time
import multiprocessing
from multiprocessing import shared_memory
import numpy as np
from config import *
from node import Node
from renderer import draw_grid, draw_elements, draw_text
from multiprocessing_worker import compute_best_path, init_worker

# batch size for each worker task
BATCH_SIZE = 4

def _build_wall_map(grid):
    """Return a (GRID_SIZE_X, GRID_SIZE_Y) uint8 numpy array (1 = wall, 0 = free)."""
    arr = np.zeros((GRID_SIZE_X, GRID_SIZE_Y), dtype=np.uint8)
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            if grid[x][y].wall:
                arr[x, y] = 1
    return arr

def _write_to_shm(shm, arr):
    """Write numpy uint8 arr into shared_memory buffer (same shape assumed)."""
    buf = np.ndarray(arr.shape, dtype=np.uint8, buffer=shm.buf)
    np.copyto(buf, arr)

def run_simulation():
    import pygame
    from pygame._sdl2 import Window

    # Pygame init
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    Window.from_display_module().maximize()
    pygame.display.set_caption("Interactive Multi-Agent Parallelized Pathfinding Simulator")
    clock = pygame.time.Clock()
    font_s = pygame.font.SysFont("Segoe UI", 24)
    font_m = pygame.font.SysFont("Segoe UI", 30, bold=True)

    # build persistent Node grid
    grid = [[Node(x, y) for y in range(GRID_SIZE_Y)] for x in range(GRID_SIZE_X)]

    agents = []
    goals = []
    moving = False
    wall_mode = False
    total_time_taken = 0.0
    move_counter = 0
    MAX_WAIT = 2

    # initial wall map and shared memory
    wall_map = _build_wall_map(grid)  # uint8
    shm = shared_memory.SharedMemory(create=True, size=wall_map.nbytes)
    _write_to_shm(shm, wall_map)

    # persistent pool
    num_workers = max(1, multiprocessing.cpu_count() - 1)
    pool = multiprocessing.Pool(
        processes=num_workers,
        initializer=init_worker,
        initargs=(shm.name, (GRID_SIZE_X, GRID_SIZE_Y))
    )

    running = True
    while running:
        # draw
        screen.fill(WHITE)
        draw_grid(screen, grid)
        draw_elements(screen, agents, goals)
        draw_text(screen, total_time_taken, wall_mode, font_s, font_m)

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    wall_mode = not wall_mode
                if event.key == pygame.K_r:
                    agents.clear()
                    goals.clear()
                    moving = False
                    total_time_taken = 0.0
                    # rebuild wall_map from grid and update shm
                    wall_map = _build_wall_map(grid)
                    _write_to_shm(shm, wall_map)
                if event.key == pygame.K_SPACE and agents and goals:
                    start_time = time.time()
                    # prepare inputs
                    goals_data = [(g.x, g.y) for g in goals]
                    reached_goals = {(g.x, g.y) for g in goals if any(a["pos"] == (g.x, g.y) for a in agents)}

                    # agent positions to compute for
                    agent_positions = [(a["node"].x, a["node"].y) for a in agents if a["pos"] not in reached_goals]
                    if agent_positions:
                        # batching
                        batches = []
                        for i in range(0, len(agent_positions), BATCH_SIZE):
                            batch = agent_positions[i:i+BATCH_SIZE]
                            batches.append((batch, goals_data, reached_goals))
                        
                        results_iter = pool.imap_unordered(compute_best_path, batches)
                        # collect and flatten results
                        all_results = []
                        for res in results_iter:
                            # res is list of (agent_pos, path_tuples) per batch
                            all_results.extend(res)
                        

                        # assign results to agents (paths are tuples -> convert to Node)
                        for agent_pos, path_coords in all_results:
                            if path_coords:
                                ax, ay = agent_pos
                                # find the agent instance whose node is (ax,ay) and assign
                                for a in agents:
                                    if a["node"].x == ax and a["node"].y == ay:
                                        path_nodes = [grid[x][y] for (x, y) in path_coords]
                                        a["path"] = path_nodes
                                        break
                    moving = True
                    total_time_taken = time.time() - start_time

        # mouse handling
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            gx, gy = mx // CELL_SIZE_X, my // CELL_SIZE_Y
            if 0 <= gx < GRID_SIZE_X and 0 <= gy < GRID_SIZE_Y:
                grid[gx][gy].wall = wall_mode
                wall_map[gx, gy] = 1 if grid[gx][gy].wall else 0
                _write_to_shm(shm, wall_map)

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

        # movement logic
        if moving:
            move_counter += 1
            if move_counter >= MOVE_DELAY:
                occupied = {tuple(a["pos"]) for a in agents}
                reserved = set()
                reached_goals = {(g.x, g.y) for g in goals if any(a["pos"] == (g.x, g.y) for a in agents)}

                stuck_agents = []  # collect for parallel replan
                for a in agents:
                    path = a.get("path")
                    current_pos = tuple(a["pos"])

                    if not path or len(path) == 0:
                        a["path"] = None
                        a["wait"] = 0
                        reserved.add(current_pos)
                        continue

                    next_pos = (path[0].x, path[0].y)

                    swap_conflict = any(
                        other is not a and
                        other.get("path") and len(other["path"]) > 0 and
                        other["path"][0].x == current_pos[0] and
                        other["path"][0].y == current_pos[1] and
                        other["pos"] == next_pos
                        for other in agents
                    )

                    if next_pos in reserved or next_pos in occupied or next_pos in reached_goals or swap_conflict:
                        a["wait"] += 1
                        if a["wait"] >= MAX_WAIT:
                            stuck_agents.append(a)
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

                # --- Parallel dynamic replanning for stuck agents ---
                if stuck_agents:
                    free_goals = [g for g in goals if (g.x, g.y) not in reached_goals]
                    if free_goals:
                        agent_positions = [(a["pos"][0], a["pos"][1]) for a in stuck_agents]

                        batches = []
                        for i in range(0, len(agent_positions), BATCH_SIZE):
                            batch = agent_positions[i:i + BATCH_SIZE]
                            batches.append((batch, [(g.x, g.y) for g in free_goals], reached_goals))

                        results_iter = pool.imap_unordered(compute_best_path, batches)
                        all_results = []
                        for res in results_iter:
                            all_results.extend(res)

                        # assign replanned paths back
                        for agent_pos, path_coords in all_results:
                            for a in stuck_agents:
                                if a["pos"] == agent_pos and path_coords:
                                    a["path"] = [grid[x][y] for (x, y) in path_coords]
                                    break

                move_counter = 0
            
            if len(reached_goals) == len(goals):
                for agent in agents:
                    if agent["path"] is not None:
                        agent["path"] = None
                        agent["wait"] = 0

            # stop moving when all paths done
            if all(a.get("path") is None for a in agents):
                moving = False

        pygame.display.flip()
        clock.tick(CLOCK_RATE)

    pool.close()
    pool.join()
    shm.close()
    shm.unlink()
    pygame.quit()