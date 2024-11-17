from PIL import Image


SWAP_COLOR = (34, 177, 76, 255) # 3

P1_GATE = (255, 126, 0, 255) # 5
P2_GATE = (153, 217, 234, 255) # 4

P1_SPAWN = (237, 28, 36, 255) # -1
P2_SPAWN = (47, 54, 153, 255) # -2

WALL_COLOR = (70, 70, 70, 255) # 1
TURRET_COLOR = (111, 49, 152, 255) # 2
PATH_COLOR = (0, 0, 0, 0) # 0

def get_maze(path):
    image = Image.open(path)

    width, height = image.size
    res = [[0] * width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            pixel = image.getpixel((x, y))
            
            if pixel == PATH_COLOR: 
                res[y][x] = 0
            elif pixel == WALL_COLOR:
                res[y][x] = 1
            elif pixel == TURRET_COLOR:
                res[y][x] = 2
            elif pixel == SWAP_COLOR:
                res[y][x] = 3
            elif pixel == P1_GATE:
                res[y][x] = 4
            elif pixel == P2_GATE:
                res[y][x] = 5
            elif pixel == P1_SPAWN:
                res[y][x] = -1
            elif pixel == P2_SPAWN:
                res[y][x] = -2
            else:
                raise RuntimeError("Invalid Color")
    image.close()
    return res
