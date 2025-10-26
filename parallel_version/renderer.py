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

def draw_text(screen, total_time_taken, wall_mode, font_small, font_medium, agents, goals):
    if total_time_taken is not None:
        text_surface = font_medium.render(f"Total Time: {total_time_taken:.8f} sec", True, BLACK)
        screen.blit(text_surface, (10, HEIGHT + 20))

    if wall_mode:
        wall_text = f"Wall Mode: Place"
    else:
        wall_text = f"Wall Mode: Remove"
    wall_surface = font_small.render(wall_text, True, BLACK)
    name1 = font_small.render("Anush Bundel 2023BCS0005", True, BLACK)
    name2 = font_small.render("Ankush 2023BCS0131", True, BLACK)

    num_agents = len(agents)
    num_goals = len(goals)
    moving_agents = sum(1 for a in agents if a.get("path"))
    waiting_agents = sum(1 for a in agents if a.get("wait", 0) > 0)

    stats_texts = [
        f"Agents: {num_agents}",
        f"Goals: {num_goals}",
        f"Moving: {moving_agents}",
        f"Waiting: {waiting_agents}"
    ]

    x_offset = WIDTH - 1150
    y_offset = HEIGHT + 23
    spacing = 130
    for i, txt in enumerate(stats_texts):
        stat_surface = font_small.render(txt, True, BLACK)
        screen.blit(stat_surface, (x_offset + i*spacing, y_offset))

    screen.blit(name1, (WIDTH - 380, HEIGHT + 10))
    screen.blit(name2, (WIDTH - 380, HEIGHT + 35))
    screen.blit(wall_surface, (WIDTH - 620, HEIGHT + 23))
