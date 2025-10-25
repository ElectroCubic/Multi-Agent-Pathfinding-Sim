import pygame
from config import *

def draw_grid(screen, grid):
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            rect = pygame.Rect(x * CELL_SIZE_X, y * CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y)
            color = BLACK if grid[x][y].wall else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_elements(screen, agents, goals):
    # Draw goals
    for g in goals:
        pygame.draw.rect(screen, GREEN, pygame.Rect(g.x * CELL_SIZE_X, g.y * CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y))

    # Draw agent paths
    for agent in agents:
        path = agent.get("path")
        if path:
            for node in path:
                pos = (node.x, node.y)
                agent_positions = {a["pos"] for a in agents}
                goal_positions = {(g.x, g.y) for g in goals}
                if pos in agent_positions or pos in goal_positions:
                    continue
                pygame.draw.rect(screen, BLUE, pygame.Rect(node.x * CELL_SIZE_X, node.y * CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y))

    # Draw agents
    for a in agents:
        px, py = a["pos"]
        if any(px == g.x and py == g.y for g in goals):
            color = GRAY
        elif a.get("wait", 0) > 0:
            color = YELLOW
        else:
            color = RED
        pygame.draw.rect(screen, color, pygame.Rect(px * CELL_SIZE_X, py * CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y))

def draw_text(screen, total_time_taken, wall_mode, font_small, font_medium):
    if total_time_taken is not None:
        t = font_medium.render(f"Total Time: {total_time_taken:.7f} sec", True, BLACK)
        screen.blit(t, (10, HEIGHT + 10))

    wall_text = font_small.render(f"Place/Remove: {wall_mode}", True, BLACK)
    wall_control = font_small.render("Press T to Toggle", True, BLACK)
    name1 = font_small.render("Anush Bundel 2023BCS0005", True, BLACK)
    name2 = font_small.render("Ankush 2023BCS0131", True, BLACK)

    screen.blit(name1, (WIDTH - 380, HEIGHT + 5))
    screen.blit(name2, (WIDTH - 380, HEIGHT + 30))
    screen.blit(wall_text, (WIDTH - 650, HEIGHT + 5))
    screen.blit(wall_control, (WIDTH - 650, HEIGHT + 30))

    run_info = font_small.render("Press Space to Run", True, BLACK)
    reset_info = font_small.render("Press R to Reset", True, BLACK)
    rightclick_info = font_small.render("Right Click - Agent", True, BLACK)
    middle_info = font_small.render("Middle Click - Goal", True, BLACK)

    screen.blit(run_info, (WIDTH - 900, HEIGHT + 5))
    screen.blit(reset_info, (WIDTH - 900, HEIGHT + 30))
    screen.blit(rightclick_info, (WIDTH - 1150, HEIGHT + 5))
    screen.blit(middle_info, (WIDTH - 1150, HEIGHT + 30))
