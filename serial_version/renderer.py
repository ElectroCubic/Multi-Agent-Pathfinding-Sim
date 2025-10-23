import pygame
from config import *

def draw_grid(screen, grid):
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            rect = pygame.Rect(x*CELL_SIZE_X, y*CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y)
            color = BLACK if grid[x][y].wall else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_elements(screen, agents, goals, paths):
    for g in goals:
        pygame.draw.rect(screen, GREEN, pygame.Rect(g.x*CELL_SIZE_X, g.y*CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y))
    for path in paths.values():
        for node in path:
            if node not in goals and node not in agents:
                pygame.draw.rect(screen, BLUE, pygame.Rect(node.x*CELL_SIZE_X, node.y*CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y))
    for a in agents:
        pygame.draw.rect(screen, RED, pygame.Rect(a.x*CELL_SIZE_X, a.y*CELL_SIZE_Y, CELL_SIZE_X, CELL_SIZE_Y))

def draw_text(screen, total_time_taken):
    if total_time_taken is not None:
        text = font_medium.render(f"Total Time: {total_time_taken:.5f} sec", True, (0, 0, 0))
        screen.blit(text, (10, HEIGHT + 10))

    name1 = font_small.render("Anush Bundel 2023BCS0005", True, BLACK)
    name2 = font_small.render("Ankush 2023BCS0131", True, BLACK)
    screen.blit(name1, (WIDTH - 380, HEIGHT + 5))
    screen.blit(name2, (WIDTH - 380, HEIGHT + 30))
