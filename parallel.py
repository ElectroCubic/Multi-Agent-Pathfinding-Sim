import pygame
import heapq
import time
import multiprocessing

CLOCK_RATE = 60
WIDTH, HEIGHT = 600, 650  # Extra 50 px for names
GRID_SIZE = 20
CELL_SIZE = WIDTH // GRID_SIZE
MOVE_DELAY = 10
move_counter = 0

WHITE, BLACK, BLUE, GREEN, RED = (255,255,255), (0,0,0), (0,0,255), (0,255,0), (255,0,0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IMAPPS")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)


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
    dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
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


# Parallel worker function
def compute_best_path(args):
    agent_pos, goals, grid_data = args
    grid = [[Node(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            grid[x][y].wall = grid_data[x][y]

    agent = grid[agent_pos[0]][agent_pos[1]]
    best_path, min_len = None, float("inf")

    for gx, gy in goals:
        goal = grid[gx][gy]
        reset_nodes(grid)
        path = a_star(agent, goal, grid)
        if path and len(path) < min_len:
            best_path, min_len = path, len(path)

    return (agent_pos, [(n.x, n.y) for n in best_path] if best_path else None)


def main():
    global move_counter
    grid = [[Node(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]

    agents, goals = [], []
    paths = {}
    moving = False
    total_time_taken = None

    running = True
    while running:
        screen.fill(WHITE)

        # Draw grid
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = BLACK if grid[x][y].wall else WHITE
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

        # Draw goals
        for g in goals:
            pygame.draw.rect(screen, GREEN, pygame.Rect(g.x*CELL_SIZE, g.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw paths
        for path in paths.values():
            for node in path:
                if node not in goals and node not in agents:
                    pygame.draw.rect(screen, BLUE, pygame.Rect(node.x*CELL_SIZE, node.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw agents
        for a in agents:
            pygame.draw.rect(screen, RED, pygame.Rect(a.x*CELL_SIZE, a.y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Timer display
        if total_time_taken is not None:
            text = font.render(f"Total Time: {total_time_taken:.2f} sec", True, (0, 0, 0))
            screen.blit(text, (10, 10))

        # Display names below the grid
        name1 = font.render("Anush Bundel 2023BCS0005", True, (0, 0, 0))
        name2 = font.render("Ankush 2023BCS0131", True, (0, 0, 0))
        screen.blit(name1, (10, HEIGHT - 45))
        screen.blit(name2, (10, HEIGHT - 25))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                if gx < GRID_SIZE and gy < GRID_SIZE:
                    grid[gx][gy].wall = not grid[gx][gy].wall

            if pygame.mouse.get_pressed()[2]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                if gx < GRID_SIZE and gy < GRID_SIZE and grid[gx][gy] not in agents and not grid[gx][gy].wall:
                    agents.append(grid[gx][gy])

            if pygame.mouse.get_pressed()[1]:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                if gx < GRID_SIZE and gy < GRID_SIZE and grid[gx][gy] not in goals and not grid[gx][gy].wall:
                    goals.append(grid[gx][gy])

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paths.clear()
                    grid_data = [[grid[x][y].wall for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]
                    goals_data = [(g.x, g.y) for g in goals]
                    agent_data = [(a.x, a.y) for a in agents]

                    start_time = time.time()
                    with multiprocessing.Pool() as pool:
                        results = pool.map(compute_best_path, [(a, goals_data, grid_data) for a in agent_data])

                    for agent_pos, path_coords in results:
                        if path_coords:
                            agent_node = grid[agent_pos[0]][agent_pos[1]]
                            path_nodes = [grid[x][y] for (x, y) in path_coords]
                            paths[agent_node] = path_nodes

                    total_time_taken = time.time() - start_time
                    moving = True

                elif event.key == pygame.K_r:
                    agents.clear()
                    goals.clear()
                    paths.clear()
                    moving = False
                    total_time_taken = None

        # Update agent movement
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
                paths = new_paths
                move_counter = 0
            if not paths:
                moving = False

        pygame.display.flip()
        clock.tick(CLOCK_RATE)

    pygame.quit()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
