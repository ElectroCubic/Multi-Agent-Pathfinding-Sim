import pygame
from config import *

def draw_grid(screen, grid):
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            rect = pygame.Rect(x * CELL_SIZE_X, y * CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y)
            color = WHITE if grid[x][y].wall else BLACK
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_elements(screen, agents, goals):
    for goal in goals:
        rect = pygame.Rect(goal.x * CELL_SIZE_X, goal.y * CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y)
        pygame.draw.rect(screen, GREEN, rect)

    for agent in agents:
        path = agent.get("path")
        if path is not None:
            for node in path:
                node_pos = (node.x, node.y)
                agent_positions = set(a["pos"] for a in agents)
                goal_positions = set((g.x, g.y) for g in goals)
                if node_pos in agent_positions or node_pos in goal_positions:
                    continue
                rect = pygame.Rect(node.x * CELL_SIZE_X, node.y * CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y)
                pygame.draw.rect(screen, BLUE, rect)

    for agent in agents:
        px, py = agent["pos"]
        if any(px == g.x and py == g.y for g in goals):
            color = (128, 128, 128)
        elif agent.get("wait", 0) > 0:
            color = YELLOW
        else:
            color = RED

        rect = pygame.Rect(px * CELL_SIZE_X, py * CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y)
        pygame.draw.rect(screen, color, rect)

def draw_text(screen, total_time_taken, wall_mode):
    if total_time_taken is not None:
        text_surface = font_medium.render(f"Total Time: {total_time_taken:.7f} sec", True, BLACK)
        screen.blit(text_surface, (10, HEIGHT + 10))

    wall_text = f"[Left Click] Add Wall: {wall_mode}"
    wall_surface = font_small.render(wall_text, True, BLACK)
    toggle_surface = font_small.render("[T] Toggle Place/Remove", True, BLACK)
    name1 = font_small.render("Anush Bundel 2023BCS0005", True, BLACK)
    name2 = font_small.render("Ankush 2023BCS0131", True, BLACK)
    run_info = font_small.render("[Space] Run Sim", True, BLACK)
    reset_info = font_small.render("[R] Reset", True, BLACK)
    agent_info = font_small.render("[Right Click] Add Agent", True, BLACK)
    goal_info = font_small.render("[Middle Click] Add Goal", True, BLACK)

    screen.blit(wall_surface, (WIDTH - 680, HEIGHT + 5))
    screen.blit(toggle_surface, (WIDTH - 680, HEIGHT + 30))
    screen.blit(name1, (WIDTH - 380, HEIGHT + 5))
    screen.blit(name2, (WIDTH - 380, HEIGHT + 30))
    screen.blit(run_info, (WIDTH - 900, HEIGHT + 5))
    screen.blit(reset_info, (WIDTH - 900, HEIGHT + 30))
    screen.blit(agent_info, (WIDTH - 1200, HEIGHT + 5))
    screen.blit(goal_info, (WIDTH - 1200, HEIGHT + 30))
