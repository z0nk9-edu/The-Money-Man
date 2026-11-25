import pygame
import random
from collections import defaultdict

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
COLOR_PLAYER = (46, 204, 113)
COLOR_HOME = (52, 152, 219)


class Maze:
    def __init__(self, chips, size=GRID_SIZE):
        self.size = size
        self.grid = [[WALL] * size for _ in range(size)]
        self.grid[START[1]][START[0]] = PATH
        self.stack = [START]
        self.current = START
        self.done = False
        self.player = MazePlayer(START, self, chips)
        self.ais = []
        self.ai_directions = [random.choice(DIRECTIONS) for _ in range(3)]
        self.ai_memory = [defaultdict(int) for _ in range(3)]
        self.ai_chasing = []
        self.ai_timers = []
        self.ai_stun_timers = []

    def step(self):
        if self.done:
            return

        if self.stack:
            x, y = self.current
            neighbors = [
                (x + dx * 2, y + dy * 2)
                for dx, dy in DIRECTIONS
                if 0 <= x + dx * 2 < self.size
                and 0 <= y + dy * 2 < self.size
                and self.grid[y + dy * 2][x + dx * 2] == WALL
            ]
            if neighbors:
                nx, ny = random.choice(neighbors)
                self.grid[ny][nx] = PATH
                self.grid[y + (ny - y) // 2][x + (nx - x) // 2] = PATH
                self.stack.append((nx, ny))
                self.current = (nx, ny)
            else:
                self.current = self.stack.pop()
        else:
            self.done = True
            self.add_extra_openings()
            for _ in range(3):
                cell = (random.randrange(1, self.size), random.randrange(1, self.size))
                while (
                    self.grid[cell[1]][cell[0]] == PATH or cell == START or cell == HOME
                ):
                    cell = (
                        random.randrange(1, self.size),
                        random.randrange(1, self.size),
                    )
                self.ais.append(MazePlayer(cell, self))
            self.ai_chasing = [False] * len(self.ais)
            self.ai_timers = [0] * len(self.ais)
            self.ai_stun_timers = [0] * len(self.ais)

    def add_extra_openings(self):
        for _ in range(self.size**2 // 6):
            x, y = random.randrange(1, self.size), random.randrange(1, self.size)
            if self.grid[y][x] == WALL:
                self.grid[y][x] = PATH

    def move_player(self, dx, dy):
        if not self.done:
            return
        self.player.move(dx, dy)

    def update_ais(self):
        if not self.done:
            return
        if len(self.ai_timers) != len(self.ais):
            self.ai_timers = [0] * len(self.ais)
        if len(self.ai_chasing) != len(self.ais):
            self.ai_chasing = [False] * len(self.ais)
        if len(self.ai_stun_timers) != len(self.ais):
            self.ai_stun_timers = [0] * len(self.ais)

        for i, ai in enumerate(self.ais):
            # If the AI is stunned after catching the player, skip its turn and decrement timer
            if self.ai_stun_timers[i] > 0:
                self.ai_stun_timers[i] -= 1
                continue

            visible = False
            for direction in DIRECTIONS:
                for step in range(1, 11):
                    check_x = ai.position[0] + direction[0] * step
                    check_y = ai.position[1] + direction[1] * step
                    if not self.valid_move(check_x, check_y):
                        break
                    if (check_x, check_y) == self.player.position:
                        visible = True
                        break
                if visible:
                    break

            self.ai_chasing[i] = visible
            if visible:
                self.ai_memory[i][self.player.position] += 1

            interval = 15 if visible else 30
            self.ai_timers[i] += 1

            if self.ai_timers[i] >= interval:
                self.ai_timers[i] = 0
                self._move_single_ai(i, visible)

    def _move_single_ai(self, i, visible):
        ai = self.ais[i]
        valid_dirs = [
            d
            for d in DIRECTIONS
            if self.valid_move(ai.position[0] + d[0], ai.position[1] + d[1])
        ]
        is_crossroads = len(valid_dirs) > 2

        current_dir = self.ai_directions[i]
        next_pos = (
            ai.position[0] + current_dir[0],
            ai.position[1] + current_dir[1],
        )
        is_path_blocked = not self.valid_move(next_pos[0], next_pos[1])

        chosen_dir = current_dir

        if visible:
            dx = self.player.position[0] - ai.position[0]
            dy = self.player.position[1] - ai.position[1]
            if abs(dx) > abs(dy):
                chosen_dir = (1 if dx > 0 else -1, 0)
            else:
                chosen_dir = (0, 1 if dy > 0 else -1)
            if not self.valid_move(
                ai.position[0] + chosen_dir[0], ai.position[1] + chosen_dir[1]
            ):
                if valid_dirs:
                    chosen_dir = random.choice(valid_dirs)
        elif self.ai_memory[i] and (is_crossroads or is_path_blocked):
            likely_position = max(self.ai_memory[i], key=self.ai_memory[i].get)
            dx = likely_position[0] - ai.position[0]
            dy = likely_position[1] - ai.position[1]
            if abs(dx) > abs(dy):
                chosen_dir = (1 if dx > 0 else -1, 0)
            else:
                chosen_dir = (0, 1 if dy > 0 else -1)
            if not self.valid_move(
                ai.position[0] + chosen_dir[0], ai.position[1] + chosen_dir[1]
            ):
                if valid_dirs:
                    chosen_dir = random.choice(valid_dirs)
        elif is_path_blocked or is_crossroads:
            non_reverse_dirs = [
                d
                for d in valid_dirs
                if (d[0] != -current_dir[0] or d[1] != -current_dir[1])
            ]
            if non_reverse_dirs:
                chosen_dir = random.choice(non_reverse_dirs)
            elif valid_dirs:
                chosen_dir = random.choice(valid_dirs)
        else:
            if self.valid_move(
                ai.position[0] + current_dir[0], ai.position[1] + current_dir[1]
            ):
                chosen_dir = current_dir
            elif valid_dirs:
                chosen_dir = random.choice(valid_dirs)

        self.ai_directions[i] = chosen_dir
        ai.move(chosen_dir[0], chosen_dir[1])

        if ai.position == self.player.position:
            self.player.lose_chips(50)
            self.ai_stun_timers[i] = 120

    def valid_move(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size and self.grid[y][x] == PATH

    def player_visible(self):
        ais = []
        for ai in self.ais:
            for direction in DIRECTIONS:
                for step in range(1, 6):
                    check_x = ai.position[0] + direction[0] * step
                    check_y = ai.position[1] + direction[1] * step
                    if not self.valid_move(check_x, check_y):
                        break
                    if (check_x, check_y) == self.player.position:
                        ais.append((self.ais.index(ai), direction))
        return ais

    def draw(self, screen):
        for y in range(self.size):
            for x in range(self.size):
                color = COLOR_PATH if self.grid[y][x] == PATH else COLOR_WALL
                pygame.draw.rect(screen, color, (x * TILE, y * TILE, TILE, TILE))
        hx, hy = HOME
        pygame.draw.rect(screen, COLOR_HOME, (hx * TILE, hy * TILE, TILE, TILE))
        if self.done:
            px, py = self.player.position
            pygame.draw.circle(
                screen,
                COLOR_PLAYER,
                (px * TILE + TILE // 2, py * TILE + TILE // 2),
                TILE // 2 - 3,
            )
            for i, ai in enumerate(self.ais):
                ax, ay = ai.position
                ai_color = (
                    (255, 0, 0)
                    if (i < len(self.ai_chasing) and self.ai_chasing[i])
                    else (255, 165, 0)
                )
                pygame.draw.circle(
                    screen,
                    ai_color,
                    (ax * TILE + TILE // 2, ay * TILE + TILE // 2),
                    TILE // 2 - 3,
                )
        else:
            cx, cy = self.current
            pygame.draw.rect(
                screen,
                COLOR_CURRENT,
                (cx * TILE + 3, cy * TILE + 3, TILE - 6, TILE - 6),
            )


class MazePlayer:
    def __init__(self, position, maze, chips=100):
        self.position = position
        self.maze = maze
        self.chips = chips

    def move(self, dx, dy):
        nx, ny = self.position[0] + dx, self.position[1] + dy
        if self.maze.valid_move(nx, ny):
            self.position = (nx, ny)

    def reached_home(self):
        return self.position == HOME

    def lose_chips(self, amount):
        self.chips = max(0, self.chips - amount)
