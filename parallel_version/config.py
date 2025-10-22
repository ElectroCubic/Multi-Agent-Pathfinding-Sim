
import pygame

CLOCK_RATE = 60
WIDTH, HEIGHT = 600, 650
GRID_SIZE = 20
CELL_SIZE = WIDTH // GRID_SIZE
MOVE_DELAY = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IMAPPS")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
