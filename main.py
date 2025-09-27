import pygame
import heapq

CLOCK_RATE = 60
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
CELL_SIZE = WIDTH // GRID_SIZE
MOVE_DELAY = 10
move_counter = 0

WHITE, BLACK, BLUE, GREEN, RED = (255,255,255), (0,0,0), (0,0,255), (0,255,0), (255,0,0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


class Node:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.parent, self.g, self.h = None, float('inf'), float('inf')
        self.wall = False

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)


def heuristic(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)


def get_neighbors(node, grid):
    dirs = [(0,1),(1,0),(-1,0),(0,-1)]
    neighbors = []
    for dx, dy in dirs:
        nx, ny = node.x + dx, node.y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            neighbors.append(grid[nx][ny])
    return neighbors


def a_star(start, end, grid):
    open_set = []
    heapq.heappush(open_set, (0, start))
    start.g, start.h = 0, heuristic(start, end)
    closed_set = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == end:
            path = []
            while current.parent:
                path.append(current)
                current = current.parent
            return path[::-1]

        closed_set.add(current)
        for neighbor in get_neighbors(current, grid):
            if neighbor.wall or neighbor in closed_set:
                continue
            tentative_g = current.g + 1
            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g, neighbor.h = tentative_g, heuristic(neighbor, end)
                heapq.heappush(open_set, (neighbor.g + neighbor.h, neighbor))
    return []


def reset_nodes(grid):
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            grid[x][y].g, grid[x][y].h = float('inf'), float('inf')
            grid[x][y].parent = None


grid = [[Node(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]

agents = []       # list of current agent nodes
goals = []        # list of goal nodes
paths = {}        # mapping: agent -> path
moving = False

running = True

while running:
    screen.fill(WHITE)

    # draw grid and walls
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = BLACK if grid[x][y].wall else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

    # draw goals
    for g in goals:
        pygame.draw.rect(screen, GREEN, pygame.Rect(g.x*CELL_SIZE, g.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # draw paths
    for path in paths.values():
        for node in path:
            if node not in goals and node not in agents:
                pygame.draw.rect(screen, BLUE, pygame.Rect(node.x*CELL_SIZE, node.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # draw agents
    for a in agents:
        pygame.draw.rect(screen, RED, pygame.Rect(a.x*CELL_SIZE, a.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if pygame.mouse.get_pressed()[0]:  # left click -> wall
            mx, my = pygame.mouse.get_pos()
            gx, gy = mx // CELL_SIZE, my // CELL_SIZE
            grid[gx][gy].wall = not grid[gx][gy].wall

        if pygame.mouse.get_pressed()[2]:  # right click -> agent
            mx, my = pygame.mouse.get_pos()
            gx, gy = mx // CELL_SIZE, my // CELL_SIZE
            if grid[gx][gy] not in agents and not grid[gx][gy].wall:
                agents.append(grid[gx][gy])

        if pygame.mouse.get_pressed()[1]:  # middle click -> goal
            mx, my = pygame.mouse.get_pos()
            gx, gy = mx // CELL_SIZE, my // CELL_SIZE
            if grid[gx][gy] not in goals and not grid[gx][gy].wall:
                goals.append(grid[gx][gy])

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paths.clear()
                for agent in agents:
                    best_path, best_goal = None, None
                    min_len = float('inf')
                    for goal in goals:
                        reset_nodes(grid)
                        path = a_star(agent, goal, grid)
                        if path and len(path) < min_len:
                            best_path, best_goal = path, goal
                            min_len = len(path)
                    if best_path:
                        paths[agent] = best_path
                moving = True

            elif event.key == pygame.K_r:
                agents.clear()
                goals.clear()
                paths.clear()
                moving = False

    # update agent movement
    if moving:
        move_counter += 1
        if move_counter >= MOVE_DELAY:
            new_paths = {}
            for agent, path in list(paths.items()):
                if path:
                    new_pos = path.pop(0)
                    agents[agents.index(agent)] = new_pos
                    if path:
                        new_paths[new_pos] = path
                # if no path left, agent stays at goal
            paths = new_paths
            move_counter = 0
        if not paths:  # all agents reached their goals
            moving = False

    pygame.display.flip()
    clock.tick(CLOCK_RATE)

pygame.quit()
