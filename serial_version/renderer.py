import pygame
from config import *

def draw_grid(screen, grid):
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = BLACK if grid[x][y].wall else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_elements(screen, agents, goals, paths):
    for g in goals:
        pygame.draw.rect(screen, GREEN, pygame.Rect(g.x*CELL_SIZE, g.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for path in paths.values():
        for node in path:
            if node not in goals and node not in agents:
                pygame.draw.rect(screen, BLUE, pygame.Rect(node.x*CELL_SIZE, node.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for a in agents:
        pygame.draw.rect(screen, RED, pygame.Rect(a.x*CELL_SIZE, a.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_text(screen, total_time_taken):
    if total_time_taken is not None:
        text = font.render(f"Total Time: {total_time_taken:.5f} sec", True, (0, 0, 0))
        screen.blit(text, (10, 10))

    name1 = font.render("Anush Bundel 2023BCS0005", True, (0, 0, 0))
    name2 = font.render("Ankush 2023BCS0131", True, (0, 0, 0))
    screen.blit(name1, (10, HEIGHT - 45))
    screen.blit(name2, (10, HEIGHT - 25))
