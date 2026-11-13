import pygame
import random
import asyncio
import sys

pygame.init()

GRID_SIZE = 31
TILE = 25
WIDTH = HEIGHT = GRID_SIZE * TILE
FPS = 60

WALL = 1
PATH = 0

START = (1, 1)
HOME = (GRID_SIZE - 2, GRID_SIZE - 2)

EXTRA_OPENINGS = 45
GEN_STEPS_PER_FRAME = 6

DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

COLOR_BG = (8, 6, 14)
COLOR_PATH = (16, 14, 26)
COLOR_WALL = (30, 18, 52)
COLOR_CURRENT = (241, 196, 15)


class MazeGenerator:
    def __init__(self, size=GRID_SIZE, extra_openings=EXTRA_OPENINGS):
        self.size = size
        self.extra_openings = extra_openings
        self.grid = [[WALL] * size for _ in range(size)]
        self.grid[START[1]][START[0]] = PATH
        self.stack = [START]
        self.current = START
        self.done = False

    def unvisited_neighbors(self, x, y):
        result = []
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 < nx < self.size - 1 and 0 < ny < self.size - 1:
                if self.grid[ny][nx] == WALL:
                    result.append((nx, ny))
        return result

    def step(self):
        if self.done:
            return
        if not self.stack:
            self.add_loops()
            self.done = True
            return

        x, y = self.stack[-1]
        self.current = (x, y)
        neighbors = self.unvisited_neighbors(x, y)
        if neighbors:
            nx, ny = random.choice(neighbors)
            self.grid[(y + ny) // 2][(x + nx) // 2] = PATH
            self.grid[ny][nx] = PATH
            self.stack.append((nx, ny))
        else:
            self.stack.pop()

    def generate(self):
        while not self.done:
            self.step()
        return self.grid

    def add_loops(self):
        g = self.grid
        candidates = []
        for y in range(1, self.size - 1):
            for x in range(1, self.size - 1):
                if g[y][x] != WALL:
                    continue
                horizontal = g[y][x - 1] == PATH and g[y][x + 1] == PATH
                vertical = g[y - 1][x] == PATH and g[y + 1][x] == PATH
                if horizontal != vertical:
                    candidates.append((x, y))
        random.shuffle(candidates)
        for x, y in candidates[: self.extra_openings]:
            g[y][x] = PATH

    def draw(self, surface):
        for y in range(self.size):
            for x in range(self.size):
                color = COLOR_PATH if self.grid[y][x] == PATH else COLOR_WALL
                pygame.draw.rect(surface, color, (x * TILE, y * TILE, TILE, TILE))
        if not self.done:
            cx, cy = self.current
            pygame.draw.rect(
                surface,
                COLOR_CURRENT,
                (cx * TILE + 3, cy * TILE + 3, TILE - 6, TILE - 6),
            )


async def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Money Man - Maze")
    clock = pygame.time.Clock()
    generator = MazeGenerator()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    generator = MazeGenerator()

        for _ in range(GEN_STEPS_PER_FRAME):
            generator.step()

        screen.fill(COLOR_BG)
        generator.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
