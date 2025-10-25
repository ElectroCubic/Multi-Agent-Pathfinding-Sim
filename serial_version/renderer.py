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

def draw_text(screen, total_time_taken, wall_mode, agents, goals):
    if total_time_taken is not None:
        text_surface = font_medium.render(f"Total Time: {total_time_taken:.7f} sec", True, BLACK)
        screen.blit(text_surface, (10, HEIGHT + 20))

    wall_text = f"[Left Click] Add Wall: {wall_mode}"
    wall_surface = font_small.render(wall_text, True, BLACK)
    toggle_surface = font_small.render("[T] Toggle Place/Remove", True, BLACK)
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

    x_offset = WIDTH - 1210
    y_offset = HEIGHT + 23
    spacing = 130
    for i, txt in enumerate(stats_texts):
        stat_surface = font_small.render(txt, True, BLACK)
        screen.blit(stat_surface, (x_offset + i*spacing, y_offset))

    screen.blit(name1, (WIDTH - 380, HEIGHT + 5))
    screen.blit(name2, (WIDTH - 380, HEIGHT + 30))
    screen.blit(wall_surface, (WIDTH - 680, HEIGHT + 5))
    screen.blit(toggle_surface, (WIDTH - 680, HEIGHT + 30))