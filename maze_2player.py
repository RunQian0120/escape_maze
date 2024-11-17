import pygame
import sys
from loader import get_maze

pygame.init()

P1_START = -1
P2_START = -2

FPS = 30
SHOOT_INTERVAL = 1000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RED = (255, 0, 0)
LIGHT_RED = (255, 102, 102)

GREEN = (0, 255, 0)

BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)

YELLOW = (204, 204, 0)
PURPLE = (128, 0, 128)

WALL_COLOR = BLACK
PATH_COLOR = WHITE
TURRET_COLOR = PURPLE

SWAP_COLOR = GREEN
P1_WALL = LIGHT_RED
P2_WALL = LIGHT_BLUE

PLAYER1_COLOR = RED
PLAYER2_COLOR = BLUE

image_path = 'pixil-frame-0.png'
MAZE = get_maze(image_path)

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
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
        if self.check_player_collision(maze.p2):
            maze.p2.move_specific(maze.p2_spawn[0], maze.p2_spawn[1])
    
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
    
    def react_keys(self, keys, maze, gates):
        up, down, right, left = self.controls 
        if keys[left]:
            self.move(-1, 0, maze, gates)
        if keys[right]:
            self.move(1, 0, maze, gates)
        if keys[up]:
            self.move(0, -1, maze, gates)
        if keys[down]:
            self.move(0, 1, maze, gates)

    def move(self, dx, dy, maze, gates):
        if self.movable(dx, dy, maze, gates):
            self.rect.x += dx * CELL_SIZE
            self.rect.y += dy * CELL_SIZE

    def move_specific(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def movable(self, dx, dy, maze, gates):
        new_rect = self.rect.move(dx * CELL_SIZE, dy * CELL_SIZE)
        i, j = new_rect.y // CELL_SIZE, new_rect.x // CELL_SIZE
        for g in gates:
            if new_rect.colliderect(g.rect):
                return False
        return maze.maze[i][j] != 1 and maze.maze[i][j] != 2

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Gate:
    def __init__(self, x, y, player, color):
        self.rect = pygame.Rect(x,y, CELL_SIZE, CELL_SIZE)
        self.color = color
        self.player = player

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Swap:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x,y, CELL_SIZE, CELL_SIZE)
        self.color = color
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Maze:
    def __init__(self, maze, p1, p2):
        self.p1 = p1
        self.p2 = p2

        self.maze = maze
        self.turrets = []
        self.p1_gates = []
        self.p2_gates = []

        self.swaps = []

        self.swapped = False

        for i in range(len(maze)):
            for j in range(len(maze[0])):
                if maze[i][j] == 2:
                    self.turrets.append(Turret(j*CELL_SIZE,i*CELL_SIZE))
                elif maze[i][j] == -1:
                    self.p1_spawn = (j*CELL_SIZE,i*CELL_SIZE)
                    self.p1.move_specific(j*CELL_SIZE, i*CELL_SIZE)
                elif maze[i][j] == -2:
                    self.p2_spawn = (j*CELL_SIZE,i*CELL_SIZE)
                    self.p2.move_specific(j*CELL_SIZE, i*CELL_SIZE)
                elif maze[i][j] == 3:
                    self.swaps.append(Swap(j*CELL_SIZE, i*CELL_SIZE, GREEN))
                elif maze[i][j] == 4:
                    self.p1_gates.append(Gate(j*CELL_SIZE, i*CELL_SIZE, p1, LIGHT_RED))
                elif maze[i][j] == 5:
                    self.p2_gates.append(Gate(j*CELL_SIZE, i*CELL_SIZE, p2, LIGHT_BLUE))

    def swap_players(self):
        cur_x, cur_y = self.p1.rect.x, self.p1.rect.y
        self.p1.move_specific(self.p2.rect.x, self.p2.rect.y)
        self.p2.move_specific(cur_x, cur_y)

    def update_state(self, keys):
        self.p1.react_keys(keys, self, self.p2_gates)
        self.p2.react_keys(keys, self, self.p1_gates)

        # check for hitting bullet
        for t in self.turrets:
            if t.check_player_collision(self.p1):
                self.p1.move_specific(self.p1_spawn[0], self.p1_spawn[1])
            if t.check_player_collision(self.p2):
                self.p2.move_specific(self.p2_spawn[0], self.p2_spawn[1])
        
        # check for hitting swaps
        if not self.swapped:
            for s in self.swaps:
                if self.p1.rect.colliderect(s.rect):
                    self.swap_players()
                    self.swapped = True
                    break
                if self.p2.rect.colliderect(s.rect):
                    self.swap_players()
                    self.swapped = True
                    break
        
        else:
            for s in self.swaps:
                if self.p1.rect.colliderect(s.rect) or self.p2.rect.colliderect(s.rect):
                    break
            else:
                self.swapped = False

    def move_bullets(self):
        for t in self.turrets:
            t.update_bullets(self)

    def shoot_turrets(self):
        for t in self.turrets:
            t.shoot(self)

    def draw(self, screen):
        screen.fill(BLACK)

        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                if cell == 0:
                    color = PATH_COLOR
                elif cell == 1:
                    color = WALL_COLOR

                pygame.draw.rect(screen, color, pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
        for t in self.turrets:
            t.draw(screen)
        for g in self.p1_gates:
            g.draw(screen)
        for g in self.p2_gates:
            g.draw(screen)
        for s in self.swaps:
            s.draw(screen)

        self.p1.draw(screen)
        self.p2.draw(screen)

P1_CONTROLS= (pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a)
P2_CONTROLS = (pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT)

def check_win_condition(maze):
    return maze.p1.rect.colliderect(maze.p2.rect)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Maze Game - Two Players')

    clock = pygame.time.Clock()
    
    player1 = Player((CELL_SIZE, CELL_SIZE), PLAYER1_COLOR, P1_CONTROLS)
    player2 = Player((CELL_SIZE * 2, CELL_SIZE * 2), PLAYER2_COLOR, P2_CONTROLS)
    maze = Maze(MAZE, player1, player2)

    SHOOT_EVENT = pygame.USEREVENT + 1
    MOVE_BULLET_EVENT = pygame.USEREVENT + 2

    pygame.time.set_timer(SHOOT_EVENT, 5000)
    pygame.time.set_timer(MOVE_BULLET_EVENT, 500)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == SHOOT_EVENT:
                maze.shoot_turrets()

            if event.type == MOVE_BULLET_EVENT:
                maze.move_bullets()

        keys = pygame.key.get_pressed()

        maze.update_state(keys)
        maze.draw(screen)

        if check_win_condition(maze):
            pygame.display.set_caption("You Won!")
            font = pygame.font.SysFont(None, 100) 
            text = font.render('You Won!', True, GREEN)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

            screen.blit(text, text_rect)

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
