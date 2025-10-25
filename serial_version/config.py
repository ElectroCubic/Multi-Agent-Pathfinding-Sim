import pygame
from pygame._sdl2 import Window

CLOCK_RATE = 60
WIDTH, HEIGHT = 1600, 720
GRID_SIZE_X = 60
GRID_SIZE_Y = 30
CELL_SIZE_X = WIDTH // GRID_SIZE_X
CELL_SIZE_Y = HEIGHT // GRID_SIZE_Y
MOVE_DELAY = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
Window.from_display_module().maximize()
pygame.display.set_caption("IMAPPS - Serial Version")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("Segoe UI", 24)
font_medium = pygame.font.SysFont("Segoe UI", 30, bold=True)