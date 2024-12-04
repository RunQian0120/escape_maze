import pygame
import sys
from loader import get_maze
import numpy as np

pygame.init()

P1_START = -1
P2_START = -2

FPS = 30
SHOOT_INTERVAL = 1000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RED = (255, 0, 0)
LIGHT_RED = (255, 102, 102)

GREEN = (0, 200, 0)

BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)

YELLOW = (204, 204, 0)
PURPLE = (128, 0, 128)

ORANGE = (255, 165, 0)

WALL_COLOR = BLACK
PATH_COLOR = WHITE
TURRET_COLOR = PURPLE
CHECKPOINT_COLOR = ORANGE
ACTIVE_CHECKPOINT_COLOR = GREEN

P1_WALL = LIGHT_RED
P2_WALL = LIGHT_BLUE

PLAYER1_COLOR = BLUE
END_POINT_COLOR = RED

image_path = 'maze_hard_v1.png'
MAZE_LAYOUTS = ['maze_hard_v1.png']
NUM_LAYOUTS = 1
MAZE = get_maze(image_path)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

CELL_SIZE = SCREEN_WIDTH // len(MAZE[0])

class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, CELL_SIZE - 10, CELL_SIZE - 10) 
        self.direction = direction
        self.speed = CELL_SIZE

    def move(self):
        if self.direction == 'up':
            self.rect.y -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'right':
            self.rect.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.rect)

    def collide(self, maze):
        grid_x = self.rect.x // CELL_SIZE
        grid_y = self.rect.y // CELL_SIZE
        
        if grid_x < 0 or grid_x >= len(maze.maze[0]) or grid_y < 0 or grid_y >= len(maze.maze):
            return True 
        if maze.maze[grid_y][grid_x] == 1:
            return True
        return False

DIRECTIONS = [("down",0,1),("up",0,-1),("right",1,0),("left",-1,0)]
class Turret:
    def __init__(self, x, y):
        self.pos_x = x
        self.pos_y = y
        self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        self.bullets = []

    def shoot(self, maze):
        h = len(maze.maze)
        w = len(maze.maze[0])
        grid_x = self.pos_x // CELL_SIZE
        grid_y = self.pos_y // CELL_SIZE
        
        for dir, d_x, d_y in DIRECTIONS:
            new_x = grid_x + d_x
            new_y = grid_y + d_y

            if 0 <= new_x < w and 0 <= new_y < h:
                if maze.maze[new_y][new_x] != 1 and maze.maze[new_y][new_x] != 2:
                    bullet = Bullet(new_x*CELL_SIZE, new_y*CELL_SIZE, dir)
                    self.bullets.append(bullet)

    def update_bullets(self, maze):
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.collide(maze):
                self.bullets.remove(bullet)

        if self.check_player_collision(maze.p1):
            maze.p1.move_specific(maze.p1_spawn[0], maze.p1_spawn[1])

    def check_player_collision(self, player):
        for bullet in self.bullets[:]:
            if bullet.rect.colliderect(player.rect):
                return True

    def draw(self, screen):
        pygame.draw.rect(screen, TURRET_COLOR, self.rect)
        for bullet in self.bullets:
            bullet.draw(screen)

class Player:
    def __init__(self, start, color, controls):
        x,y = start
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x, y, CELL_SIZE - 2, CELL_SIZE - 2)
        self.color = color
        self.controls = controls
    
    def react_keys(self, event, maze):
        up, down, right, left = self.controls
        if event == left:
            self.move(-1, 0, maze)
        elif event == right:
            self.move(1, 0, maze)
        elif event == up:
            self.move(0, -1, maze)
        elif event == down:
            self.move(0, 1, maze)


    def move(self, dx, dy, maze):
        if self.movable(dx, dy, maze):
            self.rect.x += dx * CELL_SIZE
            self.rect.y += dy * CELL_SIZE

    def move_specific(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def movable(self, dx, dy, maze):
        new_rect = self.rect.move(dx * CELL_SIZE, dy * CELL_SIZE)
        i, j = new_rect.y // CELL_SIZE, new_rect.x // CELL_SIZE

        return maze.maze[i][j] != 1 and maze.maze[i][j] != 2

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class Maze:
    def __init__(self, maze, p1):
        self.p1 = p1

        self.maze = maze
        self.turrets = []
        self.checkpoints = []
        self.last_check_point = None

        self.lock = multiprocessing.Lock()

        for i in range(len(maze)):
            for j in range(len(maze[0])):
                if maze[i][j] == 2:
                    self.turrets.append(Turret(j*CELL_SIZE,i*CELL_SIZE))
                elif maze[i][j] == -1:
                    self.end_point = pygame.Rect(j*CELL_SIZE,i*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                elif maze[i][j] == -2:
                    self.p1_spawn = (j*CELL_SIZE,i*CELL_SIZE)
                    self.p1.move_specific(j*CELL_SIZE, i*CELL_SIZE)
                elif maze[i][j] == 6:
                    self.checkpoints.append(pygame.Rect(j*CELL_SIZE,i*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def swap_maze(self, maze):
        with self.lock:
            self.maze = maze
            self.turrets = []
            self.checkpoints = []
            self.last_check_point = None

            for i in range(len(maze)):
                for j in range(len(maze[0])):
                    if maze[i][j] == 2:
                        self.turrets.append(Turret(j*CELL_SIZE,i*CELL_SIZE))
                    elif maze[i][j] == -1:
                        self.end_point = pygame.Rect(j*CELL_SIZE,i*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    elif maze[i][j] == -2:
                        self.p1_spawn = (j*CELL_SIZE,i*CELL_SIZE)
                        self.p1.move_specific(j*CELL_SIZE, i*CELL_SIZE)
                    elif maze[i][j] == 6:
                        self.checkpoints.append(pygame.Rect(j*CELL_SIZE,i*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def update_state(self, event):
        self.p1.react_keys(event, self)

        # check for hitting bullet
        for t in self.turrets:
            if t.check_player_collision(self.p1):
                self.p1.move_specific(self.p1_spawn[0], self.p1_spawn[1])
        
    def update_checkpoints(self, player_position):
        with self.lock: 
            for checkpoint in self.checkpoints:
                if pygame.Rect(*player_position, CELL_SIZE, CELL_SIZE).colliderect(checkpoint):
                    self.p1_spawn = (checkpoint.x, checkpoint.y)  # Update the reset point
                    self.last_check_point = checkpoint
                    self.end_point = checkpoint

        print(self.last_check_point)

    def move_bullets(self):
        for t in self.turrets:
            t.update_bullets(self)

    def shoot_turrets(self):
        for t in self.turrets:
            t.shoot(self)

    def draw_checkpoints(self, screen):
        # print(f"draw check_points {self.last_check_point}")
        with self.lock:
            for c in self.checkpoints:
                if c == self.last_check_point:
                    pygame.draw.rect(screen, ACTIVE_CHECKPOINT_COLOR, c)
                else:
                    pygame.draw.rect(screen, CHECKPOINT_COLOR, c)

    def draw(self, screen):
        screen.fill(BLACK)

        # cannot draw if not updated map
        with self.lock:
            print('lock acquired')
            for i, row in enumerate(self.maze):
                for j, cell in enumerate(row):
                    if cell == 0:
                        color = PATH_COLOR
                    elif cell == 1:
                        color = WALL_COLOR
                    pygame.draw.rect(screen, color, pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
            for t in self.turrets:
                t.draw(screen)
        
        # self.draw_checkpoints(screen)
        pygame.draw.rect(screen, END_POINT_COLOR, self.end_point)

        self.p1.draw(screen)

P1_CONTROLS= (pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a)
P2_CONTROLS = (pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT)

def check_win_condition(maze):
    return maze.p1.rect.colliderect(maze.end_point)

import multiprocessing

def player_view(maze, player_position, event_queue, bullet_positions, role_switch):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Player 1 View')
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                event_queue.put(event.key)

        if role_switch.value == 0:  # Player view is controller
            # Draw player view: Only the player rectangle and bullets are visible
            screen.fill(WHITE)
            # maze.update_checkpoints(player_position)
            # maze.draw_checkpoints(screen)
            
            # Draw grid
            for x in range(0, SCREEN_WIDTH, CELL_SIZE):
                pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_HEIGHT))  # Vertical lines
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                pygame.draw.line(screen, BLACK, (0, y), (SCREEN_WIDTH, y))  # Horizontal lines
            
        else:  # Player view becomes the full map
            # Draw the full map
            screen.fill(BLACK)
            # maze.update_checkpoints(player_position)
            maze.draw(screen)

            for bullet in bullet_positions:
                pygame.draw.rect(screen, YELLOW, pygame.Rect(bullet[0], bullet[1], CELL_SIZE - 10, CELL_SIZE - 10))
        
        # Draw the player
        maze.draw_checkpoints(screen)
        pygame.draw.rect(screen, PLAYER1_COLOR, pygame.Rect(player_position[0], player_position[1], CELL_SIZE - 2, CELL_SIZE - 2))
        pygame.display.flip()
        clock.tick(FPS)


def map_view(maze, player_position, event_queue, bullet_positions, role_switch):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Player 2 View')
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                event_queue.put(event.key)

        if role_switch.value == 0:  # Map view shows the full map
            # Draw the full map
            screen.fill(BLACK)
            # maze.update_checkpoints(player_position)
            maze.draw(screen)

            for bullet in bullet_positions:
                pygame.draw.rect(screen, YELLOW, pygame.Rect(bullet[0], bullet[1], CELL_SIZE - 10, CELL_SIZE - 10))

        else:  # Map view becomes the controller
            # Draw player view: Only the player rectangle and bullets are visible
            screen.fill(WHITE)
            # maze.update_checkpoints(player_position)
            # maze.draw_checkpoints(screen)
            
            # Draw grid
            for x in range(0, SCREEN_WIDTH, CELL_SIZE):
                pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_HEIGHT))  # Vertical lines
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                pygame.draw.line(screen, BLACK, (0, y), (SCREEN_WIDTH, y))  # Horizontal lines
            
        # Draw the player
        maze.draw_checkpoints(screen)
        pygame.draw.rect(screen, PLAYER1_COLOR, pygame.Rect(player_position[0], player_position[1], CELL_SIZE - 2, CELL_SIZE - 2))
        pygame.display.flip()
        clock.tick(FPS)


def main():
    manager = multiprocessing.Manager()
    player_position = manager.list([CELL_SIZE, CELL_SIZE])  # Shared player position
    bullet_positions = manager.list()  # Shared list of bullets (x, y)
    event_queue = manager.Queue()  # Queue to handle player events
    role_switch = manager.Value('i', 0)  # 0 = default roles, 1 = switched roles

    maze_layout_1 = get_maze(image_path)
    maze_layout_2 = get_maze(image_path, reflect=True)

    player = Player((CELL_SIZE, CELL_SIZE), PLAYER1_COLOR, P1_CONTROLS)
    maze = Maze(maze_layout_1, player)

    # Create two processes for the views
    player_p1 = multiprocessing.Process(target=player_view, args=(maze, player_position, event_queue, bullet_positions, role_switch))
    player_p2 = multiprocessing.Process(target=map_view, args=(maze, player_position, event_queue, bullet_positions, role_switch))
    player_p1.start()
    player_p2.start()

    clock = pygame.time.Clock()

    SHOOT_EVENT = pygame.USEREVENT + 1
    MOVE_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(MOVE_EVENT, 500)
    pygame.time.set_timer(SHOOT_EVENT, 5000)

    while True:
        # Read player input from the queue
        if not event_queue.empty():
            keys = event_queue.get()
            maze.p1.react_keys(keys, maze)

        # Update the shared player position
        player_position[0] = maze.p1.rect.x
        player_position[1] = maze.p1.rect.y
        maze.update_checkpoints(player_position)
        # Handle turret shooting
        for event in pygame.event.get():
            if event.type == SHOOT_EVENT:
                maze.shoot_turrets()
            if event.type == MOVE_EVENT:
                maze.move_bullets()
                bullet_positions[:] = [(b.rect.x, b.rect.y) for t in maze.turrets for b in t.bullets]

        # Check for collisions with bullets
        for t in maze.turrets:
            if t.check_player_collision(maze.p1):
                maze.p1.move_specific(maze.p1_spawn[0], maze.p1_spawn[1])

        # Check win condition
        if check_win_condition(maze):
            role_switch.value = 1  # Trigger role switch
            # current_maze = maze_2
            maze.swap_maze(maze_layout_2)
            # maze_level += 1

        clock.tick(FPS)
    
    player_p1.join()
    player_p2.join()

if __name__ == "__main__":
    main()

